#!/usr/bin/env python3
"""
数据库迁移部署脚本
用于生产环境的数据库迁移和初始化
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from config import ProductionConfig, DevelopmentConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """数据库迁移管理器"""
    
    def __init__(self, app):
        self.app = app
        self.migration_dir = project_root / 'migrations'
        
    def check_database_connection(self):
        """检查数据库连接"""
        try:
            with self.app.app_context():
                db.engine.execute(db.text('SELECT 1'))
            logger.info("数据库连接正常")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def backup_database(self, backup_path=None):
        """备份数据库"""
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = project_root / 'backups' / f'db_backup_{timestamp}.sql'
        
        backup_path.parent.mkdir(exist_ok=True)
        
        try:
            with self.app.app_context():
                db_uri = self.app.config['SQLALCHEMY_DATABASE_URI']
                
                if db_uri.startswith('sqlite:///'):
                    # SQLite备份
                    db_file = db_uri.replace('sqlite:///', '')
                    if os.path.exists(db_file):
                        import shutil
                        shutil.copy2(db_file, str(backup_path).replace('.sql', '.db'))
                        logger.info(f"SQLite数据库备份完成: {backup_path}")
                        return True
                elif db_uri.startswith('mysql://') or db_uri.startswith('postgresql://'):
                    # MySQL/PostgreSQL备份
                    logger.warning("MySQL/PostgreSQL备份需要手动执行相应的dump命令")
                    return False
                    
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return False
    
    def get_migration_files(self):
        """获取所有迁移文件"""
        migration_files = []
        if self.migration_dir.exists():
            for file in sorted(self.migration_dir.glob('*.py')):
                if file.name != '__init__.py' and not file.name.startswith('__'):
                    migration_files.append(file)
        return migration_files
    
    def check_migration_status(self):
        """检查迁移状态"""
        try:
            with self.app.app_context():
                # 检查是否存在迁移记录表
                result = db.engine.execute(db.text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='migration_history'
                """)).fetchone()
                
                if not result:
                    # 创建迁移记录表
                    db.engine.execute(db.text("""
                        CREATE TABLE migration_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            filename VARCHAR(255) NOT NULL UNIQUE,
                            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            checksum VARCHAR(64)
                        )
                    """))
                    logger.info("创建迁移记录表")
                
                # 获取已应用的迁移
                applied_migrations = db.engine.execute(db.text("""
                    SELECT filename FROM migration_history ORDER BY applied_at
                """)).fetchall()
                
                return [row[0] for row in applied_migrations]
                
        except Exception as e:
            logger.error(f"检查迁移状态失败: {e}")
            return []
    
    def apply_migration(self, migration_file):
        """应用单个迁移"""
        try:
            with self.app.app_context():
                # 动态导入迁移模块
                spec = importlib.util.spec_from_file_location(
                    migration_file.stem, migration_file
                )
                migration_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(migration_module)
                
                # 执行升级
                if hasattr(migration_module, 'upgrade'):
                    migration_module.upgrade()
                    
                    # 记录迁移
                    db.engine.execute(db.text("""
                        INSERT INTO migration_history (filename) VALUES (?)
                    """), (migration_file.name,))
                    
                    logger.info(f"迁移应用成功: {migration_file.name}")
                    return True
                else:
                    logger.error(f"迁移文件缺少upgrade函数: {migration_file.name}")
                    return False
                    
        except Exception as e:
            logger.error(f"应用迁移失败 {migration_file.name}: {e}")
            return False
    
    def run_migrations(self, dry_run=False):
        """运行所有待应用的迁移"""
        if not self.check_database_connection():
            return False
        
        # 备份数据库
        if not dry_run:
            self.backup_database()
        
        # 获取迁移状态
        applied_migrations = self.check_migration_status()
        migration_files = self.get_migration_files()
        
        # 找出待应用的迁移
        pending_migrations = []
        for migration_file in migration_files:
            if migration_file.name not in applied_migrations:
                pending_migrations.append(migration_file)
        
        if not pending_migrations:
            logger.info("没有待应用的迁移")
            return True
        
        logger.info(f"发现 {len(pending_migrations)} 个待应用的迁移")
        
        if dry_run:
            logger.info("干运行模式，以下迁移将被应用:")
            for migration in pending_migrations:
                logger.info(f"  - {migration.name}")
            return True
        
        # 应用迁移
        success_count = 0
        for migration_file in pending_migrations:
            if self.apply_migration(migration_file):
                success_count += 1
            else:
                logger.error(f"迁移失败，停止后续迁移: {migration_file.name}")
                break
        
        logger.info(f"成功应用 {success_count}/{len(pending_migrations)} 个迁移")
        return success_count == len(pending_migrations)


def main():
    """主函数"""
    import argparse
    import importlib.util
    
    parser = argparse.ArgumentParser(description='数据库迁移部署脚本')
    parser.add_argument('--env', choices=['development', 'production'], 
                       default='development', help='运行环境')
    parser.add_argument('--dry-run', action='store_true', 
                       help='干运行模式，不实际执行迁移')
    parser.add_argument('--backup-only', action='store_true',
                       help='仅备份数据库')
    
    args = parser.parse_args()
    
    # 创建应用
    if args.env == 'production':
        app = create_app(ProductionConfig)
    else:
        app = create_app(DevelopmentConfig)
    
    # 创建迁移器
    migrator = DatabaseMigrator(app)
    
    if args.backup_only:
        # 仅备份
        success = migrator.backup_database()
        sys.exit(0 if success else 1)
    
    # 运行迁移
    success = migrator.run_migrations(dry_run=args.dry_run)
    
    if success:
        logger.info("数据库迁移部署完成")
        sys.exit(0)
    else:
        logger.error("数据库迁移部署失败")
        sys.exit(1)


if __name__ == '__main__':
    main()