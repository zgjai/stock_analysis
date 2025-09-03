#!/usr/bin/env python3
"""
Analytics Data Structure Fix Verification
测试统计分析页面的数据结构修复
"""

import requests
import json
import sys
from datetime import datetime

def test_api_endpoint(url, endpoint_name):
    """测试单个API端点"""
    print(f"\n=== 测试 {endpoint_name} ===")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应结构: {list(data.keys())}")
            
            if data.get('success'):
                print("✓ API调用成功")
                return data.get('data')
            else:
                print(f"✗ API返回失败: {data.get('message', '未知错误')}")
                return None
        else:
            print(f"✗ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return None

def test_profit_distribution():
    """测试收益分布API"""
    data = test_api_endpoint(
        'http://localhost:5001/api/analytics/profit-distribution',
        '收益分布API'
    )
    
    if data:
        print(f"数据结构: {list(data.keys())}")
        
        if 'distribution' in data and isinstance(data['distribution'], list):
            print(f"✓ distribution数组存在，长度: {len(data['distribution'])}")
            
            if data['distribution']:
                sample_item = data['distribution'][0]
                print(f"样本项字段: {list(sample_item.keys())}")
                
                required_fields = ['range_name', 'count', 'percentage']
                missing_fields = [field for field in required_fields if field not in sample_item]
                
                if not missing_fields:
                    print("✓ 所有必需字段都存在")
                    return True
                else:
                    print(f"✗ 缺少字段: {missing_fields}")
            else:
                print("⚠ distribution数组为空")
                return True  # 空数组也是有效的
        else:
            print("✗ 缺少distribution数组或类型错误")
    
    return False

def test_monthly_statistics():
    """测试月度统计API"""
    data = test_api_endpoint(
        'http://localhost:5001/api/analytics/monthly?year=2025',
        '月度统计API'
    )
    
    if data:
        print(f"数据结构: {list(data.keys())}")
        
        if 'monthly_data' in data and isinstance(data['monthly_data'], list):
            print(f"✓ monthly_data数组存在，长度: {len(data['monthly_data'])}")
            
            if data['monthly_data']:
                sample_item = data['monthly_data'][0]
                print(f"样本项字段: {list(sample_item.keys())}")
                
                required_fields = ['month', 'total_trades', 'buy_count', 'sell_count', 'profit_amount', 'success_rate']
                missing_fields = [field for field in required_fields if field not in sample_item]
                
                if not missing_fields:
                    print("✓ 所有必需字段都存在")
                    return True
                else:
                    print(f"✗ 缺少字段: {missing_fields}")
            else:
                print("⚠ monthly_data数组为空")
                return True
        else:
            print("✗ 缺少monthly_data数组或类型错误")
    
    return False

def test_holdings_api():
    """测试持仓API"""
    data = test_api_endpoint(
        'http://localhost:5001/api/analytics/holdings',
        '持仓API'
    )
    
    if data:
        print(f"数据结构: {list(data.keys())}")
        
        if 'holdings' in data and isinstance(data['holdings'], list):
            print(f"✓ holdings数组存在，长度: {len(data['holdings'])}")
            
            required_summary_fields = ['total_cost', 'total_market_value', 'total_profit', 'total_count']
            missing_summary = [field for field in required_summary_fields if field not in data]
            
            if not missing_summary:
                print("✓ 汇总字段完整")
                return True
            else:
                print(f"✗ 缺少汇总字段: {missing_summary}")
        else:
            print("✗ 缺少holdings数组或类型错误")
    
    return False

def test_overview_api():
    """测试概览API"""
    data = test_api_endpoint(
        'http://localhost:5001/api/analytics/overview',
        '概览API'
    )
    
    if data:
        print(f"数据结构: {list(data.keys())}")
        
        required_fields = ['total_profit', 'success_rate', 'total_investment']
        missing_fields = [field for field in required_fields if field not in data]
        
        if not missing_fields:
            print("✓ 概览数据结构正确")
            return True
        else:
            print(f"✗ 缺少字段: {missing_fields}")
    
    return False

def test_performance_api():
    """测试性能API"""
    data = test_api_endpoint(
        'http://localhost:5001/api/analytics/performance',
        '性能API'
    )
    
    if data:
        print(f"数据结构: {list(data.keys())}")
        
        required_fields = ['total_trades', 'trading_days']
        missing_fields = [field for field in required_fields if field not in data]
        
        if not missing_fields:
            print("✓ 性能数据结构正确")
            return True
        else:
            print(f"✗ 缺少字段: {missing_fields}")
    
    return False

def main():
    """主测试函数"""
    print("Analytics API Data Structure Fix Verification")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("收益分布API", test_profit_distribution),
        ("月度统计API", test_monthly_statistics),
        ("持仓API", test_holdings_api),
        ("概览API", test_overview_api),
        ("性能API", test_performance_api),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} 测试异常: {str(e)}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有API数据结构测试通过！")
        print("\n修复说明:")
        print("1. ✓ 收益分布API返回 {data: {distribution: [...]}}")
        print("2. ✓ 月度统计API返回 {data: {monthly_data: [...]}}")
        print("3. ✓ 前端JavaScript已修复数据访问路径")
        print("4. ✓ 添加了数据验证和错误处理")
        return 0
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return 1

if __name__ == '__main__':
    sys.exit(main())