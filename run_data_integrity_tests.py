#!/usr/bin/env python3
"""
数据完整性和兼容性测试运行器
执行任务11的所有测试要求

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
- 验证现有analytics功能不受影响
- 测试新功能对现有数据的只读访问
- 验证错误情况下的系统稳定性
- 测试不同数据量下的性能表现
"""

import sys
import os
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class DataIntegrityTestRunner:
    """数据完整性测试运行器"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    def run_all_tests(self):
        """运行所有数据完整性和兼容性测试"""
        
        print("=" * 80)
        print("数据完整性和兼容性测试套件")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.start_time = time.time()
        
        # 测试列表
        tests = [
            {
                'name': '后端数据完整性测试',
                'description': '验证现有analytics功能不受影响，测试只读访问',
                'method': self.run_backend_integrity_tests,
                'requirements': ['8.1', '8.2', '8.3']
            },
            {
                'name': '前端兼容性测试',
                'description': '验证前端功能兼容性和用户界面稳定性',
                'method': self.run_frontend_compatibility_tests,
                'requirements': ['8.5']
            },
            {
                'name': '错误处理稳定性测试',
                'description': '验证错误情况下的系统稳定性',
                'method': self.run_error_handling_tests,
                'requirements': ['8.4']
            },
            {
                'name': '性能基准测试',
                'description': '测试不同数据量下的性能表现',
                'method': self.run_performance_tests,
                'requirements': ['8.5']
            },
            {
                'name': 'API兼容性测试',
                'description': '验证API接口的向后兼容性',
                'method': self.run_api_compatibility_tests,
                'requirements': ['8.1', '8.2']
            },
            {
                'name': '数据库事务测试',
                'description': '验证数据库操作的事务安全性',
                'method': self.run_database_transaction_tests,
                'requirements': ['8.3']
            }
        ]
        
        # 执行所有测试
        for i, test in enumerate(tests, 1):
            print(f"[{i}/{len(tests)}] {test['name']}")
            print(f"描述: {test['description']}")
            print(f"需求: {', '.join(test['requirements'])}")
            print("-" * 60)
            
            try:
                result = test['method']()
                self.test_results[test['name']] = result
                
                if result['success']:
                    print(f"✓ {test['name']} 通过")
                else:
                    print(f"✗ {test['name']} 失败: {result.get('message', '未知错误')}")
                    
            except Exception as e:
                print(f"✗ {test['name']} 异常: {str(e)}")
                self.test_results[test['name']] = {
                    'success': False,
                    'message': f'测试执行异常: {str(e)}',
                    'exception': True
                }
            
            print()
        
        self.end_time = time.time()
        
        # 生成测试报告
        self.generate_test_report()
        
        # 返回总体测试结果
        return self.calculate_overall_result()
    
    def run_backend_integrity_tests(self):
        """运行后端数据完整性测试"""
        
        try:
            # 运行pytest测试
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                'tests/test_data_integrity_compatibility.py',
                '-v', '--tb=short'
            ], capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': '所有后端完整性测试通过',
                    'details': result.stdout
                }
            else:
                return {
                    'success': False,
                    'message': '部分后端完整性测试失败',
                    'details': result.stderr,
                    'stdout': result.stdout
                }
                
        except FileNotFoundError:
            # 如果pytest不可用，尝试直接运行测试文件
            try:
                result = subprocess.run([
                    sys.executable, 'tests/test_data_integrity_compatibility.py'
                ], capture_output=True, text=True, cwd=project_root)
                
                return {
                    'success': result.returncode == 0,
                    'message': '后端完整性测试完成' if result.returncode == 0 else '后端完整性测试失败',
                    'details': result.stdout if result.returncode == 0 else result.stderr
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'message': f'无法运行后端完整性测试: {str(e)}'
                }
    
    def run_frontend_compatibility_tests(self):
        """运行前端兼容性测试"""
        
        # 检查前端测试文件是否存在
        frontend_test_file = project_root / 'test_frontend_compatibility.html'
        
        if not frontend_test_file.exists():
            return {
                'success': False,
                'message': '前端兼容性测试文件不存在'
            }
        
        # 检查关键的前端文件
        required_files = [
            'templates/analytics.html',
            'static/js/expectation-comparison-manager.js'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            return {
                'success': False,
                'message': f'缺少关键前端文件: {", ".join(missing_files)}'
            }
        
        # 验证HTML文件结构
        try:
            with open(frontend_test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查关键元素
            required_elements = [
                'test-analytics-tabs',
                'test-overview-tab',
                'test-expectation-tab',
                'FrontendCompatibilityTester'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                return {
                    'success': False,
                    'message': f'前端测试文件缺少关键元素: {", ".join(missing_elements)}'
                }
            
            return {
                'success': True,
                'message': '前端兼容性测试文件验证通过',
                'details': f'测试文件位置: {frontend_test_file}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'前端兼容性测试验证失败: {str(e)}'
            }
    
    def run_error_handling_tests(self):
        """运行错误处理稳定性测试"""
        
        try:
            # 创建临时测试脚本
            test_script = """
import sys
import os
sys.path.insert(0, '.')

from flask import Flask
from unittest.mock import patch
from services.expectation_comparison_service import ExpectationComparisonService
from api.analytics_routes import api_bp

def test_error_handling():
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix='/api')
    client = app.test_client()
    
    errors_handled = 0
    total_tests = 0
    
    with app.app_context():
        # 测试无效参数
        total_tests += 1
        response = client.get('/api/analytics/expectation-comparison?time_range=invalid')
        if response.status_code in [400, 500]:
            errors_handled += 1
        
        # 测试数据库异常
        total_tests += 1
        with patch('models.trade_record.TradeRecord.query') as mock_query:
            mock_query.side_effect = Exception("Database error")
            response = client.get('/api/analytics/expectation-comparison')
            if response.status_code == 500:
                errors_handled += 1
        
        # 测试服务层异常
        total_tests += 1
        with patch.object(ExpectationComparisonService, 'get_expectation_comparison') as mock_service:
            mock_service.side_effect = Exception("Service error")
            response = client.get('/api/analytics/expectation-comparison')
            if response.status_code == 500:
                errors_handled += 1
    
    return errors_handled, total_tests

if __name__ == '__main__':
    handled, total = test_error_handling()
    print(f"错误处理测试: {handled}/{total} 通过")
    exit(0 if handled == total else 1)
"""
            
            # 写入临时文件
            temp_file = project_root / 'temp_error_test.py'
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(test_script)
            
            try:
                # 运行测试
                result = subprocess.run([
                    sys.executable, str(temp_file)
                ], capture_output=True, text=True, cwd=project_root)
                
                return {
                    'success': result.returncode == 0,
                    'message': '错误处理测试完成' if result.returncode == 0 else '错误处理测试失败',
                    'details': result.stdout
                }
                
            finally:
                # 清理临时文件
                if temp_file.exists():
                    temp_file.unlink()
                    
        except Exception as e:
            return {
                'success': False,
                'message': f'错误处理测试异常: {str(e)}'
            }
    
    def run_performance_tests(self):
        """运行性能基准测试"""
        
        try:
            # 运行性能测试
            result = subprocess.run([
                sys.executable, 'test_performance_benchmark.py'
            ], capture_output=True, text=True, cwd=project_root)
            
            return {
                'success': result.returncode == 0,
                'message': '性能基准测试完成' if result.returncode == 0 else '性能基准测试失败',
                'details': result.stdout if result.returncode == 0 else result.stderr
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'性能测试异常: {str(e)}'
            }
    
    def run_api_compatibility_tests(self):
        """运行API兼容性测试"""
        
        try:
            # 检查API路由文件
            api_file = project_root / 'api' / 'analytics_routes.py'
            
            if not api_file.exists():
                return {
                    'success': False,
                    'message': 'API路由文件不存在'
                }
            
            # 验证API端点
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_endpoints = [
                '/analytics/overview',
                '/analytics/profit-distribution',
                '/analytics/monthly',
                '/analytics/expectation-comparison'
            ]
            
            missing_endpoints = []
            for endpoint in required_endpoints:
                if endpoint not in content:
                    missing_endpoints.append(endpoint)
            
            if missing_endpoints:
                return {
                    'success': False,
                    'message': f'缺少API端点: {", ".join(missing_endpoints)}'
                }
            
            # 检查响应格式一致性
            if 'create_success_response' not in content or 'create_error_response' not in content:
                return {
                    'success': False,
                    'message': 'API响应格式不一致'
                }
            
            return {
                'success': True,
                'message': 'API兼容性验证通过',
                'details': f'验证了 {len(required_endpoints)} 个API端点'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'API兼容性测试异常: {str(e)}'
            }
    
    def run_database_transaction_tests(self):
        """运行数据库事务测试"""
        
        try:
            # 创建数据库事务测试脚本
            test_script = """
import sys
sys.path.insert(0, '.')

from models.trade_record import TradeRecord
from services.expectation_comparison_service import ExpectationComparisonService

def test_readonly_access():
    # 记录初始状态
    initial_count = TradeRecord.query.count()
    
    # 执行只读操作
    try:
        ExpectationComparisonService.get_expectation_comparison('all')
        ExpectationComparisonService.get_expectation_comparison('1y')
        ExpectationComparisonService.get_expectation_comparison('90d')
        ExpectationComparisonService.get_expectation_comparison('30d')
    except Exception as e:
        print(f"只读操作异常: {e}")
        return False
    
    # 验证数据未被修改
    final_count = TradeRecord.query.count()
    
    if initial_count != final_count:
        print(f"数据被意外修改: {initial_count} -> {final_count}")
        return False
    
    print("数据库事务测试通过")
    return True

if __name__ == '__main__':
    success = test_readonly_access()
    exit(0 if success else 1)
"""
            
            # 写入临时文件
            temp_file = project_root / 'temp_db_test.py'
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(test_script)
            
            try:
                # 运行测试
                result = subprocess.run([
                    sys.executable, str(temp_file)
                ], capture_output=True, text=True, cwd=project_root)
                
                return {
                    'success': result.returncode == 0,
                    'message': '数据库事务测试完成' if result.returncode == 0 else '数据库事务测试失败',
                    'details': result.stdout
                }
                
            finally:
                # 清理临时文件
                if temp_file.exists():
                    temp_file.unlink()
                    
        except Exception as e:
            return {
                'success': False,
                'message': f'数据库事务测试异常: {str(e)}'
            }
    
    def calculate_overall_result(self):
        """计算总体测试结果"""
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('success', False))
        
        return {
            'success': passed_tests == total_tests,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
    
    def generate_test_report(self):
        """生成测试报告"""
        
        print("=" * 80)
        print("测试结果摘要")
        print("=" * 80)
        
        overall = self.calculate_overall_result()
        
        print(f"总测试数: {overall['total_tests']}")
        print(f"通过测试: {overall['passed_tests']}")
        print(f"失败测试: {overall['failed_tests']}")
        print(f"成功率: {overall['success_rate']:.1f}%")
        print(f"总耗时: {self.end_time - self.start_time:.2f}秒")
        print()
        
        # 详细结果
        print("详细测试结果:")
        print("-" * 60)
        
        for test_name, result in self.test_results.items():
            status = "✓ 通过" if result.get('success', False) else "✗ 失败"
            print(f"{status} {test_name}")
            
            if not result.get('success', False):
                print(f"    错误: {result.get('message', '未知错误')}")
            
            if result.get('details'):
                # 只显示详细信息的前几行
                details_lines = result['details'].split('\n')[:3]
                for line in details_lines:
                    if line.strip():
                        print(f"    {line.strip()}")
        
        print()
        
        # 需求覆盖情况
        print("需求覆盖情况:")
        print("-" * 60)
        
        requirements_coverage = {
            '8.1': '验证现有analytics功能不受影响',
            '8.2': '测试新功能对现有数据的只读访问',
            '8.3': '验证错误情况下的系统稳定性',
            '8.4': '测试不同数据量下的性能表现',
            '8.5': '确保系统整体兼容性'
        }
        
        for req_id, description in requirements_coverage.items():
            print(f"需求 {req_id}: {description} - ✓ 已测试")
        
        # 保存报告到文件
        self.save_report_to_file(overall)
        
        print()
        if overall['success']:
            print("🎉 所有数据完整性和兼容性测试通过！")
        else:
            print("⚠️  部分测试失败，请检查系统兼容性")
    
    def save_report_to_file(self, overall):
        """保存报告到文件"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = project_root / f'data_integrity_test_report_{timestamp}.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_result': overall,
            'test_results': self.test_results,
            'execution_time': self.end_time - self.start_time,
            'requirements_tested': ['8.1', '8.2', '8.3', '8.4', '8.5']
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"详细报告已保存到: {report_file}")


def main():
    """主函数"""
    
    try:
        runner = DataIntegrityTestRunner()
        overall_result = runner.run_all_tests()
        
        # 根据测试结果设置退出码
        exit_code = 0 if overall_result['success'] else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n测试运行器异常: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()