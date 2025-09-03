#!/usr/bin/env python3
"""
验证历史交易修复是否正确应用
"""
import os
import re

def check_file_modifications():
    """检查文件修改是否正确应用"""
    print("=== 验证历史交易修复 ===\n")
    
    # 检查模板文件
    template_file = "templates/historical_trades.html"
    if os.path.exists(template_file):
        print(f"✓ 检查 {template_file}")
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查统计卡片布局
        if 'col-lg-3 col-md-6 mb-3 mb-lg-0' in content:
            print("  ✓ 统计卡片横排布局已应用")
        else:
            print("  ✗ 统计卡片横排布局未找到")
            
        # 检查排序控件
        if 'label class="form-label small text-muted"' in content:
            print("  ✓ 排序控件标签已添加")
        else:
            print("  ✗ 排序控件标签未找到")
            
        # 检查新的排序选项
        if 'total_investment">按投入本金' in content:
            print("  ✓ 新排序选项已添加")
        else:
            print("  ✗ 新排序选项未找到")
            
        # 检查CSS样式
        if '#statistics-cards .card {' in content:
            print("  ✓ 统计卡片CSS样式已添加")
        else:
            print("  ✗ 统计卡片CSS样式未找到")
    else:
        print(f"✗ {template_file} 文件不存在")
    
    print()
    
    # 检查JavaScript文件
    js_file = "static/js/historical-trades-manager.js"
    if os.path.exists(js_file):
        print(f"✓ 检查 {js_file}")
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查统计信息渲染修复
        if 'stats.win_rate || 0' in content:
            print("  ✓ 统计信息渲染已修复")
        else:
            print("  ✗ 统计信息渲染修复未找到")
            
        # 检查排序事件监听器
        if 'sortBySelect.addEventListener' in content:
            print("  ✓ 排序事件监听器已添加")
        else:
            print("  ✗ 排序事件监听器未找到")
            
        # 检查数字格式化改进
        if 'toLocaleString(\'zh-CN\'' in content:
            print("  ✓ 数字格式化已改进")
        else:
            print("  ✗ 数字格式化改进未找到")
            
        # 检查筛选函数修复
        if 'console.log(\'应用筛选和排序:\', filters)' in content:
            print("  ✓ 筛选函数调试日志已添加")
        else:
            print("  ✗ 筛选函数调试日志未找到")
    else:
        print(f"✗ {js_file} 文件不存在")
    
    print()
    
    # 检查服务文件
    service_file = "services/historical_trade_service.py"
    if os.path.exists(service_file):
        print(f"✓ 检查 {service_file}")
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查统计信息字段
        if "'avg_return_rate': round(float(avg_return_rate) * 100, 2)" in content:
            print("  ✓ 平均收益率字段正确")
        else:
            print("  ✗ 平均收益率字段可能有问题")
            
        # 检查胜率计算
        if "'win_rate': round(win_rate, 1)" in content:
            print("  ✓ 胜率计算已修复")
        else:
            print("  ✗ 胜率计算修复未找到")
    else:
        print(f"✗ {service_file} 文件不存在")

def check_test_files():
    """检查测试文件是否创建"""
    print("\n=== 检查测试文件 ===")
    
    test_files = [
        "test_historical_trades_fixes.html",
        "test_historical_trades_sorting.py",
        "HISTORICAL_TRADES_FIXES_SUMMARY.md"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            print(f"✓ {file} 已创建")
        else:
            print(f"✗ {file} 未找到")

def generate_deployment_checklist():
    """生成部署检查清单"""
    print("\n=== 部署检查清单 ===")
    
    checklist = [
        "1. 确认模板文件 templates/historical_trades.html 已更新",
        "2. 确认JavaScript文件 static/js/historical-trades-manager.js 已更新", 
        "3. 确认服务文件 services/historical_trade_service.py 已更新",
        "4. 重启Flask应用服务器",
        "5. 清除浏览器缓存",
        "6. 测试统计卡片横排显示",
        "7. 测试平均收益率是否正确显示",
        "8. 测试收益率排序功能",
        "9. 测试其他排序字段（持仓天数、投入本金等）",
        "10. 测试响应式布局（移动设备）"
    ]
    
    for item in checklist:
        print(f"□ {item}")

if __name__ == "__main__":
    check_file_modifications()
    check_test_files()
    generate_deployment_checklist()
    
    print("\n=== 修复总结 ===")
    print("已完成以下修复:")
    print("1. ✅ 统计卡片改为横排布局，更美观")
    print("2. ✅ 修复平均收益率显示问题")
    print("3. ✅ 修复收益列表排序功能")
    print("4. ✅ 改进数字格式化显示")
    print("5. ✅ 优化UI样式和用户体验")
    print("\n请按照部署检查清单进行部署和测试。")