#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算期望月度收益
基于给定的概率分布和持仓策略
"""

import datetime
from dateutil.relativedelta import relativedelta

def calculate_expected_monthly_return():
    """
    计算单月期望收益率
    
    基础参数：
    - 启动资金：320万
    - 同时持仓：10只股票
    - 每只股票投入：32万
    
    概率分布：
    1. 10%能够盈利20%，持仓天数最大为30天
    2. 10%的能够盈利15%，持仓天数最大为20天
    3. 15%的能够盈利10%，持仓天数最大为15天
    4. 15%能够盈利5%，持仓天数最大为10天
    5. 10%能够盈利2%，持仓天数最大为5天
    6. 20%会亏损3%，持仓天数最大为5天
    7. 15%会亏损5%，持仓天数最大为5天
    8. 5%会亏损10%，持仓天数最大为5天
    """
    
    # 基础参数
    total_capital = 3200000  # 320万
    positions = 10  # 10只股票
    capital_per_stock = total_capital / positions  # 每只32万
    
    # 概率分布 (概率, 收益率, 最大持仓天数)
    scenarios = [
        (0.10, 0.20, 30),  # 10%概率盈利20%
        (0.10, 0.15, 20),  # 10%概率盈利15%
        (0.15, 0.10, 15),  # 15%概率盈利10%
        (0.15, 0.05, 10),  # 15%概率盈利5%
        (0.10, 0.02, 5),   # 10%概率盈利2%
        (0.20, -0.03, 5),  # 20%概率亏损3%
        (0.15, -0.05, 5),  # 15%概率亏损5%
        (0.05, -0.10, 5),  # 5%概率亏损10%
    ]
    
    print("=== 期望收益计算 ===")
    print(f"启动资金: {total_capital:,} 元")
    print(f"同时持仓: {positions} 只")
    print(f"每只投入: {capital_per_stock:,} 元")
    print()
    
    # 计算期望收益率
    expected_return_rate = 0
    print("概率分布详情:")
    for i, (prob, return_rate, days) in enumerate(scenarios, 1):
        contribution = prob * return_rate
        expected_return_rate += contribution
        print(f"{i}. 概率{prob*100:4.0f}% | 收益率{return_rate*100:+6.1f}% | 最大{days:2d}天 | 贡献{contribution*100:+6.2f}%")
    
    print(f"\n期望收益率: {expected_return_rate*100:.2f}%")
    
    # 计算月度期望收益
    # 假设一个月有22个交易日，根据持仓天数计算月度周转次数
    trading_days_per_month = 22
    
    # 计算加权平均持仓天数
    weighted_avg_days = sum(prob * days for prob, _, days in scenarios)
    print(f"加权平均持仓天数: {weighted_avg_days:.1f}天")
    
    # 计算月度周转次数
    monthly_turnover = trading_days_per_month / weighted_avg_days
    print(f"月度周转次数: {monthly_turnover:.2f}次")
    
    # 月度期望收益率
    monthly_expected_return_rate = expected_return_rate * monthly_turnover
    print(f"月度期望收益率: {monthly_expected_return_rate*100:.2f}%")
    
    # 月度期望收益金额
    monthly_expected_return_amount = total_capital * monthly_expected_return_rate
    print(f"月度期望收益金额: {monthly_expected_return_amount:,.0f} 元")
    
    return monthly_expected_return_rate, monthly_expected_return_amount

def generate_monthly_expectations():
    """
    生成未来两年的月度期望收益（复利计算）
    """
    monthly_rate, _ = calculate_expected_monthly_return()
    
    # 生成从2025年8月开始的24个月数据
    start_date = datetime.date(2025, 8, 1)
    monthly_data = []
    
    # 初始本金320万
    current_capital = 3200000
    
    print(f"\n=== 未来两年月度期望收益（复利计算）===")
    print("月份\t\t当月本金\t\t期望收益率\t期望收益金额\t月末本金")
    print("-" * 80)
    
    for i in range(24):  # 24个月
        current_date = start_date + relativedelta(months=i)
        month_str = current_date.strftime("%Y年%m月")
        
        # 计算当月期望收益
        monthly_expected_return = current_capital * monthly_rate
        
        # 月末本金 = 当月本金 + 期望收益
        end_capital = current_capital + monthly_expected_return
        
        monthly_data.append({
            'month': month_str,
            'date': current_date,
            'start_capital': current_capital,
            'expected_rate': monthly_rate,
            'expected_amount': monthly_expected_return,
            'end_capital': end_capital
        })
        
        print(f"{month_str}\t{current_capital:12,.0f}元\t{monthly_rate*100:6.2f}%\t\t{monthly_expected_return:10,.0f}元\t{end_capital:12,.0f}元")
        
        # 更新下个月的本金（复利）
        current_capital = end_capital
    
    return monthly_data

if __name__ == "__main__":
    # 计算并显示期望收益
    monthly_data = generate_monthly_expectations()
    
    # 保存为JSON格式供前端使用
    import json
    
    # 转换为JSON可序列化的格式
    json_data = []
    for item in monthly_data:
        json_data.append({
            'month': item['month'],
            'date': item['date'].strftime('%Y-%m-%d'),
            'start_capital': round(item['start_capital'], 0),
            'expected_rate': round(item['expected_rate'] * 100, 2),  # 转换为百分比
            'expected_amount': round(item['expected_amount'], 0),
            'end_capital': round(item['end_capital'], 0)
        })
    
    with open('expected_monthly_returns.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存到 expected_monthly_returns.json")