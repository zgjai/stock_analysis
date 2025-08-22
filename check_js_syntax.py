#!/usr/bin/env python3
"""
检查JavaScript语法错误
"""

import re
import subprocess
import tempfile
import os

def extract_js_from_html():
    """从HTML中提取JavaScript代码"""
    
    with open('templates/review.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取<script>标签中的JavaScript代码
    js_pattern = r'<script[^>]*>(.*?)</script>'
    js_matches = re.findall(js_pattern, content, re.DOTALL)
    
    js_code = ""
    for match in js_matches:
        # 跳过src引用的脚本
        if 'src=' not in match:
            js_code += match + "\n"
    
    return js_code

def check_syntax_with_node():
    """使用Node.js检查JavaScript语法"""
    
    js_code = extract_js_from_html()
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(js_code)
        temp_file = f.name
    
    try:
        # 使用node检查语法
        result = subprocess.run(['node', '--check', temp_file], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ JavaScript语法检查通过")
            return True
        else:
            print("❌ JavaScript语法错误:")
            print(result.stderr)
            
            # 尝试定位错误行
            if 'SyntaxError' in result.stderr:
                lines = result.stderr.split('\n')
                for line in lines:
                    if 'SyntaxError' in line:
                        print(f"错误详情: {line}")
            
            return False
            
    except FileNotFoundError:
        print("⚠️ Node.js未安装，无法进行语法检查")
        return None
    finally:
        # 清理临时文件
        os.unlink(temp_file)

def find_syntax_errors_manually():
    """手动查找常见的语法错误"""
    
    with open('templates/review.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    errors = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # 检查常见的语法错误
        if line_content:
            # 检查未闭合的括号
            open_parens = line_content.count('(')
            close_parens = line_content.count(')')
            if open_parens != close_parens and not line_content.endswith(','):
                errors.append(f"第{i}行: 括号不匹配 - {line_content}")
            
            # 检查未闭合的大括号
            open_braces = line_content.count('{')
            close_braces = line_content.count('}')
            if open_braces != close_braces and not any(keyword in line_content for keyword in ['if', 'for', 'function', 'try']):
                errors.append(f"第{i}行: 大括号不匹配 - {line_content}")
            
            # 检查箭头函数语法
            if '=>' in line_content:
                # 检查箭头函数前是否有正确的参数
                arrow_pos = line_content.find('=>')
                before_arrow = line_content[:arrow_pos].strip()
                if not (before_arrow.endswith(')') or before_arrow.split()[-1].isidentifier()):
                    errors.append(f"第{i}行: 箭头函数语法错误 - {line_content}")
            
            # 检查对象属性后的分号
            if ':' in line_content and line_content.endswith(';') and not line_content.strip().startswith('//'):
                # 检查是否在对象定义中
                if not any(keyword in line_content for keyword in ['for', 'if', 'while']):
                    errors.append(f"第{i}行: 对象属性后不应有分号 - {line_content}")
    
    return errors

def main():
    """主检查流程"""
    print("🔍 开始JavaScript语法检查...")
    
    # 手动检查
    manual_errors = find_syntax_errors_manually()
    if manual_errors:
        print("❌ 发现语法错误:")
        for error in manual_errors:
            print(f"  {error}")
    else:
        print("✅ 手动检查未发现明显错误")
    
    # Node.js检查
    node_result = check_syntax_with_node()
    
    if manual_errors or node_result is False:
        print("\n🔧 建议修复:")
        print("1. 检查括号和大括号是否匹配")
        print("2. 检查箭头函数语法是否正确")
        print("3. 检查对象属性定义是否正确")
        print("4. 检查是否有多余的分号")
    
    return len(manual_errors) == 0 and node_result is not False

if __name__ == '__main__':
    main()