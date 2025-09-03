#!/usr/bin/env python3
"""
历史交易数据同步脚本
用于从命令行执行数据同步和初始化操作
"""
import sys
import os
import argparse
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from services.data_sync_service import DataSyncService
from services.historical_trade_service import HistoricalTradeService


def setup_logging():
    """设置日志"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/data_sync.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)


def print_result(result, operation_name):
    """打印操作结果"""
    print(f"\n=== {operation_name} 结果 ===")
    print(f"操作时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"操作成功: {'是' if result.get('success', False) else '否'}")
    
    if 'total_identified' in result:
        print(f"识别的完整交易数: {result['total_identified']}")
    if 'created_count' in result:
        print(f"创建记录数: {result['created_count']}")
    if 'updated_count' in result:
        print(f"更新记录数: {result['updated_count']}")
    if 'skipped_count' in result:
        print(f"跳过记录数: {result['skipped_count']}")
    if 'error_count' in result:
        print(f"错误记录数: {result['error_count']}")
    
    if result.get('errors'):
        print("\n错误详情:")
        for error in result['errors']:
            print(f"  - {error}")
    
    if 'sync_type' in result:
        print(f"同步类型: {result['sync_type']}")
    
    print("=" * 50)


def print_integrity_check(result):
    """打印完整性检查结果"""
    print(f"\n=== 数据完整性检查结果 ===")
    print(f"检查时间: {result['check_time']}")
    print(f"数据有效性: {'有效' if result['is_valid'] else '无效'}")
    print(f"严重程度: {result['severity']}")
    print(f"交易记录总数: {result['total_trade_records']}")
    print(f"历史交易记录总数: {result['total_historical_trades']}")
    print(f"孤立买入记录数: {result['orphaned_buys_count']}")
    print(f"重复记录数: {result['duplicate_records_count']}")
    
    if result['issues']:
        print("\n发现的问题:")
        for issue in result['issues']:
            print(f"  ❌ {issue}")
    
    if result['warnings']:
        print("\n警告信息:")
        for warning in result['warnings']:
            print(f"  ⚠️  {warning}")
    
    if result['statistics']:
        stats = result['statistics']
        print(f"\n统计信息:")
        print(f"  - 盈利交易数: {stats.get('profitable_trades', 0)}")
        print(f"  - 亏损交易数: {stats.get('loss_trades', 0)}")
        print(f"  - 胜率: {stats.get('win_rate', 0):.2f}%")
        print(f"  - 数据覆盖率: {stats.get('data_coverage_ratio', 0):.2f}")
    
    print("=" * 50)


def initialize_data(args):
    """初始化历史数据"""
    logger = setup_logging()
    logger.info("开始初始化历史数据")
    
    try:
        result = DataSyncService.initialize_historical_data(
            force_regenerate=args.force
        )
        
        print_result(result, "数据初始化")
        
        if 'integrity_check' in result:
            print_integrity_check(result['integrity_check'])
        
        return result['success']
        
    except Exception as e:
        logger.error(f"初始化历史数据失败: {str(e)}")
        print(f"❌ 初始化失败: {str(e)}")
        return False


def incremental_sync(args):
    """增量同步"""
    logger = setup_logging()
    logger.info("开始增量同步")
    
    try:
        result = DataSyncService.incremental_sync()
        print_result(result, "增量同步")
        return result['success']
        
    except Exception as e:
        logger.error(f"增量同步失败: {str(e)}")
        print(f"❌ 增量同步失败: {str(e)}")
        return False


def check_integrity(args):
    """检查数据完整性"""
    logger = setup_logging()
    logger.info("开始数据完整性检查")
    
    try:
        result = DataSyncService.check_data_integrity()
        print_integrity_check(result)
        
        if args.output:
            # 保存结果到文件
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            print(f"✅ 检查结果已保存到: {args.output}")
        
        return result['is_valid']
        
    except Exception as e:
        logger.error(f"数据完整性检查失败: {str(e)}")
        print(f"❌ 完整性检查失败: {str(e)}")
        return False


def repair_integrity(args):
    """修复数据完整性"""
    logger = setup_logging()
    logger.info("开始修复数据完整性")
    
    try:
        repair_options = {
            'remove_duplicates': args.remove_duplicates,
            'fix_inconsistencies': args.fix_inconsistencies,
            'update_references': args.update_references
        }
        
        result = DataSyncService.repair_data_integrity(repair_options)
        
        print(f"\n=== 数据完整性修复结果 ===")
        print(f"修复时间: {result['repair_time']}")
        print(f"修复成功: {'是' if result['success'] else '否'}")
        
        print("\n修复操作:")
        for action in result['repair_actions']:
            print(f"  - {action['action']}: ", end="")
            if 'removed_count' in action:
                print(f"删除 {action['removed_count']} 条记录")
            elif 'fixed_count' in action:
                print(f"修复 {action['fixed_count']} 条记录")
            else:
                print("完成")
        
        print("\n修复后完整性检查:")
        print_integrity_check(result['post_repair_check'])
        
        return result['success']
        
    except Exception as e:
        logger.error(f"修复数据完整性失败: {str(e)}")
        print(f"❌ 修复失败: {str(e)}")
        return False


def get_status(args):
    """获取同步状态"""
    logger = setup_logging()
    logger.info("获取同步状态")
    
    try:
        status = DataSyncService.get_sync_status()
        
        print(f"\n=== 同步状态 ===")
        print(f"状态时间: {status['status_time']}")
        print(f"最后同步时间: {status['last_sync_time'] or '从未同步'}")
        print(f"需要同步: {'是' if status['needs_sync'] else '否'}")
        
        if status['sync_statistics']:
            stats = status['sync_statistics']
            print(f"\n同步统计:")
            print(f"  - 总同步次数: {stats.get('total_syncs', 0)}")
            print(f"  - 成功次数: {stats.get('successful_syncs', 0)}")
            print(f"  - 失败次数: {stats.get('failed_syncs', 0)}")
            if stats.get('last_error'):
                print(f"  - 最后错误: {stats['last_error']}")
        
        print("=" * 30)
        return True
        
    except Exception as e:
        logger.error(f"获取同步状态失败: {str(e)}")
        print(f"❌ 获取状态失败: {str(e)}")
        return False


def get_statistics(args):
    """获取交易统计"""
    logger = setup_logging()
    logger.info("获取交易统计")
    
    try:
        stats = HistoricalTradeService.get_trade_statistics()
        
        print(f"\n=== 历史交易统计 ===")
        print(f"总交易数: {stats['total_trades']}")
        print(f"盈利交易数: {stats['profitable_trades']}")
        print(f"亏损交易数: {stats['loss_trades']}")
        print(f"胜率: {stats['win_rate']}%")
        print(f"总投入: ¥{stats['total_investment']:,.2f}")
        print(f"总收益: ¥{stats['total_return']:,.2f}")
        print(f"总收益率: {stats['overall_return_rate']}%")
        print(f"平均收益率: {stats['avg_return_rate']}%")
        print(f"最高收益率: {stats['max_return_rate']}%")
        print(f"最低收益率: {stats['min_return_rate']}%")
        print(f"平均持仓天数: {stats['avg_holding_days']} 天")
        print(f"最长持仓天数: {stats['max_holding_days']} 天")
        print(f"最短持仓天数: {stats['min_holding_days']} 天")
        
        if args.output:
            # 保存统计到文件
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
            print(f"✅ 统计结果已保存到: {args.output}")
        
        print("=" * 40)
        return True
        
    except Exception as e:
        logger.error(f"获取交易统计失败: {str(e)}")
        print(f"❌ 获取统计失败: {str(e)}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='历史交易数据同步工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 初始化命令
    init_parser = subparsers.add_parser('init', help='初始化历史数据')
    init_parser.add_argument('--force', action='store_true', 
                           help='强制重新生成所有数据（删除现有数据）')
    init_parser.set_defaults(func=initialize_data)
    
    # 增量同步命令
    sync_parser = subparsers.add_parser('sync', help='增量同步数据')
    sync_parser.set_defaults(func=incremental_sync)
    
    # 完整性检查命令
    check_parser = subparsers.add_parser('check', help='检查数据完整性')
    check_parser.add_argument('--output', '-o', help='保存检查结果到文件')
    check_parser.set_defaults(func=check_integrity)
    
    # 修复命令
    repair_parser = subparsers.add_parser('repair', help='修复数据完整性问题')
    repair_parser.add_argument('--remove-duplicates', action='store_true',
                             help='删除重复记录')
    repair_parser.add_argument('--fix-inconsistencies', action='store_true',
                             help='修复数据不一致')
    repair_parser.add_argument('--update-references', action='store_true',
                             help='更新无效引用')
    repair_parser.set_defaults(func=repair_integrity)
    
    # 状态命令
    status_parser = subparsers.add_parser('status', help='获取同步状态')
    status_parser.set_defaults(func=get_status)
    
    # 统计命令
    stats_parser = subparsers.add_parser('stats', help='获取交易统计')
    stats_parser.add_argument('--output', '-o', help='保存统计结果到文件')
    stats_parser.set_defaults(func=get_statistics)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 创建Flask应用上下文
    app = create_app()
    
    with app.app_context():
        try:
            success = args.func(args)
            return 0 if success else 1
        except KeyboardInterrupt:
            print("\n❌ 操作被用户中断")
            return 1
        except Exception as e:
            print(f"❌ 发生未预期的错误: {str(e)}")
            return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)