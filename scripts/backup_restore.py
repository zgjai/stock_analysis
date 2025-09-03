#!/usr/bin/env python3
"""
数据备份和恢复脚本
"""
import os
import sys
import shutil
import sqlite3
import logging
import tarfile
import gzip
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config, ProductionConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackupManager:
    """备份管理器"""
    
    def __init__(self, config_class=Config):
        self.config = config_class()
        self.project_root = project_root
        self.backup_dir = self.config.BACKUP_LOCATION
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_database_backup(self, backup_name=None):
        """创建数据库备份"""
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'db_backup_{timestamp}'
        
        backup_path = self.backup_dir / f'{backup_name}.db'
        
        try:
            db_uri = self.config.SQLALCHEMY_DATABASE_URI
            
            if db_uri.startswith('sqlite:///'):
                # SQLite备份
                source_db = db_uri.replace('sqlite:///', '')
                source_path = Path(source_db)
                
                if not source_path.is_absolute():
                    source_path = self.project_root / source_path
                
                if source_path.exists():
                    shutil.copy2(source_path, backup_path)
                    logger.info(f"SQLite数据库备份完成: {backup_path}")
                    return backup_path
                else:
                    logger.error(f"源数据库文件不存在: {source_path}")
                    return None
                    
            else:
                logger.error("暂不支持非SQLite数据库的备份")
                return None
                
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return None
    
    def create_files_backup(self, backup_name=None):
        """创建文件备份"""
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'files_backup_{timestamp}'
        
        backup_path = self.backup_dir / f'{backup_name}.tar.gz'
        
        try:
            # 需要备份的目录
            dirs_to_backup = [
                ('uploads', self.project_root / 'uploads'),
                ('logs', self.project_root / 'logs'),
                ('data', self.project_root / 'data'),
            ]
            
            with tarfile.open(backup_path, 'w:gz') as tar:
                for dir_name, dir_path in dirs_to_backup:
                    if dir_path.exists():
                        tar.add(dir_path, arcname=dir_name)
                        logger.info(f"添加到备份: {dir_path}")
            
            logger.info(f"文件备份完成: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"文件备份失败: {e}")
            return None
    
    def create_full_backup(self, backup_name=None):
        """创建完整备份"""
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'full_backup_{timestamp}'
        
        logger.info(f"开始创建完整备份: {backup_name}")
        
        # 创建备份目录
        full_backup_dir = self.backup_dir / backup_name
        full_backup_dir.mkdir(exist_ok=True)
        
        # 数据库备份
        db_backup = self.create_database_backup(f'{backup_name}_db')
        if db_backup:
            shutil.move(db_backup, full_backup_dir / 'database.db')
        
        # 文件备份
        files_backup = self.create_files_backup(f'{backup_name}_files')
        if files_backup:
            shutil.move(files_backup, full_backup_dir / 'files.tar.gz')
        
        # 创建备份信息文件
        backup_info = {
            'backup_name': backup_name,
            'timestamp': datetime.now().isoformat(),
            'database_backup': 'database.db',
            'files_backup': 'files.tar.gz',
            'config': {
                'database_uri': self.config.SQLALCHEMY_DATABASE_URI,
                'upload_folder': str(self.config.UPLOAD_FOLDER),
            }
        }
        
        import json
        info_file = full_backup_dir / 'backup_info.json'
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(backup_info, f, indent=2, ensure_ascii=False)
        
        # 压缩完整备份
        compressed_backup = self.backup_dir / f'{backup_name}.tar.gz'
        with tarfile.open(compressed_backup, 'w:gz') as tar:
            tar.add(full_backup_dir, arcname=backup_name)
        
        # 删除临时目录
        shutil.rmtree(full_backup_dir)
        
        logger.info(f"完整备份创建完成: {compressed_backup}")
        return compressed_backup
    
    def restore_database(self, backup_path):
        """恢复数据库"""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            logger.error(f"备份文件不存在: {backup_path}")
            return False
        
        try:
            db_uri = self.config.SQLALCHEMY_DATABASE_URI
            
            if db_uri.startswith('sqlite:///'):
                # SQLite恢复
                target_db = db_uri.replace('sqlite:///', '')
                target_path = Path(target_db)
                
                if not target_path.is_absolute():
                    target_path = self.project_root / target_path
                
                # 备份当前数据库
                if target_path.exists():
                    backup_current = target_path.with_suffix('.db.backup')
                    shutil.copy2(target_path, backup_current)
                    logger.info(f"当前数据库已备份到: {backup_current}")
                
                # 恢复数据库
                shutil.copy2(backup_path, target_path)
                logger.info(f"数据库恢复完成: {target_path}")
                return True
                
            else:
                logger.error("暂不支持非SQLite数据库的恢复")
                return False
                
        except Exception as e:
            logger.error(f"数据库恢复失败: {e}")
            return False
    
    def restore_files(self, backup_path):
        """恢复文件"""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            logger.error(f"备份文件不存在: {backup_path}")
            return False
        
        try:
            with tarfile.open(backup_path, 'r:gz') as tar:
                # 提取到项目根目录
                tar.extractall(self.project_root)
                logger.info(f"文件恢复完成: {backup_path}")
                return True
                
        except Exception as e:
            logger.error(f"文件恢复失败: {e}")
            return False
    
    def restore_full_backup(self, backup_path):
        """恢复完整备份"""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            logger.error(f"备份文件不存在: {backup_path}")
            return False
        
        try:
            # 提取备份
            temp_dir = self.backup_dir / 'temp_restore'
            temp_dir.mkdir(exist_ok=True)
            
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(temp_dir)
            
            # 找到备份目录
            backup_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
            if not backup_dirs:
                logger.error("备份文件格式错误")
                return False
            
            backup_content_dir = backup_dirs[0]
            
            # 读取备份信息
            info_file = backup_content_dir / 'backup_info.json'
            if info_file.exists():
                import json
                with open(info_file, 'r', encoding='utf-8') as f:
                    backup_info = json.load(f)
                logger.info(f"恢复备份: {backup_info['backup_name']} ({backup_info['timestamp']})")
            
            # 恢复数据库
            db_backup = backup_content_dir / 'database.db'
            if db_backup.exists():
                if not self.restore_database(db_backup):
                    logger.error("数据库恢复失败")
                    return False
            
            # 恢复文件
            files_backup = backup_content_dir / 'files.tar.gz'
            if files_backup.exists():
                if not self.restore_files(files_backup):
                    logger.error("文件恢复失败")
                    return False
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
            
            logger.info("完整备份恢复完成")
            return True
            
        except Exception as e:
            logger.error(f"完整备份恢复失败: {e}")
            return False
    
    def list_backups(self):
        """列出所有备份"""
        backups = []
        
        for backup_file in self.backup_dir.glob('*.tar.gz'):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.name,
                'path': backup_file,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_mtime),
                'type': 'full' if 'full_backup' in backup_file.name else 'partial'
            })
        
        for backup_file in self.backup_dir.glob('*.db'):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.name,
                'path': backup_file,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_mtime),
                'type': 'database'
            })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def cleanup_old_backups(self, retention_days=None):
        """清理旧备份"""
        if retention_days is None:
            retention_days = self.config.BACKUP_RETENTION_DAYS
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        deleted_count = 0
        for backup_file in self.backup_dir.glob('*'):
            if backup_file.is_file():
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    try:
                        backup_file.unlink()
                        logger.info(f"删除旧备份: {backup_file.name}")
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"删除备份失败 {backup_file.name}: {e}")
        
        logger.info(f"清理完成，删除了 {deleted_count} 个旧备份")
        return deleted_count
    
    def verify_backup(self, backup_path):
        """验证备份完整性"""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            logger.error(f"备份文件不存在: {backup_path}")
            return False
        
        try:
            if backup_path.suffix == '.db':
                # 验证SQLite数据库
                conn = sqlite3.connect(backup_path)
                conn.execute('PRAGMA integrity_check')
                conn.close()
                logger.info(f"数据库备份验证通过: {backup_path}")
                return True
                
            elif backup_path.suffix == '.gz':
                # 验证压缩文件
                with tarfile.open(backup_path, 'r:gz') as tar:
                    tar.getnames()  # 尝试读取文件列表
                logger.info(f"压缩备份验证通过: {backup_path}")
                return True
                
            else:
                logger.warning(f"未知备份格式: {backup_path}")
                return False
                
        except Exception as e:
            logger.error(f"备份验证失败 {backup_path}: {e}")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='备份和恢复脚本')
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'cleanup', 'verify'],
                       help='操作类型')
    parser.add_argument('--type', choices=['database', 'files', 'full'], 
                       default='full', help='备份类型')
    parser.add_argument('--name', help='备份名称')
    parser.add_argument('--path', help='备份文件路径')
    parser.add_argument('--retention-days', type=int, default=30,
                       help='备份保留天数')
    parser.add_argument('--env', choices=['development', 'production'], 
                       default='production', help='运行环境')
    
    args = parser.parse_args()
    
    # 选择配置
    if args.env == 'production':
        config_class = ProductionConfig
    else:
        config_class = Config
    
    # 创建备份管理器
    backup_manager = BackupManager(config_class)
    
    try:
        if args.action == 'backup':
            if args.type == 'database':
                result = backup_manager.create_database_backup(args.name)
            elif args.type == 'files':
                result = backup_manager.create_files_backup(args.name)
            else:  # full
                result = backup_manager.create_full_backup(args.name)
            
            if result:
                logger.info(f"备份成功: {result}")
                sys.exit(0)
            else:
                logger.error("备份失败")
                sys.exit(1)
        
        elif args.action == 'restore':
            if not args.path:
                logger.error("恢复操作需要指定备份文件路径")
                sys.exit(1)
            
            if args.type == 'database':
                success = backup_manager.restore_database(args.path)
            elif args.type == 'files':
                success = backup_manager.restore_files(args.path)
            else:  # full
                success = backup_manager.restore_full_backup(args.path)
            
            if success:
                logger.info("恢复成功")
                sys.exit(0)
            else:
                logger.error("恢复失败")
                sys.exit(1)
        
        elif args.action == 'list':
            backups = backup_manager.list_backups()
            if backups:
                print(f"{'名称':<30} {'类型':<10} {'大小':<10} {'创建时间':<20}")
                print("-" * 70)
                for backup in backups:
                    size_mb = backup['size'] / (1024 * 1024)
                    created_str = backup['created'].strftime('%Y-%m-%d %H:%M:%S')
                    print(f"{backup['name']:<30} {backup['type']:<10} {size_mb:.1f}MB {created_str:<20}")
            else:
                print("没有找到备份文件")
        
        elif args.action == 'cleanup':
            deleted_count = backup_manager.cleanup_old_backups(args.retention_days)
            logger.info(f"清理完成，删除了 {deleted_count} 个备份")
        
        elif args.action == 'verify':
            if not args.path:
                logger.error("验证操作需要指定备份文件路径")
                sys.exit(1)
            
            success = backup_manager.verify_backup(args.path)
            if success:
                logger.info("备份验证通过")
                sys.exit(0)
            else:
                logger.error("备份验证失败")
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"操作失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()