#!/usr/bin/env python3
"""
调试分页问题
"""
from app import create_app
from services.historical_trade_service import HistoricalTradeService
import requests

def test_service_layer():
    """测试服务层"""
    app = create_app()
    
    with app.app_context():
        print("=== 服务层测试 ===")
        
        # 测试带分页的排序
        result = HistoricalTradeService.get_historical_trades(
            filters={},
            page=1,
            per_page=20,
            sort_by='return_rate',
            sort_order='desc'
        )
        
        trades = result.get('trades', [])
        print(f"服务层返回记录数: {len(trades)}")
        print(f"总记录数: {result.get('total', 0)}")
        print(f"当前页: {result.get('current_page', 'N/A')}")
        
        if trades:
            print("\n前5条记录的收益率:")
            for i, trade in enumerate(trades[:5]):
                return_rate = trade.get('return_rate', 0)
                print(f"  {i+1}. {trade.get('stock_code')} - {return_rate:.6f}")

def test_api_layer():
    """测试API层"""
    print("\n=== API层测试 ===")
    
    params = {
        'page': 1,
        'per_page': 20,
        'sort_by': 'return_rate',
        'sort_order': 'desc'
    }
    
    try:
        response = requests.get(
            "http://localhost:5001/api/historical-trades",
            params=params,
            timeout=10
        )
        
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                trades_data = data.get('data', {})
                trades = trades_data.get('trades', [])
                
                print(f"API返回记录数: {len(trades)}")
                print(f"总记录数: {trades_data.get('total', 0)}")
                print(f"当前页: {trades_data.get('current_page', 'N/A')}")
                
                if trades:
                    print("\n前5条记录的收益率:")
                    for i, trade in enumerate(trades[:5]):
                        return_rate = trade.get('return_rate', 0)
                        print(f"  {i+1}. {trade.get('stock_code')} - {return_rate:.6f}")
            else:
                print(f"API错误: {data.get('message')}")
        else:
            print(f"HTTP错误: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")

def test_direct_query():
    """直接测试数据库查询"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 直接数据库查询测试 ===")
        
        from models.historical_trade import HistoricalTrade
        from sqlalchemy import desc
        
        # 直接查询前20条记录
        trades = HistoricalTrade.query.order_by(desc(HistoricalTrade.return_rate)).limit(20).all()
        
        print(f"数据库查询返回记录数: {len(trades)}")
        
        if trades:
            print("\n前5条记录的收益率:")
            for i, trade in enumerate(trades[:5]):
                print(f"  {i+1}. {trade.stock_code} - {trade.return_rate:.6f}")

if __name__ == "__main__":
    # 测试服务层
    test_service_layer()
    
    # 测试API层
    test_api_layer()
    
    # 测试数据库查询
    test_direct_query()