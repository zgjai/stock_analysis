"""
性能测试和并发处理测试
测试系统在高负载和并发访问下的性能表现
"""
import pytest
import time
import threading
import concurrent.futures
from datetime import datetime, date, timedelta
from extensions import db
from models.trade_record import TradeRecord
from models.review_record import ReviewRecord
from models.stock_pool import StockPool
from models.stock_price import StockPrice
from models.sector_data import SectorData
import json
import random


class TestPerformanceConcurrency:
    """性能和并发测试"""
    
    def test_large_dataset_query_performance(self, client, db_session):
        """测试大数据集查询性能"""
        
        # 1. 创建大量测试数据
        print("创建大量测试数据...")
        start_time = time.time()
        
        # 创建1000条交易记录
        trades = []
        stock_codes = [f'00000{i%10}' for i in range(10)]  # 10只股票
        
        for i in range(1000):
            trade = TradeRecord(
                stock_code=random.choice(stock_codes),
                stock_name=f'测试股票{i%10}',
                trade_type='buy' if i % 2 == 0 else 'sell',
                price=10.00 + random.uniform(-2, 2),
                quantity=random.randint(100, 2000),
                trade_date=datetime.now() - timedelta(days=random.randint(0, 365)),
                reason=f'测试原因{i%5}'
            )
            trades.append(trade)
        
        db_session.add_all(trades)
        db_session.commit()
        
        creation_time = time.time() - start_time
        print(f"创建1000条记录耗时: {creation_time:.2f}秒")
        assert creation_time < 10.0  # 创建时间应小于10秒
        
        # 2. 测试全表查询性能
        start_time = time.time()
        all_trades = db_session.query(TradeRecord).all()
        query_time = time.time() - start_time
        
        print(f"查询所有记录耗时: {query_time:.2f}秒")
        assert len(all_trades) == 1000
        assert query_time < 1.0  # 查询时间应小于1秒
        
        # 3. 测试条件查询性能
        start_time = time.time()
        filtered_trades = db_session.query(TradeRecord).filter(
            TradeRecord.stock_code == '000001',
            TradeRecord.trade_type == 'buy'
        ).all()
        filter_time = time.time() - start_time
        
        print(f"条件查询耗时: {filter_time:.2f}秒")
        assert filter_time < 0.5  # 条件查询时间应小于0.5秒
        
        # 4. 测试分页查询性能
        start_time = time.time()
        paginated_trades = db_session.query(TradeRecord).offset(100).limit(50).all()
        pagination_time = time.time() - start_time
        
        print(f"分页查询耗时: {pagination_time:.2f}秒")
        assert len(paginated_trades) == 50
        assert pagination_time < 0.2  # 分页查询时间应小于0.2秒
        
        # 5. 测试聚合查询性能
        start_time = time.time()
        total_quantity = db_session.query(
            db.func.sum(TradeRecord.quantity)
        ).filter(TradeRecord.trade_type == 'buy').scalar()
        aggregation_time = time.time() - start_time
        
        print(f"聚合查询耗时: {aggregation_time:.2f}秒")
        assert total_quantity > 0
        assert aggregation_time < 0.3  # 聚合查询时间应小于0.3秒
        
    def test_concurrent_api_requests(self, client, db_session):
        """测试并发API请求"""
        
        # 1. 准备测试数据
        base_trade_data = {
            'stock_name': '测试股票',
            'trade_type': 'buy',
            'price': 10.00,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '并发测试'
        }
        
        # 2. 并发创建交易记录
        def create_trade(thread_id):
            trade_data = base_trade_data.copy()
            trade_data['stock_code'] = f'T{thread_id:04d}'
            trade_data['notes'] = f'线程{thread_id}创建'
            
            response = client.post('/api/trades', json=trade_data)
            return response.status_code, response.json if response.status_code == 201 else None
        
        # 使用10个线程并发创建交易记录
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_trade, i) for i in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        concurrent_time = time.time() - start_time
        print(f"并发创建50条记录耗时: {concurrent_time:.2f}秒")
        
        # 验证结果
        successful_creates = [r for r in results if r[0] == 201]
        assert len(successful_creates) == 50  # 所有请求都应该成功
        assert concurrent_time < 5.0  # 并发创建时间应小于5秒
        
        # 3. 并发查询测试
        def query_trades(thread_id):
            response = client.get('/api/trades')
            return response.status_code, len(response.json['data']) if response.status_code == 200 else 0
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(query_trades, i) for i in range(100)]
            query_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        query_time = time.time() - start_time
        print(f"并发查询100次耗时: {query_time:.2f}秒")
        
        # 验证结果
        successful_queries = [r for r in query_results if r[0] == 200]
        assert len(successful_queries) == 100  # 所有查询都应该成功
        assert query_time < 3.0  # 并发查询时间应小于3秒
        
    def test_concurrent_data_modifications(self, client, db_session):
        """测试并发数据修改"""
        
        # 1. 创建初始交易记录
        initial_trade = TradeRecord(
            stock_code='CONC01',
            stock_name='并发测试股票',
            trade_type='buy',
            price=10.00,
            quantity=1000,
            trade_date=datetime.now(),
            reason='初始记录'
        )
        db_session.add(initial_trade)
        db_session.commit()
        trade_id = initial_trade.id
        
        # 2. 并发更新同一记录
        def update_trade(thread_id, new_price):
            update_data = {
                'price': new_price,
                'notes': f'线程{thread_id}更新'
            }
            response = client.put(f'/api/trades/{trade_id}', json=update_data)
            return response.status_code, response.json if response.status_code == 200 else None
        
        # 使用5个线程并发更新同一记录
        prices = [10.10, 10.20, 10.30, 10.40, 10.50]
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(update_trade, i, prices[i]) for i in range(5)]
            update_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        update_time = time.time() - start_time
        print(f"并发更新耗时: {update_time:.2f}秒")
        
        # 验证结果 - 至少有一个更新成功
        successful_updates = [r for r in update_results if r[0] == 200]
        assert len(successful_updates) >= 1
        
        # 验证最终状态
        response = client.get(f'/api/trades/{trade_id}')
        assert response.status_code == 200
        final_trade = response.json['data']
        assert final_trade['price'] in prices  # 价格应该是其中一个更新值
        
    def test_concurrent_stock_pool_operations(self, client, db_session):
        """测试股票池并发操作"""
        
        # 1. 并发添加股票到池中
        def add_to_pool(thread_id):
            pool_data = {
                'stock_code': f'P{thread_id:04d}',
                'stock_name': f'池测试股票{thread_id}',
                'pool_type': 'watch' if thread_id % 2 == 0 else 'buy_ready',
                'target_price': 10.00 + thread_id * 0.1,
                'add_reason': f'线程{thread_id}添加',
                'status': 'active'
            }
            response = client.post('/api/stock-pool', json=pool_data)
            return response.status_code, response.json if response.status_code == 201 else None
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(add_to_pool, i) for i in range(30)]
            pool_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        pool_time = time.time() - start_time
        print(f"并发添加股票池记录耗时: {pool_time:.2f}秒")
        
        # 验证结果
        successful_adds = [r for r in pool_results if r[0] == 201]
        assert len(successful_adds) == 30
        assert pool_time < 3.0
        
        # 2. 并发查询股票池
        def query_pool(query_type):
            if query_type == 'all':
                response = client.get('/api/stock-pool')
            elif query_type == 'watch':
                response = client.get('/api/stock-pool?pool_type=watch')
            else:
                response = client.get('/api/stock-pool?pool_type=buy_ready')
            
            return response.status_code, len(response.json['data']) if response.status_code == 200 else 0
        
        query_types = ['all', 'watch', 'buy_ready'] * 10
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(query_pool, qt) for qt in query_types]
            query_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        query_time = time.time() - start_time
        print(f"并发查询股票池耗时: {query_time:.2f}秒")
        
        # 验证结果
        successful_queries = [r for r in query_results if r[0] == 200]
        assert len(successful_queries) == 30
        assert query_time < 2.0
        
    def test_price_service_performance(self, client, db_session):
        """测试价格服务性能"""
        
        # 1. 批量添加价格数据
        stock_codes = [f'P{i:04d}' for i in range(100)]
        price_data_list = []
        
        for i, stock_code in enumerate(stock_codes):
            price_data = {
                'stock_code': stock_code,
                'stock_name': f'价格测试股票{i}',
                'current_price': 10.00 + random.uniform(-2, 2),
                'change_percent': random.uniform(-10, 10),
                'record_date': date.today().isoformat()
            }
            price_data_list.append(price_data)
        
        # 2. 测试批量插入性能
        start_time = time.time()
        for price_data in price_data_list:
            response = client.post('/api/prices', json=price_data)
            assert response.status_code == 201
        
        batch_insert_time = time.time() - start_time
        print(f"批量插入100条价格记录耗时: {batch_insert_time:.2f}秒")
        assert batch_insert_time < 5.0
        
        # 3. 测试批量查询性能
        start_time = time.time()
        stock_codes_str = ','.join(stock_codes[:50])  # 查询前50只股票
        response = client.get(f'/api/prices?stock_codes={stock_codes_str}')
        batch_query_time = time.time() - start_time
        
        print(f"批量查询50只股票价格耗时: {batch_query_time:.2f}秒")
        assert response.status_code == 200
        assert len(response.json['data']) == 50
        assert batch_query_time < 1.0
        
        # 4. 测试并发价格更新
        def update_price(stock_code):
            price_data = {
                'stock_code': stock_code,
                'stock_name': f'更新测试{stock_code}',
                'current_price': 10.00 + random.uniform(-1, 1),
                'change_percent': random.uniform(-5, 5),
                'record_date': date.today().isoformat()
            }
            response = client.post('/api/prices', json=price_data)
            return response.status_code
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(update_price, code) for code in stock_codes[:20]]
            update_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        concurrent_update_time = time.time() - start_time
        print(f"并发更新20只股票价格耗时: {concurrent_update_time:.2f}秒")
        
        successful_updates = [r for r in update_results if r == 201]
        assert len(successful_updates) == 20
        assert concurrent_update_time < 3.0
        
    def test_sector_data_performance(self, client, db_session):
        """测试板块数据性能"""
        
        # 1. 创建大量板块历史数据
        sectors = ['银行', '地产', '科技', '医药', '消费', '军工', '新能源', '汽车', '钢铁', '煤炭']
        dates = [date.today() - timedelta(days=i) for i in range(30)]
        
        sector_data_list = []
        for test_date in dates:
            for i, sector in enumerate(sectors):
                sector_data = {
                    'sector_name': sector,
                    'sector_code': f'BK{1000+i}',
                    'change_percent': random.uniform(-5, 5),
                    'record_date': test_date.isoformat(),
                    'rank_position': i + 1,
                    'volume': random.randint(1000000000, 5000000000),
                    'market_cap': random.uniform(500000000000, 2000000000000)
                }
                sector_data_list.append(sector_data)
        
        # 2. 测试批量插入性能
        start_time = time.time()
        for sector_data in sector_data_list:
            response = client.post('/api/sectors', json=sector_data)
            # 可能有重复数据，忽略409错误
            assert response.status_code in [201, 409]
        
        insert_time = time.time() - start_time
        print(f"插入{len(sector_data_list)}条板块记录耗时: {insert_time:.2f}秒")
        assert insert_time < 15.0
        
        # 3. 测试复杂查询性能
        start_time = time.time()
        start_date = (date.today() - timedelta(days=7)).isoformat()
        end_date = date.today().isoformat()
        response = client.get(f'/api/sectors/history?start_date={start_date}&end_date={end_date}')
        history_query_time = time.time() - start_time
        
        print(f"查询7天板块历史耗时: {history_query_time:.2f}秒")
        assert response.status_code == 200
        assert len(response.json['data']) > 0
        assert history_query_time < 1.0
        
        # 4. 测试TOPK统计性能
        start_time = time.time()
        response = client.get('/api/sectors/top-performers?days=30&top_k=5')
        topk_time = time.time() - start_time
        
        print(f"TOPK统计查询耗时: {topk_time:.2f}秒")
        assert response.status_code == 200
        assert len(response.json['data']) > 0
        assert topk_time < 2.0
        
    def test_analytics_performance(self, client, db_session):
        """测试统计分析性能"""
        
        # 1. 创建大量交易数据用于统计
        self._create_large_trading_dataset(client, 500)
        
        # 2. 测试总体统计性能
        start_time = time.time()
        response = client.get('/api/analytics/overview')
        overview_time = time.time() - start_time
        
        print(f"总体统计查询耗时: {overview_time:.2f}秒")
        assert response.status_code == 200
        assert overview_time < 2.0
        
        # 3. 测试收益分布计算性能
        start_time = time.time()
        response = client.get('/api/analytics/profit-distribution')
        distribution_time = time.time() - start_time
        
        print(f"收益分布计算耗时: {distribution_time:.2f}秒")
        assert response.status_code == 200
        assert distribution_time < 1.5
        
        # 4. 测试月度统计性能
        start_time = time.time()
        response = client.get('/api/analytics/monthly')
        monthly_time = time.time() - start_time
        
        print(f"月度统计查询耗时: {monthly_time:.2f}秒")
        assert response.status_code == 200
        assert monthly_time < 1.0
        
        # 5. 测试导出功能性能
        start_time = time.time()
        response = client.get('/api/analytics/export')
        export_time = time.time() - start_time
        
        print(f"数据导出耗时: {export_time:.2f}秒")
        assert response.status_code == 200
        assert export_time < 3.0
        
    def test_database_connection_pool_performance(self, client, db_session):
        """测试数据库连接池性能"""
        
        # 1. 并发数据库操作测试
        def db_operation(operation_id):
            try:
                # 执行一系列数据库操作
                trade = TradeRecord(
                    stock_code=f'DB{operation_id:04d}',
                    stock_name=f'连接池测试{operation_id}',
                    trade_type='buy',
                    price=10.00 + operation_id * 0.01,
                    quantity=1000,
                    trade_date=datetime.now(),
                    reason='连接池测试'
                )
                db_session.add(trade)
                db_session.commit()
                
                # 查询操作
                result = db_session.query(TradeRecord).filter_by(stock_code=f'DB{operation_id:04d}').first()
                
                return True, result.id if result else None
            except Exception as e:
                db_session.rollback()
                return False, str(e)
        
        # 2. 高并发测试
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(db_operation, i) for i in range(100)]
            db_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        db_time = time.time() - start_time
        print(f"100个并发数据库操作耗时: {db_time:.2f}秒")
        
        # 验证结果
        successful_ops = [r for r in db_results if r[0] == True]
        failed_ops = [r for r in db_results if r[0] == False]
        
        print(f"成功操作: {len(successful_ops)}, 失败操作: {len(failed_ops)}")
        
        # 大部分操作应该成功
        assert len(successful_ops) >= 90  # 至少90%成功率
        assert db_time < 10.0  # 总时间应小于10秒
        
    def test_memory_usage_performance(self, client, db_session):
        """测试内存使用性能"""
        
        # 1. 大量数据查询的内存测试
        # 创建大量数据
        trades = []
        for i in range(2000):
            trade = TradeRecord(
                stock_code=f'MEM{i%20:02d}',
                stock_name=f'内存测试股票{i%20}',
                trade_type='buy' if i % 2 == 0 else 'sell',
                price=10.00 + random.uniform(-2, 2),
                quantity=random.randint(100, 2000),
                trade_date=datetime.now() - timedelta(days=random.randint(0, 100)),
                reason=f'内存测试{i%10}'
            )
            trades.append(trade)
        
        db_session.add_all(trades)
        db_session.commit()
        
        # 2. 测试大量数据查询
        start_time = time.time()
        all_trades = db_session.query(TradeRecord).filter(
            TradeRecord.stock_code.like('MEM%')
        ).all()
        query_time = time.time() - start_time
        
        print(f"查询2000条记录耗时: {query_time:.2f}秒")
        assert len(all_trades) == 2000
        assert query_time < 2.0
        
        # 3. 测试分批处理性能
        batch_size = 100
        batches_processed = 0
        start_time = time.time()
        
        for i in range(0, 2000, batch_size):
            batch_trades = db_session.query(TradeRecord).filter(
                TradeRecord.stock_code.like('MEM%')
            ).offset(i).limit(batch_size).all()
            
            # 模拟处理
            for trade in batch_trades:
                _ = trade.stock_code + trade.stock_name
            
            batches_processed += 1
        
        batch_time = time.time() - start_time
        print(f"分批处理{batches_processed}批数据耗时: {batch_time:.2f}秒")
        assert batches_processed == 20  # 2000/100 = 20批
        assert batch_time < 3.0
        
    def _create_large_trading_dataset(self, client, num_trades):
        """创建大量交易数据用于测试"""
        stock_codes = [f'T{i:03d}' for i in range(50)]  # 50只股票
        
        for i in range(num_trades):
            stock_code = random.choice(stock_codes)
            trade_data = {
                'stock_code': stock_code,
                'stock_name': f'测试股票{stock_code}',
                'trade_type': 'buy' if i % 3 != 0 else 'sell',  # 2/3买入，1/3卖出
                'price': 10.00 + random.uniform(-3, 3),
                'quantity': random.randint(100, 2000),
                'trade_date': (datetime.now() - timedelta(days=random.randint(0, 180))).isoformat(),
                'reason': f'测试原因{i%10}'
            }
            
            response = client.post('/api/trades', json=trade_data)
            assert response.status_code == 201
        
        print(f"创建了{num_trades}条交易记录用于测试")
        
    def test_api_response_time_consistency(self, client, db_session):
        """测试API响应时间一致性"""
        
        # 1. 创建基础数据
        self._create_large_trading_dataset(client, 100)
        
        # 2. 多次测试同一API的响应时间
        response_times = []
        
        for i in range(20):
            start_time = time.time()
            response = client.get('/api/trades')
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            response_times.append(response_time)
        
        # 3. 分析响应时间
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"API响应时间 - 平均: {avg_time:.3f}s, 最大: {max_time:.3f}s, 最小: {min_time:.3f}s")
        
        # 验证响应时间一致性
        assert avg_time < 0.5  # 平均响应时间应小于0.5秒
        assert max_time < 1.0  # 最大响应时间应小于1秒
        assert (max_time - min_time) < 0.5  # 响应时间差异应小于0.5秒
        
    def test_stress_testing(self, client, db_session):
        """压力测试"""
        
        # 1. 高频请求测试
        def high_frequency_requests():
            success_count = 0
            error_count = 0
            
            for i in range(50):
                try:
                    response = client.get('/api/trades')
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception:
                    error_count += 1
            
            return success_count, error_count
        
        # 2. 多线程高频请求
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(high_frequency_requests) for _ in range(5)]
            stress_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        stress_time = time.time() - start_time
        print(f"压力测试耗时: {stress_time:.2f}秒")
        
        # 3. 统计结果
        total_success = sum(r[0] for r in stress_results)
        total_errors = sum(r[1] for r in stress_results)
        total_requests = total_success + total_errors
        
        success_rate = total_success / total_requests if total_requests > 0 else 0
        
        print(f"压力测试结果 - 总请求: {total_requests}, 成功: {total_success}, 失败: {total_errors}")
        print(f"成功率: {success_rate:.2%}")
        
        # 验证系统在压力下的表现
        assert success_rate >= 0.95  # 成功率应大于95%
        assert stress_time < 15.0  # 总时间应小于15秒