"""
迁移: 初始数据库架构
创建时间: 2024-12-16T00:00:01
"""
from extensions import db


def upgrade():
    """应用迁移 - 创建初始表结构"""
    # 这个迁移文件主要用于记录初始架构
    # 实际的表创建由 init_db.py 中的 create_tables() 函数处理
    
    # 创建额外的复合索引
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                CREATE INDEX IF NOT EXISTS idx_trade_stock_type_date 
                ON trade_records(stock_code, trade_type, trade_date DESC)
            """))
            
            conn.execute(db.text("""
                CREATE INDEX IF NOT EXISTS idx_review_score_date 
                ON review_records(total_score DESC, review_date DESC)
            """))
            
            conn.execute(db.text("""
                CREATE INDEX IF NOT EXISTS idx_sector_performance 
                ON sector_data(change_percent DESC, record_date DESC)
            """))
            
            conn.commit()
        
        print("✓ 初始索引创建成功")
    except Exception as e:
        print(f"创建初始索引时出错: {e}")
        raise


def downgrade():
    """回滚迁移 - 删除初始表结构"""
    # 删除额外的索引
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("DROP INDEX IF EXISTS idx_trade_stock_type_date"))
            conn.execute(db.text("DROP INDEX IF EXISTS idx_review_score_date"))
            conn.execute(db.text("DROP INDEX IF EXISTS idx_sector_performance"))
            conn.commit()
        
        print("✓ 初始索引删除成功")
    except Exception as e:
        print(f"删除初始索引时出错: {e}")
        raise