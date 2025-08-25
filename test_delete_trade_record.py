#!/usr/bin/env python3
"""
测试删除交易记录功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.trade_record import TradeRecord
from models.profit_taking_target import ProfitTakingTarget
from datetime import datetime, date


def test_delete_trade_record():
    """测试删除交易记录功能"""
    app = create_app()
    
    with app.app_context():
        try:
            print("创建测试交易记录...")
            
            # 创建一个测试交易记录
            trade_record = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=10.50,
                quantity=1000,
                trade_date=date.today(),
                reason='测试',
                notes='测试删除功能'
            )
            
            db.session.add(trade_record)
            db.session.commit()
            
            trade_id = trade_record.id
            print(f"创建的交易记录ID: {trade_id}")
            
            # 创建关联的止盈目标
            profit_target = ProfitTakingTarget(
                trade_record_id=trade_id,
                target_price=12.00,
                profit_ratio=0.1429,  # (12.00 - 10.50) / 10.50
                sell_ratio=0.5,
                sequence_order=1
            )
            
            db.session.add(profit_target)
            db.session.commit()
            
            print("创建了关联的止盈目标")
            
            # 验证记录存在
            existing_trade = TradeRecord.query.get(trade_id)
            existing_targets = ProfitTakingTarget.query.filter_by(trade_record_id=trade_id).all()
            
            print(f"交易记录存在: {existing_trade is not None}")
            print(f"止盈目标数量: {len(existing_targets)}")
            
            # 测试删除功能
            print("\n开始删除交易记录...")
            
            # 删除交易记录（应该级联删除止盈目标）
            db.session.delete(existing_trade)
            db.session.commit()
            
            print("删除操作完成")
            
            # 验证删除结果
            deleted_trade = TradeRecord.query.get(trade_id)
            remaining_targets = ProfitTakingTarget.query.filter_by(trade_record_id=trade_id).all()
            
            print(f"交易记录已删除: {deleted_trade is None}")
            print(f"剩余止盈目标数量: {len(remaining_targets)}")
            
            if deleted_trade is None and len(remaining_targets) == 0:
                print("✓ 删除交易记录功能测试成功")
                return True
            else:
                print("✗ 删除交易记录功能测试失败")
                return False
                
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    success = test_delete_trade_record()
    if not success:
        sys.exit(1)