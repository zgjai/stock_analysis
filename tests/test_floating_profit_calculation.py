"""
浮盈计算功能单元测试
"""
import pytest
from decimal import Decimal
from datetime import datetime, date
from extensions import db
from services.review_service import ReviewService
from models.trade_record import TradeRecord
from models.review_record import ReviewRecord
from error_handlers import ValidationError, DatabaseError


class TestFloatingProfitCalculation:
    """浮盈计算测试类"""
    
    def test_get_buy_price_single_purchase(self, db_session):
        """测试单次买入的成本价计算"""
        # 创建单次买入记录
        trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.50'),
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试买入'
        )
        trade.save()
        
        # 获取成本价
        buy_price = ReviewService.get_buy_price_for_stock('000001')
        
        assert buy_price == 10.50
    
    def test_get_buy_price_multiple_purchases(self, db_session):
        """测试多次买入的加权平均成本价计算"""
        # 创建多次买入记录
        trades = [
            TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime.now(),
                reason='第一次买入'
            ),
            TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=Decimal('12.00'),
                quantity=500,
                trade_date=datetime.now(),
                reason='第二次买入'
            )
        ]
        
        for trade in trades:
            trade.save()
        
        # 计算预期的加权平均价格: (10.00 * 1000 + 12.00 * 500) / (1000 + 500) = 16000 / 1500 = 10.67
        expected_price = 10.67
        
        buy_price = ReviewService.get_buy_price_for_stock('000001')
        
        assert abs(buy_price - expected_price) < 0.01  # 允许小数点误差
    
    def test_get_buy_price_no_records(self, db_session):
        """测试没有买入记录时返回None"""
        buy_price = ReviewService.get_buy_price_for_stock('999999')
        
        assert buy_price is None
    
    def test_get_buy_price_only_sell_records(self, db_session):
        """测试只有卖出记录时返回None"""
        # 创建卖出记录
        trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='sell',
            price=Decimal('11.00'),
            quantity=500,
            trade_date=datetime.now(),
            reason='测试卖出'
        )
        trade.save()
        
        buy_price = ReviewService.get_buy_price_for_stock('000001')
        
        assert buy_price is None
    
    def test_get_buy_price_exclude_corrected_records(self, db_session):
        """测试排除已订正的记录"""
        # 创建正常买入记录
        normal_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.00'),
            quantity=1000,
            trade_date=datetime.now(),
            reason='正常买入'
        )
        normal_trade.save()
        
        # 创建已订正的买入记录
        corrected_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('15.00'),
            quantity=1000,
            trade_date=datetime.now(),
            reason='已订正买入',
            is_corrected=True
        )
        corrected_trade.save()
        
        # 应该只计算未订正的记录
        buy_price = ReviewService.get_buy_price_for_stock('000001')
        
        assert buy_price == 10.00
    
    def test_calculate_floating_profit_positive(self, db_session):
        """测试正浮盈计算"""
        # 创建买入记录
        trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.00'),
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试买入'
        )
        trade.save()
        
        # 计算浮盈（当前价格高于买入价格）
        current_price = 12.00
        result = ReviewService.calculate_floating_profit('000001', current_price)
        
        assert result['stock_code'] == '000001'
        assert result['buy_price'] == 10.00
        assert result['current_price'] == 12.00
        assert abs(result['floating_profit_ratio'] - 0.20) < 0.001  # 20%涨幅
        assert abs(result['floating_profit_amount'] - 2.00) < 0.001  # 2元盈利
        assert result['formatted_ratio'] == '+20.00%'
        assert result['color_class'] == 'text-success'
        assert result['is_profit'] is True
        assert result['is_loss'] is False
    
    def test_calculate_floating_profit_negative(self, db_session):
        """测试负浮盈（亏损）计算"""
        # 创建买入记录
        trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.00'),
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试买入'
        )
        trade.save()
        
        # 计算浮盈（当前价格低于买入价格）
        current_price = 8.50
        result = ReviewService.calculate_floating_profit('000001', current_price)
        
        assert result['stock_code'] == '000001'
        assert result['buy_price'] == 10.00
        assert result['current_price'] == 8.50
        assert abs(result['floating_profit_ratio'] - (-0.15)) < 0.001  # -15%跌幅
        assert abs(result['floating_profit_amount'] - (-1.50)) < 0.001  # -1.5元亏损
        assert result['formatted_ratio'] == '-15.00%'
        assert result['color_class'] == 'text-danger'
        assert result['is_profit'] is False
        assert result['is_loss'] is True
    
    def test_calculate_floating_profit_zero(self, db_session):
        """测试零浮盈计算"""
        # 创建买入记录
        trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.00'),
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试买入'
        )
        trade.save()
        
        # 计算浮盈（当前价格等于买入价格）
        current_price = 10.00
        result = ReviewService.calculate_floating_profit('000001', current_price)
        
        assert result['stock_code'] == '000001'
        assert result['buy_price'] == 10.00
        assert result['current_price'] == 10.00
        assert result['floating_profit_ratio'] == 0.0
        assert result['floating_profit_amount'] == 0.0
        assert result['formatted_ratio'] == '0.00%'
        assert result['color_class'] == 'text-muted'
        assert result['is_profit'] is False
        assert result['is_loss'] is False
    
    def test_calculate_floating_profit_no_buy_records(self, db_session):
        """测试没有买入记录时的浮盈计算"""
        current_price = 12.00
        result = ReviewService.calculate_floating_profit('999999', current_price)
        
        assert result['stock_code'] == '999999'
        assert result['buy_price'] is None
        assert result['current_price'] == 12.00
        assert result['floating_profit_ratio'] is None
        assert result['floating_profit_amount'] is None
        assert result['formatted_ratio'] == '无法计算'
        assert result['color_class'] == 'text-muted'
        assert result['is_profit'] is False
        assert result['is_loss'] is False
        assert result['message'] == '未找到买入记录'
    
    def test_calculate_floating_profit_precision(self, db_session):
        """测试浮盈计算的精度"""
        # 创建买入记录
        trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('9.87'),
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试买入'
        )
        trade.save()
        
        # 计算浮盈（测试小数精度）
        current_price = 10.23
        result = ReviewService.calculate_floating_profit('000001', current_price)
        
        expected_ratio = (10.23 - 9.87) / 9.87  # 约 0.0365
        expected_amount = 10.23 - 9.87  # 0.36
        
        assert abs(result['floating_profit_ratio'] - expected_ratio) < 0.0001
        assert abs(result['floating_profit_amount'] - expected_amount) < 0.001
        assert result['formatted_ratio'] == '+3.65%'
    
    def test_calculate_floating_profit_multiple_buys(self, db_session):
        """测试多次买入后的浮盈计算"""
        # 创建多次买入记录
        trades = [
            TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=Decimal('8.00'),
                quantity=500,
                trade_date=datetime.now(),
                reason='第一次买入'
            ),
            TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=Decimal('12.00'),
                quantity=500,
                trade_date=datetime.now(),
                reason='第二次买入'
            )
        ]
        
        for trade in trades:
            trade.save()
        
        # 加权平均成本价: (8.00 * 500 + 12.00 * 500) / 1000 = 10.00
        current_price = 11.00
        result = ReviewService.calculate_floating_profit('000001', current_price)
        
        assert result['buy_price'] == 10.00
        assert result['current_price'] == 11.00
        assert abs(result['floating_profit_ratio'] - 0.10) < 0.001  # 10%涨幅
        assert result['formatted_ratio'] == '+10.00%'


class TestReviewRecordFloatingProfitMethods:
    """测试ReviewRecord模型的浮盈相关方法"""
    
    def test_calculate_floating_profit_method(self, db_session):
        """测试ReviewRecord的calculate_floating_profit方法"""
        review = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            buy_price=Decimal('10.00'),
            price_up_score=1,
            bbi_score=1,
            volume_score=0,
            trend_score=1,
            j_score=1
        )
        
        # 计算浮盈
        ratio = review.calculate_floating_profit(12.00)
        
        assert ratio == 0.20  # 20%涨幅
        assert float(review.current_price) == 12.00
        assert float(review.floating_profit_ratio) == 0.20
    
    def test_calculate_floating_profit_no_buy_price(self, db_session):
        """测试没有买入价格时的浮盈计算"""
        review = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            price_up_score=1,
            bbi_score=1,
            volume_score=0,
            trend_score=1,
            j_score=1
        )
        
        # 没有买入价格时应该返回None
        ratio = review.calculate_floating_profit(12.00)
        
        assert ratio is None
        assert review.current_price is None
        assert review.floating_profit_ratio is None
    
    def test_get_floating_profit_display(self, db_session):
        """测试浮盈显示格式化"""
        review = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            buy_price=Decimal('10.00'),
            current_price=Decimal('12.00'),
            floating_profit_ratio=Decimal('0.20'),
            price_up_score=1,
            bbi_score=1,
            volume_score=0,
            trend_score=1,
            j_score=1
        )
        
        display = review.get_floating_profit_display()
        
        assert display['ratio'] == 0.20
        assert display['display'] == '+20.00%'
        assert display['color'] == 'text-success'
    
    def test_get_floating_profit_display_negative(self, db_session):
        """测试负浮盈显示格式化"""
        review = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            buy_price=Decimal('10.00'),
            current_price=Decimal('8.50'),
            floating_profit_ratio=Decimal('-0.15'),
            price_up_score=1,
            bbi_score=1,
            volume_score=0,
            trend_score=1,
            j_score=1
        )
        
        display = review.get_floating_profit_display()
        
        assert display['ratio'] == -0.15
        assert display['display'] == '-15.00%'
        assert display['color'] == 'text-danger'
    
    def test_get_floating_profit_display_none(self, db_session):
        """测试无浮盈数据时的显示格式化"""
        review = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            price_up_score=1,
            bbi_score=1,
            volume_score=0,
            trend_score=1,
            j_score=1
        )
        
        display = review.get_floating_profit_display()
        
        assert display['ratio'] is None
        assert display['display'] == '无法计算'
        assert display['color'] == 'text-muted'
    
    def test_update_floating_profit(self, db_session):
        """测试更新浮盈数据"""
        review = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            price_up_score=1,
            bbi_score=1,
            volume_score=0,
            trend_score=1,
            j_score=1
        )
        
        # 更新浮盈数据
        ratio = review.update_floating_profit(12.00, 10.00)
        
        assert ratio == 0.20
        assert float(review.buy_price) == 10.00
        assert float(review.current_price) == 12.00
        assert float(review.floating_profit_ratio) == 0.20
    
    def test_to_dict_includes_floating_profit_display(self, db_session):
        """测试to_dict方法包含浮盈显示数据"""
        review = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            buy_price=Decimal('10.00'),
            current_price=Decimal('11.50'),
            floating_profit_ratio=Decimal('0.15'),
            price_up_score=1,
            bbi_score=1,
            volume_score=0,
            trend_score=1,
            j_score=1
        )
        
        data = review.to_dict()
        
        assert 'floating_profit_display' in data
        assert data['floating_profit_display']['display'] == '+15.00%'
        assert data['floating_profit_display']['color'] == 'text-success'
        assert data['buy_price'] == 10.00
        assert data['current_price'] == 11.50
        assert data['floating_profit_ratio'] == 0.15