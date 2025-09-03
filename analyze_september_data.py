#!/usr/bin/env python3
"""
分析2025年9月月度收益数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from services.analytics_service import AnalyticsService
from datetime import datetime
from collections import defaultdict

def analyze_september_data():
    """分析2025年9月的月度收益数据"""
    app = create_app()
    
    with app.app_context():
        print("=== 2025年9月月度收益数据分析 ===\n")
        
        # 获取9月份的交易记录
        september_start = datetime(2025, 9, 1)
        september_end = datetime(2025, 9, 30, 23, 59, 59)
        
        september_trades = TradeRecord.query.filter(
            TradeRecord.trade_date >= september_start,
            TradeRecord.trade_date <= september_end
        ).order_by(TradeRecord.trade_date, TradeRecord.stock_code).all()
        
        print("1. 9月份交易记录:")
        print("-" * 80)
        print(f"{'日期':<12} {'股票代码':<10} {'类型':<6} {'数量':<8} {'价格':<10} {'金额':<12}")
        print("-" * 80)
        
        september_buy_amount = 0
        september_sell_amount = 0
        buy_stocks = set()
        sell_stocks = set()
        
        for trade in september_trades:
            amount = float(trade.quantity * trade.price)
            if trade.trade_type == 'buy':
                september_buy_amount += amount
                buy_stocks.add(trade.stock_code)
            else:
                september_sell_amount += amount
                sell_stocks.add(trade.stock_code)
                
            print(f"{trade.trade_date.strftime('%Y-%m-%d'):<12} "
                  f"{trade.stock_code:<10} "
                  f"{trade.trade_type:<6} "
                  f"{trade.quantity:<8} "
                  f"{trade.price:<10.2f} "
                  f"{amount:<12.2f}")
        
        print("-" * 80)
        print(f"9月份交易记录总数: {len(september_trades)}")
        print(f"9月份买入总额: {september_buy_amount:,.2f} 元")
        print(f"9月份卖出总额: {september_sell_amount:,.2f} 元")
        print(f"简单差额: {september_sell_amount - september_buy_amount:,.2f} 元")
        print(f"买入股票数: {len(buy_stocks)}")
        print(f"卖出股票数: {len(sell_stocks)}")
        print()
        
        # 获取系统计算的9月份月度统计
        try:
            system_profit, system_success, system_cost = AnalyticsService._calculate_monthly_realized_profit_and_success(
                TradeRecord.query.all(), 9, 2025
            )
            
            print("2. 系统计算的9月份统计:")
            print("-" * 50)
            print(f"月度收益: {system_profit:,.2f} 元")
            print(f"投入成本: {system_cost:,.2f} 元")
            if system_cost > 0:
                print(f"收益率: {system_profit/system_cost:.4f} ({system_profit/system_cost*100:.2f}%)")
            else:
                print("收益率: 无数据（成本为0）")
            print(f"成功股票数: {system_success}")
            print()
            
        except Exception as e:
            print(f"获取系统统计时出错: {e}")
        
        # 分析9月份买入的股票
        if buy_stocks:
            print("3. 9月份买入股票详细分析:")
            print("-" * 50)
            
            all_trades = TradeRecord.query.order_by(TradeRecord.trade_date).all()
            stock_trades = defaultdict(list)
            for trade in all_trades:
                stock_trades[trade.stock_code].append(trade)
            
            total_september_profit = 0
            total_september_cost = 0
            
            for stock_code in sorted(buy_stocks):
                print(f"\n股票 {stock_code}:")
                
                # 获取该股票的所有交易
                stock_trade_list = stock_trades[stock_code]
                
                # 显示9月份的买入记录
                september_buys = [t for t in stock_trade_list if 
                                t.trade_type == 'buy' and 
                                september_start <= t.trade_date <= september_end]
                
                print(f"  9月买入记录: {len(september_buys)} 笔")
                for buy in september_buys:
                    print(f"    {buy.trade_date.strftime('%m-%d')} 买入 {buy.quantity}股 @{buy.price}")
                
                # 计算9月份买入产生的收益
                monthly_profits = AnalyticsService._get_monthly_buy_total_profits(
                    stock_trade_list, september_start, september_end
                )
                
                stock_profit = 0
                stock_cost = 0
                
                print("  收益明细:")
                for profit_item in monthly_profits:
                    stock_profit += profit_item['total_profit']
                    stock_cost += profit_item['cost']
                    
                    if profit_item['type'] == 'realized':
                        print(f"    已实现: 成本{profit_item['cost']:.2f} 收益{profit_item['total_profit']:.2f}")
                    else:
                        print(f"    未实现: 成本{profit_item['cost']:.2f} 浮盈{profit_item['total_profit']:.2f}")
                
                total_september_profit += stock_profit
                total_september_cost += stock_cost
                
                if stock_cost > 0:
                    print(f"  小计: 成本{stock_cost:.2f} 收益{stock_profit:.2f} "
                          f"收益率{stock_profit/stock_cost:.4f}({stock_profit/stock_cost*100:.2f}%)")
            
            print(f"\n手工计算汇总:")
            print(f"9月买入总成本: {total_september_cost:,.2f}")
            print(f"9月买入总收益: {total_september_profit:,.2f}")
            if total_september_cost > 0:
                print(f"9月收益率: {total_september_profit/total_september_cost:.4f} "
                      f"({total_september_profit/total_september_cost*100:.2f}%)")
        
        else:
            print("3. 9月份没有买入任何股票")
            print("这解释了为什么系统计算的成本为0")
        
        # 检查数据异常
        print("\n4. 数据异常检查:")
        print("-" * 50)
        
        if len(september_trades) < 10:
            print("⚠️  9月份交易记录较少，可能数据不完整")
        
        if september_buy_amount == 0:
            print("⚠️  9月份没有买入交易，月度收益率无法计算")
        
        if september_sell_amount > september_buy_amount * 10:
            print("⚠️  卖出金额远大于买入金额，可能在卖出之前月份的持仓")
        
        # 检查是否有跨月的交易逻辑问题
        print("\n5. 跨月交易分析:")
        print("-" * 50)
        
        # 检查9月卖出的股票是否在8月买入
        august_trades = TradeRecord.query.filter(
            TradeRecord.trade_date >= datetime(2025, 8, 1),
            TradeRecord.trade_date <= datetime(2025, 8, 31)
        ).all()
        
        august_buy_stocks = set()
        for trade in august_trades:
            if trade.trade_type == 'buy':
                august_buy_stocks.add(trade.stock_code)
        
        september_sell_from_august = sell_stocks & august_buy_stocks
        
        if september_sell_from_august:
            print(f"9月卖出的股票中，有{len(september_sell_from_august)}只是8月买入的:")
            for stock in sorted(september_sell_from_august):
                print(f"  {stock}")
            print("这些卖出收益应该归属到8月的收益中")
        
        print(f"\n9月只卖出不买入的股票: {sell_stocks - buy_stocks}")
        print("这种情况下，9月的月度收益主要来自8月买入股票的收益变化")

if __name__ == "__main__":
    analyze_september_data()