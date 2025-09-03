#!/usr/bin/env python3
"""
测试API排序功能的脚本
"""
import requests
import json

def test_api_sorting():
    """测试API排序功能"""
    base_url = "http://localhost:5001/api"
    
    print("=== API排序功能测试 ===\n")
    
    # 测试不同的排序参数
    test_cases = [
        {
            'name': '按收益率降序',
            'params': {
                'sort_by': 'return_rate',
                'sort_order': 'desc',
                'per_page': 10
            }
        },
        {
            'name': '按收益率升序',
            'params': {
                'sort_by': 'return_rate',
                'sort_order': 'asc',
                'per_page': 10
            }
        },
        {
            'name': '按股票代码升序',
            'params': {
                'sort_by': 'stock_code',
                'sort_order': 'asc',
                'per_page': 10
            }
        },
        {
            'name': '默认排序（无参数）',
            'params': {
                'per_page': 10
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print("-" * 50)
        
        try:
            # 发送API请求
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
                    total = data.get('data', {}).get('total', 0)
                    
                    print(f"总记录数: {total}")
                    print(f"返回记录数: {len(trades)}")
                    
                    if trades:
                        sort_by = test_case['params'].get('sort_by', 'completion_date')
                        sort_order = test_case['params'].get('sort_order', 'desc')
                        
                        print(f"\n前5条记录的 {sort_by} 值:")
                        for j, trade in enumerate(trades[:5]):
                            sort_value = trade.get(sort_by)
                            if sort_by == 'return_rate' and sort_value is not None:
                                sort_value = f"{sort_value:.4f} ({sort_value * 100:.2f}%)"
                            print(f"  {j+1}. {trade.get('stock_code', 'N/A')} - {sort_by}: {sort_value}")
                        
                        # 验证排序
                        is_sorted = verify_api_sorting(trades, sort_by, sort_order)
                        print(f"\n排序验证: {'✅ 正确' if is_sorted else '❌ 错误'}")
                        
                        if not is_sorted:
                            print("排序错误详情:")
                            show_api_sorting_errors(trades, sort_by, sort_order)
                    else:
                        print("没有返回任何记录")
                else:
                    print(f"API返回错误: {data.get('message', '未知错误')}")
            else:
                print(f"HTTP错误: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
        except Exception as e:
            print(f"其他错误: {e}")
        
        print("\n" + "=" * 60 + "\n")

def verify_api_sorting(trades, sort_by, sort_order):
    """验证API返回的排序是否正确"""
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
        
        # 转换为数值类型进行比较
        try:
            current_val = float(current_val)
            next_val = float(next_val)
        except (ValueError, TypeError):
            # 如果不能转换为数值，按字符串比较
            current_val = str(current_val)
            next_val = str(next_val)
        
        if sort_order.lower() == 'desc':
            if current_val < next_val:
                return False
        else:  # asc
            if current_val > next_val:
                return False
    
    return True

def show_api_sorting_errors(trades, sort_by, sort_order):
    """显示API排序错误的详细信息"""
    for i in range(len(trades) - 1):
        current_val = trades[i].get(sort_by)
        next_val = trades[i + 1].get(sort_by)
        
        # 处理None值
        if current_val is None:
            current_val = 0
        if next_val is None:
            next_val = 0
        
        # 转换为数值类型进行比较
        try:
            current_val_num = float(current_val)
            next_val_num = float(next_val)
        except (ValueError, TypeError):
            current_val_num = str(current_val)
            next_val_num = str(next_val)
        
        is_error = False
        if sort_order.lower() == 'desc':
            if current_val_num < next_val_num:
                is_error = True
        else:  # asc
            if current_val_num > next_val_num:
                is_error = True
        
        if is_error:
            print(f"  位置 {i+1}-{i+2}: {current_val} -> {next_val} (应该是 {'降序' if sort_order.lower() == 'desc' else '升序'})")

def test_with_pagination():
    """测试分页对排序的影响"""
    base_url = "http://localhost:5001/api"
    
    print("=== 分页排序测试 ===\n")
    
    # 测试不同页码的排序一致性
    params = {
        'sort_by': 'return_rate',
        'sort_order': 'desc',
        'per_page': 5
    }
    
    for page in [1, 2, 3]:
        print(f"第 {page} 页:")
        params['page'] = page
        
        try:
            response = requests.get(
                f"{base_url}/historical-trades",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    trades = data.get('data', {}).get('trades', [])
                    
                    print(f"  返回 {len(trades)} 条记录")
                    for j, trade in enumerate(trades):
                        return_rate = trade.get('return_rate', 0)
                        print(f"    {j+1}. {trade.get('stock_code')} - 收益率: {return_rate:.4f}")
                else:
                    print(f"  API错误: {data.get('message')}")
            else:
                print(f"  HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"  请求错误: {e}")
        
        print()

if __name__ == "__main__":
    print("开始测试API排序功能...\n")
    
    # 测试基本排序功能
    test_api_sorting()
    
    print("\n" + "=" * 80 + "\n")
    
    # 测试分页排序
    test_with_pagination()
    
    print("测试完成！")