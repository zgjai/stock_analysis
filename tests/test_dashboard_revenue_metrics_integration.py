"""
仪表板收益指标集成测试
测试已清仓收益和当前持仓收益的计算准确性
"""
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from models.trade_record import TradeRecord
from models.stock_price import StockPrice
from services.analytics_service import AnalyticsService


class TestDashboardRevenueMetricsIntegration:
    """仪表板收益指标集成测试类"""
    
    def test_realized_profit_calculation_single_stock(self, db_session):
        """测试单只股票的已清仓收益计算"""
        # 创建完整的买卖周期
        buy_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.00'),
            quantity=1000,
            trade_date=datetime(2024, 1, 15, 9, 30, 0),
            reason='测试买入'
        )
        
        sell_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='sell',
            price=Decimal('12.00'),
            quantity=1000,
            trade_date=datetime(2024, 2, 15, 14, 30, 0),
            reason='测试卖出'
        )
        
        db_session.add_all([buy_trade, sell_trade])
        db_session.commit()
        
        # 计算已清仓收益
        realized_profit = AnalyticsService.get_realized_profit()
        
        # 验证收益计算：(12.00 - 10.00) * 1000 = 2000
        expected_profit = 2000.0
        assert abs(realized_profit - expected_profit) < 0.01
    
    def test_realized_profit_calculation_multiple_stocks(self, db_session):
        """测试多只股票的已清仓收益计算"""
        # 股票1：盈利
        trades_stock1 = [
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 15), reason='买入1'
            ),
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='sell', price=Decimal('12.00'), quantity=1000,
                trade_date=datetime(2024, 2, 15), reason='卖出1'
            )
        ]
        
        # 股票2：亏损
        trades_stock2 = [
            TradeRecord(
                stock_code='000002', stock_name='万科A',
                trade_type='buy', price=Decimal('15.00'), quantity=500,
                trade_date=datetime(2024, 1, 20), reason='买入2'
            ),
            TradeRecord(
                stock_code='000002', stock_name='万科A',
                trade_type='sell', price=Decimal('13.00'), quantity=500,
                trade_date=datetime(2024, 2, 20), reason='卖出2'
            )
        ]
        
        db_session.add_all(trades_stock1 + trades_stock2)
        db_session.commit()
        
        realized_profit = AnalyticsService.get_realized_profit()
        
        # 验证总收益：股票1盈利2000 + 股票2亏损1000 = 1000
        expected_profit = 1000.0
        assert abs(realized_profit - expected_profit) < 0.01
    
    def test_realized_profit_partial_sales(self, db_session):
        """测试部分卖出情况的已清仓收益计算"""
        # 买入2000股
        buy_trade = TradeRecord(
            stock_code='000001', stock_name='平安银行',
            trade_type='buy', price=Decimal('10.00'), quantity=2000,
            trade_date=datetime(2024, 1, 15), reason='买入'
        )
        
        # 卖出1000股
        sell_trade = TradeRecord(
            stock_code='000001', stock_name='平安银行',
            trade_type='sell', price=Decimal('12.00'), quantity=1000,
            trade_date=datetime(2024, 2, 15), reason='部分卖出'
        )
        
        db_session.add_all([buy_trade, sell_trade])
        db_session.commit()
        
        realized_profit = AnalyticsService.get_realized_profit()
        
        # 验证部分卖出收益：(12.00 - 10.00) * 1000 = 2000
        expected_profit = 2000.0
        assert abs(realized_profit - expected_profit) < 0.01
    
    def test_current_holdings_profit_calculation(self, db_session):
        """测试当前持仓收益计算"""
        # 创建持仓记录
        buy_trade = TradeRecord(
            stock_code='000001', stock_name='平安银行',
            trade_type='buy', price=Decimal('10.00'), quantity=1000,
            trade_date=datetime(2024, 1, 15), reason='买入'
        )
        
        # 创建当前价格记录
        current_price = StockPrice(
            stock_code='000001',
            stock_name='平安银行',
            current_price=Decimal('11.50'),
            change_percent=Decimal('15.00'),
            record_date=date.today()
        )
        
        db_session.add_all([buy_trade, current_price])
        db_session.commit()
        
        holdings_profit = AnalyticsService.get_current_holdings_profit()
        
        # 验证持仓收益：(11.50 - 10.00) * 1000 = 1500
        expected_profit = 1500.0
        assert abs(holdings_profit - expected_profit) < 0.01
    
    def test_current_holdings_profit_multiple_buys(self, db_session):
        """测试多次买入的当前持仓收益计算"""
        # 第一次买入
        buy_trade1 = TradeRecord(
            stock_code='000001', stock_name='平安银行',
            trade_type='buy', price=Decimal('10.00'), quantity=1000,
            trade_date=datetime(2024, 1, 15), reason='第一次买入'
        )
        
        # 第二次买入
        buy_trade2 = TradeRecord(
            stock_code='000001', stock_name='平安银行',
            trade_type='buy', price=Decimal('12.00'), quantity=500,
            trade_date=datetime(2024, 2, 15), reason='第二次买入'
        )
        
        # 当前价格
        current_price = StockPrice(
            stock_code='000001',
            stock_name='平安银行',
            current_price=Decimal('13.00'),
            change_percent=Decimal('8.33'),
            record_date=date.today()
        )
        
        db_session.add_all([buy_trade1, buy_trade2, current_price])
        db_session.commit()
        
        holdings_profit = AnalyticsService.get_current_holdings_profit()
        
        # 验证持仓收益：
        # 平均成本 = (10*1000 + 12*500) / 1500 = 16000/1500 = 10.67
        # 收益 = (13.00 - 10.67) * 1500 = 3500
        expected_profit = 3500.0
        assert abs(holdings_profit - expected_profit) < 1.0  # 允许小数精度误差
    
    def test_dashboard_overall_statistics_integration(self, db_session):
        """测试仪表板整体统计数据集成"""
        # 创建已完成交易
        completed_trades = [
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 15), reason='买入'
            ),
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='sell', price=Decimal('12.00'), quantity=1000,
                trade_date=datetime(2024, 2, 15), reason='卖出'
            )
        ]
        
        # 创建当前持仓
        current_holding = TradeRecord(
            stock_code='000002', stock_name='万科A',
            trade_type='buy', price=Decimal('15.00'), quantity=500,
            trade_date=datetime(2024, 3, 15), reason='持仓买入'
        )
        
        # 当前价格
        current_price = StockPrice(
            stock_code='000002',
            stock_name='万科A',
            current_price=Decimal('16.00'),
            change_percent=Decimal('6.67'),
            record_date=date.today()
        )
        
        db_session.add_all(completed_trades + [current_holding, current_price])
        db_session.commit()
        
        # 获取整体统计数据
        stats = AnalyticsService.get_overall_statistics()
        
        # 验证统计数据包含新的收益指标
        assert 'realized_profit' in stats
        assert 'current_holdings_profit' in stats
        
        # 验证已清仓收益
        assert abs(stats['realized_profit'] - 2000.0) < 0.01
        
        # 验证当前持仓收益
        assert abs(stats['current_holdings_profit'] - 500.0) < 0.01
    
    def test_empty_data_handling(self, db_session):
        """测试空数据情况的处理"""
        # 没有任何交易记录
        realized_profit = AnalyticsService.get_realized_profit()
        holdings_profit = AnalyticsService.get_current_holdings_profit()
        
        assert realized_profit == 0.0
        assert holdings_profit == 0.0
    
    def test_missing_price_data_handling(self, db_session):
        """测试缺少价格数据的处理"""
        # 创建持仓但没有价格数据
        buy_trade = TradeRecord(
            stock_code='000001', stock_name='平安银行',
            trade_type='buy', price=Decimal('10.00'), quantity=1000,
            trade_date=datetime(2024, 1, 15), reason='买入'
        )
        
        db_session.add(buy_trade)
        db_session.commit()
        
        # 当前持仓收益应该为0（没有价格数据）
        holdings_profit = AnalyticsService.get_current_holdings_profit()
        assert holdings_profit == 0.0