"""
复盘功能增强测试运行器
统一运行所有集成测试和端到端测试，生成测试报告
"""
import pytest
import json
import time
import sys
from datetime import datetime
from pathlib import Path


class TestReviewEnhancementsRunner:
    """复盘功能增强测试运行器"""
    
    def __init__(self):
        self.test_results = {
            'start_time': None,
            'end_time': None,
            'total_duration': 0,
            'test_suites': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'skipped': 0,
                'success_rate': 0.0
            },
            'coverage': {
                'holding_days_editing': {'tested': False, 'passed': False},
                'review_saving': {'tested': False, 'passed': False},
                'floating_profit_calculation': {'tested': False, 'passed': False},
                'error_handling': {'tested': False, 'passed': False},
                'data_consistency': {'tested': False, 'passed': False},
                'end_to_end_workflows': {'tested': False, 'passed': False}
            }
        }
    
    def run_all_tests(self):
        """运行所有复盘功能增强测试"""
        print("=" * 80)
        print("复盘功能增强 - 集成测试和端到端测试")
        print("=" * 80)
        
        self.test_results['start_time'] = datetime.now()
        
        try:
            # 运行集成测试
            self._run_integration_tests()
            
            # 运行端到端测试
            self._run_e2e_tests()
            
            # 运行性能测试
            self._run_performance_tests()
            
            # 生成测试报告
            self._generate_report()
            
        except Exception as e:
            print(f"测试运行过程中发生错误: {e}")
            self.test_results['summary']['errors'] += 1
        
        finally:
            self.test_results['end_time'] = datetime.now()
            self.test_results['total_duration'] = (
                self.test_results['end_time'] - self.test_results['start_time']
            ).total_seconds()
            
            # 保存测试结果
            self._save_test_results()
    
    def _run_integration_tests(self):
        """运行集成测试"""
        print("\n" + "=" * 60)
        print("运行集成测试")
        print("=" * 60)
        
        integration_test_modules = [
            'tests.test_review_enhancements_integration::TestHoldingDaysEditingIntegration',
            'tests.test_review_enhancements_integration::TestReviewSaveIntegration',
            'tests.test_review_enhancements_integration::TestFloatingProfitCalculationIntegration',
            'tests.test_review_enhancements_integration::TestErrorHandlingAndBoundaryConditions',
            'tests.test_review_enhancements_integration::TestDataConsistencyAndIntegrity'
        ]
        
        for module in integration_test_modules:
            print(f"\n运行测试模块: {module}")
            result = self._run_pytest_module(module)
            
            module_name = module.split('::')[-1]
            self.test_results['test_suites'][module_name] = result
            
            # 更新覆盖率信息
            self._update_coverage_info(module_name, result)
    
    def _run_e2e_tests(self):
        """运行端到端测试"""
        print("\n" + "=" * 60)
        print("运行端到端测试")
        print("=" * 60)
        
        e2e_test_modules = [
            'tests.test_review_enhancements_e2e::TestReviewEnhancementsE2E::test_complete_review_workflow_e2e',
            'tests.test_review_enhancements_e2e::TestReviewEnhancementsE2E::test_error_recovery_workflow_e2e',
            'tests.test_review_enhancements_e2e::TestReviewEnhancementsE2E::test_concurrent_user_operations_e2e'
        ]
        
        for module in e2e_test_modules:
            print(f"\n运行端到端测试: {module}")
            result = self._run_pytest_module(module)
            
            test_name = module.split('::')[-1]
            self.test_results['test_suites'][test_name] = result
            
            # 更新覆盖率信息
            if 'complete_review_workflow' in test_name:
                self.test_results['coverage']['end_to_end_workflows']['tested'] = True
                self.test_results['coverage']['end_to_end_workflows']['passed'] = result['passed'] > 0
    
    def _run_performance_tests(self):
        """运行性能测试"""
        print("\n" + "=" * 60)
        print("运行性能测试")
        print("=" * 60)
        
        performance_test_modules = [
            'tests.test_review_enhancements_e2e::TestReviewEnhancementsE2E::test_performance_under_load_e2e'
        ]
        
        for module in performance_test_modules:
            print(f"\n运行性能测试: {module}")
            result = self._run_pytest_module(module)
            
            test_name = f"performance_{module.split('::')[-1]}"
            self.test_results['test_suites'][test_name] = result
    
    def _run_pytest_module(self, module_path):
        """运行单个pytest模块"""
        import subprocess
        
        try:
            # 运行pytest命令
            cmd = [
                sys.executable, '-m', 'pytest',
                module_path,
                '-v',
                '--tb=short',
                '--json-report',
                '--json-report-file=/tmp/pytest_report.json'
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            duration = time.time() - start_time
            
            # 解析结果
            test_result = {
                'duration': duration,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'skipped': 0
            }
            
            # 尝试解析JSON报告
            try:
                with open('/tmp/pytest_report.json', 'r') as f:
                    json_report = json.load(f)
                    
                test_result.update({
                    'passed': json_report.get('summary', {}).get('passed', 0),
                    'failed': json_report.get('summary', {}).get('failed', 0),
                    'errors': json_report.get('summary', {}).get('error', 0),
                    'skipped': json_report.get('summary', {}).get('skipped', 0)
                })
            except (FileNotFoundError, json.JSONDecodeError):
                # 如果JSON报告不可用，从stdout解析
                self._parse_stdout_results(result.stdout, test_result)
            
            # 更新总计
            self.test_results['summary']['total_tests'] += (
                test_result['passed'] + test_result['failed'] + 
                test_result['errors'] + test_result['skipped']
            )
            self.test_results['summary']['passed'] += test_result['passed']
            self.test_results['summary']['failed'] += test_result['failed']
            self.test_results['summary']['errors'] += test_result['errors']
            self.test_results['summary']['skipped'] += test_result['skipped']
            
            # 打印结果
            status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
            print(f"  {status} - 耗时: {duration:.2f}s")
            print(f"  通过: {test_result['passed']}, 失败: {test_result['failed']}, "
                  f"错误: {test_result['errors']}, 跳过: {test_result['skipped']}")
            
            if result.returncode != 0 and result.stderr:
                print(f"  错误信息: {result.stderr[:200]}...")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print("  ⏰ 测试超时")
            return {
                'duration': 300,
                'return_code': -1,
                'stdout': '',
                'stderr': 'Test timeout',
                'passed': 0,
                'failed': 1,
                'errors': 0,
                'skipped': 0
            }
        except Exception as e:
            print(f"  ❌ 运行测试时发生错误: {e}")
            return {
                'duration': 0,
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'passed': 0,
                'failed': 0,
                'errors': 1,
                'skipped': 0
            }
    
    def _parse_stdout_results(self, stdout, test_result):
        """从stdout解析测试结果"""
        lines = stdout.split('\n')
        
        for line in lines:
            if 'passed' in line and 'failed' in line:
                # 查找类似 "5 passed, 2 failed" 的行
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        try:
                            test_result['passed'] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'failed' and i > 0:
                        try:
                            test_result['failed'] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'error' and i > 0:
                        try:
                            test_result['errors'] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'skipped' and i > 0:
                        try:
                            test_result['skipped'] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
    
    def _update_coverage_info(self, module_name, result):
        """更新测试覆盖率信息"""
        coverage_mapping = {
            'TestHoldingDaysEditingIntegration': 'holding_days_editing',
            'TestReviewSaveIntegration': 'review_saving',
            'TestFloatingProfitCalculationIntegration': 'floating_profit_calculation',
            'TestErrorHandlingAndBoundaryConditions': 'error_handling',
            'TestDataConsistencyAndIntegrity': 'data_consistency'
        }
        
        coverage_key = coverage_mapping.get(module_name)
        if coverage_key:
            self.test_results['coverage'][coverage_key]['tested'] = True
            self.test_results['coverage'][coverage_key]['passed'] = (
                result['passed'] > 0 and result['failed'] == 0 and result['errors'] == 0
            )
    
    def _generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 80)
        print("测试报告")
        print("=" * 80)
        
        # 计算成功率
        total_tests = self.test_results['summary']['total_tests']
        if total_tests > 0:
            self.test_results['summary']['success_rate'] = (
                self.test_results['summary']['passed'] / total_tests * 100
            )
        
        # 打印总体统计
        summary = self.test_results['summary']
        print(f"\n📊 总体统计:")
        print(f"  总测试数: {summary['total_tests']}")
        print(f"  通过: {summary['passed']} ✅")
        print(f"  失败: {summary['failed']} ❌")
        print(f"  错误: {summary['errors']} 💥")
        print(f"  跳过: {summary['skipped']} ⏭️")
        print(f"  成功率: {summary['success_rate']:.1f}%")
        print(f"  总耗时: {self.test_results['total_duration']:.2f}秒")
        
        # 打印功能覆盖率
        print(f"\n🎯 功能覆盖率:")
        coverage = self.test_results['coverage']
        
        coverage_items = [
            ('持仓天数编辑', 'holding_days_editing'),
            ('复盘保存功能', 'review_saving'),
            ('浮盈计算', 'floating_profit_calculation'),
            ('错误处理', 'error_handling'),
            ('数据一致性', 'data_consistency'),
            ('端到端工作流', 'end_to_end_workflows')
        ]
        
        for name, key in coverage_items:
            info = coverage[key]
            if info['tested']:
                status = "✅ 通过" if info['passed'] else "❌ 失败"
            else:
                status = "⏭️ 未测试"
            print(f"  {name}: {status}")
        
        # 打印详细的测试套件结果
        print(f"\n📋 详细测试结果:")
        for suite_name, result in self.test_results['test_suites'].items():
            status = "✅" if result['return_code'] == 0 else "❌"
            print(f"  {status} {suite_name}")
            print(f"    耗时: {result['duration']:.2f}s")
            print(f"    通过/失败/错误/跳过: {result['passed']}/{result['failed']}/{result['errors']}/{result['skipped']}")
            
            if result['return_code'] != 0 and result['stderr']:
                print(f"    错误: {result['stderr'][:100]}...")
        
        # 打印建议
        self._print_recommendations()
    
    def _print_recommendations(self):
        """打印测试建议"""
        print(f"\n💡 建议:")
        
        summary = self.test_results['summary']
        coverage = self.test_results['coverage']
        
        if summary['failed'] > 0 or summary['errors'] > 0:
            print("  ⚠️  存在失败或错误的测试，请检查具体错误信息并修复")
        
        untested_features = [
            name for name, info in [
                ('持仓天数编辑', coverage['holding_days_editing']),
                ('复盘保存功能', coverage['review_saving']),
                ('浮盈计算', coverage['floating_profit_calculation']),
                ('错误处理', coverage['error_handling']),
                ('数据一致性', coverage['data_consistency']),
                ('端到端工作流', coverage['end_to_end_workflows'])
            ] if not info['tested']
        ]
        
        if untested_features:
            print(f"  📝 以下功能尚未测试: {', '.join(untested_features)}")
        
        failed_features = [
            name for name, info in [
                ('持仓天数编辑', coverage['holding_days_editing']),
                ('复盘保存功能', coverage['review_saving']),
                ('浮盈计算', coverage['floating_profit_calculation']),
                ('错误处理', coverage['error_handling']),
                ('数据一致性', coverage['data_consistency']),
                ('端到端工作流', coverage['end_to_end_workflows'])
            ] if info['tested'] and not info['passed']
        ]
        
        if failed_features:
            print(f"  🔧 以下功能测试失败，需要修复: {', '.join(failed_features)}")
        
        if summary['success_rate'] >= 95:
            print("  🎉 测试通过率优秀！")
        elif summary['success_rate'] >= 80:
            print("  👍 测试通过率良好，建议进一步优化")
        else:
            print("  ⚠️  测试通过率较低，需要重点关注和改进")
        
        # 性能建议
        total_duration = self.test_results['total_duration']
        if total_duration > 60:
            print("  ⏱️  测试执行时间较长，考虑优化测试性能")
        elif total_duration < 10:
            print("  ⚡ 测试执行速度很快！")
    
    def _save_test_results(self):
        """保存测试结果到文件"""
        try:
            # 创建测试报告目录
            report_dir = Path('test_reports')
            report_dir.mkdir(exist_ok=True)
            
            # 生成报告文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = report_dir / f'review_enhancements_test_report_{timestamp}.json'
            
            # 转换datetime对象为字符串
            results_copy = self.test_results.copy()
            if results_copy['start_time']:
                results_copy['start_time'] = results_copy['start_time'].isoformat()
            if results_copy['end_time']:
                results_copy['end_time'] = results_copy['end_time'].isoformat()
            
            # 保存到JSON文件
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results_copy, f, ensure_ascii=False, indent=2)
            
            print(f"\n📄 测试报告已保存到: {report_file}")
            
        except Exception as e:
            print(f"⚠️  保存测试报告时发生错误: {e}")


def run_review_enhancements_tests():
    """运行复盘功能增强测试的主函数"""
    runner = TestReviewEnhancementsRunner()
    runner.run_all_tests()
    
    # 返回测试是否成功
    summary = runner.test_results['summary']
    return summary['failed'] == 0 and summary['errors'] == 0


if __name__ == '__main__':
    success = run_review_enhancements_tests()
    sys.exit(0 if success else 1)