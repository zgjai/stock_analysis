#!/usr/bin/env python3
"""
修复所有语法错误 - CSS分号和JavaScript注释分号
"""

import re

def fix_all_syntax_errors():
    """修复templates/review.html中的所有语法错误"""
    
    with open('templates/review.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复CSS中缺少的分号
    css_fixes = [
        (r'(padding: 2px 4px)(\s*\n\s*})', r'\1;\2'),
        (r'(font-weight: bold)(\s*\n\s*})', r'\1;\2'),
    ]
    
    for pattern, replacement in css_fixes:
        content = re.sub(pattern, replacement, content)
    
    # 修复JavaScript注释后的分号
    js_comment_fixes = [
        (r'// ([^;]+);(\s*\n)', r'// \1\2'),
    ]
    
    for pattern, replacement in js_comment_fixes:
        content = re.sub(pattern, replacement, content)
    
    # 修复HTML中按钮文本后的分号
    html_fixes = [
        (r'(添加交易记录);', r'\1'),
        (r'(重新加载);', r'\1'),
        (r'(重试);', r'\1'),
        (r'(编辑);', r'\1'),
        (r'(创建复盘记录);', r'\1'),
    ]
    
    for pattern, replacement in html_fixes:
        content = re.sub(pattern, replacement, content)
    
    # 手动修复一些特定的问题
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # 修复JavaScript注释后的分号
        if '//' in line and line.strip().endswith(';') and not line.strip().endswith('});'):
            # 检查是否是注释行
            comment_start = line.find('//')
            if comment_start >= 0:
                before_comment = line[:comment_start].strip()
                comment_part = line[comment_start:].rstrip(';')
                if not before_comment or before_comment.endswith('{') or before_comment.endswith(','):
                    lines[i] = line[:comment_start] + comment_part
        
        # 修复HTML按钮中的分号
        if '<i class=' in line and line.strip().endswith(';'):
            if not any(js_keyword in line for js_keyword in ['function', 'var', 'let', 'const', 'return']):
                lines[i] = line.rstrip(';')
    
    content = '\n'.join(lines)
    
    with open('templates/review.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 所有语法错误已修复")

def main():
    """主修复流程"""
    print("🔧 开始修复所有语法错误...")
    
    fix_all_syntax_errors()
    
    print("✅ 语法错误修复完成！")
    print("🚀 请刷新页面测试")

if __name__ == '__main__':
    main()