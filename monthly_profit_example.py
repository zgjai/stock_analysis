#!/usr/bin/env python3
"""
月度收益计算具体例子演示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from services.analytics_service import AnalyticsService
from datetime import datetime

def demonstrate_with_example():
    """用具体例子演示月度收益计算"""
    app = create_app()
    
    with app.app_context():
        print("=== 月度收益计算具体例子演示 ===\n")
        
        # 选择一只在8月有买入的股票作为例子
        august_start = datetime(2025, 8, 1)
        august_end = datetime(2025, 8, 31, 23, 59, 59)
        
        # 找一只有代表性的股票
        example_stock = "000776"  # 从之前的分析中选择
        
        # 获取该股票的所有交易记录
        stock_trades = TradeRecord.query.filter(
            TradeRecord.stock_code == example_stock
        ).order_by(TradeRecord.trade_date).all()
        
        print(f"以股票 {example_stock} 为例:")
        print("-" * 50)
        
        print("该股票的所有交易记录:")
        for i, trade in enumerate(stock_trades, 1):
            print(f"{i}. {trade.trade_date.strftime('%Y-%m-%d')} "
                  f"{trade.trade_type} {trade.quantity}股 "
                  f"@{trade.price}元 = {float(trade.quantity * trade.price):.2f}元")
        
        print()
        
        # 计算8月份买入产生的收益
        monthly_profits = AnalyticsService._get_monthly_buy_total_profits(
            stock_trades, august_start, august_end
        )
        
        print("8月份买入产生的收益计算:")
        print("-" * 50)
        
        total_cost = 0
        total_profit = 0
        
        for i, profit_item in enumerate(monthly_profits, 1):
            total_cost += profit_item['cost']
            total_profit += profit_item['total_profit']
            
            if profit_item['type'] == 'realized':
                print(f"{i}. 已实现收益:")
                print(f"   买入日期: {profit_item['buy_date'].strftime('%Y-%m-%d')}")
                print(f"   卖出日期: {profit_item['sell_date'].strftime('%Y-%m-%d')}")
                print(f"   交易数量: {profit_item['quantity']}股")
                print(f"   买入价格: {profit_item['buy_price']:.2f}元")
                print(f"   卖出价格: {profit_item['sell_price']:.2f}元")
                print(f"   投入成本: {profit_item['cost']:.2f}元")
                print(f"   卖出收入: {profit_item['revenue']:.2f}元")
                print(f"   实现收益: {profit_item['total_profit']:.2f}元")
            else:
                print(f"{i}. 未实现收益（浮盈浮亏）:")
                print(f"   买入日期: {profit_item['buy_date'].strftime('%Y-%m-%d')}")
                print(f"   持有数量: {profit_item['quantity']}股")
                print(f"   买入价格: {profit_item['buy_price']:.2f}元")
                print(f"   当前价格: {profit_item['current_price']:.2f}元")
                print(f"   投入成本: {profit_item['cost']:.2f}元")
                print(f"   市场价值: {profit_item['market_value']:.2f}元")
                print(f"   浮动收益: {profit_item['total_profit']:.2f}元")
            print()
        
        print("汇总:")
        print("-" * 30)
        print(f"8月买入总成本: {total_cost:.2f}元")
        print(f"8月买入总收益: {total_profit:.2f}元")
        if total_cost > 0:
            profit_rate = total_profit / total_cost
            print(f"该股票收益率: {profit_rate:.4f} ({profit_rate*100:.2f}%)")
        
        print("\n" + "="*60)
        print("关键理解点:")
        print("-" * 30)
        print("1. 只计算8月份买入的股票产生的收益")
        print("2. 不管这些股票什么时候卖出")
        print("3. 包括已卖出部分的实际收益")
        print("4. 包括仍持有部分的浮盈浮亏")
        print("5. 这样能准确反映8月投资决策的效果")
        
        # 对比简单计算方法
        print("\n对比简单计算方法:")
        print("-" * 30)
        
        august_trades = [t for t in stock_trades if august_start <= t.trade_date <= august_end]
        august_buy = sum(float(t.quantity * t.price) for t in august_trades if t.trade_type == 'buy')
        august_sell = sum(float(t.quantity * t.price) for t in august_trades if t.trade_type == 'sell')
        
        print(f"8月该股票买入金额: {august_buy:.2f}元")
        print(f"8月该股票卖出金额: {august_sell:.2f}元")
        print(f"简单差额: {august_sell - august_buy:.2f}元")
        print(f"买入归属法收益: {total_profit:.2f}元")
        print(f"差异: {total_profit - (august_sell - august_buy):.2f}元")
        print("\n差异原因:")
        print("• 简单差额没有考虑持仓的浮盈浮亏")
        print("• 简单差额可能包含了之前买入股票的卖出收益")

if __name__ == "__main__":
    demonstrate_with_example()