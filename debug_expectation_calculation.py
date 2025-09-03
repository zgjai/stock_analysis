#!/usr/bin/env python3
"""
调试期望对比计算问题
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from services.expectation_comparison_service import ExpectationComparisonService
from models.trade_record import TradeRecord
from datetime import datetime
import json

def debug_expectation_calculation():
    """调试期望对比计算"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 调试期望对比计算 ===\n")
            
            # 1. 检查交易记录数据
            print("1. 检查交易记录数据:")
            base_capital_start_date = datetime(2025, 8, 1)
            trades = TradeRecord.query.filter(
                TradeRecord.is_corrected == False,
                TradeRecord.trade_date >= base_capital_start_date
            ).all()
            
            print(f"   - 320万本金起始日期: {base_capital_start_date}")
            print(f"   - 符合条件的交易记录数: {len(trades)}")
            
            if trades:
                print(f"   - 最早交易日期: {min(t.trade_date for t in trades)}")
                print(f"   - 最晚交易日期: {max(t.trade_date for t in trades)}")
                
                # 统计买卖交易
                buy_trades = [t for t in trades if t.trade_type == 'buy']
                sell_trades = [t for t in trades if t.trade_type == 'sell']
                print(f"   - 买入交易: {len(buy_trades)}笔")
                print(f"   - 卖出交易: {len(sell_trades)}笔")
                
                # 计算总成本和总收益
                total_buy_amount = sum(float(t.price) * t.quantity for t in buy_trades)
                total_sell_amount = sum(float(t.price) * t.quantity for t in sell_trades)
                print(f"   - 总买入金额: ¥{total_buy_amount:,.2f}")
                print(f"   - 总卖出金额: ¥{total_sell_amount:,.2f}")
                print(f"   - 简单差额: ¥{total_sell_amount - total_buy_amount:,.2f}")
            
            print("\n2. 计算期望指标:")
            expectation = ExpectationComparisonService.calculate_expectation_metrics(3200000)
            print(f"   - 期望收益率: {expectation['return_rate']:.4f} ({expectation['return_rate']*100:.2f}%)")
            print(f"   - 期望收益金额: ¥{expectation['return_amount']:,.2f}")
            print(f"   - 期望持仓天数: {expectation['holding_days']:.2f}天")
            print(f"   - 期望胜率: {expectation['success_rate']:.4f} ({expectation['success_rate']*100:.2f}%)")
            
            print("\n3. 计算实际指标:")
            actual = ExpectationComparisonService.calculate_actual_metrics(trades, 3200000)
            print(f"   - 实际收益率: {actual['return_rate']:.4f} ({actual['return_rate']*100:.2f}%)")
            print(f"   - 实际收益金额: ¥{actual['return_amount']:,.2f}")
            print(f"   - 实际持仓天数: {actual['holding_days']:.2f}天")
            print(f"   - 实际胜率: {actual['success_rate']:.4f} ({actual['success_rate']*100:.2f}%)")
            print(f"   - 总交易数: {actual['total_trades']}")
            print(f"   - 完成交易数: {actual['completed_trades']}")
            
            print("\n4. 详细分析已完成交易:")
            completed_data = ExpectationComparisonService._calculate_completed_trades_metrics(trades)
            print(f"   - 加权平均收益率: {completed_data['weighted_return_rate']:.4f}")
            print(f"   - 平均持仓天数: {completed_data['avg_holding_days']:.2f}")
            print(f"   - 胜率: {completed_data['success_rate']:.4f}")
            print(f"   - 完成交易数: {completed_data['completed_count']}")
            
            # 分析具体的完成交易
            print("\n5. 分析具体完成交易:")
            from collections import defaultdict
            stock_trades = defaultdict(list)
            for trade in trades:
                stock_trades[trade.stock_code].append(trade)
            
            total_cost = 0
            total_profit = 0
            all_completed = []
            
            for stock_code, stock_trade_list in stock_trades.items():
                stock_trade_list.sort(key=lambda x: x.trade_date)
                completed = ExpectationComparisonService._calculate_stock_completed_trades(stock_trade_list)
                
                if completed:
                    stock_cost = sum(c['cost'] for c in completed)
                    stock_profit = sum(c['profit'] for c in completed)
                    print(f"   - {stock_code}: {len(completed)}笔完成交易, 成本¥{stock_cost:,.2f}, 收益¥{stock_profit:,.2f}, 收益率{stock_profit/stock_cost*100:.2f}%")
                    
                    total_cost += stock_cost
                    total_profit += stock_profit
                    all_completed.extend(completed)
            
            print(f"\n   总计: 成本¥{total_cost:,.2f}, 收益¥{total_profit:,.2f}, 收益率{total_profit/total_cost*100:.2f}%")
            print(f"   基于320万本金的标准化收益: ¥{3200000 * (total_profit/total_cost):,.2f}")
            
            print("\n6. 获取完整对比数据:")
            comparison_data = ExpectationComparisonService.get_expectation_comparison('all', 3200000)
            print(json.dumps(comparison_data, indent=2, default=str, ensure_ascii=False))
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_expectation_calculation()