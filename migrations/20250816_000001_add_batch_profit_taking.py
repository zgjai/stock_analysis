"""
迁移: 添加分批止盈功能
创建时间: 2025-08-16T00:00:01
"""
from extensions import db


def upgrade():
    """应用迁移 - 添加分批止盈相关表和字段"""
    try:
        with db.engine.connect() as conn:
            # 1. 检查并添加 use_batch_profit_taking 字段（如果不存在）
            result = conn.execute(db.text("""
                PRAGMA table_info(trade_records)
            """)).fetchall()
            
            column_exists = any(row[1] == 'use_batch_profit_taking' for row in result)
            
            if not column_exists:
                conn.execute(db.text("""
                    ALTER TABLE trade_records 
                    ADD COLUMN use_batch_profit_taking BOOLEAN DEFAULT FALSE
                """))
                print("  - 添加了 trade_records.use_batch_profit_taking 字段")
            else:
                print("  - trade_records.use_batch_profit_taking 字段已存在")
            
            # 2. 检查并创建 profit_taking_targets 表（如果不存在）
            table_exists = conn.execute(db.text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='profit_taking_targets'
            """)).fetchone()
            
            if not table_exists:
                conn.execute(db.text("""
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
                        CHECK (sell_ratio > 0 AND sell_ratio <= 1),
                        CHECK (profit_ratio >= 0),
                        CHECK (sequence_order > 0)
                    )
                """))
                print("  - 创建了 profit_taking_targets 表")
            else:
                print("  - profit_taking_targets 表已存在")
            
            # 3. 检查并创建索引（如果不存在）
            index1_exists = conn.execute(db.text("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='idx_profit_targets_trade'
            """)).fetchone()
            
            if not index1_exists:
                conn.execute(db.text("""
                    CREATE INDEX idx_profit_targets_trade 
                    ON profit_taking_targets(trade_record_id)
                """))
                print("  - 创建了 idx_profit_targets_trade 索引")
            else:
                print("  - idx_profit_targets_trade 索引已存在")
            
            index2_exists = conn.execute(db.text("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='idx_profit_targets_sequence'
            """)).fetchone()
            
            if not index2_exists:
                conn.execute(db.text("""
                    CREATE INDEX idx_profit_targets_sequence 
                    ON profit_taking_targets(trade_record_id, sequence_order)
                """))
                print("  - 创建了 idx_profit_targets_sequence 索引")
            else:
                print("  - idx_profit_targets_sequence 索引已存在")
            
            # 4. 为现有交易记录设置默认值
            conn.execute(db.text("""
                UPDATE trade_records 
                SET use_batch_profit_taking = FALSE 
                WHERE use_batch_profit_taking IS NULL
            """))
            
            conn.commit()
        
        print("✓ 分批止盈功能迁移成功")
        
    except Exception as e:
        print(f"分批止盈功能迁移失败: {e}")
        raise


def downgrade():
    """回滚迁移 - 删除分批止盈相关表和字段"""
    try:
        with db.engine.connect() as conn:
            # 1. 删除索引
            conn.execute(db.text("DROP INDEX IF EXISTS idx_profit_targets_sequence"))
            conn.execute(db.text("DROP INDEX IF EXISTS idx_profit_targets_trade"))
            
            # 2. 删除 profit_taking_targets 表
            conn.execute(db.text("DROP TABLE IF EXISTS profit_taking_targets"))
            
            # 3. 删除 trade_records 表的 use_batch_profit_taking 字段
            # SQLite 不支持直接删除列，需要重建表
            conn.execute(db.text("""
                CREATE TABLE trade_records_backup AS 
                SELECT id, stock_code, stock_name, trade_type, price, quantity, trade_date, 
                       reason, notes, stop_loss_price, take_profit_ratio, sell_ratio, 
                       expected_loss_ratio, expected_profit_ratio, is_corrected, 
                       original_record_id, correction_reason, created_at, updated_at
                FROM trade_records
            """))
            
            conn.execute(db.text("DROP TABLE trade_records"))
            
            conn.execute(db.text("ALTER TABLE trade_records_backup RENAME TO trade_records"))
            
            # 重新创建原有索引
            conn.execute(db.text("""
                CREATE INDEX idx_trade_records_stock_code ON trade_records(stock_code)
            """))
            
            conn.execute(db.text("""
                CREATE INDEX idx_trade_records_trade_date ON trade_records(trade_date)
            """))
            
            conn.execute(db.text("""
                CREATE INDEX idx_stock_date ON trade_records(stock_code, trade_date)
            """))
            
            conn.commit()
        
        print("✓ 分批止盈功能回滚成功")
        print("  - 删除了 profit_taking_targets 表")
        print("  - 删除了 trade_records.use_batch_profit_taking 字段")
        print("  - 重建了原有索引")
        
    except Exception as e:
        print(f"分批止盈功能回滚失败: {e}")
        raise