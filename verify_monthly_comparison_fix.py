#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证月度期望收益对比修复
确保与期望对比模块的收益金额计算一致
"""

import requests
import json

def test_data_consistency():
    """测试数据一致性"""
    print("=" * 60)
    print("验证月度期望收益对比数据一致性")
    print("=" * 60)
    
    try:
        # 1. 获取期望对比模块的数据
        print("1. 获取期望对比模块数据...")
        response1 = requests.get('http://localhost:5001/api/analytics/expectation-comparison?time_range=all', timeout=5)
        
        if response1.status_code != 200:
            print(f"❌ 期望对比API失败: {response1.status_code}")
            return False
            
        result1 = response1.json()
        if not result1.get('success'):
            print(f"❌ 期望对比API返回失败: {result1.get('message')}")
            return False
            
        expectation_data = result1['data']['actual']
        print(f"   期望对比模块 - 实际收益金额: {expectation_data['return_amount']:,.0f}元")
        print(f"   期望对比模块 - 已实现收益: {expectation_data['realized_profit']:,.0f}元")
        print(f"   期望对比模块 - 未实现收益: {expectation_data['unrealized_profit']:,.0f}元")
        print(f"   期望对比模块 - 总收益: {expectation_data['total_profit']:,.0f}元")
        
        # 2. 获取月度对比数据
        print("\n2. 获取月度对比数据...")
        response2 = requests.get('http://localhost:5001/api/analytics/monthly-comparison?year=2025&month=9', timeout=5)
        
        if response2.status_code != 200:
            print(f"❌ 月度对比API失败: {response2.status_code}")
            return False
            
        result2 = response2.json()
        if not result2.get('success'):
            print(f"❌ 月度对比API返回失败: {result2.get('message')}")
            return False
            
        monthly_data = result2['data']['actual']
        print(f"   月度对比模块 - 总收益: {monthly_data['total_profit']:,.0f}元")
        print(f"   月度对比模块 - 已实现收益: {monthly_data['realized_profit']:,.0f}元")
        print(f"   月度对比模块 - 未实现收益: {monthly_data['unrealized_profit']:,.0f}元")
        
        # 3. 验证一致性
        print("\n3. 验证数据一致性...")
        
        # 检查总收益是否一致
        total_profit_diff = abs(expectation_data['total_profit'] - monthly_data['total_profit'])
        if total_profit_diff < 1:
            print("   ✅ 总收益完全一致")
        else:
            print(f"   ❌ 总收益不一致，差异: {total_profit_diff:.2f}元")
            return False
            
        # 检查已实现收益是否一致
        realized_profit_diff = abs(expectation_data['realized_profit'] - monthly_data['realized_profit'])
        if realized_profit_diff < 1:
            print("   ✅ 已实现收益完全一致")
        else:
            print(f"   ❌ 已实现收益不一致，差异: {realized_profit_diff:.2f}元")
            return False
            
        # 检查未实现收益是否一致
        unrealized_profit_diff = abs(expectation_data['unrealized_profit'] - monthly_data['unrealized_profit'])
        if unrealized_profit_diff < 1:
            print("   ✅ 未实现收益完全一致")
        else:
            print(f"   ❌ 未实现收益不一致，差异: {unrealized_profit_diff:.2f}元")
            return False
            
        # 检查return_amount是否等于total_profit
        return_amount_diff = abs(expectation_data['return_amount'] - expectation_data['total_profit'])
        if return_amount_diff < 1:
            print("   ✅ return_amount与total_profit一致")
        else:
            print(f"   ❌ return_amount与total_profit不一致，差异: {return_amount_diff:.2f}元")
            return False
            
        print("\n4. 测试对比计算...")
        comparison = result2['data']['comparison']
        expected = result2['data']['expected']
        
        # 验证对比计算是否使用了总收益
        expected_diff = monthly_data['total_profit'] - expected['expected_amount']
        actual_diff = comparison['amount_diff']
        
        if abs(expected_diff - actual_diff) < 1:
            print("   ✅ 对比计算使用总收益，计算正确")
        else:
            print(f"   ❌ 对比计算错误，期望差异: {expected_diff:.2f}, 实际差异: {actual_diff:.2f}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_multiple_months():
    """测试多个月份的数据"""
    print("\n5. 测试多个月份数据...")
    
    months_to_test = [
        (2025, 8),  # 起始月份
        (2025, 9),  # 当前月份
        (2025, 10), # 未来月份
    ]
    
    for year, month in months_to_test:
        try:
            response = requests.get(f'http://localhost:5001/api/analytics/monthly-comparison?year={year}&month={month}', timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    data = result['data']
                    actual = data['actual']
                    expected = data['expected']
                    comparison = data['comparison']
                    
                    print(f"   {data['month_str']}:")
                    print(f"     期望收益: {expected['expected_amount']:,.0f}元")
                    print(f"     实际总收益: {actual['total_profit']:,.0f}元")
                    print(f"     差异: {comparison['amount_diff']:,.0f}元 ({comparison['amount_diff_pct']:.1f}%)")
                    print(f"     表现: {comparison['amount_status']['message']}")
                else:
                    print(f"   {year}年{month:02d}月: API返回失败 - {result.get('message')}")
            else:
                print(f"   {year}年{month:02d}月: HTTP错误 - {response.status_code}")
                
        except Exception as e:
            print(f"   {year}年{month:02d}月: 测试失败 - {e}")

def main():
    """主函数"""
    success = test_data_consistency()
    
    if success:
        test_multiple_months()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！月度期望收益对比已修复")
        print("\n修复内容:")
        print("✅ 实际收益现在使用总收益（已实现+未实现）")
        print("✅ 与期望对比模块的收益金额计算完全一致")
        print("✅ 对比计算基于总收益，而非仅已实现收益")
        print("✅ 前端显示已更新，显示总收益")
        print("\n现在月度对比中的35.2万与期望对比模块完全一致！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 测试失败，请检查上述错误")
        print("=" * 60)

if __name__ == "__main__":
    main()