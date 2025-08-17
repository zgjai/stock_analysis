"""
数据库迁移系统
"""
import os
import json
from datetime import datetime
from pathlib import Path
from app import create_app
from extensions import db


class DatabaseMigration:
    """数据库迁移管理器"""
    
    def __init__(self):
        self.app = create_app()
        self.migration_dir = Path(__file__).parent / 'migrations'
        self.migration_dir.mkdir(exist_ok=True)
        self.migration_table = 'schema_migrations'
    
    def _ensure_migration_table(self):
        """确保迁移记录表存在"""
        with self.app.app_context():
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text(f"""
                        CREATE TABLE IF NOT EXISTS {self.migration_table} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            version VARCHAR(50) UNIQUE NOT NULL,
                            description TEXT,
                            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    conn.commit()
            except Exception as e:
                print(f"创建迁移表失败: {e}")
                raise
    
    def _get_applied_migrations(self):
        """获取已应用的迁移"""
        with self.app.app_context():
            try:
                with db.engine.connect() as conn:
                    result = conn.execute(db.text(f"SELECT version FROM {self.migration_table} ORDER BY version"))
                    return [row[0] for row in result]
            except Exception:
                return []
    
    def _mark_migration_applied(self, version, description):
        """标记迁移为已应用"""
        with self.app.app_context():
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text(f"""
                        INSERT INTO {self.migration_table} (version, description) 
                        VALUES (:version, :description)
                    """), {"version": version, "description": description})
                    conn.commit()
            except Exception as e:
                print(f"标记迁移失败: {e}")
                raise
    
    def create_migration(self, description):
        """创建新的迁移文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        version = f"{timestamp}_{description.lower().replace(' ', '_')}"
        filename = f"{version}.py"
        filepath = self.migration_dir / filename
        
        template = f'''"""
迁移: {description}
创建时间: {datetime.now().isoformat()}
"""
from extensions import db


def upgrade():
    """应用迁移"""
    # 在这里添加升级SQL语句
    # 例如:
    # db.engine.execute("""
    #     ALTER TABLE table_name ADD COLUMN new_column VARCHAR(50)
    # """)
    pass


def downgrade():
    """回滚迁移"""
    # 在这里添加回滚SQL语句
    # 例如:
    # db.engine.execute("""
    #     ALTER TABLE table_name DROP COLUMN new_column
    # """)
    pass
'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"创建迁移文件: {filepath}")
        return version
    
    def get_pending_migrations(self):
        """获取待应用的迁移"""
        applied = set(self._get_applied_migrations())
        all_migrations = []
        
        for file in sorted(self.migration_dir.glob('*.py')):
            if file.name != '__init__.py':
                version = file.stem
                all_migrations.append(version)
        
        pending = [m for m in all_migrations if m not in applied]
        return pending
    
    def apply_migration(self, version):
        """应用单个迁移"""
        migration_file = self.migration_dir / f"{version}.py"
        
        if not migration_file.exists():
            raise FileNotFoundError(f"迁移文件不存在: {migration_file}")
        
        # 动态导入迁移模块
        import importlib.util
        spec = importlib.util.spec_from_file_location(version, migration_file)
        migration_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration_module)
        
        with self.app.app_context():
            try:
                # 执行升级
                migration_module.upgrade()
                
                # 标记为已应用
                description = getattr(migration_module, '__doc__', '').strip().split('\n')[1] if hasattr(migration_module, '__doc__') else version
                self._mark_migration_applied(version, description)
                
                print(f"✓ 应用迁移: {version}")
                return True
            except Exception as e:
                print(f"✗ 应用迁移失败 {version}: {e}")
                db.session.rollback()
                return False
    
    def rollback_migration(self, version):
        """回滚单个迁移"""
        migration_file = self.migration_dir / f"{version}.py"
        
        if not migration_file.exists():
            raise FileNotFoundError(f"迁移文件不存在: {migration_file}")
        
        # 动态导入迁移模块
        import importlib.util
        spec = importlib.util.spec_from_file_location(version, migration_file)
        migration_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration_module)
        
        with self.app.app_context():
            try:
                # 执行回滚
                migration_module.downgrade()
                
                # 从记录中移除
                with db.engine.connect() as conn:
                    conn.execute(db.text(f"DELETE FROM {self.migration_table} WHERE version = :version"), {"version": version})
                    conn.commit()
                
                print(f"✓ 回滚迁移: {version}")
                return True
            except Exception as e:
                print(f"✗ 回滚迁移失败 {version}: {e}")
                db.session.rollback()
                return False
    
    def migrate(self):
        """应用所有待处理的迁移"""
        self._ensure_migration_table()
        pending = self.get_pending_migrations()
        
        if not pending:
            print("没有待应用的迁移")
            return True
        
        print(f"发现 {len(pending)} 个待应用的迁移:")
        for migration in pending:
            print(f"  - {migration}")
        
        success_count = 0
        for migration in pending:
            if self.apply_migration(migration):
                success_count += 1
            else:
                print(f"迁移中断于: {migration}")
                break
        
        print(f"成功应用 {success_count}/{len(pending)} 个迁移")
        return success_count == len(pending)
    
    def status(self):
        """显示迁移状态"""
        self._ensure_migration_table()
        applied = self._get_applied_migrations()
        pending = self.get_pending_migrations()
        
        print("数据库迁移状态:")
        print(f"已应用迁移: {len(applied)}")
        for migration in applied:
            print(f"  ✓ {migration}")
        
        print(f"待应用迁移: {len(pending)}")
        for migration in pending:
            print(f"  - {migration}")
    
    def reset(self):
        """重置迁移状态（危险操作）"""
        with self.app.app_context():
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text(f"DROP TABLE IF EXISTS {self.migration_table}"))
                    conn.commit()
                print("✓ 迁移状态已重置")
                return True
            except Exception as e:
                print(f"✗ 重置迁移状态失败: {e}")
                return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库迁移工具')
    parser.add_argument('command', choices=['create', 'migrate', 'status', 'rollback', 'reset'], 
                       help='迁移命令')
    parser.add_argument('--description', '-d', help='迁移描述（用于create命令）')
    parser.add_argument('--version', '-v', help='迁移版本（用于rollback命令）')
    
    args = parser.parse_args()
    
    migration = DatabaseMigration()
    
    if args.command == 'create':
        if not args.description:
            print("创建迁移需要提供描述信息")
            return
        version = migration.create_migration(args.description)
        print(f"迁移文件已创建: {version}")
    
    elif args.command == 'migrate':
        migration.migrate()
    
    elif args.command == 'status':
        migration.status()
    
    elif args.command == 'rollback':
        if not args.version:
            print("回滚迁移需要指定版本")
            return
        migration.rollback_migration(args.version)
    
    elif args.command == 'reset':
        confirm = input("确定要重置迁移状态吗？这将删除所有迁移记录 (y/N): ")
        if confirm.lower() == 'y':
            migration.reset()
        else:
            print("操作已取消")


if __name__ == '__main__':
    main()