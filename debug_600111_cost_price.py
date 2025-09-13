#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试600111北方稀土成本价显示问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from sqlalchemy import func, and_
from extensions import db

def debug_600111_cost_price():
    """调试600111北方稀土的成本价计算问题"""
    
    app = create_app()
    
    with app.app_context():
        stock_code = '600111'
        
        print(f"=== 调试 {stock_code} 北方稀土成本价问题 ===\n")
        
        # 1. 查询所有相关交易记录
        print("1. 查询所有交易记录:")
        all_trades = TradeRecord.query.filter(
            TradeRecord.stock_code == stock_code
        ).order_by(TradeRecord.trade_date.asc()).all()
        
        if not all_trades:
            print(f"❌ 未找到股票代码 {stock_code} 的任何交易记录")
            return
            
        print(f"找到 {len(all_trades)} 条交易记录:")
        for i, trade in enumerate(all_trades, 1):
            print(f"  {i}. {trade.trade_date} | {trade.trade_type} | 价格: {trade.price} | 数量: {trade.quantity} | 是否修正: {trade.is_corrected}")
        
        # 2. 查询有效的买入记录（未修正的）
        print("\n2. 查询有效买入记录（未修正）:")
        buy_trades = TradeRecord.query.filter(
            and_(
                TradeRecord.stock_code == stock_code,
                TradeRecord.trade_type == 'buy',
                TradeRecord.is_corrected == False
            )
        ).order_by(TradeRecord.trade_date.asc()).all()
        
        if not buy_trades:
            print("❌ 未找到有效的买入记录")
            return
            
        print(f"找到 {len(buy_trades)} 条有效买入记录:")
        total_cost = 0
        total_quantity = 0
        
        for i, trade in enumerate(buy_trades, 1):
            cost = trade.price * trade.quantity
            total_cost += cost
            total_quantity += trade.quantity
            print(f"  {i}. {trade.trade_date} | 价格: {trade.price} | 数量: {trade.quantity} | 成本: {cost}")
        
        # 3. 计算加权平均成本价
        if total_quantity > 0:
            calculated_avg_price = total_cost / total_quantity
            print(f"\n3. 手动计算加权平均成本价:")
            print(f"  总成本: {total_cost}")
            print(f"  总数量: {total_quantity}")
            print(f"  加权平均成本价: {calculated_avg_price:.2f}")
        else:
            print("\n3. ❌ 总数量为0，无法计算成本价")
            return
        
        # 4. 使用数据库查询计算成本价（与系统逻辑一致）
        print("\n4. 使用数据库查询计算成本价:")
        buy_record = db.session.query(
            TradeRecord.stock_code,
            TradeRecord.stock_name,
            func.sum(TradeRecord.quantity).label('total_buy_quantity'),
            (func.sum(TradeRecord.price * TradeRecord.quantity) / func.sum(TradeRecord.quantity)).label('avg_buy_price')
        ).filter(
            and_(
                TradeRecord.stock_code == stock_code,
                TradeRecord.trade_type == 'buy',
                TradeRecord.is_corrected == False
            )
        ).group_by(TradeRecord.stock_code, TradeRecord.stock_name).first()
        
        if buy_record:
            db_avg_price = float(buy_record.avg_buy_price)
            print(f"  数据库计算的平均成本价: {db_avg_price:.2f}")
            print(f"  手动计算与数据库计算差异: {abs(float(calculated_avg_price) - db_avg_price):.6f}")
        else:
            print("  ❌ 数据库查询未返回结果")
        
        # 5. 查询卖出记录
        print("\n5. 查询卖出记录:")
        sell_trades = TradeRecord.query.filter(
            and_(
                TradeRecord.stock_code == stock_code,
                TradeRecord.trade_type == 'sell',
                TradeRecord.is_corrected == False
            )
        ).order_by(TradeRecord.trade_date.asc()).all()
        
        total_sell_quantity = 0
        if sell_trades:
            print(f"找到 {len(sell_trades)} 条卖出记录:")
            for i, trade in enumerate(sell_trades, 1):
                total_sell_quantity += trade.quantity
                print(f"  {i}. {trade.trade_date} | 价格: {trade.price} | 数量: {trade.quantity}")
        else:
            print("  未找到卖出记录")
        
        # 6. 计算当前持仓
        current_quantity = total_quantity - total_sell_quantity
        print(f"\n6. 当前持仓计算:")
        print(f"  总买入数量: {total_quantity}")
        print(f"  总卖出数量: {total_sell_quantity}")
        print(f"  当前持仓数量: {current_quantity}")
        
        # 7. 使用ReviewService获取持仓信息
        print("\n7. 使用ReviewService获取持仓信息:")
        try:
            from services.review_service import ReviewService
            holdings = ReviewService.get_current_holdings()
            target_holding = None
            for holding in holdings:
                if holding['stock_code'] == stock_code:
                    target_holding = holding
                    break
            
            if target_holding:
                print(f"  系统显示的成本价: {target_holding['avg_buy_price']:.2f}")
                print(f"  系统显示的持仓数量: {target_holding['current_quantity']}")
                print(f"  系统显示的当前价格: {target_holding.get('current_price', 'N/A')}")
                
                # 检查差异
                if abs(target_holding['avg_buy_price'] - calculated_avg_price) > 0.01:
                    print(f"  ⚠️  成本价差异: 系统显示 {target_holding['avg_buy_price']:.2f} vs 计算值 {calculated_avg_price:.2f}")
                else:
                    print(f"  ✅ 成本价计算正确")
            else:
                print(f"  ❌ 在当前持仓中未找到股票 {stock_code}")
        except Exception as e:
            print(f"  ❌ 获取持仓信息失败: {str(e)}")
        
        # 8. 检查是否有修正记录
        print("\n8. 检查修正记录:")
        corrected_trades = TradeRecord.query.filter(
            and_(
                TradeRecord.stock_code == stock_code,
                TradeRecord.is_corrected == True
            )
        ).all()
        
        if corrected_trades:
            print(f"找到 {len(corrected_trades)} 条修正记录:")
            for i, trade in enumerate(corrected_trades, 1):
                print(f"  {i}. {trade.trade_date} | {trade.trade_type} | 价格: {trade.price} | 数量: {trade.quantity} | 修正原因: {getattr(trade, 'correction_reason', 'N/A')}")
        else:
            print("  未找到修正记录")
        
        print(f"\n=== 调试完成 ===")

if __name__ == '__main__':
    debug_600111_cost_price()