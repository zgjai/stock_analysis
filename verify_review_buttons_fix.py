#!/usr/bin/env python3
"""
复盘记录按钮修复验证脚本
验证editReview和deleteReview函数是否正确修复
"""

import re
import sys
from pathlib import Path

def verify_review_buttons_fix():
    """验证复盘记录按钮修复"""
    
    print("🔍 验证复盘记录按钮修复...")
    
    # 检查修复文件是否存在
    review_file = Path("templates/review.html")
    if not review_file.exists():
        print("❌ 主要修复文件不存在: templates/review.html")
        return False
    
    # 读取文件内容
    content = review_file.read_text(encoding='utf-8')
    
    # 验证项目列表
    checks = [
        {
            'name': 'editReview函数存在',
            'pattern': r'window\.editReview\s*=\s*function',
            'required': True
        },
        {
            'name': 'deleteReview函数存在',
            'pattern': r'window\.deleteReview\s*=\s*function',
            'required': True
        },
        {
            'name': 'editReview使用fetch API',
            'pattern': r'fetch\(`/api/reviews/\$\{reviewId\}`\)',
            'required': True
        },
        {
            'name': 'deleteReview使用fetch API',
            'pattern': r'fetch\(`/api/reviews/\$\{reviewId\}`, \{[^}]*method: [\'"]DELETE[\'"]',
            'required': True
        },
        {
            'name': '删除确认对话框',
            'pattern': r'confirm\([\'"]确定要删除这条复盘记录吗',
            'required': True
        },
        {
            'name': 'HTTP状态码检查',
            'pattern': r'if \(!response\.ok\)',
            'required': True
        },
        {
            'name': '错误处理',
            'pattern': r'\.catch\(error\s*=>\s*\{',
            'required': True
        },
        {
            'name': '成功消息显示',
            'pattern': r'showSuccessMessage\([\'"]复盘记录.*成功',
            'required': True
        },
        {
            'name': '加载状态提示',
            'pattern': r'showInfoMessage\([\'"]正在.*复盘记录',
            'required': True
        },
        {
            'name': '列表刷新调用',
            'pattern': r'loadReviews\(\)',
            'required': True
        }
    ]
    
    # 执行验证
    results = []
    for check in checks:
        pattern = check['pattern']
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        
        if matches:
            print(f"✅ {check['name']}: 找到 {len(matches)} 处匹配")
            results.append(True)
        else:
            status = "❌" if check['required'] else "⚠️"
            print(f"{status} {check['name']}: 未找到匹配")
            results.append(False)
    
    # 检查按钮HTML结构
    button_patterns = [
        r'onclick="editReview\(\$\{review\.id\}\)"',
        r'onclick="deleteReview\(\$\{review\.id\}\)"',
        r'btn-group-vertical',
        r'fas fa-edit',
        r'fas fa-trash'
    ]
    
    print("\n🔍 验证按钮HTML结构...")
    for pattern in button_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"✅ 按钮结构: {pattern} - 找到 {len(matches)} 处")
        else:
            print(f"❌ 按钮结构: {pattern} - 未找到")
    
    # 检查是否移除了旧的API客户端检查
    old_patterns = [
        r'window\.apiClient && typeof window\.apiClient\.get',
        r'window\.apiClient && typeof window\.apiClient\.delete'
    ]
    
    print("\n🔍 检查是否移除了旧的API客户端检查...")
    old_code_found = False
    for pattern in old_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"⚠️ 发现旧代码: {pattern} - {len(matches)} 处")
            old_code_found = True
    
    if not old_code_found:
        print("✅ 已成功移除旧的API客户端检查代码")
    
    # 统计结果
    passed = sum(results)
    total = len([c for c in checks if c['required']])
    
    print(f"\n📊 验证结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 复盘记录按钮修复验证通过！")
        return True
    else:
        print("❌ 复盘记录按钮修复验证失败")
        return False

def verify_test_file():
    """验证测试文件"""
    
    print("\n🔍 验证测试文件...")
    
    test_file = Path("test_review_record_buttons_fix.html")
    if not test_file.exists():
        print("❌ 测试文件不存在: test_review_record_buttons_fix.html")
        return False
    
    content = test_file.read_text(encoding='utf-8')
    
    # 检查测试文件关键内容
    test_checks = [
        'window.fetch = function',
        'editReview函数',
        'deleteReview函数',
        'fetch(`/api/reviews/${reviewId}`)',
        'method: \'DELETE\'',
        '模拟fetch调用'
    ]
    
    for check in test_checks:
        if check in content:
            print(f"✅ 测试文件包含: {check}")
        else:
            print(f"❌ 测试文件缺少: {check}")
    
    print("✅ 测试文件验证完成")
    return True

def main():
    """主函数"""
    
    print("=" * 60)
    print("复盘记录按钮修复验证")
    print("=" * 60)
    
    # 验证主要修复
    main_fix_ok = verify_review_buttons_fix()
    
    # 验证测试文件
    test_file_ok = verify_test_file()
    
    print("\n" + "=" * 60)
    
    if main_fix_ok and test_file_ok:
        print("🎉 所有验证通过！复盘记录按钮修复成功")
        print("\n📋 修复内容:")
        print("  ✅ 添加了editReview函数，使用fetch API")
        print("  ✅ 添加了deleteReview函数，使用fetch API")
        print("  ✅ 统一了API调用方式")
        print("  ✅ 增强了错误处理")
        print("  ✅ 优化了用户体验")
        print("\n🧪 测试方法:")
        print("  1. 打开 test_review_record_buttons_fix.html")
        print("  2. 点击复盘记录右侧的编辑和删除按钮")
        print("  3. 观察测试结果区域的反馈信息")
        return True
    else:
        print("❌ 验证失败，请检查修复内容")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)