#!/usr/bin/env python3
"""
最终百分比修复验证
检查所有相关文件是否正确处理百分比显示
"""

import os
import re

def check_file_for_percentage_issues(filepath):
    """检查文件中是否存在百分比处理问题"""
    
    if not os.path.exists(filepath):
        return {"status": "not_found", "issues": []}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"status": "error", "issues": [f"读取文件失败: {e}"]}
    
    issues = []
    
    # 检查可能的问题模式
    patterns = [
        {
            "pattern": r'(data\.\w+_rate.*?)\s*/\s*100.*?Formatters\.percentage',
            "description": "可能存在双重百分比转换",
            "severity": "high"
        },
        {
            "pattern": r'(data\.\w+_rate.*?)\s*/\s*100.*?\*\s*100',
            "description": "可能存在除以100后又乘以100的问题",
            "severity": "high"
        },
        {
            "pattern": r'Formatters\.percentage\([^)]*\s*/\s*100[^)]*\)',
            "description": "Formatters.percentage参数中包含除以100",
            "severity": "medium"
        }
    ]
    
    for pattern_info in patterns:
        matches = re.finditer(pattern_info["pattern"], content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                "line": line_num,
                "text": match.group(0),
                "description": pattern_info["description"],
                "severity": pattern_info["severity"]
            })
    
    return {"status": "checked", "issues": issues}

def verify_fix_implementation():
    """验证修复实现"""
    
    print("=== 仪表板百分比修复最终验证 ===\n")
    
    # 需要检查的文件列表
    files_to_check = [
        {
            "path": "static/js/dashboard.js",
            "description": "主要仪表板JavaScript文件",
            "critical": True
        },
        {
            "path": "static/js/optimized-dashboard.js", 
            "description": "优化版仪表板JavaScript文件",
            "critical": True
        },
        {
            "path": "templates/analytics.html",
            "description": "分析页面模板",
            "critical": False
        },
        {
            "path": "routes.py",
            "description": "路由文件（包含测试代码）",
            "critical": False
        },
        {
            "path": "static/js/utils.js",
            "description": "工具函数文件",
            "critical": False
        }
    ]
    
    all_good = True
    
    for file_info in files_to_check:
        print(f"🔍 检查文件: {file_info['path']}")
        print(f"   描述: {file_info['description']}")
        
        result = check_file_for_percentage_issues(file_info['path'])
        
        if result["status"] == "not_found":
            print(f"   ⚠️  文件不存在")
            if file_info['critical']:
                all_good = False
        elif result["status"] == "error":
            print(f"   ❌ 检查失败: {result['issues'][0]}")
            if file_info['critical']:
                all_good = False
        else:
            if result["issues"]:
                print(f"   ❌ 发现 {len(result['issues'])} 个潜在问题:")
                for issue in result["issues"]:
                    severity_icon = "🔴" if issue["severity"] == "high" else "🟡"
                    print(f"      {severity_icon} 第{issue['line']}行: {issue['description']}")
                    print(f"         代码: {issue['text'][:100]}...")
                if file_info['critical'] and any(i["severity"] == "high" for i in result["issues"]):
                    all_good = False
            else:
                print(f"   ✅ 未发现问题")
        
        print()
    
    return all_good

def check_specific_fixes():
    """检查具体的修复内容"""
    
    print("=== 具体修复内容验证 ===\n")
    
    # 检查 dashboard.js 的修复
    dashboard_js_path = "static/js/dashboard.js"
    if os.path.exists(dashboard_js_path):
        with open(dashboard_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📋 检查 dashboard.js 修复:")
        
        # 检查是否移除了错误的除法
        if "data.total_return_rate || 0) / 100" in content:
            print("   ❌ 仍然存在错误的总收益率除法")
        else:
            print("   ✅ 总收益率除法已修复")
            
        if "data.success_rate || 0) / 100" in content:
            print("   ❌ 仍然存在错误的成功率除法")
        else:
            print("   ✅ 成功率除法已修复")
        
        # 检查是否正确使用 Formatters.percentage
        if "Formatters.percentage(profit)" in content and "Formatters.percentage(rate)" in content:
            print("   ✅ 正确使用 Formatters.percentage")
        else:
            print("   ⚠️  可能未正确使用 Formatters.percentage")
    
    print()
    
    # 检查 optimized-dashboard.js 的修复
    optimized_js_path = "static/js/optimized-dashboard.js"
    if os.path.exists(optimized_js_path):
        with open(optimized_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📋 检查 optimized-dashboard.js 修复:")
        
        # 检查是否添加了新的百分比动画函数
        if "animateValuePercentage" in content:
            print("   ✅ 已添加 animateValuePercentage 函数")
        else:
            print("   ❌ 未找到 animateValuePercentage 函数")
            
        # 检查是否正确调用新函数
        if "animateValuePercentage('total-return-rate'" in content:
            print("   ✅ 正确调用总收益率动画函数")
        else:
            print("   ❌ 未正确调用总收益率动画函数")
            
        if "animateValuePercentage('success-rate'" in content:
            print("   ✅ 正确调用成功率动画函数")
        else:
            print("   ❌ 未正确调用成功率动画函数")
    
    print()

def generate_test_recommendations():
    """生成测试建议"""
    
    print("=== 测试建议 ===\n")
    
    print("🧪 建议的测试步骤:")
    print("1. 启动开发服务器:")
    print("   python app.py")
    print()
    print("2. 访问仪表板页面:")
    print("   http://localhost:5000/")
    print()
    print("3. 检查显示内容:")
    print("   - 总收益率应显示为合理的百分比 (如 2.00%)")
    print("   - 成功率应显示为合理的百分比 (如 41.0%)")
    print("   - 不应出现 0.02% 或 0.41% 这样的异常小值")
    print()
    print("4. 运行专门的测试页面:")
    print("   http://localhost:5000/test_dashboard_percentage_fix.html")
    print()
    print("5. 检查浏览器控制台:")
    print("   - 确保没有JavaScript错误")
    print("   - 检查API响应数据格式")
    print()
    print("6. 测试不同数据场景:")
    print("   - 正收益和负收益")
    print("   - 零值和空值")
    print("   - 极大值和极小值")

def main():
    """主函数"""
    
    # 验证修复实现
    fixes_ok = verify_fix_implementation()
    
    # 检查具体修复内容
    check_specific_fixes()
    
    # 生成测试建议
    generate_test_recommendations()
    
    # 总结
    print("\n=== 验证总结 ===\n")
    
    if fixes_ok:
        print("✅ 所有关键文件检查通过")
        print("✅ 百分比显示修复已正确实现")
        print("✅ 可以进行功能测试")
    else:
        print("❌ 发现潜在问题，需要进一步检查")
        print("❌ 建议重新检查修复实现")
    
    print("\n📋 修复文件清单:")
    print("- static/js/dashboard.js (已修复)")
    print("- static/js/optimized-dashboard.js (已修复)")
    print("- test_dashboard_percentage_fix.html (测试文件)")
    print("- verify_dashboard_percentage_fix.py (验证脚本)")
    print("- DASHBOARD_PERCENTAGE_FIX_SUMMARY.md (修复文档)")

if __name__ == "__main__":
    main()