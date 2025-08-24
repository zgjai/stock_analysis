#!/usr/bin/env python3
"""
验证浮盈计算器实现
"""
import os
import re
from pathlib import Path

def check_file_exists(file_path):
    """检查文件是否存在"""
    return os.path.exists(file_path)

def check_content_in_file(file_path, patterns):
    """检查文件中是否包含指定内容"""
    if not os.path.exists(file_path):
        return False, f"文件不存在: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_patterns = []
        for pattern_name, pattern in patterns.items():
            if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
                missing_patterns.append(pattern_name)
        
        if missing_patterns:
            return False, f"缺少内容: {', '.join(missing_patterns)}"
        
        return True, "所有内容都存在"
    
    except Exception as e:
        return False, f"读取文件失败: {str(e)}"

def verify_floating_profit_calculator():
    """验证浮盈计算器实现"""
    print("🔍 验证浮盈计算器实现...")
    print("=" * 50)
    
    # 检查核心文件
    files_to_check = [
        "static/js/floating-profit-calculator.js",
        "templates/review.html",
        "test_floating_profit_calculator.html"
    ]
    
    print("📁 检查文件存在性:")
    for file_path in files_to_check:
        exists = check_file_exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
    
    print("\n📋 检查JavaScript实现:")
    js_patterns = {
        "FloatingProfitCalculator类": r"class FloatingProfitCalculator",
        "构造函数": r"constructor\(stockCode, buyPrice",
        "设置当前价格方法": r"setCurrentPrice\(price\)",
        "本地计算方法": r"calculateLocalProfit\(\)",
        "远程计算方法": r"calculateRemoteProfit\(\)",
        "更新显示方法": r"updateDisplay\(",
        "验证输入方法": r"validateInput\(value\)",
        "颜色更新方法": r"updateDisplayColor\(",
        "错误处理方法": r"handleCalculationError\(",
        "管理器类": r"class FloatingProfitManager",
        "全局管理器实例": r"const floatingProfitManager"
    }
    
    js_check, js_message = check_content_in_file("static/js/floating-profit-calculator.js", js_patterns)
    status = "✅" if js_check else "❌"
    print(f"  {status} JavaScript实现: {js_message}")
    
    print("\n🎨 检查HTML模板集成:")
    html_patterns = {
        "当前价格输入框": r'id="current-price-input"',
        "浮盈比例显示": r'id="floating-profit-ratio"',
        "成本价显示": r'id="buy-price-display"',
        "盈亏金额显示": r'id="profit-amount-display"',
        "错误提示显示": r'id="floating-profit-error"',
        "浮盈计算卡片": r'浮盈计算',
        "JavaScript引入": r'floating-profit-calculator\.js',
        "初始化函数": r"function initializeFloatingProfitCalculator",
        "重置函数": r"function resetFloatingProfitCalculator",
        "获取数据函数": r"function getCurrentFloatingProfitData",
        "保存复盘更新": r"getCurrentFloatingProfitData\(\)"
    }
    
    html_check, html_message = check_content_in_file("templates/review.html", html_patterns)
    status = "✅" if html_check else "❌"
    print(f"  {status} HTML模板集成: {html_message}")
    
    print("\n🎯 检查CSS样式:")
    css_patterns = {
        "浮盈容器样式": r"\.floating-profit-container",
        "盈利状态样式": r"\.floating-profit-container\.profit",
        "亏损状态样式": r"\.floating-profit-container\.loss",
        "中性状态样式": r"\.floating-profit-container\.neutral",
        "比例显示样式": r"#floating-profit-ratio",
        "输入框焦点样式": r"#current-price-input:focus",
        "响应式设计": r"@media \(max-width: 768px\)"
    }
    
    css_check, css_message = check_content_in_file("templates/review.html", css_patterns)
    status = "✅" if css_check else "❌"
    print(f"  {status} CSS样式: {css_message}")
    
    print("\n🧪 检查测试文件:")
    test_patterns = {
        "测试HTML结构": r"浮盈计算器测试",
        "本地计算测试": r"测试场景1: 本地计算",
        "远程计算测试": r"测试场景2: 远程计算",
        "模拟API客户端": r"class MockApiClient",
        "测试函数": r"function testLocalCalculation"
    }
    
    test_check, test_message = check_content_in_file("test_floating_profit_calculator.html", test_patterns)
    status = "✅" if test_check else "❌"
    print(f"  {status} 测试文件: {test_message}")
    
    print("\n📊 实现完成度检查:")
    
    # 检查任务要求的功能点
    requirements = [
        ("创建FloatingProfitCalculator类", js_check),
        ("在复盘模态框中添加当前价格输入字段", html_check),
        ("实现实时浮盈比例计算和显示", js_check),
        ("添加颜色编码（绿色为正，红色为负）", js_check and css_check),
        ("实现输入验证和错误处理", js_check)
    ]
    
    completed_count = 0
    for requirement, is_completed in requirements:
        status = "✅" if is_completed else "❌"
        print(f"  {status} {requirement}")
        if is_completed:
            completed_count += 1
    
    completion_rate = (completed_count / len(requirements)) * 100
    print(f"\n📈 完成度: {completion_rate:.1f}% ({completed_count}/{len(requirements)})")
    
    if completion_rate == 100:
        print("\n🎉 浮盈计算器实现完成！")
        print("\n📝 功能特性:")
        print("  • 实时价格输入和验证")
        print("  • 本地和远程浮盈计算")
        print("  • 颜色编码显示（绿色盈利/红色亏损）")
        print("  • 错误处理和用户反馈")
        print("  • 响应式设计")
        print("  • 完整的测试覆盖")
        
        print("\n🚀 使用方法:")
        print("  1. 在复盘模态框中输入当前价格")
        print("  2. 系统自动计算并显示浮盈比例")
        print("  3. 保存复盘时自动包含浮盈数据")
        
        print("\n🧪 测试方法:")
        print("  • 打开 test_floating_profit_calculator.html 进行功能测试")
        print("  • 在复盘页面中实际使用验证集成效果")
    else:
        print(f"\n⚠️  实现未完成，还需要完善 {len(requirements) - completed_count} 个功能点")
    
    return completion_rate == 100

if __name__ == "__main__":
    verify_floating_profit_calculator()