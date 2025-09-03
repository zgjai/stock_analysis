#!/usr/bin/env python3
"""
验证 selectMonth 错误修复
"""

import os
import re

def check_analytics_template():
    """检查 analytics.html 模板的修复"""
    print("🔍 检查 analytics.html 模板...")
    
    template_path = "templates/analytics.html"
    if not os.path.exists(template_path):
        print("   ❌ analytics.html 文件不存在")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否移除了局部变量声明
    if 'let expectationComparisonManager;' in content:
        print("   ❌ 仍然存在局部变量声明 'let expectationComparisonManager;'")
        return False
    else:
        print("   ✅ 已移除局部变量声明")
    
    # 检查是否添加了全局selectMonth函数
    if 'window.selectMonth = function' in content:
        print("   ✅ 已添加全局 selectMonth 函数")
    else:
        print("   ❌ 未找到全局 selectMonth 函数")
        return False
    
    # 检查是否添加了初始化检查
    if 'typeof window.expectationComparisonManager === \'undefined\'' in content:
        print("   ✅ 已添加初始化检查")
    else:
        print("   ❌ 未找到初始化检查")
        return False
    
    return True

def check_expectation_manager():
    """检查期望对比管理器的修复"""
    print("\n🔍 检查期望对比管理器...")
    
    manager_path = "static/js/expectation-comparison-manager.js"
    if not os.path.exists(manager_path):
        print("   ❌ expectation-comparison-manager.js 文件不存在")
        return False
    
    with open(manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有selectMonth方法
    if 'async selectMonth(index)' in content:
        print("   ✅ selectMonth 方法存在")
    else:
        print("   ❌ selectMonth 方法不存在")
        return False
    
    # 检查是否添加了错误处理
    if 'console.log(\'期望对比管理器初始化成功\')' in content:
        print("   ✅ 已添加初始化成功日志")
    else:
        print("   ❌ 未找到初始化成功日志")
        return False
    
    if 'console.error(\'期望对比管理器初始化失败:\', error)' in content:
        print("   ✅ 已添加初始化错误处理")
    else:
        print("   ❌ 未找到初始化错误处理")
        return False
    
    # 检查onclick调用方式
    onclick_calls = re.findall(r'onclick="([^"]*selectMonth[^"]*)"', content)
    if onclick_calls:
        print(f"   ✅ 找到 {len(onclick_calls)} 个 onclick selectMonth 调用")
        for call in onclick_calls:
            if 'expectationComparisonManager.selectMonth' in call:
                print(f"      ✅ 正确的管理器调用: {call}")
            else:
                print(f"      ⚠️  可能的问题调用: {call}")
    else:
        print("   ℹ️  未找到 onclick selectMonth 调用（可能是动态生成的）")
    
    return True

def check_test_files():
    """检查测试文件是否创建"""
    print("\n🔍 检查测试文件...")
    
    test_files = [
        "test_selectMonth_fix.html",
        "SELECTMONTH_ERROR_FIX_SUMMARY.md"
    ]
    
    all_exist = True
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} 已创建")
        else:
            print(f"   ❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def check_potential_issues():
    """检查潜在问题"""
    print("\n🔍 检查潜在问题...")
    
    # 检查是否还有直接的selectMonth调用
    html_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html') and not file.startswith('test_'):
                html_files.append(os.path.join(root, file))
    
    direct_calls = []
    for file_path in html_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 查找直接的selectMonth调用（不通过管理器）
                matches = re.findall(r'onclick="[^"]*selectMonth\([^)]*\)[^"]*"', content)
                for match in matches:
                    if 'expectationComparisonManager.selectMonth' not in match:
                        direct_calls.append((file_path, match))
        except Exception as e:
            print(f"   ⚠️  无法读取文件 {file_path}: {e}")
    
    if direct_calls:
        print("   ⚠️  发现直接的 selectMonth 调用:")
        for file_path, call in direct_calls:
            print(f"      {file_path}: {call}")
        print("   ℹ️  这些调用现在应该通过全局函数正常工作")
    else:
        print("   ✅ 未发现直接的 selectMonth 调用")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 selectMonth 错误修复验证")
    print("=" * 60)
    
    checks = [
        ("Analytics 模板检查", check_analytics_template),
        ("期望对比管理器检查", check_expectation_manager),
        ("测试文件检查", check_test_files),
        ("潜在问题检查", check_potential_issues)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"   ❌ {check_name} 执行失败: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有检查通过！selectMonth 错误修复完成")
        print("\n📋 下一步操作:")
        print("1. 重启应用服务器")
        print("2. 打开 analytics 页面")
        print("3. 测试月度期望收益对比功能")
        print("4. 检查浏览器控制台是否还有错误")
    else:
        print("❌ 部分检查未通过，请检查上述问题")
    print("=" * 60)

if __name__ == "__main__":
    main()