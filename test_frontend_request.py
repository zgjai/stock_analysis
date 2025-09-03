#!/usr/bin/env python3
"""
模拟前端请求的测试脚本
"""
import requests
import json

def test_frontend_request():
    """模拟前端的确切请求"""
    base_url = "http://localhost:5001/api"
    
    print("=== 模拟前端请求测试 ===\n")
    
    # 模拟前端的确切请求参数
    test_cases = [
        {
            'name': '初始加载（默认排序）',
            'params': {
                'page': 1,
                'per_page': 20,
                'sort_by': 'completion_date',
                'sort_order': 'desc'
            }
        },
        {
            'name': '按收益率降序排序',
            'params': {
                'page': 1,
                'per_page': 20,
                'sort_by': 'return_rate',
                'sort_order': 'desc'
            }
        },
        {
            'name': '按收益率升序排序',
            'params': {
                'page': 1,
                'per_page': 20,
                'sort_by': 'return_rate',
                'sort_order': 'asc'
            }
        },
        {
            'name': '按股票代码升序排序',
            'params': {
                'page': 1,
                'per_page': 20,
                'sort_by': 'stock_code',
                'sort_order': 'asc'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print("-" * 50)
        
        try:
            # 发送请求
            response = requests.get(
                f"{base_url}/historical-trades",
                params=test_case['params'],
                timeout=10
            )
            
            print(f"请求URL: {response.url}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    trades_data = data.get('data', {})
                    trades = trades_data.get('trades', [])
                    
                    print(f"总记录数: {trades_data.get('total', 0)}")
                    print(f"当前页: {trades_data.get('current_page', 'N/A')}")
                    print(f"每页数量: {trades_data.get('per_page', 'N/A')}")
                    print(f"总页数: {trades_data.get('pages', 'N/A')}")
                    print(f"返回记录数: {len(trades)}")
                    
                    if trades:
                        sort_by = test_case['params']['sort_by']
                        sort_order = test_case['params']['sort_order']
                        
                        print(f"\n前10条记录的 {sort_by} 值:")
                        for j, trade in enumerate(trades[:10]):
                            sort_value = trade.get(sort_by)
                            if sort_by == 'return_rate' and sort_value is not None:
                                display_value = f"{sort_value:.4f} ({sort_value * 100:.2f}%)"
                            else:
                                display_value = sort_value
                            print(f"  {j+1:2d}. {trade.get('stock_code', 'N/A')} - {sort_by}: {display_value}")
                        
                        # 验证排序
                        is_sorted = verify_sorting(trades, sort_by, sort_order)
                        print(f"\n排序验证: {'✅ 正确' if is_sorted else '❌ 错误'}")
                        
                        if not is_sorted:
                            print("排序错误详情:")
                            show_sorting_errors(trades, sort_by, sort_order)
                    else:
                        print("没有返回任何记录")
                else:
                    print(f"API返回错误: {data.get('message', '未知错误')}")
            else:
                print(f"HTTP错误: {response.text}")
                
        except Exception as e:
            print(f"请求错误: {e}")
        
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
            current_val = 0 if sort_by in ['return_rate', 'total_return', 'total_investment', 'holding_days'] else ''
        if next_val is None:
            next_val = 0 if sort_by in ['return_rate', 'total_return', 'total_investment', 'holding_days'] else ''
        
        # 根据字段类型进行比较
        if sort_by in ['return_rate', 'total_return', 'total_investment', 'holding_days']:
            try:
                current_val = float(current_val)
                next_val = float(next_val)
            except (ValueError, TypeError):
                current_val = 0
                next_val = 0
        else:
            current_val = str(current_val)
            next_val = str(next_val)
        
        if sort_order.lower() == 'desc':
            if current_val < next_val:
                return False
        else:  # asc
            if current_val > next_val:
                return False
    
    return True

def show_sorting_errors(trades, sort_by, sort_order):
    """显示排序错误的详细信息"""
    error_count = 0
    for i in range(len(trades) - 1):
        current_val = trades[i].get(sort_by)
        next_val = trades[i + 1].get(sort_by)
        
        # 处理None值
        if current_val is None:
            current_val = 0 if sort_by in ['return_rate', 'total_return', 'total_investment', 'holding_days'] else ''
        if next_val is None:
            next_val = 0 if sort_by in ['return_rate', 'total_return', 'total_investment', 'holding_days'] else ''
        
        # 根据字段类型进行比较
        if sort_by in ['return_rate', 'total_return', 'total_investment', 'holding_days']:
            try:
                current_val_cmp = float(current_val)
                next_val_cmp = float(next_val)
            except (ValueError, TypeError):
                current_val_cmp = 0
                next_val_cmp = 0
        else:
            current_val_cmp = str(current_val)
            next_val_cmp = str(next_val)
        
        is_error = False
        if sort_order.lower() == 'desc':
            if current_val_cmp < next_val_cmp:
                is_error = True
        else:  # asc
            if current_val_cmp > next_val_cmp:
                is_error = True
        
        if is_error:
            error_count += 1
            if error_count <= 5:  # 只显示前5个错误
                print(f"  位置 {i+1}-{i+2}: {current_val} -> {next_val} (应该是 {'降序' if sort_order.lower() == 'desc' else '升序'})")
    
    if error_count > 5:
        print(f"  ... 还有 {error_count - 5} 个排序错误")

if __name__ == "__main__":
    print("开始模拟前端请求测试...\n")
    test_frontend_request()
    print("测试完成！")