"""
为TradeRecord表添加actual_holding_days字段的迁移脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db


def upgrade():
    """添加actual_holding_days字段到trade_records表"""
    print("为trade_records表添加actual_holding_days字段...")
    
    with db.engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(db.text("""
            SELECT COUNT(*) as count FROM pragma_table_info('trade_records') 
            WHERE name = 'actual_holding_days'
        """))
        
        field_exists = result.fetchone()[0] > 0
        
        if not field_exists:
            # 添加actual_holding_days字段
            conn.execute(db.text("""
                ALTER TABLE trade_records 
                ADD COLUMN actual_holding_days INTEGER DEFAULT NULL
            """))
            
            # 创建索引以提高查询性能
            conn.execute(db.text("""
                CREATE INDEX IF NOT EXISTS idx_trade_records_holding_days 
                ON trade_records(actual_holding_days)
            """))
            
            conn.commit()
            print("成功添加actual_holding_days字段")
        else:
            print("actual_holding_days字段已存在，跳过添加")
    
    print("actual_holding_days字段迁移完成")


def downgrade():
    """移除actual_holding_days字段"""
    print("从trade_records表移除actual_holding_days字段...")
    
    with db.engine.connect() as conn:
        # SQLite不支持直接删除列，需要重建表
        # 首先备份数据
        conn.execute(db.text("""
            CREATE TABLE trade_records_backup AS 
            SELECT id, stock_code, stock_name, trade_type, price, quantity, 
                   trade_date, reason, notes, stop_loss_price, take_profit_ratio, 
                   sell_ratio, expected_loss_ratio, expected_profit_ratio, 
                   use_batch_profit_taking, is_corrected, original_record_id, 
                   correction_reason, created_at, updated_at
            FROM trade_records
        """))
        
        # 删除原表
        conn.execute(db.text("DROP TABLE trade_records"))
        
        # 重建表（不包含actual_holding_days字段）
        conn.execute(db.text("""
            CREATE TABLE trade_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code VARCHAR(10) NOT NULL,
                stock_name VARCHAR(50) NOT NULL,
                trade_type VARCHAR(10) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                quantity INTEGER NOT NULL,
                trade_date DATETIME NOT NULL,
                reason VARCHAR(50) NOT NULL,
                notes TEXT,
                stop_loss_price DECIMAL(10,2),
                take_profit_ratio DECIMAL(5,4),
                sell_ratio DECIMAL(5,4),
                expected_loss_ratio DECIMAL(5,4),
                expected_profit_ratio DECIMAL(5,4),
                use_batch_profit_taking BOOLEAN DEFAULT 0,
                is_corrected BOOLEAN DEFAULT 0,
                original_record_id INTEGER,
                correction_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (original_record_id) REFERENCES trade_records (id),
                CHECK (trade_type IN ('buy', 'sell'))
            )
        """))
        
        # 恢复数据
        conn.execute(db.text("""
            INSERT INTO trade_records 
            SELECT * FROM trade_records_backup
        """))
        
        # 删除备份表
        conn.execute(db.text("DROP TABLE trade_records_backup"))
        
        # 重建索引
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
    
    print("actual_holding_days字段移除完成")


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