#!/usr/bin/env python3
"""
验证暴力修复是否成功
"""

import os

def check_brutal_fix():
    """检查暴力修复脚本"""
    js_file = 'static/js/review-emergency-fix.js'
    
    if not os.path.exists(js_file):
        print(f"❌ 文件不存在: {js_file}")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔥 检查暴力修复脚本...")
    
    # 检查暴力覆盖标记
    brutal_markers = [
        '🔥 暴力覆盖模式启动',
        'window.openReviewModal = function',
        '🔥 使用暴力覆盖的openReviewModal函数',
        '🔥 暴力覆盖完成'
    ]
    
    all_found = True
    for marker in brutal_markers:
        if marker in content:
            print(f"✅ {marker}")
        else:
            print(f"❌ {marker} - 未找到")
            all_found = False
    
    # 检查是否在脚本开头
    lines = content.split('\n')
    brutal_start_found = False
    for i, line in enumerate(lines[:50]):  # 检查前50行
        if '🔥 暴力覆盖模式启动' in line:
            print(f"✅ 暴力覆盖在第{i+1}行开始（足够早）")
            brutal_start_found = True
            break
    
    if not brutal_start_found:
        print("❌ 暴力覆盖没有在脚本开头执行")
        all_found = False
    
    return all_found

def main():
    """主函数"""
    print("🔥 暴力修复验证")
    print("=" * 40)
    
    if check_brutal_fix():
        print("\n🎉 暴力修复验证通过！")
        print("\n现在应该：")
        print("1. 重新加载复盘分析页面")
        print("2. 点击复盘按钮应该不再报错")
        print("3. 模态框应该能正常打开")
        print("\n如果还有问题，请使用 test_brutal_fix.html 进行测试")
        return True
    else:
        print("\n❌ 暴力修复验证失败")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)