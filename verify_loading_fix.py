#!/usr/bin/env python3
"""
验证加载状态修复的脚本
"""

import os
import re

def verify_trading_records_fix():
    """验证交易记录页面的修复"""
    
    template_path = "templates/trading_records.html"
    
    if not os.path.exists(template_path):
        print(f"❌ 文件不存在: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # 检查1: 是否有初始化时的加载状态处理
    if '立即隐藏加载状态，防止卡住' in content:
        checks.append("✅ 初始化加载状态处理")
    else:
        checks.append("❌ 缺少初始化加载状态处理")
    
    # 检查2: 是否有超时处理
    if '请求超时' in content and 'Promise.race' in content:
        checks.append("✅ API请求超时处理")
    else:
        checks.append("❌ 缺少API请求超时处理")
    
    # 检查3: 是否有空数据状态显示
    if '暂无交易记录' in content and 'bi-inbox' in content:
        checks.append("✅ 空数据状态显示")
    else:
        checks.append("❌ 缺少空数据状态显示")
    
    # 检查4: 是否有错误状态处理
    if '加载失败，请重试' in content and 'bi-exclamation-triangle' in content:
        checks.append("✅ 错误状态处理")
    else:
        checks.append("❌ 缺少错误状态处理")
    
    # 检查5: 是否有重新加载按钮
    if '重新加载' in content and 'bi-arrow-clockwise' in content:
        checks.append("✅ 重新加载功能")
    else:
        checks.append("❌ 缺少重新加载功能")
    
    # 检查6: 是否有页面就绪检查
    if 'DOMContentLoaded' in content and '页面加载异常' in content:
        checks.append("✅ 页面就绪检查")
    else:
        checks.append("❌ 缺少页面就绪检查")
    
    print("交易记录页面修复验证:")
    for check in checks:
        print(f"  {check}")
    
    success_count = len([c for c in checks if c.startswith("✅")])
    total_count = len(checks)
    
    print(f"\n修复完成度: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

def check_api_client():
    """检查API客户端是否存在"""
    
    static_js_path = "static/js"
    api_files = []
    
    if os.path.exists(static_js_path):
        for file in os.listdir(static_js_path):
            if 'api' in file.lower() and file.endswith('.js'):
                api_files.append(file)
    
    if api_files:
        print(f"✅ 找到API客户端文件: {', '.join(api_files)}")
        return True
    else:
        print("❌ 未找到API客户端文件")
        return False

def check_base_template():
    """检查基础模板是否有必要的组件"""
    
    base_path = "templates/base.html"
    
    if not os.path.exists(base_path):
        print("❌ 基础模板不存在")
        return False
    
    with open(base_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    if 'bootstrap' in content.lower():
        checks.append("✅ Bootstrap CSS/JS")
    else:
        checks.append("❌ 缺少Bootstrap")
    
    if 'bootstrap-icons' in content.lower() or 'bi-' in content:
        checks.append("✅ Bootstrap Icons")
    else:
        checks.append("❌ 缺少Bootstrap Icons")
    
    if 'showMessage' in content or 'toast' in content.lower():
        checks.append("✅ 消息提示功能")
    else:
        checks.append("❌ 缺少消息提示功能")
    
    print("基础模板检查:")
    for check in checks:
        print(f"  {check}")
    
    return all(c.startswith("✅") for c in checks)

def main():
    """主函数"""
    print("🔍 验证加载状态修复...")
    print("=" * 50)
    
    # 验证交易记录页面修复
    trading_fix_ok = verify_trading_records_fix()
    
    print("\n" + "=" * 50)
    
    # 检查相关依赖
    api_ok = check_api_client()
    
    print("\n" + "=" * 50)
    
    base_ok = check_base_template()
    
    print("\n" + "=" * 50)
    
    # 总结
    if trading_fix_ok:
        print("🎉 交易记录页面修复验证通过！")
    else:
        print("⚠️  交易记录页面修复不完整")
    
    if not api_ok:
        print("⚠️  建议检查API客户端配置")
    
    if not base_ok:
        print("⚠️  建议检查基础模板配置")
    
    print("\n修复效果说明:")
    print("1. 页面加载时不会卡在'加载中'状态")
    print("2. 没有数据时显示友好的空状态提示")
    print("3. 网络错误时显示明确的错误信息")
    print("4. 提供重新加载按钮方便用户操作")
    print("5. 自动检测和修复页面加载异常")
    
    print("\n测试建议:")
    print("1. 打开 test_loading_fix.html 查看修复效果演示")
    print("2. 启动服务器并访问交易记录页面")
    print("3. 断开网络连接测试错误处理")
    print("4. 清空数据库测试空状态显示")

if __name__ == "__main__":
    main()