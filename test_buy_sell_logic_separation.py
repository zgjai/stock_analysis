#!/usr/bin/env python3
"""
测试买入和卖出逻辑分离
验证系统是否正确区分买入和卖出的处理逻辑
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.trading_service import TradingService
from services.profit_taking_service import ProfitTakingService
from error_handlers import ValidationError
from extensions import db
from app import create_app
from config import config

def test_buy_sell_logic_separation():
    """测试买入和卖出逻辑分离"""
    print("🔍 测试买入和卖出逻辑分离")
    print("=" * 50)
    
    app = create_app(config['development'])
    
    with app.app_context():
        try:
            # 测试1: 买入记录可以设置止盈目标
            print("\n--- 测试1: 买入记录设置止盈目标 ---")
            buy_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 10.00,
                'quantity': 1000,
                'reason': '少妇B1战法',
                'use_batch_profit_taking': True,
                'profit_targets': [
                    {'profit_ratio': 0.10, 'sell_ratio': 0.50},
                    {'profit_ratio': 0.20, 'sell_ratio': 0.50}
                ]
            }
            
            try:
                buy_trade = TradingService.create_trade(buy_data)
                print(f"✅ 买入记录创建成功: ID={buy_trade.id}")
                print(f"   - 股票: {buy_trade.stock_code} {buy_trade.stock_name}")
                print(f"   - 类型: {buy_trade.trade_type}")
                print(f"   - 分批止盈: {buy_trade.use_batch_profit_taking}")
                
                # 检查止盈目标
                targets = ProfitTakingService.get_profit_targets(buy_trade.id)
                print(f"   - 止盈目标数量: {len(targets)}")
                for i, target in enumerate(targets, 1):
                    print(f"     目标{i}: 价格={target.target_price}, 止盈={float(target.profit_ratio)*100:.1f}%, 卖出={float(target.sell_ratio)*100:.1f}%")
                
            except Exception as e:
                print(f"❌ 买入记录创建失败: {e}")
                return False
            
            # 测试2: 卖出记录不能设置止盈目标
            print("\n--- 测试2: 卖出记录不能设置止盈目标 ---")
            sell_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'sell',
                'price': 11.50,
                'quantity': 500,
                'reason': '部分止盈',
                'use_batch_profit_taking': True,  # 这应该被拒绝
                'profit_targets': [
                    {'profit_ratio': 0.10, 'sell_ratio': 0.50}
                ]
            }
            
            try:
                sell_trade = TradingService.create_trade(sell_data)
                print(f"❌ 卖出记录不应该能设置止盈目标，但创建成功了: ID={sell_trade.id}")
                return False
            except ValidationError as e:
                if "只有买入记录才能设置分批止盈" in str(e):
                    print(f"✅ 正确拒绝卖出记录设置止盈: {e}")
                else:
                    print(f"❌ 错误类型的验证失败: {e}")
                    return False
            except Exception as e:
                print(f"❌ 意外错误: {e}")
                return False
            
            # 测试3: 创建普通卖出记录（不设置止盈）
            print("\n--- 测试3: 创建普通卖出记录 ---")
            normal_sell_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'sell',
                'price': 11.50,
                'quantity': 500,
                'reason': '部分止盈'
            }
            
            try:
                sell_trade = TradingService.create_trade(normal_sell_data)
                print(f"✅ 普通卖出记录创建成功: ID={sell_trade.id}")
                print(f"   - 股票: {sell_trade.stock_code} {sell_trade.stock_name}")
                print(f"   - 类型: {sell_trade.trade_type}")
                print(f"   - 分批止盈: {sell_trade.use_batch_profit_taking}")
                
                # 检查是否有止盈目标（应该没有）
                targets = ProfitTakingService.get_profit_targets(sell_trade.id)
                if len(targets) == 0:
                    print(f"   ✅ 卖出记录正确地没有止盈目标")
                else:
                    print(f"   ❌ 卖出记录不应该有止盈目标，但发现了{len(targets)}个")
                    return False
                
            except Exception as e:
                print(f"❌ 普通卖出记录创建失败: {e}")
                return False
            
            # 测试4: 尝试为已存在的卖出记录设置止盈目标
            print("\n--- 测试4: 为卖出记录设置止盈目标 ---")
            try:
                profit_targets = [
                    {'profit_ratio': 0.10, 'sell_ratio': 0.50}
                ]
                TradingService.update_trade_profit_targets(sell_trade.id, profit_targets)
                print(f"❌ 不应该能为卖出记录设置止盈目标")
                return False
            except ValidationError as e:
                if "只有买入记录才能设置止盈目标" in str(e):
                    print(f"✅ 正确拒绝为卖出记录设置止盈目标: {e}")
                else:
                    print(f"❌ 错误类型的验证失败: {e}")
                    return False
            except Exception as e:
                print(f"❌ 意外错误: {e}")
                return False
            
            # 测试5: 验证买入记录可以更新止盈目标
            print("\n--- 测试5: 更新买入记录的止盈目标 ---")
            try:
                new_targets = [
                    {'profit_ratio': 0.15, 'sell_ratio': 0.60},
                    {'profit_ratio': 0.30, 'sell_ratio': 0.40}
                ]
                updated_trade = TradingService.update_trade_profit_targets(buy_trade.id, new_targets)
                print(f"✅ 买入记录止盈目标更新成功")
                
                # 检查更新后的止盈目标
                targets = ProfitTakingService.get_profit_targets(buy_trade.id)
                print(f"   - 更新后止盈目标数量: {len(targets)}")
                for i, target in enumerate(targets, 1):
                    print(f"     目标{i}: 价格={target.target_price}, 止盈={float(target.profit_ratio)*100:.1f}%, 卖出={float(target.sell_ratio)*100:.1f}%")
                
            except Exception as e:
                print(f"❌ 更新买入记录止盈目标失败: {e}")
                return False
            
            print("\n" + "=" * 50)
            print("🎉 所有测试通过！买入和卖出逻辑正确分离")
            print("\n📋 验证结果:")
            print("✅ 买入记录可以设置和更新止盈目标")
            print("✅ 卖出记录不能设置止盈目标")
            print("✅ 卖出记录可以正常创建（不设置止盈）")
            print("✅ 系统正确区分买入和卖出的处理逻辑")
            
            return True
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            return False

if __name__ == '__main__':
    success = test_buy_sell_logic_separation()
    if not success:
        sys.exit(1)