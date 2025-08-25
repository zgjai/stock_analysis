#!/usr/bin/env python3
"""
更新止盈目标表约束，支持大于10%的止盈比例和大于100%的卖出比例
"""

import sys
import os
sys.path.append('.')

from app import create_app
from extensions import db

def update_constraints():
    """更新数据库约束"""
    app = create_app()
    
    with app.app_context():
        print("=== 更新止盈目标表约束 ===\n")
        
        try:
            # 备份现有数据
            print("1. 备份现有数据...")
            backup_data = db.session.execute(db.text("""
                SELECT * FROM profit_taking_targets
            """)).fetchall()
            print(f"   备份了 {len(backup_data)} 条记录")
            
            # 删除现有表
            print("2. 删除现有表...")
            db.session.execute(db.text("DROP TABLE IF EXISTS profit_taking_targets"))
            
            # 重新创建表，使用新的约束
            print("3. 重新创建表...")
            db.session.execute(db.text("""
                CREATE TABLE profit_taking_targets (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    trade_record_id INTEGER NOT NULL,
                    target_price NUMERIC(10, 2),
                    profit_ratio NUMERIC(5, 4),
                    sell_ratio NUMERIC(5, 4) NOT NULL,
                    expected_profit_ratio NUMERIC(5, 4),
                    sequence_order INTEGER NOT NULL DEFAULT 1,
                    created_at DATETIME,
                    updated_at DATETIME,
                    FOREIGN KEY(trade_record_id) REFERENCES trade_records (id),
                    CHECK (sell_ratio > 0 AND sell_ratio <= 10),
                    CHECK (profit_ratio >= 0 AND profit_ratio <= 10),
                    CHECK (sequence_order > 0)
                )
            """))
            
            # 创建索引
            print("4. 创建索引...")
            db.session.execute(db.text("""
                CREATE INDEX idx_profit_targets_trade ON profit_taking_targets (trade_record_id)
            """))
            db.session.execute(db.text("""
                CREATE INDEX idx_profit_targets_sequence ON profit_taking_targets (trade_record_id, sequence_order)
            """))
            
            # 恢复数据
            if backup_data:
                print("5. 恢复数据...")
                for row in backup_data:
                    db.session.execute(db.text("""
                        INSERT INTO profit_taking_targets 
                        (id, trade_record_id, target_price, profit_ratio, sell_ratio, 
                         expected_profit_ratio, sequence_order, created_at, updated_at)
                        VALUES (:id, :trade_record_id, :target_price, :profit_ratio, :sell_ratio, 
                                :expected_profit_ratio, :sequence_order, :created_at, :updated_at)
                    """), {
                        'id': row.id,
                        'trade_record_id': row.trade_record_id,
                        'target_price': row.target_price,
                        'profit_ratio': row.profit_ratio,
                        'sell_ratio': row.sell_ratio,
                        'expected_profit_ratio': row.expected_profit_ratio,
                        'sequence_order': row.sequence_order,
                        'created_at': row.created_at,
                        'updated_at': row.updated_at
                    })
                print(f"   恢复了 {len(backup_data)} 条记录")
            
            db.session.commit()
            print("\n✓ 约束更新完成！")
            print("  - 止盈比例：允许 0-1000%")
            print("  - 卖出比例：允许 0-1000%")
            
        except Exception as e:
            print(f"\n✗ 更新失败: {e}")
            db.session.rollback()
            return False
        
        return True

if __name__ == '__main__':
    success = update_constraints()
    sys.exit(0 if success else 1)