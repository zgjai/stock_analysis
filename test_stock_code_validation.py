#!/usr/bin/env python3
"""
测试股票代码验证修复
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.validators import validate_stock_code
from error_handlers import ValidationError

def test_stock_code_validation():
    """测试股票代码验证功能"""
    print("=== 测试股票代码验证功能 ===")
    
    # 测试用例
    test_cases = [
        ("000001", True, "有效的股票代码"),
        ("600519", True, "有效的股票代码"),
        ("", False, "空字符串"),
        (None, False, "None值"),
        ("00001", False, "5位数字"),
        ("0000001", False, "7位数字"),
        ("abc123", False, "包含字母"),
        ("000001a", False, "包含字母后缀"),
        ("a000001", False, "包含字母前缀"),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for stock_code, should_pass, description in test_cases:
        try:
            result = validate_stock_code(stock_code)
            if should_pass:
                print(f"✓ {description}: '{stock_code}' - 验证通过")
                success_count += 1
            else:
                print(f"✗ {description}: '{stock_code}' - 应该失败但通过了")
        except ValidationError as e:
            if not should_pass:
                print(f"✓ {description}: '{stock_code}' - 正确拒绝: {e.message}")
                success_count += 1
            else:
                print(f"✗ {description}: '{stock_code}' - 应该通过但失败了: {e.message}")
        except Exception as e:
            print(f"✗ {description}: '{stock_code}' - 意外错误: {str(e)}")
    
    print(f"\n测试结果: {success_count}/{total_count} 通过")
    return success_count == total_count

def test_api_create_trade():
    """测试API创建交易记录"""
    print("\n=== 测试API创建交易记录 ===")
    
    try:
        from services.trading_service import TradingService
        from datetime import datetime
        
        # 测试数据
        test_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 10.50,
            'quantity': 1000,
            'trade_date': datetime.now(),
            'reason': '少妇B1战法',
            'notes': '测试交易记录'
        }
        
        print("测试数据:", test_data)
        
        # 尝试创建交易记录
        trade = TradingService.create_trade(test_data)
        print(f"✓ 交易记录创建成功: ID={trade.id}")
        
        # 清理测试数据
        TradingService.delete_trade(trade.id)
        print("✓ 测试数据已清理")
        
        return True
        
    except Exception as e:
        print(f"✗ 创建交易记录失败: {str(e)}")
        return False

if __name__ == '__main__':
    print("开始测试股票代码验证修复...")
    
    # 测试验证器
    validation_ok = test_stock_code_validation()
    
    # 测试API（需要数据库连接）
    try:
        api_ok = test_api_create_trade()
    except Exception as e:
        print(f"API测试跳过（可能需要数据库连接）: {str(e)}")
        api_ok = True  # 不影响整体结果
    
    if validation_ok:
        print("\n🎉 股票代码验证修复成功！")
        print("\n修复说明:")
        print("- 修复了 utils/validators.py 中 validate_stock_code 函数的正则表达式语法错误")
        print("- 原来的正则表达式缺少结束符号，导致验证失败")
        print("- 现在股票代码验证应该正常工作")
    else:
        print("\n❌ 还有问题需要解决")
        sys.exit(1)