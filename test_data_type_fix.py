#!/usr/bin/env python3
"""
测试数据类型修复
"""
import requests
import json

def test_create_trade():
    """测试创建交易记录"""
    url = "http://127.0.0.1:5001/api/trades"
    
    # 测试数据 - 模拟前端发送的数据（可能包含字符串类型的数值）
    test_data = {
        "stock_code": "000001",
        "stock_name": "平安银行",
        "trade_type": "buy",
        "price": "10.50",  # 字符串类型的价格
        "quantity": "1000",  # 字符串类型的数量
        "reason": "技术分析",
        "notes": "测试数据类型修复"
    }
    
    print("🧪 测试数据类型修复...")
    print(f"📤 发送数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"📥 响应状态码: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ 创建成功!")
            print(f"📋 响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print("❌ 创建失败!")
            print(f"📋 错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_stock_quantity_validation():
    """测试股票数量验证"""
    from utils.stock_utils import validate_stock_quantity
    
    print("\n🧪 测试股票数量验证...")
    
    # 测试用例
    test_cases = [
        ("000001", "1000", True),   # 字符串数量，普通股票
        ("000001", 1000, True),     # 整数数量，普通股票
        ("688001", "150", True),    # 字符串数量，科创板
        ("688001", 150, True),      # 整数数量，科创板
        ("000001", "150", False),   # 不是100倍数
        ("000001", "0", False),     # 零数量
        ("000001", "-100", False),  # 负数量
    ]
    
    for stock_code, quantity, expected in test_cases:
        try:
            is_valid, error_msg = validate_stock_quantity(stock_code, quantity)
            status = "✅" if is_valid == expected else "❌"
            print(f"{status} {stock_code} + {quantity} ({type(quantity).__name__}) -> {is_valid} (期望: {expected})")
            if not is_valid and error_msg:
                print(f"   错误信息: {error_msg}")
        except Exception as e:
            print(f"❌ {stock_code} + {quantity} -> 异常: {e}")

if __name__ == "__main__":
    print("🔧 数据类型修复测试")
    print("=" * 50)
    
    # 测试股票数量验证函数
    test_stock_quantity_validation()
    
    # 测试API创建交易记录
    test_create_trade()
    
    print("\n✨ 测试完成")