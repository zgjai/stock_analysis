#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试月度期望收益API
"""

import requests
import json
from datetime import datetime

def test_monthly_expectations_api():
    """测试月度期望收益API"""
    base_url = "http://localhost:5001"
    
    print("=== 测试月度期望收益API ===")
    
    try:
        # 测试获取月度期望数据
        print("\n1. 测试获取月度期望数据...")
        response = requests.get(f"{base_url}/api/analytics/monthly-expectations")
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应成功: {result.get('success', False)}")
            print(f"消息: {result.get('message', '')}")
            
            if result.get('success'):
                data = result.get('data', [])
                print(f"数据条数: {len(data)}")
                
                if data:
                    print("\n前3条数据:")
                    for i, item in enumerate(data[:3]):
                        print(f"  {i+1}. {item['month']}: 期望收益 {item['expected_amount']:,.0f}元 ({item['expected_rate']}%)")
                        print(f"     月初本金: {item['start_capital']:,.0f}元, 月末本金: {item['end_capital']:,.0f}元")
            else:
                print(f"API返回失败: {result.get('message', '未知错误')}")
        else:
            print(f"HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试月度对比API
    print("\n2. 测试月度对比API...")
    
    try:
        # 测试当前月份
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        response = requests.get(f"{base_url}/api/analytics/monthly-comparison", 
                              params={'year': current_year, 'month': current_month})
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应成功: {result.get('success', False)}")
            print(f"消息: {result.get('message', '')}")
            
            if result.get('success'):
                data = result.get('data', {})
                print(f"对比月份: {data.get('month_str', '')}")
                
                expected = data.get('expected', {})
                actual = data.get('actual', {})
                comparison = data.get('comparison', {})
                
                print(f"\n期望数据:")
                print(f"  期望收益: {expected.get('expected_amount', 0):,.0f}元")
                print(f"  期望收益率: {expected.get('expected_rate', 0)}%")
                print(f"  月初本金: {expected.get('start_capital', 0):,.0f}元")
                
                print(f"\n实际数据:")
                print(f"  实际收益: {actual.get('realized_profit', 0):,.0f}元")
                print(f"  实际收益率: {actual.get('return_rate', 0)*100:.2f}%")
                print(f"  交易次数: {actual.get('total_trades', 0)}")
                
                print(f"\n对比结果:")
                print(f"  收益差异: {comparison.get('amount_diff', 0):,.0f}元 ({comparison.get('amount_diff_pct', 0):.1f}%)")
                print(f"  收益率差异: {comparison.get('rate_diff', 0)*100:.2f}% ({comparison.get('rate_diff_pct', 0):.1f}%)")
            else:
                print(f"API返回失败: {result.get('message', '未知错误')}")
        else:
            print(f"HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试2025年8月（起始月份）
    print("\n3. 测试2025年8月对比...")
    
    try:
        response = requests.get(f"{base_url}/api/analytics/monthly-comparison", 
                              params={'year': 2025, 'month': 8})
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应成功: {result.get('success', False)}")
            
            if result.get('success'):
                data = result.get('data', {})
                print(f"对比月份: {data.get('month_str', '')}")
                
                expected = data.get('expected', {})
                print(f"期望收益: {expected.get('expected_amount', 0):,.0f}元")
                print(f"月初本金: {expected.get('start_capital', 0):,.0f}元")
            else:
                print(f"API返回失败: {result.get('message', '未知错误')}")
        else:
            print(f"HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_monthly_expectations_api()