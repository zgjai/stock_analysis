"""
性能优化集成测试
测试缓存机制、优化查询和前端集成
"""
import pytest
import time
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from flask import Flask
from extensions import db
from models.trade_record import TradeRecord
from models.stock_price import StockPrice
from services.cache_service import CacheService, CacheEntry
from services.optimized_analytics_service import OptimizedAnalyticsService
from api.optimized_analytics_routes import optimized_analytics_bp


class TestPerformanceOptimization:
    """性能优化测试类"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        app.register_blueprint(optimized_analytics_bp)
        
        with app.app_context():
            db.create_all()
            self.create_test_data()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建缓存表
        db.engine.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key VARCHAR(255) NOT NULL UNIQUE,
                cache_value TEXT NOT NULL,
                cache_type VARCHAR(50) NOT NULL,
                expires_at DATETIME NOT NULL,
                created_by VARCHAR(50) DEFAULT 'system',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建测试交易记录
        test_trades = [
            # 股票A - 已清仓（盈利）
            TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=10.00,
                quantity=1000,
                trade_date=datetime.now() - timedelta(days=30),
                reason='技术分析'
            ),
            TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='sell',
                price=12.00,
                quantity=1000,
                trade_date=datetime.now() - timedelta(days=10),
                reason='止盈'
            ),
            # 股票B - 当前持仓
            TradeRecord(
                stock_code='000002',
                stock_name='万科A',
                trade_type='buy',
                price=20.00,
                quantity=500,
                trade_date=datetime.now() - timedelta(days=20),
                reason='价值投资'
            ),
            # 股票C - 科创板股票
            TradeRecord(
                stock_code='688001',
                stock_name='华兴源创',
                trade_type='buy',
                price=50.00,
                quantity=200,
                trade_date=datetime.now() - timedelta(days=15),
                reason='科技成长'
            ),
        ]
        
        for trade in test_trades:
            db.session.add(trade)
        
        # 创建测试价格数据
        test_prices = [
            StockPrice(
                stock_code='000002',
                current_price=22.00,
                price_date=datetime.now()
            ),
            StockPrice(
                stock_code='688001',
                current_price=55.00,
                price_date=datetime.now()
            ),
        ]
        
        for price in test_prices:
            db.session.add(price)
        
        db.session.commit()
    
    def test_cache_service_basic_operations(self, app):
        """测试缓存服务基本操作"""
        with app.app_context():
            # 测试设置缓存
            test_data = {'test': 'data', 'number': 123}
            cache_key = 'test_key'
            
            CacheService.set_cached_result(
                cache_key, test_data, CacheService.ANALYTICS_OVERALL, 30
            )
            
            # 测试获取缓存
            cached_result = CacheService.get_cached_result(cache_key)
            assert cached_result is not None
            assert cached_result['test'] == 'data'
            assert cached_result['number'] == 123
            
            # 测试缓存统计
            stats = CacheService.get_cache_stats()
            assert stats['total_entries'] >= 1
            assert any(ct['type'] == CacheService.ANALYTICS_OVERALL for ct in stats['cache_types'])
    
    def test_cache_expiration(self, app):
        """测试缓存过期机制"""
        with app.app_context():
            # 设置短期缓存（1秒）
            test_data = {'expired': 'data'}
            cache_key = 'expire_test'
            
            # 手动创建过期的缓存条目
            expired_cache = CacheEntry(
                cache_key=cache_key,
                cache_value=json.dumps(test_data),
                cache_type='test',
                expires_at=datetime.now() - timedelta(seconds=1)
            )
            db.session.add(expired_cache)
            db.session.commit()
            
            # 尝试获取过期缓存
            cached_result = CacheService.get_cached_result(cache_key)
            assert cached_result is None
            
            # 测试清理过期缓存
            CacheService.cleanup_expired_cache()
            remaining_cache = CacheEntry.query.filter_by(cache_key=cache_key).first()
            assert remaining_cache is None
    
    def test_optimized_analytics_performance(self, app):
        """测试优化分析服务性能"""
        with app.app_context():
            # 测试总体统计性能
            start_time = time.time()
            overall_stats = OptimizedAnalyticsService.get_overall_statistics()
            overall_time = time.time() - start_time
            
            assert overall_stats is not None
            assert 'realized_profit' in overall_stats
            assert 'current_holdings_profit' in overall_stats
            assert overall_time < 1.0  # 应该在1秒内完成
            
            # 测试缓存效果 - 第二次调用应该更快
            start_time = time.time()
            cached_stats = OptimizedAnalyticsService.get_overall_statistics()
            cached_time = time.time() - start_time
            
            assert cached_stats == overall_stats
            assert cached_time < overall_time  # 缓存版本应该更快
    
    def test_optimized_database_queries(self, app):
        """测试优化的数据库查询"""
        with app.app_context():
            # 测试优化的交易汇总查询
            start_time = time.time()
            trade_summary = OptimizedAnalyticsService._get_optimized_trade_summary()
            query_time = time.time() - start_time
            
            assert trade_summary is not None
            assert 'buy_count' in trade_summary
            assert 'sell_count' in trade_summary
            assert 'realized_profit' in trade_summary
            assert query_time < 0.5  # 应该在0.5秒内完成
            
            # 验证数据正确性
            assert trade_summary['buy_count'] == 3  # 3笔买入
            assert trade_summary['sell_count'] == 1  # 1笔卖出
            assert trade_summary['realized_profit'] == 2000.0  # (12-10)*1000
    
    def test_optimized_holdings_calculation(self, app):
        """测试优化的持仓计算"""
        with app.app_context():
            start_time = time.time()
            holdings = OptimizedAnalyticsService._get_optimized_current_holdings()
            query_time = time.time() - start_time
            
            assert holdings is not None
            assert len(holdings) == 2  # 两只持仓股票
            assert '000002' in holdings
            assert '688001' in holdings
            assert query_time < 0.5
            
            # 验证持仓数据正确性
            wanke_holding = holdings['000002']
            assert wanke_holding['quantity'] == 500
            assert wanke_holding['avg_cost'] == 20.00
            assert wanke_holding['current_price'] == 22.00
            assert wanke_holding['profit_amount'] == 1000.0  # (22-20)*500
    
    def test_cache_invalidation(self, app):
        """测试缓存失效机制"""
        with app.app_context():
            # 先获取数据并缓存
            original_stats = OptimizedAnalyticsService.get_overall_statistics()
            
            # 验证缓存存在
            cache_stats = CacheService.get_cache_stats()
            assert cache_stats['total_entries'] > 0
            
            # 使缓存失效
            CacheService.invalidate_analytics_cache()
            
            # 验证缓存已清除
            cache_stats_after = CacheService.get_cache_stats()
            assert cache_stats_after['total_entries'] == 0
    
    def test_api_endpoints_performance(self, app, client):
        """测试API端点性能"""
        with app.app_context():
            # 测试总体统计API
            start_time = time.time()
            response = client.get('/api/optimized-analytics/overall')
            api_time = time.time() - start_time
            
            assert response.status_code == 200
            assert api_time < 2.0  # API响应应该在2秒内
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'realized_profit' in data['data']
            
            # 测试性能基准API
            response = client.get('/api/optimized-analytics/benchmark')
            assert response.status_code == 200
            
            benchmark_data = json.loads(response.data)
            assert 'benchmark_results' in benchmark_data['data']
            assert 'summary' in benchmark_data['data']
    
    def test_monthly_statistics_optimization(self, app):
        """测试月度统计优化"""
        with app.app_context():
            current_year = datetime.now().year
            
            start_time = time.time()
            monthly_stats = OptimizedAnalyticsService.get_monthly_statistics(current_year)
            query_time = time.time() - start_time
            
            assert monthly_stats is not None
            assert 'year_summary' in monthly_stats
            assert 'monthly_data' in monthly_stats
            assert query_time < 1.0
            
            # 验证月度数据结构
            monthly_data = monthly_stats['monthly_data']
            assert len(monthly_data) == 12  # 12个月
            
            # 验证当前月份有数据
            current_month = datetime.now().month
            current_month_data = next(
                (m for m in monthly_data if m['month'] == current_month), None
            )
            assert current_month_data is not None
            assert current_month_data['has_data'] is True
    
    def test_profit_distribution_optimization(self, app):
        """测试收益分布优化"""
        with app.app_context():
            # 创建默认配置
            from models.profit_distribution_config import ProfitDistributionConfig
            ProfitDistributionConfig.create_default_configs()
            
            start_time = time.time()
            distribution = OptimizedAnalyticsService.get_profit_distribution(use_trade_pairs=True)
            query_time = time.time() - start_time
            
            assert distribution is not None
            assert 'total_trades' in distribution
            assert 'distribution' in distribution
            assert 'summary' in distribution
            assert query_time < 1.0
            
            # 验证分布数据
            assert distribution['total_trades'] >= 0
            assert len(distribution['distribution']) > 0
    
    def test_concurrent_access_performance(self, app):
        """测试并发访问性能"""
        import threading
        import queue
        
        with app.app_context():
            results = queue.Queue()
            
            def worker():
                try:
                    start_time = time.time()
                    stats = OptimizedAnalyticsService.get_overall_statistics()
                    end_time = time.time()
                    results.put({
                        'success': True,
                        'time': end_time - start_time,
                        'data_size': len(str(stats))
                    })
                except Exception as e:
                    results.put({
                        'success': False,
                        'error': str(e)
                    })
            
            # 创建多个并发线程
            threads = []
            for i in range(5):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            # 收集结果
            all_results = []
            while not results.empty():
                all_results.append(results.get())
            
            # 验证结果
            assert len(all_results) == 5
            successful_results = [r for r in all_results if r['success']]
            assert len(successful_results) == 5
            
            # 验证性能
            avg_time = sum(r['time'] for r in successful_results) / len(successful_results)
            assert avg_time < 2.0  # 平均响应时间应该在2秒内
    
    def test_memory_usage_optimization(self, app):
        """测试内存使用优化"""
        import psutil
        import os
        
        with app.app_context():
            # 获取初始内存使用
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # 执行多次查询
            for i in range(10):
                OptimizedAnalyticsService.get_overall_statistics()
                OptimizedAnalyticsService.get_current_holdings_with_performance()
            
            # 获取最终内存使用
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # 内存增长应该控制在合理范围内（小于50MB）
            assert memory_increase < 50 * 1024 * 1024
    
    def test_cache_hit_rate(self, app):
        """测试缓存命中率"""
        with app.app_context():
            # 清除所有缓存
            CacheService.invalidate_analytics_cache()
            
            # 第一次调用（缓存未命中）
            start_time = time.time()
            OptimizedAnalyticsService.get_overall_statistics()
            first_call_time = time.time() - start_time
            
            # 第二次调用（缓存命中）
            start_time = time.time()
            OptimizedAnalyticsService.get_overall_statistics()
            second_call_time = time.time() - start_time
            
            # 缓存命中应该显著提高性能
            performance_improvement = (first_call_time - second_call_time) / first_call_time
            assert performance_improvement > 0.3  # 至少30%的性能提升
    
    def test_error_handling_performance(self, app):
        """测试错误处理性能"""
        with app.app_context():
            # 模拟数据库错误
            with patch('services.optimized_analytics_service.db.session.execute') as mock_execute:
                mock_execute.side_effect = Exception("Database connection failed")
                
                start_time = time.time()
                try:
                    OptimizedAnalyticsService._get_optimized_trade_summary()
                except Exception:
                    pass
                error_handling_time = time.time() - start_time
                
                # 错误处理应该快速完成
                assert error_handling_time < 0.1
    
    def test_data_consistency_after_optimization(self, app):
        """测试优化后数据一致性"""
        with app.app_context():
            # 获取优化版本的数据
            optimized_stats = OptimizedAnalyticsService.get_overall_statistics()
            
            # 获取原始版本的数据进行对比
            from services.analytics_service import AnalyticsService
            original_stats = AnalyticsService.get_overall_statistics()
            
            # 验证关键数据一致性
            assert abs(optimized_stats['realized_profit'] - original_stats['realized_profit']) < 0.01
            assert abs(optimized_stats['current_holdings_profit'] - original_stats['current_holdings_profit']) < 0.01
            assert optimized_stats['current_holdings_count'] == original_stats['current_holdings_count']
    
    def test_api_response_time_sla(self, app, client):
        """测试API响应时间SLA"""
        with app.app_context():
            # 定义SLA要求（毫秒）
            sla_requirements = {
                '/api/optimized-analytics/overall': 2000,
                '/api/optimized-analytics/monthly': 3000,
                '/api/optimized-analytics/profit-distribution': 2000,
                '/api/optimized-analytics/holdings': 1500,
                '/api/optimized-analytics/performance': 1000,
            }
            
            for endpoint, max_time_ms in sla_requirements.items():
                start_time = time.time()
                response = client.get(endpoint)
                response_time_ms = (time.time() - start_time) * 1000
                
                assert response.status_code == 200
                assert response_time_ms < max_time_ms, f"{endpoint} 响应时间 {response_time_ms}ms 超过SLA要求 {max_time_ms}ms"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])