# -*- coding: utf-8 -*-
"""
数据备份服务测试
Basic Backup Function Tests

测试需求:
- 测试数据库的基本备份功能
- 验证备份文件的完整性  
- 测试简单的数据恢复流程
- 需求: 2.4, 8.1
"""

import pytest
import tempfile
import shutil
import json
import zipfile
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from services.backup_service import BackupService


class TestBackupService:
    """备份服务基本功能测试"""
    
    @pytest.fixture
    def temp_backup_service(self):
        """创建临时备份服务实例"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 创建临时目录结构
            data_dir = temp_path / 'data'
            backup_dir = temp_path / 'backups'
            uploads_dir = temp_path / 'uploads'
            
            data_dir.mkdir()
            backup_dir.mkdir()
            uploads_dir.mkdir()
            
            # 创建临时数据库
            db_path = data_dir / 'trading_journal.db'
            conn = sqlite3.connect(str(db_path))
            conn.execute('''
                CREATE TABLE trades (
                    id INTEGER PRIMARY KEY,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    trade_type TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                INSERT INTO trades (stock_code, stock_name, trade_type, price, quantity)
                VALUES ('000001', '平安银行', 'buy', 12.50, 1000)
            ''')
            conn.commit()
            conn.close()
            
            # 创建测试上传文件
            test_file = uploads_dir / 'test_image.png'
            test_file.write_bytes(b'fake image data')
            
            # 创建备份服务实例并设置路径
            service = BackupService()
            service.base_dir = temp_path
            service.data_dir = data_dir
            service.backup_dir = backup_dir
            service.uploads_dir = uploads_dir
            service.db_path = db_path
            
            yield service
    
    def test_create_backup_basic(self, temp_backup_service):
        """测试基本备份创建功能"""
        service = temp_backup_service
        
        # 执行备份
        result = service.create_backup('test_backup')
        
        # 验证结果
        assert result['success'] is True
        assert 'backup_path' in result
        assert 'backup_name' in result
        assert 'size' in result
        assert result['backup_name'] == 'test_backup'
        
        # 验证备份文件存在
        backup_path = Path(result['backup_path'])
        assert backup_path.exists()
        assert backup_path.suffix == '.zip'
        
        # 验证备份文件内容
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            file_list = zipf.namelist()
            assert 'data/trading_journal.db' in file_list
            assert 'uploads/test_image.png' in file_list
            assert 'backup_metadata.json' in file_list
    
    def test_create_backup_auto_name(self, temp_backup_service):
        """测试自动生成备份名称"""
        service = temp_backup_service
        
        # 执行备份（不指定名称）
        result = service.create_backup()
        
        # 验证结果
        assert result['success'] is True
        assert 'backup_name' in result
        
        # 验证自动生成的名称格式
        backup_name = result['backup_name']
        assert backup_name.startswith('trading_journal_backup_')
        assert len(backup_name) > 20  # 包含时间戳
    
    def test_backup_metadata_content(self, temp_backup_service):
        """测试备份元数据内容"""
        service = temp_backup_service
        
        # 执行备份
        result = service.create_backup('metadata_test')
        assert result['success'] is True
        
        # 读取备份文件中的元数据
        backup_path = Path(result['backup_path'])
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            metadata_content = zipf.read('backup_metadata.json')
            metadata = json.loads(metadata_content.decode('utf-8'))
            
            # 验证元数据内容
            assert metadata['backup_name'] == 'metadata_test'
            assert 'created_at' in metadata
            assert 'database_size' in metadata
            assert 'uploads_count' in metadata
            assert metadata['version'] == '1.0'
            assert metadata['database_size'] > 0
            assert metadata['uploads_count'] == 1
    
    def test_backup_database_integrity(self, temp_backup_service):
        """测试备份数据库完整性"""
        service = temp_backup_service
        
        # 执行备份
        result = service.create_backup('db_integrity_test')
        assert result['success'] is True
        
        # 提取并验证数据库文件
        backup_path = Path(result['backup_path'])
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            db_content = zipf.read('data/trading_journal.db')
            
            # 写入临时文件并验证
            with tempfile.NamedTemporaryFile() as temp_db:
                temp_db.write(db_content)
                temp_db.flush()
                
                # 连接数据库并验证数据
                conn = sqlite3.connect(temp_db.name)
                cursor = conn.cursor()
                
                # 验证表结构
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                assert len(tables) > 0
                assert ('trades',) in tables
                
                # 验证数据内容
                cursor.execute("SELECT * FROM trades")
                rows = cursor.fetchall()
                assert len(rows) == 1
                assert rows[0][1] == '000001'  # stock_code
                assert rows[0][2] == '平安银行'  # stock_name
                
                conn.close()
    
    def test_backup_uploads_integrity(self, temp_backup_service):
        """测试备份上传文件完整性"""
        service = temp_backup_service
        
        # 添加更多测试文件
        test_file2 = service.uploads_dir / 'subdir' / 'test_image2.png'
        test_file2.parent.mkdir(exist_ok=True)
        test_file2.write_bytes(b'another fake image data')
        
        # 执行备份
        result = service.create_backup('uploads_test')
        assert result['success'] is True
        
        # 验证上传文件备份
        backup_path = Path(result['backup_path'])
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            file_list = zipf.namelist()
            
            # 验证文件存在
            assert 'uploads/test_image.png' in file_list
            assert 'uploads/subdir/test_image2.png' in file_list
            
            # 验证文件内容
            content1 = zipf.read('uploads/test_image.png')
            assert content1 == b'fake image data'
            
            content2 = zipf.read('uploads/subdir/test_image2.png')
            assert content2 == b'another fake image data'
    
    def test_restore_backup_basic(self, temp_backup_service):
        """测试基本备份恢复功能"""
        service = temp_backup_service
        
        # 先创建备份
        backup_result = service.create_backup('restore_test')
        assert backup_result['success'] is True
        
        # 修改原始数据
        conn = sqlite3.connect(str(service.db_path))
        conn.execute("DELETE FROM trades")
        conn.commit()
        conn.close()
        
        # 删除上传文件
        (service.uploads_dir / 'test_image.png').unlink()
        
        # 执行恢复
        restore_result = service.restore_backup('restore_test.zip')
        
        # 验证恢复结果
        assert restore_result['success'] is True
        assert 'message' in restore_result
        assert 'uploads_restored' in restore_result
        assert restore_result['uploads_restored'] == 1
        
        # 验证数据库恢复
        conn = sqlite3.connect(str(service.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades")
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][1] == '000001'
        conn.close()
        
        # 验证上传文件恢复
        assert (service.uploads_dir / 'test_image.png').exists()
        content = (service.uploads_dir / 'test_image.png').read_bytes()
        assert content == b'fake image data'
    
    def test_restore_nonexistent_backup(self, temp_backup_service):
        """测试恢复不存在的备份文件"""
        service = temp_backup_service
        
        # 尝试恢复不存在的备份
        result = service.restore_backup('nonexistent.zip')
        
        # 验证错误处理
        assert result['success'] is False
        assert 'error' in result
        assert '备份文件不存在' in result['error']
    
    def test_list_backups_empty(self, temp_backup_service):
        """测试列出空备份目录"""
        service = temp_backup_service
        
        # 列出备份（应该为空）
        result = service.list_backups()
        
        # 验证结果
        assert result['success'] is True
        assert result['backups'] == []
        assert result['total_count'] == 0
        assert result['total_size_mb'] == 0
    
    def test_list_backups_with_files(self, temp_backup_service):
        """测试列出包含文件的备份目录"""
        service = temp_backup_service
        
        # 创建几个备份
        service.create_backup('backup1')
        service.create_backup('backup2')
        
        # 列出备份
        result = service.list_backups()
        
        # 验证结果
        assert result['success'] is True
        assert len(result['backups']) == 2
        assert result['total_count'] == 2
        assert result['total_size_mb'] >= 0
        
        # 验证备份信息
        backup_names = [b['filename'] for b in result['backups']]
        assert 'backup1.zip' in backup_names
        assert 'backup2.zip' in backup_names
        
        # 验证备份详细信息
        for backup in result['backups']:
            assert 'filename' in backup
            assert 'size' in backup
            assert 'created_at' in backup
            assert 'size_mb' in backup
            assert backup['size'] > 0
            assert backup['size_mb'] >= 0
    
    def test_verify_backup_valid(self, temp_backup_service):
        """测试验证有效备份文件"""
        service = temp_backup_service
        
        # 创建备份
        backup_result = service.create_backup('verify_test')
        assert backup_result['success'] is True
        
        # 验证备份
        verify_result = service.verify_backup('verify_test.zip')
        
        # 验证结果
        assert verify_result['success'] is True
        verification = verify_result['verification']
        
        assert verification['filename'] == 'verify_test.zip'
        assert verification['is_valid'] is True
        assert verification['has_database'] is True
        assert verification['has_metadata'] is True
        assert verification['uploads_count'] == 1
        assert verification['database_tables'] > 0
        assert len(verification['errors']) == 0
        
        # 验证元数据
        assert 'metadata' in verification
        metadata = verification['metadata']
        assert metadata['backup_name'] == 'verify_test'
        assert metadata['version'] == '1.0'
    
    def test_verify_backup_invalid(self, temp_backup_service):
        """测试验证无效备份文件"""
        service = temp_backup_service
        
        # 创建无效的ZIP文件
        invalid_backup = service.backup_dir / 'invalid.zip'
        invalid_backup.write_bytes(b'not a valid zip file')
        
        # 验证备份
        verify_result = service.verify_backup('invalid.zip')
        
        # 验证错误处理
        assert verify_result['success'] is False
        assert 'error' in verify_result
    
    def test_verify_backup_missing_database(self, temp_backup_service):
        """测试验证缺少数据库的备份文件"""
        service = temp_backup_service
        
        # 创建只包含上传文件的备份
        backup_path = service.backup_dir / 'no_db.zip'
        with zipfile.ZipFile(backup_path, 'w') as zipf:
            zipf.writestr('uploads/test.png', b'fake data')
            zipf.writestr('backup_metadata.json', json.dumps({
                'backup_name': 'no_db',
                'created_at': datetime.now().isoformat(),
                'version': '1.0'
            }))
        
        # 验证备份
        verify_result = service.verify_backup('no_db.zip')
        
        # 验证结果
        assert verify_result['success'] is True
        verification = verify_result['verification']
        
        assert verification['is_valid'] is False
        assert verification['has_database'] is False
        assert verification['has_metadata'] is True
        assert '缺少数据库文件' in verification['errors']
    
    def test_delete_backup(self, temp_backup_service):
        """测试删除备份文件"""
        service = temp_backup_service
        
        # 创建备份
        backup_result = service.create_backup('delete_test')
        assert backup_result['success'] is True
        
        # 验证文件存在
        backup_path = service.backup_dir / 'delete_test.zip'
        assert backup_path.exists()
        
        # 删除备份
        delete_result = service.delete_backup('delete_test.zip')
        
        # 验证删除结果
        assert delete_result['success'] is True
        assert 'message' in delete_result
        assert not backup_path.exists()
    
    def test_delete_nonexistent_backup(self, temp_backup_service):
        """测试删除不存在的备份文件"""
        service = temp_backup_service
        
        # 尝试删除不存在的备份
        result = service.delete_backup('nonexistent.zip')
        
        # 验证错误处理
        assert result['success'] is False
        assert 'error' in result
        assert '备份文件不存在' in result['error']
    
    def test_cleanup_old_backups(self, temp_backup_service):
        """测试清理过期备份"""
        service = temp_backup_service
        
        # 创建新备份
        service.create_backup('new_backup')
        
        # 创建旧备份（模拟旧文件）
        old_backup = service.backup_dir / 'old_backup.zip'
        old_backup.write_bytes(b'fake old backup')
        
        # 修改文件时间为31天前
        old_time = datetime.now() - timedelta(days=31)
        old_timestamp = old_time.timestamp()
        os.utime(old_backup, (old_timestamp, old_timestamp))
        
        # 执行清理（保留30天）
        cleanup_result = service.cleanup_old_backups(30)
        
        # 验证清理结果
        assert cleanup_result['success'] is True
        assert cleanup_result['deleted_count'] == 1
        assert cleanup_result['deleted_size_mb'] >= 0
        assert cleanup_result['retention_days'] == 30
        
        # 验证文件状态
        assert not old_backup.exists()  # 旧文件被删除
        assert (service.backup_dir / 'new_backup.zip').exists()  # 新文件保留
    
    def test_auto_backup_check_no_backups(self, temp_backup_service):
        """测试自动备份检查（无备份文件）"""
        service = temp_backup_service
        
        # 检查自动备份
        result = service.auto_backup_check()
        
        # 验证结果
        assert result['success'] is True
        assert result['needs_backup'] is True
        assert result['latest_backup'] is None
        assert result['latest_backup_time'] is None
        assert '没有找到任何备份文件' in result['reason']
    
    def test_auto_backup_check_recent_backup(self, temp_backup_service):
        """测试自动备份检查（有最近备份）"""
        service = temp_backup_service
        
        # 创建最近的备份
        service.create_backup('recent_backup')
        
        # 检查自动备份
        result = service.auto_backup_check()
        
        # 验证结果
        assert result['success'] is True
        assert result['needs_backup'] is False
        assert result['latest_backup'] == 'recent_backup.zip'
        assert result['latest_backup_time'] is not None
        assert '暂不需要备份' in result['reason']
    
    def test_auto_backup_check_old_backup(self, temp_backup_service):
        """测试自动备份检查（有过期备份）"""
        service = temp_backup_service
        
        # 创建旧备份
        old_backup = service.backup_dir / 'old_backup.zip'
        old_backup.write_bytes(b'fake old backup')
        
        # 修改文件时间为8天前
        old_time = datetime.now() - timedelta(days=8)
        old_timestamp = old_time.timestamp()
        os.utime(old_backup, (old_timestamp, old_timestamp))
        
        # 检查自动备份
        result = service.auto_backup_check()
        
        # 验证结果
        assert result['success'] is True
        assert result['needs_backup'] is True
        assert result['latest_backup'] == 'old_backup.zip'
        assert result['latest_backup_time'] is not None
        assert '距离上次备份已过去 8 天' in result['reason']


class TestBackupServiceErrorHandling:
    """备份服务错误处理测试"""
    
    @pytest.fixture
    def temp_backup_service(self):
        """创建临时备份服务实例"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 创建临时目录结构
            data_dir = temp_path / 'data'
            backup_dir = temp_path / 'backups'
            uploads_dir = temp_path / 'uploads'
            
            data_dir.mkdir()
            backup_dir.mkdir()
            uploads_dir.mkdir()
            
            # 创建临时数据库
            db_path = data_dir / 'trading_journal.db'
            conn = sqlite3.connect(str(db_path))
            conn.execute('''
                CREATE TABLE trades (
                    id INTEGER PRIMARY KEY,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    trade_type TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                INSERT INTO trades (stock_code, stock_name, trade_type, price, quantity)
                VALUES ('000001', '平安银行', 'buy', 12.50, 1000)
            ''')
            conn.commit()
            conn.close()
            
            # 创建测试上传文件
            test_file = uploads_dir / 'test_image.png'
            test_file.write_bytes(b'fake image data')
            
            # 创建备份服务实例并设置路径
            service = BackupService()
            service.base_dir = temp_path
            service.data_dir = data_dir
            service.backup_dir = backup_dir
            service.uploads_dir = uploads_dir
            service.db_path = db_path
            
            yield service
    
    def test_create_backup_permission_error(self):
        """测试备份创建权限错误"""
        service = BackupService()
        
        # 模拟zipfile创建错误
        with patch('zipfile.ZipFile', side_effect=PermissionError("Permission denied")):
            result = service.create_backup('permission_test')
            
            assert result['success'] is False
            assert 'error' in result
    
    def test_restore_backup_corrupted_zip(self, temp_backup_service):
        """测试恢复损坏的ZIP文件"""
        service = temp_backup_service
        
        # 创建损坏的ZIP文件
        corrupted_backup = service.backup_dir / 'corrupted.zip'
        corrupted_backup.write_bytes(b'corrupted zip data')
        
        # 尝试恢复
        result = service.restore_backup('corrupted.zip')
        
        # 验证错误处理
        assert result['success'] is False
        assert 'error' in result
    
    def test_backup_database_connection_error(self, temp_backup_service):
        """测试数据库连接错误时的备份"""
        service = temp_backup_service
        
        # 删除数据库文件
        service.db_path.unlink()
        
        # 执行备份（应该仍然成功，但不包含数据库）
        result = service.create_backup('no_db_test')
        
        # 验证结果
        assert result['success'] is True
        
        # 验证备份内容
        backup_path = Path(result['backup_path'])
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            file_list = zipf.namelist()
            assert 'data/trading_journal.db' not in file_list
            assert 'backup_metadata.json' in file_list


class TestBackupServiceIntegration:
    """备份服务集成测试"""
    
    @pytest.fixture
    def temp_backup_service(self):
        """创建临时备份服务实例"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 创建临时目录结构
            data_dir = temp_path / 'data'
            backup_dir = temp_path / 'backups'
            uploads_dir = temp_path / 'uploads'
            
            data_dir.mkdir()
            backup_dir.mkdir()
            uploads_dir.mkdir()
            
            # 创建临时数据库
            db_path = data_dir / 'trading_journal.db'
            conn = sqlite3.connect(str(db_path))
            conn.execute('''
                CREATE TABLE trades (
                    id INTEGER PRIMARY KEY,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    trade_type TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                INSERT INTO trades (stock_code, stock_name, trade_type, price, quantity)
                VALUES ('000001', '平安银行', 'buy', 12.50, 1000)
            ''')
            conn.commit()
            conn.close()
            
            # 创建测试上传文件
            test_file = uploads_dir / 'test_image.png'
            test_file.write_bytes(b'fake image data')
            
            # 创建备份服务实例并设置路径
            service = BackupService()
            service.base_dir = temp_path
            service.data_dir = data_dir
            service.backup_dir = backup_dir
            service.uploads_dir = uploads_dir
            service.db_path = db_path
            
            yield service
    
    def test_full_backup_restore_cycle(self, temp_backup_service):
        """测试完整的备份-恢复周期"""
        service = temp_backup_service
        
        # 准备测试数据
        original_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000
        }
        
        # 添加更多数据到数据库
        conn = sqlite3.connect(str(service.db_path))
        conn.execute('''
            INSERT INTO trades (stock_code, stock_name, trade_type, price, quantity)
            VALUES (?, ?, ?, ?, ?)
        ''', (original_data['stock_code'], original_data['stock_name'], 
              original_data['trade_type'], original_data['price'], original_data['quantity']))
        conn.commit()
        conn.close()
        
        # 创建备份
        backup_result = service.create_backup('integration_test')
        assert backup_result['success'] is True
        
        # 验证备份
        verify_result = service.verify_backup('integration_test.zip')
        assert verify_result['success'] is True
        assert verify_result['verification']['is_valid'] is True
        
        # 清空数据
        conn = sqlite3.connect(str(service.db_path))
        conn.execute("DELETE FROM trades")
        conn.commit()
        conn.close()
        
        # 恢复备份
        restore_result = service.restore_backup('integration_test.zip')
        assert restore_result['success'] is True
        
        # 验证恢复的数据
        conn = sqlite3.connect(str(service.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades WHERE stock_code = ?", (original_data['stock_code'],))
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) >= 1
        # 验证数据内容（注意原始数据和新添加的数据）
        found_original = False
        for row in rows:
            if (row[1] == original_data['stock_code'] and 
                row[2] == original_data['stock_name'] and
                row[3] == original_data['trade_type']):
                found_original = True
                break
        assert found_original
    
    def test_backup_with_large_uploads(self, temp_backup_service):
        """测试包含大量上传文件的备份"""
        service = temp_backup_service
        
        # 创建多个测试文件
        for i in range(10):
            test_file = service.uploads_dir / f'test_file_{i}.png'
            test_file.write_bytes(b'fake image data ' * 100)  # 较大的文件
        
        # 创建子目录和文件
        sub_dir = service.uploads_dir / 'subdir'
        sub_dir.mkdir()
        for i in range(5):
            test_file = sub_dir / f'sub_file_{i}.jpg'
            test_file.write_bytes(b'fake sub image data ' * 50)
        
        # 创建备份
        backup_result = service.create_backup('large_uploads_test')
        assert backup_result['success'] is True
        
        # 验证备份
        verify_result = service.verify_backup('large_uploads_test.zip')
        assert verify_result['success'] is True
        verification = verify_result['verification']
        
        assert verification['is_valid'] is True
        assert verification['uploads_count'] == 16  # 1 original + 10 + 5 new files
        
        # 验证备份文件大小
        assert backup_result['size'] > 1000  # 应该有一定大小
    
    def test_concurrent_backup_operations(self, temp_backup_service):
        """测试并发备份操作"""
        import threading
        import time
        
        service = temp_backup_service
        results = []
        
        def create_backup_thread(name):
            time.sleep(0.1)  # 小延迟确保并发
            result = service.create_backup(f'concurrent_{name}')
            results.append(result)
        
        # 创建多个并发备份线程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_backup_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(results) == 3
        for result in results:
            assert result['success'] is True
        
        # 验证所有备份文件都存在
        backup_files = list(service.backup_dir.glob('concurrent_*.zip'))
        assert len(backup_files) == 3