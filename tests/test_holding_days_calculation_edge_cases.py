"""
持仓天数计算边界条件测试
测试各种边界情况下的持仓天数计算准确性
"""
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from models.trade_record import TradeRecord
from models.non_trading_day import NonTradingDay
from services.non_trading_day_service import NonTradingDayService


class TestHoldingDaysCalculationEdgeCases:
    """持仓天数计算边界条件测试类"""
    
    def test_same_day_buy_sell(self, db_session):
        """测试同一天买卖的持仓天数"""
        trade_date = date(2024, 1, 15)  # 周一
        
        # 同一天买卖
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(trade_date, trade_date)
        
        # 同一天应该算作1个交易日
        assert holding_days == 1
    
    def test_weekend_buy_sell(self, db_session):
        """测试周末买卖的持仓天数"""
        saturday = date(2024, 1, 6)   # 周六
        sunday = date(2024, 1, 7)     # 周日
        
        service = NonTradingDayService()
        
        # 周六到周日
        holding_days = service.calculate_holding_days(saturday, sunday)
        assert holding_days == 0  # 周末不是交易日
        
        # 周六到下周一
        monday = date(2024, 1, 8)
        holding_days = service.calculate_holding_days(saturday, monday)
        assert holding_days == 1  # 只有周一是交易日
    
    def test_holiday_period_calculation(self, db_session):
        """测试节假日期间的持仓天数计算"""
        # 添加春节假期（连续多天）
        spring_festival_days = [
            NonTradingDay(
                date=date(2024, 2, 10), name='春节', type='holiday'
            ),
            NonTradingDay(
                date=date(2024, 2, 11), name='春节', type='holiday'
            ),
            NonTradingDay(
                date=date(2024, 2, 12), name='春节', type='holiday'
            ),
            NonTradingDay(
                date=date(2024, 2, 13), name='春节', type='holiday'
            ),
            NonTradingDay(
                date=date(2024, 2, 14), name='春节', type='holiday'
            )
        ]
        db_session.add_all(spring_festival_days)
        db_session.commit()
        
        # 春节前买入，春节后卖出
        buy_date = date(2024, 2, 9)   # 春节前最后一个交易日（周五）
        sell_date = date(2024, 2, 15)  # 春节后第一个交易日（周四）
        
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(buy_date, sell_date)
        
        # 应该只计算2个交易日：2月9日和2月15日
        assert holding_days == 2
    
    def test_cross_month_calculation(self, db_session):
        """测试跨月持仓天数计算"""
        # 1月最后一天到2月第一天
        buy_date = date(2024, 1, 31)   # 周三
        sell_date = date(2024, 2, 1)   # 周四
        
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(buy_date, sell_date)
        
        assert holding_days == 2  # 两个交易日
    
    def test_cross_year_calculation(self, db_session):
        """测试跨年持仓天数计算"""
        # 添加元旦假期
        new_year = NonTradingDay(
            date=date(2024, 1, 1), name='元旦', type='holiday'
        )
        db_session.add(new_year)
        db_session.commit()
        
        # 2023年最后一个交易日到2024年第一个交易日
        buy_date = date(2023, 12, 29)  # 2023年最后一个交易日（周五）
        sell_date = date(2024, 1, 2)   # 2024年第一个交易日（周二）
        
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(buy_date, sell_date)
        
        # 应该是2个交易日：12月29日和1月2日
        # （排除12月30-31日周末和1月1日元旦）
        assert holding_days == 2
    
    def test_leap_year_february_calculation(self, db_session):
        """测试闰年2月的持仓天数计算"""
        # 2024年是闰年，2月有29天
        buy_date = date(2024, 2, 28)   # 2月28日
        sell_date = date(2024, 2, 29)  # 2月29日（闰年特有）
        
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(buy_date, sell_date)
        
        assert holding_days == 2  # 两个交易日
    
    def test_very_long_holding_period(self, db_session):
        """测试很长持仓期间的计算"""
        # 持仓一整年
        buy_date = date(2024, 1, 2)    # 年初第一个交易日
        sell_date = date(2024, 12, 31)  # 年末最后一个交易日
        
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(buy_date, sell_date)
        
        # 验证结果合理性（大约250个交易日左右）
        assert 240 <= holding_days <= 260
    
    def test_negative_date_range(self, db_session):
        """测试负日期范围（卖出日期早于买入日期）"""
        buy_date = date(2024, 2, 15)
        sell_date = date(2024, 1, 15)  # 早于买入日期
        
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(buy_date, sell_date)
        
        # 应该返回0或处理错误情况
        assert holding_days == 0
    
    def test_multiple_buys_earliest_date_calculation(self, db_session):
        """测试多次买入时基于最早日期的持仓天数计算"""
        # 创建多次买入记录
        trades = [
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('10.00'), quantity=500,
                trade_date=datetime(2024, 1, 15, 9, 30),  # 第一次买入
                reason='第一次买入'
            ),
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('11.00'), quantity=300,
                trade_date=datetime(2024, 1, 25, 10, 30),  # 第二次买入
                reason='第二次买入'
            ),
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('12.00'), quantity=200,
                trade_date=datetime(2024, 2, 5, 14, 30),   # 第三次买入
                reason='第三次买入'
            )
        ]
        
        db_session.add_all(trades)
        db_session.commit()
        
        # 获取当前持仓及持仓天数
        service = NonTradingDayService()
        holdings = service.get_current_holdings_with_days()
        
        assert len(holdings) == 1
        holding = holdings[0]
        
        # 持仓天数应该基于最早买入日期（1月15日）计算
        expected_days = NonTradingDay.calculate_trading_days(
            date(2024, 1, 15),
            date.today()
        )
        assert holding['holding_days'] == expected_days
    
    def test_partial_sell_holding_days_update(self, db_session):
        """测试部分卖出后持仓天数的更新"""
        # 创建买入记录
        buy_trade = TradeRecord(
            stock_code='000001', stock_name='平安银行',
            trade_type='buy', price=Decimal('10.00'), quantity=1000,
            trade_date=datetime(2024, 1, 15, 9, 30),
            reason='买入'
        )
        
        # 创建部分卖出记录
        sell_trade = TradeRecord(
            stock_code='000001', stock_name='平安银行',
            trade_type='sell', price=Decimal('12.00'), quantity=400,
            trade_date=datetime(2024, 2, 15, 14, 30),
            reason='部分卖出'
        )
        
        db_session.add_all([buy_trade, sell_trade])
        db_session.commit()
        
        # 获取当前持仓
        service = NonTradingDayService()
        holdings = service.get_current_holdings_with_days()
        
        assert len(holdings) == 1
        holding = holdings[0]
        
        # 剩余持仓数量应该正确
        assert holding['quantity'] == 600  # 1000 - 400
        
        # 持仓天数仍然基于最初买入日期
        expected_days = NonTradingDay.calculate_trading_days(
            date(2024, 1, 15),
            date.today()
        )
        assert holding['holding_days'] == expected_days
    
    def test_complete_sell_no_holding_days(self, db_session):
        """测试完全卖出后无持仓天数"""
        # 创建完整买卖周期
        trades = [
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 15, 9, 30),
                reason='买入'
            ),
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='sell', price=Decimal('12.00'), quantity=1000,
                trade_date=datetime(2024, 2, 15, 14, 30),
                reason='全部卖出'
            )
        ]
        
        db_session.add_all(trades)
        db_session.commit()
        
        # 获取当前持仓
        service = NonTradingDayService()
        holdings = service.get_current_holdings_with_days()
        
        # 应该没有持仓
        assert len(holdings) == 0
    
    def test_holiday_on_buy_sell_dates(self, db_session):
        """测试买入或卖出日期恰好是节假日的情况"""
        # 添加节假日
        holiday = NonTradingDay(
            date=date(2024, 5, 1), name='劳动节', type='holiday'
        )
        db_session.add(holiday)
        db_session.commit()
        
        # 在节假日买入，工作日卖出
        buy_date = date(2024, 5, 1)   # 劳动节（节假日）
        sell_date = date(2024, 5, 2)  # 工作日
        
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(buy_date, sell_date)
        
        # 节假日不算交易日，只有卖出日算交易日
        assert holding_days == 1
    
    def test_weekend_and_holiday_combination(self, db_session):
        """测试周末和节假日组合的情况"""
        # 添加周一的节假日
        holiday = NonTradingDay(
            date=date(2024, 1, 8), name='测试节假日', type='holiday'  # 周一
        )
        db_session.add(holiday)
        db_session.commit()
        
        # 周五买入，下周二卖出（跨过周末+周一节假日）
        buy_date = date(2024, 1, 5)   # 周五
        sell_date = date(2024, 1, 9)  # 周二
        
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(buy_date, sell_date)
        
        # 只有周五和周二是交易日
        assert holding_days == 2
    
    def test_current_date_calculation(self, db_session):
        """测试基于当前日期的持仓天数计算"""
        # 创建几天前的买入记录
        days_ago = 5
        buy_date = date.today() - timedelta(days=days_ago)
        
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(buy_date, None)  # None表示使用当前日期
        
        # 验证结果合理性
        assert holding_days >= 1
        assert holding_days <= days_ago + 1  # 不会超过实际天数
    
    def test_extreme_date_values(self, db_session):
        """测试极端日期值"""
        service = NonTradingDayService()
        
        # 测试很早的日期
        very_old_date = date(1990, 1, 1)
        recent_date = date(2024, 1, 1)
        
        holding_days = service.calculate_holding_days(very_old_date, recent_date)
        
        # 应该能正常计算，不会出错
        assert holding_days > 0
        assert holding_days < 10000  # 合理的上限
    
    def test_database_performance_large_date_range(self, db_session):
        """测试大日期范围的数据库性能"""
        import time
        
        # 添加一些节假日
        holidays = [
            NonTradingDay(date=date(2024, 1, 1), name='元旦', type='holiday'),
            NonTradingDay(date=date(2024, 5, 1), name='劳动节', type='holiday'),
            NonTradingDay(date=date(2024, 10, 1), name='国庆节', type='holiday'),
        ]
        db_session.add_all(holidays)
        db_session.commit()
        
        # 测试一年的日期范围
        start_time = time.time()
        
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(
            date(2024, 1, 1),
            date(2024, 12, 31)
        )
        
        end_time = time.time()
        calculation_time = end_time - start_time
        
        # 验证计算时间合理（应该在1秒内完成）
        assert calculation_time < 1.0
        assert holding_days > 0