#!/usr/bin/env python3
"""
完整分析2025年8月月度收益计算
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from services.analytics_service import AnalyticsService
from datetime import datetime
from collections import defaultdict

def complete_august_analysis():
    """完整分析2025年8月的月度收益计算"""
    app = create_app()
    
    with app.app_context():
        print("=== 2025年8月月度收益完整计算分析 ===\n")
        
        # 获取所有交易记录
        all_trades = TradeRecord.query.order_by(TradeRecord.trade_date).all()
        
        # 按股票分组
        stock_trades = defaultdict(list)
        for trade in all_trades:
            stock_trades[trade.stock_code].append(trade)
        
        # 分析8月份买入的股票
        august_start = datetime(2025, 8, 1)
        august_end = datetime(2025, 8, 31, 23, 59, 59)
        
        # 找出8月份有买入的股票
        august_buy_stocks = set()
        for trade in all_trades:
            if (trade.trade_type == 'buy' and 
                august_start <= trade.trade_date <= august_end):
                august_buy_stocks.add(trade.stock_code)
        
        print(f"8月份买入的股票数量: {len(august_buy_stocks)}")
        print("股票列表:", sorted(august_buy_stocks))
        print()
        
        total_profit = 0
        total_cost = 0
        success_stocks = 0
        
        # 分析每只股票
        for stock_code in sorted(august_buy_stocks):
            print(f"股票 {stock_code}:")
            
            # 获取该股票的所有交易
            stock_trade_list = stock_trades[stock_code]
            
            # 显示该股票的所有交易记录
            print("  所有交易记录:")
            for trade in stock_trade_list:
                print(f"    {trade.trade_date.strftime('%Y-%m-%d')} {trade.trade_type} "
                      f"{trade.quantity}@{trade.price}")
            
            # 计算8月份买入产生的收益
            monthly_profits = AnalyticsService._get_monthly_buy_total_profits(
                stock_trade_list, august_start, august_end
            )
            
            stock_profit = 0
            stock_cost = 0
            
            print("  8月买入产生的收益:")
            for profit_item in monthly_profits:
                stock_profit += profit_item['total_profit']
                stock_cost += profit_item['cost']
                
                if profit_item['type'] == 'realized':
                    print(f"    已实现: 买入{profit_item['buy_date'].strftime('%m-%d')} "
                          f"卖出{profit_item['sell_date'].strftime('%m-%d')} "
                          f"数量{profit_item['quantity']} "
                          f"成本{profit_item['cost']:.2f} "
                          f"收益{profit_item['total_profit']:.2f}")
                else:
                    print(f"    未实现: 买入{profit_item['buy_date'].strftime('%m-%d')} "
                          f"持有{profit_item['quantity']} "
                          f"成本{profit_item['cost']:.2f} "
                          f"浮盈{profit_item['total_profit']:.2f}")
            
            total_profit += stock_profit
            total_cost += stock_cost
            
            if stock_profit > 0:
                success_stocks += 1
            
            profit_rate = stock_profit / stock_cost if stock_cost > 0 else 0
            print(f"  小计: 成本{stock_cost:.2f} 收益{stock_profit:.2f} "
                  f"收益率{profit_rate:.4f}({profit_rate*100:.2f}%)")
            print()
        
        print("="*60)
        print("手工计算结果:")
        print(f"总成本: {total_cost:,.2f}")
        print(f"总收益: {total_profit:,.2f}")
        if total_cost > 0:
            print(f"收益率: {total_profit/total_cost:.4f} ({total_profit/total_cost*100:.2f}%)")
        print(f"成功股票数: {success_stocks}")
        
        # 验证系统计算结果
        system_profit, system_success, system_cost = AnalyticsService._calculate_monthly_realized_profit_and_success(
            all_trades, 8, 2025
        )
        
        print("\n系统计算结果:")
        print(f"总成本: {system_cost:,.2f}")
        print(f"总收益: {system_profit:,.2f}")
        if system_cost > 0:
            print(f"收益率: {system_profit/system_cost:.4f} ({system_profit/system_cost*100:.2f}%)")
        print(f"成功股票数: {system_success}")

if __name__ == "__main__":
    complete_august_analysis()