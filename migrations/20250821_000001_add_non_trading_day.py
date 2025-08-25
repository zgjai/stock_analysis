"""
添加非交易日表的数据库迁移脚本
"""
from datetime import date
from extensions import db
from models.non_trading_day import NonTradingDay


def upgrade():
    """执行迁移"""
    print("创建非交易日表...")
    
    # 创建表
    db.create_all()
    
    # 添加一些默认的节假日数据（2024年中国法定节假日）
    default_holidays = [
        # 2024年法定节假日
        {'date': date(2024, 1, 1), 'name': '元旦', 'description': '新年第一天'},
        {'date': date(2024, 2, 10), 'name': '春节', 'description': '农历新年第一天'},
        {'date': date(2024, 2, 11), 'name': '春节', 'description': '农历新年第二天'},
        {'date': date(2024, 2, 12), 'name': '春节', 'description': '农历新年第三天'},
        {'date': date(2024, 2, 13), 'name': '春节', 'description': '农历新年第四天'},
        {'date': date(2024, 2, 14), 'name': '春节', 'description': '农历新年第五天'},
        {'date': date(2024, 2, 15), 'name': '春节', 'description': '农历新年第六天'},
        {'date': date(2024, 2, 16), 'name': '春节', 'description': '农历新年第七天'},
        {'date': date(2024, 2, 17), 'name': '春节', 'description': '农历新年第八天'},
        {'date': date(2024, 4, 4), 'name': '清明节', 'description': '清明节'},
        {'date': date(2024, 4, 5), 'name': '清明节', 'description': '清明节'},
        {'date': date(2024, 4, 6), 'name': '清明节', 'description': '清明节'},
        {'date': date(2024, 5, 1), 'name': '劳动节', 'description': '国际劳动节'},
        {'date': date(2024, 5, 2), 'name': '劳动节', 'description': '劳动节假期'},
        {'date': date(2024, 5, 3), 'name': '劳动节', 'description': '劳动节假期'},
        {'date': date(2024, 5, 4), 'name': '劳动节', 'description': '劳动节假期'},
        {'date': date(2024, 5, 5), 'name': '劳动节', 'description': '劳动节假期'},
        {'date': date(2024, 6, 10), 'name': '端午节', 'description': '端午节'},
        {'date': date(2024, 9, 15), 'name': '中秋节', 'description': '中秋节'},
        {'date': date(2024, 9, 16), 'name': '中秋节', 'description': '中秋节假期'},
        {'date': date(2024, 9, 17), 'name': '中秋节', 'description': '中秋节假期'},
        {'date': date(2024, 10, 1), 'name': '国庆节', 'description': '国庆节第一天'},
        {'date': date(2024, 10, 2), 'name': '国庆节', 'description': '国庆节第二天'},
        {'date': date(2024, 10, 3), 'name': '国庆节', 'description': '国庆节第三天'},
        {'date': date(2024, 10, 4), 'name': '国庆节', 'description': '国庆节第四天'},
        {'date': date(2024, 10, 5), 'name': '国庆节', 'description': '国庆节第五天'},
        {'date': date(2024, 10, 6), 'name': '国庆节', 'description': '国庆节第六天'},
        {'date': date(2024, 10, 7), 'name': '国庆节', 'description': '国庆节第七天'},
        
        # 2025年部分节假日
        {'date': date(2025, 1, 1), 'name': '元旦', 'description': '新年第一天'},
        {'date': date(2025, 1, 28), 'name': '春节', 'description': '农历新年除夕'},
        {'date': date(2025, 1, 29), 'name': '春节', 'description': '农历新年第一天'},
        {'date': date(2025, 1, 30), 'name': '春节', 'description': '农历新年第二天'},
        {'date': date(2025, 1, 31), 'name': '春节', 'description': '农历新年第三天'},
        {'date': date(2025, 2, 1), 'name': '春节', 'description': '农历新年第四天'},
        {'date': date(2025, 2, 2), 'name': '春节', 'description': '农历新年第五天'},
        {'date': date(2025, 2, 3), 'name': '春节', 'description': '农历新年第六天'},
        {'date': date(2025, 4, 5), 'name': '清明节', 'description': '清明节'},
        {'date': date(2025, 5, 1), 'name': '劳动节', 'description': '国际劳动节'},
        {'date': date(2025, 5, 2), 'name': '劳动节', 'description': '劳动节假期'},
        {'date': date(2025, 5, 3), 'name': '劳动节', 'description': '劳动节假期'},
        {'date': date(2025, 5, 31), 'name': '端午节', 'description': '端午节'},
        {'date': date(2025, 10, 1), 'name': '国庆节', 'description': '国庆节第一天'},
        {'date': date(2025, 10, 2), 'name': '国庆节', 'description': '国庆节第二天'},
        {'date': date(2025, 10, 3), 'name': '国庆节', 'description': '国庆节第三天'},
        {'date': date(2025, 10, 4), 'name': '国庆节', 'description': '国庆节第四天'},
        {'date': date(2025, 10, 5), 'name': '国庆节', 'description': '国庆节第五天'},
        {'date': date(2025, 10, 6), 'name': '国庆节', 'description': '国庆节第六天'},
        {'date': date(2025, 10, 7), 'name': '国庆节', 'description': '国庆节第七天'},
    ]
    
    print("添加默认节假日数据...")
    added_count = 0
    
    for holiday_data in default_holidays:
        # 检查是否已存在
        existing = NonTradingDay.query.filter_by(date=holiday_data['date']).first()
        if not existing:
            holiday = NonTradingDay(
                date=holiday_data['date'],
                name=holiday_data['name'],
                type='holiday',
                description=holiday_data['description']
            )
            db.session.add(holiday)
            added_count += 1
    
    try:
        db.session.commit()
        print(f"成功添加 {added_count} 个默认节假日")
    except Exception as e:
        db.session.rollback()
        print(f"添加默认节假日失败: {str(e)}")
        raise e
    
    print("非交易日表创建完成")


def downgrade():
    """回滚迁移"""
    print("删除非交易日表...")
    
    # 删除表
    NonTradingDay.__table__.drop(db.engine)
    
    print("非交易日表删除完成")


if __name__ == '__main__':
    """直接运行此脚本进行迁移"""
    import sys
    import os
    
    # 添加项目根目录到Python路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        try:
            upgrade()
            print("迁移执行成功")
        except Exception as e:
            print(f"迁移执行失败: {str(e)}")
            sys.exit(1)