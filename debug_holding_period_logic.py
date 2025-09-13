#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试持仓周期逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def debug_holding_period_logic():
    """调试持仓周期逻辑"""
    
    app = create_app()
    
    with app.app_context():
        from services.review_service import HoldingService
        
        stock_code = '600111'
        print(f"=== 调试 {stock_code} 持仓周期逻辑 ===\n")
        
        # 使用我们修复后的方法获取当前持仓周期
        period = HoldingService._get_current_holding_period(stock_code)
        
        if period:
            print("✅ 找到当前活跃持仓周期:")
            print(f"  股票代码: {period['stock_code']}")
            print(f"  股票名称: {period['stock_name']}")
            print(f"  周期开始日期: {period['start_date']}")
            print(f"  当前持仓数量: {period['current_quantity']}")
            print(f"  总买入数量: {period['total_buy_quantity']}")
            print(f"  总卖出数量: {period['total_sell_quantity']}")
            print(f"  总成本: ¥{period['total_cost']:.2f}")
            print(f"  平均成本价: ¥{period['avg_buy_price']:.2f}")
            
            print(f"\n当前持仓周期的买入明细:")
            for i, trade in enumerate(period['buy_trades'], 1):
                cost = trade.price * trade.quantity
                print(f"  {i}. {trade.trade_date} | {trade.quantity}股 @ ¥{trade.price} = ¥{cost:.2f}")
            
            if period['sell_trades']:
                print(f"\n当前持仓周期的卖出明细:")
                for i, trade in enumerate(period['sell_trades'], 1):
                    print(f"  {i}. {trade.trade_date} | {trade.quantity}股 @ ¥{trade.price}")
            else:
                print(f"\n当前持仓周期无卖出记录")
            
            # 验证计算
            manual_avg = period['total_cost'] / period['total_buy_quantity']
            print(f"\n验证计算:")
            print(f"  手动计算: ¥{period['total_cost']:.2f} ÷ {period['total_buy_quantity']}股 = ¥{manual_avg:.2f}")
            print(f"  系统计算: ¥{period['avg_buy_price']:.2f}")
            
            diff = abs(manual_avg - period['avg_buy_price'])
            if diff < 0.01:
                print(f"  ✅ 计算正确 (差异: {diff:.4f})")
            else:
                print(f"  ❌ 计算有误 (差异: {diff:.4f})")
                
        else:
            print("❌ 未找到当前活跃持仓周期")

if __name__ == '__main__':
    debug_holding_period_logic()