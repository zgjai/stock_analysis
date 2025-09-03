#!/usr/bin/env python3
"""
月度收益计算逻辑详细说明
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from services.analytics_service import AnalyticsService
from datetime import datetime

def explain_monthly_profit_calculation():
    """详细说明月度收益计算逻辑"""
    app = create_app()
    
    with app.app_context():
        print("=== 月度收益计算逻辑详细说明 ===\n")
        
        print("1. 计算原理:")
        print("-" * 40)
        print("月度收益采用'买入归属'原则，即:")
        print("• 该月的收益 = 该月买入的股票产生的所有收益")
        print("• 不管这些股票是什么时候卖出的")
        print("• 包括已实现收益和未实现收益（浮盈浮亏）")
        print()
        
        print("2. 具体计算步骤:")
        print("-" * 40)
        print("步骤1: 找出该月买入的所有股票")
        print("步骤2: 对每只股票，使用FIFO方法计算收益")
        print("步骤3: 汇总所有股票的收益和成本")
        print("步骤4: 计算月度收益率 = 总收益 / 总成本")
        print()
        
        # 获取2025年8月的实际数据
        system_profit, system_success, system_cost = AnalyticsService._calculate_monthly_realized_profit_and_success(
            TradeRecord.query.all(), 8, 2025
        )
        
        print("3. 2025年8月实际数据:")
        print("-" * 40)
        print(f"该月买入总成本: {system_cost:,.2f} 元")
        print(f"该月买入总收益: {system_profit:,.2f} 元")
        print(f"月度收益率: {system_profit/system_cost:.4f} ({system_profit/system_cost*100:.2f}%)")
        print(f"盈利股票数: {system_success}")
        print()
        
        print("4. 为什么不用简单的 卖出金额 - 买入金额？")
        print("-" * 50)
        
        # 计算8月份的简单差额
        august_trades = TradeRecord.query.filter(
            TradeRecord.trade_date >= datetime(2025, 8, 1),
            TradeRecord.trade_date <= datetime(2025, 8, 31)
        ).all()
        
        august_buy_amount = 0
        august_sell_amount = 0
        
        for trade in august_trades:
            amount = float(trade.quantity * trade.price)
            if trade.trade_type == 'buy':
                august_buy_amount += amount
            else:
                august_sell_amount += amount
        
        simple_diff = august_sell_amount - august_buy_amount
        
        print(f"8月份买入金额: {august_buy_amount:,.2f} 元")
        print(f"8月份卖出金额: {august_sell_amount:,.2f} 元")
        print(f"简单差额: {simple_diff:,.2f} 元")
        print()
        
        print("问题在于:")
        print("• 8月卖出的股票可能是7月或更早买入的")
        print("• 8月买入的股票可能在9月才卖出")
        print("• 简单差额无法准确反映8月投资决策的效果")
        print()
        
        print("5. 举例说明:")
        print("-" * 40)
        print("假设:")
        print("• 7月买入股票A，成本100元")
        print("• 8月买入股票B，成本200元")
        print("• 8月卖出股票A，收入110元")
        print("• 9月卖出股票B，收入250元")
        print()
        print("简单计算法:")
        print("8月收益 = 8月卖出(110) - 8月买入(200) = -90元")
        print()
        print("买入归属法:")
        print("8月收益 = 8月买入股票B的收益 = 250 - 200 = 50元")
        print("(更准确反映8月投资决策的效果)")
        print()
        
        print("6. 已实现收益 vs 未实现收益:")
        print("-" * 40)
        print("已实现收益:")
        print("• 该月买入的股票，后来卖出的部分")
        print("• 收益 = 卖出价格 × 数量 - 买入价格 × 数量")
        print()
        print("未实现收益（浮盈浮亏）:")
        print("• 该月买入的股票，目前仍持有的部分")
        print("• 收益 = 当前价格 × 数量 - 买入价格 × 数量")
        print()
        
        print("7. FIFO匹配原则:")
        print("-" * 40)
        print("当同一只股票有多次买入和卖出时:")
        print("• 按时间顺序，先买入的先卖出")
        print("• 确保收益计算的准确性")
        print("• 避免重复计算或遗漏")

if __name__ == "__main__":
    explain_monthly_profit_calculation()