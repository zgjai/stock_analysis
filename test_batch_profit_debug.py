#!/usr/bin/env python3
"""
测试分批止盈保存功能的调试脚本
"""
import requests
import json

def test_batch_profit_save():
    """测试分批止盈保存功能"""
    
    # 测试数据 - 模拟前端发送的分批止盈数据
    test_data = {
        "stock_code": "000001",
        "stock_name": "平安银行",
        "trade_type": "buy",
        "price": 10.50,
        "quantity": 1000,
        "trade_date": "2025-01-15T10:30:00",
        "reason": "技术分析",
        "notes": "测试分批止盈功能",
        "stop_loss_price": 9.50,
        "use_batch_profit_taking": True,
        "profit_targets": [
            {
                "target_price": 11.55,
                "profit_ratio": 0.10,
                "sell_ratio": 0.30,
                "notes": "第一批止盈"
            },
            {
                "target_price": 12.60,
                "profit_ratio": 0.20,
                "sell_ratio": 0.40,
                "notes": "第二批止盈"
            },
            {
                "target_price": 13.65,
                "profit_ratio": 0.30,
                "sell_ratio": 0.30,
                "notes": "第三批止盈"
            }
        ]
    }
    
    print("=== 测试分批止盈保存功能 ===")
    print(f"发送数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        # 发送POST请求到/api/trades
        url = "http://localhost:5001/api/trades"
        headers = {
            'Content-Type': 'application/json'
        }
        
        print(f"\n发送请求到: {url}")
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ 请求成功")
            response_data = response.json()
            print(f"响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        else:
            print("❌ 请求失败")
            print(f"响应内容: {response.text}")
            
            # 尝试解析JSON错误信息
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("无法解析错误响应为JSON")
    
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保服务器在端口5001上运行")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    test_batch_profit_save()