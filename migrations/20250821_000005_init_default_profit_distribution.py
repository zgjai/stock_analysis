"""
创建默认收益分布区间配置的初始化脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db


def upgrade():
    """初始化默认收益分布配置"""
    print("初始化默认收益分布配置...")
    
    # 默认收益分布区间配置
    default_configs = [
        {
            'range_name': '严重亏损',
            'min_profit_rate': None,  # 无下限
            'max_profit_rate': -0.2000,  # -20%
            'sort_order': 1,
            'is_active': True,
            'created_by': 'system'
        },
        {
            'range_name': '中度亏损',
            'min_profit_rate': -0.2000,  # -20%
            'max_profit_rate': -0.1000,  # -10%
            'sort_order': 2,
            'is_active': True,
            'created_by': 'system'
        },
        {
            'range_name': '轻微亏损',
            'min_profit_rate': -0.1000,  # -10%
            'max_profit_rate': -0.0500,  # -5%
            'sort_order': 3,
            'is_active': True,
            'created_by': 'system'
        },
        {
            'range_name': '小幅亏损',
            'min_profit_rate': -0.0500,  # -5%
            'max_profit_rate': 0.0000,   # 0%
            'sort_order': 4,
            'is_active': True,
            'created_by': 'system'
        },
        {
            'range_name': '盈亏平衡',
            'min_profit_rate': 0.0000,   # 0%
            'max_profit_rate': 0.0500,   # 5%
            'sort_order': 5,
            'is_active': True,
            'created_by': 'system'
        },
        {
            'range_name': '小幅盈利',
            'min_profit_rate': 0.0500,   # 5%
            'max_profit_rate': 0.1000,   # 10%
            'sort_order': 6,
            'is_active': True,
            'created_by': 'system'
        },
        {
            'range_name': '中等盈利',
            'min_profit_rate': 0.1000,   # 10%
            'max_profit_rate': 0.2000,   # 20%
            'sort_order': 7,
            'is_active': True,
            'created_by': 'system'
        },
        {
            'range_name': '良好盈利',
            'min_profit_rate': 0.2000,   # 20%
            'max_profit_rate': 0.3000,   # 30%
            'sort_order': 8,
            'is_active': True,
            'created_by': 'system'
        },
        {
            'range_name': '优秀盈利',
            'min_profit_rate': 0.3000,   # 30%
            'max_profit_rate': 0.5000,   # 50%
            'sort_order': 9,
            'is_active': True,
            'created_by': 'system'
        },
        {
            'range_name': '卓越盈利',
            'min_profit_rate': 0.5000,   # 50%
            'max_profit_rate': None,     # 无上限
            'sort_order': 10,
            'is_active': True,
            'created_by': 'system'
        }
    ]
    
    with db.engine.connect() as conn:
        # 检查是否已有配置数据
        result = conn.execute(db.text("""
            SELECT COUNT(*) as count FROM profit_distribution_configs
        """))
        
        existing_count = result.fetchone()[0]
        
        if existing_count == 0:
            print("添加默认收益分布配置...")
            
            # 插入默认配置
            for config in default_configs:
                conn.execute(db.text("""
                    INSERT INTO profit_distribution_configs 
                    (range_name, min_profit_rate, max_profit_rate, sort_order, is_active, created_by)
                    VALUES (:range_name, :min_profit_rate, :max_profit_rate, :sort_order, :is_active, :created_by)
                """), config)
            
            conn.commit()
            print(f"成功添加 {len(default_configs)} 个默认收益分布配置")
        else:
            print(f"已存在 {existing_count} 个收益分布配置，跳过初始化")
    
    print("默认收益分布配置初始化完成")


def downgrade():
    """删除默认收益分布配置"""
    print("删除默认收益分布配置...")
    
    with db.engine.connect() as conn:
        # 删除系统创建的默认配置
        conn.execute(db.text("""
            DELETE FROM profit_distribution_configs 
            WHERE created_by = 'system'
        """))
        
        conn.commit()
    
    print("默认收益分布配置删除完成")


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