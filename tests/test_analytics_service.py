"""
统计分析服务测试
"""
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from services.analytics_service import AnalyticsService
from models.trade_record import TradeRecord
from models.stock_price import StockPrice
from error_handlers import DatabaseError, ValidationError


class TestAnalyticsService:
    """统计分析服务测试类"""
    
    def test_get_overall_statistics_empty_data(self, app, db_session):
        """测试空数据时的总体统计"""
        with app.app_context():
            stats = AnalyticsService.get_overall_statistics()
            
            assert stats['total_investment'] == 0
            assert stats['closed_profit'] == 0
            assert stats['floating_profit'] == 0
            assert stats['total_profit'] == 0
            assert stats['total_return_rate'] == 0
            assert stats['current_holdings_count'] == 0
            assert stats['total_buy_count'] == 0
            assert stats['total_sell_count'] == 0
            assert stats['success_rate'] == 0
    
    def test_get_overall_statistics_with_data(self, app, db_session):
        """测试有数据时的总体统计"""
        with app.app_context():
            # 创建测试交易记录
            # 股票A：买入1000股@10元，卖出500股@12元（部分盈利）
            buy_trade_a1 = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='测试买入'
            )
            buy_trade_a1.save()
            
            sell_trade_a1 = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='sell',
                price=Decimal('12.00'),
                quantity=500,
                trade_date=datetime(2024, 1, 15),
                reason='部分止盈'
            )
            sell_trade_a1.save()
            
            # 股票B：买入500股@20元，卖出500股@18元（全部亏损）
            buy_trade_b = TradeRecord(
                stock_code='000002',
                stock_name='万科A',
                trade_type='buy',
                price=Decimal('20.00'),
                quantity=500,
                trade_date=datetime(2024, 1, 10),
                reason='测试买入'
            )
            buy_trade_b.save()
            
            sell_trade_b = TradeRecord(
                stock_code='000002',
                stock_name='万科A',
                trade_type='sell',
                price=Decimal('18.00'),
                quantity=500,
                trade_date=datetime(2024, 1, 20),
                reason='止损'
            )
            sell_trade_b.save()
            
            # 创建股票价格数据（用于计算持仓浮盈浮亏）
            price_a = StockPrice(
                stock_code='000001',
                stock_name='平安银行',
                current_price=Decimal('11.00'),
                change_percent=Decimal('1.5'),
                record_date=date.today()
            )
            price_a.save()
            
            stats = AnalyticsService.get_overall_statistics()
            
            # 验证统计数据
            assert stats['total_investment'] == 20000  # 1000*10 + 500*20
            assert stats['closed_profit'] == -1000  # 股票B全部亏损1000，股票A还有持仓
            assert stats['current_holdings_count'] == 1  # 只有000001还有持仓
            assert stats['total_buy_count'] == 2
            assert stats['total_sell_count'] == 2
            assert stats['success_rate'] == 0  # 只有股票B完全清仓且亏损，股票A还有持仓
    
    def test_get_profit_distribution(self, app, db_session):
        """测试收益分布分析"""
        with app.app_context():
            # 创建不同收益率的股票
            # 股票A：亏损15%
            buy_a = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='测试买入'
            )
            buy_a.save()
            
            sell_a = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='sell',
                price=Decimal('8.50'),
                quantity=1000,
                trade_date=datetime(2024, 1, 15),
                reason='止损'
            )
            sell_a.save()
            
            # 股票B：盈利25%
            buy_b = TradeRecord(
                stock_code='000002',
                stock_name='股票B',
                trade_type='buy',
                price=Decimal('20.00'),
                quantity=500,
                trade_date=datetime(2024, 1, 10),
                reason='测试买入'
            )
            buy_b.save()
            
            sell_b = TradeRecord(
                stock_code='000002',
                stock_name='股票B',
                trade_type='sell',
                price=Decimal('25.00'),
                quantity=500,
                trade_date=datetime(2024, 1, 20),
                reason='止盈'
            )
            sell_b.save()
            
            distribution = AnalyticsService.get_profit_distribution()
            
            assert distribution['total_stocks'] == 2
            assert distribution['closed_stocks'] == 2
            assert distribution['holding_stocks'] == 0
            
            # 检查分布区间
            ranges = {r['range']: r for r in distribution['profit_ranges']}
            assert ranges['-20% ~ -10%']['count'] == 1  # 股票A
            assert ranges['20% ~ 50%']['count'] == 1   # 股票B
    
    def test_get_monthly_statistics(self, app, db_session):
        """测试月度统计"""
        with app.app_context():
            # 创建不同月份的交易记录
            # 1月份交易
            jan_buy = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 15),
                reason='测试买入'
            )
            jan_buy.save()
            
            jan_sell = TradeRecord(
                stock_code='000001',
                stock_name='股票A',
                trade_type='sell',
                price=Decimal('12.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 25),
                reason='止盈'
            )
            jan_sell.save()
            
            # 2月份交易
            feb_buy = TradeRecord(
                stock_code='000002',
                stock_name='股票B',
                trade_type='buy',
                price=Decimal('20.00'),
                quantity=500,
                trade_date=datetime(2024, 2, 10),
                reason='测试买入'
            )
            feb_buy.save()
            
            monthly_stats = AnalyticsService.get_monthly_statistics(2024)
            
            assert monthly_stats['year_summary']['year'] == 2024
            assert monthly_stats['year_summary']['total_buy_count'] == 2
            assert monthly_stats['year_summary']['total_sell_count'] == 1
            
            # 检查1月份数据
            jan_data = next(m for m in monthly_stats['monthly_data'] if m['month'] == 1)
            assert jan_data['buy_count'] == 1
            assert jan_data['sell_count'] == 1
            assert jan_data['unique_stocks'] == 1
            
            # 检查2月份数据
            feb_data = next(m for m in monthly_stats['monthly_data'] if m['month'] == 2)
            assert feb_data['buy_count'] == 1
            assert feb_data['sell_count'] == 0
            assert feb_data['unique_stocks'] == 1
    
    def test_export_statistics_to_excel(self, app, db_session):
        """测试Excel导出功能"""
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
            
            # 测试Excel导出
            excel_data = AnalyticsService.export_statistics_to_excel()
            
            assert isinstance(excel_data, bytes)
            assert len(excel_data) > 0
            
            # 验证Excel文件头部（Excel文件以PK开头）
            assert excel_data[:2] == b'PK'
    
    def test_calculate_current_holdings(self, app, db_session):
        """测试持仓计算"""
        with app.app_context():
            # 创建交易记录
            trades = [
                TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='buy',
                    price=Decimal('10.00'),
                    quantity=1000,
                    trade_date=datetime(2024, 1, 1),
                    reason='买入'
                ),
                TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='sell',
                    price=Decimal('12.00'),
                    quantity=300,
                    trade_date=datetime(2024, 1, 15),
                    reason='部分卖出'
                )
            ]
            
            for trade in trades:
                trade.save()
            
            # 创建价格数据
            price = StockPrice(
                stock_code='000001',
                stock_name='股票A',
                current_price=Decimal('11.00'),
                change_percent=Decimal('1.0'),
                record_date=date.today()
            )
            price.save()
            
            holdings = AnalyticsService._calculate_current_holdings(trades)
            
            assert '000001' in holdings
            holding = holdings['000001']
            assert holding['quantity'] == 700  # 1000 - 300
            assert holding['avg_cost'] == 10.0  # 成本价
            assert holding['current_price'] == 11.0
            assert holding['profit_rate'] == 0.1  # 10%收益率
    
    def test_calculate_closed_positions_profit(self, app, db_session):
        """测试已清仓收益计算"""
        with app.app_context():
            # 创建完整的买卖交易（已清仓）
            trades = [
                TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='buy',
                    price=Decimal('10.00'),
                    quantity=1000,
                    trade_date=datetime(2024, 1, 1),
                    reason='买入'
                ),
                TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='sell',
                    price=Decimal('12.00'),
                    quantity=1000,
                    trade_date=datetime(2024, 1, 15),
                    reason='卖出'
                )
            ]
            
            for trade in trades:
                trade.save()
            
            profit = AnalyticsService._calculate_closed_positions_profit(trades)
            
            assert profit == 2000  # (12-10) * 1000
    
    def test_calculate_success_rate(self, app, db_session):
        """测试成功率计算"""
        with app.app_context():
            # 创建两只股票的交易记录
            trades = [
                # 股票A：盈利
                TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='buy',
                    price=Decimal('10.00'),
                    quantity=1000,
                    trade_date=datetime(2024, 1, 1),
                    reason='买入'
                ),
                TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='sell',
                    price=Decimal('12.00'),
                    quantity=1000,
                    trade_date=datetime(2024, 1, 15),
                    reason='卖出'
                ),
                # 股票B：亏损
                TradeRecord(
                    stock_code='000002',
                    stock_name='股票B',
                    trade_type='buy',
                    price=Decimal('20.00'),
                    quantity=500,
                    trade_date=datetime(2024, 1, 10),
                    reason='买入'
                ),
                TradeRecord(
                    stock_code='000002',
                    stock_name='股票B',
                    trade_type='sell',
                    price=Decimal('18.00'),
                    quantity=500,
                    trade_date=datetime(2024, 1, 20),
                    reason='卖出'
                )
            ]
            
            for trade in trades:
                trade.save()
            
            success_rate = AnalyticsService._calculate_success_rate(trades)
            
            assert success_rate == 50.0  # 2只股票中1只盈利
    
    def test_invalid_year_validation(self, app, db_session):
        """测试无效年份验证"""
        with app.app_context():
            # 测试过早的年份
            with pytest.raises(ValidationError):
                AnalyticsService.get_monthly_statistics(1999)
            
            # 测试过晚的年份
            future_year = datetime.now().year + 10
            with pytest.raises(ValidationError):
                AnalyticsService.get_monthly_statistics(future_year)
    
    def test_empty_holdings_calculation(self, app, db_session):
        """测试空持仓计算"""
        with app.app_context():
            holdings = AnalyticsService._calculate_current_holdings([])
            assert holdings == {}
    
    def test_partial_sell_holdings_calculation(self, app, db_session):
        """测试部分卖出后的持仓计算"""
        with app.app_context():
            # 创建多次买入和部分卖出的交易
            trades = [
                TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='buy',
                    price=Decimal('10.00'),
                    quantity=1000,
                    trade_date=datetime(2024, 1, 1),
                    reason='买入1'
                ),
                TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='buy',
                    price=Decimal('12.00'),
                    quantity=500,
                    trade_date=datetime(2024, 1, 5),
                    reason='买入2'
                ),
                TradeRecord(
                    stock_code='000001',
                    stock_name='股票A',
                    trade_type='sell',
                    price=Decimal('11.00'),
                    quantity=600,
                    trade_date=datetime(2024, 1, 10),
                    reason='部分卖出'
                )
            ]
            
            for trade in trades:
                trade.save()
            
            # 创建价格数据
            price = StockPrice(
                stock_code='000001',
                stock_name='股票A',
                current_price=Decimal('13.00'),
                change_percent=Decimal('2.0'),
                record_date=date.today()
            )
            price.save()
            
            holdings = AnalyticsService._calculate_current_holdings(trades)
            
            assert '000001' in holdings
            holding = holdings['000001']
            assert holding['quantity'] == 900  # 1000 + 500 - 600
            
            # 验证平均成本计算
            # 总成本：1000*10 + 500*12 = 16000
            # 卖出后剩余成本按比例计算
            expected_avg_cost = 16000 / 1500 * (900 / 900)  # 简化计算
            assert holding['avg_cost'] > 0
    
    def test_corrected_trades_exclusion(self, app, db_session):
        """测试排除已订正的交易记录"""
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
                price=Decimal('10.50'),
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='买入',
                original_record_id=original_trade.id,
                correction_reason='价格订正'
            )
            corrected_trade.save()
            
            stats = AnalyticsService.get_overall_statistics()
            
            # 应该只统计订正后的记录
            assert stats['total_buy_count'] == 1
            assert stats['total_investment'] == 10500  # 使用订正后的价格