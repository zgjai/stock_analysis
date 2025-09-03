#!/usr/bin/env python3
"""
测试历史交易排序功能
"""
import requests
import json
from datetime import datetime

def test_historical_trades_api():
    """测试历史交易API的排序功能"""
    base_url = "http://localhost:5000/api"
    
    # 测试不同的排序参数
    test_cases = [
        {
            "name": "按收益率降序排序",
            "params": {
                "sort_by": "return_rate",
                "sort_order": "desc",
                "per_page": 5
            }
        },
        {
            "name": "按收益率升序排序", 
            "params": {
                "sort_by": "return_rate",
                "sort_order": "asc",
                "per_page": 5
            }
        },
        {
            "name": "按完成日期降序排序",
            "params": {
                "sort_by": "completion_date",
                "sort_order": "desc",
                "per_page": 5
            }
        },
        {
            "name": "按股票代码升序排序",
            "params": {
                "sort_by": "stock_code",
                "sort_order": "asc",
                "per_page": 5
            }
        },
        {
            "name": "按持仓天数降序排序",
            "params": {
                "sort_by": "holding_days",
                "sort_order": "desc",
                "per_page": 5
            }
        }
    ]
    
    print("=== 历史交易排序功能测试 ===\n")
    
    for test_case in test_cases:
        print(f"测试: {test_case['name']}")
        print(f"参数: {test_case['params']}")
        
        try:
            response = requests.get(
                f"{base_url}/historical-trades",
                params=test_case['params'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    trades = data.get('data', {}).get('trades', [])
                    print(f"✓ 成功获取 {len(trades)} 条记录")
                    
                    if trades:
                        print("前3条记录:")
                        for i, trade in enumerate(trades[:3]):
                            sort_field = test_case['params']['sort_by']
                            sort_value = trade.get(sort_field, 'N/A')
                            
                            # 格式化显示值
                            if sort_field == 'return_rate':
                                sort_value = f"{float(sort_value) * 100:.2f}%" if sort_value != 'N/A' else 'N/A'
                            elif sort_field in ['total_investment', 'total_return']:
                                sort_value = f"¥{float(sort_value):,.2f}" if sort_value != 'N/A' else 'N/A'
                            elif sort_field == 'completion_date':
                                if sort_value != 'N/A':
                                    sort_value = datetime.fromisoformat(sort_value.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                            
                            print(f"  {i+1}. {trade.get('stock_code', 'N/A')} - {sort_field}: {sort_value}")
                    else:
                        print("  无数据")
                else:
                    print(f"✗ API返回错误: {data.get('message', '未知错误')}")
            else:
                print(f"✗ HTTP错误: {response.status_code}")
                print(f"  响应: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ 请求失败: {str(e)}")
        
        print("-" * 50)
    
    # 测试统计信息API
    print("\n=== 统计信息测试 ===")
    try:
        response = requests.get(f"{base_url}/historical-trades/statistics", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('data', {})
                print("✓ 统计信息获取成功:")
                print(f"  总交易数: {stats.get('total_trades', 0)}")
                print(f"  盈利交易: {stats.get('profitable_trades', 0)}")
                print(f"  胜率: {stats.get('win_rate', 0)}%")
                print(f"  总收益: ¥{stats.get('total_return', 0):,.2f}")
                print(f"  平均收益率: {stats.get('avg_return_rate', 0):.2f}%")
                print(f"  平均持仓天数: {stats.get('avg_holding_days', 0):.1f}天")
            else:
                print(f"✗ 统计信息API返回错误: {data.get('message', '未知错误')}")
        else:
            print(f"✗ 统计信息HTTP错误: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ 统计信息请求失败: {str(e)}")

def test_sorting_logic():
    """测试排序逻辑"""
    print("\n=== 排序逻辑测试 ===")
    
    # 模拟数据
    test_data = [
        {"stock_code": "002484", "return_rate": 0.1996, "holding_days": 4},
        {"stock_code": "002738", "return_rate": 0.0198, "holding_days": 5},
        {"stock_code": "688255", "return_rate": -0.0448, "holding_days": 1},
        {"stock_code": "603271", "return_rate": -0.0020, "holding_days": 6},
    ]
    
    # 测试按收益率降序排序
    sorted_by_return_desc = sorted(test_data, key=lambda x: x['return_rate'], reverse=True)
    print("按收益率降序排序:")
    for item in sorted_by_return_desc:
        print(f"  {item['stock_code']}: {item['return_rate']*100:.2f}%")
    
    # 测试按持仓天数升序排序
    sorted_by_days_asc = sorted(test_data, key=lambda x: x['holding_days'])
    print("\n按持仓天数升序排序:")
    for item in sorted_by_days_asc:
        print(f"  {item['stock_code']}: {item['holding_days']}天")

if __name__ == "__main__":
    # 首先测试排序逻辑
    test_sorting_logic()
    
    # 然后测试API
    test_historical_trades_api()