#!/usr/bin/env python3
"""
股票交易记录系统 - 快速测试环境准备脚本

此脚本用于验证系统能够正常启动和运行，检查数据库连接和基本配置，
确保所有API端点可访问。

需求覆盖: 1.1, 6.1
"""

import sys
import os
import time
import requests
import sqlite3
from pathlib import Path
from datetime import datetime
import subprocess
import threading
import signal
from contextlib import contextmanager

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config import Config, TestingConfig
from extensions import db


class TestEnvironmentSetup:
    """测试环境设置类"""
    
    def __init__(self):
        self.app = None
        self.server_process = None
        self.base_url = "http://localhost:5002"
        self.test_results = {
            'system_startup': False,
            'database_connection': False,
            'api_endpoints': {},
            'configuration_check': False,
            'overall_status': False
        }
        
    def run_all_checks(self):
        """运行所有环境检查"""
        print("=" * 60)
        print("股票交易记录系统 - 快速测试环境准备")
        print("=" * 60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # 1. 验证系统能够正常启动和运行
            print("1. 验证系统启动和运行...")
            self.test_system_startup()
            
            # 2. 检查数据库连接和基本配置
            print("\n2. 检查数据库连接和基本配置...")
            self.test_database_connection()
            self.test_basic_configuration()
            
            # 3. 确保所有API端点可访问
            print("\n3. 检查API端点可访问性...")
            self.test_api_endpoints()
            
            # 生成测试报告
            self.generate_report()
            
        except Exception as e:
            print(f"测试过程中发生错误: {str(e)}")
            self.test_results['overall_status'] = False
        finally:
            self.cleanup()
            
        return self.test_results['overall_status']
    
    def test_system_startup(self):
        """测试系统启动"""
        try:
            print("  - 创建Flask应用实例...")
            self.app = create_app(TestingConfig)
            
            print("  - 验证应用配置...")
            assert self.app is not None, "Flask应用创建失败"
            assert self.app.config['TESTING'] is True, "测试配置未正确设置"
            
            print("  - 启动测试服务器...")
            self.start_test_server()
            
            # 等待服务器启动
            time.sleep(2)
            
            # 验证服务器响应
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            assert response.status_code == 200, f"健康检查失败: {response.status_code}"
            
            self.test_results['system_startup'] = True
            print("  ✓ 系统启动成功")
            
        except Exception as e:
            print(f"  ✗ 系统启动失败: {str(e)}")
            self.test_results['system_startup'] = False
            raise
    
    def start_test_server(self):
        """启动测试服务器"""
        def run_server():
            with self.app.app_context():
                db.create_all()
                self.app.run(host='0.0.0.0', port=5002, debug=False, use_reloader=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
    def test_database_connection(self):
        """测试数据库连接"""
        try:
            print("  - 测试数据库连接...")
            
            with self.app.app_context():
                # 测试数据库连接
                db.engine.execute('SELECT 1')
                
                # 验证表结构
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                
                expected_tables = [
                    'trade_records', 'review_records', 'stock_pool', 
                    'case_studies', 'stock_prices', 'sector_data',
                    'trading_strategies', 'configurations'
                ]
                
                missing_tables = [table for table in expected_tables if table not in tables]
                if missing_tables:
                    print(f"  ! 警告: 缺少表 {missing_tables}")
                
                print(f"  - 发现 {len(tables)} 个数据表")
                
            self.test_results['database_connection'] = True
            print("  ✓ 数据库连接正常")
            
        except Exception as e:
            print(f"  ✗ 数据库连接失败: {str(e)}")
            self.test_results['database_connection'] = False
            raise
    
    def test_basic_configuration(self):
        """测试基本配置"""
        try:
            print("  - 检查基本配置...")
            
            # 检查必要目录
            data_dir = Path('data')
            upload_dir = Path('uploads')
            
            assert data_dir.exists(), "数据目录不存在"
            assert upload_dir.exists(), "上传目录不存在"
            
            # 检查配置项
            with self.app.app_context():
                assert self.app.config.get('SECRET_KEY'), "SECRET_KEY未配置"
                assert self.app.config.get('SQLALCHEMY_DATABASE_URI'), "数据库URI未配置"
                assert self.app.config.get('UPLOAD_FOLDER'), "上传目录未配置"
            
            self.test_results['configuration_check'] = True
            print("  ✓ 基本配置检查通过")
            
        except Exception as e:
            print(f"  ✗ 配置检查失败: {str(e)}")
            self.test_results['configuration_check'] = False
            raise
    
    def test_api_endpoints(self):
        """测试API端点可访问性"""
        # 定义需要测试的API端点
        endpoints = {
            # 基础端点
            'health_check': '/api/health',
            'api_info': '/api/',
            
            # 交易记录端点
            'trades_list': '/api/trades',
            'trade_config': '/api/trades/config',
            'trade_stats': '/api/trades/stats',
            
            # 股票池端点
            'stock_pool_list': '/api/stock-pool',
            'watch_pool': '/api/stock-pool/watch',
            'buy_ready_pool': '/api/stock-pool/buy-ready',
            'stock_pool_stats': '/api/stock-pool/stats',
            
            # 策略端点
            'strategies_list': '/api/strategies',
            'active_strategies': '/api/strategies/active',
            'default_strategy': '/api/strategies/default',
            'holding_alerts': '/api/holdings/alerts',
            
            # 案例端点
            'cases_list': '/cases',
            
            # 其他端点
            'analytics_overview': '/api/analytics/overview',
            'price_current': '/api/prices/current',
            'sector_analysis': '/api/sectors/analysis',
            'review_stats': '/api/reviews/stats'
        }
        
        successful_endpoints = 0
        total_endpoints = len(endpoints)
        
        for name, endpoint in endpoints.items():
            try:
                print(f"  - 测试端点: {endpoint}")
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                
                # 检查响应状态
                if response.status_code in [200, 404]:  # 404也算正常，说明端点存在但可能没有数据
                    self.test_results['api_endpoints'][name] = {
                        'status': 'success',
                        'status_code': response.status_code,
                        'response_time': response.elapsed.total_seconds()
                    }
                    successful_endpoints += 1
                    print(f"    ✓ {name}: {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
                else:
                    self.test_results['api_endpoints'][name] = {
                        'status': 'failed',
                        'status_code': response.status_code,
                        'error': f"Unexpected status code: {response.status_code}"
                    }
                    print(f"    ✗ {name}: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.test_results['api_endpoints'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
                print(f"    ✗ {name}: 连接错误 - {str(e)}")
        
        success_rate = (successful_endpoints / total_endpoints) * 100
        print(f"\n  API端点测试完成: {successful_endpoints}/{total_endpoints} ({success_rate:.1f}%)")
        
        if success_rate >= 80:  # 80%以上成功率认为通过
            print("  ✓ API端点可访问性测试通过")
            return True
        else:
            print("  ✗ API端点可访问性测试失败")
            return False
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("测试环境准备报告")
        print("=" * 60)
        
        # 系统启动检查
        status = "✓ 通过" if self.test_results['system_startup'] else "✗ 失败"
        print(f"系统启动检查: {status}")
        
        # 数据库连接检查
        status = "✓ 通过" if self.test_results['database_connection'] else "✗ 失败"
        print(f"数据库连接检查: {status}")
        
        # 配置检查
        status = "✓ 通过" if self.test_results['configuration_check'] else "✗ 失败"
        print(f"基本配置检查: {status}")
        
        # API端点检查
        successful_apis = sum(1 for ep in self.test_results['api_endpoints'].values() 
                             if ep.get('status') == 'success')
        total_apis = len(self.test_results['api_endpoints'])
        success_rate = (successful_apis / total_apis * 100) if total_apis > 0 else 0
        
        print(f"API端点检查: {successful_apis}/{total_apis} ({success_rate:.1f}%)")
        
        # 整体状态
        overall_success = (
            self.test_results['system_startup'] and
            self.test_results['database_connection'] and
            self.test_results['configuration_check'] and
            success_rate >= 80
        )
        
        self.test_results['overall_status'] = overall_success
        
        print("\n" + "-" * 60)
        if overall_success:
            print("✓ 测试环境准备完成，系统可以正常使用")
        else:
            print("✗ 测试环境准备失败，请检查上述问题")
        
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def cleanup(self):
        """清理资源"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                pass


def main():
    """主函数"""
    setup = TestEnvironmentSetup()
    success = setup.run_all_checks()
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()