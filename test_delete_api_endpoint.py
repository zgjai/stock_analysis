#!/usr/bin/env python3
"""
测试删除交易记录API端点
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import date


def test_delete_api():
    """测试删除交易记录API"""
    base_url = 'http://localhost:5000'
    
    try:
        print("1. 创建测试交易记录...")
        
        # 创建交易记录
        trade_data = {
            'stock_code': '000002',
            'stock_name': '万科A',
            'trade_type': 'buy',
            'price': 15.50,
            'quantity': 500,
            'trade_date': date.today().isoformat(),
            'reason': 'API测试',
            'notes': '测试删除API功能'
        }
        
        response = requests.post(f'{base_url}/api/trades', json=trade_data)
        
        if response.status_code != 201:
            print(f"创建交易记录失败: {response.status_code} - {response.text}")
            return False
        
        trade_result = response.json()
        trade_id = trade_result['data']['id']
        print(f"创建的交易记录ID: {trade_id}")
        
        # 创建止盈目标
        profit_data = {
            'trade_record_id': trade_id,
            'targets': [
                {
                    'target_price': 18.00,
                    'profit_ratio': 0.1613,  # (18.00 - 15.50) / 15.50
                    'sell_ratio': 0.3,
                    'sequence_order': 1
                },
                {
                    'target_price': 20.00,
                    'profit_ratio': 0.2903,  # (20.00 - 15.50) / 15.50
                    'sell_ratio': 0.7,
                    'sequence_order': 2
                }
            ]
        }
        
        response = requests.post(f'{base_url}/api/profit-targets', json=profit_data)
        
        if response.status_code == 201:
            print("创建了止盈目标")
        else:
            print(f"创建止盈目标失败: {response.status_code} - {response.text}")
        
        print("\n2. 验证记录存在...")
        
        # 验证交易记录存在
        response = requests.get(f'{base_url}/api/trades/{trade_id}')
        if response.status_code == 200:
            print("交易记录存在")
        else:
            print(f"获取交易记录失败: {response.status_code}")
            return False
        
        # 验证止盈目标存在
        response = requests.get(f'{base_url}/api/profit-targets/{trade_id}')
        if response.status_code == 200:
            targets = response.json().get('data', [])
            print(f"止盈目标数量: {len(targets)}")
        else:
            print(f"获取止盈目标失败: {response.status_code}")
        
        print("\n3. 测试删除功能...")
        
        # 删除交易记录
        response = requests.delete(f'{base_url}/api/trades/{trade_id}')
        
        if response.status_code == 200:
            print("删除请求成功")
        else:
            print(f"删除请求失败: {response.status_code} - {response.text}")
            return False
        
        print("\n4. 验证删除结果...")
        
        # 验证交易记录已删除
        response = requests.get(f'{base_url}/api/trades/{trade_id}')
        if response.status_code == 404:
            print("交易记录已删除")
        else:
            print(f"交易记录仍然存在: {response.status_code}")
            return False
        
        # 验证止盈目标已删除
        response = requests.get(f'{base_url}/api/profit-targets/{trade_id}')
        if response.status_code == 200:
            targets = response.json().get('data', [])
            if len(targets) == 0:
                print("止盈目标已删除")
            else:
                print(f"仍有 {len(targets)} 个止盈目标存在")
                return False
        else:
            print("止盈目标已删除（API返回错误，这是正常的）")
        
        print("\n✓ 删除交易记录API测试成功")
        return True
        
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        return False


if __name__ == '__main__':
    success = test_delete_api()
    if not success:
        sys.exit(1)