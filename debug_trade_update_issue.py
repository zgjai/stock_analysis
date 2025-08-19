#!/usr/bin/env python3
"""
调试交易记录更新问题
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.trade_record import TradeRecord
from services.trading_service import TradingService
import json
import traceback

def debug_trade_update():
    """调试交易记录更新问题"""
    app = create_app()
    
    with app.app_context():
        try:
            # 获取最近的交易记录
            trades = TradeRecord.query.order_by(TradeRecord.id.desc()).limit(5).all()
            
            print("=== 最近的交易记录 ===")
            for trade in trades:
                print(f"ID: {trade.id}, 股票: {trade.stock_code}, 类型: {trade.trade_type}")
                print(f"价格: {trade.price}, 数量: {trade.quantity}")
                print(f"分批止盈: {trade.use_batch_profit_taking}")
                print("---")
            
            if not trades:
                print("没有找到交易记录")
                return
            
            # 测试更新第一个记录
            test_trade = trades[0]
            print(f"\n=== 测试更新交易记录 ID: {test_trade.id} ===")
            
            # 模拟前端发送的更新数据
            update_data = {
                'price': 10.50,
                'quantity': 1000,
                'notes': '测试更新'
            }
            
            print(f"更新数据: {update_data}")
            
            # 尝试更新
            try:
                updated_trade = TradingService.update_trade(test_trade.id, update_data)
                print(f"更新成功: {updated_trade.to_dict()}")
            except Exception as e:
                print(f"更新失败: {str(e)}")
                print(f"错误类型: {type(e).__name__}")
                traceback.print_exc()
                
                # 尝试直接更新模型
                print("\n=== 尝试直接更新模型 ===")
                try:
                    test_trade.price = 10.50
                    test_trade.quantity = 1000
                    test_trade.notes = '直接更新测试'
                    test_trade.save()
                    print("直接更新成功")
                except Exception as e2:
                    print(f"直接更新也失败: {str(e2)}")
                    traceback.print_exc()
        
        except Exception as e:
            print(f"调试过程出错: {str(e)}")
            traceback.print_exc()

if __name__ == '__main__':
    debug_trade_update()