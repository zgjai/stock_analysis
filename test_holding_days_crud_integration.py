#!/usr/bin/env python3
"""
持仓天数CRUD操作集成测试
测试完整的创建、读取、更新、删除流程
"""

import requests
import json
from datetime import date

# 配置
BASE_URL = "http://localhost:5000/api"
STOCK_CODE = "000001"

def test_holding_days_crud_workflow():
    """测试持仓天数完整CRUD工作流程"""
    
    print("=== 持仓天数CRUD集成测试 ===")
    
    # 1. 测试GET - 获取不存在的持仓天数
    print("\n1. 测试获取不存在的持仓天数...")
    response = requests.get(f"{BASE_URL}/holdings/{STOCK_CODE}/days")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['data']['holding_days'] is None
    
    # 2. 测试POST - 创建持仓天数
    print("\n2. 测试创建持仓天数...")
    create_data = {"holding_days": 10}
    response = requests.post(
        f"{BASE_URL}/holdings/{STOCK_CODE}/days",
        json=create_data,
        headers={'Content-Type': 'application/json'}
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 201
    assert data['data']['holding_days'] == 10
    
    # 3. 测试GET - 获取已创建的持仓天数
    print("\n3. 测试获取已创建的持仓天数...")
    response = requests.get(f"{BASE_URL}/holdings/{STOCK_CODE}/days")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['data']['holding_days'] == 10
    
    # 4. 测试PUT - 更新持仓天数
    print("\n4. 测试更新持仓天数...")
    update_data = {"holding_days": 15}
    response = requests.put(
        f"{BASE_URL}/holdings/{STOCK_CODE}/days",
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['data']['holding_days'] == 15
    
    # 5. 测试GET - 验证更新后的值
    print("\n5. 测试验证更新后的值...")
    response = requests.get(f"{BASE_URL}/holdings/{STOCK_CODE}/days")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['data']['holding_days'] == 15
    
    # 6. 测试DELETE - 删除持仓天数
    print("\n6. 测试删除持仓天数...")
    response = requests.delete(f"{BASE_URL}/holdings/{STOCK_CODE}/days")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    
    # 7. 测试验证删除后的状态
    print("\n7. 测试验证删除后的状态...")
    response = requests.get(f"{BASE_URL}/holdings/{STOCK_CODE}/days")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    # 删除后应该返回None（使用自动计算）
    assert data['data']['holding_days'] is None
    
    print("\n=== 所有测试通过！ ===")

def test_validation_errors():
    """测试数据验证错误"""
    
    print("\n=== 数据验证测试 ===")
    
    # 测试创建无效数据
    print("\n1. 测试创建负数持仓天数...")
    create_data = {"holding_days": -5}
    response = requests.post(
        f"{BASE_URL}/holdings/{STOCK_CODE}/days",
        json=create_data,
        headers={'Content-Type': 'application/json'}
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 400
    assert "持仓天数必须是正整数" in data['error']['message']
    
    # 测试创建零值
    print("\n2. 测试创建零值持仓天数...")
    create_data = {"holding_days": 0}
    response = requests.post(
        f"{BASE_URL}/holdings/{STOCK_CODE}/days",
        json=create_data,
        headers={'Content-Type': 'application/json'}
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 400
    assert "持仓天数必须是正整数" in data['error']['message']
    
    # 测试创建非数字值
    print("\n3. 测试创建非数字持仓天数...")
    create_data = {"holding_days": "invalid"}
    response = requests.post(
        f"{BASE_URL}/holdings/{STOCK_CODE}/days",
        json=create_data,
        headers={'Content-Type': 'application/json'}
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 400
    assert "持仓天数必须是正整数" in data['error']['message']
    
    print("\n=== 验证测试通过！ ===")

if __name__ == "__main__":
    try:
        test_holding_days_crud_workflow()
        test_validation_errors()
        print("\n🎉 所有集成测试通过！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()