#!/usr/bin/env python3
"""
测试交易录入工作流程的新功能
"""
import requests
import json

BASE_URL = "http://localhost:5001/api"

def test_current_holdings_endpoint():
    """测试当前持仓API端点"""
    print("测试当前持仓API端点...")
    
    try:
        response = requests.get(f"{BASE_URL}/trades/current-holdings")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('success'):
                holdings = data.get('data', {}).get('holdings', [])
                print(f"✅ 成功获取 {len(holdings)} 个持仓股票")
                
                for holding in holdings[:3]:  # 显示前3个
                    print(f"  - {holding['stock_code']} {holding['stock_name']}: {holding['quantity']}股")
            else:
                print(f"❌ API返回失败: {data.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_trade_creation_workflow():
    """测试交易创建工作流程"""
    print("\n测试交易创建工作流程...")
    
    # 测试买入交易
    buy_trade_data = {
        "stock_code": "000001",
        "stock_name": "平安银行",
        "trade_type": "buy",
        "price": 10.50,
        "quantity": 100,
        "reason": "少妇B1战法",
        "trade_date": "2024-01-15T10:30:00"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/trades",
            json=buy_trade_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"买入交易创建状态码: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ 买入交易创建成功")
            trade_id = data.get('data', {}).get('id')
            print(f"交易ID: {trade_id}")
        else:
            print(f"❌ 买入交易创建失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 买入交易创建请求失败: {e}")

if __name__ == "__main__":
    print("=== 交易录入工作流程测试 ===")
    test_current_holdings_endpoint()
    test_trade_creation_workflow()
    print("\n测试完成")