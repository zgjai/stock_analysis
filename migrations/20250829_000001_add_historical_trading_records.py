"""
添加历史交易记录功能相关表
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db


def upgrade():
    """创建历史交易记录相关表"""
    with db.engine.connect() as conn:
        # 创建历史交易记录表
        conn.execute(db.text("""
            CREATE TABLE IF NOT EXISTS historical_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code VARCHAR(10) NOT NULL,
                stock_name VARCHAR(50) NOT NULL,
                buy_date DATETIME NOT NULL,
                sell_date DATETIME NOT NULL,
                holding_days INTEGER NOT NULL,
                total_investment DECIMAL(12,2) NOT NULL,
                total_return DECIMAL(12,2) NOT NULL,
                return_rate DECIMAL(8,4) NOT NULL,
                buy_records_ids TEXT,
                sell_records_ids TEXT,
                is_completed BOOLEAN DEFAULT 1 NOT NULL,
                completion_date DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                CONSTRAINT check_positive_investment CHECK (total_investment > 0),
                CONSTRAINT check_non_negative_holding_days CHECK (holding_days >= 0),
                CONSTRAINT check_date_order CHECK (sell_date >= buy_date)
            )
        """))
        
        # 创建历史交易记录索引
        conn.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_historical_trades_stock_code 
            ON historical_trades(stock_code)
        """))
        
        conn.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_historical_trades_buy_date 
            ON historical_trades(buy_date)
        """))
        
        conn.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_historical_trades_sell_date 
            ON historical_trades(sell_date)
        """))
        
        conn.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_historical_stock_date 
            ON historical_trades(stock_code, buy_date)
        """))
        
        conn.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_historical_completion 
            ON historical_trades(completion_date, is_completed)
        """))
        
        conn.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_historical_return_rate 
            ON historical_trades(return_rate)
        """))
        
        # 创建交易复盘记录表
        conn.execute(db.text("""
            CREATE TABLE IF NOT EXISTS trade_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                historical_trade_id INTEGER NOT NULL,
                review_title VARCHAR(200),
                review_content TEXT,
                review_type VARCHAR(20) DEFAULT 'general',
                strategy_score INTEGER,
                timing_score INTEGER,
                risk_control_score INTEGER,
                overall_score INTEGER,
                key_learnings TEXT,
                improvement_areas TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                FOREIGN KEY (historical_trade_id) REFERENCES historical_trades(id),
                CONSTRAINT check_review_type CHECK (review_type IN ('general', 'success', 'failure', 'lesson')),
                CONSTRAINT check_strategy_score CHECK (strategy_score IS NULL OR (strategy_score >= 1 AND strategy_score <= 5)),
                CONSTRAINT check_timing_score CHECK (timing_score IS NULL OR (timing_score >= 1 AND timing_score <= 5)),
                CONSTRAINT check_risk_control_score CHECK (risk_control_score IS NULL OR (risk_control_score >= 1 AND risk_control_score <= 5)),
                CONSTRAINT check_overall_score CHECK (overall_score IS NULL OR (overall_score >= 1 AND overall_score <= 5))
            )
        """))
        
        # 创建交易复盘记录索引
        conn.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_review_historical_trade 
            ON trade_reviews(historical_trade_id)
        """))
        
        conn.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_review_type 
            ON trade_reviews(review_type)
        """))
        
        # 创建复盘图片表
        conn.execute(db.text("""
            CREATE TABLE IF NOT EXISTS review_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_review_id INTEGER NOT NULL,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER,
                mime_type VARCHAR(100),
                description TEXT,
                display_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                FOREIGN KEY (trade_review_id) REFERENCES trade_reviews(id),
                CONSTRAINT check_positive_file_size CHECK (file_size IS NULL OR file_size > 0),
                CONSTRAINT check_non_negative_display_order CHECK (display_order >= 0)
            )
        """))
        
        # 创建复盘图片索引
        conn.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_review_image_trade_review 
            ON review_images(trade_review_id)
        """))
        
        conn.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_review_image_order 
            ON review_images(trade_review_id, display_order)
        """))
        
        conn.commit()
    
    print("历史交易记录功能相关表创建成功")


def downgrade():
    """删除历史交易记录相关表"""
    with db.engine.connect() as conn:
        # 删除表（注意外键依赖顺序）
        conn.execute(db.text("DROP TABLE IF EXISTS review_images"))
        conn.execute(db.text("DROP TABLE IF EXISTS trade_reviews"))
        conn.execute(db.text("DROP TABLE IF EXISTS historical_trades"))
        conn.commit()
    print("历史交易记录功能相关表删除成功")


if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        upgrade()