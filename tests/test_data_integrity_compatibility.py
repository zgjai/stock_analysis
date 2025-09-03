"""
数据完整性和兼容性测试
测试期望对比功能对现有系统的影响

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
- 验证现有analytics功能不受影响
- 测试新功能对现有数据的只读访问
- 验证错误情况下的系统稳定性
- 测试不同数据量下的性能表现
"""

import pytest
import time
import json
from datetime import datetime, timedelta
from flask import Flask
from unittest.mock import patch, MagicMock
from models.trade_record import TradeRecord
from services.analytics_service import AnalyticsService
from services.expectation_comparison_service import ExpectationComparisonService
from api.analytics_routes import api_bp


class TestDataIntegrityCompatibility:
    """数据完整性和兼容性测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.app = Flask(__name__)
        self.app.register_blueprint(api_bp, url_prefix='/api')
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        
        # 记录测试开始时的数据状态
        self.initial_trade_count = self._get_trade_count()
        self.initial_data_checksum = self._calculate_data_checksum()
    
    def teardown_method(self):
        """测试后清理"""
        # 验证数据完整性
        final_trade_count = self._get_trade_count()
        final_data_checksum = self._calculate_data_checksum()
        
        assert final_trade_count == self.initial_trade_count, "交易记录数量发生变化"
        assert final_data_checksum == self.initial_data_checksum, "数据内容发生变化"
    
    def _get_trade_count(self):
        """获取交易记录总数"""
        try:
            return TradeRecord.query.count()
        except Exception:
            return 0
    
    def _calculate_data_checksum(self):
        """计算数据校验和"""
        try:
            trades = TradeRecord.query.all()
            data_str = ""
            for trade in trades:
                data_str += f"{trade.id}{trade.stock_code}{trade.trade_type}{trade.quantity}{trade.price}"
            return hash(data_str)
        except Exception:
            return 0
    
    def test_existing_analytics_functionality_unaffected(self):
        """测试现有analytics功能不受影响 - Requirement 8.1, 8.2"""
        
        # 测试总体统计概览
        with self.app.app_context():
            response = self.client.get('/api/analytics/overview')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'data' in data
        
        # 测试收益分布
        with self.app.app_context():
            response = self.client.get('/api/analytics/profit-distribution')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
        
        # 测试月度统计
        with self.app.app_context():
            current_year = datetime.now().year
            response = self.client.get(f'/api/analytics/monthly?year={current_year}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
        
        # 测试持仓数据
        with self.app.app_context():
            response = self.client.get('/api/analytics/holdings')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
        
        # 测试投资表现指标
        with self.app.app_context():
            response = self.client.get('/api/analytics/performance')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
    
    def test_readonly_data_access(self):
        """测试新功能对现有数据的只读访问 - Requirement 8.3"""
        
        # 记录调用前的数据状态
        initial_count = self._get_trade_count()
        initial_checksum = self._calculate_data_checksum()
        
        # 调用期望对比功能
        with self.app.app_context():
            # 测试不同时间范围
            time_ranges = ['30d', '90d', '1y', 'all']
            
            for time_range in time_ranges:
                response = self.client.get(f'/api/analytics/expectation-comparison?time_range={time_range}')
                
                # 验证响应成功
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                
                # 验证数据未被修改
                current_count = self._get_trade_count()
                current_checksum = self._calculate_data_checksum()
                
                assert current_count == initial_count, f"时间范围 {time_range} 测试后数据数量发生变化"
                assert current_checksum == initial_checksum, f"时间范围 {time_range} 测试后数据内容发生变化"
    
    def test_service_layer_readonly_access(self):
        """测试服务层的只读访问 - Requirement 8.3"""
        
        initial_count = self._get_trade_count()
        initial_checksum = self._calculate_data_checksum()
        
        # 直接调用服务层方法
        with self.app.app_context():
            # 测试期望对比服务
            comparison_data = ExpectationComparisonService.get_expectation_comparison('all')
            assert comparison_data is not None
            
            # 测试分析服务
            overview = AnalyticsService.get_overall_statistics()
            assert overview is not None
            
            distribution = AnalyticsService.get_profit_distribution()
            assert distribution is not None
            
            monthly_stats = AnalyticsService.get_monthly_statistics(datetime.now().year)
            assert monthly_stats is not None
        
        # 验证数据完整性
        final_count = self._get_trade_count()
        final_checksum = self._calculate_data_checksum()
        
        assert final_count == initial_count, "服务层调用后数据数量发生变化"
        assert final_checksum == initial_checksum, "服务层调用后数据内容发生变化"
    
    def test_error_handling_system_stability(self):
        """测试错误情况下的系统稳定性 - Requirement 8.4"""
        
        # 测试无效时间范围参数
        with self.app.app_context():
            response = self.client.get('/api/analytics/expectation-comparison?time_range=invalid')
            # 应该返回错误但不崩溃
            assert response.status_code in [400, 500]
            data = json.loads(response.data)
            assert data['success'] is False
        
        # 测试无效本金参数
        with self.app.app_context():
            response = self.client.get('/api/analytics/expectation-comparison?base_capital=-1000')
            assert response.status_code in [400, 500]
            data = json.loads(response.data)
            assert data['success'] is False
        
        # 测试数据库连接异常情况
        with patch('models.trade_record.TradeRecord.query') as mock_query:
            mock_query.side_effect = Exception("Database connection error")
            
            with self.app.app_context():
                response = self.client.get('/api/analytics/expectation-comparison')
                # 系统应该优雅处理错误
                assert response.status_code == 500
                data = json.loads(response.data)
                assert data['success'] is False
                assert 'error' in data
        
        # 验证错误后系统仍然正常
        with self.app.app_context():
            response = self.client.get('/api/analytics/overview')
            assert response.status_code == 200
    
    def test_performance_with_different_data_volumes(self):
        """测试不同数据量下的性能表现 - Requirement 8.5"""
        
        # 测试小数据量性能
        start_time = time.time()
        with self.app.app_context():
            response = self.client.get('/api/analytics/expectation-comparison?time_range=30d')
            small_data_time = time.time() - start_time
        
        assert response.status_code == 200
        assert small_data_time < 5.0, f"小数据量查询耗时过长: {small_data_time}秒"
        
        # 测试中等数据量性能
        start_time = time.time()
        with self.app.app_context():
            response = self.client.get('/api/analytics/expectation-comparison?time_range=1y')
            medium_data_time = time.time() - start_time
        
        assert response.status_code == 200
        assert medium_data_time < 10.0, f"中等数据量查询耗时过长: {medium_data_time}秒"
        
        # 测试大数据量性能
        start_time = time.time()
        with self.app.app_context():
            response = self.client.get('/api/analytics/expectation-comparison?time_range=all')
            large_data_time = time.time() - start_time
        
        assert response.status_code == 200
        assert large_data_time < 15.0, f"大数据量查询耗时过长: {large_data_time}秒"
        
        # 测试并发访问性能
        import threading
        
        def concurrent_request():
            with self.app.app_context():
                response = self.client.get('/api/analytics/expectation-comparison')
                assert response.status_code == 200
        
        threads = []
        start_time = time.time()
        
        # 创建5个并发请求
        for i in range(5):
            thread = threading.Thread(target=concurrent_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        concurrent_time = time.time() - start_time
        assert concurrent_time < 30.0, f"并发访问耗时过长: {concurrent_time}秒"
    
    def test_memory_usage_stability(self):
        """测试内存使用稳定性"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 执行多次API调用
        with self.app.app_context():
            for i in range(10):
                response = self.client.get('/api/analytics/expectation-comparison')
                assert response.status_code == 200
                
                response = self.client.get('/api/analytics/overview')
                assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存增长不应超过50MB
        assert memory_increase < 50 * 1024 * 1024, f"内存增长过多: {memory_increase / 1024 / 1024:.2f}MB"
    
    def test_data_consistency_across_apis(self):
        """测试不同API之间的数据一致性"""
        
        with self.app.app_context():
            # 获取总体统计
            overview_response = self.client.get('/api/analytics/overview')
            overview_data = json.loads(overview_response.data)['data']
            
            # 获取期望对比数据
            comparison_response = self.client.get('/api/analytics/expectation-comparison')
            comparison_data = json.loads(comparison_response.data)['data']
            
            # 验证数据一致性
            if 'actual' in comparison_data and 'return_rate' in comparison_data['actual']:
                # 总收益率应该一致（允许小的浮点误差）
                overview_rate = overview_data.get('total_return_rate', 0)
                actual_rate = comparison_data['actual']['return_rate']
                
                if overview_rate is not None and actual_rate is not None:
                    rate_diff = abs(overview_rate - actual_rate)
                    assert rate_diff < 0.001, f"收益率数据不一致: {overview_rate} vs {actual_rate}"
    
    def test_tab_switching_compatibility(self):
        """测试Tab切换的兼容性 - Requirement 8.5"""
        
        # 模拟用户在不同tab之间切换
        with self.app.app_context():
            # 访问统计概览tab的数据
            overview_response = self.client.get('/api/analytics/overview')
            assert overview_response.status_code == 200
            
            profit_response = self.client.get('/api/analytics/profit-distribution')
            assert profit_response.status_code == 200
            
            monthly_response = self.client.get('/api/analytics/monthly')
            assert monthly_response.status_code == 200
            
            # 切换到期望对比tab
            expectation_response = self.client.get('/api/analytics/expectation-comparison')
            assert expectation_response.status_code == 200
            
            # 再次访问统计概览tab，确保功能正常
            overview_response2 = self.client.get('/api/analytics/overview')
            assert overview_response2.status_code == 200
            
            # 验证数据一致性
            data1 = json.loads(overview_response.data)
            data2 = json.loads(overview_response2.data)
            assert data1 == data2, "Tab切换后数据不一致"
    
    def test_database_transaction_isolation(self):
        """测试数据库事务隔离性"""
        
        with self.app.app_context():
            # 模拟并发访问
            import threading
            import time
            
            results = []
            errors = []
            
            def api_call(endpoint, results_list, errors_list):
                try:
                    response = self.client.get(endpoint)
                    results_list.append(response.status_code)
                except Exception as e:
                    errors_list.append(str(e))
            
            threads = []
            endpoints = [
                '/api/analytics/overview',
                '/api/analytics/expectation-comparison',
                '/api/analytics/profit-distribution',
                '/api/analytics/monthly'
            ]
            
            # 创建并发请求
            for endpoint in endpoints:
                for _ in range(3):  # 每个端点3个并发请求
                    thread = threading.Thread(
                        target=api_call, 
                        args=(endpoint, results, errors)
                    )
                    threads.append(thread)
            
            # 启动所有线程
            for thread in threads:
                thread.start()
            
            # 等待完成
            for thread in threads:
                thread.join()
            
            # 验证结果
            assert len(errors) == 0, f"并发访问出现错误: {errors}"
            assert all(status == 200 for status in results), f"并发访问状态码异常: {results}"
    
    def test_api_response_format_consistency(self):
        """测试API响应格式一致性"""
        
        with self.app.app_context():
            # 测试所有analytics相关API的响应格式
            endpoints = [
                '/api/analytics/overview',
                '/api/analytics/profit-distribution',
                '/api/analytics/monthly',
                '/api/analytics/holdings',
                '/api/analytics/performance',
                '/api/analytics/expectation-comparison'
            ]
            
            for endpoint in endpoints:
                response = self.client.get(endpoint)
                assert response.status_code == 200
                
                data = json.loads(response.data)
                
                # 验证响应格式一致性
                assert 'success' in data, f"{endpoint} 缺少 success 字段"
                assert 'data' in data, f"{endpoint} 缺少 data 字段"
                assert 'message' in data, f"{endpoint} 缺少 message 字段"
                assert data['success'] is True, f"{endpoint} success 字段不为 True"
    
    def test_error_recovery_capability(self):
        """测试错误恢复能力"""
        
        with self.app.app_context():
            # 先正常调用
            response = self.client.get('/api/analytics/expectation-comparison')
            assert response.status_code == 200
            
            # 模拟错误情况
            with patch('services.expectation_comparison_service.ExpectationComparisonService.get_expectation_comparison') as mock_service:
                mock_service.side_effect = Exception("Temporary error")
                
                response = self.client.get('/api/analytics/expectation-comparison')
                assert response.status_code == 500
            
            # 验证错误后能够恢复
            response = self.client.get('/api/analytics/expectation-comparison')
            assert response.status_code == 200
            
            # 验证其他功能不受影响
            response = self.client.get('/api/analytics/overview')
            assert response.status_code == 200


def run_compatibility_tests():
    """运行兼容性测试的主函数"""
    
    print("开始数据完整性和兼容性测试...")
    
    # 创建测试实例
    test_instance = TestDataIntegrityCompatibility()
    
    try:
        # 运行所有测试
        test_methods = [
            'test_existing_analytics_functionality_unaffected',
            'test_readonly_data_access',
            'test_service_layer_readonly_access',
            'test_error_handling_system_stability',
            'test_performance_with_different_data_volumes',
            'test_memory_usage_stability',
            'test_data_consistency_across_apis',
            'test_tab_switching_compatibility',
            'test_database_transaction_isolation',
            'test_api_response_format_consistency',
            'test_error_recovery_capability'
        ]
        
        results = {}
        
        for method_name in test_methods:
            print(f"执行测试: {method_name}")
            
            try:
                test_instance.setup_method()
                method = getattr(test_instance, method_name)
                method()
                test_instance.teardown_method()
                results[method_name] = "PASSED"
                print(f"✓ {method_name} 通过")
                
            except Exception as e:
                results[method_name] = f"FAILED: {str(e)}"
                print(f"✗ {method_name} 失败: {str(e)}")
        
        # 输出测试结果摘要
        print("\n" + "="*60)
        print("测试结果摘要:")
        print("="*60)
        
        passed_count = sum(1 for result in results.values() if result == "PASSED")
        total_count = len(results)
        
        for test_name, result in results.items():
            status = "✓" if result == "PASSED" else "✗"
            print(f"{status} {test_name}: {result}")
        
        print(f"\n总计: {passed_count}/{total_count} 测试通过")
        
        if passed_count == total_count:
            print("🎉 所有兼容性测试通过！")
            return True
        else:
            print("⚠️  部分测试失败，请检查系统兼容性")
            return False
            
    except Exception as e:
        print(f"测试执行出现异常: {str(e)}")
        return False


if __name__ == '__main__':
    success = run_compatibility_tests()
    exit(0 if success else 1)