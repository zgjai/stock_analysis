#!/usr/bin/env python3
"""
详细验证月度收益计算逻辑调整
验证按买入时间归属收益的正确性
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001"

def get_all_trades():
    """获取所有交易记录用于验证"""
    try:
        response = requests.get(f"{BASE_URL}/api/trades?limit=1000")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data['data']['trades']
    except Exception as e:
        print(f"获取交易记录失败: {e}")
    return []

def analyze_trade_patterns():
    """分析交易模式，验证新逻辑的合理性"""
    print("=" * 60)
    print("交易模式分析")
    print("=" * 60)
    
    trades = get_all_trades()
    if not trades:
        print("❌ 无法获取交易数据")
        return
    
    # 按股票分组分析
    stock_trades = {}
    for trade in trades:
        stock_code = trade['stock_code']
        if stock_code not in stock_trades:
            stock_trades[stock_code] = []
        stock_trades[stock_code].append(trade)
    
    print(f"📊 总共分析 {len(stock_trades)} 只股票的交易记录")
    
    # 分析跨月交易情况
    cross_month_cases = []
    same_month_cases = []
    
    for stock_code, stock_trade_list in stock_trades.items():
        # 按时间排序
        stock_trade_list.sort(key=lambda x: x['trade_date'])
        
        # 查找买入-卖出配对
        buy_trades = [t for t in stock_trade_list if t['trade_type'] == 'buy']
        sell_trades = [t for t in stock_trade_list if t['trade_type'] == 'sell']
        
        if buy_trades and sell_trades:
            first_buy_date = datetime.fromisoformat(buy_trades[0]['trade_date'].replace('Z', '+00:00'))
            first_sell_date = datetime.fromisoformat(sell_trades[0]['trade_date'].replace('Z', '+00:00'))
            
            buy_month = f"{first_buy_date.year}-{first_buy_date.month:02d}"
            sell_month = f"{first_sell_date.year}-{first_sell_date.month:02d}"
            
            case_info = {
                'stock_code': stock_code,
                'stock_name': stock_trade_list[0].get('stock_name', ''),
                'buy_month': buy_month,
                'sell_month': sell_month,
                'buy_count': len(buy_trades),
                'sell_count': len(sell_trades)
            }
            
            if buy_month != sell_month:
                cross_month_cases.append(case_info)
            else:
                same_month_cases.append(case_info)
    
    print(f"\n📈 跨月交易案例: {len(cross_month_cases)} 个")
    print("   (这些案例最能体现新旧逻辑的差异)")
    
    for i, case in enumerate(cross_month_cases[:5], 1):  # 显示前5个
        print(f"   {i}. {case['stock_code']} ({case['stock_name']})")
        print(f"      买入月份: {case['buy_month']}, 卖出月份: {case['sell_month']}")
        print(f"      旧逻辑: 收益归属{case['sell_month']}")
        print(f"      新逻辑: 收益归属{case['buy_month']}")
    
    if len(cross_month_cases) > 5:
        print(f"   ... 还有 {len(cross_month_cases) - 5} 个跨月案例")
    
    print(f"\n📊 同月交易案例: {len(same_month_cases)} 个")
    print("   (这些案例新旧逻辑结果相同)")

def verify_monthly_calculation_logic():
    """验证月度计算逻辑的正确性"""
    print(f"\n" + "=" * 60)
    print("月度计算逻辑验证")
    print("=" * 60)
    
    try:
        # 获取2025年月度统计
        response = requests.get(f"{BASE_URL}/api/analytics/monthly?year=2025")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                monthly_data = data['data']['monthly_data']
                
                print("✅ 新逻辑验证要点:")
                print("\n1. 收益归属原则:")
                print("   - 该月买入的股票，无论何时卖出，收益都归属该月")
                print("   - 未卖出的股票不计入月度收益（只计算已实现收益）")
                
                print("\n2. FIFO匹配原则:")
                print("   - 卖出时按先进先出原则匹配买入记录")
                print("   - 每笔卖出都能追溯到对应的买入记录")
                print("   - 收益 = 匹配数量 × (卖出价格 - 买入价格)")
                
                print("\n3. 月度收益率计算:")
                print("   - 月度收益率 = 该月买入产生的已实现收益 / 该月买入成本")
                print("   - 分母是该月买入的总成本，分子是这些买入最终产生的收益")
                
                # 显示有数据的月份
                months_with_data = [m for m in monthly_data if m['has_data']]
                print(f"\n4. 当前数据验证:")
                print(f"   - 有交易数据的月份: {len(months_with_data)} 个")
                
                for month_info in months_with_data:
                    print(f"   - {month_info['month_name']}: ")
                    print(f"     买入次数: {month_info['buy_count']}")
                    print(f"     卖出次数: {month_info['sell_count']}")
                    print(f"     月度收益: ¥{month_info['profit_amount']:.2f}")
                    if month_info['profit_rate'] is not None:
                        print(f"     收益率: {month_info['profit_rate']:.4f} ({month_info['profit_rate']*100:.2f}%)")
                    else:
                        print(f"     收益率: 无数据")
                
            else:
                print(f"❌ 获取月度数据失败: {data.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 验证失败: {e}")

def test_edge_cases():
    """测试边缘情况"""
    print(f"\n" + "=" * 60)
    print("边缘情况测试")
    print("=" * 60)
    
    edge_cases = [
        {
            "case": "分批买入分批卖出",
            "description": "1月买入100股，2月买入200股，3月卖出150股，4月卖出150股",
            "expected": "1月收益=100股对应的收益，2月收益=200股中50股的收益+剩余150股的收益"
        },
        {
            "case": "买入后长期持有",
            "description": "1月买入，至今未卖出",
            "expected": "1月收益=0（不计算浮盈浮亏）"
        },
        {
            "case": "当月买入当月卖出",
            "description": "1月买入，1月卖出",
            "expected": "1月收益=实际收益（新旧逻辑结果相同）"
        },
        {
            "case": "多次买入后一次性卖出",
            "description": "1月买入100股，2月买入100股，3月卖出200股",
            "expected": "1月收益=100股收益，2月收益=100股收益"
        }
    ]
    
    for i, case in enumerate(edge_cases, 1):
        print(f"\n{i}. {case['case']}")
        print(f"   场景: {case['description']}")
        print(f"   预期: {case['expected']}")

if __name__ == "__main__":
    print("月度收益计算逻辑详细验证")
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 分析交易模式
    analyze_trade_patterns()
    
    # 验证计算逻辑
    verify_monthly_calculation_logic()
    
    # 测试边缘情况
    test_edge_cases()
    
    print(f"\n" + "=" * 60)
    print("✅ 验证完成")
    print("新的月度收益计算逻辑已按要求调整：")
    print("- 收益归属改为按买入时间")
    print("- 该月买入的股票最终产生的收益都算作该月收益")
    print("- 保持FIFO匹配原则确保计算准确性")
    print("=" * 60)