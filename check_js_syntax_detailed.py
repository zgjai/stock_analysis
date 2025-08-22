#!/usr/bin/env python3
"""
详细的 JavaScript 语法检查脚本
"""

import re
import os

def extract_js_blocks(content):
    """提取所有 JavaScript 代码块"""
    
    # 匹配 <script> 标签内的内容
    pattern = r'<script[^>]*>(.*?)</script>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    js_blocks = []
    for i, match in enumerate(matches):
        # 跳过空的或只有空白的脚本块
        if match.strip():
            js_blocks.append({
                'index': i + 1,
                'content': match,
                'lines': match.split('\n')
            })
    
    return js_blocks

def check_brace_balance(js_code):
    """检查大括号平衡"""
    
    # 移除字符串和注释中的大括号
    cleaned_code = remove_strings_and_comments(js_code)
    
    open_braces = cleaned_code.count('{')
    close_braces = cleaned_code.count('}')
    
    return {
        'balanced': open_braces == close_braces,
        'open': open_braces,
        'close': close_braces,
        'difference': open_braces - close_braces
    }

def remove_strings_and_comments(js_code):
    """移除字符串和注释，避免误判"""
    
    # 简单的字符串和注释移除
    # 这不是完美的解析器，但对基本检查足够了
    
    # 移除单行注释
    js_code = re.sub(r'//.*$', '', js_code, flags=re.MULTILINE)
    
    # 移除多行注释
    js_code = re.sub(r'/\*.*?\*/', '', js_code, flags=re.DOTALL)
    
    # 移除双引号字符串
    js_code = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '""', js_code)
    
    # 移除单引号字符串
    js_code = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", "''", js_code)
    
    # 移除模板字符串
    js_code = re.sub(r'`[^`\\]*(?:\\.[^`\\]*)*`', '``', js_code)
    
    return js_code

def find_unclosed_functions(js_code):
    """查找可能未闭合的函数"""
    
    lines = js_code.split('\n')
    unclosed_functions = []
    
    for i, line in enumerate(lines):
        # 查找函数定义
        if re.search(r'function\s+\w+\s*\([^)]*\)\s*\{', line):
            # 检查这一行后面是否有对应的闭合大括号
            remaining_code = '\n'.join(lines[i:])
            brace_info = check_brace_balance(remaining_code)
            
            if brace_info['difference'] > 0:
                unclosed_functions.append({
                    'line': i + 1,
                    'content': line.strip(),
                    'brace_difference': brace_info['difference']
                })
    
    return unclosed_functions

def check_syntax_errors(js_code):
    """检查常见的语法错误"""
    
    errors = []
    lines = js_code.split('\n')
    
    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        
        # 检查未闭合的括号
        if stripped.count('(') != stripped.count(')'):
            errors.append(f"第 {line_num} 行: 括号不匹配")
        
        # 检查未闭合的方括号
        if stripped.count('[') != stripped.count(']'):
            errors.append(f"第 {line_num} 行: 方括号不匹配")
        
        # 检查常见的语法错误模式
        if re.search(r'if\s*\([^)]*$', stripped):
            errors.append(f"第 {line_num} 行: if 语句可能未闭合")
        
        if re.search(r'for\s*\([^)]*$', stripped):
            errors.append(f"第 {line_num} 行: for 循环可能未闭合")
        
        if re.search(r'while\s*\([^)]*$', stripped):
            errors.append(f"第 {line_num} 行: while 循环可能未闭合")
    
    return errors

def main():
    """主函数"""
    
    print("🔍 详细 JavaScript 语法检查...")
    
    file_path = "templates/review.html"
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 JavaScript 代码块
    js_blocks = extract_js_blocks(content)
    print(f"📊 找到 {len(js_blocks)} 个 JavaScript 代码块")
    
    total_issues = 0
    
    for block in js_blocks:
        print(f"\n🔍 检查脚本块 {block['index']}...")
        
        # 检查大括号平衡
        brace_info = check_brace_balance(block['content'])
        if not brace_info['balanced']:
            print(f"❌ 大括号不平衡: {brace_info['open']} 开 vs {brace_info['close']} 闭 (差值: {brace_info['difference']})")
            total_issues += 1
        else:
            print(f"✅ 大括号平衡: {brace_info['open']} 开 vs {brace_info['close']} 闭")
        
        # 检查未闭合的函数
        unclosed_functions = find_unclosed_functions(block['content'])
        if unclosed_functions:
            print(f"❌ 发现 {len(unclosed_functions)} 个可能未闭合的函数:")
            for func in unclosed_functions:
                print(f"   - 第 {func['line']} 行: {func['content']}")
            total_issues += len(unclosed_functions)
        else:
            print("✅ 未发现未闭合的函数")
        
        # 检查其他语法错误
        syntax_errors = check_syntax_errors(block['content'])
        if syntax_errors:
            print(f"❌ 发现 {len(syntax_errors)} 个语法问题:")
            for error in syntax_errors:
                print(f"   - {error}")
            total_issues += len(syntax_errors)
        else:
            print("✅ 未发现其他语法问题")
    
    print(f"\n📊 检查完成，共发现 {total_issues} 个问题")
    
    if total_issues == 0:
        print("🎉 JavaScript 语法检查通过！")
        return True
    else:
        print("⚠️ 发现语法问题，建议进一步检查")
        return False

if __name__ == "__main__":
    main()