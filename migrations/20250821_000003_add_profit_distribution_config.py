"""
添加收益分布配置表
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db


def upgrade():
    """创建收益分布配置表"""
    with db.engine.connect() as conn:
        conn.execute(db.text("""
            CREATE TABLE IF NOT EXISTS profit_distribution_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                range_name VARCHAR(50) NOT NULL,
                min_profit_rate DECIMAL(8,4),
                max_profit_rate DECIMAL(8,4),
                sort_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_by VARCHAR(50) DEFAULT 'system',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # 创建索引
        conn.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_profit_config_active_order 
            ON profit_distribution_configs(is_active, sort_order)
        """))
        
        conn.commit()
    
    print("收益分布配置表创建成功")


def downgrade():
    """删除收益分布配置表"""
    with db.engine.connect() as conn:
        conn.execute(db.text("DROP TABLE IF EXISTS profit_distribution_configs"))
        conn.commit()
    print("收益分布配置表删除成功")


if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        upgrade()