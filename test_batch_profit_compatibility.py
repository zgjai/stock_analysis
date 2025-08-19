#!/usr/bin/env python3
"""
分批止盈功能兼容性测试脚本
"""
from app import create_app
from extensions import db
from models.trade_record import TradeRecord
from models.profit_taking_target import ProfitTakingTarget
from services.trading_service import TradingService
from services.profit_taking_service import ProfitTakingService
from utils.batch_profit_compatibility import BatchProfitCompatibilityHandler, LegacyDataHandler
from datetime import datetime


def test_compatibility_handler():
    """测试兼容性处理器"""
    print("=" * 60)
    print("测试兼容性处理器")
    print("=" * 60)
    
    try:
        # 1. 测试状态报告
        print("1. 获取兼容性状态报告...")
        status = BatchProfitCompatibilityHandler.get_compatibility_status()
        print(f"   总记录数: {status['total_records']}")
        print(f"   分批止盈记录: {status['batch_profit_records']}")
        print(f"   单一止盈记录: {status['single_profit_records']}")
        print(f"   未设置标志记录: {status['null_flag_records']}")
        print(f"   兼容性状态: {'良好' if status['is_compatible'] else '需要修复'}")
        
        # 2. 测试兼容性确保
        print("\n2. 执行兼容性处理...")
        result = BatchProfitCompatibilityHandler.ensure_compatibility()
        print(f"   更新记录数: {result['updated_records']}")
        print(f"   警告数: {len(result['warnings'])}")
        print(f"   错误数: {len(result['errors'])}")
        
        # 3. 测试数据修复
        print("\n3. 修复数据不一致问题...")
        fix_result = BatchProfitCompatibilityHandler.fix_data_inconsistencies()
        print(f"   修复记录数: {fix_result['fixed_records']}")
        print(f"   错误数: {len(fix_result['errors'])}")
        
        print("\n✅ 兼容性处理器测试完成")
        
    except Exception as e:
        print(f"❌ 兼容性处理器测试失败: {e}")


def test_legacy_data_handler():
    """测试遗留数据处理器"""
    print("=" * 60)
    print("测试遗留数据处理器")
    print("=" * 60)
    
    try:
        # 查找一个使用传统止盈的记录
        legacy_trade = TradeRecord.query.filter(
            TradeRecord.use_batch_profit_taking == False,
            TradeRecord.take_profit_ratio.isnot(None)
        ).first()
        
        if legacy_trade:
            print(f"1. 测试遗留数据获取 (记录ID: {legacy_trade.id})...")
            legacy_data = LegacyDataHandler.get_legacy_profit_data(legacy_trade)
            if legacy_data:
                print(f"   止盈比例: {legacy_data['take_profit_ratio']}")
                print(f"   卖出比例: {legacy_data['sell_ratio']}")
                print(f"   预期收益率: {legacy_data['expected_profit_ratio']}")
            else:
                print("   该记录使用分批止盈，无遗留数据")
            
            print("\n2. 测试向后兼容性确保...")
            trade_dict = legacy_trade.to_dict()
            compatible_dict = LegacyDataHandler.ensure_backward_compatibility(trade_dict)
            print(f"   包含传统字段: {'take_profit_ratio' in compatible_dict}")
            
            print("\n3. 测试遗留格式转换...")
            legacy_format = LegacyDataHandler.convert_to_legacy_format(legacy_trade)
            print(f"   移除分批止盈字段: {'use_batch_profit_taking' not in legacy_format}")
            
        else:
            print("   没有找到使用传统止盈的记录")
        
        print("\n✅ 遗留数据处理器测试完成")
        
    except Exception as e:
        print(f"❌ 遗留数据处理器测试失败: {e}")


def test_migration_functions():
    """测试迁移功能"""
    print("=" * 60)
    print("测试迁移功能")
    print("=" * 60)
    
    try:
        # 查找一个可以迁移的记录
        single_profit_trade = TradeRecord.query.filter(
            TradeRecord.use_batch_profit_taking == False,
            TradeRecord.trade_type == 'buy',
            TradeRecord.take_profit_ratio.isnot(None),
            TradeRecord.sell_ratio.isnot(None)
        ).first()
        
        if single_profit_trade:
            trade_id = single_profit_trade.id
            print(f"1. 测试单一止盈迁移为分批止盈 (记录ID: {trade_id})...")
            
            # 记录原始数据
            original_take_profit = float(single_profit_trade.take_profit_ratio)
            original_sell_ratio = float(single_profit_trade.sell_ratio)
            
            # 执行迁移
            result = BatchProfitCompatibilityHandler.migrate_single_to_batch_profit(trade_id)
            if result['success']:
                print(f"   ✅ {result['message']}")
                
                # 验证迁移结果
                db.session.refresh(single_profit_trade)
                if single_profit_trade.use_batch_profit_taking:
                    targets = ProfitTakingService.get_profit_targets(trade_id)
                    if targets and len(targets) == 1:
                        target = targets[0]
                        print(f"   验证: 止盈比例 {float(target.profit_ratio):.4f} == {original_take_profit:.4f}")
                        print(f"   验证: 卖出比例 {float(target.sell_ratio):.4f} == {original_sell_ratio:.4f}")
                
                print("\n2. 测试分批止盈迁移回单一止盈...")
                # 迁移回单一止盈
                back_result = BatchProfitCompatibilityHandler.migrate_batch_to_single_profit(trade_id)
                if back_result['success']:
                    print(f"   ✅ {back_result['message']}")
                    
                    # 验证迁移结果
                    db.session.refresh(single_profit_trade)
                    if not single_profit_trade.use_batch_profit_taking:
                        print(f"   验证: 恢复止盈比例 {float(single_profit_trade.take_profit_ratio):.4f}")
                        print(f"   验证: 恢复卖出比例 {float(single_profit_trade.sell_ratio):.4f}")
                else:
                    print(f"   ❌ {back_result['message']}")
            else:
                print(f"   ❌ {result['message']}")
        else:
            print("   没有找到可以迁移的单一止盈记录")
        
        print("\n✅ 迁移功能测试完成")
        
    except Exception as e:
        print(f"❌ 迁移功能测试失败: {e}")


def test_service_compatibility():
    """测试服务层兼容性"""
    print("=" * 60)
    print("测试服务层兼容性")
    print("=" * 60)
    
    try:
        # 测试获取交易记录的兼容性
        trades = TradeRecord.query.limit(5).all()
        
        for trade in trades:
            print(f"测试记录 {trade.id} (分批止盈: {trade.use_batch_profit_taking})...")
            
            # 测试 to_dict 方法
            trade_dict = trade.to_dict()
            print(f"   包含 use_batch_profit_taking: {'use_batch_profit_taking' in trade_dict}")
            print(f"   包含传统字段: {'take_profit_ratio' in trade_dict}")
            
            # 测试服务层获取
            service_dict = TradingService.get_trade_with_profit_targets(trade.id)
            print(f"   服务层兼容性: {'take_profit_ratio' in service_dict}")
            
            if trade.use_batch_profit_taking:
                print(f"   分批止盈目标数: {len(service_dict.get('profit_targets', []))}")
            
            print()
        
        print("✅ 服务层兼容性测试完成")
        
    except Exception as e:
        print(f"❌ 服务层兼容性测试失败: {e}")


def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("开始分批止盈功能兼容性测试")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 运行所有测试
        test_compatibility_handler()
        print()
        test_legacy_data_handler()
        print()
        test_migration_functions()
        print()
        test_service_compatibility()
        
        print()
        print("所有兼容性测试完成")


if __name__ == '__main__':
    main()