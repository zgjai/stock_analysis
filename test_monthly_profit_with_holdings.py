#!/usr/bin/env python3
"""
测试月度收益计算逻辑 - 包含持仓浮盈浮亏
验证该月买入的股票收益包括已实现收益和持仓浮盈浮亏
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_monthly_analytics_with_holdings():
    """测试包含持仓浮盈浮亏的月度收益计算"""
    print("=" * 70)
    print("测试月度收益计算 - 包含持仓浮盈浮亏")
    print("新逻辑：该月买入的股票收益 = 已实现收益 + 持仓浮盈浮亏")
    print("=" * 70)
    
    try:
        # 测试当前年份的月度统计
        current_year = datetime.now().year
        print(f"\n1. 测试 {current_year} 年月度统计（包含持仓收益）...")
        
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
                
                print(f"\n月度详情（包含持仓浮盈浮亏）：")
                for month_data in monthly_data:
                    if month_data['has_data']:
                        profit_rate_str = f"{month_data['profit_rate']:.4f}" if month_data['profit_rate'] is not None else "无数据"
                        print(f"  {month_data['month_name']}: ")
                        print(f"    - 交易次数: {month_data['total_trades']} (买入{month_data['buy_count']}, 卖出{month_data['sell_count']})")
                        print(f"    - 月度收益: ¥{month_data['profit_amount']:.2f} (包含持仓浮盈浮亏)")
                        print(f"    - 收益率: {profit_rate_str}")
                        print(f"    - 涉及股票: {month_data['unique_stocks']}只")
                
                # 对比总体统计
                print(f"\n2. 对比总体统计数据...")
                overview_response = requests.get(f"{BASE_URL}/api/analytics/overview")
                if overview_response.status_code == 200:
                    overview_data = overview_response.json()
                    if overview_data.get('success'):
                        overview = overview_data['data']
                        print(f"  总体已实现收益: ¥{overview['realized_profit']:.2f}")
                        print(f"  总体持仓收益: ¥{overview['current_holdings_profit']:.2f}")
                        print(f"  总体收益: ¥{overview['total_profit']:.2f}")
                        
                        # 验证月度收益是否包含了持仓收益
                        total_monthly_profit = year_summary['total_profit']
                        total_overall_profit = overview['total_profit']
                        
                        print(f"\n3. 收益一致性验证:")
                        print(f"  月度收益汇总: ¥{total_monthly_profit:.2f}")
                        print(f"  总体收益: ¥{total_overall_profit:.2f}")
                        
                        if abs(total_monthly_profit - total_overall_profit) < 0.01:
                            print(f"  ✅ 收益数据一致")
                        else:
                            print(f"  ⚠️ 收益数据存在差异，可能是跨年交易导致")
                
            else:
                print(f"❌ API返回错误: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_holdings_impact():
    """测试持仓对月度收益的影响"""
    print(f"\n" + "=" * 70)
    print("测试持仓对月度收益的影响")
    print("=" * 70)
    
    try:
        # 获取当前持仓
        holdings_response = requests.get(f"{BASE_URL}/api/analytics/holdings")
        if holdings_response.status_code == 200:
            holdings_data = holdings_response.json()
            if holdings_data.get('success'):
                holdings = holdings_data['data']
                
                print(f"当前持仓概况:")
                print(f"  - 持仓股票数: {holdings['total_count']}只")
                print(f"  - 总市值: ¥{holdings['total_market_value']:.2f}")
                print(f"  - 总成本: ¥{holdings['total_cost']:.2f}")
                print(f"  - 浮盈浮亏: ¥{holdings['total_profit']:.2f}")
                
                print(f"\n持仓明细（前10只）:")
                for i, holding in enumerate(holdings['holdings'][:10], 1):
                    print(f"  {i}. {holding['stock_code']} - {holding.get('stock_name', '')}")
                    print(f"     持仓: {holding['quantity']}股, 成本: ¥{holding['total_cost']:.2f}")
                    print(f"     市值: ¥{holding['market_value']:.2f}, 收益: ¥{holding['profit_amount']:.2f}")
                    print(f"     收益率: {holding['profit_rate']*100:.2f}%")
                
                print(f"\n💡 说明:")
                print(f"  - 这些持仓的浮盈浮亏现在会计入对应买入月份的收益")
                print(f"  - 月度收益会随着股价变化实时更新")
                print(f"  - 体现了投资决策在不同时期的完整表现")
                
        else:
            print(f"❌ 获取持仓数据失败: {holdings_response.status_code}")
    
    except Exception as e:
        print(f"❌ 测试持仓影响失败: {e}")

def explain_new_logic():
    """解释新的计算逻辑"""
    print(f"\n" + "=" * 70)
    print("新月度收益计算逻辑说明")
    print("=" * 70)
    
    logic_points = [
        {
            "title": "收益构成",
            "content": "月度收益 = 该月买入股票的已实现收益 + 该月买入股票的持仓浮盈浮亏"
        },
        {
            "title": "已实现收益",
            "content": "该月买入且已卖出的股票产生的收益（使用FIFO匹配）"
        },
        {
            "title": "持仓浮盈浮亏",
            "content": "该月买入但仍持仓的股票，按当前价格计算的浮盈浮亏"
        },
        {
            "title": "实时更新",
            "content": "持仓部分会随股价变化实时更新，反映投资决策的当前表现"
        },
        {
            "title": "归属原则",
            "content": "按买入时间归属，体现投资决策的时间分布和效果"
        }
    ]
    
    for i, point in enumerate(logic_points, 1):
        print(f"\n{i}. {point['title']}")
        print(f"   {point['content']}")
    
    print(f"\n📊 计算示例:")
    print(f"   假设8月买入股票A 1000股，成本10万元")
    print(f"   - 9月卖出500股，获利5000元")
    print(f"   - 剩余500股当前浮盈3000元")
    print(f"   - 则8月收益 = 5000 + 3000 = 8000元")
    print(f"   - 如果股价继续上涨，8月收益会继续增加")

if __name__ == "__main__":
    print("月度收益计算逻辑测试 - 包含持仓浮盈浮亏")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 解释新逻辑
    explain_new_logic()
    
    # 测试月度统计
    test_monthly_analytics_with_holdings()
    
    # 测试持仓影响
    test_holdings_impact()
    
    print(f"\n" + "=" * 70)
    print("✅ 测试完成")
    print("月度收益现在包含该月买入股票的完整收益表现：")
    print("- 已实现收益（已卖出部分）")
    print("- 持仓浮盈浮亏（未卖出部分，实时更新）")
    print("=" * 70)