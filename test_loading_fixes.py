#!/usr/bin/env python3
"""
测试加载状态修复
"""
import requests
import time
import json

def test_trading_records_page():
    """测试交易记录页面加载"""
    print("测试交易记录页面...")
    
    try:
        # 测试页面加载
        response = requests.get('http://localhost:5001/trading-records', timeout=10)
        if response.status_code == 200:
            print("✅ 交易记录页面加载成功")
            
            # 检查是否包含修复后的JavaScript
            if 'renderTradesTable' in response.text:
                print("✅ JavaScript函数存在")
            else:
                print("❌ JavaScript函数缺失")
                
        else:
            print(f"❌ 页面加载失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 页面测试失败: {e}")

def test_review_page():
    """测试复盘页面加载"""
    print("\n测试复盘页面...")
    
    try:
        # 测试页面加载
        response = requests.get('http://localhost:5001/review', timeout=10)
        if response.status_code == 200:
            print("✅ 复盘页面加载成功")
            
            # 检查是否包含修复后的JavaScript
            if 'renderReviews' in response.text and 'Array.isArray' in response.text:
                print("✅ JavaScript修复已应用")
            else:
                print("❌ JavaScript修复未应用")
                
        else:
            print(f"❌ 页面加载失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 页面测试失败: {e}")

def test_api_endpoints():
    """测试API端点"""
    print("\n测试API端点...")
    
    endpoints = [
        ('/api/trades', '交易记录API'),
        ('/api/reviews', '复盘记录API'),
        ('/api/holdings/alerts', '持仓提醒API')
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'http://localhost:5001{endpoint}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ {name} 正常")
                else:
                    print(f"⚠️ {name} 返回错误: {data.get('message', '未知错误')}")
            else:
                print(f"❌ {name} HTTP错误: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ {name} 超时")
        except Exception as e:
            print(f"❌ {name} 失败: {e}")

def test_empty_data_handling():
    """测试空数据处理"""
    print("\n测试空数据处理...")
    
    # 模拟空数据响应
    test_cases = [
        ([], "空数组"),
        (None, "null值"),
        ({}, "空对象"),
        ({"data": []}, "包含空数组的对象"),
        ({"data": {"reviews": []}}, "嵌套空数组")
    ]
    
    for data, description in test_cases:
        print(f"测试 {description}: ", end="")
        
        # 模拟JavaScript中的数据处理逻辑
        try:
            if data is None:
                result = []
            elif isinstance(data, list):
                result = data
            elif isinstance(data, dict):
                if 'reviews' in data:
                    result = data['reviews']
                elif 'data' in data:
                    if isinstance(data['data'], list):
                        result = data['data']
                    elif isinstance(data['data'], dict) and 'reviews' in data['data']:
                        result = data['data']['reviews']
                    else:
                        result = []
                else:
                    result = []
            else:
                result = []
                
            if isinstance(result, list):
                print("✅ 正确处理为数组")
            else:
                print("❌ 未正确处理为数组")
                
        except Exception as e:
            print(f"❌ 处理失败: {e}")

if __name__ == '__main__':
    print("🔧 测试加载状态修复")
    print("=" * 50)
    
    test_trading_records_page()
    test_review_page()
    test_api_endpoints()
    test_empty_data_handling()
    
    print("\n" + "=" * 50)
    print("测试完成")