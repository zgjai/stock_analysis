"""
历史交易记录功能性能测试
验证系统在大量数据和并发请求下的响应时间
"""
import pytest
import time
import json
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from models import TradingRecord, HistoricalTrade, TradeReview
from services.historical_trade_service import HistoricalTradeService


class TestHistoricalTradingPerformance:
    """历史交易记录性能测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.performance_threshold = 3.0  # 3秒响应时间阈值
        self.large_dataset_size = 1000    # 大数据集大小
        self.concurrent_requests = 10     # 并发请求数
    
    def create_large_dataset(self, db_session, size=1000):
        """创建大量测试数据"""
        records = []
        base_date = datetime(2024, 1, 1)
        
        for i in range(size):
            stock_code = f"{i:06d}"
            stock_name = f"测试股票{i}"
            
            # 买入记录
            buy_record = TradingRecord(
                stock_code=stock_code,
                stock_name=stock_name,
                trade_type='buy',
                price=10.00 + (i % 50),
                quantity=1000,
                trade_date=base_date + timedelta(days=i),
                reason='测试买入'
            )
            
            # 卖出记录
            sell_record = TradingRecord(
                stock_code=stock_code,
                stock_name=stock_name,
                trade_type='sell',
                price=12.00 + (i % 50),
                quantity=1000,
                trade_date=base_date + timedelta(days=i + 10),
                reason='测试卖出',
                sell_ratio=1.0
            )
            
            records.extend([buy_record, sell_record])
        
        # 批量插入
        db_session.bulk_save_objects(records)
        db_session.commit()
        
        return size
    
    def measure_execution_time(self, func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    
    def test_large_dataset_sync_performance(self, client, db_session):
        """测试大数据集同步性能"""
        # 创建大量交易记录
        dataset_size = self.create_large_dataset(db_session, 500)  # 500笔交易
        
        # 测量同步时间
        response, execution_time = self.measure_execution_time(
            client.post, '/api/historical-trades/sync'
        )
        
        assert response.status_code == 200
        assert execution_time < self.performance_threshold * 2  # 允许同步操作更长时间
        
        # 验证数据正确性
        historical_trades_count = HistoricalTrade.query.count()
        assert historical_trades_count == dataset_size
        
        print(f"同步{dataset_size}笔交易耗时: {execution_time:.2f}秒")
    
    def test_historical_trades_list_performance(self, client, db_session):
        """测试历史交易列表查询性能"""
        # 创建历史交易记录
        self.create_large_dataset(db_session, 200)
        client.post('/api/historical-trades/sync')
        
        # 测试不同分页大小的性能
        page_sizes = [10, 20, 50, 100]
        
        for page_size in page_sizes:
            response, execution_time = self.measure_execution_time(
                client.get, f'/api/historical-trades?page=1&per_page={page_size}'
            )
            
            assert response.status_code == 200
            assert execution_time < self.performance_threshold
            
            data = json.loads(response.data)
            assert len(data['trades']) <= page_size
            
            print(f"查询{page_size}条记录耗时: {execution_time:.2f}秒")
    
    def test_concurrent_api_requests_performance(self, client, db_session):
        """测试并发API请求性能"""
        # 准备测试数据
        self.create_large_dataset(db_session, 100)
        client.post('/api/historical-trades/sync')
        
        def make_request():
            """发起单个API请求"""
            start_time = time.time()
            response = client.get('/api/historical-trades?page=1&per_page=20')
            end_time = time.time()
            return response.status_code, end_time - start_time
        
        # 并发请求测试
        with ThreadPoolExecutor(max_workers=self.concurrent_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(self.concurrent_requests)]
            
            results = []
            for future in as_completed(futures):
                status_code, execution_time = future.result()
                results.append((status_code, execution_time))
        
        # 验证所有请求都成功
        for status_code, execution_time in results:
            assert status_code == 200
            assert execution_time < self.performance_threshold
        
        avg_time = sum(time for _, time in results) / len(results)
        max_time = max(time for _, time in results)
        
        print(f"并发{self.concurrent_requests}个请求 - 平均耗时: {avg_time:.2f}秒, 最大耗时: {max_time:.2f}秒")
    
    def test_review_creation_performance(self, client, db_session):
        """测试复盘记录创建性能"""
        # 创建历史交易记录
        self.create_large_dataset(db_session, 50)
        client.post('/api/historical-trades/sync')
        
        historical_trades = HistoricalTrade.query.limit(10).all()
        
        review_data = {
            'review_title': '性能测试复盘',
            'review_content': '这是一个性能测试的复盘记录' * 100,  # 较长的内容
            'strategy_score': 4,
            'timing_score': 3,
            'risk_control_score': 5,
            'overall_score': 4
        }
        
        creation_times = []
        
        for trade in historical_trades:
            data = {
                'historical_trade_id': trade.id,
                **review_data
            }
            
            response, execution_time = self.measure_execution_time(
                client.post,
                '/api/trade-reviews',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            assert execution_time < self.performance_threshold
            creation_times.append(execution_time)
        
        avg_creation_time = sum(creation_times) / len(creation_times)
        print(f"复盘记录创建平均耗时: {avg_creation_time:.2f}秒")
    
    def test_database_query_optimization(self, client, db_session):
        """测试数据库查询优化"""
        # 创建大量数据
        self.create_large_dataset(db_session, 300)
        client.post('/api/historical-trades/sync')
        
        # 测试不同查询场景的性能
        test_scenarios = [
            ('基本查询', '/api/historical-trades'),
            ('股票代码筛选', '/api/historical-trades?stock_code=000001'),
            ('收益率范围筛选', '/api/historical-trades?min_return_rate=0.1&max_return_rate=0.3'),
            ('日期范围筛选', '/api/historical-trades?start_date=2024-01-01&end_date=2024-06-30'),
            ('复合筛选', '/api/historical-trades?stock_code=000001&min_return_rate=0.1&start_date=2024-01-01')
        ]
        
        for scenario_name, url in test_scenarios:
            response, execution_time = self.measure_execution_time(client.get, url)
            
            assert response.status_code == 200
            assert execution_time < self.performance_threshold
            
            print(f"{scenario_name}查询耗时: {execution_time:.2f}秒")
    
    def test_memory_usage_under_load(self, client, db_session):
        """测试负载下的内存使用情况"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量数据并进行多次查询
        self.create_large_dataset(db_session, 500)
        client.post('/api/historical-trades/sync')
        
        # 执行多次查询操作
        for i in range(50):
            client.get(f'/api/historical-trades?page={i % 10 + 1}&per_page=20')
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该在合理范围内（小于100MB）
        assert memory_increase < 100
        
        print(f"内存使用 - 初始: {initial_memory:.2f}MB, 最终: {final_memory:.2f}MB, 增长: {memory_increase:.2f}MB")
    
    def test_response_time_consistency(self, client, db_session):
        """测试响应时间一致性"""
        # 准备数据
        self.create_large_dataset(db_session, 100)
        client.post('/api/historical-trades/sync')
        
        # 多次执行相同请求，测试响应时间的一致性
        response_times = []
        
        for _ in range(20):
            _, execution_time = self.measure_execution_time(
                client.get, '/api/historical-trades?page=1&per_page=20'
            )
            response_times.append(execution_time)
        
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # 响应时间变化不应该太大
        time_variance = max_time - min_time
        assert time_variance < 1.0  # 变化小于1秒
        assert avg_time < self.performance_threshold
        
        print(f"响应时间一致性 - 平均: {avg_time:.2f}秒, 最大: {max_time:.2f}秒, 最小: {min_time:.2f}秒, 变化: {time_variance:.2f}秒")
    
    def test_bulk_operations_performance(self, client, db_session):
        """测试批量操作性能"""
        # 测试批量创建复盘记录
        self.create_large_dataset(db_session, 100)
        client.post('/api/historical-trades/sync')
        
        historical_trades = HistoricalTrade.query.limit(50).all()
        
        # 批量创建复盘记录
        start_time = time.time()
        
        for trade in historical_trades:
            review_data = {
                'historical_trade_id': trade.id,
                'review_title': f'批量复盘 - {trade.stock_code}',
                'review_content': '批量创建的复盘记录',
                'overall_score': 4
            }
            
            response = client.post(
                '/api/trade-reviews',
                data=json.dumps(review_data),
                content_type='application/json'
            )
            assert response.status_code == 201
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_record = total_time / len(historical_trades)
        
        assert avg_time_per_record < 0.5  # 每条记录创建时间小于0.5秒
        
        print(f"批量创建{len(historical_trades)}条复盘记录耗时: {total_time:.2f}秒, 平均每条: {avg_time_per_record:.2f}秒")