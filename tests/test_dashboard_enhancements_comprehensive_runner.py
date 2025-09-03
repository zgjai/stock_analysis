"""
仪表板交易增强功能综合测试运行器
执行所有相关测试用例并生成测试报告
"""
import pytest
import json
import sys
from datetime import datetime
from pathlib import Path


class DashboardEnhancementsTestRunner:
    """仪表板增强功能测试运行器"""
    
    def __init__(self):
        self.test_modules = [
            'tests.test_dashboard_revenue_metrics_integration',
            'tests.test_trading_entry_workflow_e2e',
            'tests.test_non_trading_day_functionality',
            'tests.test_profit_distribution_analysis_accuracy',
            'tests.test_holding_days_calculation_edge_cases'
        ]
        
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_modules': {},
            'coverage_summary': {},
            'performance_metrics': {}
        }
    
    def run_comprehensive_tests(self):
        """运行所有综合测试"""
        print("开始执行仪表板交易增强功能综合测试...")
        print("=" * 60)
        
        # 运行每个测试模块
        for module in self.test_modules:
            print(f"\n执行测试模块: {module}")
            print("-" * 40)
            
            # 使用pytest运行测试
            result = pytest.main([
                '-v',
                '--tb=short',
                '--json-report',
                '--json-report-file=temp_test_report.json',
                module.replace('.', '/')
            ])
            
            # 读取测试结果
            self._process_test_results(module, result)
        
        # 生成最终报告
        self._generate_final_report()
        
        return self.test_results
    
    def _process_test_results(self, module, result_code):
        """处理单个模块的测试结果"""
        try:
            # 读取pytest生成的JSON报告
            with open('temp_test_report.json', 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # 提取测试统计信息
            summary = report_data.get('summary', {})
            
            module_results = {
                'total': summary.get('total', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0),
                'skipped': summary.get('skipped', 0),
                'duration': report_data.get('duration', 0),
                'tests': []
            }
            
            # 提取详细测试信息
            for test in report_data.get('tests', []):
                test_info = {
                    'name': test.get('nodeid', ''),
                    'outcome': test.get('outcome', ''),
                    'duration': test.get('duration', 0),
                    'setup_duration': test.get('setup', {}).get('duration', 0),
                    'call_duration': test.get('call', {}).get('duration', 0),
                    'teardown_duration': test.get('teardown', {}).get('duration', 0)
                }
                
                if test.get('outcome') == 'failed':
                    test_info['error'] = test.get('call', {}).get('longrepr', '')
                
                module_results['tests'].append(test_info)
            
            # 更新总体统计
            self.test_results['total_tests'] += module_results['total']
            self.test_results['passed_tests'] += module_results['passed']
            self.test_results['failed_tests'] += module_results['failed']
            self.test_results['skipped_tests'] += module_results['skipped']
            
            # 保存模块结果
            self.test_results['test_modules'][module] = module_results
            
            # 打印模块结果摘要
            print(f"模块测试完成:")
            print(f"  总计: {module_results['total']}")
            print(f"  通过: {module_results['passed']}")
            print(f"  失败: {module_results['failed']}")
            print(f"  跳过: {module_results['skipped']}")
            print(f"  耗时: {module_results['duration']:.2f}秒")
            
        except FileNotFoundError:
            print(f"警告: 无法读取模块 {module} 的测试报告")
            self.test_results['test_modules'][module] = {
                'error': '无法读取测试报告',
                'result_code': result_code
            }
        except Exception as e:
            print(f"处理模块 {module} 测试结果时出错: {str(e)}")
            self.test_results['test_modules'][module] = {
                'error': str(e),
                'result_code': result_code
            }
    
    def _generate_final_report(self):
        """生成最终测试报告"""
        print("\n" + "=" * 60)
        print("综合测试报告")
        print("=" * 60)
        
        # 总体统计
        print(f"\n总体测试统计:")
        print(f"  总测试数: {self.test_results['total_tests']}")
        print(f"  通过数量: {self.test_results['passed_tests']}")
        print(f"  失败数量: {self.test_results['failed_tests']}")
        print(f"  跳过数量: {self.test_results['skipped_tests']}")
        
        if self.test_results['total_tests'] > 0:
            pass_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100
            print(f"  通过率: {pass_rate:.1f}%")
        
        # 各模块详细结果
        print(f"\n各模块测试结果:")
        for module, results in self.test_results['test_modules'].items():
            if 'error' in results:
                print(f"  {module}: 错误 - {results['error']}")
            else:
                print(f"  {module}:")
                print(f"    通过: {results['passed']}/{results['total']}")
                print(f"    耗时: {results['duration']:.2f}秒")
        
        # 失败测试详情
        failed_tests = []
        for module, results in self.test_results['test_modules'].items():
            if 'tests' in results:
                for test in results['tests']:
                    if test['outcome'] == 'failed':
                        failed_tests.append({
                            'module': module,
                            'test': test['name'],
                            'error': test.get('error', '未知错误')
                        })
        
        if failed_tests:
            print(f"\n失败测试详情:")
            for failed in failed_tests:
                print(f"  模块: {failed['module']}")
                print(f"  测试: {failed['test']}")
                print(f"  错误: {failed['error'][:200]}...")
                print()
        
        # 性能分析
        self._analyze_performance()
        
        # 保存详细报告到文件
        self._save_detailed_report()
    
    def _analyze_performance(self):
        """分析测试性能"""
        print(f"\n性能分析:")
        
        total_duration = 0
        slowest_tests = []
        
        for module, results in self.test_results['test_modules'].items():
            if 'tests' in results:
                total_duration += results.get('duration', 0)
                
                for test in results['tests']:
                    if test['duration'] > 1.0:  # 超过1秒的测试
                        slowest_tests.append({
                            'module': module,
                            'test': test['name'],
                            'duration': test['duration']
                        })
        
        print(f"  总执行时间: {total_duration:.2f}秒")
        
        if slowest_tests:
            print(f"  慢速测试 (>1秒):")
            slowest_tests.sort(key=lambda x: x['duration'], reverse=True)
            for slow_test in slowest_tests[:5]:  # 显示最慢的5个
                print(f"    {slow_test['test']}: {slow_test['duration']:.2f}秒")
        
        self.test_results['performance_metrics'] = {
            'total_duration': total_duration,
            'slowest_tests': slowest_tests[:10]  # 保存最慢的10个
        }
    
    def _save_detailed_report(self):
        """保存详细报告到文件"""
        report_file = f"dashboard_enhancements_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            print(f"\n详细测试报告已保存到: {report_file}")
            
        except Exception as e:
            print(f"保存测试报告时出错: {str(e)}")
    
    def run_specific_test_category(self, category):
        """运行特定类别的测试"""
        category_modules = {
            'revenue': ['tests.test_dashboard_revenue_metrics_integration'],
            'trading': ['tests.test_trading_entry_workflow_e2e'],
            'non_trading_days': ['tests.test_non_trading_day_functionality'],
            'profit_distribution': ['tests.test_profit_distribution_analysis_accuracy'],
            'holding_days': ['tests.test_holding_days_calculation_edge_cases']
        }
        
        if category not in category_modules:
            print(f"未知的测试类别: {category}")
            print(f"可用类别: {list(category_modules.keys())}")
            return
        
        print(f"执行 {category} 类别的测试...")
        
        original_modules = self.test_modules
        self.test_modules = category_modules[category]
        
        try:
            return self.run_comprehensive_tests()
        finally:
            self.test_modules = original_modules


def main():
    """主函数"""
    runner = DashboardEnhancementsTestRunner()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        category = sys.argv[1]
        results = runner.run_specific_test_category(category)
    else:
        results = runner.run_comprehensive_tests()
    
    # 根据测试结果设置退出码
    if results['failed_tests'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()