#!/usr/bin/env python3
"""
测试编辑交易记录修复验证
"""

import requests
import json
import sys
from datetime import datetime

def test_edit_trade_fix():
    """测试编辑交易记录修复"""
    base_url = "http://127.0.0.1:5001"
    
    print("=== 编辑交易记录修复验证测试 ===")
    
    try:
        # 1. 首先创建一个测试交易记录
        print("\n1. 创建测试交易记录...")
        create_data = {
            "stock_code": "000001",
            "stock_name": "平安银行",
            "trade_type": "buy",
            "price": 10.50,
            "quantity": 1000,
            "reason": "少妇B1战法",
            "trade_date": datetime.now().isoformat(),
            "notes": "测试记录"
        }
        
        response = requests.post(f"{base_url}/api/trades", json=create_data)
        if response.status_code != 201:
            print(f"创建交易记录失败: {response.status_code} - {response.text}")
            return False
        
        trade_data = response.json()
        if not trade_data.get('success'):
            print(f"创建交易记录失败: {trade_data.get('message')}")
            return False
        
        trade_id = trade_data['data']['id']
        print(f"✓ 创建交易记录成功，ID: {trade_id}")
        
        # 2. 测试正常编辑（包含所有必填字段）
        print("\n2. 测试正常编辑...")
        update_data = {
            "stock_code": "000001",
            "stock_name": "平安银行",
            "trade_type": "buy",
            "price": 11.00,
            "quantity": 1200,
            "reason": "少妇B1战法",
            "notes": "更新后的测试记录"
        }
        
        response = requests.put(f"{base_url}/api/trades/{trade_id}", json=update_data)
        if response.status_code != 200:
            print(f"正常编辑失败: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if not result.get('success'):
            print(f"正常编辑失败: {result.get('message')}")
            return False
        
        print("✓ 正常编辑成功")
        
        # 3. 测试包含None值的编辑（这应该被过滤掉）
        print("\n3. 测试包含None值的编辑...")
        update_data_with_none = {
            "stock_code": "000001",
            "stock_name": "平安银行",
            "trade_type": "buy",
            "price": None,  # 这应该被过滤掉
            "quantity": None,  # 这应该被过滤掉
            "reason": "少妇B1战法",
            "notes": "测试None值处理"
        }
        
        response = requests.put(f"{base_url}/api/trades/{trade_id}", json=update_data_with_none)
        if response.status_code == 400:
            print("✓ 正确拒绝了包含None值的请求")
        else:
            print(f"⚠ 意外的响应: {response.status_code} - {response.text}")
        
        # 4. 测试包含空字符串的编辑
        print("\n4. 测试包含空字符串的编辑...")
        update_data_with_empty = {
            "stock_code": "000001",
            "stock_name": "平安银行",
            "trade_type": "buy",
            "price": "",  # 空字符串
            "quantity": "",  # 空字符串
            "reason": "少妇B1战法",
            "notes": "测试空字符串处理"
        }
        
        response = requests.put(f"{base_url}/api/trades/{trade_id}", json=update_data_with_empty)
        if response.status_code == 400:
            print("✓ 正确拒绝了包含空字符串的请求")
        else:
            print(f"⚠ 意外的响应: {response.status_code} - {response.text}")
        
        # 5. 测试部分更新（只更新notes）
        print("\n5. 测试部分更新...")
        partial_update_data = {
            "notes": "只更新备注字段"
        }
        
        response = requests.put(f"{base_url}/api/trades/{trade_id}", json=partial_update_data)
        if response.status_code != 200:
            print(f"部分更新失败: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if not result.get('success'):
            print(f"部分更新失败: {result.get('message')}")
            return False
        
        print("✓ 部分更新成功")
        
        # 6. 验证记录仍然完整
        print("\n6. 验证记录完整性...")
        response = requests.get(f"{base_url}/api/trades/{trade_id}")
        if response.status_code != 200:
            print(f"获取记录失败: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if not result.get('success'):
            print(f"获取记录失败: {result.get('message')}")
            return False
        
        trade = result['data']
        if trade['price'] is None or trade['quantity'] is None:
            print(f"✗ 记录完整性验证失败: price={trade['price']}, quantity={trade['quantity']}")
            return False
        
        print(f"✓ 记录完整性验证通过: price={trade['price']}, quantity={trade['quantity']}")
        
        # 7. 清理测试数据
        print("\n7. 清理测试数据...")
        response = requests.delete(f"{base_url}/api/trades/{trade_id}")
        if response.status_code == 200:
            print("✓ 测试数据清理完成")
        else:
            print(f"⚠ 清理测试数据失败: {response.status_code}")
        
        print("\n=== 所有测试通过 ===")
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_edit_trade_fix()
    sys.exit(0 if success else 1)