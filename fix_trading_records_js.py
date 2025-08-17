#!/usr/bin/env python3
"""
修复交易记录页面的JavaScript问题
"""

import re
import os

def fix_trading_records_template():
    """修复交易记录模板中的JavaScript问题"""
    
    template_path = 'templates/trading_records.html'
    
    if not os.path.exists(template_path):
        print(f"错误: 文件 {template_path} 不存在")
        return False
    
    try:
        # 读取文件内容
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"原文件大小: {len(content)} 字符")
        
        # 检查是否有未完成的代码行
        issues_found = []
        
        # 检查是否有未完成的参数行
        if 'per_page: t\n' in content or 'per_page: t' in content:
            issues_found.append("发现未完成的per_page参数")
            content = content.replace('per_page: t', 'per_page: this.perPage')
        
        # 检查是否有未闭合的函数或对象
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            issues_found.append(f"大括号不匹配: 开 {open_braces}, 闭 {close_braces}")
        
        # 检查是否有未闭合的括号
        open_parens = content.count('(')
        close_parens = content.count(')')
        if open_parens != close_parens:
            issues_found.append(f"圆括号不匹配: 开 {open_parens}, 闭 {close_parens}")
        
        # 检查是否有未完成的字符串
        single_quotes = content.count("'")
        double_quotes = content.count('"')
        if single_quotes % 2 != 0:
            issues_found.append(f"单引号不匹配: {single_quotes}")
        if double_quotes % 2 != 0:
            issues_found.append(f"双引号不匹配: {double_quotes}")
        
        # 检查是否有语法错误的常见模式
        syntax_patterns = [
            (r'per_page:\s*t\s*[,}]', 'per_page: this.perPage'),
            (r'function\s+\w+\s*\(\s*\)\s*{[^}]*$', None),  # 未闭合的函数
            (r'class\s+\w+\s*{[^}]*$', None),  # 未闭合的类
        ]
        
        for pattern, replacement in syntax_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                if replacement:
                    content = re.sub(pattern, replacement, content)
                    issues_found.append(f"修复了模式: {pattern}")
                else:
                    issues_found.append(f"发现可能的语法错误: {pattern}")
        
        if issues_found:
            print("发现的问题:")
            for issue in issues_found:
                print(f"  - {issue}")
            
            # 备份原文件
            backup_path = template_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已创建备份文件: {backup_path}")
            
            # 写入修复后的内容
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("已修复JavaScript问题")
            return True
        else:
            print("未发现明显的JavaScript语法问题")
            return True
            
    except Exception as e:
        print(f"修复过程中出错: {e}")
        return False

def validate_javascript_syntax():
    """验证JavaScript语法"""
    
    template_path = 'templates/trading_records.html'
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取JavaScript代码
        js_pattern = r'<script[^>]*>(.*?)</script>'
        js_blocks = re.findall(js_pattern, content, re.DOTALL)
        
        print(f"找到 {len(js_blocks)} 个JavaScript代码块")
        
        for i, js_code in enumerate(js_blocks):
            print(f"\n代码块 {i+1} (长度: {len(js_code)} 字符):")
            
            # 检查常见的语法问题
            lines = js_code.split('\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                
                # 检查未完成的语句
                if line.endswith(',') and not any(x in line for x in ['{', '[', '(']):
                    if line_num == len(lines) or not lines[line_num].strip():
                        print(f"  警告: 第{line_num}行可能有未完成的语句: {line}")
                
                # 检查未闭合的字符串
                if line.count('"') % 2 != 0 or line.count("'") % 2 != 0:
                    print(f"  警告: 第{line_num}行可能有未闭合的字符串: {line}")
        
        return True
        
    except Exception as e:
        print(f"验证过程中出错: {e}")
        return False

if __name__ == '__main__':
    print("开始修复交易记录页面的JavaScript问题...")
    
    # 修复问题
    if fix_trading_records_template():
        print("\n验证修复结果...")
        validate_javascript_syntax()
        print("\n修复完成!")
    else:
        print("修复失败!")