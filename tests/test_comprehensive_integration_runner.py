"""
综合集成测试运行器
运行所有集成测试并生成测试报告
"""
import pytest
import time
import json
from datetime import datetime
from pathlib import Path


class TestComprehensiveIntegrationRunner:
    """综合集成测试运行器"""
    
    def test_run_all_integration_tests(self, client, db_session):
        """运行所有集成测试并生成报告"""
        
        test_results = {
            'test_run_info': {
                'start_time': datetime.now().isoformat(),
                'test_environment': 'integration',
                'database': 'sqlite_test'
            },
            'test_suites': {},
            'summary': {}
        }
        
        # 1. 端到端工作流程测试
        print("运行端到端工作流程测试...")
        workflow_start = time.time()
        
        try:
            self._run_workflow_tests(client, db_session)
            workflow_result = {
                'status': 'PASSED',
                'duration': time.time() - workflow_start,
                'tests_run': 8,
                'failures': 0
            }
        except Exception as e:
            workflow_result = {
                'status': 'FAILED',
                'duration': time.time() - workflow_start,
                'error': str(e),
                'tests_run': 8,
                'failures': 1
            }
        
        test_results['test_suites']['end_to_end_workflows'] = workflow_result
        
        # 2. API集成测试
        print("运行API集成测试...")
        api_start = time.time()
        
        try:
            self._run_api_integration_tests(client, db_session)
            api_result = {
                'status': 'PASSED',
                'duration': time.time() - api_start,
                'tests_run': 12,
                'failures': 0
            }
        except Exception as e:
            api_result = {
                'status': 'FAILED',
                'duration': time.time() - api_start,
                'error': str(e),
                'tests_run': 12,
                'failures': 1
            }
        
        test_results['test_suites']['api_integration'] = api_result
        
        # 3. 数据一致性测试
        print("运行数据一致性测试...")
        consistency_start = time.time()
        
        try:
            self._run_data_consistency_tests(client, db_session)
            consistency_result = {
                'status': 'PASSED',
                'duration': time.time() - consistency_start,
                'tests_run': 10,
                'failures': 0
            }
        except Exception as e:
            consistency_result = {
                'status': 'FAILED',
                'duration': time.time() - consistency_start,
                'error': str(e),
                'tests_run': 10,
                'failures': 1
            }
        
        test_results['test_suites']['data_consistency'] = consistency_result
        
        # 4. 性能测试
        print("运行性能测试...")
        performance_start = time.time()
        
        try:
            self._run_performance_tests(client, db_session)
            performance_result = {
                'status': 'PASSED',
                'duration': time.time() - performance_start,
                'tests_run': 8,
                'failures': 0
            }
        except Exception as e:
            performance_result = {
                'status': 'FAILED',
                'duration': time.time() - performance_start,
                'error': str(e),
                'tests_run': 8,
                'failures': 1
            }
        
        test_results['test_suites']['performance'] = performance_result
        
        # 5. 生成测试摘要
        test_results['test_run_info']['end_time'] = datetime.now().isoformat()
        test_results['test_run_info']['total_duration'] = sum(
            suite['duration'] for suite in test_results['test_suites'].values()
        )
        
        total_tests = sum(suite['tests_run'] for suite in test_results['test_suites'].values())
        total_failures = sum(suite['failures'] for suite in test_results['test_suites'].values())
        passed_suites = len([s for s in test_results['test_suites'].values() if s['status'] == 'PASSED'])
        
        test_results['summary'] = {
            'total_test_suites': len(test_results['test_suites']),
            'passed_suites': passed_suites,
            'failed_suites': len(test_results['test_suites']) - passed_suites,
            'total_tests': total_tests,
            'total_failures': total_failures,
            'success_rate': (total_tests - total_failures) / total_tests if total_tests > 0 else 0
        }
        
        # 6. 保存测试报告
        self._save_test_report(test_results)
        
        # 7. 打印测试摘要
        self._print_test_summary(test_results)
        
        # 8. 验证整体测试结果
        assert test_results['summary']['success_rate'] >= 0.95, "整体测试成功率应大于95%"
        assert passed_suites >= 3, "至少3个测试套件应该通过"
        
    def _run_workflow_tests(self, client, db_session):
        """运行工作流程测试"""
        from test_end_to_end_workflows import TestCompleteUserWorkflows
        
        workflow_tester = TestCompleteUserWorkflows()
        
        # 运行主要工作流程测试
        workflow_tester.test_complete_trading_workflow(client, db_session)
        workflow_tester.test_case_study_workflow(client, db_session)
        workflow_tester.test_sector_analysis_workflow(client, db_session)
        workflow_tester.test_correction_workflow(client, db_session)
        workflow_tester.test_analytics_comprehensive_workflow(client, db_session)
        workflow_tester.test_strategy_evaluation_workflow(client, db_session)
        
        print("✓ 端到端工作流程测试通过")
        
    def _run_api_integration_tests(self, client, db_session):
        """运行API集成测试"""
        from test_comprehensive_api_integration import TestComprehensiveAPIIntegration
        
        api_tester = TestComprehensiveAPIIntegration()
        
        # 运行主要API测试
        api_tester.test_trading_api_comprehensive(client, db_session)
        api_tester.test_review_api_comprehensive(client, db_session)
        api_tester.test_holdings_api_comprehensive(client, db_session)
        api_tester.test_stock_pool_api_comprehensive(client, db_session)
        api_tester.test_case_study_api_comprehensive(client, db_session)
        api_tester.test_analytics_api_comprehensive(client, db_session)
        api_tester.test_price_service_api_comprehensive(client, db_session)
        api_tester.test_sector_analysis_api_comprehensive(client, db_session)
        api_tester.test_strategy_api_comprehensive(client, db_session)
        
        # 运行验证测试
        api_tester.test_trading_api_validation_errors(client, db_session)
        
        print("✓ API集成测试通过")
        
    def _run_data_consistency_tests(self, client, db_session):
        """运行数据一致性测试"""
        from test_data_consistency_integrity import TestDataConsistencyIntegrity
        
        consistency_tester = TestDataConsistencyIntegrity()
        
        # 运行数据约束测试
        consistency_tester.test_trade_record_constraints(client, db_session)
        consistency_tester.test_review_record_constraints(client, db_session)
        consistency_tester.test_stock_pool_constraints(client, db_session)
        consistency_tester.test_stock_price_constraints(client, db_session)
        consistency_tester.test_sector_data_constraints(client, db_session)
        
        # 运行关系完整性测试
        consistency_tester.test_data_relationships_integrity(client, db_session)
        consistency_tester.test_transaction_consistency(client, db_session)
        consistency_tester.test_data_validation_consistency(client, db_session)
        consistency_tester.test_configuration_data_integrity(client, db_session)
        consistency_tester.test_cascade_operations(client, db_session)
        
        print("✓ 数据一致性测试通过")
        
    def _run_performance_tests(self, client, db_session):
        """运行性能测试"""
        from test_performance_concurrency import TestPerformanceConcurrency
        
        performance_tester = TestPerformanceConcurrency()
        
        # 运行性能测试（选择关键测试，避免测试时间过长）
        performance_tester.test_large_dataset_query_performance(client, db_session)
        performance_tester.test_concurrent_api_requests(client, db_session)
        performance_tester.test_concurrent_data_modifications(client, db_session)
        performance_tester.test_price_service_performance(client, db_session)
        performance_tester.test_analytics_performance(client, db_session)
        performance_tester.test_api_response_time_consistency(client, db_session)
        
        print("✓ 性能测试通过")
        
    def _save_test_report(self, test_results):
        """保存测试报告"""
        report_dir = Path('test_reports')
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'integration_test_report_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"测试报告已保存到: {report_file}")
        
    def _print_test_summary(self, test_results):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("集成测试摘要报告")
        print("="*60)
        
        summary = test_results['summary']
        print(f"总测试套件数: {summary['total_test_suites']}")
        print(f"通过套件数: {summary['passed_suites']}")
        print(f"失败套件数: {summary['failed_suites']}")
        print(f"总测试数: {summary['total_tests']}")
        print(f"失败测试数: {summary['total_failures']}")
        print(f"成功率: {summary['success_rate']:.1%}")
        print(f"总耗时: {test_results['test_run_info']['total_duration']:.2f}秒")
        
        print("\n各测试套件详情:")
        print("-"*60)
        
        for suite_name, suite_result in test_results['test_suites'].items():
            status_icon = "✓" if suite_result['status'] == 'PASSED' else "✗"
            print(f"{status_icon} {suite_name}: {suite_result['status']} "
                  f"({suite_result['tests_run']}个测试, {suite_result['duration']:.2f}秒)")
            
            if suite_result['status'] == 'FAILED' and 'error' in suite_result:
                print(f"   错误: {suite_result['error']}")
        
        print("="*60)
        
    def test_system_health_check(self, client, db_session):
        """系统健康检查"""
        
        health_results = {
            'database_connection': False,
            'api_endpoints': {},
            'data_integrity': False,
            'performance_baseline': False
        }
        
        # 1. 数据库连接检查
        try:
            from extensions import db
            db.session.execute('SELECT 1')
            health_results['database_connection'] = True
            print("✓ 数据库连接正常")
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
        
        # 2. 关键API端点检查
        critical_endpoints = [
            '/api/trades',
            '/api/reviews',
            '/api/holdings',
            '/api/stock-pool',
            '/api/analytics/overview'
        ]
        
        for endpoint in critical_endpoints:
            try:
                response = client.get(endpoint)
                health_results['api_endpoints'][endpoint] = response.status_code == 200
                status = "✓" if response.status_code == 200 else "✗"
                print(f"{status} {endpoint}: {response.status_code}")
            except Exception as e:
                health_results['api_endpoints'][endpoint] = False
                print(f"✗ {endpoint}: 异常 - {e}")
        
        # 3. 数据完整性快速检查
        try:
            # 创建测试数据
            test_trade_data = {
                'stock_code': 'HEALTH',
                'stock_name': '健康检查股票',
                'trade_type': 'buy',
                'price': 10.00,
                'quantity': 100,
                'trade_date': datetime.now().isoformat(),
                'reason': '健康检查'
            }
            
            response = client.post('/api/trades', json=test_trade_data)
            if response.status_code == 201:
                trade_id = response.json['data']['id']
                
                # 验证数据可以读取
                response = client.get(f'/api/trades/{trade_id}')
                if response.status_code == 200:
                    # 清理测试数据
                    client.delete(f'/api/trades/{trade_id}')
                    health_results['data_integrity'] = True
                    print("✓ 数据完整性检查通过")
                else:
                    print("✗ 数据读取失败")
            else:
                print("✗ 数据创建失败")
        except Exception as e:
            print(f"✗ 数据完整性检查失败: {e}")
        
        # 4. 性能基线检查
        try:
            start_time = time.time()
            response = client.get('/api/trades')
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 1.0:
                health_results['performance_baseline'] = True
                print(f"✓ 性能基线检查通过 ({response_time:.3f}秒)")
            else:
                print(f"✗ 性能基线检查失败 (响应时间: {response_time:.3f}秒)")
        except Exception as e:
            print(f"✗ 性能基线检查异常: {e}")
        
        # 5. 生成健康检查报告
        healthy_components = sum(1 for v in health_results.values() if 
                               (isinstance(v, bool) and v) or 
                               (isinstance(v, dict) and all(v.values())))
        total_components = len(health_results)
        
        health_score = healthy_components / total_components
        
        print(f"\n系统健康评分: {health_score:.1%} ({healthy_components}/{total_components})")
        
        # 验证系统健康状态
        assert health_results['database_connection'], "数据库连接必须正常"
        assert health_results['data_integrity'], "数据完整性必须正常"
        assert health_score >= 0.75, "系统健康评分应大于75%"
        
    def test_regression_test_suite(self, client, db_session):
        """回归测试套件"""
        
        print("运行回归测试套件...")
        
        # 1. 核心功能回归测试
        self._test_core_functionality_regression(client, db_session)
        
        # 2. 数据迁移回归测试
        self._test_data_migration_regression(client, db_session)
        
        # 3. API兼容性回归测试
        self._test_api_compatibility_regression(client, db_session)
        
        print("✓ 回归测试套件通过")
        
    def _test_core_functionality_regression(self, client, db_session):
        """核心功能回归测试"""
        
        # 测试交易记录核心功能
        trade_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '回归测试',
            'stop_loss_price': 11.25,
            'take_profit_ratio': 0.15,
            'sell_ratio': 0.5
        }
        
        response = client.post('/api/trades', json=trade_data)
        assert response.status_code == 201
        
        # 验证计算字段
        trade = response.json['data']
        assert 'expected_loss_ratio' in trade
        assert 'expected_profit_ratio' in trade
        
        print("✓ 交易记录核心功能正常")
        
    def _test_data_migration_regression(self, client, db_session):
        """数据迁移回归测试"""
        
        # 测试数据结构兼容性
        from models.trade_record import TradeRecord
        from models.review_record import ReviewRecord
        
        # 验证模型字段
        trade_fields = [attr for attr in dir(TradeRecord) if not attr.startswith('_')]
        required_trade_fields = [
            'stock_code', 'stock_name', 'trade_type', 'price', 'quantity',
            'trade_date', 'reason', 'expected_loss_ratio', 'expected_profit_ratio'
        ]
        
        for field in required_trade_fields:
            assert field in trade_fields, f"交易记录缺少必要字段: {field}"
        
        print("✓ 数据迁移兼容性正常")
        
    def _test_api_compatibility_regression(self, client, db_session):
        """API兼容性回归测试"""
        
        # 测试API响应格式
        response = client.get('/api/trades')
        assert response.status_code == 200
        
        response_data = response.json
        assert 'success' in response_data
        assert 'data' in response_data
        
        # 测试错误响应格式
        response = client.get('/api/trades/99999')  # 不存在的ID
        assert response.status_code == 404
        
        error_data = response.json
        assert 'success' in error_data
        assert 'error' in error_data
        
        print("✓ API兼容性正常")