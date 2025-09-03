#!/usr/bin/env python3
"""
调试后端排序问题的脚本
"""
from app import create_app
from services.historical_trade_service import HistoricalTradeService
from models.historical_trade import HistoricalTrade
from extensions import db

def test_backend_sorting():
    """测试后端排序功能"""
    app = create_app()
    
    with app.app_context():
        print("=== 后端排序功能测试 ===\n")
        
        # 测试不同的排序参数
        test_cases = [
            {
                'name': '按收益率降序',
                'sort_by': 'return_rate',
                'sort_order': 'desc'
            },
            {
                'name': '按收益率升序',
                'sort_by': 'return_rate',
                'sort_order': 'asc'
            },
            {
                'name': '按股票代码升序',
                'sort_by': 'stock_code',
                'sort_order': 'asc'
            },
            {
                'name': '按持仓天数降序',
                'sort_by': 'holding_days',
                'sort_order': 'desc'
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"{i}. {test_case['name']}")
            print("-" * 50)
            
            try:
                # 调用服务方法
                result = HistoricalTradeService.get_historical_trades(
                    filters={},
                    page=1,
                    per_page=10,
                    sort_by=test_case['sort_by'],
                    sort_order=test_case['sort_order']
                )
                
                trades = result.get('trades', [])
                print(f"返回记录数: {len(trades)}")
                
                if trades:
                    print(f"排序字段: {test_case['sort_by']}")
                    print(f"排序方向: {test_case['sort_order']}")
                    print("\n前5条记录的排序字段值:")
                    
                    for j, trade in enumerate(trades[:5]):
                        sort_value = trade.get(test_case['sort_by'])
                        print(f"  {j+1}. {trade.get('stock_code', 'N/A')} - {test_case['sort_by']}: {sort_value}")
                    
                    # 验证排序是否正确
                    is_sorted = verify_sorting(trades, test_case['sort_by'], test_case['sort_order'])
                    print(f"\n排序验证: {'✅ 正确' if is_sorted else '❌ 错误'}")
                    
                    if not is_sorted:
                        print("排序错误详情:")
                        show_sorting_errors(trades, test_case['sort_by'], test_case['sort_order'])
                else:
                    print("没有返回任何记录")
                    
            except Exception as e:
                print(f"❌ 测试失败: {e}")
            
            print("\n" + "=" * 60 + "\n")

def verify_sorting(trades, sort_by, sort_order):
    """验证排序是否正确"""
    if len(trades) < 2:
        return True
    
    for i in range(len(trades) - 1):
        current_val = trades[i].get(sort_by)
        next_val = trades[i + 1].get(sort_by)
        
        # 处理None值
        if current_val is None:
            current_val = 0
        if next_val is None:
            next_val = 0
        
        if sort_order.lower() == 'desc':
            if current_val < next_val:
                return False
        else:  # asc
            if current_val > next_val:
                return False
    
    return True

def show_sorting_errors(trades, sort_by, sort_order):
    """显示排序错误的详细信息"""
    for i in range(len(trades) - 1):
        current_val = trades[i].get(sort_by)
        next_val = trades[i + 1].get(sort_by)
        
        # 处理None值
        if current_val is None:
            current_val = 0
        if next_val is None:
            next_val = 0
        
        is_error = False
        if sort_order.lower() == 'desc':
            if current_val < next_val:
                is_error = True
        else:  # asc
            if current_val > next_val:
                is_error = True
        
        if is_error:
            print(f"  位置 {i+1}-{i+2}: {current_val} -> {next_val} (应该是 {'降序' if sort_order.lower() == 'desc' else '升序'})")

def test_direct_query():
    """直接测试数据库查询"""
    app = create_app()
    
    with app.app_context():
        print("=== 直接数据库查询测试 ===\n")
        
        # 测试直接查询
        from sqlalchemy import desc, asc
        
        print("1. 按收益率降序 (直接查询)")
        trades = HistoricalTrade.query.order_by(desc(HistoricalTrade.return_rate)).limit(5).all()
        
        print("前5条记录:")
        for i, trade in enumerate(trades):
            print(f"  {i+1}. {trade.stock_code} - 收益率: {trade.return_rate}")
        
        print("\n2. 按收益率升序 (直接查询)")
        trades = HistoricalTrade.query.order_by(asc(HistoricalTrade.return_rate)).limit(5).all()
        
        print("前5条记录:")
        for i, trade in enumerate(trades):
            print(f"  {i+1}. {trade.stock_code} - 收益率: {trade.return_rate}")
        
        print("\n3. 检查数据库中的实际数据")
        total_count = HistoricalTrade.query.count()
        print(f"总记录数: {total_count}")
        
        # 检查收益率的分布
        max_return = db.session.query(db.func.max(HistoricalTrade.return_rate)).scalar()
        min_return = db.session.query(db.func.min(HistoricalTrade.return_rate)).scalar()
        avg_return = db.session.query(db.func.avg(HistoricalTrade.return_rate)).scalar()
        
        print(f"收益率范围: {min_return} ~ {max_return}")
        print(f"平均收益率: {avg_return}")

if __name__ == "__main__":
    print("开始调试后端排序问题...\n")
    
    # 测试服务层排序
    test_backend_sorting()
    
    print("\n" + "=" * 80 + "\n")
    
    # 测试直接数据库查询
    test_direct_query()
    
    print("\n调试完成！")