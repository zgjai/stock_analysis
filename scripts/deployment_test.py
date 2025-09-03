#!/usr/bin/env python3
"""
生产环境部署测试脚本
"""
import os
import sys
import time
import json
import logging
import requests
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from config import ProductionConfig, DevelopmentConfig
from extensions import db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentTester:
    """部署测试器"""
    
    def __init__(self, base_url='http://localhost:5001', config_class=ProductionConfig):
        self.base_url = base_url.rstrip('/')
        self.config_class = config_class
        self.test_results = []
        
    def log_test_result(self, test_name, success, message="", details=None):
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "PASS" if success else "FAIL"
        logger.info(f"[{status}] {test_name}: {message}")
        
        if details:
            logger.debug(f"Details: {details}")
    
    def test_database_connection(self):
        """测试数据库连接"""
        try:
            app = create_app(self.config_class)
            with app.app_context():
                db.engine.execute(db.text('SELECT 1'))
            
            self.log_test_result(
                "数据库连接测试", 
                True, 
                "数据库连接正常"
            )
            return True
        except Exception as e:
            self.log_test_result(
                "数据库连接测试", 
                False, 
                f"数据库连接失败: {str(e)}"
            )
            return False
    
    def test_database_tables(self):
        """测试数据库表结构"""
        try:
            app = create_app(self.config_class)
            with app.app_context():
                # 检查历史交易记录相关表
                tables_to_check = [
                    'historical_trades',
                    'trade_reviews', 
                    'review_images'
                ]
                
                missing_tables = []
                for table in tables_to_check:
                    result = db.engine.execute(db.text(f"""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='{table}'
                    """)).fetchone()
                    
                    if not result:
                        missing_tables.append(table)
                
                if missing_tables:
                    self.log_test_result(
                        "数据库表结构测试",
                        False,
                        f"缺少表: {', '.join(missing_tables)}"
                    )
                    return False
                else:
                    self.log_test_result(
                        "数据库表结构测试",
                        True,
                        "所有必需的表都存在"
                    )
                    return True
                    
        except Exception as e:
            self.log_test_result(
                "数据库表结构测试",
                False,
                f"检查表结构失败: {str(e)}"
            )
            return False
    
    def test_directory_structure(self):
        """测试目录结构"""
        required_dirs = [
            project_root / 'data',
            project_root / 'logs',
            project_root / 'backups',
            project_root / 'uploads',
            project_root / 'uploads' / 'reviews',
            project_root / 'uploads' / 'reviews' / 'images',
        ]
        
        missing_dirs = []
        for directory in required_dirs:
            if not directory.exists():
                missing_dirs.append(str(directory))
        
        if missing_dirs:
            self.log_test_result(
                "目录结构测试",
                False,
                f"缺少目录: {', '.join(missing_dirs)}"
            )
            return False
        else:
            self.log_test_result(
                "目录结构测试",
                True,
                "所有必需的目录都存在"
            )
            return True
    
    def test_file_permissions(self):
        """测试文件权限"""
        if os.name == 'nt':  # Windows
            self.log_test_result(
                "文件权限测试",
                True,
                "Windows系统，跳过权限检查"
            )
            return True
        
        try:
            # 测试上传目录写权限
            test_file = project_root / 'uploads' / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()
            
            self.log_test_result(
                "文件权限测试",
                True,
                "上传目录写权限正常"
            )
            return True
        except Exception as e:
            self.log_test_result(
                "文件权限测试",
                False,
                f"文件权限测试失败: {str(e)}"
            )
            return False
    
    def test_application_startup(self):
        """测试应用启动"""
        try:
            app = create_app(self.config_class)
            
            # 检查应用配置
            with app.app_context():
                config_checks = [
                    ('SECRET_KEY', app.config.get('SECRET_KEY') != 'dev-secret-key-change-in-production'),
                    ('SQLALCHEMY_DATABASE_URI', bool(app.config.get('SQLALCHEMY_DATABASE_URI'))),
                    ('UPLOAD_FOLDER', Path(app.config.get('UPLOAD_FOLDER', '')).exists()),
                ]
                
                failed_checks = []
                for check_name, check_result in config_checks:
                    if not check_result:
                        failed_checks.append(check_name)
                
                if failed_checks:
                    self.log_test_result(
                        "应用启动测试",
                        False,
                        f"配置检查失败: {', '.join(failed_checks)}"
                    )
                    return False
                else:
                    self.log_test_result(
                        "应用启动测试",
                        True,
                        "应用配置正常"
                    )
                    return True
                    
        except Exception as e:
            self.log_test_result(
                "应用启动测试",
                False,
                f"应用启动失败: {str(e)}"
            )
            return False
    
    def test_api_endpoints(self):
        """测试API端点"""
        if not self._is_server_running():
            self.log_test_result(
                "API端点测试",
                False,
                "服务器未运行，跳过API测试"
            )
            return False
        
        endpoints_to_test = [
            ('/api/historical-trades', 'GET'),
            ('/api/health', 'GET'),  # 如果有健康检查端点
        ]
        
        failed_endpoints = []
        for endpoint, method in endpoints_to_test:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.request(method, url, timeout=10)
                
                if response.status_code not in [200, 404]:  # 404可能是正常的（没有数据）
                    failed_endpoints.append(f"{method} {endpoint} -> {response.status_code}")
                    
            except Exception as e:
                failed_endpoints.append(f"{method} {endpoint} -> {str(e)}")
        
        if failed_endpoints:
            self.log_test_result(
                "API端点测试",
                False,
                f"API端点测试失败: {'; '.join(failed_endpoints)}"
            )
            return False
        else:
            self.log_test_result(
                "API端点测试",
                True,
                "API端点响应正常"
            )
            return True
    
    def test_static_files(self):
        """测试静态文件服务"""
        if not self._is_server_running():
            self.log_test_result(
                "静态文件测试",
                False,
                "服务器未运行，跳过静态文件测试"
            )
            return False
        
        try:
            # 测试CSS文件
            response = requests.get(f"{self.base_url}/static/css/style.css", timeout=10)
            
            if response.status_code == 200:
                self.log_test_result(
                    "静态文件测试",
                    True,
                    "静态文件服务正常"
                )
                return True
            else:
                self.log_test_result(
                    "静态文件测试",
                    False,
                    f"静态文件访问失败: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "静态文件测试",
                False,
                f"静态文件测试失败: {str(e)}"
            )
            return False
    
    def test_security_headers(self):
        """测试安全头"""
        if not self._is_server_running():
            self.log_test_result(
                "安全头测试",
                False,
                "服务器未运行，跳过安全头测试"
            )
            return False
        
        try:
            response = requests.get(self.base_url, timeout=10)
            headers = response.headers
            
            security_checks = [
                ('X-Content-Type-Options', 'nosniff'),
                ('X-Frame-Options', ['DENY', 'SAMEORIGIN']),
                ('X-XSS-Protection', '1; mode=block'),
            ]
            
            missing_headers = []
            for header_name, expected_values in security_checks:
                if header_name not in headers:
                    missing_headers.append(header_name)
                elif isinstance(expected_values, list):
                    if headers[header_name] not in expected_values:
                        missing_headers.append(f"{header_name} (wrong value)")
                elif headers[header_name] != expected_values:
                    missing_headers.append(f"{header_name} (wrong value)")
            
            if missing_headers:
                self.log_test_result(
                    "安全头测试",
                    False,
                    f"缺少或错误的安全头: {', '.join(missing_headers)}"
                )
                return False
            else:
                self.log_test_result(
                    "安全头测试",
                    True,
                    "安全头配置正确"
                )
                return True
                
        except Exception as e:
            self.log_test_result(
                "安全头测试",
                False,
                f"安全头测试失败: {str(e)}"
            )
            return False
    
    def _is_server_running(self):
        """检查服务器是否运行"""
        try:
            response = requests.get(self.base_url, timeout=5)
            return response.status_code < 500
        except:
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始部署测试...")
        
        tests = [
            self.test_database_connection,
            self.test_database_tables,
            self.test_directory_structure,
            self.test_file_permissions,
            self.test_application_startup,
            self.test_api_endpoints,
            self.test_static_files,
            self.test_security_headers,
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # 生成测试报告
        self.generate_test_report()
        
        success_rate = (passed_tests / total_tests) * 100
        logger.info(f"测试完成: {passed_tests}/{total_tests} 通过 ({success_rate:.1f}%)")
        
        return passed_tests == total_tests
    
    def generate_test_report(self):
        """生成测试报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.test_results),
            'passed_tests': sum(1 for r in self.test_results if r['success']),
            'failed_tests': sum(1 for r in self.test_results if not r['success']),
            'test_results': self.test_results
        }
        
        report_file = project_root / 'deployment_test_report.json'
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"测试报告已生成: {report_file}")
        except Exception as e:
            logger.error(f"生成测试报告失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='部署测试脚本')
    parser.add_argument('--env', choices=['development', 'production'], 
                       default='production', help='测试环境')
    parser.add_argument('--base-url', default='http://localhost:5001',
                       help='应用基础URL')
    
    args = parser.parse_args()
    
    # 选择配置
    if args.env == 'production':
        config_class = ProductionConfig
    else:
        config_class = DevelopmentConfig
    
    # 运行测试
    tester = DeploymentTester(args.base_url, config_class)
    success = tester.run_all_tests()
    
    if success:
        logger.info("所有部署测试通过")
        sys.exit(0)
    else:
        logger.error("部分部署测试失败")
        sys.exit(1)


if __name__ == '__main__':
    main()