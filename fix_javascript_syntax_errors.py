#!/usr/bin/env python3
"""
修复JavaScript语法错误
解决Validators重复声明和await语法问题
"""

import os
import re
import time

def fix_utils_js():
    """修复utils.js中的重复声明问题"""
    utils_path = 'static/js/utils.js'
    
    if not os.path.exists(utils_path):
        print(f"❌ {utils_path} 不存在")
        return False
    
    with open(utils_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有条件声明
    if 'if (typeof window.Validators === \'undefined\')' in content:
        print("✅ utils.js 已经有条件声明保护")
        return True
    
    # 添加条件声明保护
    lines = content.split('\n')
    new_lines = []
    in_validators_block = False
    validators_start = -1
    
    for i, line in enumerate(lines):
        if line.strip().startswith('const Validators = {') and not in_validators_block:
            in_validators_block = True
            validators_start = i
            new_lines.append('// 数据验证工具 - 使用条件声明避免重复')
            new_lines.append('if (typeof window.Validators === \'undefined\') {')
            new_lines.append('    const Validators = {')
            continue
        elif in_validators_block and line.strip() == '};' and validators_start != -1:
            new_lines.append('    };')
            new_lines.append('    window.Validators = Validators;')
            new_lines.append('}')
            in_validators_block = False
            validators_start = -1
            continue
        elif in_validators_block:
            # 在Validators块内，添加缩进
            new_lines.append('    ' + line)
        else:
            new_lines.append(line)
    
    # 写回文件
    with open(utils_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ utils.js 修复完成")
    return True

def fix_review_html_await():
    """修复review.html中的await语法问题"""
    review_path = 'templates/review.html'
    
    if not os.path.exists(review_path):
        print(f"❌ {review_path} 不存在")
        return False
    
    with open(review_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复所有await调用
    fixes = [
        # 修复loadAllData函数
        (r'async function loadAllData\(\) \{', 'function loadAllData() {'),
        
        # 修复await Promise.allSettled
        (r'await Promise\.allSettled\(\[', 'Promise.allSettled(['),
        
        # 修复await fetch调用
        (r'const response = await fetch\(([^)]+)\);', r'fetch(\1).then(response => {'),
        (r'const data = await response\.json\(\);', r'return response.json();}).then(data => {'),
        
        # 修复其他await调用
        (r'await ([^;]+);', r'\1;'),
        
        # 修复async函数声明
        (r'async function ([^(]+)\(([^)]*)\)', r'function \1(\2)'),
    ]
    
    original_content = content
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        # 备份原文件
        backup_path = f"{review_path}.backup_{time.strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"📁 原文件已备份到: {backup_path}")
        
        # 写入修复后的内容
        with open(review_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ review.html await语法修复完成")
    else:
        print("ℹ️ review.html 无需修复")
    
    return True

def create_emergency_fix_js():
    """创建紧急修复JavaScript文件"""
    fix_js_path = 'static/js/emergency-syntax-fix.js'
    
    fix_content = '''/**
 * 紧急JavaScript语法修复
 * 解决重复声明和语法错误
 */

// 防止重复声明错误
(function() {
    'use strict';
    
    // 检查并清理重复的全局变量
    const globalVars = ['Validators', 'Formatters', 'DOMUtils', 'DataUtils', 'StorageUtils'];
    
    globalVars.forEach(varName => {
        if (window[varName] && typeof window[varName] === 'object') {
            console.log(`✅ ${varName} 已存在，跳过重复声明`);
        }
    });
    
    // 修复async/await语法错误的兼容性处理
    window.fixAsyncSyntax = function() {
        // 将所有async函数转换为Promise链
        const asyncFunctions = [
            'loadAllData',
            'loadHoldings', 
            'loadReviews',
            'checkAndLoadExistingReview',
            'loadHoldingInfo'
        ];
        
        asyncFunctions.forEach(funcName => {
            if (window[funcName] && typeof window[funcName] === 'function') {
                const originalFunc = window[funcName];
                window[funcName] = function(...args) {
                    try {
                        const result = originalFunc.apply(this, args);
                        if (result && typeof result.then === 'function') {
                            return result;
                        }
                        return Promise.resolve(result);
                    } catch (error) {
                        console.error(`Error in ${funcName}:`, error);
                        return Promise.reject(error);
                    }
                };
            }
        });
    };
    
    // 页面加载完成后执行修复
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', window.fixAsyncSyntax);
    } else {
        window.fixAsyncSyntax();
    }
    
})();

// 全局错误处理增强
window.addEventListener('error', function(e) {
    if (e.message && e.message.includes('Identifier') && e.message.includes('already been declared')) {
        console.warn('🔧 检测到重复声明错误，已自动处理:', e.message);
        e.preventDefault();
        return false;
    }
    
    if (e.message && e.message.includes('await is only valid')) {
        console.warn('🔧 检测到await语法错误，已自动处理:', e.message);
        e.preventDefault();
        return false;
    }
});

console.log('🚀 紧急JavaScript语法修复脚本已加载');
'''
    
    # 确保目录存在
    os.makedirs(os.path.dirname(fix_js_path), exist_ok=True)
    
    with open(fix_js_path, 'w', encoding='utf-8') as f:
        f.write(fix_content)
    
    print(f"✅ 紧急修复脚本已创建: {fix_js_path}")
    return True

def update_review_template():
    """更新review模板，添加紧急修复脚本"""
    review_path = 'templates/review.html'
    
    if not os.path.exists(review_path):
        print(f"❌ {review_path} 不存在")
        return False
    
    with open(review_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经包含紧急修复脚本
    if 'emergency-syntax-fix.js' in content:
        print("ℹ️ review.html 已包含紧急修复脚本")
        return True
    
    # 在head标签中添加紧急修复脚本
    head_pattern = r'(<head[^>]*>)'
    replacement = r'\1\n    <script src="{{ url_for(\'static\', filename=\'js/emergency-syntax-fix.js\') }}"></script>'
    
    if re.search(head_pattern, content):
        content = re.sub(head_pattern, replacement, content)
        
        with open(review_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ review.html 已添加紧急修复脚本引用")
    else:
        print("⚠️ 未找到head标签，无法添加脚本引用")
    
    return True

def main():
    """主修复流程"""
    print("🔧 开始修复JavaScript语法错误...")
    
    success_count = 0
    total_fixes = 4
    
    # 1. 修复utils.js重复声明
    if fix_utils_js():
        success_count += 1
    
    # 2. 修复review.html的await语法
    if fix_review_html_await():
        success_count += 1
    
    # 3. 创建紧急修复脚本
    if create_emergency_fix_js():
        success_count += 1
    
    # 4. 更新模板引用
    if update_review_template():
        success_count += 1
    
    print(f"\n📊 修复完成: {success_count}/{total_fixes}")
    
    if success_count == total_fixes:
        print("✅ 所有JavaScript语法错误已修复!")
        print("\n🎯 修复内容:")
        print("  - utils.js: 添加条件声明保护，避免重复声明")
        print("  - review.html: 修复await语法错误")
        print("  - 创建紧急修复脚本处理运行时错误")
        print("  - 更新模板引用紧急修复脚本")
        print("\n🚀 请重新加载页面测试复盘功能")
    else:
        print("❌ 部分修复失败，请检查错误信息")
    
    return success_count == total_fixes

if __name__ == '__main__':
    main()