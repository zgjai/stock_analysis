#!/usr/bin/env python3
"""
验证非交易日配置导航修复
"""

import os
import re

def check_main_js_routes():
    """检查main.js中的路由配置"""
    main_js_path = 'static/js/main.js'
    
    if not os.path.exists(main_js_path):
        print("❌ main.js文件不存在")
        return False
    
    with open(main_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含non-trading-days路由
    if "'non-trading-days': '/non-trading-days'" in content:
        print("✅ main.js中已添加non-trading-days路由")
        return True
    else:
        print("❌ main.js中缺少non-trading-days路由")
        return False

def check_base_template():
    """检查base.html模板中的导航链接"""
    base_template_path = 'templates/base.html'
    
    if not os.path.exists(base_template_path):
        print("❌ base.html模板不存在")
        return False
    
    with open(base_template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查导航链接
    if 'data-page="non-trading-days"' in content and '非交易日配置' in content:
        print("✅ base.html中包含正确的导航链接")
        return True
    else:
        print("❌ base.html中导航链接有问题")
        return False

def check_routes_py():
    """检查routes.py中的路由定义"""
    routes_path = 'routes.py'
    
    if not os.path.exists(routes_path):
        print("❌ routes.py文件不存在")
        return False
    
    with open(routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查路由定义
    if "@frontend_bp.route('/non-trading-days')" in content and "def non_trading_days():" in content:
        print("✅ routes.py中包含正确的路由定义")
        return True
    else:
        print("❌ routes.py中路由定义有问题")
        return False

def check_non_trading_days_template():
    """检查非交易日配置模板"""
    template_path = 'templates/non_trading_days.html'
    
    if not os.path.exists(template_path):
        print("❌ non_trading_days.html模板不存在")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查模板内容
    if 'non-trading-days.js' in content and '非交易日配置' in content:
        print("✅ non_trading_days.html模板正确")
        return True
    else:
        print("❌ non_trading_days.html模板有问题")
        return False

def check_non_trading_days_js():
    """检查非交易日配置JavaScript文件"""
    js_path = 'static/js/non-trading-days.js'
    
    if not os.path.exists(js_path):
        print("❌ non-trading-days.js文件不存在")
        return False
    
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查JavaScript类定义
    if 'class NonTradingDaysManager' in content and 'nonTradingDaysManager = new NonTradingDaysManager()' in content:
        print("✅ non-trading-days.js文件正确")
        return True
    else:
        print("❌ non-trading-days.js文件有问题")
        return False

def main():
    """主验证函数"""
    print("🔍 验证非交易日配置导航修复...")
    print("=" * 50)
    
    checks = [
        check_main_js_routes,
        check_base_template,
        check_routes_py,
        check_non_trading_days_template,
        check_non_trading_days_js
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    print("=" * 50)
    
    if all(results):
        print("🎉 所有检查通过！非交易日配置导航应该可以正常工作了。")
        print("\n📋 修复总结：")
        print("1. ✅ 在main.js中添加了non-trading-days路由映射")
        print("2. ✅ 在main.js中添加了页面初始化逻辑")
        print("3. ✅ 确认了所有相关文件都存在且配置正确")
        print("\n🚀 现在可以测试点击'非交易日配置'tab了！")
    else:
        print("❌ 部分检查失败，请检查上述错误信息。")
        
    return all(results)

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)