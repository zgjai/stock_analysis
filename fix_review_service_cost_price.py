#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复ReviewService中的成本价计算逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from sqlalchemy import func, and_
from extensions import db
from datetime import datetime
from typing import List, Dict, Any, Optional

def get_current_holding_periods(stock_code: str) -> Optional[Dict[str, Any]]:
    """获取股票当前活跃持仓周期的信息"""
    
    # 获取所有交易记录，按时间排序
    trades = TradeRecord.query.filter(
        and_(
            TradeRecord.stock_code == stock_code,
            TradeRecord.is_corrected == False
        )
    ).order_by(TradeRecord.trade_date.asc()).all()
    
    if not trades:
        return None
    
    # 分析持仓周期
    current_period = None
    running_quantity = 0
    
    for trade in trades:
        if trade.trade_type == 'buy':
            if current_period is None:
                # 开始新的持仓周期
                current_period = {
                    'stock_code': stock_code,
                    'stock_name': trade.stock_name,
                    'start_date': trade.trade_date,
                    'buy_trades': [],
                    'sell_trades': [],
                    'total_buy_quantity': 0,
                    'total_sell_quantity': 0,
                    'total_cost': 0
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
                    current_period = None
                    running_quantity = 0
    
    # 返回当前活跃的持仓周期
    if current_period is not None and running_quantity > 0:
        current_period['current_quantity'] = running_quantity
        current_period['avg_buy_price'] = current_period['total_cost'] / current_period['total_buy_quantity']
        return current_period
    
    return None

def get_corrected_current_holdings() -> List[Dict[str, Any]]:
    """获取修正后的当前持仓列表（按持仓周期计算成本价）"""
    
    # 获取所有有交易记录的股票代码
    stock_codes = db.session.query(TradeRecord.stock_code).filter(
        TradeRecord.is_corrected == False
    ).distinct().all()
    
    holdings = []
    
    for (stock_code,) in stock_codes:
        period = get_current_holding_periods(stock_code)
        
        if period and period['current_quantity'] > 0:
            holding = {
                'stock_code': period['stock_code'],
                'stock_name': period['stock_name'],
                'current_quantity': period['current_quantity'],
                'total_buy_quantity': period['total_buy_quantity'],
                'total_sell_quantity': period['total_sell_quantity'],
                'avg_buy_price': period['avg_buy_price'],
                'avg_price': period['avg_buy_price'],  # 兼容字段
                'first_buy_date': period['start_date'].isoformat(),
                'last_buy_date': period['buy_trades'][-1].trade_date.isoformat() if period['buy_trades'] else period['start_date'].isoformat()
            }
            holdings.append(holding)
    
    return holdings

def test_corrected_cost_price():
    """测试修正后的成本价计算"""
    
    app = create_app()
    
    with app.app_context():
        print("=== 测试修正后的成本价计算 ===\n")
        
        # 获取修正后的持仓列表
        corrected_holdings = get_corrected_current_holdings()
        
        print(f"找到 {len(corrected_holdings)} 个当前持仓:")
        
        for holding in corrected_holdings:
            print(f"\n股票: {holding['stock_code']} {holding['stock_name']}")
            print(f"  持仓数量: {holding['current_quantity']}")
            print(f"  修正后成本价: {holding['avg_buy_price']:.2f}")
            print(f"  首次买入日期: {holding['first_buy_date']}")
            print(f"  最后买入日期: {holding['last_buy_date']}")
            
            # 对比原系统的计算结果
            try:
                # 使用原系统的计算方法
                buy_record = db.session.query(
                    TradeRecord.stock_code,
                    TradeRecord.stock_name,
                    func.sum(TradeRecord.quantity).label('total_buy_quantity'),
                    (func.sum(TradeRecord.price * TradeRecord.quantity) / func.sum(TradeRecord.quantity)).label('avg_buy_price')
                ).filter(
                    and_(
                        TradeRecord.stock_code == holding['stock_code'],
                        TradeRecord.trade_type == 'buy',
                        TradeRecord.is_corrected == False
                    )
                ).group_by(TradeRecord.stock_code, TradeRecord.stock_name).first()
                
                if buy_record:
                    original_price = float(buy_record.avg_buy_price)
                    print(f"  原系统成本价: {original_price:.2f}")
                    
                    difference = abs(holding['avg_buy_price'] - original_price)
                    if difference > 0.01:
                        print(f"  ⚠️  差异: {difference:.2f} (修正后更准确)")
                    else:
                        print(f"  ✅ 两种计算方法结果一致")
                        
            except Exception as e:
                print(f"  ❌ 对比原系统计算失败: {str(e)}")

if __name__ == '__main__':
    test_corrected_cost_price()