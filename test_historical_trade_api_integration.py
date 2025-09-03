#!/usr/bin/env python3
"""
历史交易记录API集成测试脚本
用于验证API的基本功能
"""
import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:5000/api"

def test_api_endpoints():
    """测试API端点"""
    print("=== 历史交易记录API集成测试 ===\n")
    
    # 1. 测试获取历史交易记录列表
    print("1. 测试获取历史交易记录列表...")
    try:
        response = requests.get(f"{BASE_URL}/historical-trades")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   成功: {data['success']}")
            print(f"   总数: {data['data']['total']}")
            print("   ✓ 获取历史交易记录列表成功")
        else:
            print(f"   ✗ 请求失败: {response.text}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
    
    print()
    
    # 2. 测试分页
    print("2. 测试分页功能...")
    try:
        response = requests.get(f"{BASE_URL}/historical-trades?page=1&per_page=5")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   当前页: {data['data'].get('current_page', 'N/A')}")
            print(f"   每页数量: {data['data'].get('per_page', 'N/A')}")
            print("   ✓ 分页功能正常")
        else:
            print(f"   ✗ 请求失败: {response.text}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
    
    print()
    
    # 3. 测试筛选
    print("3. 测试筛选功能...")
    try:
        response = requests.get(f"{BASE_URL}/historical-trades?is_profitable=true")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   盈利交易数: {data['data']['total']}")
            print("   ✓ 筛选功能正常")
        else:
            print(f"   ✗ 请求失败: {response.text}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
    
    print()
    
    # 4. 测试识别已完成交易
    print("4. 测试识别已完成交易...")
    try:
        response = requests.post(f"{BASE_URL}/historical-trades/identify")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   识别到的交易数: {data['data']['total_count']}")
            print("   ✓ 识别功能正常")
        else:
            print(f"   ✗ 请求失败: {response.text}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
    
    print()
    
    # 5. 测试获取统计信息
    print("5. 测试获取统计信息...")
    try:
        response = requests.get(f"{BASE_URL}/historical-trades/statistics")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            stats = data['data']
            print(f"   总交易数: {stats.get('total_trades', 0)}")
            print(f"   盈利交易数: {stats.get('profitable_trades', 0)}")
            print(f"   胜率: {stats.get('win_rate', 0)}%")
            print("   ✓ 统计功能正常")
        else:
            print(f"   ✗ 请求失败: {response.text}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
    
    print()
    
    # 6. 测试数据验证
    print("6. 测试数据验证...")
    try:
        test_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'buy_date': '2024-01-01T00:00:00',
            'sell_date': '2024-01-15T00:00:00',
            'holding_days': 14,
            'total_investment': 10000.00,
            'total_return': 1000.00,
            'return_rate': 0.10,
            'is_completed': True,
            'completion_date': '2024-01-15T00:00:00'
        }
        
        response = requests.post(f"{BASE_URL}/historical-trades/validate", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   验证结果: {'通过' if data['data']['is_valid'] else '失败'}")
            print("   ✓ 数据验证功能正常")
        else:
            print(f"   ✗ 请求失败: {response.text}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
    
    print()
    
    # 7. 测试参数验证
    print("7. 测试参数验证...")
    try:
        response = requests.get(f"{BASE_URL}/historical-trades?page=0")  # 无效页码
        print(f"   状态码: {response.status_code}")
        if response.status_code == 400:
            print("   ✓ 参数验证正常（正确拒绝无效参数）")
        else:
            print(f"   ✗ 参数验证异常: {response.text}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
    
    print()
    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_api_endpoints()