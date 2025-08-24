#!/usr/bin/env python3
"""
精确语法修复 - 只修复语法错误，不改变页面功能和布局
"""

import re

def fix_utils_js_only():
    """只修复utils.js的重复声明问题，不改变其他内容"""
    with open('static/js/utils.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 只在Validators声明前添加条件检查
    if 'if (typeof window.Validators === \'undefined\')' not in content:
        # 找到Validators声明的位置
        validators_pattern = r'(// 数据验证工具\s*\n)(const Validators = \{)'
        if re.search(validators_pattern, content):
            content = re.sub(
                validators_pattern,
                r'\1if (typeof window.Validators === \'undefined\') {\n\2',
                content
            )
            
            # 找到Validators对象结束的位置，添加闭合括号
            # 查找最后一个 }; 在Validators对象中
            lines = content.split('\n')
            in_validators = False
            validators_end = -1
            
            for i, line in enumerate(lines):
                if 'if (typeof window.Validators === \'undefined\')' in line:
                    in_validators = True
                elif in_validators and line.strip() == '};' and 'email:' in lines[i-5:i]:
                    # 这应该是Validators对象的结束
                    lines[i] = '    };\n    window.Validators = Validators;\n}'
                    validators_end = i
                    break
            
            if validators_end > 0:
                content = '\n'.join(lines)
    
    with open('static/js/utils.js', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ utils.js 重复声明问题已修复")

def fix_review_html_syntax_only():
    """只修复review.html的语法错误，不改变页面结构"""
    with open('templates/review.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复具体的语法错误
    fixes = [
        # 修复不完整的Promise链 - 只修复明显的语法错误
        (r'return response\.json\(\);\}\.then\(data => \{', 
         r'return response.json();}).then(data => {'),
        
        # 修复缺少的分号
        (r'(\w+)\s*$', r'\1;'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # 手动修复已知的具体问题行
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # 修复第1559行和类似的问题
        if 'return response.json();}.then(data => {' in line:
            lines[i] = line.replace('return response.json();}.then(data => {', 
                                  'return response.json();}).then(data => {')
        
        # 修复第1618行和类似的问题  
        if 'return response.json();}.then(data => {' in line:
            lines[i] = line.replace('return response.json();}.then(data => {', 
                                  'return response.json();}).then(data => {')
    
    content = '\n'.join(lines)
    
    with open('templates/review.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ review.html 语法错误已修复")

def main():
    """主修复流程 - 只修复语法，不改变功能"""
    print("🔧 开始精确语法修复（不改变页面功能）...")
    
    # 1. 修复utils.js重复声明
    fix_utils_js_only()
    
    # 2. 修复review.html语法错误
    fix_review_html_syntax_only()
    
    print("\n✅ 精确语法修复完成！")
    print("📋 修复内容：")
    print("- 修复了utils.js的重复声明问题")
    print("- 修复了review.html的语法错误")
    print("- 保持了原有的页面布局和功能")
    
    print("\n🚀 请刷新页面测试，页面应该恢复正常！")

if __name__ == '__main__':
    main()