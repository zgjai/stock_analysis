"""
非交易日配置功能测试用例
测试非交易日配置、交易日判断、持仓天数计算等功能
"""
import pytest
from datetime import date, datetime, timedelta
from models.non_trading_day import NonTradingDay
from models.trade_record import TradeRecord
from services.non_trading_day_service import NonTradingDayService
from decimal import Decimal


class TestNonTradingDayFunctionality:
    """非交易日配置功能测试类"""
    
    def test_weekend_auto_exclusion(self, db_session):
        """测试周末自动排除功能"""
        # 测试周六
        saturday = date(2024, 1, 6)  # 2024年1月6日是周六
        assert NonTradingDay.is_trading_day(saturday) == False
        
        # 测试周日
        sunday = date(2024, 1, 7)  # 2024年1月7日是周日
        assert NonTradingDay.is_trading_day(sunday) == False
        
        # 测试工作日
        monday = date(2024, 1, 8)  # 2024年1月8日是周一
        assert NonTradingDay.is_trading_day(monday) == True
    
    def test_holiday_configuration(self, db_session):
        """测试节假日配置功能"""
        # 添加春节假期
        spring_festival_days = [
            NonTradingDay(
                date=date(2024, 2, 10),
                name='春节',
                type='holiday',
                description='2024年春节假期'
            ),
            NonTradingDay(
                date=date(2024, 2, 11),
                name='春节',
                type='holiday',
                description='2024年春节假期'
            ),
            NonTradingDay(
                date=date(2024, 2, 12),
                name='春节',
                type='holiday',
                description='2024年春节假期'
            )
        ]
        
        db_session.add_all(spring_festival_days)
        db_session.commit()
        
        # 验证节假日不是交易日
        assert NonTradingDay.is_trading_day(date(2024, 2, 10)) == False
        assert NonTradingDay.is_trading_day(date(2024, 2, 11)) == False
        assert NonTradingDay.is_trading_day(date(2024, 2, 12)) == False
        
        # 验证非节假日是交易日（假设是工作日）
        assert NonTradingDay.is_trading_day(date(2024, 2, 9)) == True  # 周五
        assert NonTradingDay.is_trading_day(date(2024, 2, 13)) == True  # 周二
    
    def test_trading_days_calculation(self, db_session):
        """测试交易日数量计算"""
        # 添加一个节假日
        holiday = NonTradingDay(
            date=date(2024, 1, 10),  # 周三
            name='测试节假日',
            type='holiday'
        )
        db_session.add(holiday)
        db_session.commit()
        
        # 计算2024年1月8日（周一）到1月12日（周五）的交易日
        start_date = date(2024, 1, 8)
        end_date = date(2024, 1, 12)
        
        trading_days = NonTradingDay.calculate_trading_days(start_date, end_date)
        
        # 应该是4天：周一、周二、周四、周五（排除周三节假日）
        assert trading_days == 4
    
    def test_trading_days_calculation_with_weekends(self, db_session):
        """测试包含周末的交易日计算"""
        # 计算一周的交易日（包含周末）
        start_date = date(2024, 1, 8)   # 周一
        end_date = date(2024, 1, 14)    # 周日
        
        trading_days = NonTradingDay.calculate_trading_days(start_date, end_date)
        
        # 应该是5天：周一到周五
        assert trading_days == 5
    
    def test_holding_days_calculation_basic(self, db_session):
        """测试基本持仓天数计算"""
        # 创建买入记录
        buy_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.00'),
            quantity=1000,
            trade_date=datetime(2024, 1, 8, 9, 30),  # 周一
            reason='买入'
        )
        
        # 创建卖出记录
        sell_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='sell',
            price=Decimal('12.00'),
            quantity=1000,
            trade_date=datetime(2024, 1, 12, 14, 30),  # 周五
            reason='卖出'
        )
        
        db_session.add_all([buy_trade, sell_trade])
        db_session.commit()
        
        # 计算持仓天数
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(
            buy_trade.trade_date.date(),
            sell_trade.trade_date.date()
        )
        
        # 周一到周五应该是5个交易日
        assert holding_days == 5
    
    def test_holding_days_calculation_with_holidays(self, db_session):
        """测试包含节假日的持仓天数计算"""
        # 添加节假日
        holiday = NonTradingDay(
            date=date(2024, 1, 10),  # 周三
            name='测试节假日',
            type='holiday'
        )
        db_session.add(holiday)
        db_session.commit()
        
        # 创建交易记录
        buy_date = date(2024, 1, 8)   # 周一
        sell_date = date(2024, 1, 12)  # 周五
        
        service = NonTradingDayService()
        holding_days = service.calculate_holding_days(buy_date, sell_date)
        
        # 应该是4天：周一、周二、周四、周五（排除周三节假日）
        assert holding_days == 4
    
    def test_current_holdings_with_holding_days(self, db_session):
        """测试当前持仓的持仓天数计算"""
        # 创建持仓记录
        buy_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.00'),
            quantity=1000,
            trade_date=datetime(2024, 1, 8, 9, 30),  # 几天前
            reason='买入'
        )
        
        db_session.add(buy_trade)
        db_session.commit()
        
        # 获取当前持仓及持仓天数
        service = NonTradingDayService()
        holdings = service.get_current_holdings_with_days()
        
        assert len(holdings) == 1
        assert holdings[0]['stock_code'] == '000001'
        assert holdings[0]['holding_days'] > 0
    
    def test_multiple_buys_holding_days(self, db_session):
        """测试多次买入的持仓天数计算"""
        # 第一次买入
        buy_trade1 = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.00'),
            quantity=500,
            trade_date=datetime(2024, 1, 8, 9, 30),  # 较早日期
            reason='第一次买入'
        )
        
        # 第二次买入
        buy_trade2 = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('11.00'),
            quantity=500,
            trade_date=datetime(2024, 1, 15, 9, 30),  # 较晚日期
            reason='第二次买入'
        )
        
        db_session.add_all([buy_trade1, buy_trade2])
        db_session.commit()
        
        # 获取持仓天数（应该基于最早买入日期）
        service = NonTradingDayService()
        holdings = service.get_current_holdings_with_days()
        
        assert len(holdings) == 1
        # 持仓天数应该基于第一次买入日期计算
        expected_days = NonTradingDay.calculate_trading_days(
            date(2024, 1, 8), 
            date.today()
        )
        assert holdings[0]['holding_days'] == expected_days
    
    def test_non_trading_day_api_integration(self, client, db_session):
        """测试非交易日API集成"""
        # 测试添加非交易日
        holiday_data = {
            'date': '2024-05-01',
            'name': '劳动节',
            'type': 'holiday',
            'description': '2024年劳动节'
        }
        
        response = client.post('/api/non-trading-days',
                             json=holiday_data)
        assert response.status_code == 201
        
        # 测试获取非交易日列表
        response = client.get('/api/non-trading-days')
        assert response.status_code == 200
        
        holidays = response.get_json()
        assert len(holidays) >= 1
        assert any(h['name'] == '劳动节' for h in holidays)
        
        # 测试删除非交易日
        holiday_id = next(h['id'] for h in holidays if h['name'] == '劳动节')
        response = client.delete(f'/api/non-trading-days/{holiday_id}')
        assert response.status_code == 200
    
    def test_trading_day_validation_api(self, client, db_session):
        """测试交易日验证API"""
        # 添加节假日
        holiday = NonTradingDay(
            date=date(2024, 5, 1),
            name='劳动节',
            type='holiday'
        )
        db_session.add(holiday)
        db_session.commit()
        
        # 测试工作日验证
        response = client.get('/api/non-trading-days/validate?date=2024-05-02')  # 假设是工作日
        assert response.status_code == 200
        result = response.get_json()
        assert result['is_trading_day'] == True
        
        # 测试节假日验证
        response = client.get('/api/non-trading-days/validate?date=2024-05-01')
        assert response.status_code == 200
        result = response.get_json()
        assert result['is_trading_day'] == False
        
        # 测试周末验证
        response = client.get('/api/non-trading-days/validate?date=2024-05-04')  # 假设是周六
        assert response.status_code == 200
        result = response.get_json()
        assert result['is_trading_day'] == False
    
    def test_edge_cases_same_day_trading(self, db_session):
        """测试边界条件：同一天买卖"""
        buy_date = date(2024, 1, 8)  # 周一
        sell_date = date(2024, 1, 8)  # 同一天
        
        trading_days = NonTradingDay.calculate_trading_days(buy_date, sell_date)
        assert trading_days == 1  # 同一天应该算1个交易日
    
    def test_edge_cases_non_trading_day_buy_sell(self, db_session):
        """测试边界条件：在非交易日买卖"""
        # 添加节假日
        holiday = NonTradingDay(
            date=date(2024, 1, 10),
            name='测试节假日',
            type='holiday'
        )
        db_session.add(holiday)
        db_session.commit()
        
        # 在节假日买入和卖出
        buy_date = date(2024, 1, 10)
        sell_date = date(2024, 1, 10)
        
        trading_days = NonTradingDay.calculate_trading_days(buy_date, sell_date)
        assert trading_days == 0  # 非交易日应该是0天
    
    def test_bulk_holiday_import(self, db_session):
        """测试批量导入节假日"""
        # 模拟批量导入2024年所有节假日
        holidays_2024 = [
            {'date': date(2024, 1, 1), 'name': '元旦', 'type': 'holiday'},
            {'date': date(2024, 2, 10), 'name': '春节', 'type': 'holiday'},
            {'date': date(2024, 2, 11), 'name': '春节', 'type': 'holiday'},
            {'date': date(2024, 2, 12), 'name': '春节', 'type': 'holiday'},
            {'date': date(2024, 4, 4), 'name': '清明节', 'type': 'holiday'},
            {'date': date(2024, 5, 1), 'name': '劳动节', 'type': 'holiday'},
            {'date': date(2024, 6, 10), 'name': '端午节', 'type': 'holiday'},
            {'date': date(2024, 9, 17), 'name': '中秋节', 'type': 'holiday'},
            {'date': date(2024, 10, 1), 'name': '国庆节', 'type': 'holiday'},
            {'date': date(2024, 10, 2), 'name': '国庆节', 'type': 'holiday'},
            {'date': date(2024, 10, 3), 'name': '国庆节', 'type': 'holiday'},
        ]
        
        # 批量添加
        for holiday_data in holidays_2024:
            holiday = NonTradingDay(**holiday_data)
            db_session.add(holiday)
        
        db_session.commit()
        
        # 验证所有节假日都不是交易日
        for holiday_data in holidays_2024:
            assert NonTradingDay.is_trading_day(holiday_data['date']) == False
        
        # 验证节假日数量
        total_holidays = NonTradingDay.query.count()
        assert total_holidays == len(holidays_2024)