#!/usr/bin/env python3
"""
调试API请求问题
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from app import create_app
from extensions import db
from models.trade_record import TradeRecord

def test_api_requests():
    """测试API请求"""
    
    # 启动应用
    app = create_app()
    
    with app.app_context():
        # 获取一个测试记录
        trade = TradeRecord.query.first()
        if not trade:
            print("没有找到测试记录")
            return
        
        print(f"测试交易记录 ID: {trade.id}")
        print(f"当前数据: {trade.to_dict()}")
    
    # 测试API请求
    base_url = 'http://localhost:5000'
    
    # 测试GET请求
    print("\n=== 测试GET请求 ===")
    try:
        response = requests.get(f'{base_url}/api/trades/{trade.id}', timeout=5)
        print(f"GET状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"GET响应: {response.json()}")
        else:
            print(f"GET错误: {response.text}")
    except Exception as e:
        print(f"GET请求失败: {str(e)}")
    
    # 测试PUT请求 - 模拟前端数据
    print("\n=== 测试PUT请求 ===")
    
    # 模拟前端可能发送的各种数据格式
    test_cases = [
        {
            'name': '正常更新',
            'data': {
                'price': 15.50,
                'quantity': 1200,
                'notes': 'API测试更新'
            }
        },
        {
            'name': '字符串数字',
            'data': {
                'price': '15.50',
                'quantity': '1200',
                'notes': 'API测试更新'
            }
        },
        {
            'name': '包含空值',
            'data': {
                'price': 15.50,
                'quantity': 1200,
                'notes': 'API测试更新',
                'stop_loss_price': None,
                'take_profit_ratio': None
            }
        },
        {
            'name': '包含空字符串',
            'data': {
                'price': 15.50,
                'quantity': 1200,
                'notes': 'API测试更新',
                'stop_loss_price': '',
                'take_profit_ratio': ''
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        try:
            response = requests.put(
                f'{base_url}/api/trades/{trade.id}',
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            print(f"PUT状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"PUT成功: {response.json()}")
            else:
                print(f"PUT错误: {response.text}")
                try:
                    error_json = response.json()
                    print(f"错误详情: {json.dumps(error_json, indent=2, ensure_ascii=False)}")
                except:
                    pass
        except Exception as e:
            print(f"PUT请求失败: {str(e)}")

if __name__ == '__main__':
    test_api_requests()