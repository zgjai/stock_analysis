"""
输入验证测试
测试系统对各种输入数据的验证能力，包括必填字段、数值格式、日期格式等
"""
import pytest
import json
from datetime import datetime, date
from decimal import Decimal
from app import create_app
from extensions import db
from models.trade_record import TradeRecord
from models.review_record import ReviewRecord
from models.stock_pool import StockPool
from utils.validators import (
    validate_stock_code, validate_price, validate_quantity, 
    validate_trade_type, validate_ratio, validate_date,
    validate_positive_integer
)
from error_handlers import ValidationError


class TestInputValidation:
    """输入验证测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试设置"""
        from config import TestingConfig
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # 创建测试数据库表
        db.create_all()
        
        yield
        
        # 清理
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_required_fields_validation(self):
        """测试必填字段验证"""
        
        # 测试交易记录必填字段
        test_cases = [
            # 缺少股票代码
            {
                'data': {
                    'stock_name': '测试股票',
                    'trade_type': 'buy',
                    'price': 10.50,
                    'quantity': 100,
                    'reason': '技术突破'
                },
                'expected_error': 'stock_code'
            },
            # 缺少股票名称
            {
                'data': {
                    'stock_code': '000001',
                    'trade_type': 'buy',
                    'price': 10.50,
                    'quantity': 100,
                    'reason': '技术突破'
                },
                'expected_error': 'stock_name'
            },
            # 缺少交易类型
            {
                'data': {
                    'stock_code': '000001',
                    'stock_name': '测试股票',
                    'price': 10.50,
                    'quantity': 100,
                    'reason': '技术突破'
                },
                'expected_error': 'trade_type'
            },
            # 缺少价格
            {
                'data': {
                    'stock_code': '000001',
                    'stock_name': '测试股票',
                    'trade_type': 'buy',
                    'quantity': 100,
                    'reason': '技术突破'
                },
                'expected_error': 'price'
            },
            # 缺少数量
            {
                'data': {
                    'stock_code': '000001',
                    'stock_name': '测试股票',
                    'trade_type': 'buy',
                    'price': 10.50,
                    'reason': '技术突破'
                },
                'expected_error': 'quantity'
            },
            # 缺少原因
            {
                'data': {
                    'stock_code': '000001',
                    'stock_name': '测试股票',
                    'trade_type': 'buy',
                    'price': 10.50,
                    'quantity': 100
                },
                'expected_error': 'reason'
            }
        ]
        
        for case in test_cases:
            response = self.client.post(
                '/api/trades',
                data=json.dumps(case['data']),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            response_data = json.loads(response.data)
            assert not response_data['success']
            assert case['expected_error'] in response_data['error']['message'].lower()
    
    def test_stock_code_validation(self):
        """测试股票代码格式验证"""
        
        # 有效股票代码
        valid_codes = ['000001', '000002', '600000', '300001', '002001']
        for code in valid_codes:
            assert validate_stock_code(code) == True
        
        # 无效股票代码
        invalid_cases = [
            ('', '股票代码不能为空'),
            (None, '股票代码不能为空'),
            ('00001', '股票代码格式不正确'),  # 5位数字
            ('0000001', '股票代码格式不正确'),  # 7位数字
            ('00000a', '股票代码格式不正确'),  # 包含字母
            ('abc123', '股票代码格式不正确'),  # 字母开头
            ('000-01', '股票代码格式不正确'),  # 包含特殊字符
        ]
        
        for code, expected_message in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                validate_stock_code(code)
            assert expected_message in str(exc_info.value)
    
    def test_price_validation(self):
        """测试价格格式和范围验证"""
        
        # 有效价格
        valid_prices = [0.01, 1.0, 10.50, 100.99, 999.99, 9999.99]
        for price in valid_prices:
            result = validate_price(price)
            assert result == float(price)
        
        # 字符串格式的有效价格
        valid_price_strings = ['0.01', '10.50', '100.99']
        for price_str in valid_price_strings:
            result = validate_price(price_str)
            assert result == float(price_str)
        
        # 无效价格
        invalid_cases = [
            (None, '价格不能为空'),
            ('', '价格格式不正确'),  # 空字符串会被float()处理为ValueError
            (0, '价格必须大于0'),
            (-1.0, '价格必须大于0'),
            (10000.0, '价格不能超过9999.99'),
            ('abc', '价格格式不正确'),
            ('10.5.0', '价格格式不正确'),
            ('10,50', '价格格式不正确'),
        ]
        
        for price, expected_message in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                validate_price(price)
            assert expected_message in str(exc_info.value)
    
    def test_quantity_validation(self):
        """测试数量格式和范围验证"""
        
        # 有效数量
        valid_quantities = [1, 100, 1000, 10000, 999999]
        for quantity in valid_quantities:
            result = validate_quantity(quantity)
            assert result == int(quantity)
        
        # 字符串格式的有效数量
        valid_quantity_strings = ['1', '100', '1000']
        for quantity_str in valid_quantity_strings:
            result = validate_quantity(quantity_str)
            assert result == int(quantity_str)
        
        # 无效数量
        invalid_cases = [
            (None, '数量不能为空'),
            ('', '数量格式不正确'),  # 空字符串会被int()处理为ValueError
            (0, '数量必须大于0'),
            (-1, '数量必须大于0'),
            (1000000, '数量不能超过999999'),
            ('abc', '数量格式不正确'),
            ('10.5', '数量格式不正确'),
            ('1,000', '数量格式不正确'),
        ]
        
        for quantity, expected_message in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                validate_quantity(quantity)
            assert expected_message in str(exc_info.value)
    
    def test_trade_type_validation(self):
        """测试交易类型验证"""
        
        # 有效交易类型
        valid_types = ['buy', 'sell']
        for trade_type in valid_types:
            result = validate_trade_type(trade_type)
            assert result == trade_type
        
        # 无效交易类型
        invalid_cases = [
            (None, '交易类型不能为空'),
            ('', '交易类型不能为空'),
            ('BUY', '交易类型必须是buy或sell'),
            ('SELL', '交易类型必须是buy或sell'),
            ('purchase', '交易类型必须是buy或sell'),
            ('sale', '交易类型必须是buy或sell'),
            ('hold', '交易类型必须是buy或sell'),
        ]
        
        for trade_type, expected_message in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                validate_trade_type(trade_type)
            assert expected_message in str(exc_info.value)
    
    def test_ratio_validation(self):
        """测试比例值验证（0-1之间）"""
        
        # 有效比例
        valid_ratios = [0.0, 0.1, 0.5, 0.99, 1.0]
        for ratio in valid_ratios:
            result = validate_ratio(ratio, 'test_ratio')
            assert result == float(ratio)
        
        # None值应该返回None
        assert validate_ratio(None, 'test_ratio') is None
        
        # 字符串格式的有效比例
        valid_ratio_strings = ['0.1', '0.5', '0.99']
        for ratio_str in valid_ratio_strings:
            result = validate_ratio(ratio_str, 'test_ratio')
            assert result == float(ratio_str)
        
        # 无效比例
        invalid_cases = [
            (-0.1, 'test_ratio必须在0-1之间'),
            (1.1, 'test_ratio必须在0-1之间'),
            (2.0, 'test_ratio必须在0-1之间'),
            ('abc', 'test_ratio格式不正确'),
            ('1.5.0', 'test_ratio格式不正确'),
        ]
        
        for ratio, expected_message in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                validate_ratio(ratio, 'test_ratio')
            assert expected_message in str(exc_info.value)
    
    def test_date_validation(self):
        """测试日期格式验证"""
        
        # 有效日期格式
        valid_dates = [
            '2024-01-01',
            '2024-12-31',
            '2023-02-28',
            '2024-02-29',  # 闰年
        ]
        
        for date_str in valid_dates:
            result = validate_date(date_str)
            assert isinstance(result, date)
            assert result == datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 无效日期格式
        invalid_cases = [
            (None, '日期不能为空'),
            ('', '日期不能为空'),
            ('2024/01/01', '日期格式不正确'),
            ('01-01-2024', '日期格式不正确'),
            ('2024-13-01', '日期格式不正确'),  # 无效月份
            ('2024-02-30', '日期格式不正确'),  # 无效日期
            ('2023-02-29', '日期格式不正确'),  # 非闰年2月29日
            ('abc', '日期格式不正确'),
            ('2024-01-01 10:00:00', '日期格式不正确'),  # 包含时间
        ]
        
        for date_str, expected_message in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                validate_date(date_str)
            assert expected_message in str(exc_info.value)
    
    def test_positive_integer_validation(self):
        """测试正整数验证"""
        
        # 有效正整数
        valid_integers = [1, 10, 100, 1000, 999999]
        for integer in valid_integers:
            result = validate_positive_integer(integer, 'test_field')
            assert result == int(integer)
        
        # 字符串格式的有效正整数
        valid_integer_strings = ['1', '10', '100']
        for integer_str in valid_integer_strings:
            result = validate_positive_integer(integer_str, 'test_field')
            assert result == int(integer_str)
        
        # 无效正整数
        invalid_cases = [
            (None, 'test_field不能为空'),
            ('', 'test_field必须是正整数'),  # 空字符串会被int()处理为ValueError
            (0, 'test_field必须大于0'),
            (-1, 'test_field必须大于0'),
            ('abc', 'test_field必须是正整数'),
            ('10.5', 'test_field必须是正整数'),
            ('1,000', 'test_field必须是正整数'),
        ]
        
        for integer, expected_message in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                validate_positive_integer(integer, 'test_field')
            assert expected_message in str(exc_info.value)
    
    def test_api_input_validation_integration(self):
        """测试API接口的输入验证集成"""
        
        # 测试交易记录API的输入验证
        invalid_trade_data = [
            # 无效股票代码
            {
                'stock_code': '00001',  # 5位数字
                'stock_name': '测试股票',
                'trade_type': 'buy',
                'price': 10.50,
                'quantity': 100,
                'reason': '技术突破'
            },
            # 无效价格
            {
                'stock_code': '000001',
                'stock_name': '测试股票',
                'trade_type': 'buy',
                'price': -10.50,  # 负数价格
                'quantity': 100,
                'reason': '技术突破'
            },
            # 无效数量
            {
                'stock_code': '000001',
                'stock_name': '测试股票',
                'trade_type': 'buy',
                'price': 10.50,
                'quantity': 0,  # 零数量
                'reason': '技术突破'
            },
            # 无效交易类型
            {
                'stock_code': '000001',
                'stock_name': '测试股票',
                'trade_type': 'hold',  # 无效类型
                'price': 10.50,
                'quantity': 100,
                'reason': '技术突破'
            }
        ]
        
        for invalid_data in invalid_trade_data:
            response = self.client.post(
                '/api/trades',
                data=json.dumps(invalid_data),
                content_type='application/json'
            )
            
            # 验证错误可能返回400（API级别验证）或500（模型级别验证）
            assert response.status_code in [400, 500]
            response_data = json.loads(response.data)
            assert not response_data['success']
            assert 'error' in response_data
            assert 'message' in response_data['error']
            # 验证错误信息中包含验证相关的内容
            assert any(keyword in response_data['error']['message'] for keyword in 
                      ['格式不正确', '必须大于0', '必须是buy或sell', '无效的交易类型'])
    
    def test_boundary_values_validation(self):
        """测试边界值验证"""
        
        # 测试价格边界值
        boundary_cases = [
            # 最小有效价格
            {'price': 0.01, 'should_pass': True},
            # 最大有效价格
            {'price': 9999.99, 'should_pass': True},
            # 超出上限
            {'price': 10000.00, 'should_pass': False},
            # 零价格
            {'price': 0.00, 'should_pass': False},
        ]
        
        for case in boundary_cases:
            if case['should_pass']:
                result = validate_price(case['price'])
                assert result == case['price']
            else:
                with pytest.raises(ValidationError):
                    validate_price(case['price'])
        
        # 测试数量边界值
        quantity_boundary_cases = [
            # 最小有效数量
            {'quantity': 1, 'should_pass': True},
            # 最大有效数量
            {'quantity': 999999, 'should_pass': True},
            # 超出上限
            {'quantity': 1000000, 'should_pass': False},
            # 零数量
            {'quantity': 0, 'should_pass': False},
        ]
        
        for case in quantity_boundary_cases:
            if case['should_pass']:
                result = validate_quantity(case['quantity'])
                assert result == case['quantity']
            else:
                with pytest.raises(ValidationError):
                    validate_quantity(case['quantity'])
    
    def test_special_characters_validation(self):
        """测试特殊字符输入验证"""
        
        # 测试包含特殊字符的股票代码
        special_char_codes = [
            '000001;',
            '000001\'',
            '000001"',
            '000001<script>',
            '000001--',
            '000001/*',
        ]
        
        for code in special_char_codes:
            with pytest.raises(ValidationError):
                validate_stock_code(code)
        
        # 测试包含特殊字符的价格
        special_char_prices = [
            '10.50;',
            '10.50\'',
            '10.50"',
            '10.50<script>',
            '10.50--',
            '10.50/*',
        ]
        
        for price in special_char_prices:
            with pytest.raises(ValidationError):
                validate_price(price)
    
    def test_unicode_and_emoji_validation(self):
        """测试Unicode字符和表情符号验证"""
        
        # 测试包含中文字符的股票代码（应该失败）
        unicode_codes = [
            '中文代码',
            '000001中',
            '🚀000001',
            '000001💰',
        ]
        
        for code in unicode_codes:
            with pytest.raises(ValidationError):
                validate_stock_code(code)
        
        # 测试包含Unicode字符的价格（应该失败）
        unicode_prices = [
            '十点五',
            '10.5元',
            '💰10.50',
            '10.50🚀',
        ]
        
        for price in unicode_prices:
            with pytest.raises(ValidationError):
                validate_price(price)
    
    def test_null_and_empty_validation(self):
        """测试空值和null值验证"""
        
        # 测试各种空值情况
        empty_values = [None, '', ' ', '\t', '\n', '   ']
        
        for empty_value in empty_values:
            # 股票代码不能为空
            with pytest.raises(ValidationError):
                validate_stock_code(empty_value)
            
            # 交易类型不能为空
            with pytest.raises(ValidationError):
                validate_trade_type(empty_value)
            
            # 日期不能为空
            with pytest.raises(ValidationError):
                validate_date(empty_value)
        
        # 测试None值对于可选字段的处理
        assert validate_ratio(None, 'test_ratio') is None
    
    def test_large_input_validation(self):
        """测试超长输入验证"""
        
        # 测试超长字符串
        very_long_string = 'a' * 10000
        
        # 股票代码应该拒绝超长输入
        with pytest.raises(ValidationError):
            validate_stock_code(very_long_string)
        
        # 测试超长数字字符串
        very_long_number = '1' * 1000
        
        with pytest.raises(ValidationError):
            validate_price(very_long_number)
        
        with pytest.raises(ValidationError):
            validate_quantity(very_long_number)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])