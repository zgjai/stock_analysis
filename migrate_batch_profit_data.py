#!/usr/bin/env python3
"""
分批止盈功能数据迁移工具
"""
import sys
import argparse
from datetime import datetime
from app import create_app
from utils.batch_profit_compatibility import BatchProfitCompatibilityHandler, LegacyDataHandler


def print_status_report():
    """打印兼容性状态报告"""
    print("=" * 60)
    print("分批止盈功能兼容性状态报告")
    print("=" * 60)
    
    try:
        status = BatchProfitCompatibilityHandler.get_compatibility_status()
        
        print(f"总交易记录数: {status['total_records']}")
        print(f"使用分批止盈的记录: {status['batch_profit_records']}")
        print(f"使用单一止盈的记录: {status['single_profit_records']}")
        print(f"未设置止盈标志的记录: {status['null_flag_records']}")
        print(f"止盈目标总数: {status['total_profit_targets']}")
        
        if status['inconsistent_records']:
            print("\n⚠️  发现数据不一致问题:")
            for issue in status['inconsistent_records']:
                print(f"  - {issue}")
        
        if status['is_compatible']:
            print("\n✅ 数据兼容性状态: 良好")
        else:
            print("\n❌ 数据兼容性状态: 需要修复")
        
    except Exception as e:
        print(f"❌ 获取状态报告失败: {e}")


def ensure_compatibility():
    """确保数据兼容性"""
    print("=" * 60)
    print("执行兼容性处理")
    print("=" * 60)
    
    try:
        result = BatchProfitCompatibilityHandler.ensure_compatibility()
        
        print(f"✅ 更新了 {result['updated_records']} 条记录")
        
        if result['warnings']:
            print("\n⚠️  警告:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if result['errors']:
            print("\n❌ 错误:")
            for error in result['errors']:
                print(f"  - {error}")
        
        if not result['errors']:
            print("\n✅ 兼容性处理完成")
        
    except Exception as e:
        print(f"❌ 兼容性处理失败: {e}")


def fix_inconsistencies():
    """修复数据不一致问题"""
    print("=" * 60)
    print("修复数据不一致问题")
    print("=" * 60)
    
    try:
        result = BatchProfitCompatibilityHandler.fix_data_inconsistencies()
        
        print(f"✅ 修复了 {result['fixed_records']} 条记录")
        
        if result['errors']:
            print("\n❌ 修复过程中的错误:")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['fixed_records'] > 0:
            print("\n✅ 数据不一致问题修复完成")
        else:
            print("\n✅ 没有发现需要修复的数据不一致问题")
        
    except Exception as e:
        print(f"❌ 修复数据不一致问题失败: {e}")


def migrate_single_to_batch(trade_id):
    """将单一止盈迁移为分批止盈"""
    print("=" * 60)
    print(f"迁移交易记录 {trade_id} 为分批止盈")
    print("=" * 60)
    
    try:
        result = BatchProfitCompatibilityHandler.migrate_single_to_batch_profit(trade_id)
        
        if result['success']:
            print(f"✅ {result['message']}")
            if 'migrated_target' in result:
                target = result['migrated_target']
                print(f"  - 止盈比例: {target['profit_ratio']:.2%}")
                print(f"  - 卖出比例: {target['sell_ratio']:.2%}")
                if target['target_price']:
                    print(f"  - 止盈价格: {target['target_price']:.2f}")
        else:
            print(f"❌ {result['message']}")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")


def migrate_batch_to_single(trade_id):
    """将分批止盈迁移为单一止盈"""
    print("=" * 60)
    print(f"迁移交易记录 {trade_id} 为单一止盈")
    print("=" * 60)
    
    try:
        result = BatchProfitCompatibilityHandler.migrate_batch_to_single_profit(trade_id)
        
        if result['success']:
            print(f"✅ {result['message']}")
            if 'migrated_data' in result:
                data = result['migrated_data']
                print(f"  - 止盈比例: {data['take_profit_ratio']:.2%}")
                print(f"  - 卖出比例: {data['sell_ratio']:.2%}")
        else:
            print(f"❌ {result['message']}")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='分批止盈功能数据迁移工具')
    parser.add_argument('action', choices=[
        'status', 'ensure', 'fix', 'migrate-to-batch', 'migrate-to-single'
    ], help='要执行的操作')
    parser.add_argument('--trade-id', type=int, help='交易记录ID（用于迁移操作）')
    
    args = parser.parse_args()
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        print(f"开始执行操作: {args.action}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if args.action == 'status':
            print_status_report()
        elif args.action == 'ensure':
            ensure_compatibility()
        elif args.action == 'fix':
            fix_inconsistencies()
        elif args.action == 'migrate-to-batch':
            if not args.trade_id:
                print("❌ 请提供 --trade-id 参数")
                sys.exit(1)
            migrate_single_to_batch(args.trade_id)
        elif args.action == 'migrate-to-single':
            if not args.trade_id:
                print("❌ 请提供 --trade-id 参数")
                sys.exit(1)
            migrate_batch_to_single(args.trade_id)
        
        print()
        print("操作完成")


if __name__ == '__main__':
    main()