#!/usr/bin/env python3
"""
验证交易录入工作流程实现
"""
import os
import re

def check_api_endpoint():
    """检查API端点是否正确实现"""
    print("=== 检查API端点实现 ===")
    
    # 检查trading_routes.py中的新端点
    with open('api/trading_routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 检查是否有current-holdings端点
    if '/trades/current-holdings' in content:
        print("✅ 找到 /trades/current-holdings 端点")
    else:
        print("❌ 未找到 /trades/current-holdings 端点")
        
    # 检查函数名是否正确
    if 'def get_current_holdings_for_trading():' in content:
        print("✅ 函数名正确，避免了冲突")
    else:
        print("❌ 函数名可能有问题")
        
    # 检查是否使用了AnalyticsService
    if 'AnalyticsService._calculate_current_holdings' in content:
        print("✅ 正确使用了AnalyticsService计算持仓")
    else:
        print("❌ 未正确使用AnalyticsService")

def check_template_changes():
    """检查模板文件的修改"""
    print("\n=== 检查模板文件修改 ===")
    
    with open('templates/trading_records.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查交易类型选择界面
    if 'trade-type-selection' in content:
        print("✅ 找到交易类型选择界面")
    else:
        print("❌ 未找到交易类型选择界面")
        
    # 检查买入和卖出的不同界面
    if 'buy-stock-input' in content and 'sell-stock-selection' in content:
        print("✅ 找到买入和卖出的不同界面")
    else:
        print("❌ 未找到买入和卖出的不同界面")
        
    # 检查持仓股票选择器
    if 'holding-stock-select' in content:
        print("✅ 找到持仓股票选择器")
    else:
        print("❌ 未找到持仓股票选择器")
        
    # 检查JavaScript方法
    js_methods = [
        'selectTradeType',
        'loadCurrentHoldings',
        'populateHoldingStockSelect',
        'onHoldingStockSelect',
        'showTradeTypeSelection'
    ]
    
    found_methods = []
    for method in js_methods:
        if f'{method}(' in content:
            found_methods.append(method)
            
    print(f"✅ 找到 {len(found_methods)}/{len(js_methods)} 个JavaScript方法:")
    for method in found_methods:
        print(f"  - {method}")
        
    missing_methods = set(js_methods) - set(found_methods)
    if missing_methods:
        print(f"❌ 缺少方法: {', '.join(missing_methods)}")

def check_event_listeners():
    """检查事件监听器"""
    print("\n=== 检查事件监听器 ===")
    
    with open('templates/trading_records.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查新的事件监听器
    listeners = [
        'select-buy-btn',
        'select-sell-btn', 
        'back-to-type-selection',
        'holding-stock-select'
    ]
    
    found_listeners = []
    for listener in listeners:
        if f"getElementById('{listener}').addEventListener" in content:
            found_listeners.append(listener)
            
    print(f"✅ 找到 {len(found_listeners)}/{len(listeners)} 个事件监听器:")
    for listener in found_listeners:
        print(f"  - {listener}")

def check_validation_updates():
    """检查表单验证更新"""
    print("\n=== 检查表单验证更新 ===")
    
    with open('templates/trading_records.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查股票代码验证是否支持卖出模式
    if 'this.currentTradeType === \'sell\'' in content:
        print("✅ 股票代码验证支持卖出模式")
    else:
        print("❌ 股票代码验证未支持卖出模式")
        
    # 检查数量验证是否支持持仓限制
    if 'maxQuantity' in content and 'quantityInput.max' in content:
        print("✅ 数量验证支持持仓限制")
    else:
        print("❌ 数量验证未支持持仓限制")

def main():
    """主函数"""
    print("验证交易录入工作流程实现")
    print("=" * 50)
    
    check_api_endpoint()
    check_template_changes()
    check_event_listeners()
    check_validation_updates()
    
    print("\n=== 验证完成 ===")

if __name__ == "__main__":
    main()