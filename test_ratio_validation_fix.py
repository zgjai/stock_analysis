#!/usr/bin/env python3
"""
测试 take_profit_ratio 验证修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.validators import validate_ratio
from error_handlers import ValidationError

def test_validate_ratio():
    """测试 validate_ratio 函数的各种输入情况"""
    
    print("=== 测试 validate_ratio 函数 ===\n")
    
    test_cases = [
        # (输入值, 字段名, 期望结果, 描述)
        (None, 'test_field', None, "None 值"),
        ('', 'test_field', None, "空字符串"),
        ('  ', 'test_field', None, "空白字符串"),
        ('0.1', 'test_field', 0.1, "有效小数"),
        ('10', 'test_field', 0.1, "百分比转换"),
        ('50', 'test_field', 0.5, "百分比转换"),
        ('100', 'test_field', 1.0, "100% 转换"),
        ('0', 'test_field', 0.0, "零值"),
        ('abc', 'test_field', 'ValidationError', "无效字符串"),
        ('150', 'test_field', 'ValidationError', "超过100的值"),
        ('-10', 'test_field', 'ValidationError', "负值"),
        (0.5, 'test_field', 0.5, "数值类型"),
        (50, 'test_field', 0.5, "整数类型"),
    ]
    
    for i, (input_value, field_name, expected, description) in enumerate(test_cases, 1):
        print(f"测试 {i}: {description}")
        print(f"输入: {repr(input_value)} (类型: {type(input_value).__name__})")
        
        try:
            result = validate_ratio(input_value, field_name)
            print(f"结果: {repr(result)} (类型: {type(result).__name__})")
            
            if expected == 'ValidationError':
                print("❌ 期望抛出 ValidationError，但没有抛出")
            elif result == expected:
                print("✅ 通过")
            else:
                print(f"❌ 期望: {repr(expected)}，实际: {repr(result)}")
                
        except ValidationError as e:
            if expected == 'ValidationError':
                print(f"✅ 正确抛出 ValidationError: {e.message}")
            else:
                print(f"❌ 意外的 ValidationError: {e.message}")
        except Exception as e:
            print(f"❌ 意外的异常: {type(e).__name__}: {e}")
        
        print("-" * 50)

def test_trade_record_creation():
    """测试交易记录创建时的验证"""
    
    print("\n=== 测试交易记录创建 ===\n")
    
    from models.trade_record import TradeRecord
    from datetime import datetime
    
    test_cases = [
        {
            'description': '空字符串 take_profit_ratio',
            'data': {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 10.50,
                'quantity': 200,
                'trade_date': datetime.now(),
                'reason': '测试',
                'take_profit_ratio': '',  # 空字符串
                'sell_ratio': '',         # 空字符串
            }
        },
        {
            'description': 'None take_profit_ratio',
            'data': {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 10.50,
                'quantity': 200,
                'trade_date': datetime.now(),
                'reason': '测试',
                'take_profit_ratio': None,
                'sell_ratio': None,
            }
        },
        {
            'description': '有效的 take_profit_ratio',
            'data': {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 10.50,
                'quantity': 200,
                'trade_date': datetime.now(),
                'reason': '测试',
                'take_profit_ratio': '10',  # 有效值
                'sell_ratio': '50',         # 有效值
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试 {i}: {test_case['description']}")
        print(f"数据: {test_case['data']}")
        
        try:
            # 只验证数据，不实际创建记录
            trade = TradeRecord(**test_case['data'])
            print("✅ 验证通过")
            print(f"take_profit_ratio: {trade.take_profit_ratio}")
            print(f"sell_ratio: {trade.sell_ratio}")
        except ValidationError as e:
            print(f"❌ ValidationError: {e.message}")
        except Exception as e:
            print(f"❌ 其他异常: {type(e).__name__}: {e}")
        
        print("-" * 50)

if __name__ == '__main__':
    test_validate_ratio()
    test_trade_record_creation()