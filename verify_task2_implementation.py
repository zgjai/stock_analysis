#!/usr/bin/env python3
"""
验证任务2的实现：初始化API客户端和保存管理器
"""

import re
import os

def verify_task2_implementation():
    """验证任务2的实现"""
    print("🔍 验证任务2实现：初始化API客户端和保存管理器")
    print("=" * 60)
    
    results = {
        "全局变量声明": False,
        "依赖检查函数": False,
        "API客户端初始化": False,
        "保存管理器初始化": False,
        "错误处理函数": False,
        "页面初始化函数": False,
        "saveReview函数重写": False,
        "调试函数": False
    }
    
    # 检查review.html文件
    review_html_path = "templates/review.html"
    if not os.path.exists(review_html_path):
        print("❌ review.html文件不存在")
        return False
    
    with open(review_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查全局变量声明
    if "let apiClient = null;" in content and "let reviewSaveManager = null;" in content:
        results["全局变量声明"] = True
        print("✅ 全局变量声明正确")
    else:
        print("❌ 缺少全局变量声明")
    
    # 检查依赖检查函数
    if "function checkDependencies()" in content:
        results["依赖检查函数"] = True
        print("✅ 依赖检查函数存在")
    else:
        print("❌ 缺少依赖检查函数")
    
    # 检查API客户端初始化函数
    if "function initializeApiClient()" in content and "apiClient = new ApiClient();" in content:
        results["API客户端初始化"] = True
        print("✅ API客户端初始化函数正确")
    else:
        print("❌ API客户端初始化函数有问题")
    
    # 检查保存管理器初始化函数
    if "function initializeReviewSaveManager()" in content and "reviewSaveManager = new ReviewSaveManager" in content:
        results["保存管理器初始化"] = True
        print("✅ 保存管理器初始化函数正确")
    else:
        print("❌ 保存管理器初始化函数有问题")
    
    # 检查错误处理函数
    if "function showErrorMessage(" in content and "function showSuccessMessage(" in content:
        results["错误处理函数"] = True
        print("✅ 错误处理函数存在")
    else:
        print("❌ 缺少错误处理函数")
    
    # 检查页面初始化函数
    if "async function initializeReviewPage()" in content:
        results["页面初始化函数"] = True
        print("✅ 页面初始化函数存在")
    else:
        print("❌ 缺少页面初始化函数")
    
    # 检查saveReview函数重写
    if "reviewSaveManager.saveReview();" in content and "保存功能未正确初始化" in content:
        results["saveReview函数重写"] = True
        print("✅ saveReview函数已正确重写")
    else:
        print("❌ saveReview函数重写有问题")
    
    # 检查调试函数
    if "function testInitialization()" in content and "function diagnoseReviewPage()" in content:
        results["调试函数"] = True
        print("✅ 调试函数存在")
    else:
        print("❌ 缺少调试函数")
    
    # 检查JavaScript文件是否存在
    js_files = [
        "static/js/api.js",
        "static/js/review-save-manager.js"
    ]
    
    js_files_exist = True
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"✅ {js_file} 存在")
        else:
            print(f"❌ {js_file} 不存在")
            js_files_exist = False
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 实现验证结果:")
    
    passed = 0
    total = len(results)
    
    for item, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {item}")
        if status:
            passed += 1
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total and js_files_exist:
        print("🎉 任务2实现验证通过！")
        return True
    else:
        print("⚠️ 任务2实现需要改进")
        return False

def check_task_requirements():
    """检查任务要求是否满足"""
    print("\n🎯 检查任务要求:")
    print("-" * 40)
    
    requirements = [
        "创建全局apiClient实例的初始化代码",
        "创建全局reviewSaveManager实例的初始化代码", 
        "实现依赖检查函数，确保所有必要的类都已加载",
        "添加初始化失败的错误处理和用户提示"
    ]
    
    review_html_path = "templates/review.html"
    with open(review_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        "apiClient = new ApiClient()" in content,
        "reviewSaveManager = new ReviewSaveManager" in content,
        "function checkDependencies()" in content and "typeof ApiClient !== 'undefined'" in content,
        "showErrorMessage(" in content and "初始化失败" in content
    ]
    
    for i, (req, check) in enumerate(zip(requirements, checks), 1):
        status = "✅" if check else "❌"
        print(f"{status} {i}. {req}")
    
    all_passed = all(checks)
    print(f"\n需求满足度: {sum(checks)}/{len(checks)} ({sum(checks)/len(checks)*100:.1f}%)")
    
    return all_passed

if __name__ == "__main__":
    implementation_ok = verify_task2_implementation()
    requirements_ok = check_task_requirements()
    
    if implementation_ok and requirements_ok:
        print("\n🎊 任务2完成度: 100%")
        print("所有子任务都已正确实现！")
    else:
        print("\n⚠️ 任务2需要进一步完善")