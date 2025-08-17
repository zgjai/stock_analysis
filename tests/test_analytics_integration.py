"""
统计分析集成测试
"""
import pytest
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from models.trade_record import TradeRecord
from models.stock_price import StockPrice
from services.analytics_service import AnalyticsService


class TestAnalyticsIntegration:
    """统计分析集成测试类"""
    
    def test_complete_trading_workflow_statistics(self, client, app, db_session):
        """测试完整交易流程的统计分析"""
        with app.app_context():
            # 模拟完整的交易流程
            # 第一阶段：买入多只股票
            trades_data = [
                # 股票A：最终盈利
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': Decimal('10.00'),
                    'quantity': 1000,
                    'trade_date': datetime(2024, 1, 5),
                    'reason': '技术突破'
                },
                # 股票B：最终亏损
                {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'trade_type': 'buy',
                    'price': Decimal('20.00'),
                    'quantity': 500,
                    'trade_date': datetime(2024, 1, 10),
                    'reason': '价值投资'
                },
                # 股票C：持续持仓
                {
                    'stock_code': '000003',
                    'stock_name': '中国建筑',
                    'trade_type': 'buy',
                    'price': Decimal('5.00'),
                    'quantity': 2000,
                    'trade_date': datetime(2024, 1, 15),
                    'reason': '低估值'
                }
            ]
            
            # 创建买入交易
            for trade_data in trades_data:
                trade = TradeRecord(**trade_data)
                trade.save()
            
            # 第二阶段：部分卖出操作
            sell_trades = [
                # 股票A：部分止盈
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'sell',
                    'price': Decimal('15.00'),
                    'quantity': 600,
                    'trade_date': datetime(2024, 2, 1),
                    'reason': '部分止盈'
                },
                # 股票B：全部止损
                {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'trade_type': 'sell',
                    'price': Decimal('16.00'),
                    'quantity': 500,
                    'trade_date': datetime(2024, 2, 5),
                    'reason': '止损'
                }
            ]
            
            for trade_data in sell_trades:
                trade = TradeRecord(**trade_data)
                trade.save()
            
            # 第三阶段：创建当前价格数据
            current_prices = [
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'current_price': Decimal('12.00'),
                    'change_percent': Decimal('2.5'),
                    'record_date': date.today()
                },
                {
                    'stock_code': '000003',
                    'stock_name': '中国建筑',
                    'current_price': Decimal('6.00'),
                    'change_percent': Decimal('1.8'),
                    'record_date': date.today()
                }
            ]
            
            for price_data in current_prices:
                price = StockPrice(**price_data)
                price.save()
        
        # 测试总体统计
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        overview_data = json.loads(response.data)['data']
        
        # 验证总体统计数据
        expected_investment = 10000 + 10000 + 10000  # 三只股票的买入金额
        assert overview_data['total_investment'] == expected_investment
        assert overview_data['current_holdings_count'] == 2  # 股票A和C还有持仓
        assert overview_data['total_buy_count'] == 3
        assert overview_data['total_sell_count'] == 2
        
        # 测试收益分布
        response = client.get('/api/analytics/profit-distribution')
        assert response.status_code == 200
        distribution_data = json.loads(response.data)['data']
        
        assert distribution_data['total_stocks'] == 3  # 总共3只股票
        assert distribution_data['holding_stocks'] == 2  # 2只持仓
        assert distribution_data['closed_stocks'] == 1  # 1只已清仓
        
        # 测试月度统计
        response = client.get('/api/analytics/monthly?year=2024')
        assert response.status_code == 200
        monthly_data = json.loads(response.data)['data']
        
        # 验证1月份数据
        jan_data = next(m for m in monthly_data['monthly_data'] if m['month'] == 1)
        assert jan_data['buy_count'] == 3
        assert jan_data['sell_count'] == 0
        assert jan_data['unique_stocks'] == 3
        
        # 验证2月份数据
        feb_data = next(m for m in monthly_data['monthly_data'] if m['month'] == 2)
        assert feb_data['buy_count'] == 0
        assert feb_data['sell_count'] == 2
        assert feb_data['unique_stocks'] == 2
        
        # 测试当前持仓
        response = client.get('/api/analytics/holdings')
        assert response.status_code == 200
        holdings_data = json.loads(response.data)['data']
        
        assert holdings_data['total_count'] == 2
        holdings = holdings_data['holdings']
        
        # 验证持仓详情
        stock_a_holding = next(h for h in holdings if h['stock_code'] == '000001')
        assert stock_a_holding['quantity'] == 400  # 1000 - 600
        assert stock_a_holding['current_price'] == 12.0
        
        stock_c_holding = next(h for h in holdings if h['stock_code'] == '000003')
        assert stock_c_holding['quantity'] == 2000
        assert stock_c_holding['current_price'] == 6.0
        assert stock_c_holding['profit_rate'] == 0.2  # 20%收益率
    
    def test_excel_export_with_comprehensive_data(self, client, app, db_session):
        """测试包含完整数据的Excel导出"""
        with app.app_context():
            # 创建多样化的交易数据
            # 不同月份、不同收益率的交易
            trades = [
                # 1月：盈利交易
                TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='buy',
                    price=Decimal('10.00'),
                    quantity=1000,
                    trade_date=datetime(2024, 1, 5),
                    reason='买入'
                ),
                TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='sell',
                    price=Decimal('12.00'),
                    quantity=1000,
                    trade_date=datetime(2024, 1, 25),
                    reason='卖出'
                ),
                # 2月：亏损交易
                TradeRecord(
                    stock_code='000002',
                    stock_name='股票B',
                    trade_type='buy',
                    price=Decimal('20.00'),
                    quantity=500,
                    trade_date=datetime(2024, 2, 10),
                    reason='买入'
                ),
                TradeRecord(
                    stock_code='000002',
                    stock_name='股票B',
                    trade_type='sell',
                    price=Decimal('18.00'),
                    quantity=500,
                    trade_date=datetime(2024, 2, 20),
                    reason='止损'
                ),
                # 3月：持仓中
                TradeRecord(
                    stock_code='000003',
                    stock_name='股票C',
                    trade_type='buy',
                    price=Decimal('15.00'),
                    quantity=800,
                    trade_date=datetime(2024, 3, 15),
                    reason='买入'
                )
            ]
            
            for trade in trades:
                trade.save()
            
            # 创建持仓股票的价格数据
            price = StockPrice(
                stock_code='000003',
                stock_name='股票C',
                current_price=Decimal('18.00'),
                change_percent=Decimal('20.0'),
                record_date=date.today()
            )
            price.save()
        
        # 测试Excel导出
        response = client.get('/api/analytics/export?format=excel')
        
        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        # 验证文件名包含时间戳
        content_disposition = response.headers.get('Content-Disposition', '')
        assert 'attachment' in content_disposition
        assert '股票交易统计报表_' in content_disposition
        assert '.xlsx' in content_disposition
        
        # 验证文件内容
        assert len(response.data) > 1000  # Excel文件应该有一定大小
        assert response.data[:2] == b'PK'  # Excel文件格式验证
    
    def test_performance_metrics_comprehensive(self, client, app, db_session):
        """测试综合投资表现指标"""
        with app.app_context():
            # 创建多天、多股票的交易记录
            base_date = datetime(2024, 1, 1)
            
            # 股票A：交易频繁，表现最佳
            for i in range(3):
                buy_trade = TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='buy',
                    price=Decimal('10.00'),
                    quantity=500,
                    trade_date=base_date + timedelta(days=i*10),
                    reason='买入'
                )
                buy_trade.save()
                
                sell_trade = TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='sell',
                    price=Decimal('15.00'),
                    quantity=500,
                    trade_date=base_date + timedelta(days=i*10+5),
                    reason='卖出'
                )
                sell_trade.save()
            
            # 股票B：表现最差
            buy_b = TradeRecord(
                stock_code='000002',
                stock_name='股票B',
                trade_type='buy',
                price=Decimal('20.00'),
                quantity=1000,
                trade_date=base_date + timedelta(days=15),
                reason='买入'
            )
            buy_b.save()
            
            sell_b = TradeRecord(
                stock_code='000002',
                stock_name='股票B',
                trade_type='sell',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=base_date + timedelta(days=25),
                reason='止损'
            )
            sell_b.save()
            
            # 股票C：少量交易
            buy_c = TradeRecord(
                stock_code='000003',
                stock_name='股票C',
                trade_type='buy',
                price=Decimal('5.00'),
                quantity=2000,
                trade_date=base_date + timedelta(days=30),
                reason='买入'
            )
            buy_c.save()
            
            sell_c = TradeRecord(
                stock_code='000003',
                stock_name='股票C',
                trade_type='sell',
                price=Decimal('6.00'),
                quantity=2000,
                trade_date=base_date + timedelta(days=35),
                reason='卖出'
            )
            sell_c.save()
        
        response = client.get('/api/analytics/performance')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        performance = data['data']
        
        # 验证基本指标
        assert performance['total_trades'] == 8  # 总共8笔交易
        assert performance['trading_days'] > 0
        assert performance['avg_trades_per_day'] > 0
        assert performance['closed_positions_count'] == 3
        
        # 验证最常交易股票
        most_traded = performance['most_traded_stock']
        assert most_traded['stock_code'] == '000001'
        assert most_traded['trade_count'] == 6  # 3次买入+3次卖出
        
        # 验证最佳表现股票
        best_performing = performance['best_performing_stock']
        assert best_performing['stock_code'] == '000001'
        assert best_performing['profit_rate'] == 50.0  # 50%收益率
        
        # 验证最差表现股票
        worst_performing = performance['worst_performing_stock']
        assert worst_performing['stock_code'] == '000002'
        assert worst_performing['profit_rate'] == -50.0  # -50%收益率
    
    def test_corrected_trades_impact_on_statistics(self, client, app, db_session):
        """测试订正交易对统计数据的影响"""
        with app.app_context():
            # 创建原始交易记录
            original_trade = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='买入',
                is_corrected=True  # 标记为已订正
            )
            original_trade.save()
            
            # 创建订正后的交易记录
            corrected_trade = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='buy',
                price=Decimal('10.50'),  # 订正后的价格
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='买入',
                original_record_id=original_trade.id,
                correction_reason='价格订正'
            )
            corrected_trade.save()
            
            # 创建价格数据
            price = StockPrice(
                stock_code='000001',
                stock_name='股票A',
                current_price=Decimal('12.00'),
                change_percent=Decimal('14.3'),
                record_date=date.today()
            )
            price.save()
        
        # 测试总体统计
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        overview = json.loads(response.data)['data']
        
        # 应该使用订正后的数据
        assert overview['total_investment'] == 10500  # 1000 * 10.50
        assert overview['total_buy_count'] == 1  # 只统计未订正的记录
        
        # 测试持仓计算
        response = client.get('/api/analytics/holdings')
        assert response.status_code == 200
        holdings = json.loads(response.data)['data']
        
        # 持仓成本应该基于订正后的价格
        holding = holdings['holdings'][0]
        assert holding['avg_cost'] == 10.5  # 订正后的价格
        assert holding['total_cost'] == 10500
    
    def test_multi_year_statistics(self, client, app, db_session):
        """测试跨年度统计数据"""
        with app.app_context():
            # 创建2023年的交易
            trade_2023 = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='buy',
                price=Decimal('8.00'),
                quantity=1000,
                trade_date=datetime(2023, 12, 15),
                reason='买入'
            )
            trade_2023.save()
            
            # 创建2024年的交易
            trade_2024 = TradeRecord(
                stock_code='000002',
                stock_name='股票B',
                trade_type='buy',
                price=Decimal('12.00'),
                quantity=500,
                trade_date=datetime(2024, 1, 15),
                reason='买入'
            )
            trade_2024.save()
        
        # 测试2023年统计
        response = client.get('/api/analytics/monthly?year=2023')
        assert response.status_code == 200
        data_2023 = json.loads(response.data)['data']
        
        assert data_2023['year_summary']['total_buy_count'] == 1
        dec_data = next(m for m in data_2023['monthly_data'] if m['month'] == 12)
        assert dec_data['buy_count'] == 1
        
        # 测试2024年统计
        response = client.get('/api/analytics/monthly?year=2024')
        assert response.status_code == 200
        data_2024 = json.loads(response.data)['data']
        
        assert data_2024['year_summary']['total_buy_count'] == 1
        jan_data = next(m for m in data_2024['monthly_data'] if m['month'] == 1)
        assert jan_data['buy_count'] == 1
    
    def test_edge_cases_and_boundary_conditions(self, client, app, db_session):
        """测试边界条件和特殊情况"""
        with app.app_context():
            # 测试零价格交易（理论上不应该存在，但测试健壮性）
            # 注意：由于有验证，这里创建正常的最小价格交易
            min_price_trade = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='buy',
                price=Decimal('0.01'),  # 最小价格
                quantity=100000,  # 大数量
                trade_date=datetime(2024, 1, 1),
                reason='买入'
            )
            min_price_trade.save()
            
            # 创建对应的价格数据
            price = StockPrice(
                stock_code='000001',
                stock_name='股票A',
                current_price=Decimal('0.02'),  # 100%收益率
                change_percent=Decimal('100.0'),
                record_date=date.today()
            )
            price.save()
        
        # 测试统计计算的准确性
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        overview = json.loads(response.data)['data']
        
        assert overview['total_investment'] == 1000  # 0.01 * 100000
        assert overview['current_holdings_count'] == 1
        
        # 测试收益分布
        response = client.get('/api/analytics/profit-distribution')
        assert response.status_code == 200
        distribution = json.loads(response.data)['data']
        
        # 100%收益率应该在> 50%区间
        ranges = {r['range']: r for r in distribution['profit_ranges']}
        assert ranges['> 50%']['count'] == 1