#!/usr/bin/env python3
"""
分析8月份月度收益计算逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from services.analytics_service import AnalyticsService
from datetime import datetime
from collections import defaultdict

def analyze_august_monthly_profit():
    """分析8月份的月度收益计算"""
    app = create_app()
    
    with app.app_context():
        print("=== 8月份月度收益计算分析 ===\n")
        
        # 1. 获取8月份的所有交易记录
        august_trades = TradeRecord.query.filter(
            TradeRecord.trade_date >= datetime(2024, 8, 1),
            TradeRecord.trade_date <= datetime(2024, 8, 31)
        ).order_by(TradeRecord.trade_date, TradeRecord.stock_code).all()
        
        print("1. 8月份交易记录:")
        print("-" * 80)
        print(f"{'日期':<12} {'股票代码':<10} {'类型':<6} {'数量':<8} {'价格':<10} {'金额':<12}")
        print("-" * 80)
        
        august_buy_amount = 0
        august_sell_amount = 0
        
        for trade in august_trades:
            amount = trade.quantity * trade.price
            if trade.trade_type == 'buy':
                august_buy_amount += amount
            else:
                august_sell_amount += amount
                
            print(f"{trade.trade_date.strftime('%Y-%m-%d'):<12} "
                  f"{trade.stock_code:<10} "
                  f"{trade.trade_type:<6} "
                  f"{trade.quantity:<8} "
                  f"{trade.price:<10.2f} "
                  f"{amount:<12.2f}")
        
        print("-" * 80)
        print(f"8月份买入总额: {august_buy_amount:.2f}")
        print(f"8月份卖出总额: {august_sell_amount:.2f}")
        print(f"简单差额: {august_sell_amount - august_buy_amount:.2f}")
        print()
        
        # 2. 获取系统计算的月度统计
        monthly_stats = AnalyticsService.get_monthly_statistics(2024)
        august_stats = None
        for stat in monthly_stats:
            if stat['month'] == 8:
                august_stats = stat
                break
        
        if august_stats:
            print("2. 系统计算的8月份统计:")
            print("-" * 50)
            print(f"总收益金额: {august_stats['profit_amount']:.2f}")
            if august_stats['profit_rate'] is not None:
                print(f"月度收益率: {august_stats['profit_rate']:.4f} ({august_stats['profit_rate']*100:.2f}%)")
            else:
                print("月度收益率: 无数据")
            print(f"成功交易数: {august_stats['success_count']}")
            print(f"成功率: {august_stats['success_rate']:.2f}%")
            print()
        
        # 3. 详细分析计算逻辑
        print("3. 详细计算逻辑分析:")
        print("-" * 50)
        
        # 获取所有交易记录（不仅仅是8月份的）
        all_trades = TradeRecord.query.order_by(TradeRecord.trade_date).all()
        
        # 按股票分组
        stock_trades = defaultdict(list)
        for trade in all_trades:
            stock_trades[trade.stock_code].append(trade)
        
        print("按股票分析8月份买入产生的收益:")
        print()
        
        total_august_profit = 0
        total_august_cost = 0
        success_stocks = 0
        
        for stock_code, trades in stock_trades.items():
            # 检查是否有8月份买入的交易
            august_buys = [t for t in trades if t.trade_type == 'buy' and 
                          datetime(2024, 8, 1) <= t.trade_date <= datetime(2024, 8, 31)]
            
            if august_buys:
                print(f"\n股票 {stock_code}:")
                print(f"  8月份买入记录: {len(august_buys)} 笔")
                
                # 计算该股票8月份买入产生的收益
                monthly_profits = AnalyticsService._get_monthly_buy_total_profits(
                    trades, datetime(2024, 8, 1), datetime(2024, 8, 31, 23, 59, 59)
                )
                
                stock_profit = 0
                stock_cost = 0
                
                for profit_item in monthly_profits:
                    stock_profit += profit_item['total_profit']
                    stock_cost += profit_item['cost']
                    
                    print(f"    {profit_item['type']} - "
                          f"成本: {profit_item['cost']:.2f}, "
                          f"收益: {profit_item['total_profit']:.2f}")
                
                total_august_profit += stock_profit
                total_august_cost += stock_cost
                
                if stock_profit > 0:
                    success_stocks += 1
                
                print(f"  该股票8月买入总成本: {stock_cost:.2f}")
                print(f"  该股票8月买入总收益: {stock_profit:.2f}")
                if stock_cost > 0:
                    print(f"  该股票收益率: {stock_profit/stock_cost:.4f} ({stock_profit/stock_cost*100:.2f}%)")
        
        print("\n" + "="*60)
        print("4. 最终计算结果:")
        print("-" * 30)
        print(f"8月份买入总成本: {total_august_cost:.2f}")
        print(f"8月份买入总收益: {total_august_profit:.2f}")
        if total_august_cost > 0:
            print(f"8月份月度收益率: {total_august_profit/total_august_cost:.4f} ({total_august_profit/total_august_cost*100:.2f}%)")
        print(f"成功股票数: {success_stocks}")
        
        print("\n" + "="*60)
        print("5. 计算逻辑说明:")
        print("-" * 30)
        print("月度收益计算采用'买入归属'原则:")
        print("1. 只计算该月买入的股票产生的收益")
        print("2. 包括已实现收益（该月买入后来卖出的部分）")
        print("3. 包括未实现收益（该月买入但仍持有的部分，按当前价格计算浮盈浮亏）")
        print("4. 月度收益率 = 该月买入产生的总收益 / 该月买入的总成本")
        print("5. 这样可以准确反映每月投资决策的效果")

if __name__ == "__main__":
    analyze_august_monthly_profit()