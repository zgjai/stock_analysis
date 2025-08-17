"""
数据库初始化脚本
"""
import os
import sys
from datetime import datetime
from app import create_app
from extensions import db
from models import *  # 导入所有模型


def create_tables():
    """创建所有数据库表"""
    try:
        db.create_all()
        print("✓ 数据库表创建成功！")
        return True
    except Exception as e:
        print(f"✗ 数据库表创建失败: {e}")
        return False


def create_indexes():
    """创建额外的索引"""
    try:
        # 创建复合索引
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                CREATE INDEX IF NOT EXISTS idx_trade_stock_type_date 
                ON trade_records(stock_code, trade_type, trade_date DESC)
            """))
            
            conn.execute(db.text("""
                CREATE INDEX IF NOT EXISTS idx_review_score_date 
                ON review_records(total_score DESC, review_date DESC)
            """))
            
            conn.commit()
        
        print("✓ 数据库索引创建成功！")
        return True
    except Exception as e:
        print(f"✗ 数据库索引创建失败: {e}")
        return False


def insert_initial_data():
    """插入初始配置数据"""
    try:
        # 检查是否已有配置数据
        if Configuration.get_by_key('buy_reasons'):
            print("✓ 配置数据已存在，跳过初始化")
            return True
        
        # 插入买入原因配置
        buy_reasons = ["少妇B1战法", "少妇SB1战法", "少妇B2战法", "单针二十战法"]
        Configuration.set_value('buy_reasons', buy_reasons, '买入原因选项')
        
        # 插入卖出原因配置
        sell_reasons = ["部分止盈", "止损", "下等马/草泥马"]
        Configuration.set_value('sell_reasons', sell_reasons, '卖出原因选项')
        
        # 插入默认交易策略
        default_strategy_rules = {
            "rules": [
                {"day_range": [1, 1], "loss_threshold": -0.05, "action": "sell_all", "condition": "loss_exceed"},
                {"day_range": [2, 4], "loss_threshold": -0.03, "action": "sell_all", "condition": "loss_exceed"},
                {"day_range": [5, 5], "loss_threshold": -0.02, "action": "sell_all", "condition": "loss_exceed"},
                {"day_range": [6, 6], "profit_threshold": 0.03, "action": "sell_all", "condition": "profit_below"},
                {"day_range": [7, 10], "profit_threshold": 0.07, "action": "sell_all", "condition": "profit_below"},
                {"day_range": [7, 10], "profit_threshold": 0.10, "action": "sell_partial", "sell_ratio": 0.3, "condition": "profit_exceed"},
                {"day_range": [11, 15], "profit_threshold": 0.15, "drawdown_threshold": 0.10, "action": "sell_all", "condition": "profit_below_or_drawdown"},
                {"day_range": [11, 15], "profit_threshold": 0.20, "action": "sell_partial", "sell_ratio": 0.3, "condition": "profit_exceed"},
                {"day_range": [16, 20], "profit_threshold": 0.25, "drawdown_threshold": 0.15, "action": "sell_all", "condition": "profit_below_or_drawdown"},
                {"day_range": [16, 20], "profit_threshold": 0.30, "action": "sell_partial", "sell_ratio": 0.2, "condition": "profit_exceed"},
                {"day_range": [21, 30], "profit_threshold": 0.30, "drawdown_threshold": 0.15, "action": "sell_all", "condition": "profit_below_or_drawdown"}
            ]
        }
        
        default_strategy = TradingStrategy(
            strategy_name='默认持仓策略',
            is_active=True,
            description='基于持仓天数的动态止损止盈策略'
        )
        default_strategy.rules_list = default_strategy_rules
        default_strategy.save()
        
        print("✓ 初始配置数据插入成功！")
        return True
    except Exception as e:
        print(f"✗ 初始配置数据插入失败: {e}")
        return False


def verify_database():
    """验证数据库表结构"""
    try:
        # 检查所有表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'trade_records', 'trade_corrections', 'review_records', 'stock_pool',
            'case_studies', 'configurations', 'stock_prices', 'sector_data',
            'sector_rankings', 'trading_strategies'
        ]
        
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            print(f"✗ 缺少数据库表: {missing_tables}")
            return False
        
        print("✓ 数据库表结构验证成功！")
        
        # 验证配置数据
        buy_reasons = Configuration.get_value('buy_reasons')
        sell_reasons = Configuration.get_value('sell_reasons')
        default_strategy = TradingStrategy.get_default_strategy()
        
        if not buy_reasons or not sell_reasons or not default_strategy:
            print("✗ 初始配置数据验证失败")
            return False
        
        print("✓ 初始配置数据验证成功！")
        return True
    except Exception as e:
        print(f"✗ 数据库验证失败: {e}")
        return False


def test_database_connection():
    """测试数据库连接"""
    try:
        # 执行简单查询测试连接
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SELECT 1")).fetchone()
            if result and result[0] == 1:
                print("✓ 数据库连接测试成功！")
                return True
            else:
                print("✗ 数据库连接测试失败")
                return False
    except Exception as e:
        print(f"✗ 数据库连接测试失败: {e}")
        return False


def init_database(force_recreate=False):
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        print("开始初始化数据库...")
        print(f"数据库文件路径: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 测试数据库连接
        if not test_database_connection():
            return False
        
        # 如果强制重建，先删除所有表
        if force_recreate:
            print("强制重建模式：删除现有表...")
            db.drop_all()
        
        # 创建表
        if not create_tables():
            return False
        
        # 创建索引
        if not create_indexes():
            return False
        
        # 插入初始数据
        if not insert_initial_data():
            return False
        
        # 验证数据库
        if not verify_database():
            return False
        
        print("✓ 数据库初始化完成！")
        return True


def backup_database():
    """备份数据库"""
    try:
        from shutil import copy2
        from pathlib import Path
        
        app = create_app()
        db_path = Path(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        
        if db_path.exists():
            backup_path = db_path.parent / f"trading_journal_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            copy2(db_path, backup_path)
            print(f"✓ 数据库备份成功: {backup_path}")
            return str(backup_path)
        else:
            print("✗ 数据库文件不存在，无法备份")
            return None
    except Exception as e:
        print(f"✗ 数据库备份失败: {e}")
        return None


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库初始化工具')
    parser.add_argument('--force', action='store_true', help='强制重建数据库')
    parser.add_argument('--backup', action='store_true', help='备份现有数据库')
    parser.add_argument('--verify', action='store_true', help='仅验证数据库结构')
    
    args = parser.parse_args()
    
    if args.backup:
        backup_database()
        return
    
    if args.verify:
        app = create_app()
        with app.app_context():
            if test_database_connection() and verify_database():
                print("✓ 数据库验证通过")
                sys.exit(0)
            else:
                print("✗ 数据库验证失败")
                sys.exit(1)
        return
    
    # 如果强制重建，先备份
    if args.force:
        backup_database()
    
    # 初始化数据库
    if init_database(force_recreate=args.force):
        print("数据库初始化成功！")
        sys.exit(0)
    else:
        print("数据库初始化失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()