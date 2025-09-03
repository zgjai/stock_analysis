#!/usr/bin/env python3
"""
检查实际交易记录和真实收益
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from datetime import datetime
from collections import defaultdict

def check_actual_trades():
    """检查实际交易记录"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 检查实际交易记录和真实收益 ===\n")
            
            # 获取所有交易记录
            all_trades = TradeRecord.query.filter(TradeRecord.is_corrected == False).all()
            print(f"总交易记录数: {len(all_trades)}")
            
            if not all_trades:
                print("没有找到交易记录")
                return
            
            # 按日期排序显示所有交易
            all_trades.sort(key=lambda x: x.trade_date)
            print("\n所有交易记录:")
            print("日期\t\t股票代码\t交易类型\t数量\t价格\t\t金额")
            print("-" * 80)
            
            total_buy_amount = 0
            total_sell_amount = 0
            
            for trade in all_trades:
                amount = float(trade.price) * trade.quantity
                print(f"{trade.trade_date}\t{trade.stock_code}\t{trade.trade_type}\t{trade.quantity}\t{trade.price}\t\t{amount:,.2f}")
                
                if trade.trade_type == 'buy':
                    total_buy_amount += amount
                elif trade.trade_type == 'sell':
                    total_sell_amount += amount
            
            print("-" * 80)
            print(f"总买入金额: ¥{total_buy_amount:,.2f}")
            print(f"总卖出金额: ¥{total_sell_amount:,.2f}")
            print(f"简单差额: ¥{total_sell_amount - total_buy_amount:,.2f}")
            
            # 检查320万本金起始日期后的交易
            base_capital_start_date = datetime(2025, 8, 1)
            recent_trades = [t for t in all_trades if t.trade_date >= base_capital_start_date]
            
            print(f"\n320万本金起始日期({base_capital_start_date})后的交易:")
            print(f"交易记录数: {len(recent_trades)}")
            
            if recent_trades:
                recent_buy_amount = sum(float(t.price) * t.quantity for t in recent_trades if t.trade_type == 'buy')
                recent_sell_amount = sum(float(t.price) * t.quantity for t in recent_trades if t.trade_type == 'sell')
                
                print(f"买入金额: ¥{recent_buy_amount:,.2f}")
                print(f"卖出金额: ¥{recent_sell_amount:,.2f}")
                print(f"差额: ¥{recent_sell_amount - recent_buy_amount:,.2f}")
            
            # 按股票分组计算实际盈亏
            print("\n按股票分组的实际盈亏:")
            stock_trades = defaultdict(list)
            for trade in all_trades:
                stock_trades[trade.stock_code].append(trade)
            
            total_actual_profit = 0
            
            for stock_code, trades in stock_trades.items():
                trades.sort(key=lambda x: x.trade_date)
                
                buy_amount = sum(float(t.price) * t.quantity for t in trades if t.trade_type == 'buy')
                sell_amount = sum(float(t.price) * t.quantity for t in trades if t.trade_type == 'sell')
                profit = sell_amount - buy_amount
                
                print(f"{stock_code}: 买入¥{buy_amount:,.2f}, 卖出¥{sell_amount:,.2f}, 盈亏¥{profit:,.2f}")
                total_actual_profit += profit
            
            print(f"\n总实际盈亏: ¥{total_actual_profit:,.2f}")
            
            # 检查是否有持仓
            print("\n当前持仓情况:")
            current_holdings = defaultdict(int)
            for trade in all_trades:
                if trade.trade_type == 'buy':
                    current_holdings[trade.stock_code] += trade.quantity
                elif trade.trade_type == 'sell':
                    current_holdings[trade.stock_code] -= trade.quantity
            
            has_holdings = False
            for stock_code, quantity in current_holdings.items():
                if quantity > 0:
                    has_holdings = True
                    print(f"{stock_code}: 持仓{quantity}股")
            
            if not has_holdings:
                print("无持仓")
            
            print(f"\n结论: 实际总收益应该是 ¥{total_actual_profit:,.2f}，而不是40多万！")
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_actual_trades()