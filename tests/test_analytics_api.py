"""
统计分析API测试
"""
import pytest
import json
from datetime import datetime, date
from decimal import Decimal
from models.trade_record import TradeRecord
from models.stock_price import StockPrice


class TestAnalyticsAPI:
    """统计分析API测试类"""
    
    def test_get_analytics_overview_empty(self, client, app, db_session):
        """测试获取空数据的总体统计概览"""
        response = client.get('/api/analytics/overview')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == '获取总体统计成功'
        
        overview = data['data']
        assert overview['total_investment'] == 0
        assert overview['closed_profit'] == 0
        assert overview['floating_profit'] == 0
        assert overview['total_profit'] == 0
        assert overview['total_return_rate'] == 0
        assert overview['current_holdings_count'] == 0
        assert overview['total_buy_count'] == 0
        assert overview['total_sell_count'] == 0
        assert overview['success_rate'] == 0
        assert 'last_updated' in overview
    
    def test_get_analytics_overview_with_data(self, client, app, db_session):
        """测试获取有数据的总体统计概览"""
        with app.app_context():
            # 创建测试交易记录
            buy_trade = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='测试买入'
            )
            buy_trade.save()
            
            sell_trade = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='sell',
                price=Decimal('12.00'),
                quantity=500,
                trade_date=datetime(2024, 1, 15),
                reason='部分止盈'
            )
            sell_trade.save()
            
            # 创建价格数据
            price = StockPrice(
                stock_code='000001',
                stock_name='平安银行',
                current_price=Decimal('11.00'),
                change_percent=Decimal('1.5'),
                record_date=date.today()
            )
            price.save()
        
        response = client.get('/api/analytics/overview')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        overview = data['data']
        assert overview['total_investment'] == 10000  # 1000 * 10
        assert overview['current_holdings_count'] == 1  # 还有500股持仓
        assert overview['total_buy_count'] == 1
        assert overview['total_sell_count'] == 1
    
    def test_get_profit_distribution_empty(self, client, app, db_session):
        """测试获取空数据的收益分布"""
        response = client.get('/api/analytics/profit-distribution')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == '获取收益分布成功'
        
        distribution = data['data']
        assert distribution['total_stocks'] == 0
        assert distribution['holding_stocks'] == 0
        assert distribution['closed_stocks'] == 0
        assert len(distribution['profit_ranges']) == 9  # 9个收益区间
    
    def test_get_profit_distribution_with_data(self, client, app, db_session):
        """测试获取有数据的收益分布"""
        with app.app_context():
            # 创建盈利的已清仓股票
            buy_trade = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='买入'
            )
            buy_trade.save()
            
            sell_trade = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='sell',
                price=Decimal('12.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 15),
                reason='卖出'
            )
            sell_trade.save()
        
        response = client.get('/api/analytics/profit-distribution')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        distribution = data['data']
        assert distribution['total_stocks'] == 1
        assert distribution['closed_stocks'] == 1
        assert distribution['holding_stocks'] == 0
        
        # 检查收益区间分布
        profit_ranges = {r['range']: r for r in distribution['profit_ranges']}
        assert profit_ranges['20% ~ 50%']['count'] == 1  # 25%收益率的股票 (25-20)/20 = 0.25
    
    def test_get_monthly_statistics_default_year(self, client, app, db_session):
        """测试获取默认年份的月度统计"""
        response = client.get('/api/analytics/monthly')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        monthly_stats = data['data']
        current_year = datetime.now().year
        assert monthly_stats['year_summary']['year'] == current_year
        assert len(monthly_stats['monthly_data']) == 12  # 12个月
    
    def test_get_monthly_statistics_specific_year(self, client, app, db_session):
        """测试获取指定年份的月度统计"""
        with app.app_context():
            # 创建2023年的交易记录
            trade = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2023, 6, 15),
                reason='买入'
            )
            trade.save()
        
        response = client.get('/api/analytics/monthly?year=2023')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert '2023年月度统计成功' in data['message']
        
        monthly_stats = data['data']
        assert monthly_stats['year_summary']['year'] == 2023
        assert monthly_stats['year_summary']['total_buy_count'] == 1
        
        # 检查6月份数据
        june_data = next(m for m in monthly_stats['monthly_data'] if m['month'] == 6)
        assert june_data['buy_count'] == 1
        assert june_data['unique_stocks'] == 1
    
    def test_get_monthly_statistics_invalid_year(self, client, app, db_session):
        """测试无效年份的月度统计"""
        # 测试过早的年份
        response = client.get('/api/analytics/monthly?year=1999')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # 测试过晚的年份
        future_year = datetime.now().year + 10
        response = client.get(f'/api/analytics/monthly?year={future_year}')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_export_statistics_excel(self, client, app, db_session):
        """测试导出Excel统计数据"""
        with app.app_context():
            # 创建一些测试数据
            trade = TradeRecord(
                stock_code='000001',
                stock_name='测试股票',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='测试买入'
            )
            trade.save()
        
        response = client.get('/api/analytics/export?format=excel')
        
        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        # 检查响应头
        content_disposition = response.headers.get('Content-Disposition', '')
        assert 'attachment' in content_disposition
        # 检查文件名（可能被URL编码）
        assert '.xlsx' in content_disposition
        
        # 检查文件内容不为空
        assert len(response.data) > 0
        
        # 验证Excel文件格式（Excel文件以PK开头）
        assert response.data[:2] == b'PK'
    
    def test_export_statistics_invalid_format(self, client, app, db_session):
        """测试无效格式的导出请求"""
        response = client.get('/api/analytics/export?format=pdf')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert '只支持Excel格式导出' in data['error']['message']
    
    def test_get_current_holdings_empty(self, client, app, db_session):
        """测试获取空的当前持仓"""
        response = client.get('/api/analytics/holdings')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == '获取当前持仓成功'
        
        holdings_data = data['data']
        assert holdings_data['total_count'] == 0
        assert holdings_data['total_market_value'] == 0
        assert holdings_data['total_cost'] == 0
        assert holdings_data['total_profit'] == 0
        assert len(holdings_data['holdings']) == 0
    
    def test_get_current_holdings_with_data(self, client, app, db_session):
        """测试获取有数据的当前持仓"""
        with app.app_context():
            # 创建持仓交易记录
            buy_trade = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='买入'
            )
            buy_trade.save()
            
            # 创建价格数据
            price = StockPrice(
                stock_code='000001',
                stock_name='平安银行',
                current_price=Decimal('12.00'),
                change_percent=Decimal('20.0'),
                record_date=date.today()
            )
            price.save()
        
        response = client.get('/api/analytics/holdings')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        holdings_data = data['data']
        assert holdings_data['total_count'] == 1
        assert holdings_data['total_market_value'] == 12000  # 1000 * 12
        assert holdings_data['total_cost'] == 10000  # 1000 * 10
        assert holdings_data['total_profit'] == 2000  # 12000 - 10000
        
        # 检查持仓详情
        holding = holdings_data['holdings'][0]
        assert holding['stock_code'] == '000001'
        assert holding['stock_name'] == '平安银行'
        assert holding['quantity'] == 1000
        assert holding['avg_cost'] == 10.0
        assert holding['current_price'] == 12.0
        assert holding['profit_rate'] == 0.2  # 20%
    
    def test_get_performance_metrics_empty(self, client, app, db_session):
        """测试获取空数据的投资表现指标"""
        response = client.get('/api/analytics/performance')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == '暂无交易数据'
        
        performance = data['data']
        assert performance['total_trades'] == 0
        assert performance['trading_days'] == 0
        assert performance['avg_trades_per_day'] == 0
        assert performance['most_traded_stock'] is None
        assert performance['best_performing_stock'] is None
        assert performance['worst_performing_stock'] is None
    
    def test_get_performance_metrics_with_data(self, client, app, db_session):
        """测试获取有数据的投资表现指标"""
        with app.app_context():
            # 创建多只股票的交易记录
            # 股票A：盈利
            buy_a = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='买入'
            )
            buy_a.save()
            
            sell_a = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='sell',
                price=Decimal('15.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 15),
                reason='卖出'
            )
            sell_a.save()
            
            # 股票B：亏损
            buy_b = TradeRecord(
                stock_code='000002',
                stock_name='股票B',
                trade_type='buy',
                price=Decimal('20.00'),
                quantity=500,
                trade_date=datetime(2024, 1, 10),
                reason='买入'
            )
            buy_b.save()
            
            sell_b = TradeRecord(
                stock_code='000002',
                stock_name='股票B',
                trade_type='sell',
                price=Decimal('16.00'),
                quantity=500,
                trade_date=datetime(2024, 1, 20),
                reason='卖出'
            )
            sell_b.save()
            
            # 股票A再次交易（使其成为最常交易的股票）
            buy_a2 = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='buy',
                price=Decimal('12.00'),
                quantity=500,
                trade_date=datetime(2024, 2, 1),
                reason='再次买入'
            )
            buy_a2.save()
            
            # 股票A最后卖出（完全清仓）
            sell_a2 = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='sell',
                price=Decimal('18.00'),
                quantity=500,
                trade_date=datetime(2024, 2, 5),
                reason='卖出'
            )
            sell_a2.save()
        
        response = client.get('/api/analytics/performance')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        performance = data['data']
        assert performance['total_trades'] == 6  # 现在有6笔交易
        assert performance['trading_days'] > 0
        assert performance['avg_trades_per_day'] > 0
        assert performance['closed_positions_count'] == 2  # 现在两只股票都完全清仓
        
        # 检查最常交易的股票
        most_traded = performance['most_traded_stock']
        assert most_traded['stock_code'] == '000001'  # 股票A交易了4次
        assert most_traded['trade_count'] == 4
        
        # 检查最佳表现股票
        best_performing = performance['best_performing_stock']
        assert best_performing['stock_code'] == '000001'
        # 股票A总体收益率应该是正的
        assert best_performing['profit_rate'] > 0
        
        # 检查最差表现股票
        worst_performing = performance['worst_performing_stock']
        assert worst_performing['stock_code'] == '000002'
        assert worst_performing['profit_rate'] == -20.0  # -20%收益率
    
    def test_api_error_handling(self, client, app, db_session, monkeypatch):
        """测试API错误处理"""
        # 模拟数据库错误
        def mock_get_overall_statistics():
            raise Exception("Database connection failed")
        
        monkeypatch.setattr(
            'services.analytics_service.AnalyticsService.get_overall_statistics',
            mock_get_overall_statistics
        )
        
        response = client.get('/api/analytics/overview')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'INTERNAL_ERROR'
        assert 'Database connection failed' in data['error']['message']
    
    def test_holdings_sorting(self, client, app, db_session):
        """测试持仓按收益率排序"""
        with app.app_context():
            # 创建多只股票的持仓
            # 股票A：收益率20%
            buy_a = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='买入'
            )
            buy_a.save()
            
            price_a = StockPrice(
                stock_code='000001',
                stock_name='股票A',
                current_price=Decimal('12.00'),
                change_percent=Decimal('20.0'),
                record_date=date.today()
            )
            price_a.save()
            
            # 股票B：收益率-10%
            buy_b = TradeRecord(
                stock_code='000002',
                stock_name='股票B',
                trade_type='buy',
                price=Decimal('20.00'),
                quantity=500,
                trade_date=datetime(2024, 1, 10),
                reason='买入'
            )
            buy_b.save()
            
            price_b = StockPrice(
                stock_code='000002',
                stock_name='股票B',
                current_price=Decimal('18.00'),
                change_percent=Decimal('-10.0'),
                record_date=date.today()
            )
            price_b.save()
        
        response = client.get('/api/analytics/holdings')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        holdings = data['data']['holdings']
        assert len(holdings) == 2
        
        # 验证按收益率降序排列
        assert holdings[0]['stock_code'] == '000001'  # 收益率20%
        assert holdings[0]['profit_rate'] == 0.2
        assert holdings[1]['stock_code'] == '000002'  # 收益率-10%
        assert holdings[1]['profit_rate'] == -0.1