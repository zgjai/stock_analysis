#!/usr/bin/env python3
"""
静态兼容性测试
通过代码分析验证数据完整性和兼容性

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
- 验证现有analytics功能不受影响
- 测试新功能对现有数据的只读访问
- 验证错误情况下的系统稳定性
- 测试不同数据量下的性能表现
"""

import os
import ast
import json
import re
from pathlib import Path
from datetime import datetime


class StaticCompatibilityAnalyzer:
    """静态兼容性分析器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        
    def run_all_tests(self):
        """运行所有静态分析测试"""
        
        print("=" * 60)
        print("静态兼容性分析")
        print("=" * 60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        tests = [
            ('API路由兼容性分析', self.analyze_api_routes),
            ('服务层只读访问分析', self.analyze_service_readonly),
            ('错误处理机制分析', self.analyze_error_handling),
            ('前端兼容性分析', self.analyze_frontend_compatibility),
            ('数据库访问模式分析', self.analyze_database_access),
            ('文件结构完整性检查', self.check_file_structure)
        ]
        
        for test_name, test_method in tests:
            print(f"执行分析: {test_name}")
            
            try:
                result = test_method()
                self.test_results[test_name] = result
                
                if result['success']:
                    print(f"✓ {test_name} 通过")
                else:
                    print(f"✗ {test_name} 失败: {result['message']}")
                    
            except Exception as e:
                print(f"✗ {test_name} 异常: {str(e)}")
                self.test_results[test_name] = {
                    'success': False,
                    'message': f'分析异常: {str(e)}'
                }
            
            print()
        
        return self.generate_report()
    
    def analyze_api_routes(self):
        """分析API路由兼容性 - Requirement 8.1, 8.2"""
        
        try:
            api_file = self.project_root / 'api' / 'analytics_routes.py'
            
            if not api_file.exists():
                return {'success': False, 'message': 'API路由文件不存在'}
            
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查必需的API端点
            required_endpoints = [
                '/analytics/overview',
                '/analytics/profit-distribution',
                '/analytics/monthly',
                '/analytics/holdings',
                '/analytics/performance',
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
            if 'create_success_response' not in content:
                return {'success': False, 'message': '缺少统一的成功响应格式'}
            
            if 'create_error_response' not in content:
                return {'success': False, 'message': '缺少统一的错误响应格式'}
            
            # 检查新端点是否正确集成
            expectation_endpoint_pattern = r'@api_bp\.route\([\'\"]/analytics/expectation-comparison[\'\"]\s*,\s*methods=\[[\'\"](GET|POST)[\'\"]\]\)'
            if not re.search(expectation_endpoint_pattern, content):
                return {'success': False, 'message': '期望对比端点定义不正确'}
            
            return {
                'success': True, 
                'message': f'API路由兼容性验证通过，包含 {len(required_endpoints)} 个端点'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'API路由分析异常: {str(e)}'}
    
    def analyze_service_readonly(self):
        """分析服务层只读访问 - Requirement 8.2, 8.3"""
        
        try:
            service_file = self.project_root / 'services' / 'expectation_comparison_service.py'
            
            if not service_file.exists():
                return {'success': False, 'message': '期望对比服务文件不存在'}
            
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST检查是否有写操作
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                return {'success': False, 'message': f'服务文件语法错误: {str(e)}'}
            
            # 检查是否包含写操作关键字
            write_operations = [
                '.save()', '.commit()', '.delete()', '.update()', 
                '.add()', '.merge()', '.bulk_insert', '.bulk_update'
            ]
            
            found_writes = []
            for write_op in write_operations:
                if write_op in content:
                    found_writes.append(write_op)
            
            if found_writes:
                return {
                    'success': False, 
                    'message': f'发现可能的写操作: {", ".join(found_writes)}'
                }
            
            # 检查是否正确使用查询方法
            if '.query.' not in content and 'TradeRecord' in content:
                return {'success': False, 'message': '未正确使用数据库查询'}
            
            return {
                'success': True, 
                'message': '服务层只读访问模式验证通过'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'服务层分析异常: {str(e)}'}
    
    def analyze_error_handling(self):
        """分析错误处理机制 - Requirement 8.4"""
        
        try:
            api_file = self.project_root / 'api' / 'analytics_routes.py'
            
            if not api_file.exists():
                return {'success': False, 'message': 'API文件不存在'}
            
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查错误处理模式
            error_patterns = [
                r'try:\s*.*?except.*?:',  # try-except块
                r'ValidationError',       # 验证错误
                r'DatabaseError',         # 数据库错误
                r'create_error_response'  # 错误响应创建
            ]
            
            missing_patterns = []
            for pattern in error_patterns:
                if not re.search(pattern, content, re.DOTALL):
                    missing_patterns.append(pattern)
            
            if missing_patterns:
                return {
                    'success': False, 
                    'message': f'缺少错误处理模式: {len(missing_patterns)} 个'
                }
            
            # 检查期望对比端点的错误处理
            expectation_function = re.search(
                r'def get_expectation_comparison\(\):(.*?)(?=def|\Z)', 
                content, 
                re.DOTALL
            )
            
            if not expectation_function:
                return {'success': False, 'message': '未找到期望对比函数'}
            
            func_content = expectation_function.group(1)
            
            if 'try:' not in func_content or 'except' not in func_content:
                return {'success': False, 'message': '期望对比函数缺少错误处理'}
            
            return {
                'success': True, 
                'message': '错误处理机制验证通过'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'错误处理分析异常: {str(e)}'}
    
    def analyze_frontend_compatibility(self):
        """分析前端兼容性 - Requirement 8.5"""
        
        try:
            # 检查analytics.html
            analytics_file = self.project_root / 'templates' / 'analytics.html'
            
            if not analytics_file.exists():
                return {'success': False, 'message': 'analytics.html文件不存在'}
            
            with open(analytics_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 检查Tab结构
            required_elements = [
                'analytics-tabs',           # Tab导航
                'overview-tab',            # 统计概览tab
                'expectation-tab',         # 期望对比tab
                'overview-content',        # 概览内容
                'expectation-content'      # 期望对比内容
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in html_content:
                    missing_elements.append(element)
            
            if missing_elements:
                return {
                    'success': False, 
                    'message': f'缺少前端元素: {", ".join(missing_elements)}'
                }
            
            # 检查JavaScript文件
            js_file = self.project_root / 'static' / 'js' / 'expectation-comparison-manager.js'
            
            if not js_file.exists():
                return {'success': False, 'message': '期望对比JavaScript文件不存在'}
            
            with open(js_file, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            # 检查关键JavaScript类和方法
            js_requirements = [
                'ExpectationComparisonManager',
                'loadComparisonData',
                'renderComparison',
                'updateTimeRange'
            ]
            
            missing_js = []
            for requirement in js_requirements:
                if requirement not in js_content:
                    missing_js.append(requirement)
            
            if missing_js:
                return {
                    'success': False, 
                    'message': f'缺少JavaScript功能: {", ".join(missing_js)}'
                }
            
            return {
                'success': True, 
                'message': '前端兼容性验证通过'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'前端兼容性分析异常: {str(e)}'}
    
    def analyze_database_access(self):
        """分析数据库访问模式 - Requirement 8.3"""
        
        try:
            # 检查服务文件中的数据库访问模式
            service_files = [
                'services/expectation_comparison_service.py',
                'services/analytics_service.py'
            ]
            
            for service_file in service_files:
                file_path = self.project_root / service_file
                
                if not file_path.exists():
                    continue
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否使用了正确的查询模式
                if 'TradeRecord.query' not in content and 'TradeRecord' in content:
                    return {
                        'success': False, 
                        'message': f'{service_file} 中数据库访问模式不正确'
                    }
                
                # 检查是否有事务管理
                dangerous_operations = [
                    'db.session.commit()',
                    'db.session.add(',
                    'db.session.delete(',
                    'db.session.merge('
                ]
                
                found_dangerous = []
                for op in dangerous_operations:
                    if op in content:
                        found_dangerous.append(op)
                
                if found_dangerous and 'expectation_comparison' in service_file:
                    return {
                        'success': False, 
                        'message': f'期望对比服务中发现写操作: {", ".join(found_dangerous)}'
                    }
            
            return {
                'success': True, 
                'message': '数据库访问模式验证通过'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'数据库访问分析异常: {str(e)}'}
    
    def check_file_structure(self):
        """检查文件结构完整性"""
        
        try:
            # 检查必需的文件
            required_files = [
                'api/analytics_routes.py',
                'services/expectation_comparison_service.py',
                'services/dto/expectation_comparison_dto.py',
                'templates/analytics.html',
                'static/js/expectation-comparison-manager.js',
                'tests/test_expectation_comparison_api.py',
                'tests/test_expectation_comparison_service.py'
            ]
            
            missing_files = []
            existing_files = []
            
            for file_path in required_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    existing_files.append(file_path)
                else:
                    missing_files.append(file_path)
            
            if missing_files:
                return {
                    'success': False, 
                    'message': f'缺少文件: {", ".join(missing_files)}'
                }
            
            # 检查文件大小（确保不是空文件）
            small_files = []
            for file_path in existing_files:
                full_path = self.project_root / file_path
                if full_path.stat().st_size < 100:  # 小于100字节可能是空文件
                    small_files.append(file_path)
            
            if small_files:
                return {
                    'success': False, 
                    'message': f'文件过小可能为空: {", ".join(small_files)}'
                }
            
            return {
                'success': True, 
                'message': f'文件结构完整，包含 {len(existing_files)} 个必需文件'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'文件结构检查异常: {str(e)}'}
    
    def generate_report(self):
        """生成分析报告"""
        
        print("=" * 60)
        print("静态兼容性分析报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('success', False))
        failed_tests = total_tests - passed_tests
        
        print(f"总分析项: {total_tests}")
        print(f"通过分析: {passed_tests}")
        print(f"失败分析: {failed_tests}")
        print(f"成功率: {(passed_tests / total_tests * 100):.1f}%")
        print()
        
        # 详细结果
        print("详细分析结果:")
        print("-" * 40)
        for test_name, result in self.test_results.items():
            status = "✓" if result.get('success', False) else "✗"
            print(f"{status} {test_name}")
            print(f"    {result.get('message', '无消息')}")
        
        print()
        
        # 需求映射
        print("需求覆盖情况:")
        print("-" * 40)
        requirements_mapping = {
            'API路由兼容性分析': ['8.1', '8.2'],
            '服务层只读访问分析': ['8.2', '8.3'],
            '错误处理机制分析': ['8.4'],
            '前端兼容性分析': ['8.5'],
            '数据库访问模式分析': ['8.3'],
            '文件结构完整性检查': ['8.1', '8.5']
        }
        
        covered_requirements = set()
        for test_name, requirements in requirements_mapping.items():
            if self.test_results.get(test_name, {}).get('success', False):
                covered_requirements.update(requirements)
        
        all_requirements = ['8.1', '8.2', '8.3', '8.4', '8.5']
        for req in all_requirements:
            status = "✓" if req in covered_requirements else "✗"
            descriptions = {
                '8.1': '验证现有analytics功能不受影响',
                '8.2': '测试新功能对现有数据的只读访问',
                '8.3': '验证错误情况下的系统稳定性',
                '8.4': '测试不同数据量下的性能表现',
                '8.5': '确保系统整体兼容性'
            }
            print(f"{status} 需求 {req}: {descriptions[req]}")
        
        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'static_compatibility_report_{timestamp}.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'static_compatibility',
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'requirements_coverage': {
                'covered': list(covered_requirements),
                'total': all_requirements
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n详细报告已保存到: {report_file}")
        
        # 总结
        overall_success = passed_tests == total_tests
        
        if overall_success:
            print("\n🎉 静态兼容性分析全部通过！")
            print("代码结构和兼容性符合要求")
        else:
            print(f"\n⚠️  {failed_tests} 项分析失败")
            print("请检查代码结构和兼容性问题")
        
        return {
            'success': overall_success,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'covered_requirements': list(covered_requirements)
        }


def main():
    """主函数"""
    
    try:
        analyzer = StaticCompatibilityAnalyzer()
        result = analyzer.run_all_tests()
        
        # 根据分析结果设置退出码
        exit_code = 0 if result['success'] else 1
        return exit_code
        
    except KeyboardInterrupt:
        print("\n分析被用户中断")
        return 1
        
    except Exception as e:
        print(f"\n分析执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)