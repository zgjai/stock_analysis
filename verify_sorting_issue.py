#!/usr/bin/env python3
"""
直接验证收益率倒序排序问题
"""
import requests
import json

def test_return_rate_desc():
    """测试收益率倒序排序"""
    base_url = "http://localhost:5001/api"
    
    print("=== 收益率倒序排序验证 ===\n")
    
    # 发送收益率倒序请求
    params = {
        'page': 1,
        'per_page': 10,
        'sort_by': 'return_rate',
        'sort_order': 'desc'
    }
    
    try:
        response = requests.get(
            f"{base_url}/historical-trades",
            params=params,
            timeout=10
        )
        
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                trades = data.get('data', {}).get('trades', [])
                
                print(f"返回记录数: {len(trades)}")
                print("\n前5条记录的收益率:")
                print("-" * 60)
                print("序号 | 股票代码 | 收益率     | 收益率(小数)")
                print("-" * 60)
                
                for i, trade in enumerate(trades[:5]):
                    return_rate = trade.get('return_rate', 0)
                    return_rate_percent = return_rate * 100
                    print(f"{i+1:2d}   | {trade.get('stock_code', 'N/A'):8} | {return_rate_percent:8.2f}% | {return_rate:.6f}")
                
                print("-" * 60)
                
                # 验证排序
                if len(trades) > 1:
                    is_sorted = True
                    for i in range(len(trades) - 1):
                        current_rate = trades[i].get('return_rate', 0)
                        next_rate = trades[i + 1].get('return_rate', 0)
                        
                        if current_rate < next_rate:
                            is_sorted = False
                            print(f"\n❌ 排序错误发现在位置 {i+1}-{i+2}:")
                            print(f"   {trades[i].get('stock_code')} ({current_rate:.6f}) < {trades[i+1].get('stock_code')} ({next_rate:.6f})")
                            break
                    
                    if is_sorted:
                        print("\n✅ 排序正确：收益率确实是降序排列")
                    else:
                        print("\n❌ 排序错误：收益率不是降序排列")
                        
                        # 显示所有记录的收益率
                        print("\n所有记录的收益率:")
                        for i, trade in enumerate(trades):
                            return_rate = trade.get('return_rate', 0)
                            print(f"{i+1:2d}. {trade.get('stock_code'):8} - {return_rate:.6f}")
                
            else:
                print(f"API返回错误: {data.get('message', '未知错误')}")
        else:
            print(f"HTTP错误 {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")

def test_raw_database():
    """直接测试数据库查询"""
    print("\n=== 直接数据库查询验证 ===\n")
    
    try:
        from app import create_app
        from models.historical_trade import HistoricalTrade
        from sqlalchemy import desc
        
        app = create_app()
        with app.app_context():
            # 直接查询数据库
            trades = HistoricalTrade.query.order_by(desc(HistoricalTrade.return_rate)).limit(5).all()
            
            print("数据库直接查询结果（收益率降序）:")
            print("-" * 60)
            print("序号 | 股票代码 | 收益率     | 收益率(小数)")
            print("-" * 60)
            
            for i, trade in enumerate(trades):
                return_rate_percent = trade.return_rate * 100
                print(f"{i+1:2d}   | {trade.stock_code:8} | {return_rate_percent:8.2f}% | {trade.return_rate:.6f}")
            
            print("-" * 60)
            
    except Exception as e:
        print(f"数据库查询失败: {e}")

if __name__ == "__main__":
    # 测试API
    test_return_rate_desc()
    
    # 测试数据库
    test_raw_database()