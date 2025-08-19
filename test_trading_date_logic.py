#!/usr/bin/env python3
"""
测试交易日期逻辑
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import datetime, time
from utils.trading_date_utils import get_trading_date, get_data_context

def test_trading_date_logic():
    """测试交易日期逻辑"""
    
    print("=== 交易日期逻辑测试 ===\n")
    
    # 1. 测试当前时间的日期逻辑
    print("1. 当前时间日期逻辑:")
    context = get_data_context()
    trading_date = get_trading_date()
    
    print(f"当前时间: {context['current_datetime']}")
    print(f"当前日期: {context['current_date']}")
    print(f"交易日期: {trading_date}")
    print(f"是否早晨8点前: {context['is_early_morning']}")
    print(f"日期是否调整: {context['date_adjusted']}")
    print(f"调整原因: {context['adjustment_reason']}")
    
    # 2. 测试API调用
    print(f"\n2. 测试板块数据刷新API:")
    base_url = "http://localhost:5001"
    
    try:
        response = requests.post(f"{base_url}/api/sectors/refresh", timeout=30)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            data = result.get('data', {})
            print(f"\n✓ 刷新成功")
            print(f"  数据日期: {data.get('date')}")
            print(f"  交易日期: {data.get('trading_date')}")
            print(f"  当前日期: {data.get('current_date')}")
            print(f"  日期调整: {data.get('date_adjusted')}")
            print(f"  调整原因: {data.get('adjustment_reason')}")
            print(f"  数据条数: {data.get('count')}")
            
            # 验证日期逻辑
            if data.get('date_adjusted'):
                print(f"✓ 日期已正确调整: {data.get('current_date')} -> {data.get('trading_date')}")
            else:
                print(f"✓ 日期无需调整: {data.get('date')}")
                
        else:
            print(f"✗ 刷新失败: {result.get('error', {}).get('message', '未知错误')}")
            
    except Exception as e:
        print(f"✗ API调用失败: {e}")
    
    # 3. 验证数据存储
    print(f"\n3. 验证数据存储:")
    try:
        response = requests.get(f"{base_url}/api/sectors/ranking", timeout=10)
        result = response.json()
        
        if result.get('success'):
            ranking_data = result.get('data', [])
            print(f"✓ 获取到 {len(ranking_data)} 条排名数据")
            
            if ranking_data:
                first_record = ranking_data[0]
                stored_date = first_record.get('record_date')
                print(f"  存储的数据日期: {stored_date}")
                print(f"  预期的交易日期: {trading_date}")
                
                if stored_date == trading_date.isoformat():
                    print(f"✓ 数据日期正确")
                else:
                    print(f"⚠ 数据日期不匹配")
        else:
            print(f"✗ 获取排名失败")
            
    except Exception as e:
        print(f"✗ 验证失败: {e}")
    
    print(f"\n=== 测试完成 ===")
    
    # 4. 显示不同时间点的预期行为
    print(f"\n4. 不同时间点的预期行为:")
    test_scenarios = [
        ("周二早上7:30", "数据归属周一"),
        ("周二上午9:30", "数据归属周二"),
        ("周六任意时间", "数据归属周五"),
        ("周日任意时间", "数据归属周五"),
        ("周一早上7:30", "数据归属上周五"),
    ]
    
    for scenario, expected in test_scenarios:
        print(f"  {scenario}: {expected}")

if __name__ == "__main__":
    test_trading_date_logic()