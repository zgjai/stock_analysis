"""
浮盈计算API端点测试
"""
import pytest
import json
from decimal import Decimal
from datetime import datetime
from extensions import db
from models.trade_record import TradeRecord
from models.review_record import ReviewRecord


class TestFloatingProfitAPI:
    """浮盈计算API测试类"""
    
    def test_calculate_floating_profit_success(self, client, db_session):
        """测试成功计算浮盈"""
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
        
        # 发送API请求
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={
                                 'stock_code': '000001',
                                 'current_price': 12.00
                             })
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == '浮盈计算成功'
        
        result = data['data']
        assert result['stock_code'] == '000001'
        assert result['buy_price'] == 10.00
        assert result['current_price'] == 12.00
        assert abs(result['floating_profit_ratio'] - 0.20) < 0.001
        assert abs(result['floating_profit_amount'] - 2.00) < 0.001
        assert result['formatted_ratio'] == '+20.00%'
        assert result['color_class'] == 'text-success'
        assert result['is_profit'] is True
        assert result['is_loss'] is False
    
    def test_calculate_floating_profit_loss(self, client, db_session):
        """测试计算亏损情况"""
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
        
        # 发送API请求（当前价格低于买入价格）
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={
                                 'stock_code': '000001',
                                 'current_price': 8.50
                             })
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        result = data['data']
        
        assert result['stock_code'] == '000001'
        assert result['buy_price'] == 10.00
        assert result['current_price'] == 8.50
        assert abs(result['floating_profit_ratio'] - (-0.15)) < 0.001
        assert abs(result['floating_profit_amount'] - (-1.50)) < 0.001
        assert result['formatted_ratio'] == '-15.00%'
        assert result['color_class'] == 'text-danger'
        assert result['is_profit'] is False
        assert result['is_loss'] is True
    
    def test_calculate_floating_profit_no_buy_records(self, client, db_session):
        """测试没有买入记录的情况"""
        # 发送API请求（没有创建买入记录）
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={
                                 'stock_code': '999999',
                                 'current_price': 12.00
                             })
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        result = data['data']
        
        assert result['stock_code'] == '999999'
        assert result['buy_price'] is None
        assert result['current_price'] == 12.00
        assert result['floating_profit_ratio'] is None
        assert result['floating_profit_amount'] is None
        assert result['formatted_ratio'] == '无法计算'
        assert result['color_class'] == 'text-muted'
        assert result['message'] == '未找到买入记录'
    
    def test_calculate_floating_profit_missing_stock_code(self, client, db_session):
        """测试缺少股票代码的情况"""
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={
                                 'current_price': 12.00
                             })
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert '股票代码不能为空' in data['error']['message']
    
    def test_calculate_floating_profit_missing_current_price(self, client, db_session):
        """测试缺少当前价格的情况"""
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={
                                 'stock_code': '000001'
                             })
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert '当前价格不能为空' in data['error']['message']
    
    def test_calculate_floating_profit_invalid_current_price(self, client, db_session):
        """测试无效当前价格的情况"""
        # 测试负数价格
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={
                                 'stock_code': '000001',
                                 'current_price': -5.00
                             })
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert '当前价格必须大于0' in data['error']['message']
        
        # 测试非数字价格
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={
                                 'stock_code': '000001',
                                 'current_price': 'invalid'
                             })
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert '当前价格必须是有效数字' in data['error']['message']
    
    def test_calculate_floating_profit_zero_current_price(self, client, db_session):
        """测试零价格的情况"""
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={
                                 'stock_code': '000001',
                                 'current_price': 0
                             })
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert '当前价格必须大于0' in data['error']['message']
    
    def test_calculate_floating_profit_empty_request(self, client, db_session):
        """测试空请求的情况"""
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={})
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert '股票代码不能为空' in data['error']['message']
    
    def test_calculate_floating_profit_null_request(self, client, db_session):
        """测试null请求的情况"""
        response = client.post('/api/reviews/calculate-floating-profit', 
                             data=None,
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert '请求数据格式错误' in data['error']['message']
    
    def test_calculate_floating_profit_multiple_buys(self, client, db_session):
        """测试多次买入的加权平均成本价计算"""
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
        
        # 发送API请求
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={
                                 'stock_code': '000001',
                                 'current_price': 11.00
                             })
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        result = data['data']
        
        # 加权平均成本价应该是 (8.00 * 500 + 12.00 * 500) / 1000 = 10.00
        assert result['buy_price'] == 10.00
        assert result['current_price'] == 11.00
        assert abs(result['floating_profit_ratio'] - 0.10) < 0.001  # 10%涨幅
        assert result['formatted_ratio'] == '+10.00%'
    
    def test_calculate_floating_profit_string_price(self, client, db_session):
        """测试字符串格式的价格"""
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
        
        # 发送API请求（使用字符串格式的价格）
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={
                                 'stock_code': '000001',
                                 'current_price': '12.50'
                             })
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        result = data['data']
        
        assert result['current_price'] == 12.50
        assert abs(result['floating_profit_ratio'] - 0.25) < 0.001  # 25%涨幅
        assert result['formatted_ratio'] == '+25.00%'
    
    def test_calculate_floating_profit_precision(self, client, db_session):
        """测试计算精度"""
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
        
        # 发送API请求
        response = client.post('/api/reviews/calculate-floating-profit', 
                             json={
                                 'stock_code': '000001',
                                 'current_price': 10.23
                             })
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        result = data['data']
        
        expected_ratio = (10.23 - 9.87) / 9.87  # 约 0.0365
        expected_amount = 10.23 - 9.87  # 0.36
        
        assert abs(result['floating_profit_ratio'] - expected_ratio) < 0.0001
        assert abs(result['floating_profit_amount'] - expected_amount) < 0.001
        assert result['formatted_ratio'] == '+3.65%'