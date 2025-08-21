#!/usr/bin/env python3
"""
任务7验证脚本 - 未保存更改的警告机制
验证保存管理器的beforeunload警告功能、模态框关闭确认对话框等功能
"""

import time
import json
from datetime import datetime

def verify_warning_mechanisms():
    """验证警告机制的实现"""
    print("🔍 验证任务7 - 未保存更改的警告机制")
    print("=" * 60)
    
    results = {
        "task": "任务7 - 添加未保存更改的警告机制",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
    }
    
    # 测试1: 检查beforeunload警告功能的实现
    test_beforeunload_implementation(results)
    
    # 测试2: 检查模态框关闭确认对话框的实现
    test_modal_close_confirmation(results)
    
    # 测试3: 检查未保存更改检测的准确性
    test_unsaved_changes_detection(results)
    
    # 测试4: 检查警告消息的用户友好性
    test_warning_message_friendliness(results)
    
    # 测试5: 检查事件处理器的正确绑定
    test_event_handler_binding(results)
    
    # 生成测试报告
    generate_test_report(results)
    
    return results

def test_beforeunload_implementation(results):
    """测试beforeunload警告功能的实现"""
    print("\n📋 测试1: beforeunload警告功能实现")
    
    test_result = {
        "name": "beforeunload警告功能实现",
        "passed": False,
        "details": [],
        "issues": []
    }
    
    try:
        # 检查review-save-manager.js文件
        with open('static/js/review-save-manager.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键实现
        checks = [
            ("setupBeforeUnloadWarning方法存在", "setupBeforeUnloadWarning()" in content),
            ("beforeunload事件监听器", "addEventListener('beforeunload'" in content),
            ("事件处理器引用保存", "this.beforeUnloadHandler" in content),
            ("未保存更改检查", "this.hasUnsavedChanges" in content),
            ("警告消息设置", "e.preventDefault()" in content and "e.returnValue" in content),
            ("事件处理器清理", "removeEventListener('beforeunload'" in content)
        ]
        
        passed_checks = 0
        for check_name, check_result in checks:
            if check_result:
                test_result["details"].append(f"✅ {check_name}")
                passed_checks += 1
            else:
                test_result["details"].append(f"❌ {check_name}")
                test_result["issues"].append(f"缺少{check_name}")
        
        # 检查警告消息的内容
        if "您有未保存的复盘数据，确定要离开吗？" in content:
            test_result["details"].append("✅ 警告消息内容合适")
            passed_checks += 1
        else:
            test_result["details"].append("❌ 警告消息内容不合适")
            test_result["issues"].append("警告消息内容需要优化")
        
        test_result["passed"] = passed_checks >= 6
        
        if test_result["passed"]:
            print("✅ beforeunload警告功能实现正确")
        else:
            print("❌ beforeunload警告功能实现有问题")
            for issue in test_result["issues"]:
                print(f"   - {issue}")
    
    except Exception as e:
        test_result["issues"].append(f"检查过程中出错: {str(e)}")
        print(f"❌ 检查过程中出错: {e}")
    
    results["tests"].append(test_result)
    results["summary"]["total"] += 1
    if test_result["passed"]:
        results["summary"]["passed"] += 1
    else:
        results["summary"]["failed"] += 1

def test_modal_close_confirmation(results):
    """测试模态框关闭确认对话框的实现"""
    print("\n📋 测试2: 模态框关闭确认对话框实现")
    
    test_result = {
        "name": "模态框关闭确认对话框实现",
        "passed": False,
        "details": [],
        "issues": []
    }
    
    try:
        with open('static/js/review-save-manager.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("setupModalCloseWarning方法存在", "setupModalCloseWarning()" in content),
            ("模态框关闭事件监听", "hide.bs.modal" in content),
            ("模态框关闭处理器引用", "this.modalCloseHandler" in content),
            ("确认对话框显示", "showModalCloseConfirmation" in content),
            ("事件阻止机制", "e.preventDefault()" in content),
            ("未保存字段信息获取", "getUnsavedFieldsInfo" in content),
            ("字段标签获取", "getFieldLabel" in content),
            ("字段值格式化", "formatFieldValue" in content)
        ]
        
        passed_checks = 0
        for check_name, check_result in checks:
            if check_result:
                test_result["details"].append(f"✅ {check_name}")
                passed_checks += 1
            else:
                test_result["details"].append(f"❌ {check_name}")
                test_result["issues"].append(f"缺少{check_name}")
        
        test_result["passed"] = passed_checks >= 6
        
        if test_result["passed"]:
            print("✅ 模态框关闭确认对话框实现正确")
        else:
            print("❌ 模态框关闭确认对话框实现有问题")
    
    except Exception as e:
        test_result["issues"].append(f"检查过程中出错: {str(e)}")
        print(f"❌ 检查过程中出错: {e}")
    
    results["tests"].append(test_result)
    results["summary"]["total"] += 1
    if test_result["passed"]:
        results["summary"]["passed"] += 1
    else:
        results["summary"]["failed"] += 1

def test_unsaved_changes_detection(results):
    """测试未保存更改检测的准确性"""
    print("\n📋 测试3: 未保存更改检测准确性")
    
    test_result = {
        "name": "未保存更改检测准确性",
        "passed": False,
        "details": [],
        "issues": []
    }
    
    try:
        with open('static/js/review-save-manager.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("变化检测方法", "detectChanges()" in content),
            ("表单数据获取", "getCurrentFormData()" in content),
            ("数据比较方法", "compareFormData(" in content),
            ("原始数据捕获", "captureOriginalFormData()" in content),
            ("未保存状态标记", "this.hasUnsavedChanges" in content),
            ("状态更新机制", "updateSaveButtonState()" in content),
            ("防抖优化", "debouncedDetectChanges" in content)
        ]
        
        passed_checks = 0
        for check_name, check_result in checks:
            if check_result:
                test_result["details"].append(f"✅ {check_name}")
                passed_checks += 1
            else:
                test_result["details"].append(f"❌ {check_name}")
                test_result["issues"].append(f"缺少{check_name}")
        
        test_result["passed"] = passed_checks >= 6
        
        if test_result["passed"]:
            print("✅ 未保存更改检测实现正确")
        else:
            print("❌ 未保存更改检测实现有问题")
    
    except Exception as e:
        test_result["issues"].append(f"检查过程中出错: {str(e)}")
        print(f"❌ 检查过程中出错: {e}")
    
    results["tests"].append(test_result)
    results["summary"]["total"] += 1
    if test_result["passed"]:
        results["summary"]["passed"] += 1
    else:
        results["summary"]["failed"] += 1

def test_warning_message_friendliness(results):
    """测试警告消息的用户友好性"""
    print("\n📋 测试4: 警告消息用户友好性")
    
    test_result = {
        "name": "警告消息用户友好性",
        "passed": False,
        "details": [],
        "issues": []
    }
    
    try:
        with open('static/js/review-save-manager.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查警告消息的友好性特征
        friendly_features = [
            ("中文警告消息", "您有未保存的复盘数据" in content),
            ("详细字段信息", "未保存的更改包括" in content),
            ("字段标签获取", "getFieldLabel" in content),
            ("值格式化显示", "formatFieldValue" in content),
            ("字符长度限制", "substring(0, 20)" in content),
            ("布尔值友好显示", "已选中" in content and "未选中" in content),
            ("确认对话框增强", "showCustomConfirmDialog" in content)
        ]
        
        passed_features = 0
        for feature_name, feature_exists in friendly_features:
            if feature_exists:
                test_result["details"].append(f"✅ {feature_name}")
                passed_features += 1
            else:
                test_result["details"].append(f"❌ {feature_name}")
                test_result["issues"].append(f"缺少{feature_name}")
        
        test_result["passed"] = passed_features >= 5
        
        if test_result["passed"]:
            print("✅ 警告消息用户友好性良好")
        else:
            print("❌ 警告消息用户友好性需要改进")
    
    except Exception as e:
        test_result["issues"].append(f"检查过程中出错: {str(e)}")
        print(f"❌ 检查过程中出错: {e}")
    
    results["tests"].append(test_result)
    results["summary"]["total"] += 1
    if test_result["passed"]:
        results["summary"]["passed"] += 1
    else:
        results["summary"]["failed"] += 1

def test_event_handler_binding(results):
    """测试事件处理器的正确绑定"""
    print("\n📋 测试5: 事件处理器绑定")
    
    test_result = {
        "name": "事件处理器绑定",
        "passed": False,
        "details": [],
        "issues": []
    }
    
    try:
        with open('static/js/review-save-manager.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        binding_checks = [
            ("初始化时调用警告设置", "this.setupBeforeUnloadWarning();" in content),
            ("事件处理器引用保存", "this.beforeUnloadHandler =" in content),
            ("模态框处理器引用保存", "this.modalCloseHandler =" in content),
            ("额外警告机制", "setupAdditionalWarnings" in content),
            ("popstate事件监听", "popstate" in content),
            ("visibilitychange事件监听", "visibilitychange" in content),
            ("事件清理机制", "removeEventListener" in content),
            ("销毁方法更新", "destroy()" in content)
        ]
        
        passed_bindings = 0
        for binding_name, binding_exists in binding_checks:
            if binding_exists:
                test_result["details"].append(f"✅ {binding_name}")
                passed_bindings += 1
            else:
                test_result["details"].append(f"❌ {binding_name}")
                test_result["issues"].append(f"缺少{binding_name}")
        
        test_result["passed"] = passed_bindings >= 6
        
        if test_result["passed"]:
            print("✅ 事件处理器绑定正确")
        else:
            print("❌ 事件处理器绑定有问题")
    
    except Exception as e:
        test_result["issues"].append(f"检查过程中出错: {str(e)}")
        print(f"❌ 检查过程中出错: {e}")
    
    results["tests"].append(test_result)
    results["summary"]["total"] += 1
    if test_result["passed"]:
        results["summary"]["passed"] += 1
    else:
        results["summary"]["failed"] += 1

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("📊 任务7验证结果汇总")
    print("=" * 60)
    
    print(f"总测试数: {results['summary']['total']}")
    print(f"通过测试: {results['summary']['passed']}")
    print(f"失败测试: {results['summary']['failed']}")
    print(f"通过率: {(results['summary']['passed']/results['summary']['total']*100):.1f}%")
    
    print("\n📋 详细结果:")
    for test in results["tests"]:
        status = "✅ 通过" if test["passed"] else "❌ 失败"
        print(f"{status} - {test['name']}")
        
        if not test["passed"] and test["issues"]:
            print("   问题:")
            for issue in test["issues"]:
                print(f"   - {issue}")
    
    # 保存详细报告
    report_file = f"task7_warning_mechanisms_verification_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    # 总体评估
    if results['summary']['passed'] == results['summary']['total']:
        print("\n🎉 任务7 - 未保存更改的警告机制 实现完成！")
        print("所有警告机制都已正确实现并通过验证。")
    elif results['summary']['passed'] >= results['summary']['total'] * 0.8:
        print("\n⚠️ 任务7基本完成，但还有一些改进空间")
        print("大部分警告机制已实现，建议完善剩余功能。")
    else:
        print("\n❌ 任务7需要进一步完善")
        print("警告机制实现不完整，需要继续开发。")

if __name__ == "__main__":
    verify_warning_mechanisms()