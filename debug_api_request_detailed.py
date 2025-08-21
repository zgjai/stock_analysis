#!/usr/bin/env python3
"""
详细的API请求调试工具
"""

import requests
import json
import logging
from datetime import datetime

# 设置详细日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_review_api():
    """测试复盘API"""
    
    # 测试数据
    test_data = {
        "stock_code": "000001",
        "review_date": "2025-01-21",
        "holding_days": 5,
        "current_price": 10.50,
        "floating_profit_ratio": None,
        "buy_price": None,
        "price_up_score": 1,
        "bbi_score": 1,
        "volume_score": 0,
        "trend_score": 1,
        "j_score": 0,
        "analysis": "测试分析内容",
        "decision": "hold",
        "reason": "测试决策理由"
    }
    
    print("=== 复盘API调试测试 ===")
    print(f"时间: {datetime.now()}")
    print(f"测试数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        # 发送POST请求
        url = "http://localhost:5001/api/reviews"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print(f"\n发送请求到: {url}")
        print(f"请求头: {json.dumps(headers, indent=2)}")
        
        response = requests.post(
            url, 
            json=test_data, 
            headers=headers,
            timeout=10
        )
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print(f"响应文本: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ 请求成功!")
        else:
            print("❌ 请求失败!")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

def test_validation_scenarios():
    """测试各种验证场景"""
    
    scenarios = [
        {
            "name": "正常数据",
            "data": {
                "stock_code": "000001",
                "review_date": "2025-01-21",
                "holding_days": 5,
                "current_price": 10.50,
                "decision": "hold",
                "reason": "测试理由",
                "analysis": "测试分析"
            }
        },
        {
            "name": "缺少股票代码",
            "data": {
                "review_date": "2025-01-21",
                "holding_days": 5,
                "decision": "hold",
                "reason": "测试理由"
            }
        },
        {
            "name": "缺少复盘日期",
            "data": {
                "stock_code": "000001",
                "holding_days": 5,
                "decision": "hold",
                "reason": "测试理由"
            }
        },
        {
            "name": "持仓天数为0",
            "data": {
                "stock_code": "000001",
                "review_date": "2025-01-21",
                "holding_days": 0,
                "decision": "hold",
                "reason": "测试理由"
            }
        },
        {
            "name": "空的决策理由",
            "data": {
                "stock_code": "000001",
                "review_date": "2025-01-21",
                "holding_days": 5,
                "decision": "hold",
                "reason": ""
            }
        }
    ]
    
    print("\n=== 验证场景测试 ===")
    
    for scenario in scenarios:
        print(f"\n--- 测试场景: {scenario['name']} ---")
        
        try:
            response = requests.post(
                "http://localhost:5001/api/reviews",
                json=scenario['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            
            try:
                response_data = response.json()
                if response.status_code >= 400:
                    error_msg = response_data.get('error', {}).get('message', '未知错误')
                    print(f"错误信息: {error_msg}")
                else:
                    print("✅ 请求成功")
            except json.JSONDecodeError:
                print(f"响应文本: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")

if __name__ == '__main__':
    print("开始API调试测试...")
    
    # 首先测试基本功能
    test_review_api()
    
    # 然后测试各种验证场景
    test_validation_scenarios()
    
    print("\n调试测试完成!")