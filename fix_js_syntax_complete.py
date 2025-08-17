#!/usr/bin/env python3
import re

def check_and_fix_js_syntax():
    """检查并修复JavaScript语法错误"""
    
    with open('templates/trading_records.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查常见的语法问题
    issues_found = []
    
    # 1. 检查未闭合的大括号
    lines = content.split('\n')
    
    # 重点检查第985-1000行
    for i in range(984, min(1000, len(lines))):
        line = lines[i]
        line_num = i + 1
        
        # 检查if语句是否有闭合的大括号
        if 'if (' in line and '{' in line:
            # 查找对应的闭合大括号
            brace_count = line.count('{') - line.count('}')
            j = i + 1
            while j < len(lines) and brace_count > 0:
                next_line = lines[j]
                brace_count += next_line.count('{') - next_line.count('}')
                j += 1
            
            if brace_count > 0:
                issues_found.append(f"第{line_num}行: if语句可能缺少闭合大括号")
    
    # 2. 检查特定的问题行
    problem_patterns = [
        (r'if\s*\([^)]+\)\s*\{[^}]*$', '未闭合的if语句'),
        (r'}\s*}', '多余的大括号'),
        (r'function\s+\w+\s*\([^)]*\)\s*\{[^}]*$', '未闭合的函数'),
    ]
    
    for i, line in enumerate(lines):
        line_num = i + 1
        if 985 <= line_num <= 1000:  # 重点检查问题区域
            for pattern, description in problem_patterns:
                if re.search(pattern, line):
                    issues_found.append(f"第{line_num}行: {description} - {line.strip()}")
    
    # 输出检查结果
    if issues_found:
        print("发现以下语法问题:")
        for issue in issues_found:
            print(f"  ❌ {issue}")
    else:
        print("✅ 未发现明显的语法问题")
    
    # 显示第985-1000行的内容
    print("\n第985-1000行的内容:")
    for i in range(984, min(1000, len(lines))):
        line_num = i + 1
        line = lines[i]
        print(f"{line_num:3d}: {line}")

if __name__ == "__main__":
    check_and_fix_js_syntax()