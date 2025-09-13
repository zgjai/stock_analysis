#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面测试成本价计算逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_comprehensive_cost_calculation():
    """全面测试成本价计算逻辑"""
    
    app = create_app()
    
    with app.app_context():
        from services.review_service import ReviewService, HoldingService
        
        print("=== 全面测试成本价计算逻辑 ===\n")
        
        # 获取所有当前持仓
        holdings = ReviewService.get_current_holdings()
        
        print(f"找到 {len(holdings)} 个当前持仓，验证成本价计算:\n")
        
        for holding in holdings:
            stock_code = holding['stock_code']
            print(f"📊 {stock_code} {holding['stock_name']}")
            print(f"   系统显示成本价: ¥{holding['avg_buy_price']:.2f}")
            print(f"   当前持仓数量: {holding['current_quantity']}股")
            
            # 获取当前持仓周期的详细信息
            period = HoldingService._get_current_holding_period(stock_code)
            
            if period:
                print(f"   持仓周期开始: {period['start_date'].strftime('%Y-%m-%d %H:%M')}")
                print(f"   周期内买入次数: {len(period['buy_trades'])}")
                
                if len(period['buy_trades']) > 1:
                    print(f"   📝 多次买入的加权平均计算:")
                    total_cost = 0
                    total_quantity = 0
                    
                    for i, trade in enumerate(period['buy_trades'], 1):
                        cost = trade.price * trade.quantity
                        total_cost += cost
                        total_quantity += trade.quantity
                        print(f"      {i}. {trade.trade_date.strftime('%m-%d %H:%M')} | {trade.quantity}股 @ ¥{trade.price} = ¥{cost:.2f}")
                    
                    manual_avg = total_cost / total_quantity
                    print(f"   ✅ 加权平均: ¥{total_cost:.2f} ÷ {total_quantity}股 = ¥{manual_avg:.2f}")
                    
                    # 验证系统计算
                    diff = abs(holding['avg_buy_price'] - float(manual_avg))
                    if diff < 0.01:
                        print(f"   ✅ 系统计算正确 (差异: {diff:.4f})")
                    else:
                        print(f"   ❌ 系统计算有误 (差异: {diff:.4f})")
                        
                elif len(period['buy_trades']) == 1:
                    trade = period['buy_trades'][0]
                    print(f"   📝 单次买入:")
                    print(f"      {trade.trade_date.strftime('%m-%d %H:%M')} | {trade.quantity}股 @ ¥{trade.price}")
                    print(f"   ✅ 成本价 = 买入价 = ¥{trade.price}")
                    
                    if abs(holding['avg_buy_price'] - float(trade.price)) < 0.01:
                        print(f"   ✅ 系统计算正确")
                    else:
                        print(f"   ❌ 系统计算有误")
                
                # 检查是否有卖出记录
                if period['sell_trades']:
                    print(f"   📝 周期内卖出记录: {len(period['sell_trades'])}次")
                    for i, trade in enumerate(period['sell_trades'], 1):
                        print(f"      {i}. {trade.trade_date.strftime('%m-%d %H:%M')} | 卖出{trade.quantity}股 @ ¥{trade.price}")
                    print(f"   💡 卖出不影响剩余持仓的成本价计算")
                
            else:
                print(f"   ❌ 未找到持仓周期信息")
            
            print()
        
        print("="*60)
        print("🔑 加权平均成本价计算逻辑总结:")
        print("="*60)
        print("✅ 1. 按持仓周期计算：只计算当前活跃持仓周期内的买入记录")
        print("✅ 2. 加权平均公式：总成本 ÷ 总买入数量")
        print("✅ 3. 多次买入：自动按金额加权平均")
        print("✅ 4. 部分卖出：不影响剩余持仓的成本价")
        print("✅ 5. 持仓清空：持仓周期结束，重新开始计算")
        print("✅ 6. 新买入：开始新的持仓周期，重新计算成本价")
        
        print(f"\n📈 实际应用示例:")
        print(f"   - 如果你分3次买入同一股票：1000股@10元，2000股@12元，1000股@8元")
        print(f"   - 总成本：10000 + 24000 + 8000 = 42000元")
        print(f"   - 总数量：1000 + 2000 + 1000 = 4000股")
        print(f"   - 加权平均成本价：42000 ÷ 4000 = 10.5元")
        print(f"   - 即使后来卖出1000股，剩余3000股的成本价仍然是10.5元")

if __name__ == '__main__':
    test_comprehensive_cost_calculation()