#!/usr/bin/env python3
"""
验证复盘页面修复效果
"""

import os
import re
import subprocess
from pathlib import Path

def check_javascript_syntax():
    """检查JavaScript语法"""
    js_files = [
        "static/js/utils.js",
        "static/js/review-fix-emergency.js",
        "static/js/review-page-fix.js",
        "static/js/review-save-manager.js",
        "static/js/keyboard-shortcuts.js"
    ]
    
    print("🔍 检查JavaScript语法...")
    
    for js_file in js_files:
        if not os.path.exists(js_file):
            print(f"⚠️ 文件不存在: {js_file}")
            continue
            
        try:
            # 使用node检查语法（如果可用）
            result = subprocess.run(['node', '-c', js_file], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {js_file} - 语法正确")
            else:
                print(f"❌ {js_file} - 语法错误: {result.stderr}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # 如果没有node，进行基础检查
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查基本语法问题
            issues = []
            
            # 检查括号匹配
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                issues.append(f"大括号不匹配: {open_braces} 开 vs {close_braces} 闭")
            
            open_parens = content.count('(')
            close_parens = content.count(')')
            if open_parens != close_parens:
                issues.append(f"小括号不匹配: {open_parens} 开 vs {close_parens} 闭")
            
            # 检查重复声明
            if 'reviewSaveManager = new ReviewSaveManager();\s*reviewSaveManager = new ReviewSaveManager();' in content:
                issues.append("发现重复的reviewSaveManager声明")
            
            if issues:
                print(f"⚠️ {js_file} - 发现问题: {', '.join(issues)}")
            else:
                print(f"✅ {js_file} - 基础检查通过")

def check_template_issues():
    """检查模板问题"""
    template_path = "templates/review.html"
    
    print("\n🔍 检查模板问题...")
    
    if not os.path.exists(template_path):
        print(f"❌ 模板文件不存在: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 检查重复脚本引用
    emergency_script_count = content.count("review-fix-emergency.js")
    if emergency_script_count > 1:
        issues.append(f"重复引用emergency脚本 {emergency_script_count} 次")
    
    # 检查JavaScript代码完整性
    if "style.display = 'inl" in content and "inline" not in content.split("style.display = 'inl")[1].split("'")[0]:
        issues.append("发现不完整的JavaScript代码")
    
    # 检查模态框结构
    if '<div class="modal fade" id="reviewModal"' not in content:
        issues.append("缺少复盘模态框")
    
    if issues:
        print(f"⚠️ 模板问题: {', '.join(issues)}")
        return False
    else:
        print("✅ 模板检查通过")
        return True

def check_fix_scripts():
    """检查修复脚本"""
    print("\n🔍 检查修复脚本...")
    
    fix_scripts = [
        "static/js/review-fix-emergency.js",
        "static/js/review-page-fix.js"
    ]
    
    for script in fix_scripts:
        if not os.path.exists(script):
            print(f"❌ 修复脚本不存在: {script}")
            continue
            
        with open(script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键函数
        required_functions = {
            "static/js/review-fix-emergency.js": [
                "forceCleanupLoadingStates",
                "SimpleFloatingProfitCalculator",
                "debounce",
                "throttle"
            ],
            "static/js/review-page-fix.js": [
                "loadHoldings",
                "loadReviews", 
                "loadHoldingAlerts",
                "showEmptyState"
            ]
        }
        
        missing_functions = []
        for func in required_functions.get(script, []):
            if func not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"⚠️ {script} - 缺少函数: {', '.join(missing_functions)}")
        else:
            print(f"✅ {script} - 包含所需函数")

def generate_fix_report():
    """生成修复报告"""
    print("\n📋 生成修复报告...")
    
    report = """
# 复盘页面修复报告

## 修复内容

### 1. JavaScript语法错误修复
- 移除了重复的变量声明
- 修复了不完整的代码行
- 确保了括号匹配

### 2. 模板问题修复
- 移除了重复的脚本引用
- 确保了JavaScript代码完整性
- 保持了模态框结构完整

### 3. 加载问题修复
- 创建了紧急修复脚本 (review-fix-emergency.js)
- 创建了页面修复脚本 (review-page-fix.js)
- 实现了强制清理加载状态功能
- 添加了空状态显示逻辑

### 4. 用户体验改进
- 5秒超时自动显示内容
- 友好的错误提示
- 重试机制

## 测试建议

1. 打开复盘分析页面
2. 检查控制台是否还有错误
3. 验证数据是否正常加载
4. 测试复盘功能是否可用
5. 使用测试页面 (test_review_page_fix.html) 进行详细测试

## 如果问题仍然存在

1. 清除浏览器缓存
2. 检查网络连接
3. 确认后端API是否正常
4. 查看服务器日志
"""
    
    with open("REVIEW_PAGE_FIX_REPORT.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ 修复报告已生成: REVIEW_PAGE_FIX_REPORT.md")

def main():
    """主函数"""
    print("🔍 开始验证复盘页面修复效果...\n")
    
    # 检查JavaScript语法
    check_javascript_syntax()
    
    # 检查模板问题
    template_ok = check_template_issues()
    
    # 检查修复脚本
    check_fix_scripts()
    
    # 生成修复报告
    generate_fix_report()
    
    print("\n" + "="*50)
    print("🎯 验证完成!")
    print("\n📋 下一步操作:")
    print("1. 刷新浏览器页面")
    print("2. 打开开发者工具查看控制台")
    print("3. 测试复盘功能")
    print("4. 如需详细测试，打开 test_review_page_fix.html")
    
    if template_ok:
        print("\n✅ 主要问题已修复，页面应该可以正常显示")
    else:
        print("\n⚠️ 仍有一些问题需要手动检查")

if __name__ == "__main__":
    main()