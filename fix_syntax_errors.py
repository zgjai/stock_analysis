#!/usr/bin/env python3
"""
修复具体的语法错误
"""

import re

def fix_review_html_syntax():
    """修复review.html中的语法错误"""
    with open('templates/review.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复对象属性后面多余的分号
    fixes = [
        # 修复对象属性中的分号
        (r'(\w+):\s*([^,}]+);(\s*[,}])', r'\1: \2\3'),
        
        # 修复特定的错误行
        ('failedStep: step.name;', 'failedStep: step.name'),
        ('stack: error.stack;', 'stack: error.stack'),
        ('duration: 1000;', 'duration: 1000'),
        ('force_refresh: true;', 'force_refresh: true'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    # 手动修复一些特殊情况
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # 修复注释后的分号
        if '// 聚焦到第一个输入框;' in line:
            lines[i] = line.replace('// 聚焦到第一个输入框;', '// 聚焦到第一个输入框')
        
        # 修复其他明显的语法错误
        if ': ' in line and line.strip().endswith(';') and not line.strip().endswith('});'):
            # 检查是否是对象属性
            if re.match(r'\s*\w+:\s*[^,}]+;$', line.strip()):
                lines[i] = line.rstrip(';')
    
    content = '\n'.join(lines)
    
    with open('templates/review.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ review.html 语法错误已修复")

def main():
    """主修复流程"""
    print("🔧 修复具体的语法错误...")
    
    fix_review_html_syntax()
    
    print("✅ 语法错误修复完成！")
    print("🚀 请刷新页面测试")

if __name__ == '__main__':
    main()