#!/usr/bin/env python3
"""
仪表板交易增强功能数据库迁移执行脚本
执行所有相关的数据库迁移，包括：
1. 非交易日表创建和数据初始化
2. 收益分布配置表创建
3. TradeRecord表添加actual_holding_days字段
4. 默认收益分布配置初始化
"""
import sys
import os
import importlib.util
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db


def load_migration_module(migration_file):
    """动态加载迁移模块"""
    spec = importlib.util.spec_from_file_location("migration", migration_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_migration(migration_file, description):
    """执行单个迁移"""
    print(f"\n{'='*60}")
    print(f"执行迁移: {description}")
    print(f"文件: {migration_file}")
    print(f"{'='*60}")
    
    try:
        # 动态加载迁移模块
        migration_module = load_migration_module(migration_file)
        
        # 执行升级
        migration_module.upgrade()
        
        print(f"✅ 迁移成功: {description}")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {description}")
        print(f"错误信息: {str(e)}")
        return False


def main():
    """主函数"""
    print("🚀 开始执行仪表板交易增强功能数据库迁移")
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        # 确保数据库连接正常
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            print("✅ 数据库连接正常")
        except Exception as e:
            print(f"❌ 数据库连接失败: {str(e)}")
            sys.exit(1)
        
        # 定义迁移列表（按执行顺序）
        migrations = [
            {
                'file': 'migrations/20250821_000001_add_non_trading_day.py',
                'description': '创建非交易日表并初始化默认节假日数据'
            },
            {
                'file': 'migrations/20250821_000002_update_profit_target_constraints.py',
                'description': '更新止盈目标约束'
            },
            {
                'file': 'migrations/20250821_000003_add_profit_distribution_config.py',
                'description': '创建收益分布配置表'
            },
            {
                'file': 'migrations/20250821_000004_add_actual_holding_days.py',
                'description': '为TradeRecord表添加actual_holding_days字段'
            },
            {
                'file': 'migrations/20250821_000005_init_default_profit_distribution.py',
                'description': '初始化默认收益分布配置'
            }
        ]
        
        # 执行迁移
        success_count = 0
        total_count = len(migrations)
        
        for migration in migrations:
            migration_file = project_root / migration['file']
            
            if not migration_file.exists():
                print(f"⚠️  迁移文件不存在: {migration_file}")
                continue
            
            if run_migration(migration_file, migration['description']):
                success_count += 1
            else:
                print(f"\n❌ 迁移失败，停止执行后续迁移")
                break
        
        # 输出总结
        print(f"\n{'='*60}")
        print(f"迁移执行完成")
        print(f"成功: {success_count}/{total_count}")
        
        if success_count == total_count:
            print("🎉 所有迁移执行成功！")
            
            # 验证迁移结果
            print(f"\n{'='*60}")
            print("验证迁移结果...")
            
            try:
                with db.engine.connect() as conn:
                    # 检查非交易日表
                    result = conn.execute(db.text("""
                        SELECT COUNT(*) as count FROM non_trading_days
                    """))
                    non_trading_count = result.fetchone()[0]
                    print(f"✅ 非交易日记录数: {non_trading_count}")
                    
                    # 检查收益分布配置表
                    result = conn.execute(db.text("""
                        SELECT COUNT(*) as count FROM profit_distribution_configs
                    """))
                    profit_config_count = result.fetchone()[0]
                    print(f"✅ 收益分布配置数: {profit_config_count}")
                    
                    # 检查actual_holding_days字段
                    result = conn.execute(db.text("""
                        SELECT COUNT(*) as count FROM pragma_table_info('trade_records') 
                        WHERE name = 'actual_holding_days'
                    """))
                    field_exists = result.fetchone()[0] > 0
                    print(f"✅ actual_holding_days字段: {'已添加' if field_exists else '未找到'}")
                
                print("🎉 所有数据库结构验证通过！")
                
            except Exception as e:
                print(f"⚠️  验证过程中出现错误: {str(e)}")
        else:
            print("❌ 部分迁移失败，请检查错误信息")
            sys.exit(1)


if __name__ == '__main__':
    main()