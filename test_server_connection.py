#!/usr/bin/env python3
"""
测试服务器连接
"""

import requests
import json

def test_server():
    """测试服务器连接"""
    base_url = "http://127.0.0.1:5000"
    
    try:
        # 测试基本连接
        print("测试服务器连接...")
        response = requests.get(f"{base_url}/")
        print(f"主页响应: {response.status_code}")
        
        # 测试API端点
        print("测试API端点...")
        response = requests.get(f"{base_url}/api/trades")
        print(f"API响应: {response.status_code}")
        print(f"响应内容: {response.text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"连接错误: {str(e)}")
        return False

if __name__ == "__main__":
    test_server()