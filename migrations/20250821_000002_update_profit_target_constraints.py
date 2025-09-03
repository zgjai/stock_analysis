"""
更新止盈目标约束，支持大于10%的止盈比例和大于100%的卖出比例
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db


def upgrade():
    """升级数据库"""
    print("更新止盈目标约束...")
    
    with db.engine.connect() as conn:
        # 检查profit_taking_targets表是否存在
        result = conn.execute(db.text("""
            SELECT COUNT(*) as count FROM sqlite_master 
            WHERE type='table' AND name='profit_taking_targets'
        """))
        
        table_exists = result.fetchone()[0] > 0
        
        if table_exists:
            print("profit_taking_targets表存在，检查约束...")
            
            # 检查当前约束是否已经是新版本
            result = conn.execute(db.text("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='profit_taking_targets'
            """))
            
            table_sql = result.fetchone()[0]
            
            # 如果约束已经更新，跳过
            if 'sell_ratio <= 10' in table_sql:
                print("约束已经是最新版本，跳过更新")
                return
            
            print("更新约束中...")
            
            # SQLite不支持直接修改约束，需要重建表
            # 首先备份数据
            conn.execute(db.text("""
                CREATE TABLE profit_taking_targets_backup AS 
                SELECT * FROM profit_taking_targets
            """))
            
            # 删除原表
            conn.execute(db.text("DROP TABLE profit_taking_targets"))
            
            # 重建表，使用新的约束
            conn.execute(db.text("""
                CREATE TABLE profit_taking_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_record_id INTEGER NOT NULL,
                    profit_ratio DECIMAL(5,4) NOT NULL,
                    sell_ratio DECIMAL(5,4) NOT NULL,
                    expected_profit_ratio DECIMAL(5,4),
                    is_executed BOOLEAN DEFAULT 0,
                    executed_at DATETIME,
                    executed_price DECIMAL(10,2),
                    executed_quantity INTEGER,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trade_record_id) REFERENCES trade_records (id),
                    CHECK (sell_ratio > 0 AND sell_ratio <= 10),
                    CHECK (profit_ratio >= 0 AND profit_ratio <= 10)
                )
            """))
            
            # 恢复数据（明确指定列名以避免列数不匹配）
            conn.execute(db.text("""
                INSERT INTO profit_taking_targets 
                (id, trade_record_id, profit_ratio, sell_ratio, expected_profit_ratio, 
                 is_executed, executed_at, executed_price, executed_quantity, notes, 
                 created_at, updated_at)
                SELECT id, trade_record_id, profit_ratio, sell_ratio, expected_profit_ratio, 
                       is_executed, executed_at, executed_price, executed_quantity, notes, 
                       created_at, updated_at
                FROM profit_taking_targets_backup
            """))
            
            # 删除备份表
            conn.execute(db.text("DROP TABLE profit_taking_targets_backup"))
            
            # 重建索引
            conn.execute(db.text("""
                CREATE INDEX IF NOT EXISTS idx_profit_targets_trade_record 
                ON profit_taking_targets(trade_record_id)
            """))
            
            conn.commit()
            print("止盈目标约束更新完成")
        else:
            print("profit_taking_targets表不存在，跳过约束更新")


def downgrade():
    """降级数据库"""
    print("恢复原始止盈目标约束...")
    
    with db.engine.connect() as conn:
        # 检查表是否存在
        result = conn.execute(db.text("""
            SELECT COUNT(*) as count FROM sqlite_master 
            WHERE type='table' AND name='profit_taking_targets'
        """))
        
        table_exists = result.fetchone()[0] > 0
        
        if table_exists:
            # 备份数据
            conn.execute(db.text("""
                CREATE TABLE profit_taking_targets_backup AS 
                SELECT * FROM profit_taking_targets
            """))
            
            # 删除原表
            conn.execute(db.text("DROP TABLE profit_taking_targets"))
            
            # 重建表，使用原始约束
            conn.execute(db.text("""
                CREATE TABLE profit_taking_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_record_id INTEGER NOT NULL,
                    profit_ratio DECIMAL(5,4) NOT NULL,
                    sell_ratio DECIMAL(5,4) NOT NULL,
                    expected_profit_ratio DECIMAL(5,4),
                    is_executed BOOLEAN DEFAULT 0,
                    executed_at DATETIME,
                    executed_price DECIMAL(10,2),
                    executed_quantity INTEGER,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trade_record_id) REFERENCES trade_records (id),
                    CHECK (sell_ratio > 0 AND sell_ratio <= 1),
                    CHECK (profit_ratio >= 0)
                )
            """))
            
            # 恢复数据（明确指定列名）
            conn.execute(db.text("""
                INSERT INTO profit_taking_targets 
                (id, trade_record_id, profit_ratio, sell_ratio, expected_profit_ratio, 
                 is_executed, executed_at, executed_price, executed_quantity, notes, 
                 created_at, updated_at)
                SELECT id, trade_record_id, profit_ratio, sell_ratio, expected_profit_ratio, 
                       is_executed, executed_at, executed_price, executed_quantity, notes, 
                       created_at, updated_at
                FROM profit_taking_targets_backup
            """))
            
            # 删除备份表
            conn.execute(db.text("DROP TABLE profit_taking_targets_backup"))
            
            conn.commit()
            print("原始约束恢复完成")


if __name__ == '__main__':
    """直接运行此脚本进行迁移"""
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        try:
            upgrade()
            print("迁移执行成功")
        except Exception as e:
            print(f"迁移执行失败: {str(e)}")
            sys.exit(1)