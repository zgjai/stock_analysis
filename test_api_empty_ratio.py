#!/usr/bin/env python3
"""
测试API处理空的 take_profit_ratio 字段
"""

import requests
import json

def test_empty_ratio_api():
    """测试API处理空比例字段"""
    
    base_url = "http://localhost:5000/api"
    
    test_cases = [
        {
            'name': '空字符串测试',
            'data': {
                "stock_code": "000001",
                "stock_name": "平安银行",
                "trade_type": "buy",
                "price": 10.50,
                "quantity": 200,
                "reason": "少妇B1战法",
                "take_profit_ratio": "",  # 空字符串
                "sell_ratio": "",         # 空字符串
                "stop_loss_price": ""     # 空字符串
            }
        },
        {
            'name': 'null值测试',
            'data': {
                "stock_code": "000001",
                "stock_name": "平安银行",
                "trade_type": "buy",
                "price": 10.50,
                "quantity": 200,
                "reason": "少妇B1战法",
                "take_profit_ratio": None,  # null
                "sell_ratio": None,         # null
                "stop_loss_price": None     # null
            }
        },
        {
            'name': '有效值测试',
            'data': {
                "stock_code": "000001",
                "stock_name": "平安银行",
                "trade_type": "buy",
                "price": 10.50,
                "quantity": 200,
                "reason": "少妇B1战法",
                "take_profit_ratio": "10",  # 有效值
                "sell_ratio": "50",         # 有效值
                "stop_loss_price": "9.50"   # 有效值
            }
        }
    ]
    
    print("=== 测试API处理空比例字段 ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试 {i}: {test_case['name']}")
        print(f"发送数据: {json.dumps(test_case['data'], indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(
                f"{base_url}/trades",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            
            try:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if response.status_code == 201:
                    print("✅ 成功创建交易记录")
                else:
                    print(f"❌ 创建失败: {result.get('message', '未知错误')}")
                    
            except json.JSONDecodeError:
                print(f"❌ 响应不是有效的JSON: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
        
        print("-" * 60)

if __name__ == '__main__':
    test_empty_ratio_api()