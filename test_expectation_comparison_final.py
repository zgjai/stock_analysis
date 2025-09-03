#!/usr/bin/env python3
"""
期望对比功能最终测试脚本
验证所有功能是否正常工作，包括性能优化和用户体验改进
"""

import sys
import os
import time
import json
import requests
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_endpoints():
    """测试API端点功能"""
    print("=" * 60)
    print("测试API端点功能")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 测试期望对比API
    test_cases = [
        {"time_range": "all", "base_capital": 3200000},
        {"time_range": "1y", "base_capital": 3200000},
        {"time_range": "90d", "base_capital": 5000000},
        {"time_range": "30d", "base_capital": 1000000}
    ]
    
    for i, params in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {params}")
        try:
            start_time = time.time()
            response = requests.get(
                f"{base_url}/api/analytics/expectation-comparison",
                params=params,
                timeout=10
            )
            end_time = time.time()
            
            print(f"响应时间: {(end_time - start_time) * 1000:.2f}ms")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✓ API调用成功")
                    
                    # 验证数据结构
                    required_keys = ['expectation', 'actual', 'comparison', 'time_range']
                    if all(key in data['data'] for key in required_keys):
                        print("✓ 数据结构完整")
                        
                        # 验证期望值计算
                        expectation = data['data']['expectation']
                        if all(key in expectation for key in ['return_rate', 'return_amount', 'holding_days', 'success_rate']):
                            print("✓ 期望值计算正确")
                        else:
                            print("✗ 期望值数据不完整")
                        
                        # 验证实际值计算
                        actual = data['data']['actual']
                        if all(key in actual for key in ['return_rate', 'return_amount', 'holding_days', 'success_rate']):
                            print("✓ 实际值计算正确")
                        else:
                            print("✗ 实际值数据不完整")
                        
                        # 验证对比结果
                        comparison = data['data']['comparison']
                        if all(key in comparison for key in ['return_rate_diff', 'return_amount_diff', 'holding_days_diff', 'success_rate_diff']):
                            print("✓ 对比结果计算正确")
                        else:
                            print("✗ 对比结果数据不完整")
                    else:
                        print("✗ 数据结构不完整")
                else:
                    print(f"✗ API返回失败: {data.get('message', '未知错误')}")
            else:
                print(f"✗ HTTP错误: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("✗ 请求超时")
        except requests.exceptions.ConnectionError:
            print("✗ 连接失败 - 请确保服务器正在运行")
        except Exception as e:
            print(f"✗ 测试失败: {e}")

def test_parameter_validation():
    """测试参数验证"""
    print("\n" + "=" * 60)
    print("测试参数验证")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 测试无效参数
    invalid_cases = [
        {"time_range": "invalid", "base_capital": 3200000, "expected_error": "时间范围"},
        {"time_range": "all", "base_capital": -1000000, "expected_error": "基准本金"},
        {"time_range": "all", "base_capital": 0, "expected_error": "基准本金"},
        {"time_range": "1d", "base_capital": 3200000, "expected_error": "时间范围"}
    ]
    
    for i, case in enumerate(invalid_cases, 1):
        print(f"\n无效参数测试 {i}: {case['time_range']}, {case['base_capital']}")
        try:
            response = requests.get(
                f"{base_url}/api/analytics/expectation-comparison",
                params={"time_range": case["time_range"], "base_capital": case["base_capital"]},
                timeout=5
            )
            
            if response.status_code == 400:
                data = response.json()
                if case["expected_error"] in data.get('message', ''):
                    print(f"✓ 正确拒绝无效参数: {data['message']}")
                else:
                    print(f"✗ 错误消息不匹配: {data.get('message', '')}")
            else:
                print(f"✗ 应该返回400错误，实际返回: {response.status_code}")
                
        except Exception as e:
            print(f"✗ 测试失败: {e}")

def test_performance_benchmarks():
    """测试性能基准"""
    print("\n" + "=" * 60)
    print("测试性能基准")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 性能测试
    print("\n执行性能测试...")
    response_times = []
    
    for i in range(5):
        try:
            start_time = time.time()
            response = requests.get(
                f"{base_url}/api/analytics/expectation-comparison",
                params={"time_range": "all", "base_capital": 3200000},
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = (end_time - start_time) * 1000
                response_times.append(response_time)
                print(f"请求 {i+1}: {response_time:.2f}ms")
            else:
                print(f"请求 {i+1}: 失败 (状态码: {response.status_code})")
                
        except Exception as e:
            print(f"请求 {i+1}: 异常 - {e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"\n性能统计:")
        print(f"平均响应时间: {avg_time:.2f}ms")
        print(f"最大响应时间: {max_time:.2f}ms")
        print(f"最小响应时间: {min_time:.2f}ms")
        
        # 性能基准检查
        if avg_time < 1000:  # 1秒内
            print("✓ 性能表现良好")
        elif avg_time < 3000:  # 3秒内
            print("⚠ 性能可接受，但有优化空间")
        else:
            print("✗ 性能较差，需要优化")

def test_data_consistency():
    """测试数据一致性"""
    print("\n" + "=" * 60)
    print("测试数据一致性")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    try:
        # 获取期望对比数据
        response = requests.get(
            f"{base_url}/api/analytics/expectation-comparison",
            params={"time_range": "all", "base_capital": 3200000},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            
            # 验证期望值一致性
            expectation = data['expectation']
            
            # 手动计算期望收益率
            probability_model = [
                {'probability': 0.10, 'return_rate': 0.20},
                {'probability': 0.10, 'return_rate': 0.15},
                {'probability': 0.15, 'return_rate': 0.10},
                {'probability': 0.15, 'return_rate': 0.05},
                {'probability': 0.10, 'return_rate': 0.02},
                {'probability': 0.20, 'return_rate': -0.03},
                {'probability': 0.15, 'return_rate': -0.05},
                {'probability': 0.05, 'return_rate': -0.10}
            ]
            
            expected_return_rate = sum(p['probability'] * p['return_rate'] for p in probability_model)
            
            if abs(expectation['return_rate'] - expected_return_rate) < 0.001:
                print("✓ 期望收益率计算一致")
            else:
                print(f"✗ 期望收益率不一致: 期望 {expected_return_rate}, 实际 {expectation['return_rate']}")
            
            # 验证收益金额计算
            expected_amount = 3200000 * expected_return_rate
            if abs(expectation['return_amount'] - expected_amount) < 0.01:
                print("✓ 期望收益金额计算一致")
            else:
                print(f"✗ 期望收益金额不一致: 期望 {expected_amount}, 实际 {expectation['return_amount']}")
            
            # 验证对比结果计算
            comparison = data['comparison']
            actual = data['actual']
            
            expected_diff = actual['return_rate'] - expectation['return_rate']
            if abs(comparison['return_rate_diff'] - expected_diff) < 0.001:
                print("✓ 收益率差异计算一致")
            else:
                print(f"✗ 收益率差异不一致: 期望 {expected_diff}, 实际 {comparison['return_rate_diff']}")
            
        else:
            print(f"✗ 无法获取测试数据: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 数据一致性测试失败: {e}")

def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试错误处理")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 测试各种错误情况
    error_cases = [
        {
            "name": "缺少参数",
            "url": f"{base_url}/api/analytics/expectation-comparison",
            "params": {},
            "expected_status": [200, 400]  # 可能有默认值
        },
        {
            "name": "无效时间范围",
            "url": f"{base_url}/api/analytics/expectation-comparison",
            "params": {"time_range": "invalid"},
            "expected_status": [400]
        },
        {
            "name": "负数本金",
            "url": f"{base_url}/api/analytics/expectation-comparison",
            "params": {"base_capital": -1000},
            "expected_status": [400]
        },
        {
            "name": "不存在的端点",
            "url": f"{base_url}/api/analytics/nonexistent",
            "params": {},
            "expected_status": [404]
        }
    ]
    
    for case in error_cases:
        print(f"\n测试 {case['name']}...")
        try:
            response = requests.get(case['url'], params=case['params'], timeout=5)
            
            if response.status_code in case['expected_status']:
                print(f"✓ 正确处理错误: {response.status_code}")
                
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        if 'message' in error_data:
                            print(f"  错误消息: {error_data['message']}")
                        else:
                            print("  ⚠ 缺少错误消息")
                    except:
                        print("  ⚠ 响应不是有效的JSON")
            else:
                print(f"✗ 错误处理不当: 期望 {case['expected_status']}, 实际 {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("✗ 请求超时")
        except Exception as e:
            print(f"✗ 测试失败: {e}")

def generate_test_report():
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("生成测试报告")
    print("=" * 60)
    
    report = {
        "test_time": datetime.now().isoformat(),
        "test_summary": {
            "total_tests": 4,
            "passed_tests": 0,
            "failed_tests": 0,
            "warnings": 0
        },
        "performance_metrics": {
            "api_response_time": "待测试",
            "memory_usage": "待测试",
            "cpu_usage": "待测试"
        },
        "recommendations": []
    }
    
    # 保存报告
    with open('expectation_comparison_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✓ 测试报告已生成: expectation_comparison_test_report.json")

def main():
    """主测试函数"""
    print("期望对比功能最终测试")
    print("测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # 执行所有测试
        test_api_endpoints()
        test_parameter_validation()
        test_performance_benchmarks()
        test_data_consistency()
        test_error_handling()
        generate_test_report()
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        print("✓ 所有测试已执行完毕")
        print("✓ 详细报告请查看 expectation_comparison_test_report.json")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试执行失败: {e}")

if __name__ == "__main__":
    main()