"""
迁移: 为复盘记录添加当前价格和浮盈比例字段
创建时间: 2025-08-19T00:00:01
"""
from extensions import db


def upgrade():
    """应用迁移 - 为复盘记录表添加当前价格和浮盈比例字段"""
    try:
        with db.engine.connect() as conn:
            # 1. 检查并添加 current_price 字段（如果不存在）
            result = conn.execute(db.text("""
                PRAGMA table_info(review_records)
            """)).fetchall()
            
            current_price_exists = any(row[1] == 'current_price' for row in result)
            floating_profit_ratio_exists = any(row[1] == 'floating_profit_ratio' for row in result)
            buy_price_exists = any(row[1] == 'buy_price' for row in result)
            
            if not current_price_exists:
                conn.execute(db.text("""
                    ALTER TABLE review_records 
                    ADD COLUMN current_price DECIMAL(10, 2)
                """))
                print("  - 添加了 review_records.current_price 字段")
            else:
                print("  - review_records.current_price 字段已存在")
            
            # 2. 检查并添加 floating_profit_ratio 字段（如果不存在）
            if not floating_profit_ratio_exists:
                conn.execute(db.text("""
                    ALTER TABLE review_records 
                    ADD COLUMN floating_profit_ratio DECIMAL(5, 4)
                """))
                print("  - 添加了 review_records.floating_profit_ratio 字段")
            else:
                print("  - review_records.floating_profit_ratio 字段已存在")
            
            # 3. 检查并添加 buy_price 字段（如果不存在）
            if not buy_price_exists:
                conn.execute(db.text("""
                    ALTER TABLE review_records 
                    ADD COLUMN buy_price DECIMAL(10, 2)
                """))
                print("  - 添加了 review_records.buy_price 字段")
            else:
                print("  - review_records.buy_price 字段已存在")
            
            # 4. 检查并创建索引（如果不存在）
            current_price_index_exists = conn.execute(db.text("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='idx_review_current_price'
            """)).fetchone()
            
            if not current_price_index_exists:
                conn.execute(db.text("""
                    CREATE INDEX idx_review_current_price 
                    ON review_records(current_price)
                """))
                print("  - 创建了 idx_review_current_price 索引")
            else:
                print("  - idx_review_current_price 索引已存在")
            
            floating_profit_index_exists = conn.execute(db.text("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='idx_review_floating_profit'
            """)).fetchone()
            
            if not floating_profit_index_exists:
                conn.execute(db.text("""
                    CREATE INDEX idx_review_floating_profit 
                    ON review_records(floating_profit_ratio)
                """))
                print("  - 创建了 idx_review_floating_profit 索引")
            else:
                print("  - idx_review_floating_profit 索引已存在")
            
            conn.commit()
        
        print("✓ 复盘记录浮盈功能迁移成功")
        
    except Exception as e:
        print(f"复盘记录浮盈功能迁移失败: {e}")
        raise


def downgrade():
    """回滚迁移 - 删除复盘记录的浮盈相关字段"""
    try:
        with db.engine.connect() as conn:
            # 1. 删除索引
            conn.execute(db.text("DROP INDEX IF EXISTS idx_review_floating_profit"))
            conn.execute(db.text("DROP INDEX IF EXISTS idx_review_current_price"))
            
            # 2. 删除字段 - SQLite 不支持直接删除列，需要重建表
            conn.execute(db.text("""
                CREATE TABLE review_records_backup AS 
                SELECT id, stock_code, review_date, price_up_score, bbi_score, 
                       volume_score, trend_score, j_score, total_score, analysis, 
                       decision, reason, holding_days, created_at, updated_at
                FROM review_records
            """))
            
            conn.execute(db.text("DROP TABLE review_records"))
            
            conn.execute(db.text("ALTER TABLE review_records_backup RENAME TO review_records"))
            
            # 重新创建原有索引和约束
            conn.execute(db.text("""
                CREATE INDEX idx_review_stock_date ON review_records(stock_code, review_date)
            """))
            
            conn.execute(db.text("""
                CREATE UNIQUE INDEX unique_stock_review_date 
                ON review_records(stock_code, review_date)
            """))
            
            conn.commit()
        
        print("✓ 复盘记录浮盈功能回滚成功")
        print("  - 删除了 current_price 字段")
        print("  - 删除了 floating_profit_ratio 字段")
        print("  - 删除了 buy_price 字段")
        print("  - 重建了原有索引")
        
    except Exception as e:
        print(f"复盘记录浮盈功能回滚失败: {e}")
        raise