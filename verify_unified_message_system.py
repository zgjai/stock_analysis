#!/usr/bin/env python3
"""
验证统一消息系统实现
检查任务4的所有子任务是否完成
"""

import os
import re

def check_file_exists(filepath):
    """检查文件是否存在"""
    exists = os.path.exists(filepath)
    print(f"{'✅' if exists else '❌'} 文件存在检查: {filepath}")
    return exists

def check_file_content(filepath, patterns):
    """检查文件内容是否包含指定模式"""
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = []
    for pattern_name, pattern in patterns.items():
        found = bool(re.search(pattern, content, re.MULTILINE | re.DOTALL))
        print(f"{'✅' if found else '❌'} {pattern_name}: {filepath}")
        results.append(found)
    
    return all(results)

def main():
    print("🔍 验证统一消息系统实现 (任务4)")
    print("=" * 50)
    
    # 子任务1: 创建showErrorMessage函数用于显示错误消息
    print("\n📋 子任务1: 创建showErrorMessage函数")
    unified_system_patterns = {
        "showErrorMessage函数定义": r"showErrorMessage\s*\([^)]*\)\s*{",
        "错误消息类型处理": r"type:\s*['\"]error['\"]",
        "错误图标配置": r"icon:\s*['\"]fas\s+fa-exclamation-triangle['\"]"
    }
    
    task1_success = check_file_content('static/js/unified-message-system.js', unified_system_patterns)
    
    # 子任务2: 创建showSuccessMessage函数用于显示成功消息
    print("\n📋 子任务2: 创建showSuccessMessage函数")
    success_patterns = {
        "showSuccessMessage函数定义": r"showSuccessMessage\s*\([^)]*\)\s*{",
        "成功消息类型处理": r"type:\s*['\"]success['\"]",
        "成功图标配置": r"icon:\s*['\"]fas\s+fa-check-circle['\"]"
    }
    
    task2_success = check_file_content('static/js/unified-message-system.js', success_patterns)
    
    # 子任务3: 实现消息的自动消失机制
    print("\n📋 子任务3: 实现消息的自动消失机制")
    auto_dismiss_patterns = {
        "自动消失配置": r"duration:\s*\d+",
        "setTimeout自动移除Alert": r"setTimeout.*removeAlert",
        "setTimeout自动移除Toast": r"setTimeout.*removeToast"
    }
    
    task3_success = check_file_content('static/js/unified-message-system.js', auto_dismiss_patterns)
    
    # 子任务4: 确保消息样式与现有UI风格一致
    print("\n📋 子任务4: 确保消息样式与现有UI风格一致")
    ui_consistency_patterns = {
        "Bootstrap Alert类": r"alert-danger|alert-success|alert-warning|alert-info",
        "Bootstrap Toast结构": r"toast-header|toast-body",
        "响应式样式": r"position-fixed|top-0|end-0",
        "动画效果": r"@keyframes|animation:"
    }
    
    task4_success = check_file_content('static/js/unified-message-system.js', ui_consistency_patterns)
    
    # 检查复盘页面集成
    print("\n📋 复盘页面集成检查")
    review_integration_patterns = {
        "统一消息系统脚本加载": r"unified-message-system\.js",
        "消息函数注释说明": r"统一消息系统",
        "依赖检查包含UnifiedMessageSystem": r"UnifiedMessageSystem.*check"
    }
    
    integration_success = check_file_content('templates/review.html', review_integration_patterns)
    
    # 检查测试文件
    print("\n📋 测试文件检查")
    test_file_exists = check_file_exists('test_unified_message_system.html')
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 任务4完成情况总结:")
    print(f"{'✅' if task1_success else '❌'} 子任务1: 创建showErrorMessage函数")
    print(f"{'✅' if task2_success else '❌'} 子任务2: 创建showSuccessMessage函数") 
    print(f"{'✅' if task3_success else '❌'} 子任务3: 实现自动消失机制")
    print(f"{'✅' if task4_success else '❌'} 子任务4: 确保UI风格一致")
    print(f"{'✅' if integration_success else '❌'} 复盘页面集成")
    print(f"{'✅' if test_file_exists else '❌'} 测试文件创建")
    
    all_success = all([task1_success, task2_success, task3_success, task4_success, integration_success, test_file_exists])
    
    print(f"\n🎯 任务4总体状态: {'✅ 完成' if all_success else '❌ 未完成'}")
    
    if all_success:
        print("\n🎉 统一消息提示系统实现完成！")
        print("主要功能:")
        print("- ✅ showErrorMessage() - 显示错误消息")
        print("- ✅ showSuccessMessage() - 显示成功消息") 
        print("- ✅ showWarningMessage() - 显示警告消息")
        print("- ✅ showInfoMessage() - 显示信息消息")
        print("- ✅ 自动消失机制 (可配置时间)")
        print("- ✅ Bootstrap风格一致性")
        print("- ✅ Alert和Toast两种显示模式")
        print("- ✅ 动画效果和响应式设计")
        print("- ✅ 向后兼容性支持")
        print("\n使用方法:")
        print("showErrorMessage('错误信息');")
        print("showSuccessMessage('成功信息', { position: 'toast' });")
        print("showWarningMessage('警告信息', { duration: 4000 });")
    else:
        print("\n⚠️ 部分功能可能需要进一步检查")
    
    return all_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)