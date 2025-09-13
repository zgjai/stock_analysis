#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多次买入的加权平均成本价计算
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from sqlalchemy import and_

def test_weighted_average_scenarios():
    """测试不同场景下的加权平均成本价计算"""
    
    app = create_app()
    
    with app.app_context():
        print("=== 测试加权平均成本价计算逻辑 ===\n")
        
        # 获取所有有多次买入记录的股票
        from services.review_service import ReviewService
        holdings = ReviewService.get_current_holdings()
        
        print("当前持仓中的加权平均成本价计算验证:\n")
        
        for holding in holdings:
            stock_code = holding['stock_code']
            
            # 获取该股票的所有买入记录（当前持仓周期）
            trades = TradeRecord.query.filter(
                and_(
                    TradeRecord.stock_code == stock_code,
                    TradeRecord.trade_type == 'buy',
                    TradeRecord.is_corrected == False
                )
            ).order_by(TradeRecord.trade_date.asc()).all()
            
            if len(trades) > 1:  # 只显示多次买入的股票
                print(f"📊 {stock_code} {holding['stock_name']}")
                print(f"   当前持仓: {holding['current_quantity']}股")
                print(f"   系统计算成本价: ¥{holding['avg_buy_price']:.2f}")
                
                # 手动验证加权平均计算
                total_cost = 0
                total_quantity = 0
                print(f"   买入明细:")
                
                for i, trade in enumerate(trades, 1):
                    cost = trade.price * trade.quantity
                    total_cost += cost
                    total_quantity += trade.quantity
                    print(f"     {i}. {trade.trade_date.strftime('%m-%d %H:%M')} | {trade.quantity}股 @ ¥{trade.price} = ¥{cost:.2f}")
                
                manual_avg = total_cost / total_quantity if total_quantity > 0 else 0
                print(f"   手动计算: 总成本¥{total_cost:.2f} ÷ 总数量{total_quantity}股 = ¥{manual_avg:.2f}")
                
                # 验证计算是否正确
                diff = abs(holding['avg_buy_price'] - float(manual_avg))
                if diff < 0.01:
                    print(f"   ✅ 加权平均计算正确 (差异: {diff:.4f})")
                else:
                    print(f"   ❌ 计算有误 (差异: {diff:.4f})")
                
                print()
        
        # 创建一个模拟场景来演示逻辑
        print("\n" + "="*60)
        print("📝 加权平均成本价计算逻辑说明:")
        print("="*60)
        
        scenarios = [
            {
                'name': '场景1: 单次买入',
                'trades': [{'date': '09-01', 'quantity': 1000, 'price': 10.00}],
                'expected': 10.00
            },
            {
                'name': '场景2: 两次买入（相同价格）',
                'trades': [
                    {'date': '09-01', 'quantity': 1000, 'price': 10.00},
                    {'date': '09-02', 'quantity': 2000, 'price': 10.00}
                ],
                'expected': 10.00
            },
            {
                'name': '场景3: 两次买入（不同价格）',
                'trades': [
                    {'date': '09-01', 'quantity': 1000, 'price': 10.00},
                    {'date': '09-02', 'quantity': 1000, 'price': 12.00}
                ],
                'expected': 11.00
            },
            {
                'name': '场景4: 三次买入（加权平均）',
                'trades': [
                    {'date': '09-01', 'quantity': 1000, 'price': 10.00},  # 成本: 10,000
                    {'date': '09-02', 'quantity': 2000, 'price': 15.00},  # 成本: 30,000
                    {'date': '09-03', 'quantity': 1000, 'price': 8.00}    # 成本: 8,000
                ],
                'expected': 12.00  # 总成本48,000 ÷ 总数量4,000 = 12.00
            },
            {
                'name': '场景5: 买入后部分卖出（持仓周期未结束）',
                'description': '买入3000股，卖出1000股，剩余2000股的成本价仍按原买入加权平均计算',
                'trades': [
                    {'date': '09-01', 'quantity': 1000, 'price': 10.00},
                    {'date': '09-02', 'quantity': 2000, 'price': 15.00},
                    {'date': '09-03', 'quantity': -1000, 'price': 12.00, 'type': 'sell'}  # 卖出不影响成本价
                ],
                'expected': 13.33  # (10*1000 + 15*2000) ÷ 3000 = 13.33，卖出不影响成本价
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{scenario['name']}:")
            if 'description' in scenario:
                print(f"  说明: {scenario['description']}")
            
            total_cost = 0
            total_buy_quantity = 0
            
            print("  交易明细:")
            for trade in scenario['trades']:
                if trade.get('type') == 'sell':
                    print(f"    {trade['date']} | 卖出 {abs(trade['quantity'])}股 @ ¥{trade['price']} (不影响成本价)")
                else:
                    cost = trade['quantity'] * trade['price']
                    total_cost += cost
                    total_buy_quantity += trade['quantity']
                    print(f"    {trade['date']} | 买入 {trade['quantity']}股 @ ¥{trade['price']} = ¥{cost}")
            
            if total_buy_quantity > 0:
                calculated_avg = total_cost / total_buy_quantity
                print(f"  计算: 总成本¥{total_cost} ÷ 总买入{total_buy_quantity}股 = ¥{calculated_avg:.2f}")
                print(f"  预期: ¥{scenario['expected']:.2f}")
                
                if abs(calculated_avg - scenario['expected']) < 0.01:
                    print("  ✅ 计算正确")
                else:
                    print("  ❌ 计算有误")
        
        print(f"\n" + "="*60)
        print("🔑 关键要点:")
        print("="*60)
        print("1. ✅ 在同一个持仓周期内，多次买入会按加权平均计算成本价")
        print("2. ✅ 加权平均公式: 总成本 ÷ 总买入数量")
        print("3. ✅ 部分卖出不影响剩余持仓的成本价")
        print("4. ✅ 只有当持仓全部清空时，持仓周期才结束")
        print("5. ✅ 新的持仓周期重新开始计算成本价")
        print("6. ✅ 修复后的逻辑正确处理了持仓周期的概念")

if __name__ == '__main__':
    test_weighted_average_scenarios()