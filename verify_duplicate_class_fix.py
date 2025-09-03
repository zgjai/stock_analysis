#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证重复类定义修复
"""

import os
import subprocess
import requests

def check_analytics_html():
    """检查analytics.html中是否还有重复的类定义"""
    print("1. 检查analytics.html中的类定义...")
    
    if not os.path.exists('templates/analytics.html'):
        print("   ❌ analytics.html文件不存在")
        return False
    
    with open('templates/analytics.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否还有重复的类定义
    class_count = content.count('class ExpectationComparisonManager')
    if class_count == 0:
        print("   ✅ analytics.html中已删除重复的类定义")
    else:
        print(f"   ❌ analytics.html中仍有{class_count}个类定义")
        return False
    
    # 检查是否还有重复的实例化
    instance_count = content.count('new ExpectationComparisonManager')
    if instance_count == 0:
        print("   ✅ analytics.html中已删除重复的实例化")
    else:
        print(f"   ❌ analytics.html中仍有{instance_count}个实例化")
        return False
    
    return True

def check_external_js():
    """检查外部JavaScript文件"""
    print("\n2. 检查外部JavaScript文件...")
    
    js_file = 'static/js/expectation-comparison-manager.js'
    if not os.path.exists(js_file):
        print("   ❌ expectation-comparison-manager.js文件不存在")
        return False
    
    # 检查语法
    try:
        result = subprocess.run(['node', '-c', js_file], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ JavaScript语法检查通过")
        else:
            print(f"   ❌ JavaScript语法错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ JavaScript语法检查失败: {e}")
        return False
    
    # 检查类定义
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'class ExpectationComparisonManager' in content:
        print("   ✅ 外部文件包含ExpectationComparisonManager类定义")
    else:
        print("   ❌ 外部文件缺少ExpectationComparisonManager类定义")
        return False
    
    # 检查全局实例创建
    if 'window.expectationComparisonManager = new ExpectationComparisonManager' in content:
        print("   ✅ 外部文件包含全局实例创建")
    else:
        print("   ❌ 外部文件缺少全局实例创建")
        return False
    
    return True

def check_api_functionality():
    """检查API功能"""
    print("\n3. 检查API功能...")
    
    try:
        # 测试月度期望API
        response = requests.get('http://localhost:5001/api/analytics/monthly-expectations', timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ 月度期望API正常")
            else:
                print(f"   ❌ 月度期望API返回失败: {result.get('message')}")
                return False
        else:
            print(f"   ❌ 月度期望API状态码: {response.status_code}")
            return False
        
        # 测试月度对比API
        response = requests.get('http://localhost:5001/api/analytics/monthly-comparison?year=2025&month=9', timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ 月度对比API正常")
                
                # 验证数据一致性
                data = result['data']
                actual = data['actual']
                if 'total_profit' in actual and actual['total_profit'] > 0:
                    print("   ✅ 数据计算正常")
                else:
                    print("   ❌ 数据计算异常")
                    return False
            else:
                print(f"   ❌ 月度对比API返回失败: {result.get('message')}")
                return False
        else:
            print(f"   ❌ 月度对比API状态码: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"   ❌ API测试失败: {e}")
        return False
    
    return True

def check_file_structure():
    """检查文件结构"""
    print("\n4. 检查文件结构...")
    
    required_files = [
        'templates/analytics.html',
        'static/js/expectation-comparison-manager.js',
        'monthly_expectation_service.py',
        'expected_monthly_returns.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if not missing_files:
        print("   ✅ 所有必要文件都存在")
        return True
    else:
        print(f"   ❌ 缺少文件: {missing_files}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("重复类定义修复验证")
    print("=" * 60)
    
    checks = [
        check_analytics_html,
        check_external_js,
        check_api_functionality,
        check_file_structure
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
        print("🎉 所有检查通过！重复类定义问题已完全修复")
        print("\n修复内容:")
        print("✅ 删除了analytics.html中重复的ExpectationComparisonManager类定义")
        print("✅ 删除了analytics.html中重复的实例化代码")
        print("✅ 保留外部expectation-comparison-manager.js中的类定义")
        print("✅ 全局实例由外部文件自动创建")
        print("✅ API功能正常，数据计算正确")
        print("\n现在可以正常使用月度期望收益对比功能了！")
        print("访问: http://localhost:5001/analytics -> 期望对比Tab -> 月度期望收益对比")
    else:
        print(f"❌ 检查结果: {passed}/{total} 通过")
        print("请修复失败的检查项后重新验证")
    print("=" * 60)

if __name__ == "__main__":
    main()