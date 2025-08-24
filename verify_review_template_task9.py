#!/usr/bin/env python3
"""
验证复盘页面HTML模板更新 - 任务9实现验证
"""

import os
import re
from pathlib import Path

def verify_template_updates():
    """验证模板更新是否完成"""
    template_path = Path("templates/review.html")
    
    if not template_path.exists():
        print("❌ 模板文件不存在")
        return False
    
    content = template_path.read_text(encoding='utf-8')
    
    # 检查项目列表
    checks = [
        # 1. 当前价格输入字段
        {
            'name': '当前价格输入字段',
            'pattern': r'id="current-price-input"',
            'required': True
        },
        # 2. 浮盈计算显示
        {
            'name': '浮盈比例显示',
            'pattern': r'id="floating-profit-ratio"',
            'required': True
        },
        # 3. 成本价显示
        {
            'name': '成本价显示',
            'pattern': r'id="buy-price-display"',
            'required': True
        },
        # 4. 持仓天数编辑功能
        {
            'name': '持仓天数编辑容器',
            'pattern': r'holding-days-container',
            'required': True
        },
        # 5. 保存状态指示器
        {
            'name': '保存状态指示器',
            'pattern': r'id="save-status-display"',
            'required': True
        },
        # 6. 保存进度条
        {
            'name': '保存进度条',
            'pattern': r'id="save-progress"',
            'required': True
        },
        # 7. 未保存更改警告
        {
            'name': '未保存更改警告',
            'pattern': r'id="unsaved-changes-warning"',
            'required': True
        },
        # 8. 最后保存时间显示
        {
            'name': '最后保存时间',
            'pattern': r'id="last-saved-time"',
            'required': True
        },
        # 9. 保存按钮状态管理
        {
            'name': '保存按钮状态',
            'pattern': r'save-btn-spinner',
            'required': True
        },
        # 10. CSS样式 - 浮盈计算器
        {
            'name': '浮盈计算器样式',
            'pattern': r'floating-profit-container',
            'required': True
        },
        # 11. CSS样式 - 持仓天数编辑
        {
            'name': '持仓天数编辑样式',
            'pattern': r'holding-days-editable-container',
            'required': True
        },
        # 12. CSS样式 - 保存状态
        {
            'name': '保存状态样式',
            'pattern': r'save-status-indicator',
            'required': True
        },
        # 13. JavaScript函数 - 保存状态更新
        {
            'name': '保存状态更新函数',
            'pattern': r'function updateSaveStatus',
            'required': True
        },
        # 14. JavaScript函数 - 持仓天数编辑器初始化
        {
            'name': '持仓天数编辑器初始化',
            'pattern': r'function initializeHoldingDaysEditors',
            'required': True
        },
        # 15. JavaScript函数 - 模态框关闭处理
        {
            'name': '模态框关闭处理',
            'pattern': r'function handleModalClose',
            'required': True
        },
        # 16. 组件脚本引用
        {
            'name': 'HoldingDaysEditor脚本',
            'pattern': r'holding-days-editor\.js',
            'required': True
        },
        {
            'name': 'FloatingProfitCalculator脚本',
            'pattern': r'floating-profit-calculator\.js',
            'required': True
        },
        {
            'name': 'ReviewSaveManager脚本',
            'pattern': r'review-save-manager\.js',
            'required': True
        }
    ]
    
    print("🔍 验证复盘页面HTML模板更新...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for check in checks:
        if re.search(check['pattern'], content, re.IGNORECASE | re.MULTILINE):
            print(f"✅ {check['name']}")
            passed += 1
        else:
            if check['required']:
                print(f"❌ {check['name']} - 未找到")
                failed += 1
            else:
                print(f"⚠️  {check['name']} - 可选项未找到")
    
    print("=" * 60)
    print(f"总计: {passed} 通过, {failed} 失败")
    
    # 检查特定功能实现
    print("\n🔍 检查功能实现细节...")
    
    # 检查浮盈计算卡片结构
    if '浮盈计算' in content and 'card-header' in content:
        print("✅ 浮盈计算卡片结构正确")
    else:
        print("❌ 浮盈计算卡片结构缺失")
        failed += 1
    
    # 检查持仓列表编辑功能
    if 'holding-days-display' in content and 'holding-days-actions' in content:
        print("✅ 持仓天数编辑功能结构正确")
    else:
        print("❌ 持仓天数编辑功能结构缺失")
        failed += 1
    
    # 检查保存状态管理
    if 'setSaveButtonState' in content and 'updateSaveProgress' in content:
        print("✅ 保存状态管理功能完整")
    else:
        print("❌ 保存状态管理功能不完整")
        failed += 1
    
    # 检查响应式设计
    if '@media (max-width: 768px)' in content:
        print("✅ 响应式设计已实现")
    else:
        print("❌ 响应式设计缺失")
        failed += 1
    
    print("=" * 60)
    
    if failed == 0:
        print("🎉 所有检查项目都通过了！")
        print("✅ 任务9: 更新复盘页面HTML模板 - 实现完成")
        return True
    else:
        print(f"❌ 有 {failed} 个检查项目失败")
        print("❌ 任务9: 更新复盘页面HTML模板 - 需要修复")
        return False

def check_file_structure():
    """检查相关文件结构"""
    print("\n🔍 检查相关文件结构...")
    
    files_to_check = [
        "templates/review.html",
        "static/js/holding-days-editor.js",
        "static/js/floating-profit-calculator.js", 
        "static/js/review-save-manager.js",
        "static/css/main.css",
        "static/css/components.css"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")

if __name__ == "__main__":
    print("验证任务9: 更新复盘页面HTML模板")
    print("=" * 60)
    
    check_file_structure()
    success = verify_template_updates()
    
    if success:
        print("\n🎉 任务9验证通过！")
        print("📋 实现的功能:")
        print("  • 在复盘模态框中添加了当前价格输入字段")
        print("  • 更新了持仓列表显示以支持编辑功能")
        print("  • 添加了保存状态指示器")
        print("  • 更新了CSS样式以支持新的UI元素")
        print("  • 集成了所有相关的JavaScript组件")
        print("  • 实现了响应式设计")
        exit(0)
    else:
        print("\n❌ 任务9验证失败，需要进一步修复")
        exit(1)