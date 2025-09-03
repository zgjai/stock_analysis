#!/usr/bin/env python3
"""
详细分析2025年8月月度收益计算
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from services.analytics_service import AnalyticsService
from datetime import datetime
from collections import defaultdict

def detailed_august_analysis():
    """详细分析2025年8月的月度收益计算"""
    app = create_app()
    
    with app.app_context():
        print("=== 2025年8月月度收益详细计算分析 ===\n")
        
        # 获取所有交易记录
        all_trades = TradeRecord.query.order_by(TradeRecord.trade_date).all()
        
        # 按股票分组
        stock_trades = defaultdict(list)
        for trade in all_trades:
            stock_trades[trade.stock_code].append(trade)
        
        # 分析8月份买入的股票
        august_start = datetime(2025, 8, 1)
        august_end = datetime(2025, 8, 31, 23, 59, 59)
        
        print("1. 月度收益计算原理:")
        print("-" * 50)
        print("月度收益采用'买入归属'原则:")
        print("• 只计算该月买入的股票产生的收益")
        print("• 包括已实现收益：该月买入后来卖出的部分")
        print("• 包括未实现收益：该月买入但仍持有的部分（浮盈浮亏）")
        print("• 月度收益率 = 该月买入产生的总收益 / 该月买入的总成本")
        print()
        
        # 找出8月份有买入的股票
        august_buy_stocks = set()
        for trade in all_trades:
            if (trade.trade_type == 'buy' and 
                august_start <= trade.trade_date <= august_end):
                august_buy_stocks.add(trade.stock_code)
        
        print(f"2. 2025年8月买入的股票数量: {len(august_buy_stocks)}")
        print("-" * 50)
        
        total_profit = 0
        total_cost = 0
        success_stocks = 0
        
        # 分析每只股票
        for i, stock_code in enumerate(sorted(august_buy_stocks), 1):
            print(f"\n{i}. 股票 {stock_code}:")
            
            # 获取该股票的所有交易
            stock_trade_list = stock_trades[stock_code]
            
            # 计算8月份买入产生的收益
            monthly_profits = AnalyticsService._get_monthly_buy_total_profits(
                stock_trade_list, august_start, august_end
            )
            
            stock_profit = 0
            stock_cost = 0
            realized_profit = 0
            unrealized_profit = 0
            
            print("   交易明细:")
            for profit_item in monthly_profits:
                stock_profit += profit_item['total_profit']
                stock_cost += profit_item['cost']
                
                if profit_item['type'] == 'realized':
                    realized_profit += profit_item['total_profit']
                    print(f"   • 已实现: 买入{profit_item['buy_date'].strftime('%m-%d')} "
                          f"卖出{profit_item['sell_date'].strftime('%m-%d')} "
                          f"数量{profit_item['quantity']} "
                          f"成本{profit_item['cost']:.2f} "
                          f"收益{profit_item['total_profit']:.2f}")
                else:
                    unrealized_profit += profit_item['total_profit']
                    print(f"   • 未实现: 买入{profit_item['buy_date'].strftime('%m-%d')} "
                          f"持有{profit_item['quantity']} "
                          f"成本{profit_item['cost']:.2f} "
                          f"浮盈{profit_item['total_profit']:.2f}")
            
            total_profit += stock_profit
            total_cost += stock_cost
            
            if stock_profit > 0:
                success_stocks += 1
            
            profit_rate = stock_profit / stock_cost if stock_cost > 0 else 0
            print(f"   小计: 成本{stock_cost:.2f} 收益{stock_profit:.2f} "
                  f"收益率{profit_rate:.4f}({profit_rate*100:.2f}%)")
            
            if i >= 10:  # 只显示前10只股票的详情
                print(f"\n   ... (还有{len(august_buy_stocks)-10}只股票)")
                break
        
        print("\n" + "="*60)
        print("3. 最终计算结果:")
        print("-" * 30)
        print(f"8月份买入股票总数: {len(august_buy_stocks)}")
        print(f"8月份买入总成本: {total_cost:,.2f} 元")
        print(f"8月份买入总收益: {total_profit:,.2f} 元")
        
        if total_cost > 0:
            monthly_return = total_profit / total_cost
            print(f"8月份月度收益率: {monthly_return:.4f} ({monthly_return*100:.2f}%)")
        
        print(f"盈利股票数量: {success_stocks}")
        print(f"成功率: {success_stocks/len(august_buy_stocks)*100:.2f}%")
        
        # 验证系统计算结果
        system_profit, system_success, system_cost = AnalyticsService._calculate_monthly_realized_profit_and_success(
            all_trades, 8, 2025
        )
        
        print("\n4. 系统计算验证:")
        print("-" * 30)
        print(f"系统计算收益: {system_profit:,.2f}")
        print(f"系统计算成本: {system_cost:,.2f}")
        print(f"系统计算成功数: {system_success}")
        
        print("\n5. 为什么不是简单的 卖出金额 - 买入金额？")
        print("-" * 50)
        print("因为:")
        print("• 8月买入的股票可能在9月才卖出")
        print("• 8月卖出的股票可能是7月买入的")
        print("• 月度收益要准确反映该月投资决策的效果")
        print("• 所以采用'买入归属'原则，计算该月买入股票的收益")
        print("• 包括已实现收益和未实现收益（持仓浮盈浮亏）")

if __name__ == "__main__":
    detailed_august_analysis()