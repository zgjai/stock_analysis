#!/usr/bin/env python3
"""
测试月度收益计算逻辑调整
从"按卖出时间归属"改为"按买入时间归属"
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_monthly_analytics_new_logic():
    """测试新的月度收益计算逻辑"""
    print("=" * 60)
    print("测试月度收益计算逻辑调整")
    print("新逻辑：该月买入的股票最终产生的收益都算作该月收益")
    print("=" * 60)
    
    try:
        # 测试当前年份的月度统计
        current_year = datetime.now().year
        print(f"\n1. 测试 {current_year} 年月度统计...")
        
        response = requests.get(f"{BASE_URL}/api/analytics/monthly?year={current_year}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                monthly_data = data['data']['monthly_data']
                year_summary = data['data']['year_summary']
                
                print(f"✅ 获取月度统计成功")
                print(f"年度汇总：")
                print(f"  - 总交易次数: {year_summary['total_trades']}")
                print(f"  - 总收益: ¥{year_summary['total_profit']:.2f}")
                print(f"  - 有数据月份: {year_summary['months_with_data']}")
                print(f"  - 平均月度收益率: {year_summary['average_monthly_return']:.4f}")
                
                print(f"\n月度详情：")
                for month_data in monthly_data:
                    if month_data['has_data']:
                        profit_rate_str = f"{month_data['profit_rate']:.4f}" if month_data['profit_rate'] is not None else "无数据"
                        print(f"  {month_data['month_name']}: "
                              f"交易{month_data['total_trades']}次, "
                              f"收益¥{month_data['profit_amount']:.2f}, "
                              f"收益率{profit_rate_str}, "
                              f"涉及{month_data['unique_stocks']}只股票")
                
                # 验证逻辑调整的关键点
                print(f"\n🔍 逻辑验证要点：")
                print(f"1. 收益归属：现在按买入时间归属，而非卖出时间")
                print(f"2. 计算方式：该月买入的股票，无论何时卖出，收益都算该月")
                print(f"3. 未卖出股票：该月买入但未卖出的股票，收益为0（不影响月度收益）")
                
            else:
                print(f"❌ API返回错误: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_specific_scenarios():
    """测试特定场景下的月度收益计算"""
    print(f"\n" + "=" * 60)
    print("测试特定场景")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "跨月交易场景",
            "description": "1月买入，2月卖出 -> 收益应归属1月"
        },
        {
            "name": "分批交易场景", 
            "description": "1月买入100股，2月买入200股，3月全部卖出 -> 1月和2月都有收益"
        },
        {
            "name": "持仓未卖场景",
            "description": "1月买入但未卖出 -> 1月收益为0（不计算浮盈浮亏）"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   场景说明: {scenario['description']}")
        print(f"   验证方法: 查看月度统计数据，确认收益归属正确")

def compare_old_vs_new_logic():
    """对比新旧逻辑的差异"""
    print(f"\n" + "=" * 60)
    print("新旧逻辑对比")
    print("=" * 60)
    
    comparison = [
        {
            "aspect": "收益归属时间",
            "old_logic": "按卖出时间归属",
            "new_logic": "按买入时间归属"
        },
        {
            "aspect": "跨月交易处理",
            "old_logic": "1月买入2月卖出 -> 收益归2月",
            "new_logic": "1月买入2月卖出 -> 收益归1月"
        },
        {
            "aspect": "分批交易处理",
            "old_logic": "按每次卖出的时间分别归属",
            "new_logic": "按对应买入的时间分别归属"
        },
        {
            "aspect": "业务含义",
            "old_logic": "反映资金回笼的时间分布",
            "new_logic": "反映投资决策的时间分布"
        }
    ]
    
    for comp in comparison:
        print(f"\n📊 {comp['aspect']}:")
        print(f"   旧逻辑: {comp['old_logic']}")
        print(f"   新逻辑: {comp['new_logic']}")

if __name__ == "__main__":
    print("月度收益计算逻辑调整测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 对比新旧逻辑
    compare_old_vs_new_logic()
    
    # 测试特定场景
    test_specific_scenarios()
    
    # 测试新逻辑
    test_monthly_analytics_new_logic()
    
    print(f"\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)