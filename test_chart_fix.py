#!/usr/bin/env python3
"""
测试图表数据修复
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_chart_apis():
    """测试图表相关的API数据格式"""
    print("测试图表API数据格式...")
    
    # 测试月度统计API
    try:
        print("\n1. 测试月度统计API...")
        response = requests.get(f"{BASE_URL}/api/analytics/monthly")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 月度统计API调用成功")
            
            if 'data' in data:
                monthly_data = data['data']
                print(f"  数据结构: {type(monthly_data).__name__}")
                
                if isinstance(monthly_data, dict):
                    print(f"  数据字段: {list(monthly_data.keys())}")
                    
                    if 'monthly_data' in monthly_data:
                        monthly_list = monthly_data['monthly_data']
                        print(f"  月度数据数组长度: {len(monthly_list)}")
                        
                        if len(monthly_list) > 0:
                            print(f"  第一项字段: {list(monthly_list[0].keys())}")
                            print(f"  示例数据: {monthly_list[0]}")
                        else:
                            print("  月度数据为空")
                    else:
                        print("  缺少 monthly_data 字段")
                else:
                    print(f"  数据不是对象格式: {monthly_data}")
            else:
                print("  响应缺少 data 字段")
        else:
            print(f"✗ 月度统计API失败 (状态码: {response.status_code})")
            print(f"  错误信息: {response.text}")
            
    except Exception as e:
        print(f"✗ 月度统计API异常: {str(e)}")
    
    # 测试收益分布API
    try:
        print("\n2. 测试收益分布API...")
        response = requests.get(f"{BASE_URL}/api/analytics/profit-distribution")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 收益分布API调用成功")
            
            if 'data' in data:
                distribution_data = data['data']
                print(f"  数据结构: {type(distribution_data).__name__}")
                
                if isinstance(distribution_data, dict):
                    print(f"  数据字段: {list(distribution_data.keys())}")
                    
                    if 'profit_ranges' in distribution_data:
                        profit_ranges = distribution_data['profit_ranges']
                        print(f"  收益区间数组长度: {len(profit_ranges)}")
                        
                        if len(profit_ranges) > 0:
                            print(f"  第一项字段: {list(profit_ranges[0].keys())}")
                            
                            # 显示有数据的区间
                            non_zero_ranges = [r for r in profit_ranges if r.get('count', 0) > 0]
                            print(f"  有数据的区间数: {len(non_zero_ranges)}")
                            
                            for range_info in non_zero_ranges:
                                print(f"    {range_info['range']}: {range_info['count']}只股票")
                        else:
                            print("  收益区间数据为空")
                    else:
                        print("  缺少 profit_ranges 字段")
                else:
                    print(f"  数据不是对象格式: {distribution_data}")
            else:
                print("  响应缺少 data 字段")
        else:
            print(f"✗ 收益分布API失败 (状态码: {response.status_code})")
            print(f"  错误信息: {response.text}")
            
    except Exception as e:
        print(f"✗ 收益分布API异常: {str(e)}")

def test_dashboard_page():
    """测试仪表板页面加载"""
    print("\n3. 测试仪表板页面...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            print("✓ 仪表板页面加载成功")
            
            # 检查关键元素
            content = response.text
            
            if 'profitChart' in content:
                print("✓ 收益趋势图元素存在")
            else:
                print("✗ 收益趋势图元素缺失")
                
            if 'distributionChart' in content:
                print("✓ 收益分布图元素存在")
            else:
                print("✗ 收益分布图元素缺失")
                
            if 'chart.js@3.9.1' in content:
                print("✓ Chart.js 3.9.1 版本引用正确")
            else:
                print("✗ Chart.js版本引用可能有问题")
                
        else:
            print(f"✗ 仪表板页面加载失败 (状态码: {response.status_code})")
            
    except Exception as e:
        print(f"✗ 仪表板页面测试异常: {str(e)}")

if __name__ == "__main__":
    test_chart_apis()
    test_dashboard_page()
    
    print("\n修复说明:")
    print("1. 修复了图表数据格式处理问题")
    print("2. 正确处理 API 返回的嵌套数据结构")
    print("3. 添加了数据验证和错误处理")
    print("4. 过滤掉空数据以改善图表显示")
    print("\n请在浏览器中访问 http://localhost:5001 查看图表是否正常显示")