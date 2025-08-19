#!/usr/bin/env python3
"""
测试编辑交易记录价格修复
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5001/api'

def test_create_trade():
    """测试创建交易记录"""
    print("=== 测试创建交易记录 ===")
    
    data = {
        'stock_code': '000001',
        'stock_name': '测试股票',
        'trade_type': 'buy',
        'price': 12.50,
        'quantity': 1000,
        'reason': '少妇B1战法',
        'trade_date': datetime.now().isoformat()
    }
    
    try:
        response = requests.post(f'{BASE_URL}/trades', json=data)
        result = response.json()
        
        if response.status_code == 201 and result.get('success'):
            trade_id = result['data']['id']
            print(f"✅ 创建成功，交易ID: {trade_id}")
            return trade_id
        else:
            print(f"❌ 创建失败: {result.get('error', {}).get('message', '未知错误')}")
            return None
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return None

def test_update_trade_normal(trade_id):
    """测试正常更新价格"""
    print(f"\n=== 测试正常更新价格 (ID: {trade_id}) ===")
    
    data = {
        'price': 13.75,
        'quantity': 1200
    }
    
    try:
        response = requests.put(f'{BASE_URL}/trades/{trade_id}', json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print(f"✅ 更新成功，新价格: {result['data']['price']}")
            return True
        else:
            print(f"❌ 更新失败: {result.get('error', {}).get('message', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

def test_update_trade_empty_price(trade_id):
    """测试空价格更新（应该失败）"""
    print(f"\n=== 测试空价格更新 (ID: {trade_id}) ===")
    
    data = {
        'price': '',
        'stock_name': '更新后的股票名称'
    }
    
    try:
        response = requests.put(f'{BASE_URL}/trades/{trade_id}', json=data)
        result = response.json()
        
        if response.status_code != 200:
            error_msg = result.get('error', {}).get('message', '未知错误')
            if '价格不能为空' in error_msg or 'price' in error_msg.lower():
                print(f"✅ 正确拒绝空价格: {error_msg}")
                return True
            else:
                print(f"❌ 错误信息不正确: {error_msg}")
                return False
        else:
            print(f"❌ 应该失败但成功了")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_update_trade_partial(trade_id):
    """测试部分字段更新（不包含价格）"""
    print(f"\n=== 测试部分字段更新 (ID: {trade_id}) ===")
    
    data = {
        'stock_name': '部分更新的股票名称',
        'reason': '少妇B2战法'
    }
    
    try:
        response = requests.put(f'{BASE_URL}/trades/{trade_id}', json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print(f"✅ 部分更新成功")
            return True
        else:
            print(f"❌ 部分更新失败: {result.get('error', {}).get('message', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 部分更新失败: {e}")
        return False

def test_update_trade_string_price(trade_id):
    """测试字符串价格更新"""
    print(f"\n=== 测试字符串价格更新 (ID: {trade_id}) ===")
    
    data = {
        'price': '15.25'  # 字符串格式
    }
    
    try:
        response = requests.put(f'{BASE_URL}/trades/{trade_id}', json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print(f"✅ 字符串价格转换成功，新价格: {result['data']['price']}")
            return True
        else:
            print(f"❌ 字符串价格更新失败: {result.get('error', {}).get('message', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 字符串价格更新失败: {e}")
        return False

def test_update_trade_zero_price(trade_id):
    """测试零价格更新（应该失败）"""
    print(f"\n=== 测试零价格更新 (ID: {trade_id}) ===")
    
    data = {
        'price': 0
    }
    
    try:
        response = requests.put(f'{BASE_URL}/trades/{trade_id}', json=data)
        result = response.json()
        
        if response.status_code != 200:
            error_msg = result.get('error', {}).get('message', '未知错误')
            if '必须大于0' in error_msg:
                print(f"✅ 正确拒绝零价格: {error_msg}")
                return True
            else:
                print(f"❌ 错误信息不正确: {error_msg}")
                return False
        else:
            print(f"❌ 应该失败但成功了")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def cleanup_test_data(trade_id):
    """清理测试数据"""
    print(f"\n=== 清理测试数据 (ID: {trade_id}) ===")
    
    try:
        response = requests.delete(f'{BASE_URL}/trades/{trade_id}')
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print(f"✅ 测试数据清理成功")
            return True
        else:
            print(f"❌ 清理失败: {result.get('error', {}).get('message', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试编辑交易记录价格修复")
    print("=" * 50)
    
    # 测试结果统计
    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }
    
    def record_result(test_name, success):
        results['total'] += 1
        if success:
            results['passed'] += 1
        else:
            results['failed'] += 1
        print(f"测试 '{test_name}': {'通过' if success else '失败'}")
    
    # 1. 创建测试交易记录
    trade_id = test_create_trade()
    if not trade_id:
        print("❌ 无法创建测试数据，终止测试")
        return
    
    # 2. 测试各种更新场景
    record_result("正常更新价格", test_update_trade_normal(trade_id))
    record_result("空价格更新", test_update_trade_empty_price(trade_id))
    record_result("部分字段更新", test_update_trade_partial(trade_id))
    record_result("字符串价格更新", test_update_trade_string_price(trade_id))
    record_result("零价格更新", test_update_trade_zero_price(trade_id))
    
    # 3. 清理测试数据
    cleanup_test_data(trade_id)
    
    # 4. 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"总测试数: {results['total']}")
    print(f"通过: {results['passed']}")
    print(f"失败: {results['failed']}")
    print(f"成功率: {results['passed']/results['total']*100:.1f}%")
    
    if results['failed'] == 0:
        print("🎉 所有测试通过！价格验证修复成功！")
    else:
        print("⚠️ 部分测试失败，需要进一步检查")

if __name__ == '__main__':
    main()