#!/usr/bin/env python3
"""
创建测试用的传统止盈记录
"""
from app import create_app
from extensions import db
from models.trade_record import TradeRecord
from datetime import datetime


def create_legacy_record():
    """创建一个传统止盈记录用于测试"""
    app = create_app()
    
    with app.app_context():
        try:
            # 创建一个传统的买入记录
            trade_data = {
                'stock_code': '000001',
                'stock_name': '测试股票',
                'trade_type': 'buy',
                'price': 10.00,
                'quantity': 1000,
                'trade_date': datetime.now(),
                'reason': '技术分析',
                'notes': '测试用传统止盈记录',
                'stop_loss_price': 9.00,
                'take_profit_ratio': 0.15,  # 15%
                'sell_ratio': 0.50,         # 50%
                'use_batch_profit_taking': False
            }
            
            # 直接创建记录，绕过服务层的分批止盈处理
            trade = TradeRecord(**trade_data)
            trade.save()
            
            print(f"✅ 创建了测试用传统止盈记录，ID: {trade.id}")
            print(f"   股票代码: {trade.stock_code}")
            print(f"   止盈比例: {float(trade.take_profit_ratio):.2%}")
            print(f"   卖出比例: {float(trade.sell_ratio):.2%}")
            print(f"   使用分批止盈: {trade.use_batch_profit_taking}")
            
            return trade.id
            
        except Exception as e:
            print(f"❌ 创建测试记录失败: {e}")
            return None


if __name__ == '__main__':
    create_legacy_record()