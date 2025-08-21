#!/usr/bin/env python3
"""
验证止损价格修复的脚本
"""

import re
import os

def verify_stop_loss_fix():
    """验证止损价格修复是否正确应用"""
    
    template_file = 'templates/trading_records.html'
    
    if not os.path.exists(template_file):
        print("❌ 模板文件不存在")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_verified = []
    
    # 1. 验证是否添加了DOM直接获取逻辑
    dom_logic_pattern = r'const stopLossPriceElement = document\.getElementById\(\'stop-loss-price\'\);'
    if re.search(dom_logic_pattern, content):
        fixes_verified.append("✅ 添加了DOM直接获取止损价格的逻辑")
    else:
        fixes_verified.append("❌ 缺少DOM直接获取逻辑")
    
    # 2. 验证是否添加了调试信息
    debug_pattern = r'console\.log\(\'\[DEBUG\] 从DOM获取止损价格:\''
    if re.search(debug_pattern, content):
        fixes_verified.append("✅ 添加了止损价格调试信息")
    else:
        fixes_verified.append("❌ 缺少调试信息")
    
    # 3. 验证是否检查了DOM中的止损价格值
    dom_check_pattern = r'console\.log\(\'\[DEBUG\] DOM中的止损价格值:\''
    if re.search(dom_check_pattern, content):
        fixes_verified.append("✅ 添加了DOM值检查")
    else:
        fixes_verified.append("❌ 缺少DOM值检查")
    
    # 4. 验证是否有数值验证逻辑
    validation_pattern = r'if \(!isNaN\(stopLossPrice\) && stopLossPrice > 0\)'
    if re.search(validation_pattern, content):
        fixes_verified.append("✅ 添加了止损价格数值验证")
    else:
        fixes_verified.append("❌ 缺少数值验证")
    
    # 5. 验证止损价格字段定义是否正确
    field_pattern = r'name="stop_loss_price"'
    if re.search(field_pattern, content):
        fixes_verified.append("✅ 止损价格字段定义正确")
    else:
        fixes_verified.append("❌ 止损价格字段定义有问题")
    
    # 输出验证结果
    print("🔍 止损价格修复验证结果:")
    print("=" * 50)
    for fix in fixes_verified:
        print(fix)
    
    # 检查是否所有修复都成功
    success_count = sum(1 for fix in fixes_verified if fix.startswith("✅"))
    total_count = len(fixes_verified)
    
    print("=" * 50)
    print(f"修复成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 止损价格修复已成功应用！")
        return True
    else:
        print("⚠️  部分修复可能需要进一步检查")
        return False

def analyze_form_serialization():
    """分析表单序列化可能的问题"""
    
    print("\n🔧 表单序列化问题分析:")
    print("-" * 30)
    
    # 检查可能的问题
    issues = [
        "1. 隐藏字段序列化：买入设置默认隐藏，可能影响FormData序列化",
        "2. 字段值为空：如果止损价格为空字符串，可能被忽略",
        "3. 字段类型：number类型字段的值可能需要特殊处理",
        "4. 表单结构：嵌套在div中的字段可能有序列化问题"
    ]
    
    for issue in issues:
        print(f"   {issue}")
    
    print("\n💡 修复策略:")
    strategies = [
        "✅ 直接从DOM获取字段值，绕过FormData序列化问题",
        "✅ 添加详细的调试信息，便于问题定位",
        "✅ 增加数值验证，确保数据有效性",
        "✅ 保留原有的删除逻辑，处理空值情况"
    ]
    
    for strategy in strategies:
        print(f"   {strategy}")

def suggest_testing_steps():
    """建议测试步骤"""
    
    print("\n📋 建议测试步骤:")
    print("-" * 20)
    
    steps = [
        "1. 打开浏览器开发者工具，查看控制台",
        "2. 访问交易记录页面",
        "3. 编辑一个有止损价格的买入交易",
        "4. 查看控制台中的调试信息：",
        "   - '[DEBUG] DOM中的止损价格值: xxx'",
        "   - '[DEBUG] 从DOM获取止损价格: xxx'",
        "5. 保存交易，检查数据是否正确保存",
        "6. 重新编辑同一交易，验证止损价格是否正确显示"
    ]
    
    for step in steps:
        print(f"   {step}")

if __name__ == "__main__":
    print("🚀 开始验证止损价格修复...")
    
    success = verify_stop_loss_fix()
    analyze_form_serialization()
    suggest_testing_steps()
    
    if success:
        print("\n✨ 修复验证完成！现在可以测试止损价格功能了。")
    else:
        print("\n❌ 部分修复可能不完整，请检查上述问题。")