#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证月度期望收益对比功能修复
"""

import requests
import json
import subprocess
import os
from datetime import datetime

def check_javascript_syntax():
    """检查JavaScript语法"""
    print("1. 检查JavaScript语法...")
    
    try:
        result = subprocess.run(['node', '-c', 'static/js/expectation-comparison-manager.js'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ JavaScript语法检查通过")
            return True
        else:
            print(f"   ❌ JavaScript语法错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ JavaScript语法检查失败: {e}")
        return False

def check_api_endpoints():
    """检查API端点"""
    print("\n2. 检查API端点...")
    
    base_url = "http://localhost:5001"
    
    # 检查月度期望API
    try:
        response = requests.get(f"{base_url}/api/analytics/monthly-expectations", timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ 月度期望API正常")
                print(f"      数据条数: {len(result.get('data', []))}")
            else:
                print(f"   ❌ 月度期望API返回失败: {result.get('message')}")
                return False
        else:
            print(f"   ❌ 月度期望API状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 月度期望API测试失败: {e}")
        return False
    
    # 检查月度对比API
    try:
        response = requests.get(f"{base_url}/api/analytics/monthly-comparison?year=2025&month=8", timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ 月度对比API正常")
                data = result.get('data', {})
                print(f"      对比月份: {data.get('month_str')}")
            else:
                print(f"   ❌ 月度对比API返回失败: {result.get('message')}")
                return False
        else:
            print(f"   ❌ 月度对比API状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 月度对比API测试失败: {e}")
        return False
    
    return True

def check_data_files():
    """检查数据文件"""
    print("\n3. 检查数据文件...")
    
    # 检查期望收益数据文件
    if os.path.exists('expected_monthly_returns.json'):
        try:
            with open('expected_monthly_returns.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if len(data) == 24:
                print("   ✅ 期望收益数据文件正常")
                print(f"      包含24个月数据")
                
                # 检查第一条数据
                first_item = data[0]
                if all(key in first_item for key in ['month', 'expected_amount', 'start_capital', 'end_capital']):
                    print("   ✅ 数据格式正确")
                else:
                    print("   ❌ 数据格式不完整")
                    return False
            else:
                print(f"   ❌ 数据条数错误: {len(data)} (期望24条)")
                return False
        except Exception as e:
            print(f"   ❌ 读取数据文件失败: {e}")
            return False
    else:
        print("   ❌ 期望收益数据文件不存在")
        return False
    
    return True

def check_html_integration():
    """检查HTML集成"""
    print("\n4. 检查HTML集成...")
    
    # 检查analytics.html文件
    if os.path.exists('templates/analytics.html'):
        try:
            with open('templates/analytics.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查必要的HTML元素
            required_elements = [
                'monthly-expectation-list',
                'monthly-comparison-detail',
                'refresh-monthly-expectation-btn',
                '月度期望收益对比'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if not missing_elements:
                print("   ✅ HTML集成正常")
                print("      所有必要元素都存在")
            else:
                print(f"   ❌ 缺少HTML元素: {missing_elements}")
                return False
                
        except Exception as e:
            print(f"   ❌ 读取HTML文件失败: {e}")
            return False
    else:
        print("   ❌ analytics.html文件不存在")
        return False
    
    return True

def check_service_files():
    """检查服务文件"""
    print("\n5. 检查服务文件...")
    
    # 检查月度期望服务文件
    if os.path.exists('monthly_expectation_service.py'):
        try:
            with open('monthly_expectation_service.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查必要的类和方法
            required_items = [
                'class MonthlyExpectationService',
                'get_monthly_expectations',
                'get_monthly_comparison',
                '_calculate_actual_monthly_return'
            ]
            
            missing_items = []
            for item in required_items:
                if item not in content:
                    missing_items.append(item)
            
            if not missing_items:
                print("   ✅ 月度期望服务文件正常")
            else:
                print(f"   ❌ 缺少服务方法: {missing_items}")
                return False
                
        except Exception as e:
            print(f"   ❌ 读取服务文件失败: {e}")
            return False
    else:
        print("   ❌ monthly_expectation_service.py文件不存在")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("月度期望收益对比功能修复验证")
    print("=" * 60)
    
    checks = [
        check_javascript_syntax,
        check_api_endpoints,
        check_data_files,
        check_html_integration,
        check_service_files
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        else:
            print(f"\n❌ 检查失败，请修复上述问题")
            break
    
    print(f"\n" + "=" * 60)
    if passed == total:
        print("🎉 所有检查通过！月度期望收益对比功能已成功修复")
        print("\n功能使用方法:")
        print("1. 访问 http://localhost:5001/analytics")
        print("2. 点击'期望对比'Tab")
        print("3. 在'月度期望收益对比'卡片中选择月份查看对比")
    else:
        print(f"❌ 检查结果: {passed}/{total} 通过")
        print("请修复失败的检查项后重新验证")
    print("=" * 60)

if __name__ == "__main__":
    main()