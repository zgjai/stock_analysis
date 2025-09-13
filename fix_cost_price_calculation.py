#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复成本价计算逻辑 - 正确处理持仓周期
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from sqlalchemy import func, and_, or_
from extensions import db
from datetime import datetime
from typing import List, Dict, Any, Optional

def analyze_holding_periods(stock_code: str) -> List[Dict[str, Any]]:
    """分析股票的持仓周期"""
    
    # 获取所有交易记录，按时间排序
    trades = TradeRecord.query.filter(
        and_(
            TradeRecord.stock_code == stock_code,
            TradeRecord.is_corrected == False
        )
    ).order_by(TradeRecord.trade_date.asc()).all()
    
    if not trades:
        return []
    
    periods = []
    current_period = None
    running_quantity = 0
    
    for trade in trades:
        if trade.trade_type == 'buy':
            if current_period is None:
                # 开始新的持仓周期
                current_period = {
                    'start_date': trade.trade_date,
                    'end_date': None,
                    'buy_trades': [],
                    'sell_trades': [],
                    'total_buy_quantity': 0,
                    'total_sell_quantity': 0,
                    'total_cost': 0,
                    'is_active': True
                }
            
            current_period['buy_trades'].append(trade)
            current_period['total_buy_quantity'] += trade.quantity
            current_period['total_cost'] += trade.price * trade.quantity
            running_quantity += trade.quantity
            
        elif trade.trade_type == 'sell':
            if current_period is not None:
                current_period['sell_trades'].append(trade)
                current_period['total_sell_quantity'] += trade.quantity
                running_quantity -= trade.quantity
                
                # 如果卖完了，结束当前持仓周期
                if running_quantity <= 0:
                    current_period['end_date'] = trade.trade_date
                    current_period['is_active'] = False
                    periods.append(current_period)
                    current_period = None
                    running_quantity = 0
    
    # 如果还有未结束的持仓周期
    if current_period is not None:
        periods.append(current_period)
    
    return periods

def get_current_holding_cost_price(stock_code: str) -> Optional[float]:
    """获取当前持仓的正确成本价"""
    
    periods = analyze_holding_periods(stock_code)
    
    if not periods:
        return None
    
    # 找到最后一个活跃的持仓周期
    active_period = None
    for period in reversed(periods):
        if period['is_active']:
            active_period = period
            break
    
    if not active_period:
        return None
    
    # 计算当前持仓周期的成本价
    if active_period['total_buy_quantity'] > 0:
        return active_period['total_cost'] / active_period['total_buy_quantity']
    
    return None

def fix_600111_cost_price():
    """修复600111的成本价计算"""
    
    app = create_app()
    
    with app.app_context():
        stock_code = '600111'
        
        print(f"=== 修复 {stock_code} 北方稀土成本价计算 ===\n")
        
        # 分析持仓周期
        periods = analyze_holding_periods(stock_code)
        
        print(f"发现 {len(periods)} 个持仓周期:")
        for i, period in enumerate(periods, 1):
            status = "活跃" if period['is_active'] else "已结束"
            avg_price = period['total_cost'] / period['total_buy_quantity'] if period['total_buy_quantity'] > 0 else 0
            
            print(f"\n周期 {i} ({status}):")
            print(f"  开始日期: {period['start_date']}")
            print(f"  结束日期: {period['end_date'] or '未结束'}")
            print(f"  买入次数: {len(period['buy_trades'])}")
            print(f"  卖出次数: {len(period['sell_trades'])}")
            print(f"  总买入数量: {period['total_buy_quantity']}")
            print(f"  总卖出数量: {period['total_sell_quantity']}")
            print(f"  当前持仓: {period['total_buy_quantity'] - period['total_sell_quantity']}")
            print(f"  总成本: {period['total_cost']:.2f}")
            print(f"  平均成本价: {avg_price:.2f}")
            
            # 显示交易明细
            print(f"  买入明细:")
            for trade in period['buy_trades']:
                print(f"    {trade.trade_date} | 买入 {trade.quantity}股 @ {trade.price}")
            
            if period['sell_trades']:
                print(f"  卖出明细:")
                for trade in period['sell_trades']:
                    print(f"    {trade.trade_date} | 卖出 {trade.quantity}股 @ {trade.price}")
        
        # 获取正确的当前持仓成本价
        correct_cost_price = get_current_holding_cost_price(stock_code)
        
        print(f"\n=== 结论 ===")
        if correct_cost_price:
            print(f"✅ 当前持仓的正确成本价应该是: {correct_cost_price:.2f}")
            
            # 检查系统当前显示的成本价
            try:
                from services.review_service import ReviewService
                holdings = ReviewService.get_current_holdings()
                target_holding = None
                for holding in holdings:
                    if holding['stock_code'] == stock_code:
                        target_holding = holding
                        break
                
                if target_holding:
                    system_price = target_holding['avg_buy_price']
                    print(f"❌ 系统当前显示的成本价: {system_price:.2f}")
                    print(f"⚠️  差异: {abs(system_price - correct_cost_price):.2f}")
                    
                    if abs(system_price - correct_cost_price) > 0.01:
                        print(f"\n🔧 需要修复系统的成本价计算逻辑！")
                        print(f"   问题：系统把已结束的持仓周期也算进了成本价")
                        print(f"   解决方案：修改ReviewService.get_current_holdings()方法")
                    else:
                        print(f"✅ 系统成本价计算正确")
                else:
                    print(f"❌ 系统中未找到该股票的持仓记录")
            except Exception as e:
                print(f"❌ 获取系统持仓信息失败: {str(e)}")
        else:
            print(f"❌ 当前没有活跃的持仓")

if __name__ == '__main__':
    fix_600111_cost_price()