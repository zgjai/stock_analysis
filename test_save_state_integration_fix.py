#!/usr/bin/env python3
"""
测试保存状态管理集成修复
"""
import requests
import time

def test_review_page_initialization():
    """测试复盘页面初始化"""
    print("🔍 测试复盘页面初始化...")
    
    try:
        response = requests.get("http://localhost:5001/review", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # 检查关键元素
            checks = [
                ("复盘表单", 'id="review-form"' in content),
                ("保存按钮", 'id="save-review-btn"' in content),
                ("模态框", 'id="reviewModal"' in content),
                ("保存管理器脚本", 'review-save-manager.js' in content),
                ("初始化函数", 'integrateReviewSaveStateManagement' in content),
                ("函数重复检查", content.count('function integrateReviewSaveStateManagement') == 1),
            ]
            
            passed = 0
            for check_name, result in checks:
                if result:
                    print(f"   ✅ {check_name}")
                    passed += 1
                else:
                    print(f"   ❌ {check_name}")
            
            print(f"   📊 页面检查: {passed}/{len(checks)} 通过")
            return passed >= len(checks) - 1  # 允许一个检查失败
            
        else:
            print(f"❌ 复盘页面加载失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        return False

def test_javascript_functions():
    """测试JavaScript函数定义"""
    print("\n🔍 测试JavaScript函数定义...")
    
    try:
        response = requests.get("http://localhost:5001/review", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # 检查函数重复定义
            function_counts = {
                'integrateReviewSaveStateManagement': content.count('function integrateReviewSaveStateManagement'),
                'verifySaveStateManagementIntegration': content.count('function verifySaveStateManagementIntegration'),
                'saveReview': content.count('function saveReview'),
                'testInitialization': content.count('function testInitialization'),
                'diagnoseReviewPage': content.count('function diagnoseReviewPage'),
            }
            
            issues = []
            for func_name, count in function_counts.items():
                if count > 1:
                    issues.append(f"{func_name} 定义了 {count} 次")
                    print(f"   ❌ {func_name}: {count} 次定义")
                elif count == 1:
                    print(f"   ✅ {func_name}: 1 次定义")
                else:
                    print(f"   ⚠️  {func_name}: 0 次定义")
            
            if issues:
                print(f"\n❌ 发现函数重复定义问题:")
                for issue in issues:
                    print(f"   - {issue}")
                return False
            else:
                print(f"\n✅ 没有发现函数重复定义问题")
                return True
                
        else:
            print(f"❌ 页面加载失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        return False

def create_fix_summary():
    """创建修复总结"""
    print("\n📝 创建修复总结...")
    
    summary = {
        "fix_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "issue": "保存状态管理集成失败",
        "root_cause": "函数重复定义导致后定义的函数覆盖前面的函数",
        "fixes_applied": [
            "删除重复的 integrateReviewSaveStateManagement 函数定义",
            "增强第一个函数的错误处理和验证逻辑",
            "使用 window.reviewSaveManager 确保全局访问",
            "添加更详细的日志输出便于调试",
            "改进按钮和表单绑定验证"
        ],
        "expected_result": "保存状态管理集成步骤应该成功返回 true",
        "test_status": "待验证"
    }
    
    import json
    with open("save_state_integration_fix_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("✅ 修复总结已保存到 save_state_integration_fix_summary.json")

def main():
    """主函数"""
    print("🚀 测试保存状态管理集成修复")
    print("=" * 60)
    
    # 检查服务器
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        print("✅ 服务器运行正常")
    except:
        print("❌ 服务器未运行，请先启动服务器")
        return False
    
    # 运行测试
    test1 = test_review_page_initialization()
    test2 = test_javascript_functions()
    
    # 创建总结
    create_fix_summary()
    
    # 最终结果
    print(f"\n{'='*60}")
    print("📊 修复测试结果:")
    print(f"   页面初始化测试: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"   JavaScript函数测试: {'✅ 通过' if test2 else '❌ 失败'}")
    
    if test1 and test2:
        print(f"\n🎉 保存状态管理集成修复成功!")
        print("✅ 函数重复定义问题已解决")
        print("✅ 页面初始化应该不再失败")
        print("✅ 保存状态管理集成步骤应该返回 true")
        
        print(f"\n💡 建议:")
        print("   1. 刷新复盘页面测试初始化结果")
        print("   2. 检查浏览器控制台确认没有错误")
        print("   3. 测试保存功能是否正常工作")
        
        return True
    else:
        print(f"\n⚠️  修复测试部分失败，可能仍有问题")
        return False

if __name__ == "__main__":
    main()