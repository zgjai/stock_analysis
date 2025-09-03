#!/usr/bin/env python3
"""
测试基本API端点
"""
import requests
import json

def test_basic_endpoints():
    """测试基本端点"""
    endpoints = [
        "http://localhost:5001/api/trades",
        "http://localhost:5001/api/analytics/overview",
        "http://localhost:5001/api/trades/current-holdings"
    ]
    
    for url in endpoints:
        try:
            print(f"\n测试: {url}")
            response = requests.get(url, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 成功")
                if 'data' in data:
                    if isinstance(data['data'], list):
                        print(f"返回 {len(data['data'])} 条记录")
                    elif isinstance(data['data'], dict):
                        print(f"返回数据字段: {list(data['data'].keys())}")
            else:
                print(f"❌ 错误: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")

if __name__ == "__main__":
    test_basic_endpoints()