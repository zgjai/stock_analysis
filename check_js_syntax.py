#!/usr/bin/env python3
import re
import subprocess
import tempfile
import os

def extract_js_from_html(html_file):
    """从HTML文件中提取JavaScript代码"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有script标签中的内容
    js_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    
    # 合并所有JavaScript代码
    js_code = '\n'.join(js_blocks)
    return js_code

def check_js_syntax(js_code):
    """使用Node.js检查JavaScript语法"""
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_code)
            temp_file = f.name
        
        # 使用node检查语法
        result = subprocess.run(['node', '-c', temp_file], 
                              capture_output=True, text=True)
        
        # 清理临时文件
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return True, "JavaScript语法检查通过"
        else:
            return False, result.stderr
            
    except FileNotFoundError:
        return False, "Node.js未安装，无法检查JavaScript语法"
    except Exception as e:
        return False, f"语法检查失败: {str(e)}"

def main():
    html_file = 'templates/trading_records.html'
    
    print(f"检查文件: {html_file}")
    
    # 提取JavaScript代码
    js_code = extract_js_from_html(html_file)
    print(f"提取的JavaScript代码长度: {len(js_code)} 字符")
    
    # 检查语法
    is_valid, message = check_js_syntax(js_code)
    
    if is_valid:
        print("✅ " + message)
    else:
        print("❌ " + message)
        
        # 如果有语法错误，尝试找到具体位置
        lines = js_code.split('\n')
        for i, line in enumerate(lines, 1):
            if i >= 980 and i <= 1000:  # 重点检查第989行附近
                print(f"第{i}行: {line}")

if __name__ == "__main__":
    main()