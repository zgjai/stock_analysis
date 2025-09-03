#!/usr/bin/env python3
"""
测试历史交易排序功能的调试脚本
"""
import requests
import json
from datetime import datetime

def test_sorting_api():
    """测试排序API功能"""
    base_url = "http://localhost:5001/api"
    
    print("=== 历史交易排序功能测试 ===\n")
    
    # 测试不同的排序参数
    test_cases = [
        {
            'name': '默认排序（按完成日期降序）',
            'params': {}
        },
        {
            'name': '按股票代码升序',
            'params': {'sort_by': 'stock_code', 'sort_order': 'asc'}
        },
        {
            'name': '按收益率降序',
            'params': {'sort_by': 'return_rate', 'sort_order': 'desc'}
        },
        {
            'name': '按持仓天数升序',
            'params': {'sort_by': 'holding_days', 'sort_order': 'asc'}
        },
        {
            'name': '按投入本金降序',
            'params': {'sort_by': 'total_investment', 'sort_order': 'desc'}
        },
        {
            'name': '按实际收益升序',
            'params': {'sort_by': 'total_return', 'sort_order': 'asc'}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print("-" * 50)
        
        try:
            # 添加基本参数
            params = {
                'per_page': 5,  # 只获取5条记录用于测试
                **test_case['params']
            }
            
            print(f"请求参数: {params}")
            
            response = requests.get(
                f"{base_url}/historical-trades",
                params=params,
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    trades = data.get('data', {}).get('trades', [])
                    total = data.get('data', {}).get('total', 0)
                    
                    print(f"总记录数: {total}")
                    print(f"返回记录数: {len(trades)}")
                    
                    if trades:
                        print("\n前几条记录:")
                        print("股票代码 | 完成日期 | 收益率 | 持仓天数 | 投入本金 | 实际收益")
                        print("-" * 80)
                        
                        for trade in trades:
                            print(f"{trade.get('stock_code', 'N/A'):8} | "
                                  f"{trade.get('completion_date', 'N/A'):10} | "
                                  f"{(trade.get('return_rate', 0) * 100):6.2f}% | "
                                  f"{trade.get('holding_days', 0):6}天 | "
                                  f"¥{trade.get('total_investment', 0):8.2f} | "
                                  f"¥{trade.get('total_return', 0):8.2f}")
                        
                        # 验证排序是否正确
                        if len(trades) > 1:
                            sort_field = params.get('sort_by', 'completion_date')
                            sort_order = params.get('sort_order', 'desc')
                            
                            print(f"\n排序验证 (按{sort_field} {sort_order}):")
                            
                            is_sorted = True
                            for j in range(len(trades) - 1):
                                current_val = trades[j].get(sort_field)
                                next_val = trades[j + 1].get(sort_field)
                                
                                if sort_order == 'desc':
                                    if current_val < next_val:
                                        is_sorted = False
                                        break
                                else:  # asc
                                    if current_val > next_val:
                                        is_sorted = False
                                        break
                            
                            print(f"排序正确: {'✓' if is_sorted else '✗'}")
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
        
        print("\n" + "=" * 80 + "\n")

def test_frontend_elements():
    """测试前端元素是否存在"""
    print("=== 前端元素检查 ===\n")
    
    # 检查模板文件
    template_file = "templates/historical_trades.html"
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查关键元素
        elements_to_check = [
            ('sort-by', 'id="sort-by"'),
            ('sort-order', 'id="sort-order"'),
            ('应用排序按钮', 'onclick="filterHistoricalTrades()"'),
            ('重置按钮', 'onclick="resetFilter()"')
        ]
        
        print("模板文件检查:")
        for name, pattern in elements_to_check:
            if pattern in content:
                print(f"✓ {name}: 存在")
            else:
                print(f"✗ {name}: 缺失")
                
    except FileNotFoundError:
        print(f"✗ 模板文件不存在: {template_file}")
    except Exception as e:
        print(f"✗ 检查模板文件时出错: {e}")
    
    print()
    
    # 检查JavaScript文件
    js_file = "static/js/historical-trades-manager.js"
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查关键方法
        methods_to_check = [
            ('applyFilters方法', 'applyFilters()'),
            ('loadHistoricalTrades方法', 'loadHistoricalTrades()'),
            ('排序字段事件监听', 'sort-by'),
            ('排序方向事件监听', 'sort-order')
        ]
        
        print("JavaScript文件检查:")
        for name, pattern in methods_to_check:
            if pattern in content:
                print(f"✓ {name}: 存在")
            else:
                print(f"✗ {name}: 缺失")
                
    except FileNotFoundError:
        print(f"✗ JavaScript文件不存在: {js_file}")
    except Exception as e:
        print(f"✗ 检查JavaScript文件时出错: {e}")

if __name__ == "__main__":
    print("开始测试历史交易排序功能...\n")
    
    # 测试前端元素
    test_frontend_elements()
    
    print("\n" + "=" * 80 + "\n")
    
    # 测试API功能
    test_sorting_api()
    
    print("测试完成！")