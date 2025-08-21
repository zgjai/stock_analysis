#!/usr/bin/env python3
"""
验证复盘页面紧急修复是否完整
"""

import os
import re

def check_js_file():
    """检查JavaScript修复文件"""
    js_file = 'static/js/review-emergency-fix.js'
    
    if not os.path.exists(js_file):
        print(f"❌ 文件不存在: {js_file}")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必需的对象和函数
    required_items = [
        'window.ReviewPageGlobals',
        'window.BatchProcessor',
        'window.FloatingProfitCalculator', 
        'window.holdingDaysEditorManager',
        'window.ReviewSaveManager',
        'window.floatingProfitManager',
        'window.initializeHoldingDaysEditors',
        'window.initializeFloatingProfitCalculator',
        'window.loadHoldings',
        'window.loadReviews',
        'window.openReviewModal',
        'window.saveReview',
        'displayHoldings',
        'showEmptyHoldings'
    ]
    
    print("检查JavaScript修复文件...")
    all_found = True
    
    for item in required_items:
        if item in content:
            print(f"✅ {item}")
        else:
            print(f"❌ {item} - 未找到")
            all_found = False
    
    return all_found

def check_template_file():
    """检查模板文件"""
    template_file = 'templates/review.html'
    
    if not os.path.exists(template_file):
        print(f"❌ 文件不存在: {template_file}")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n检查模板文件...")
    
    # 检查是否引用了紧急修复脚本
    if 'review-emergency-fix.js' in content:
        print("✅ 引用了紧急修复脚本")
    else:
        print("❌ 未引用紧急修复脚本")
        return False
    
    # 检查是否还有冲突的脚本引用
    conflicting_scripts = [
        'review-fix-emergency.js',
        'review-page-fix.js',
        'performance-optimizations.js',
        'review-integration.js'
    ]
    
    conflicts_found = False
    for script in conflicting_scripts:
        if script in content and script != 'review-emergency-fix.js':
            print(f"⚠️  发现可能冲突的脚本: {script}")
            conflicts_found = True
    
    if not conflicts_found:
        print("✅ 没有发现冲突的脚本引用")
    
    return True

def main():
    """主函数"""
    print("复盘页面紧急修复验证")
    print("=" * 40)
    
    js_ok = check_js_file()
    template_ok = check_template_file()
    
    print("\n" + "=" * 40)
    if js_ok and template_ok:
        print("🎉 验证通过！修复应该已经完成。")
        print("\n建议:")
        print("1. 重新加载复盘分析页面")
        print("2. 检查浏览器控制台是否还有错误")
        print("3. 测试持仓数据是否正常显示")
        return True
    else:
        print("❌ 验证失败，需要进一步修复。")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)