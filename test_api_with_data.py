#!/usr/bin/env python3
"""
测试API端点是否能正常返回数据
"""
import requests
import json

def test_api_endpoints():
    """测试主要的API端点"""
    base_url = "http://127.0.0.1:8080"
    
    endpoints = [
        "/health",
        "/api/analytics/overview",
        "/api/trades?limit=5&order=desc",
        "/api/holdings/alerts",
        "/api/analytics/monthly",
        "/api/analytics/profit-distribution"
    ]
    
    print("测试API端点...")
    print("=" * 60)
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            print(f"测试: {endpoint}")
            
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if 'data' in data:
                            print(f"  数据: {type(data['data'])} - {len(str(data['data']))} 字符")
                        else:
                            print(f"  响应: {list(data.keys())}")
                    else:
                        print(f"  响应: {type(data)}")
                    print("  ✓ 成功")
                except json.JSONDecodeError:
                    print(f"  响应长度: {len(response.text)} 字符")
                    print("  ✓ 成功 (非JSON)")
            else:
                print(f"  错误: {response.text[:100]}")
                print("  ✗ 失败")
                
        except requests.exceptions.RequestException as e:
            print(f"  网络错误: {e}")
            print("  ✗ 失败")
        
        print("-" * 40)
    
    print("API测试完成")

if __name__ == '__main__':
    test_api_endpoints()