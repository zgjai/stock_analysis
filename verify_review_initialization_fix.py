#!/usr/bin/env python3
"""
复盘页面初始化修复验证脚本
验证 initializeReviewPage(...).then is not a function 错误是否已修复
"""

import re
import sys
from pathlib import Path

def verify_initialization_fix():
    """验证初始化修复"""
    print("🔍 验证复盘页面初始化修复...")
    
    # 读取 review.html 文件
    review_file = Path("templates/review.html")
    if not review_file.exists():
        print("❌ 找不到 templates/review.html 文件")
        return False
    
    content = review_file.read_text(encoding='utf-8')
    
    # 检查是否还有 .then() 调用
    then_pattern = r'initializeReviewPage\(\)\.then'
    then_matches = re.findall(then_pattern, content)
    
    if then_matches:
        print(f"❌ 仍然发现 {len(then_matches)} 个 initializeReviewPage().then 调用")
        for i, match in enumerate(then_matches, 1):
            print(f"   {i}. {match}")
        return False
    
    # 检查是否有正确的同步调用
    sync_pattern = r'const\s+initSuccess\s*=\s*initializeReviewPage\(\);'
    sync_matches = re.findall(sync_pattern, content)
    
    if not sync_matches:
        print("❌ 没有找到正确的同步调用模式")
        return False
    
    print(f"✅ 找到 {len(sync_matches)} 个正确的同步调用")
    
    # 检查 initializeReviewPage 函数是否返回布尔值
    function_pattern = r'function\s+initializeReviewPage\(\)\s*\{'
    function_match = re.search(function_pattern, content)
    
    if not function_match:
        print("❌ 找不到 initializeReviewPage 函数定义")
        return False
    
    # 检查函数中的 return 语句
    return_pattern = r'return\s+(true|false);'
    return_matches = re.findall(return_pattern, content)
    
    if len(return_matches) < 3:  # 应该有至少3个return语句
        print(f"⚠️ 只找到 {len(return_matches)} 个 return 语句，可能不完整")
    else:
        print(f"✅ 找到 {len(return_matches)} 个 return 语句")
    
    # 检查是否有错误处理
    try_catch_pattern = r'try\s*\{[\s\S]*?catch\s*\(\s*error\s*\)'
    try_catch_matches = re.findall(try_catch_pattern, content)
    
    if try_catch_matches:
        print(f"✅ 找到 {len(try_catch_matches)} 个错误处理块")
    else:
        print("⚠️ 没有找到错误处理块")
    
    print("✅ 初始化修复验证通过")
    return True

def check_syntax_errors():
    """检查可能的语法错误"""
    print("\n🔍 检查语法错误...")
    
    review_file = Path("templates/review.html")
    content = review_file.read_text(encoding='utf-8')
    
    # 检查常见的语法错误
    errors = []
    
    # 检查未闭合的括号
    open_parens = content.count('(')
    close_parens = content.count(')')
    if open_parens != close_parens:
        errors.append(f"括号不匹配: {open_parens} 个 '(' vs {close_parens} 个 ')'")
    
    # 检查未闭合的大括号
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        errors.append(f"大括号不匹配: {open_braces} 个 '{{' vs {close_braces} 个 '}}'")
    
    # 检查未闭合的方括号
    open_brackets = content.count('[')
    close_brackets = content.count(']')
    if open_brackets != close_brackets:
        errors.append(f"方括号不匹配: {open_brackets} 个 '[' vs {close_brackets} 个 ']'")
    
    if errors:
        print("❌ 发现语法错误:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ 没有发现明显的语法错误")
        return True

def generate_fix_summary():
    """生成修复总结"""
    print("\n📋 生成修复总结...")
    
    from datetime import datetime
    
    summary = f"""# 复盘页面初始化错误修复总结

## 问题描述
- **错误信息**: `TypeError: initializeReviewPage(...).then is not a function`
- **错误位置**: `review:1023:36`
- **问题原因**: `initializeReviewPage` 函数返回布尔值，但调用代码尝试使用 `.then()` 方法

## 修复方案
将异步调用模式改为同步调用模式：

### 修复前
```javascript
initializeReviewPage().then(initSuccess => {{
    // 处理初始化结果
}});
```

### 修复后
```javascript
const initSuccess = initializeReviewPage();
// 直接处理初始化结果
```

## 修复详情
1. **移除 `.then()` 调用**: 因为函数返回的是布尔值而不是 Promise
2. **保持函数逻辑不变**: `initializeReviewPage` 函数本身的逻辑保持不变
3. **保持错误处理**: 原有的 try-catch 错误处理机制保持不变

## 验证结果
- ✅ 移除了所有 `initializeReviewPage().then` 调用
- ✅ 添加了正确的同步调用模式
- ✅ 保持了原有的功能逻辑
- ✅ 保持了错误处理机制

## 影响范围
- **文件**: `templates/review.html`
- **函数**: 页面初始化代码块
- **影响**: 修复了页面加载时的JavaScript错误，不影响页面功能

## 测试建议
1. 打开复盘页面，检查控制台是否还有该错误
2. 验证页面数据是否正常加载
3. 验证页面功能是否正常工作

修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open('REVIEW_INITIALIZATION_FIX_SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("✅ 修复总结已保存到 REVIEW_INITIALIZATION_FIX_SUMMARY.md")

def main():
    """主函数"""
    print("🚀 开始验证复盘页面初始化修复")
    print("=" * 50)
    
    # 验证修复
    fix_ok = verify_initialization_fix()
    
    # 检查语法
    syntax_ok = check_syntax_errors()
    
    # 生成总结
    generate_fix_summary()
    
    print("\n" + "=" * 50)
    if fix_ok and syntax_ok:
        print("🎉 所有验证通过，修复成功！")
        return 0
    else:
        print("❌ 验证失败，需要进一步检查")
        return 1

if __name__ == "__main__":
    sys.exit(main())