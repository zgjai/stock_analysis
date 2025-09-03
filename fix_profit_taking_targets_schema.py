#!/usr/bin/env python3
"""
修复profit_taking_targets表结构，添加缺失的列
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from datetime import datetime


def fix_profit_taking_targets_schema():
    """修复profit_taking_targets表结构"""
    db_path = 'data/trading_journal.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("检查profit_taking_targets表当前结构...")
        
        # 获取当前表结构
        cursor.execute('PRAGMA table_info(profit_taking_targets)')
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"当前列: {column_names}")
        
        # 检查缺失的列
        missing_columns = []
        if 'target_price' not in column_names:
            missing_columns.append('target_price')
        if 'sequence_order' not in column_names:
            missing_columns.append('sequence_order')
        
        if not missing_columns:
            print("表结构已经是最新的，无需修复")
            return True
        
        print(f"需要添加的列: {missing_columns}")
        
        # 备份当前数据
        print("备份当前数据...")
        cursor.execute("""
            CREATE TABLE profit_taking_targets_temp AS 
            SELECT * FROM profit_taking_targets
        """)
        
        # 删除原表
        print("删除原表...")
        cursor.execute("DROP TABLE profit_taking_targets")
        
        # 创建新表结构（与模型定义一致）
        print("创建新表结构...")
        cursor.execute("""
            CREATE TABLE profit_taking_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_record_id INTEGER NOT NULL,
                target_price DECIMAL(10, 2),
                profit_ratio DECIMAL(5, 4),
                sell_ratio DECIMAL(5, 4) NOT NULL,
                expected_profit_ratio DECIMAL(5, 4),
                sequence_order INTEGER NOT NULL DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trade_record_id) REFERENCES trade_records(id) ON DELETE CASCADE,
                CHECK (sell_ratio > 0 AND sell_ratio <= 10),
                CHECK (profit_ratio >= 0 AND profit_ratio <= 10),
                CHECK (sequence_order > 0)
            )
        """)
        
        # 恢复数据，为新列设置默认值
        print("恢复数据...")
        cursor.execute("""
            INSERT INTO profit_taking_targets 
            (id, trade_record_id, profit_ratio, sell_ratio, expected_profit_ratio, 
             target_price, sequence_order, created_at, updated_at)
            SELECT 
                id, 
                trade_record_id, 
                profit_ratio, 
                sell_ratio, 
                expected_profit_ratio,
                NULL as target_price,
                1 as sequence_order,
                COALESCE(created_at, CURRENT_TIMESTAMP) as created_at,
                COALESCE(updated_at, CURRENT_TIMESTAMP) as updated_at
            FROM profit_taking_targets_temp
        """)
        
        # 删除临时表
        cursor.execute("DROP TABLE profit_taking_targets_temp")
        
        # 创建索引
        print("创建索引...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_profit_targets_trade 
            ON profit_taking_targets(trade_record_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_profit_targets_sequence 
            ON profit_taking_targets(trade_record_id, sequence_order)
        """)
        
        # 提交更改
        conn.commit()
        
        # 验证新结构
        print("验证新表结构...")
        cursor.execute('PRAGMA table_info(profit_taking_targets)')
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]
        
        print(f"新表结构: {new_column_names}")
        
        # 检查数据是否正确恢复
        cursor.execute('SELECT COUNT(*) FROM profit_taking_targets')
        count = cursor.fetchone()[0]
        print(f"恢复的记录数: {count}")
        
        conn.close()
        
        print("✓ profit_taking_targets表结构修复成功")
        return True
        
    except Exception as e:
        print(f"修复失败: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


if __name__ == '__main__':
    success = fix_profit_taking_targets_schema()
    if not success:
        sys.exit(1)