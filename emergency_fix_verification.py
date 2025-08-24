#!/usr/bin/env python3
"""
紧急修复验证脚本 - 检查交易记录页面是否能正常加载
"""

import re
import os

def check_javascript_syntax():
    """检查JavaScript语法问题"""
    
    template_file = 'templates/trading_records.html'
    
    if not os.path.exists(template_file):
        print("❌ 模板文件不存在")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 1. 检查重复的变量声明
    stopLossDeclarations = re.findall(r'const stopLossPriceElement', content)
    if len(stopLossDeclarations) > 1:
        issues.append(f"❌ stopLossPriceElement 重复声明 {len(stopLossDeclarations)} 次")
    else:
        print("✅ stopLossPriceElement 声明正常")
    
    # 2. 检查大括号匹配
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        issues.append(f"❌ 大括号不匹配: {open_braces} 开 vs {close_braces} 闭")
    else:
        print("✅ 大括号匹配正常")
    
    # 3. 检查关键方法是否存在
    if 'triggerFormValidation()' in content:
        print("✅ triggerFormValidation 方法存在")
    else:
        issues.append("❌ triggerFormValidation 方法缺失")
    
    # 4. 检查TradingRecordsManager类结构
    if 'class TradingRecordsManager' in content:
        print("✅ TradingRecordsManager 类定义存在")
    else:
        issues.append("❌ TradingRecordsManager 类定义缺失")
    
    # 5. 检查handleTradeFormSubmit方法
    if 'async handleTradeFormSubmit(formData)' in content:
        print("✅ handleTradeFormSubmit 方法存在")
    else:
        issues.append("❌ handleTradeFormSubmit 方法缺失")
    
    return len(issues) == 0, issues

def check_critical_functions():
    """检查关键功能是否完整"""
    
    template_file = 'templates/trading_records.html'
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    critical_functions = [
        ('loadTrades', '加载交易记录'),
        ('editTrade', '编辑交易'),
        ('saveTrade', '保存交易'),
        ('updateReasonOptions', '更新原因选项'),
        ('populateBasicTradeForm', '填充基本表单'),
    ]
    
    missing_functions = []
    
    for func_name, description in critical_functions:
        if func_name in content:
            print(f"✅ {description} ({func_name}) 存在")
        else:
            missing_functions.append(f"❌ {description} ({func_name}) 缺失")
    
    return len(missing_functions) == 0, missing_functions

def suggest_immediate_actions():
    """建议立即采取的行动"""
    
    print("\n🚨 立即行动建议:")
    print("-" * 30)
    
    actions = [
        "1. 刷新浏览器页面，清除缓存",
        "2. 打开浏览器开发者工具，查看控制台错误",
        "3. 如果仍有问题，请提供具体的错误信息",
        "4. 检查网络请求是否正常（Network标签）",
        "5. 验证JavaScript文件是否正确加载"
    ]
    
    for action in actions:
        print(f"   {action}")

def main():
    print("🚨 紧急修复验证 - 交易记录页面")
    print("=" * 50)
    
    # 检查JavaScript语法
    syntax_ok, syntax_issues = check_javascript_syntax()
    
    if syntax_issues:
        print("\n❌ 发现语法问题:")
        for issue in syntax_issues:
            print(f"   {issue}")
    
    # 检查关键功能
    print("\n🔍 检查关键功能:")
    functions_ok, missing_functions = check_critical_functions()
    
    if missing_functions:
        print("\n❌ 缺失的功能:")
        for func in missing_functions:
            print(f"   {func}")
    
    # 总体状态
    print("\n" + "=" * 50)
    if syntax_ok and functions_ok:
        print("🎉 验证通过！页面应该能正常加载。")
        print("\n💡 如果页面仍然有问题，可能是:")
        print("   - 浏览器缓存问题")
        print("   - 网络连接问题") 
        print("   - 服务器端问题")
    else:
        print("⚠️ 发现问题，需要进一步修复。")
    
    suggest_immediate_actions()

if __name__ == "__main__":
    main()