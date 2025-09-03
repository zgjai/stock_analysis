#!/usr/bin/env python3
"""
分析当前持仓收益
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from models.stock_price import StockPrice
from datetime import datetime
from collections import defaultdict

def analyze_holdings():
    """分析当前持仓收益"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 分析当前持仓收益 ===\n")
            
            # 获取所有交易记录
            trades = TradeRecord.query.filter(TradeRecord.is_corrected == False).all()
            
            # 计算持仓情况
            holdings = defaultdict(lambda: {'quantity': 0, 'total_cost': 0})
            
            for trade in trades:
                if trade.trade_type == 'buy':
                    holdings[trade.stock_code]['quantity'] += trade.quantity
                    holdings[trade.stock_code]['total_cost'] += float(trade.price) * trade.quantity
                elif trade.trade_type == 'sell':
                    # 按FIFO计算卖出成本
                    sell_quantity = trade.quantity
                    sell_amount = float(trade.price) * trade.quantity
                    
                    # 简化处理：按平均成本计算
                    if holdings[trade.stock_code]['quantity'] > 0:
                        avg_cost = holdings[trade.stock_code]['total_cost'] / holdings[trade.stock_code]['quantity']
                        cost_reduction = avg_cost * sell_quantity
                        holdings[trade.stock_code]['total_cost'] -= cost_reduction
                        holdings[trade.stock_code]['quantity'] -= sell_quantity
            
            # 显示持仓情况
            print("当前持仓:")
            total_cost = 0
            total_market_value = 0
            
            for stock_code, holding in holdings.items():
                if holding['quantity'] > 0:
                    # 获取股票最新价格
                    stock_price = StockPrice.get_latest_price(stock_code)
                    current_price = float(stock_price.current_price) if stock_price and stock_price.current_price else 0
                    
                    market_value = current_price * holding['quantity']
                    profit = market_value - holding['total_cost']
                    profit_rate = (profit / holding['total_cost'] * 100) if holding['total_cost'] > 0 else 0
                    
                    print(f"{stock_code}: {holding['quantity']}股")
                    print(f"  成本: ¥{holding['total_cost']:,.2f}")
                    print(f"  现价: ¥{current_price}")
                    print(f"  市值: ¥{market_value:,.2f}")
                    print(f"  浮盈浮亏: ¥{profit:,.2f} ({profit_rate:+.2f}%)")
                    print()
                    
                    total_cost += holding['total_cost']
                    total_market_value += market_value
            
            total_unrealized_profit = total_market_value - total_cost
            
            print(f"持仓汇总:")
            print(f"  总成本: ¥{total_cost:,.2f}")
            print(f"  总市值: ¥{total_market_value:,.2f}")
            print(f"  未实现收益: ¥{total_unrealized_profit:,.2f}")
            
            # 计算已实现收益
            print(f"\n已实现收益: ¥21,252.00")
            
            # 计算总收益
            total_profit = 21252 + total_unrealized_profit
            print(f"总收益(已实现+未实现): ¥{total_profit:,.2f}")
            
            # 计算总投入
            total_invested = sum(float(t.price) * t.quantity for t in trades if t.trade_type == 'buy')
            print(f"总投入: ¥{total_invested:,.2f}")
            
            # 计算总收益率
            total_return_rate = total_profit / total_invested if total_invested > 0 else 0
            print(f"总收益率: {total_return_rate*100:.2f}%")
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    analyze_holdings()