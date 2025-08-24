#!/usr/bin/env python3
"""
紧急修复 app.logger 错误
"""

import os
import re

def fix_app_logger_error():
    """修复 app.logger 未定义的错误"""
    
    file_path = 'api/trading_routes.py'
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经导入了 current_app
    if 'from flask import request, jsonify, current_app' not in content:
        print("❌ current_app 导入失败")
        return False
    
    # 检查是否还有 app.logger
    if 'app.logger' in content:
        print("❌ 仍然存在 app.logger 引用")
        # 替换所有 app.logger 为 current_app.logger
        content = content.replace('app.logger', 'current_app.logger')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 已修复所有 app.logger 引用")
    else:
        print("✅ 没有发现 app.logger 引用")
    
    return True

def verify_fix():
    """验证修复是否正确"""
    
    file_path = 'api/trading_routes.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查导入
    has_current_app = 'current_app' in content and 'from flask import' in content
    
    # 检查是否还有错误的引用
    has_app_logger = 'app.logger' in content
    has_current_app_logger = 'current_app.logger' in content
    
    print("\n🔍 验证结果:")
    print(f"✅ 导入 current_app: {'是' if has_current_app else '否'}")
    print(f"❌ 存在 app.logger: {'是' if has_app_logger else '否'}")
    print(f"✅ 使用 current_app.logger: {'是' if has_current_app_logger else '否'}")
    
    if has_current_app and not has_app_logger and has_current_app_logger:
        print("\n🎉 修复成功！")
        return True
    else:
        print("\n⚠️ 修复可能不完整")
        return False

def main():
    print("🚨 紧急修复 app.logger 错误...")
    
    if fix_app_logger_error():
        if verify_fix():
            print("\n✅ 修复完成，请重启服务器测试")
        else:
            print("\n❌ 修复验证失败")
    else:
        print("\n❌ 修复失败")

if __name__ == "__main__":
    main()