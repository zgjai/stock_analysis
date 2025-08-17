#!/usr/bin/env python3
"""
股票价格服务演示脚本
"""
import sys
import os
from datetime import date

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from services.price_service import PriceService
from models.stock_price import StockPrice


def demo_price_service():
    """演示价格服务功能"""
    print("=== 股票价格服务演示 ===\n")
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        # 初始化价格服务
        price_service = PriceService()
        
        # 演示股票代码
        demo_stocks = ['000001', '000002', '600000']
        
        print("1. 检查缓存状态")
        cache_status = price_service.get_cache_status(demo_stocks)
        print(f"总股票数: {cache_status['total_stocks']}")
        print(f"今日已缓存: {cache_status['cached_today']}")
        print(f"需要刷新: {cache_status['need_refresh']}")
        print()
        
        print("2. 模拟价格数据（因为AKShare需要网络连接）")
        # 手动创建一些测试数据
        test_data = [
            {'stock_code': '000001', 'stock_name': '平安银行', 'price': 12.50, 'change': 2.5},
            {'stock_code': '000002', 'stock_name': '万科A', 'price': 20.80, 'change': 1.2},
            {'stock_code': '600000', 'stock_name': '浦发银行', 'price': 8.90, 'change': -0.8}
        ]
        
        today = date.today()
        for data in test_data:
            price_record = StockPrice.update_or_create(
                stock_code=data['stock_code'],
                stock_name=data['stock_name'],
                current_price=data['price'],
                change_percent=data['change'],
                record_date=today
            )
            print(f"创建价格记录: {data['stock_code']} - {data['stock_name']} - ¥{data['price']}")
        print()
        
        print("3. 获取单个股票价格")
        price_data = price_service.get_stock_price('000001', today)
        if price_data:
            print(f"股票代码: {price_data['stock_code']}")
            print(f"股票名称: {price_data['stock_name']}")
            print(f"当前价格: ¥{price_data['current_price']}")
            print(f"涨跌幅: {price_data['change_percent']}%")
        print()
        
        print("4. 获取最新价格")
        latest_price = price_service.get_latest_price('000002')
        if latest_price:
            print(f"最新价格: {latest_price['stock_name']} - ¥{latest_price['current_price']}")
        print()
        
        print("5. 获取价格历史")
        history = price_service.get_price_history('000001', 5)
        print(f"价格历史记录数: {len(history)}")
        for record in history:
            print(f"  {record['record_date']}: ¥{record['current_price']} ({record['change_percent']}%)")
        print()
        
        print("6. 再次检查缓存状态")
        cache_status = price_service.get_cache_status(demo_stocks)
        print(f"今日已缓存: {cache_status['cached_today']}")
        print(f"需要刷新: {cache_status['need_refresh']}")
        
        for detail in cache_status['details']:
            print(f"  {detail['stock_code']}: {detail['status']}")
        print()
        
        print("7. 数据去重测试")
        print("尝试重复创建今日价格记录...")
        duplicate_record = StockPrice.update_or_create(
            stock_code='000001',
            stock_name='平安银行',
            current_price=12.80,  # 更新价格
            change_percent=3.0,   # 更新涨跌幅
            record_date=today
        )
        print(f"更新后价格: ¥{duplicate_record.current_price}")
        
        # 验证数据库中只有一条记录
        all_records = StockPrice.query.filter_by(stock_code='000001', record_date=today).all()
        print(f"数据库中000001今日记录数: {len(all_records)}")
        print()
        
        print("=== 演示完成 ===")


if __name__ == '__main__':
    demo_price_service()