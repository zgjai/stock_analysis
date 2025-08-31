#!/usr/bin/env python3
"""
测试API类型转换修复
"""
import requests
import json
from datetime import datetime

def test_api_type_conversion():
    """测试API类型转换修复"""
    base_url = "http://127.0.0.1:5001"
    
    # 测试数据 - 模拟前端发送的字符串类型数据
    test_data = {
        'stock_code': '000001',
        'stock_name': '平安银行',
        'trade_type': 'buy',
        'price': '10.50',  # 字符串类型
        'quantity': '1000',
        'trade_date': datetime.now().strftime('%Y-%m-%d'),
        'reason': '少妇B1战法',
        'stop_loss_price': '9.50',  # 字符串类型
        'take_profit_ratio': '0.15',
        'sell_ratio': '1.0'
    }
    
    print("=== 测试API类型转换修复 ===")
    print(f"测试数据: {test_data}")
    
    try:
        # 发送POST请求创建交易记录
        response = requests.post(
            f"{base_url}/api/trades",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ 交易记录创建成功！")
            print(f"创建的记录ID: {result.get('data', {}).get('id')}")
            return True
        else:
            print(f"❌ API调用失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == '__main__':
    success = test_api_type_conversion()
    if success:
        print("\n🎉 API类型转换修复测试通过！")
    else:
        print("\n💥 API类型转换修复测试失败！")