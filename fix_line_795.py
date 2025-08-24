#!/usr/bin/env python3
"""
精确修复第795行的语法错误
"""

def fix_line_795():
    """修复第795行的语法错误"""
    
    with open('templates/review.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 检查第795行（索引794）
    if len(lines) > 794:
        line_795 = lines[794]
        print(f"第795行内容: '{line_795.strip()}'")
        print(f"第795行字符: {[ord(c) for c in line_795]}")
        
        # 检查前后几行的上下文
        for i in range(max(0, 794-5), min(len(lines), 794+6)):
            line_num = i + 1
            line_content = lines[i].rstrip('\n')
            print(f"第{line_num}行: '{line_content}'")
            
            # 检查是否有语法问题
            if line_num == 795:
                # 检查是否有多余的分号或其他字符
                if ';' in line_content and 'fn:' in line_content:
                    print(f"发现问题：第{line_num}行包含不应该有的分号")
                    # 修复：移除多余的分号
                    lines[i] = line_content.replace(';', '') + '\n'
                    print(f"修复后: '{lines[i].strip()}'")
    
    # 写回文件
    with open('templates/review.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ 第795行修复完成")

if __name__ == '__main__':
    fix_line_795()