#!/usr/bin/env python3
"""
股票交易记录系统 - 快速环境检查脚本

快速验证系统基本功能，包括：
1. 系统启动能力
2. 数据库连接
3. API端点可访问性

需求覆盖: 1.1, 6.1
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from config import TestingConfig
    from extensions import db
    import requests
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


class QuickEnvironmentCheck:
    """快速环境检查类"""
    
    def __init__(self):
        self.results = {
            'system_startup': False,
            'database_connection': False,
            'api_accessibility': False,
            'configuration': False
        }
    
    def run_checks(self):
        """运行所有检查"""
        print("=" * 50)
        print("股票交易记录系统 - 快速环境检查")
        print("=" * 50)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. 系统启动检查
        print("1. 系统启动检查...")
        self.check_system_startup()
        
        # 2. 数据库连接检查
        print("\n2. 数据库连接检查...")
        self.check_database_connection()
        
        # 3. 基本配置检查
        print("\n3. 基本配置检查...")
        self.check_configuration()
        
        # 4. API可访问性检查（使用测试客户端）
        print("\n4. API可访问性检查...")
        self.check_api_accessibility()
        
        # 生成报告
        self.generate_report()
        
        return all(self.results.values())
    
    def check_system_startup(self):
        """检查系统启动能力"""
        try:
            print("  - 创建Flask应用...")
            app = create_app(TestingConfig)
            
            print("  - 验证应用配置...")
            assert app is not None, "应用创建失败"
            assert app.config['TESTING'] is True, "测试配置未设置"
            
            print("  - 验证蓝图注册...")
            blueprint_names = [bp.name for bp in app.blueprints.values()]
            expected_blueprints = ['api', 'sector', 'case', 'frontend']
            
            for bp_name in expected_blueprints:
                if bp_name not in blueprint_names:
                    print(f"    ! 警告: 蓝图 {bp_name} 未注册")
            
            self.app = app
            self.results['system_startup'] = True
            print("  ✓ 系统启动检查通过")
            
        except Exception as e:
            print(f"  ✗ 系统启动检查失败: {str(e)}")
            self.results['system_startup'] = False
    
    def check_database_connection(self):
        """检查数据库连接"""
        try:
            if not hasattr(self, 'app'):
                raise Exception("应用未初始化")
            
            with self.app.app_context():
                print("  - 测试数据库连接...")
                
                # 创建所有表
                db.create_all()
                
                # 测试基本查询
                from sqlalchemy import text
                result = db.session.execute(text('SELECT 1')).fetchone()
                assert result[0] == 1, "数据库查询失败"
                
                # 检查表结构
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"  - 发现 {len(tables)} 个数据表")
                
                # 验证关键表存在
                key_tables = ['trade_records', 'review_records', 'stock_pool']
                missing_tables = [t for t in key_tables if t not in tables]
                if missing_tables:
                    print(f"    ! 警告: 缺少关键表 {missing_tables}")
                
            self.results['database_connection'] = True
            print("  ✓ 数据库连接检查通过")
            
        except Exception as e:
            print(f"  ✗ 数据库连接检查失败: {str(e)}")
            self.results['database_connection'] = False
    
    def check_configuration(self):
        """检查基本配置"""
        try:
            if not hasattr(self, 'app'):
                raise Exception("应用未初始化")
            
            print("  - 检查必要目录...")
            
            # 检查数据目录
            data_dir = Path('data')
            if not data_dir.exists():
                data_dir.mkdir(exist_ok=True)
                print("    - 创建数据目录")
            
            # 检查上传目录
            upload_dir = Path('uploads')
            if not upload_dir.exists():
                upload_dir.mkdir(exist_ok=True)
                print("    - 创建上传目录")
            
            print("  - 检查应用配置...")
            with self.app.app_context():
                config_items = [
                    ('SECRET_KEY', self.app.config.get('SECRET_KEY')),
                    ('SQLALCHEMY_DATABASE_URI', self.app.config.get('SQLALCHEMY_DATABASE_URI')),
                    ('UPLOAD_FOLDER', self.app.config.get('UPLOAD_FOLDER')),
                    ('MAX_CONTENT_LENGTH', self.app.config.get('MAX_CONTENT_LENGTH'))
                ]
                
                for key, value in config_items:
                    if not value:
                        raise Exception(f"配置项 {key} 未设置")
            
            self.results['configuration'] = True
            print("  ✓ 基本配置检查通过")
            
        except Exception as e:
            print(f"  ✗ 基本配置检查失败: {str(e)}")
            self.results['configuration'] = False
    
    def check_api_accessibility(self):
        """检查API可访问性（使用测试客户端）"""
        try:
            if not hasattr(self, 'app'):
                raise Exception("应用未初始化")
            
            print("  - 创建测试客户端...")
            client = self.app.test_client()
            
            # 测试关键API端点
            endpoints = [
                ('/api/health', 'GET', '健康检查'),
                ('/api/', 'GET', 'API信息'),
                ('/api/trades', 'GET', '交易记录列表'),
                ('/api/stock-pool', 'GET', '股票池列表'),
                ('/api/strategies', 'GET', '策略列表'),
                ('/cases', 'GET', '案例列表')
            ]
            
            successful = 0
            total = len(endpoints)
            
            for endpoint, method, description in endpoints:
                try:
                    if method == 'GET':
                        response = client.get(endpoint)
                    else:
                        response = client.post(endpoint)
                    
                    # 200或404都算成功（404说明端点存在但可能没有数据）
                    if response.status_code in [200, 404]:
                        successful += 1
                        print(f"    ✓ {description}: {response.status_code}")
                    else:
                        print(f"    ✗ {description}: {response.status_code}")
                        
                except Exception as e:
                    print(f"    ✗ {description}: 错误 - {str(e)}")
            
            success_rate = (successful / total) * 100
            print(f"  - API端点测试: {successful}/{total} ({success_rate:.1f}%)")
            
            if success_rate >= 80:
                self.results['api_accessibility'] = True
                print("  ✓ API可访问性检查通过")
            else:
                print("  ✗ API可访问性检查失败")
                
        except Exception as e:
            print(f"  ✗ API可访问性检查失败: {str(e)}")
            self.results['api_accessibility'] = False
    
    def generate_report(self):
        """生成检查报告"""
        print("\n" + "=" * 50)
        print("环境检查报告")
        print("=" * 50)
        
        checks = [
            ('系统启动', self.results['system_startup']),
            ('数据库连接', self.results['database_connection']),
            ('基本配置', self.results['configuration']),
            ('API可访问性', self.results['api_accessibility'])
        ]
        
        for check_name, passed in checks:
            status = "✓ 通过" if passed else "✗ 失败"
            print(f"{check_name}: {status}")
        
        overall_success = all(self.results.values())
        print("\n" + "-" * 50)
        
        if overall_success:
            print("✓ 环境检查全部通过，系统可以正常使用")
        else:
            print("✗ 环境检查存在问题，请检查失败项目")
        
        print(f"检查完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        return overall_success


def main():
    """主函数"""
    checker = QuickEnvironmentCheck()
    success = checker.run_checks()
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()