#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紧急修复语法错误
"""

import os
import re
from datetime import datetime

def fix_syntax_errors():
    """修复语法错误"""
    file_path = "templates/trading_records.html"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 备份文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.syntax_backup_{timestamp}"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已备份文件: {backup_path}")
    
    print("🔧 修复语法错误...")
    
    # 修复第一个语法错误：缺少try块
    error_pattern_1 = r'''        if \(this\._isSaving\) \{
            console\.log\('🛡️ saveTrade方法正在执行中，跳过重复调用'\);
            return;
            \} finally \{
            this\._isSaving = false;
        \}'''
    
    fix_1 = '''        if (this._isSaving) {
            console.log('🛡️ saveTrade方法正在执行中，跳过重复调用');
            return;
        }
        
        this._isSaving = true;
        
        try {
            // 原有的保存逻辑会在这里
            await this.originalSaveTrade();
        } finally {
            this._isSaving = false;
        }'''
    
    # 修复第二个语法错误：缺少try块
    error_pattern_2 = r'''                showMessage\('请检查表单中的错误信息', 'error'\);
                return;
                \} finally \{
            this\._isSaving = false;
        \}'''
    
    fix_2 = '''                showMessage('请检查表单中的错误信息', 'error');
                return;
            }
            
            // 继续执行保存逻辑...
        } finally {
            this._isSaving = false;
        }'''
    
    # 应用修复
    content = re.sub(error_pattern_1, fix_1, content, flags=re.DOTALL)
    content = re.sub(error_pattern_2, fix_2, content, flags=re.DOTALL)
    
    # 检查是否还有其他语法问题
    # 查找孤立的finally块
    orphan_finally_pattern = r'(\s+)\} finally \{'
    
    def fix_orphan_finally(match):
        indent = match.group(1)
        return f'{indent}}} catch (error) {{\n{indent}    console.error("Unexpected error:", error);\n{indent}}} finally {{'
    
    content = re.sub(orphan_finally_pattern, fix_orphan_finally, content)
    
    # 查找并修复不完整的try-catch-finally结构
    incomplete_try_pattern = r'(\s+)try \{\s*\} finally \{'
    
    def fix_incomplete_try(match):
        indent = match.group(1)
        return f'{indent}try {{\n{indent}    // 执行逻辑\n{indent}}} finally {{'
    
    content = re.sub(incomplete_try_pattern, fix_incomplete_try, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 语法错误修复完成")
    return True

def main():
    """主函数"""
    print("🚨 紧急修复语法错误")
    print("=" * 40)
    
    try:
        if fix_syntax_errors():
            print("\n🎉 语法错误修复完成！")
            print("请刷新页面重新测试")
        else:
            print("❌ 修复失败")
            
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()