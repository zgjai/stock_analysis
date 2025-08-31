#!/usr/bin/env python3
"""
更新收益分布配置脚本
按照用户要求的具体区间重新配置收益分布
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.profit_distribution_config import ProfitDistributionConfig


def update_profit_distribution_configs():
    """更新收益分布配置为用户指定的区间"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 开始更新收益分布配置...")
            
            # 1. 删除现有配置
            print("1. 删除现有配置...")
            deleted_count = ProfitDistributionConfig.query.delete()
            print(f"   删除了 {deleted_count} 个现有配置")
            
            # 2. 创建新的配置（按用户要求的具体区间）
            print("2. 创建新的收益分布区间配置...")
            new_configs = [
                {
                    'range_name': '(负无穷,-10%)',
                    'min_profit_rate': None,
                    'max_profit_rate': -0.1,
                    'sort_order': 1,
                    'is_active': True,
                    'created_by': 'system_update'
                },
                {
                    'range_name': '[-10%,-5%)',
                    'min_profit_rate': -0.1,
                    'max_profit_rate': -0.05,
                    'sort_order': 2,
                    'is_active': True,
                    'created_by': 'system_update'
                },
                {
                    'range_name': '[-5%,-3%)',
                    'min_profit_rate': -0.05,
                    'max_profit_rate': -0.03,
                    'sort_order': 3,
                    'is_active': True,
                    'created_by': 'system_update'
                },
                {
                    'range_name': '[-3%,-1%)',
                    'min_profit_rate': -0.03,
                    'max_profit_rate': -0.01,
                    'sort_order': 4,
                    'is_active': True,
                    'created_by': 'system_update'
                },
                {
                    'range_name': '[-1%,0%)',
                    'min_profit_rate': -0.01,
                    'max_profit_rate': 0,
                    'sort_order': 5,
                    'is_active': True,
                    'created_by': 'system_update'
                },
                {
                    'range_name': '[0%,2%)',
                    'min_profit_rate': 0,
                    'max_profit_rate': 0.02,
                    'sort_order': 6,
                    'is_active': True,
                    'created_by': 'system_update'
                },
                {
                    'range_name': '[2%,5%)',
                    'min_profit_rate': 0.02,
                    'max_profit_rate': 0.05,
                    'sort_order': 7,
                    'is_active': True,
                    'created_by': 'system_update'
                },
                {
                    'range_name': '[5%,10%)',
                    'min_profit_rate': 0.05,
                    'max_profit_rate': 0.1,
                    'sort_order': 8,
                    'is_active': True,
                    'created_by': 'system_update'
                },
                {
                    'range_name': '[10%,15%)',
                    'min_profit_rate': 0.1,
                    'max_profit_rate': 0.15,
                    'sort_order': 9,
                    'is_active': True,
                    'created_by': 'system_update'
                },
                {
                    'range_name': '[15%,20%)',
                    'min_profit_rate': 0.15,
                    'max_profit_rate': 0.2,
                    'sort_order': 10,
                    'is_active': True,
                    'created_by': 'system_update'
                },
                {
                    'range_name': '[20%,正无穷)',
                    'min_profit_rate': 0.2,
                    'max_profit_rate': None,
                    'sort_order': 11,
                    'is_active': True,
                    'created_by': 'system_update'
                }
            ]
            
            # 创建新配置
            created_count = 0
            for config_data in new_configs:
                config = ProfitDistributionConfig(**config_data)
                db.session.add(config)
                created_count += 1
                print(f"   创建配置: {config_data['range_name']}")
            
            # 3. 提交更改
            db.session.commit()
            print(f"✅ 成功创建 {created_count} 个新的收益分布配置")
            
            # 4. 验证配置
            print("3. 验证新配置...")
            active_configs = ProfitDistributionConfig.get_active_configs()
            print(f"   活跃配置数量: {len(active_configs)}")
            
            print("\n📊 新的收益分布区间配置:")
            for config in active_configs:
                min_rate = f"{config.min_profit_rate*100:.1f}%" if config.min_profit_rate is not None else "负无穷"
                max_rate = f"{config.max_profit_rate*100:.1f}%" if config.max_profit_rate is not None else "正无穷"
                print(f"   {config.sort_order:2d}. {config.range_name} ({min_rate} 到 {max_rate})")
            
            print("\n🎨 颜色配置说明:")
            print("   - 负收益区间: 绿色系 (越亏损越深绿)")
            print("   - 正收益区间: 红色系 (越盈利越深红)")
            
            print("\n✅ 收益分布配置更新完成!")
            print("💡 提示: 重新访问统计分析页面查看新的收益分布图表")
            
        except Exception as e:
            print(f"❌ 更新配置失败: {str(e)}")
            db.session.rollback()
            return False
    
    return True


if __name__ == '__main__':
    success = update_profit_distribution_configs()
    if success:
        print("\n🎉 配置更新成功! 现在可以在统计分析页面查看按具体收益率区间的分布图表。")
    else:
        print("\n💥 配置更新失败，请检查错误信息。")
        sys.exit(1)