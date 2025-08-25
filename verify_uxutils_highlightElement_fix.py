#!/usr/bin/env python3
"""
验证 UXUtils.highlightElement 修复
"""

import os
import re

def check_utils_js():
    """检查 utils.js 中是否包含 highlightElement 方法"""
    utils_path = 'static/js/utils.js'
    
    if not os.path.exists(utils_path):
        print("❌ utils.js 文件不存在")
        return False
    
    with open(utils_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含 highlightElement 方法
    if 'highlightElement:' in content:
        print("✅ utils.js 中包含 highlightElement 方法")
        
        # 检查方法实现
        highlight_pattern = r'highlightElement:\s*\([^)]*\)\s*=>\s*\{'
        if re.search(highlight_pattern, content):
            print("✅ highlightElement 方法实现正确")
            return True
        else:
            print("❌ highlightElement 方法实现不正确")
            return False
    else:
        print("❌ utils.js 中缺少 highlightElement 方法")
        return False

def check_css_styles():
    """检查 CSS 文件中是否包含高亮样式"""
    css_path = 'static/css/main.css'
    
    if not os.path.exists(css_path):
        print("❌ main.css 文件不存在")
        return False
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含高亮样式
    if '.field-highlight-error' in content:
        print("✅ main.css 中包含字段高亮错误样式")
        
        if 'field-error-highlight' in content:
            print("✅ main.css 中包含高亮动画")
            return True
        else:
            print("❌ main.css 中缺少高亮动画")
            return False
    else:
        print("❌ main.css 中缺少字段高亮样式")
        return False

def check_form_validation_usage():
    """检查 form-validation.js 中对 highlightElement 的使用"""
    form_validation_path = 'static/js/form-validation.js'
    
    if not os.path.exists(form_validation_path):
        print("❌ form-validation.js 文件不存在")
        return False
    
    with open(form_validation_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否调用了 UXUtils.highlightElement
    if 'UXUtils.highlightElement' in content:
        print("✅ form-validation.js 中正确调用了 UXUtils.highlightElement")
        return True
    else:
        print("❌ form-validation.js 中没有调用 UXUtils.highlightElement")
        return False

def main():
    print("开始验证 UXUtils.highlightElement 修复...")
    print("=" * 50)
    
    checks = [
        ("检查 utils.js 中的 highlightElement 方法", check_utils_js),
        ("检查 CSS 高亮样式", check_css_styles),
        ("检查 form-validation.js 中的使用", check_form_validation_usage)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ 所有检查通过！UXUtils.highlightElement 修复成功")
        print("\n建议:")
        print("1. 在浏览器中打开 test_uxutils_highlightElement_fix.html 进行功能测试")
        print("2. 测试表单验证时的字段高亮效果")
        print("3. 确认控制台不再出现 'UXUtils.highlightElement is not a function' 错误")
    else:
        print("❌ 部分检查失败，请检查修复内容")
    
    return all_passed

if __name__ == "__main__":
    main()