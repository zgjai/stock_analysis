#!/usr/bin/env python3
"""
简单的API测试
"""
import requests
import json
import time

def test_api():
    """测试API端点"""
    url = "http://localhost:5001/api/trades/current-holdings"
    
    try:
        print(f"正在测试: {url}")
        response = requests.get(url, timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API调用成功")
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    test_api()