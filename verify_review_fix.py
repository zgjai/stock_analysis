#!/usr/bin/env python3
"""
复盘页面修复验证脚本
验证 ReviewSaveManager 和 updateQuickReviewOptions 问题是否已修复
"""

import re
import os

def check_review_html_fixes():
    """检查 review.html 文件中的修复"""
    
    print("🔍 验证复盘页面修复...")
    
    file_path = "templates/review.html"
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_verified = []
    
    # 检查1: 备用 ReviewSaveManager 类定义
    if 'class ReviewSaveManager' in content and 'typeof ReviewSaveManager === \'undefined\'' in content:
        fixes_verified.append("✅ 备用 ReviewSaveManager 类已添加")
    else:
        fixes_verified.append("❌ 备用 ReviewSaveManager 类未找到")
    
    # 检查2: updateQuickReviewOptions 函数定义位置
    # 查找函数定义和调用的位置
    function_def_match = re.search(r'function updateQuickReviewOptions.*?\{', content, re.DOTALL)
    function_call_match = re.search(r'updateQuickReviewOptions\(data\.data\)', content)
    
    if function_def_match and function_call_match:
        def_pos = function_def_match.start()
        call_pos = function_call_match.start()
        
        if def_pos < call_pos:
            fixes_verified.append("✅ updateQuickReviewOptions 函数定义在调用之前")
        else:
            fixes_verified.append("❌ updateQuickReviewOptions 函数定义在调用之后")
    else:
        fixes_verified.append("❌ updateQuickReviewOptions 函数定义或调用未找到")
    
    # 检查3: 安全调用机制
    if 'typeof updateQuickReviewOptions === \'function\'' not in content:
        fixes_verified.append("✅ 已移除不必要的安全检查")
    else:
        fixes_verified.append("⚠️ 仍存在安全检查（可能是其他位置）")
    
    # 检查4: 错误处理改进
    if 'console.error(\'加载持仓数据失败:\', error)' in content:
        fixes_verified.append("✅ 错误处理机制完整")
    else:
        fixes_verified.append("❌ 错误处理机制不完整")
    
    # 输出结果
    print("\n📋 修复验证结果:")
    for fix in fixes_verified:
        print(f"  {fix}")
    
    # 统计
    success_count = sum(1 for fix in fixes_verified if fix.startswith("✅"))
    total_count = len(fixes_verified)
    
    print(f"\n📊 修复完成度: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

def check_javascript_syntax():
    """检查 JavaScript 语法是否正确"""
    
    print("\n🔍 检查 JavaScript 语法...")
    
    file_path = "templates/review.html"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 JavaScript 代码
    js_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    
    syntax_issues = []
    
    for i, js_code in enumerate(js_blocks):
        # 基本语法检查
        if js_code.strip():
            # 检查括号匹配
            open_braces = js_code.count('{')
            close_braces = js_code.count('}')
            if open_braces != close_braces:
                syntax_issues.append(f"脚本块 {i+1}: 大括号不匹配 ({open_braces} 开 vs {close_braces} 闭)")
            
            # 检查常见语法错误
            if re.search(r'function\s+\w+\s*\([^)]*\)\s*{[^}]*$', js_code, re.MULTILINE):
                syntax_issues.append(f"脚本块 {i+1}: 可能存在未闭合的函数")
    
    if syntax_issues:
        print("❌ 发现语法问题:")
        for issue in syntax_issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ JavaScript 语法检查通过")
        return True

def generate_fix_summary():
    """生成修复总结"""
    
    summary = """
# 复盘页面修复总结

## 修复的问题

### 1. 保存管理器未初始化
**问题**: `ReviewSaveManager` 类未定义，导致保存功能无法正常工作
**解决方案**: 
- 添加了备用的 `ReviewSaveManager` 类定义
- 在外部文件加载失败时提供基本的保存功能
- 包含完整的表单管理和保存逻辑

### 2. updateQuickReviewOptions 函数未定义
**问题**: 函数在定义之前被调用，导致 `ReferenceError`
**解决方案**:
- 将 `updateQuickReviewOptions` 函数定义移到调用位置之前
- 移除了不必要的安全检查
- 确保函数在需要时可用

## 修复后的改进

1. **更好的错误处理**: 添加了完整的错误捕获和用户友好的错误消息
2. **备用机制**: 当外部依赖加载失败时，提供基本功能
3. **性能优化**: 移除了不必要的检查，提高执行效率
4. **代码组织**: 改善了函数定义的顺序和结构

## 测试建议

1. 刷新复盘页面，检查控制台是否还有错误
2. 尝试加载持仓数据，验证 `updateQuickReviewOptions` 是否正常工作
3. 测试保存功能，确认 `ReviewSaveManager` 正常初始化
4. 检查快速复盘选项是否正确填充

## 预期结果

- ✅ 不再出现 "保存管理器未初始化" 错误
- ✅ 不再出现 "updateQuickReviewOptions is not defined" 错误
- ✅ 持仓数据加载正常
- ✅ 保存功能正常工作
"""
    
    with open('REVIEW_FIX_SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("📄 修复总结已保存到 REVIEW_FIX_SUMMARY.md")

def main():
    """主函数"""
    
    print("🚀 开始验证复盘页面修复...")
    
    # 检查修复
    fixes_ok = check_review_html_fixes()
    
    # 检查语法
    syntax_ok = check_javascript_syntax()
    
    # 生成总结
    generate_fix_summary()
    
    # 最终结果
    if fixes_ok and syntax_ok:
        print("\n🎉 所有修复验证通过！复盘页面应该可以正常工作了。")
        print("\n📋 下一步:")
        print("  1. 刷新浏览器中的复盘页面")
        print("  2. 检查控制台是否还有错误")
        print("  3. 测试持仓数据加载和保存功能")
        return True
    else:
        print("\n⚠️ 部分修复可能需要进一步调整。")
        return False

if __name__ == "__main__":
    main()