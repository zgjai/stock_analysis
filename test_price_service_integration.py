#!/usr/bin/env python3
"""
测试价格服务集成和持仓价格显示修复
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from services.price_service import PriceService
from services.review_service import HoldingService
from models.trade_record import TradeRecord
from datetime import date, datetime
import json

def test_price_service():
    """测试价格服务功能"""
    print("=== 测试价格服务功能 ===\n")
    
    app = create_app()
    with app.app_context():
        price_service = PriceService()
        
        # 测试股票代码
        test_stock_codes = ['000776', '000001', '000002']
        
        print("1. 测试获取股票价格:")
        for stock_code in test_stock_codes:
            try:
                print(f"\n测试股票: {stock_code}")
                
                # 尝试获取最新价格
                latest_price = price_service.get_latest_price(stock_code)
                if latest_price:
                    print(f"  ✅ 缓存价格: {latest_price['current_price']} ({latest_price['stock_name']})")
                else:
                    print(f"  ⚠️  无缓存价格，尝试刷新...")
                    
                    # 刷新价格
                    result = price_service.refresh_stock_price(stock_code, force_refresh=True)
                    if result['success']:
                        print(f"  ✅ 刷新成功: {result['data']['current_price']} ({result['data']['stock_name']})")
                    else:
                        print(f"  ❌ 刷新失败")
                        
            except Exception as e:
                print(f"  ❌ 错误: {e}")

def test_holding_service():
    """测试持仓服务功能"""
    print("\n=== 测试持仓服务功能 ===\n")
    
    app = create_app()
    with app.app_context():
        print("1. 测试获取当前持仓:")
        try:
            holdings = HoldingService.get_current_holdings()
            
            if holdings:
                print(f"  ✅ 获取到 {len(holdings)} 个持仓")
                
                for holding in holdings[:3]:  # 只显示前3个
                    print(f"\n  股票: {holding['stock_code']} - {holding['stock_name']}")
                    print(f"    成本价: {holding.get('avg_buy_price', 'N/A')}")
                    print(f"    当前价: {holding.get('current_price', 'N/A')}")
                    print(f"    持仓量: {holding.get('current_quantity', 'N/A')}")
                    print(f"    持仓天数: {holding.get('holding_days', 'N/A')}")
                    
                    # 检查字段完整性
                    required_fields = ['stock_code', 'stock_name', 'avg_buy_price', 'current_price', 'current_quantity']
                    missing_fields = [field for field in required_fields if field not in holding or holding[field] is None]
                    if missing_fields:
                        print(f"    ⚠️  缺失字段: {missing_fields}")
                    else:
                        print(f"    ✅ 字段完整")
            else:
                print("  ⚠️  暂无持仓数据")
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")

def test_trade_records():
    """测试交易记录数据"""
    print("\n=== 测试交易记录数据 ===\n")
    
    app = create_app()
    with app.app_context():
        print("1. 检查交易记录:")
        try:
            # 获取所有买入记录
            buy_records = TradeRecord.query.filter_by(trade_type='buy', is_corrected=False).all()
            
            if buy_records:
                print(f"  ✅ 找到 {len(buy_records)} 条买入记录")
                
                # 按股票代码分组
                stock_groups = {}
                for record in buy_records:
                    if record.stock_code not in stock_groups:
                        stock_groups[record.stock_code] = []
                    stock_groups[record.stock_code].append(record)
                
                print(f"  涉及 {len(stock_groups)} 只股票:")
                for stock_code, records in list(stock_groups.items())[:5]:  # 只显示前5个
                    total_quantity = sum(r.quantity for r in records)
                    avg_price = sum(r.price * r.quantity for r in records) / total_quantity
                    print(f"    {stock_code}: {len(records)}笔交易, 总量{total_quantity}, 均价{avg_price:.2f}")
            else:
                print("  ⚠️  暂无买入记录")
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")

def create_test_data():
    """创建测试数据"""
    print("\n=== 创建测试数据 ===\n")
    
    app = create_app()
    with app.app_context():
        try:
            # 检查是否已有测试数据
            existing_record = TradeRecord.query.filter_by(stock_code='000776').first()
            if existing_record:
                print("  ✅ 测试数据已存在")
                return
            
            # 创建测试交易记录
            test_trade = TradeRecord(
                stock_code='000776',
                stock_name='广发证券',
                trade_type='buy',
                price=10.50,
                quantity=500,
                trade_date=datetime.now(),
                reason='测试买入',
                is_corrected=False
            )
            
            db.session.add(test_trade)
            db.session.commit()
            
            print("  ✅ 创建测试数据成功")
            
        except Exception as e:
            print(f"  ❌ 创建测试数据失败: {e}")
            db.session.rollback()

def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===\n")
    
    app = create_app()
    with app.test_client() as client:
        print("1. 测试持仓API:")
        try:
            response = client.get('/api/holdings')
            data = response.get_json()
            
            if response.status_code == 200 and data.get('success'):
                print(f"  ✅ API调用成功，返回 {len(data.get('data', []))} 个持仓")
                
                if data['data']:
                    holding = data['data'][0]
                    print(f"  示例数据结构:")
                    for key, value in holding.items():
                        print(f"    {key}: {value}")
            else:
                print(f"  ❌ API调用失败: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        
        print("\n2. 测试价格API:")
        try:
            response = client.get('/api/prices/000776/latest')
            data = response.get_json()
            
            if response.status_code == 200 and data.get('success'):
                print(f"  ✅ 价格API调用成功")
                print(f"  价格数据: {data.get('data')}")
            else:
                print(f"  ⚠️  价格API返回: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")

def main():
    """主函数"""
    print("股票价格显示修复测试")
    print("=" * 50)
    
    # 创建测试数据
    create_test_data()
    
    # 测试各个组件
    test_trade_records()
    test_price_service()
    test_holding_service()
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n建议:")
    print("1. 如果价格获取失败，检查网络连接和AKShare服务状态")
    print("2. 如果持仓数据缺失字段，检查HoldingService的实现")
    print("3. 访问 /test_price_display_fix.html 进行前端测试")

if __name__ == "__main__":
    main()