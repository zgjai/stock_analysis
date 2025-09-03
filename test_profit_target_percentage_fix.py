#!/usr/bin/env python3
"""
测试止盈目标百分比处理修复
"""

import sys
import os
sys.path.append('.')

from app import create_app
from extensions import db
from services.profit_taking_service import ProfitTakingService
from models.trade_record import TradeRecord
from models.profit_taking_target import ProfitTakingTarget
from error_handlers import ValidationError
import json

def test_percentage_handling():
    """测试百分比处理逻辑"""
    app = create_app()
    
    with app.app_context():
        print("=== 测试止盈目标百分比处理修复 ===\n")
        
        # 创建测试交易记录
        from datetime import date
        test_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=10.00,
            quantity=1000,
            trade_date=date(2025, 1, 1),
            reason='测试',
            use_batch_profit_taking=True
        )
        test_trade.save()
        print(f"创建测试交易记录: ID={test_trade.id}, 买入价格={test_trade.price}")
        
        # 测试1: 大于10%的止盈比例
        print("\n--- 测试1: 大于10%的止盈比例 ---")
        targets_data_1 = [
            {
                'profit_ratio': 20.0,  # 20%
                'sell_ratio': 50.0,    # 50%
                'sequence_order': 1
            },
            {
                'profit_ratio': 50.0,  # 50%
                'sell_ratio': 30.0,    # 30%
                'sequence_order': 2
            }
        ]
        
        try:
            targets_1 = ProfitTakingService.create_profit_targets(test_trade.id, targets_data_1)
            print(f"✓ 成功创建{len(targets_1)}个止盈目标")
            for target in targets_1:
                print(f"  目标{target.sequence_order}: 止盈比例={float(target.profit_ratio)*100:.2f}%, 卖出比例={float(target.sell_ratio)*100:.2f}%")
        except ValidationError as e:
            print(f"✗ 验证失败: {e.message}")
            if hasattr(e, 'details'):
                print(f"  详细错误: {e.details}")
        
        # 测试2: 大于100%的卖出比例
        print("\n--- 测试2: 大于100%的卖出比例 ---")
        targets_data_2 = [
            {
                'profit_ratio': 15.0,   # 15%
                'sell_ratio': 120.0,    # 120%
                'sequence_order': 1
            }
        ]
        
        # 先清除之前的目标
        ProfitTakingTarget.delete_by_trade_record(test_trade.id)
        
        try:
            targets_2 = ProfitTakingService.create_profit_targets(test_trade.id, targets_data_2)
            print(f"✓ 成功创建{len(targets_2)}个止盈目标")
            for target in targets_2:
                print(f"  目标{target.sequence_order}: 止盈比例={float(target.profit_ratio)*100:.2f}%, 卖出比例={float(target.sell_ratio)*100:.2f}%")
        except ValidationError as e:
            print(f"✗ 验证失败: {e.message}")
            if hasattr(e, 'details'):
                print(f"  详细错误: {e.details}")
        
        # 测试3: 百分比格式转换
        print("\n--- 测试3: 百分比格式转换 ---")
        targets_data_3 = [
            {
                'profit_ratio': 25.5,   # 25.5%
                'sell_ratio': 33.33,    # 33.33%
                'sequence_order': 1
            }
        ]
        
        # 先清除之前的目标
        ProfitTakingTarget.delete_by_trade_record(test_trade.id)
        
        try:
            targets_3 = ProfitTakingService.create_profit_targets(test_trade.id, targets_data_3)
            print(f"✓ 成功创建{len(targets_3)}个止盈目标")
            for target in targets_3:
                stored_profit = float(target.profit_ratio)
                stored_sell = float(target.sell_ratio)
                print(f"  目标{target.sequence_order}:")
                print(f"    输入: 止盈比例=25.5%, 卖出比例=33.33%")
                print(f"    存储: 止盈比例={stored_profit:.4f} (小数), 卖出比例={stored_sell:.4f} (小数)")
                print(f"    显示: 止盈比例={stored_profit*100:.2f}%, 卖出比例={stored_sell*100:.2f}%")
                
                # 验证转换正确性
                expected_profit = 25.5 / 100
                expected_sell = 33.33 / 100
                if abs(stored_profit - expected_profit) < 0.0001 and abs(stored_sell - expected_sell) < 0.0001:
                    print("    ✓ 百分比转换正确")
                else:
                    print("    ✗ 百分比转换错误")
                    
        except ValidationError as e:
            print(f"✗ 验证失败: {e.message}")
            if hasattr(e, 'details'):
                print(f"  详细错误: {e.details}")
        
        # 测试4: 边界值测试
        print("\n--- 测试4: 边界值测试 ---")
        
        # 测试最大值
        targets_data_4 = [
            {
                'profit_ratio': 1000.0,  # 1000% (最大值)
                'sell_ratio': 1000.0,    # 1000% (最大值)
                'sequence_order': 1
            }
        ]
        
        # 先清除之前的目标
        ProfitTakingTarget.delete_by_trade_record(test_trade.id)
        
        try:
            targets_4 = ProfitTakingService.create_profit_targets(test_trade.id, targets_data_4)
            print(f"✓ 边界值测试通过: 1000%止盈比例和1000%卖出比例")
        except ValidationError as e:
            print(f"✗ 边界值测试失败: {e.message}")
        
        # 测试超出最大值
        targets_data_5 = [
            {
                'profit_ratio': 1001.0,  # 1001% (超出最大值)
                'sell_ratio': 50.0,
                'sequence_order': 1
            }
        ]
        
        # 先清除之前的目标
        ProfitTakingTarget.delete_by_trade_record(test_trade.id)
        
        try:
            targets_5 = ProfitTakingService.create_profit_targets(test_trade.id, targets_data_5)
            print(f"✗ 应该拒绝超出最大值的输入")
        except ValidationError as e:
            print(f"✓ 正确拒绝超出最大值的输入: {e.message}")
        
        # 清理测试数据
        ProfitTakingTarget.delete_by_trade_record(test_trade.id)
        test_trade.delete()
        
        print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_percentage_handling()