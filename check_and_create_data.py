#!/usr/bin/env python3
"""
检查数据库状态并创建测试数据
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.trade_record import TradeRecord

def check_database():
    """检查数据库状态"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查数据库连接
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✓ 数据库连接正常")
            
            # 检查表是否存在
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✓ 数据库表: {tables}")
            
            # 检查交易记录数量
            trade_count = TradeRecord.query.count()
            print(f"✓ 交易记录数量: {trade_count}")
            
            if trade_count == 0:
                print("! 数据库中没有交易记录，创建测试数据...")
                create_test_data()
            else:
                print("✓ 数据库中已有交易记录")
                
        except Exception as e:
            print(f"✗ 数据库检查失败: {e}")
            return False
    
    return True

def create_test_data():
    """创建测试数据"""
    app = create_app()
    
    with app.app_context():
        try:
            # 直接使用SQL插入测试数据，避免验证问题
            sql_statements = [
                """
                INSERT INTO trade_records (
                    stock_code, stock_name, trade_type, price, quantity, 
                    trade_date, reason, notes, stop_loss_price, take_profit_ratio,
                    created_at, updated_at
                ) VALUES 
                ('000001', '平安银行', 'buy', 12.50, 1000, '{}', '技术突破', '测试买入记录', 11.25, 0.15, '{}', '{}'),
                ('000001', '平安银行', 'sell', 13.20, 500, '{}', '止盈', '部分止盈', NULL, NULL, '{}', '{}'),
                ('000002', '万科A', 'buy', 18.80, 500, '{}', '价值投资', '长期持有', 16.92, 0.20, '{}', '{}'),
                ('600036', '招商银行', 'buy', 35.60, 300, '{}', '银行股反弹', '短期交易', 32.04, 0.12, '{}', '{}'),
                ('600036', '招商银行', 'sell', 37.20, 300, '{}', '止盈', '达到目标价位', NULL, NULL, '{}', '{}')
                """.format(
                    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            ]
            
            with db.engine.connect() as conn:
                for sql in sql_statements:
                    conn.execute(db.text(sql))
                conn.commit()
            
            print("✓ 成功创建测试交易记录")
            
            # 验证数据
            total_trades = TradeRecord.query.count()
            print(f"✓ 数据库中现有 {total_trades} 条交易记录")
            
            # 显示一些记录
            recent_trades = TradeRecord.query.order_by(TradeRecord.trade_date.desc()).limit(3).all()
            print("✓ 最近的交易记录:")
            for trade in recent_trades:
                print(f"  - {trade.stock_name}({trade.stock_code}) {trade.trade_type} {trade.price} x {trade.quantity}")
            
        except Exception as e:
            print(f"✗ 创建测试数据失败: {e}")
            import traceback
            traceback.print_exc()

def main():
    print("检查数据库状态...")
    print("=" * 50)
    
    if check_database():
        print("=" * 50)
        print("✓ 数据库检查完成")
    else:
        print("=" * 50)
        print("✗ 数据库检查失败")
        sys.exit(1)

if __name__ == '__main__':
    main()