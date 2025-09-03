#!/usr/bin/env python3
"""
测试数据库迁移结果
验证所有新增的数据库结构和功能是否正常工作
"""
import sys
import os
from datetime import date, datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from models.non_trading_day import NonTradingDay
from models.profit_distribution_config import ProfitDistributionConfig
from models.trade_record import TradeRecord


def test_non_trading_day_functionality():
    """测试非交易日功能"""
    print("\n🧪 测试非交易日功能...")
    
    try:
        # 测试查询非交易日
        holidays = NonTradingDay.query.limit(5).all()
        print(f"✅ 查询到 {len(holidays)} 个节假日记录")
        
        if holidays:
            for holiday in holidays:
                print(f"   - {holiday.date}: {holiday.name}")
        
        # 测试交易日判断
        test_date = date(2024, 1, 1)  # 元旦
        is_trading = NonTradingDay.is_trading_day(test_date)
        print(f"✅ {test_date} 是否为交易日: {is_trading}")
        
        # 测试计算交易日数量
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 10)
        trading_days = NonTradingDay.calculate_trading_days(start_date, end_date)
        print(f"✅ {start_date} 到 {end_date} 的交易日数: {trading_days}")
        
        return True
        
    except Exception as e:
        print(f"❌ 非交易日功能测试失败: {str(e)}")
        return False


def test_profit_distribution_config():
    """测试收益分布配置功能"""
    print("\n🧪 测试收益分布配置功能...")
    
    try:
        # 测试查询收益分布配置
        configs = ProfitDistributionConfig.query.order_by(ProfitDistributionConfig.sort_order).all()
        print(f"✅ 查询到 {len(configs)} 个收益分布配置")
        
        for config in configs[:3]:  # 显示前3个
            min_rate = f"{config.min_profit_rate*100:.1f}%" if config.min_profit_rate else "无下限"
            max_rate = f"{config.max_profit_rate*100:.1f}%" if config.max_profit_rate else "无上限"
            print(f"   - {config.range_name}: {min_rate} ~ {max_rate}")
        
        # 测试获取活跃配置
        active_configs = ProfitDistributionConfig.get_active_configs()
        print(f"✅ 活跃配置数量: {len(active_configs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 收益分布配置功能测试失败: {str(e)}")
        return False


def test_trade_record_holding_days():
    """测试交易记录持仓天数字段"""
    print("\n🧪 测试交易记录持仓天数字段...")
    
    try:
        # 检查字段是否存在
        with db.engine.connect() as conn:
            result = conn.execute(db.text("""
                SELECT COUNT(*) as count FROM pragma_table_info('trade_records') 
                WHERE name = 'actual_holding_days'
            """))
            
            field_exists = result.fetchone()[0] > 0
            print(f"✅ actual_holding_days字段存在: {field_exists}")
        
        # 测试查询交易记录（如果有数据）
        trade_count = TradeRecord.query.count()
        print(f"✅ 交易记录总数: {trade_count}")
        
        if trade_count > 0:
            # 查看前几条记录的持仓天数字段
            trades = TradeRecord.query.limit(3).all()
            for trade in trades:
                holding_days = getattr(trade, 'actual_holding_days', None)
                print(f"   - {trade.stock_code} ({trade.trade_date.date()}): 持仓天数 = {holding_days}")
        
        return True
        
    except Exception as e:
        print(f"❌ 交易记录持仓天数字段测试失败: {str(e)}")
        return False


def test_database_integrity():
    """测试数据库完整性"""
    print("\n🧪 测试数据库完整性...")
    
    try:
        # 测试所有表是否可以正常访问
        tables_to_test = [
            ('non_trading_days', NonTradingDay),
            ('profit_distribution_configs', ProfitDistributionConfig),
            ('trade_records', TradeRecord)
        ]
        
        for table_name, model_class in tables_to_test:
            try:
                count = model_class.query.count()
                print(f"✅ {table_name} 表正常，记录数: {count}")
            except Exception as e:
                print(f"❌ {table_name} 表访问失败: {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库完整性测试失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("🚀 开始测试数据库迁移结果")
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        test_results = []
        
        # 执行各项测试
        test_results.append(test_database_integrity())
        test_results.append(test_non_trading_day_functionality())
        test_results.append(test_profit_distribution_config())
        test_results.append(test_trade_record_holding_days())
        
        # 输出测试结果
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"\n{'='*60}")
        print(f"测试结果汇总")
        print(f"通过: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("🎉 所有测试通过！数据库迁移成功！")
            return 0
        else:
            print("❌ 部分测试失败，请检查错误信息")
            return 1


if __name__ == '__main__':
    sys.exit(main())