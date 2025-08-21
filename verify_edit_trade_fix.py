#!/usr/bin/env python3
"""
验证编辑交易修复的脚本
"""

import re
import os

def verify_fixes():
    """验证修复是否正确应用"""
    
    template_file = 'templates/trading_records.html'
    
    if not os.path.exists(template_file):
        print("❌ 模板文件不存在")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_verified = []
    
    # 1. 验证 triggerFormValidation 方法是否存在
    if 'triggerFormValidation()' in content and 'console.log(\'Triggering form validation...\');' in content:
        fixes_verified.append("✅ triggerFormValidation 方法已添加")
    else:
        fixes_verified.append("❌ triggerFormValidation 方法缺失")
    
    # 2. 验证 updateReasonOptions 方法是否保留当前值
    if 'const currentValue = reasonSelect.value;' in content and 'reasonSelect.value = currentValue;' in content:
        fixes_verified.append("✅ updateReasonOptions 方法已修复，会保留当前选中值")
    else:
        fixes_verified.append("❌ updateReasonOptions 方法未正确修复")
    
    # 3. 验证调用顺序是否正确
    # 查找 editTrade 方法中的调用顺序
    edit_trade_pattern = r'console\.log\(\'Updating reason options\.\.\.\'\);.*?this\.updateReasonOptions\(trade\.trade_type\);.*?console\.log\(\'Populating basic form\.\.\.\'\);.*?this\.populateBasicTradeForm\(trade\);'
    if re.search(edit_trade_pattern, content, re.DOTALL):
        fixes_verified.append("✅ editTrade 方法调用顺序已修复")
    else:
        fixes_verified.append("❌ editTrade 方法调用顺序未正确修复")
    
    # 4. 验证止损价格设置是否存在
    if 'document.getElementById(\'stop-loss-price\').value = trade.stop_loss_price || \'\';' in content:
        fixes_verified.append("✅ 止损价格设置代码存在")
    else:
        fixes_verified.append("❌ 止损价格设置代码缺失")
    
    # 输出验证结果
    print("🔍 编辑交易修复验证结果:")
    print("=" * 50)
    for fix in fixes_verified:
        print(fix)
    
    # 检查是否所有修复都成功
    success_count = sum(1 for fix in fixes_verified if fix.startswith("✅"))
    total_count = len(fixes_verified)
    
    print("=" * 50)
    print(f"修复成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 所有修复都已成功应用！")
        return True
    else:
        print("⚠️  部分修复可能需要进一步检查")
        return False

def check_common_issues():
    """检查常见问题"""
    
    print("\n🔧 检查常见问题:")
    print("-" * 30)
    
    # 检查是否有重复的方法定义
    template_file = 'templates/trading_records.html'
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计 triggerFormValidation 出现次数
    trigger_count = content.count('triggerFormValidation()')
    if trigger_count > 1:
        print(f"⚠️  triggerFormValidation 方法定义了 {trigger_count} 次，可能有重复")
    else:
        print("✅ triggerFormValidation 方法定义正常")
    
    # 检查是否有语法错误的迹象
    if content.count('{') != content.count('}'):
        print("⚠️  大括号不匹配，可能有语法错误")
    else:
        print("✅ 大括号匹配正常")
    
    # 检查关键字段是否存在
    required_fields = ['stock-code', 'reason', 'stop-loss-price']
    for field in required_fields:
        if f'id="{field}"' in content:
            print(f"✅ 字段 {field} 存在")
        else:
            print(f"❌ 字段 {field} 缺失")

if __name__ == "__main__":
    print("🚀 开始验证编辑交易修复...")
    
    success = verify_fixes()
    check_common_issues()
    
    if success:
        print("\n✨ 修复验证完成！可以测试编辑交易功能了。")
        print("\n📝 测试步骤:")
        print("1. 启动服务器")
        print("2. 访问交易记录页面")
        print("3. 点击编辑按钮")
        print("4. 检查操作原因和止损价格是否正确显示")
        print("5. 检查控制台是否还有 triggerFormValidation 错误")
    else:
        print("\n❌ 部分修复可能不完整，请检查上述问题。")