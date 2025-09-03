#!/usr/bin/env python3
"""
监控API请求的脚本
"""
import requests
import json
from datetime import datetime

def monitor_sorting_requests():
    """监控排序请求"""
    base_url = "http://localhost:5001/api"
    
    print("=== 实时API请求监控 ===")
    print("请在浏览器中操作排序功能，我将捕获实际的API请求和响应")
    print("按 Ctrl+C 停止监控\n")
    
    # 测试不同的排序参数组合
    test_cases = [
        {
            'name': '默认排序',
            'params': {'page': 1, 'per_page': 20}
        },
        {
            'name': '收益率降序',
            'params': {'page': 1, 'per_page': 20, 'sort_by': 'return_rate', 'sort_order': 'desc'}
        },
        {
            'name': '收益率升序', 
            'params': {'page': 1, 'per_page': 20, 'sort_by': 'return_rate', 'sort_order': 'asc'}
        },
        {
            'name': '股票代码升序',
            'params': {'page': 1, 'per_page': 20, 'sort_by': 'stock_code', 'sort_order': 'asc'}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"测试: {test_case['name']}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
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
                    trades = data.get('data', {}).get('trades', [])
                    pagination = data.get('data', {})
                    
                    print(f"总记录数: {pagination.get('total', 0)}")
                    print(f"当前页: {pagination.get('current_page', 'N/A')}")
                    print(f"返回记录数: {len(trades)}")
                    
                    if trades:
                        sort_by = test_case['params'].get('sort_by', 'completion_date')
                        sort_order = test_case['params'].get('sort_order', 'desc')
                        
                        print(f"\n排序字段: {sort_by}")
                        print(f"排序方向: {sort_order}")
                        print(f"\n前10条记录:")
                        print("-" * 80)
                        
                        for i, trade in enumerate(trades[:10]):
                            sort_value = trade.get(sort_by, 'N/A')
                            
                            # 格式化显示值
                            if sort_by == 'return_rate' and sort_value != 'N/A':
                                display_value = f"{sort_value:.6f} ({sort_value*100:.2f}%)"
                            elif sort_by in ['total_investment', 'total_return'] and sort_value != 'N/A':
                                display_value = f"¥{float(sort_value):.2f}"
                            else:
                                display_value = str(sort_value)
                            
                            print(f"{i+1:2d}. {trade.get('stock_code', 'N/A'):8} | {sort_by}: {display_value}")
                        
                        # 验证排序
                        if len(trades) > 1:
                            is_sorted = verify_sorting(trades, sort_by, sort_order)
                            print(f"\n排序验证: {'✅ 正确' if is_sorted else '❌ 错误'}")
                            
                            if not is_sorted:
                                print("❌ 发现排序错误！")
                                show_sorting_errors(trades, sort_by, sort_order)
                    else:
                        print("没有返回任何记录")
                else:
                    print(f"API错误: {data.get('message', '未知错误')}")
            else:
                print(f"HTTP错误: {response.text}")
                
        except Exception as e:
            print(f"请求异常: {e}")
        
        print("\n" + "="*60)

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
        
        # 数值比较
        if sort_by in ['return_rate', 'total_return', 'total_investment', 'holding_days']:
            try:
                current_val = float(current_val)
                next_val = float(next_val)
            except (ValueError, TypeError):
                current_val = 0
                next_val = 0
        
        if sort_order.lower() == 'desc':
            if current_val < next_val:
                return False
        else:  # asc
            if current_val > next_val:
                return False
    
    return True

def show_sorting_errors(trades, sort_by, sort_order):
    """显示排序错误详情"""
    print("\n排序错误详情:")
    error_count = 0
    
    for i in range(len(trades) - 1):
        current_val = trades[i].get(sort_by)
        next_val = trades[i + 1].get(sort_by)
        
        # 处理None值
        if current_val is None:
            current_val = 0 if sort_by in ['return_rate', 'total_return', 'total_investment', 'holding_days'] else ''
        if next_val is None:
            next_val = 0 if sort_by in ['return_rate', 'total_return', 'total_investment', 'holding_days'] else ''
        
        # 数值比较
        if sort_by in ['return_rate', 'total_return', 'total_investment', 'holding_days']:
            try:
                current_val_cmp = float(current_val)
                next_val_cmp = float(next_val)
            except (ValueError, TypeError):
                current_val_cmp = 0
                next_val_cmp = 0
        else:
            current_val_cmp = current_val
            next_val_cmp = next_val
        
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
                print(f"  位置 {i+1}-{i+2}: {trades[i].get('stock_code')} ({current_val}) -> {trades[i+1].get('stock_code')} ({next_val})")
    
    if error_count > 5:
        print(f"  ... 还有 {error_count - 5} 个排序错误")

if __name__ == "__main__":
    monitor_sorting_requests()