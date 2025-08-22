#!/usr/bin/env python3
"""
验证JavaScript修复效果
"""

import os
import re

def check_utils_js():
    """检查utils.js修复状态"""
    utils_path = 'static/js/utils.js'
    
    if not os.path.exists(utils_path):
        return False, "utils.js文件不存在"
    
    with open(utils_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有条件声明保护
    if 'if (typeof window.Validators === \'undefined\')' in content:
        return True, "✅ utils.js已有条件声明保护"
    else:
        return False, "❌ utils.js缺少条件声明保护"

def check_review_html():
    """检查review.html修复状态"""
    review_path = 'templates/review.html'
    
    if not os.path.exists(review_path):
        return False, "review.html文件不存在"
    
    with open(review_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 检查是否还有裸露的await调用
    await_matches = re.findall(r'^\s*await\s+', content, re.MULTILINE)
    if await_matches:
        issues.append(f"发现{len(await_matches)}个裸露的await调用")
    
    # 检查是否包含紧急修复脚本
    if 'emergency-syntax-fix.js' in content:
        issues.append("✅ 已包含紧急语法修复脚本")
    else:
        issues.append("❌ 缺少紧急语法修复脚本")
    
    if not issues or all('✅' in issue for issue in issues):
        return True, "; ".join(issues)
    else:
        return False, "; ".join(issues)

def check_emergency_fix_script():
    """检查紧急修复脚本"""
    script_path = 'static/js/emergency-syntax-fix.js'
    
    if not os.path.exists(script_path):
        return False, "紧急修复脚本不存在"
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键功能
    required_features = [
        'fixAsyncSyntax',
        'addEventListener',
        'Identifier.*already been declared',
        'await is only valid'
    ]
    
    missing_features = []
    for feature in required_features:
        if not re.search(feature, content):
            missing_features.append(feature)
    
    if not missing_features:
        return True, "✅ 紧急修复脚本功能完整"
    else:
        return False, f"❌ 缺少功能: {', '.join(missing_features)}"

def check_syntax_errors():
    """检查常见的JavaScript语法错误"""
    js_files = [
        'static/js/utils.js',
        'static/js/emergency-syntax-fix.js',
        'static/js/review-emergency-fix.js'
    ]
    
    errors = []
    
    for js_file in js_files:
        if not os.path.exists(js_file):
            continue
            
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查常见语法错误
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # 检查未闭合的括号
            if line.count('(') != line.count(')'):
                if not line.strip().endswith(',') and not line.strip().endswith('{'):
                    errors.append(f"{js_file}:{i} 可能的括号不匹配")
            
            # 检查未闭合的大括号
            if line.count('{') != line.count('}'):
                if not any(keyword in line for keyword in ['if', 'for', 'while', 'function', 'try', 'catch']):
                    errors.append(f"{js_file}:{i} 可能的大括号不匹配")
    
    if not errors:
        return True, "✅ 未发现明显的语法错误"
    else:
        return False, f"❌ 发现{len(errors)}个潜在语法错误"

def main():
    """主验证流程"""
    print("🔍 开始验证JavaScript修复效果...\n")
    
    checks = [
        ("utils.js修复状态", check_utils_js),
        ("review.html修复状态", check_review_html),
        ("紧急修复脚本", check_emergency_fix_script),
        ("语法错误检查", check_syntax_errors)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            success, message = check_func()
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{check_name}: {status}")
            print(f"  {message}\n")
            results.append(success)
        except Exception as e:
            print(f"{check_name}: ❌ 异常")
            print(f"  错误: {str(e)}\n")
            results.append(False)
    
    # 总结
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"验证结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 所有检查都通过！JavaScript修复成功！")
        print("\n📋 建议:")
        print("1. 重启Flask应用")
        print("2. 清除浏览器缓存")
        print("3. 访问复盘页面测试功能")
        print("4. 检查浏览器控制台是否还有错误")
    else:
        print("⚠️ 部分检查未通过，可能需要进一步修复")
    
    return passed == total

if __name__ == '__main__':
    main()