# -*- coding: utf-8 -*-
"""
数据备份和恢复服务
Data Backup and Recovery Service
"""

import os
import shutil
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class BackupService:
    """数据备份和恢复服务"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.backup_dir = self.base_dir / 'backups'
        self.uploads_dir = self.base_dir / 'uploads'
        self.db_path = self.data_dir / 'trading_journal.db'
        
        # 确保备份目录存在
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, backup_name=None):
        """创建完整备份"""
        try:
            if backup_name is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f'trading_journal_backup_{timestamp}'
            
            backup_path = self.backup_dir / f'{backup_name}.zip'
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 备份数据库文件
                if self.db_path.exists():
                    zipf.write(self.db_path, 'data/trading_journal.db')
                    logger.info(f"数据库文件已备份: {self.db_path}")
                
                # 备份上传的图片文件
                if self.uploads_dir.exists():
                    for file_path in self.uploads_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = f'uploads/{file_path.relative_to(self.uploads_dir)}'
                            zipf.write(file_path, arcname)
                    logger.info(f"上传文件已备份: {self.uploads_dir}")
                
                # 创建备份元数据
                metadata = {
                    'backup_name': backup_name,
                    'created_at': datetime.now().isoformat(),
                    'database_size': self.db_path.stat().st_size if self.db_path.exists() else 0,
                    'uploads_count': len(list(self.uploads_dir.rglob('*'))) if self.uploads_dir.exists() else 0,
                    'version': '1.0'
                }
                
                zipf.writestr('backup_metadata.json', json.dumps(metadata, indent=2, ensure_ascii=False))
            
            logger.info(f"备份创建成功: {backup_path}")
            return {
                'success': True,
                'backup_path': str(backup_path),
                'backup_name': backup_name,
                'size': backup_path.stat().st_size
            }
            
        except Exception as e:
            logger.error(f"创建备份失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_backup(self, backup_file):
        """恢复备份"""
        try:
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
            # 创建恢复前的备份
            pre_restore_backup = self.create_backup(f'pre_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            if not pre_restore_backup['success']:
                logger.warning("创建恢复前备份失败，继续恢复操作")
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # 读取备份元数据
                try:
                    metadata_content = zipf.read('backup_metadata.json')
                    metadata = json.loads(metadata_content.decode('utf-8'))
                    logger.info(f"恢复备份: {metadata['backup_name']}, 创建时间: {metadata['created_at']}")
                except:
                    logger.warning("无法读取备份元数据，继续恢复操作")
                
                # 恢复数据库文件
                try:
                    db_content = zipf.read('data/trading_journal.db')
                    self.data_dir.mkdir(exist_ok=True)
                    
                    # 备份当前数据库
                    if self.db_path.exists():
                        current_db_backup = self.db_path.with_suffix('.db.bak')
                        shutil.copy2(self.db_path, current_db_backup)
                    
                    # 写入新数据库
                    with open(self.db_path, 'wb') as f:
                        f.write(db_content)
                    
                    logger.info("数据库恢复成功")
                except KeyError:
                    logger.warning("备份中未找到数据库文件")
                
                # 恢复上传文件
                uploads_restored = 0
                for file_info in zipf.filelist:
                    if file_info.filename.startswith('uploads/') and not file_info.is_dir():
                        # 提取文件
                        file_content = zipf.read(file_info.filename)
                        file_path = self.base_dir / file_info.filename
                        
                        # 确保目录存在
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # 写入文件
                        with open(file_path, 'wb') as f:
                            f.write(file_content)
                        
                        uploads_restored += 1
                
                if uploads_restored > 0:
                    logger.info(f"恢复了 {uploads_restored} 个上传文件")
            
            return {
                'success': True,
                'message': f'备份恢复成功: {backup_file}',
                'uploads_restored': uploads_restored
            }
            
        except Exception as e:
            logger.error(f"恢复备份失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_backups(self):
        """列出所有备份文件"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob('*.zip'):
                try:
                    stat = backup_file.stat()
                    backup_info = {
                        'filename': backup_file.name,
                        'size': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'size_mb': round(stat.st_size / (1024 * 1024), 2)
                    }
                    
                    # 尝试读取备份元数据
                    try:
                        with zipfile.ZipFile(backup_file, 'r') as zipf:
                            metadata_content = zipf.read('backup_metadata.json')
                            metadata = json.loads(metadata_content.decode('utf-8'))
                            backup_info.update({
                                'backup_name': metadata.get('backup_name'),
                                'database_size': metadata.get('database_size', 0),
                                'uploads_count': metadata.get('uploads_count', 0),
                                'version': metadata.get('version', 'unknown')
                            })
                    except:
                        pass
                    
                    backups.append(backup_info)
                    
                except Exception as e:
                    logger.warning(f"读取备份文件信息失败 {backup_file}: {str(e)}")
            
            # 按创建时间倒序排列
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return {
                'success': True,
                'backups': backups,
                'total_count': len(backups),
                'total_size_mb': sum(b['size_mb'] for b in backups)
            }
            
        except Exception as e:
            logger.error(f"列出备份文件失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_backup(self, backup_file):
        """删除备份文件"""
        try:
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
            backup_path.unlink()
            logger.info(f"备份文件已删除: {backup_path}")
            
            return {
                'success': True,
                'message': f'备份文件已删除: {backup_file}'
            }
            
        except Exception as e:
            logger.error(f"删除备份文件失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_old_backups(self, retention_days=30):
        """清理过期备份"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_count = 0
            deleted_size = 0
            
            for backup_file in self.backup_dir.glob('*.zip'):
                try:
                    stat = backup_file.stat()
                    if datetime.fromtimestamp(stat.st_mtime) < cutoff_date:
                        deleted_size += stat.st_size
                        backup_file.unlink()
                        deleted_count += 1
                        logger.info(f"删除过期备份: {backup_file.name}")
                        
                except Exception as e:
                    logger.warning(f"删除过期备份失败 {backup_file}: {str(e)}")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'deleted_size_mb': round(deleted_size / (1024 * 1024), 2),
                'retention_days': retention_days
            }
            
        except Exception as e:
            logger.error(f"清理过期备份失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_backup(self, backup_file):
        """验证备份文件完整性"""
        try:
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
            verification_result = {
                'filename': backup_file,
                'is_valid': False,
                'has_database': False,
                'has_metadata': False,
                'uploads_count': 0,
                'errors': []
            }
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # 检查ZIP文件完整性
                bad_file = zipf.testzip()
                if bad_file:
                    verification_result['errors'].append(f"ZIP文件损坏: {bad_file}")
                    return verification_result
                
                file_list = zipf.namelist()
                
                # 检查数据库文件
                if 'data/trading_journal.db' in file_list:
                    verification_result['has_database'] = True
                    
                    # 验证数据库文件
                    try:
                        db_content = zipf.read('data/trading_journal.db')
                        # 尝试连接数据库验证格式
                        import tempfile
                        with tempfile.NamedTemporaryFile() as temp_db:
                            temp_db.write(db_content)
                            temp_db.flush()
                            
                            conn = sqlite3.connect(temp_db.name)
                            cursor = conn.cursor()
                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                            tables = cursor.fetchall()
                            conn.close()
                            
                            if len(tables) > 0:
                                verification_result['database_tables'] = len(tables)
                            else:
                                verification_result['errors'].append("数据库中没有表")
                                
                    except Exception as e:
                        verification_result['errors'].append(f"数据库验证失败: {str(e)}")
                else:
                    verification_result['errors'].append("缺少数据库文件")
                
                # 检查元数据文件
                if 'backup_metadata.json' in file_list:
                    verification_result['has_metadata'] = True
                    try:
                        metadata_content = zipf.read('backup_metadata.json')
                        metadata = json.loads(metadata_content.decode('utf-8'))
                        verification_result['metadata'] = metadata
                    except Exception as e:
                        verification_result['errors'].append(f"元数据读取失败: {str(e)}")
                
                # 统计上传文件
                uploads_files = [f for f in file_list if f.startswith('uploads/') and not f.endswith('/')]
                verification_result['uploads_count'] = len(uploads_files)
                
                # 如果没有错误，标记为有效
                if not verification_result['errors']:
                    verification_result['is_valid'] = True
            
            return {
                'success': True,
                'verification': verification_result
            }
            
        except Exception as e:
            logger.error(f"验证备份文件失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def auto_backup_check(self):
        """检查是否需要自动备份"""
        try:
            # 获取最新备份时间
            latest_backup = None
            latest_time = None
            
            for backup_file in self.backup_dir.glob('*.zip'):
                stat = backup_file.stat()
                backup_time = datetime.fromtimestamp(stat.st_mtime)
                if latest_time is None or backup_time > latest_time:
                    latest_time = backup_time
                    latest_backup = backup_file.name
            
            # 检查是否需要备份（默认7天）
            needs_backup = False
            if latest_time is None:
                needs_backup = True
                reason = "没有找到任何备份文件"
            else:
                days_since_backup = (datetime.now() - latest_time).days
                if days_since_backup >= 7:
                    needs_backup = True
                    reason = f"距离上次备份已过去 {days_since_backup} 天"
                else:
                    reason = f"距离上次备份 {days_since_backup} 天，暂不需要备份"
            
            return {
                'success': True,
                'needs_backup': needs_backup,
                'latest_backup': latest_backup,
                'latest_backup_time': latest_time.isoformat() if latest_time else None,
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"检查自动备份失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }