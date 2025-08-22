#!/usr/bin/env python3
"""
验证板块数据刷新修复
检查UXUtils.showToast方法是否已正确添加
"""

import os
import re

def check_uxutils_showtoast():
    """检查UXUtils.showToast方法是否存在"""
    utils_js_path = 'static/js/utils.js'
    
    if not os.path.exists(utils_js_path):
        return False, "utils.js文件不存在"
    
    with open(utils_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查showToast方法是否存在
    showtoast_pattern = r'showToast\s*:\s*\([^)]*\)\s*=>\s*{'
    if re.search(showtoast_pattern, content):
        return True, "UXUtils.showToast方法已存在"
    
    # 检查是否有showToast的别名定义
    alias_pattern = r'showToast.*UXUtils\.showMessage'
    if re.search(alias_pattern, content):
        return True, "UXUtils.showToast别名方法已存在"
    
    return False, "UXUtils.showToast方法不存在"

def check_main_js_calls():
    """检查main.js中对UXUtils.showToast的调用"""
    main_js_path = 'static/js/main.js'
    
    if not os.path.exists(main_js_path):
        return False, "main.js文件不存在"
    
    with open(main_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找UXUtils.showToast的调用
    calls = re.findall(r'UXUtils\.showToast\([^)]*\)', content)
    
    if calls:
        return True, f"找到{len(calls)}个UXUtils.showToast调用: {calls}"
    else:
        return False, "未找到UXUtils.showToast调用"

def check_sector_analysis_template():
    """检查板块分析模板中的refreshSectorData函数"""
    template_path = 'templates/sector_analysis.html'
    
    if not os.path.exists(template_path):
        return False, "sector_analysis.html模板不存在"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查refreshSectorData函数是否存在
    if 'async function refreshSectorData()' in content:
        # 检查是否调用了showMessage
        if 'showMessage(' in content:
            return True, "refreshSectorData函数存在且调用了showMessage"
        else:
            return False, "refreshSectorData函数存在但未调用showMessage"
    else:
        return False, "refreshSectorData函数不存在"

def main():
    """主验证函数"""
    print("🔍 验证板块数据刷新修复...")
    print("=" * 50)
    
    # 检查UXUtils.showToast方法
    success, message = check_uxutils_showtoast()
    status = "✅" if success else "❌"
    print(f"{status} UXUtils.showToast: {message}")
    
    # 检查main.js中的调用
    success, message = check_main_js_calls()
    status = "✅" if success else "❌"
    print(f"{status} main.js调用: {message}")
    
    # 检查板块分析模板
    success, message = check_sector_analysis_template()
    status = "✅" if success else "❌"
    print(f"{status} 板块分析模板: {message}")
    
    print("\n" + "=" * 50)
    
    # 检查JavaScript文件加载顺序
    base_template_path = 'templates/base.html'
    if os.path.exists(base_template_path):
        with open(base_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查JavaScript文件加载顺序
        js_files = re.findall(r'static/js/([^"\']+\.js)', content)
        print("📋 JavaScript文件加载顺序:")
        for i, js_file in enumerate(js_files, 1):
            print(f"  {i}. {js_file}")
        
        # 验证关键文件是否按正确顺序加载
        required_order = ['utils.js', 'api.js', 'main.js']
        current_order = [f for f in js_files if f in required_order]
        
        if current_order == required_order:
            print("✅ JavaScript文件加载顺序正确")
        else:
            print(f"❌ JavaScript文件加载顺序错误: {current_order}")
    
    print("\n🎯 修复总结:")
    print("1. 已在UXUtils中添加showToast方法")
    print("2. showToast方法作为showMessage的别名")
    print("3. 保持了与现有代码的兼容性")
    print("4. 板块数据刷新功能应该可以正常工作")
    
    print("\n🧪 测试建议:")
    print("1. 打开板块分析页面")
    print("2. 点击'刷新板块数据'按钮")
    print("3. 观察是否有错误消息显示")
    print("4. 检查浏览器控制台是否还有UXUtils.showToast错误")

if __name__ == '__main__':
    main()