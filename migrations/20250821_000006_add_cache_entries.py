"""
添加缓存条目表
用于存储系统缓存数据，提高查询性能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db
from app import create_app
from sqlalchemy import text


def upgrade():
    """创建缓存条目表"""
    
    app = create_app()
    with app.app_context():
        # 创建缓存条目表
        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key VARCHAR(255) NOT NULL UNIQUE,
                    cache_value TEXT NOT NULL,
                    cache_type VARCHAR(50) NOT NULL,
                    expires_at DATETIME NOT NULL,
                    created_by VARCHAR(50) DEFAULT 'system',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 创建索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cache_key ON cache_entries(cache_key)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cache_type ON cache_entries(cache_type)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_entries(expires_at)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cache_type_expires ON cache_entries(cache_type, expires_at)
            """))
            
            conn.commit()
        
        print("✓ 缓存条目表创建完成")


def downgrade():
    """删除缓存条目表"""
    
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            # 删除索引
            conn.execute(text("DROP INDEX IF EXISTS idx_cache_type_expires"))
            conn.execute(text("DROP INDEX IF EXISTS idx_cache_expires"))
            conn.execute(text("DROP INDEX IF EXISTS idx_cache_type"))
            conn.execute(text("DROP INDEX IF EXISTS idx_cache_key"))
            
            # 删除表
            conn.execute(text("DROP TABLE IF EXISTS cache_entries"))
            
            conn.commit()
        
        print("✓ 缓存条目表删除完成")


if __name__ == '__main__':
    upgrade()