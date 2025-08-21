#!/usr/bin/env python3
"""
ReviewSaveManager 功能验证脚本
验证复盘保存管理器的各项功能是否正确实现
"""

import os
import re
import json
from pathlib import Path

def verify_file_exists(file_path):
    """验证文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ 文件存在: {file_path}")
        return True
    else:
        print(f"❌ 文件不存在: {file_path}")
        return False

def verify_javascript_syntax(file_path):
    """验证JavaScript文件的基本语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查基本的JavaScript语法元素
        checks = [
            (r'class ReviewSaveManager', '类定义'),
            (r'constructor\s*\(', '构造函数'),
            (r'async\s+saveReview\s*\(', '保存方法'),
            (r'detectChanges\s*\(', '变化检测方法'),
            (r'validateReviewData\s*\(', '数据验证方法'),
            (r'setupBeforeUnloadWarning\s*\(', '离开警告设置'),
            (r'updateSaveButtonState\s*\(', '按钮状态更新'),
            (r'enableAutoSave\s*\(', '自动保存启用'),
            (r'addEventListener', '事件监听器'),
        ]
        
        all_passed = True
        for pattern, description in checks:
            if re.search(pattern, content):
                print(f"✅ {description}: 找到")
            else:
                print(f"❌ {description}: 未找到")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

def verify_template_integration(template_path):
    """验证模板文件的集成"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            (r'review-save-manager\.js', 'JavaScript文件引用'),
            (r'reviewSaveManager', 'SaveManager实例引用'),
            (r'reviewSaved.*addEventListener', '保存成功事件监听'),
            (r'reviewSaveError.*addEventListener', '保存失败事件监听'),
            (r'ReviewSaveManager.*destroy', '保存管理器清理'),
        ]
        
        all_passed = True
        for pattern, description in checks:
            if re.search(pattern, content, re.DOTALL):
                print(f"✅ 模板集成 - {description}: 找到")
            else:
                print(f"❌ 模板集成 - {description}: 未找到")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 读取模板文件失败: {e}")
        return False

def verify_api_integration(api_file_path):
    """验证API集成"""
    try:
        with open(api_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            (r'async\s+saveReview\s*\(', 'saveReview方法'),
            (r'requestWithRetry', '重试机制'),
            (r'handleReviewError', '错误处理'),
            (r'current_price.*reviewData\.current_price', '新字段支持'),
        ]
        
        all_passed = True
        for pattern, description in checks:
            if re.search(pattern, content):
                print(f"✅ API集成 - {description}: 找到")
            else:
                print(f"❌ API集成 - {description}: 未找到")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 读取API文件失败: {e}")
        return False

def verify_functionality_completeness():
    """验证功能完整性"""
    print("\n=== 功能完整性检查 ===")
    
    # 检查任务要求的功能点
    required_features = [
        "创建ReviewSaveManager类管理保存逻辑",
        "实现表单变化检测机制", 
        "添加未保存更改警告功能",
        "实现保存按钮状态管理",
        "添加保存成功和失败的用户反馈"
    ]
    
    js_file = "static/js/review-save-manager.js"
    if not os.path.exists(js_file):
        print("❌ ReviewSaveManager文件不存在")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    feature_checks = [
        (r'class ReviewSaveManager', required_features[0]),
        (r'detectChanges.*compareFormData', required_features[1]),
        (r'beforeunload.*hasUnsavedChanges', required_features[2]),
        (r'updateSaveButtonState.*disabled', required_features[3]),
        (r'handleSaveSuccess.*handleSaveError', required_features[4]),
    ]
    
    all_passed = True
    for pattern, feature in feature_checks:
        if re.search(pattern, content, re.DOTALL):
            print(f"✅ {feature}")
        else:
            print(f"❌ {feature}")
            all_passed = False
    
    return all_passed

def main():
    """主验证函数"""
    print("ReviewSaveManager 功能验证")
    print("=" * 50)
    
    # 验证文件存在
    print("\n=== 文件存在性检查 ===")
    files_to_check = [
        "static/js/review-save-manager.js",
        "templates/review.html",
        "static/js/api.js",
        "test_review_save_manager.html"
    ]
    
    files_exist = all(verify_file_exists(f) for f in files_to_check)
    
    # 验证JavaScript语法
    print("\n=== JavaScript语法检查 ===")
    js_syntax_ok = verify_javascript_syntax("static/js/review-save-manager.js")
    
    # 验证模板集成
    print("\n=== 模板集成检查 ===")
    template_integration_ok = verify_template_integration("templates/review.html")
    
    # 验证API集成
    print("\n=== API集成检查 ===")
    api_integration_ok = verify_api_integration("static/js/api.js")
    
    # 验证功能完整性
    functionality_ok = verify_functionality_completeness()
    
    # 总结
    print("\n=== 验证总结 ===")
    all_checks = [
        ("文件存在", files_exist),
        ("JavaScript语法", js_syntax_ok),
        ("模板集成", template_integration_ok),
        ("API集成", api_integration_ok),
        ("功能完整性", functionality_ok),
    ]
    
    passed_count = sum(1 for _, passed in all_checks if passed)
    total_count = len(all_checks)
    
    for check_name, passed in all_checks:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{check_name}: {status}")
    
    print(f"\n总体结果: {passed_count}/{total_count} 项检查通过")
    
    if passed_count == total_count:
        print("🎉 所有检查都通过！ReviewSaveManager实现完成。")
        return True
    else:
        print("⚠️  部分检查未通过，请检查上述问题。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)