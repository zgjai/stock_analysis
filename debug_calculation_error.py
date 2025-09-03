#!/usr/bin/env python3
"""
调试期望对比计算错误
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from services.expectation_comparison_service import ExpectationComparisonService
from models.trade_record import TradeRecord
from datetime import datetime
from collections import defaultdict

def debug_calculation_error():
    """调试计算错误"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 调试期望对比计算错误 ===\n")
            
            # 获取交易记录
            base_capital_start_date = datetime(2025, 8, 1)
            trades = TradeRecord.query.filter(
                TradeRecord.is_corrected == False,
                TradeRecord.trade_date >= base_capital_start_date
            ).all()
            
            print("1. 原始交易数据:")
            for trade in trades:
                print(f"   {trade.trade_date} {trade.stock_code} {trade.trade_type} {trade.quantity}股 @¥{trade.price}")
            
            # 调用服务的内部方法进行调试
            print("\n2. 调试_calculate_completed_trades_metrics方法:")
            completed_data = ExpectationComparisonService._calculate_completed_trades_metrics(trades)
            print(f"   加权平均收益率: {completed_data['weighted_return_rate']}")
            print(f"   完成交易数: {completed_data['completed_count']}")
            
            # 调试_calculate_stock_completed_trades方法
            print("\n3. 调试_calculate_stock_completed_trades方法:")
            stock_trades = defaultdict(list)
            for trade in trades:
                stock_trades[trade.stock_code].append(trade)
            
            for stock_code, stock_trade_list in stock_trades.items():
                print(f"\n   股票 {stock_code}:")
                stock_trade_list.sort(key=lambda x: x.trade_date)
                
                print("   交易序列:")
                for trade in stock_trade_list:
                    print(f"     {trade.trade_date} {trade.trade_type} {trade.quantity}股 @¥{trade.price}")
                
                completed = ExpectationComparisonService._calculate_stock_completed_trades(stock_trade_list)
                print(f"   完成交易数: {len(completed)}")
                
                total_cost = 0
                total_profit = 0
                
                for i, comp in enumerate(completed):
                    print(f"   完成交易{i+1}: 数量{comp['quantity']}, 买价¥{comp['buy_price']}, 卖价¥{comp['sell_price']}")
                    print(f"     成本¥{comp['cost']:.2f}, 收益¥{comp['profit']:.2f}, 持仓{comp['holding_days']}天")
                    total_cost += comp['cost']
                    total_profit += comp['profit']
                
                print(f"   总成本: ¥{total_cost:.2f}")
                print(f"   总收益: ¥{total_profit:.2f}")
                print(f"   收益率: {total_profit/total_cost*100:.2f}%" if total_cost > 0 else "   收益率: 0%")
            
            # 检查实际应该的计算
            print("\n4. 正确的计算应该是:")
            print("   买入: 31,100股 × ¥19.46 = ¥605,206")
            print("   卖出: 7,700股 × ¥22.22 = ¥171,094")
            print("   已实现收益: ¥171,094 - (7,700 × ¥19.46) = ¥171,094 - ¥149,842 = ¥21,252")
            print("   收益率: ¥21,252 / ¥149,842 = 14.18%")
            print("   但这只是部分卖出，还有23,400股持仓")
            print("   如果要计算总收益率，应该考虑未实现的浮盈浮亏")
            
            # 问题分析
            print("\n5. 问题分析:")
            print("   期望对比服务只计算了已完成的交易（已卖出部分）")
            print("   然后将这个收益率（14.18%）应用到320万本金上")
            print("   但这是错误的，因为:")
            print("   - 实际投入的资金是¥605,206，不是320万")
            print("   - 只卖出了部分股票，还有大量持仓")
            print("   - 应该显示实际的收益金额¥21,252，而不是标准化后的金额")
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_calculation_error()