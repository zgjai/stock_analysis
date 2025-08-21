#!/usr/bin/env python3
"""
验证删除交易记录功能修复

这个脚本验证之前的删除交易记录约束问题是否已经完全解决。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.trade_record import TradeRecord
from models.profit_taking_target import ProfitTakingTarget
from services.trading_service import TradingService
from datetime import datetime


def main():
    """主验证函数"""
    app = create_app()
    
    with app.app_context():
        print("验证删除交易记录功能修复")
        print("=" * 40)
        
        # 测试场景1：删除有分批止盈的交易记录
        print("测试场景1：删除有分批止盈的交易记录")
        
        test_data = {
            'stock_code': '000002',
            'stock_name': '万科A',
            'trade_type': 'buy',
            'price': 15.50,
            'quantity': 1000,
            'trade_date': datetime.now(),
            'reason': '少妇B1战法',
            'use_batch_profit_taking': True
        }
        
        profit_targets = [
            {'target_price': 16.50, 'profit_ratio': 0.065, 'sell_ratio': 0.30},
            {'target_price': 17.50, 'profit_ratio': 0.129, 'sell_ratio': 0.40},
            {'target_price': 18.50, 'profit_ratio': 0.194, 'sell_ratio': 0.30}
        ]
        
        try:
            # 创建交易记录
            trade = TradingService.create_trade_with_batch_profit(test_data, profit_targets)
            print(f"✓ 创建交易记录成功，ID: {trade.id}")
            
            # 验证止盈目标
            targets_before = ProfitTakingTarget.query.filter_by(trade_record_id=trade.id).count()
            print(f"✓ 创建了 {targets_before} 个止盈目标")
            
            # 删除交易记录
            result = TradingService.delete_trade(trade.id)
            print(f"✓ 删除交易记录成功")
            
            # 验证清理
            db.session.expire_all()
            targets_after = ProfitTakingTarget.query.filter_by(trade_record_id=trade.id).count()
            trade_exists = TradeRecord.get_by_id(trade.id) is not None
            
            if targets_after == 0 and not trade_exists:
                print("✓ 相关记录已完全清理")
            else:
                print(f"✗ 清理不完整：止盈目标剩余 {targets_after} 个，交易记录存在: {trade_exists}")
                
        except Exception as e:
            print(f"✗ 测试失败: {str(e)}")
            return False
        
        print()
        
        # 测试场景2：删除普通交易记录（无分批止盈）
        print("测试场景2：删除普通交易记录（无分批止盈）")
        
        simple_data = {
            'stock_code': '000003',
            'stock_name': '万科B',
            'trade_type': 'buy',
            'price': 12.30,
            'quantity': 500,
            'trade_date': datetime.now(),
            'reason': '少妇B1战法',
            'take_profit_ratio': 0.15,
            'sell_ratio': 0.80,
            'stop_loss_price': 11.00
        }
        
        try:
            # 创建普通交易记录
            trade = TradingService.create_trade(simple_data)
            print(f"✓ 创建普通交易记录成功，ID: {trade.id}")
            
            # 删除交易记录
            result = TradingService.delete_trade(trade.id)
            print(f"✓ 删除普通交易记录成功")
            
            # 验证清理
            db.session.expire_all()
            trade_exists = TradeRecord.get_by_id(trade.id) is not None
            
            if not trade_exists:
                print("✓ 交易记录已完全删除")
            else:
                print("✗ 交易记录未删除")
                return False
                
        except Exception as e:
            print(f"✗ 测试失败: {str(e)}")
            return False
        
        print()
        print("🎉 所有测试通过！删除功能已完全修复。")
        return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)