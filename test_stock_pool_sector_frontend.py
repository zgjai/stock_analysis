#!/usr/bin/env python3
"""
股票池和板块分析前端页面测试脚本
测试任务16的实现：股票池管理界面和板块分析前端页面
"""

import os
import sys
import re
from pathlib import Path

def test_stock_pool_template():
    """测试股票池模板实现"""
    print("=== 测试股票池模板 ===")
    
    template_path = "templates/stock_pool.html"
    if not os.path.exists(template_path):
        print(f"❌ 模板文件不存在: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必要的HTML元素
    required_elements = [
        # 操作按钮
        'data-bs-toggle="modal"',
        'data-bs-target="#addStockModal"',
        'onclick="refreshStockPool()"',
        
        # 股票池区域
        'id="watch-pool"',
        'id="buy-pool"',
        'id="watch-pool-count"',
        'id="buy-pool-count"',
        'id="pool-history"',
        
        # 模态框
        'id="addStockModal"',
        'id="editStockModal"',
        'id="addStockForm"',
        'id="editStockForm"',
        
        # 表单字段
        'id="stockCode"',
        'id="stockName"',
        'id="poolType"',
        'id="targetPrice"',
        'id="addReason"',
        
        # JavaScript函数
        'function initStockPool()',
        'function loadStockPool()',
        'function submitAddStock()',
        'function editStock(',
        'function moveStock(',
        'function removeStock(',
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ 缺少必要元素: {missing_elements}")
        return False
    
    print("✅ 股票池模板检查通过")
    return True

def test_sector_analysis_template():
    """测试板块分析模板实现"""
    print("=== 测试板块分析模板 ===")
    
    template_path = "templates/sector_analysis.html"
    if not os.path.exists(template_path):
        print(f"❌ 模板文件不存在: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必要的HTML元素
    required_elements = [
        # 操作按钮
        'onclick="refreshSectorData()"',
        'onclick="loadSectorRanking()"',
        'onclick="toggleChartView()"',
        
        # 板块排名区域
        'id="sector-ranking-tbody"',
        'id="sector-table-view"',
        'id="sector-chart-view"',
        'id="sectorChart"',
        
        # 筛选控件
        'id="rankingFilter"',
        'id="changeFilter"',
        'id="searchSector"',
        'onchange="filterSectorRanking()"',
        
        # TOPK统计区域
        'id="statsDays"',
        'id="topK"',
        'id="top-performers-result"',
        'onclick="loadTopPerformers()"',
        
        # 历史查询区域
        'id="historyStartDate"',
        'id="historyEndDate"',
        'id="historySector"',
        'id="sector-history-result"',
        'onclick="loadSectorHistory()"',
        
        # JavaScript函数
        'function initSectorAnalysis()',
        'function refreshSectorData()',
        'function loadSectorRanking()',
        'function renderSectorRanking()',
        'function toggleChartView()',
        'function filterSectorRanking()',
        'function loadTopPerformers()',
        'function loadSectorHistory()',
        
        # Chart.js引用
        'chart.js',
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ 缺少必要元素: {missing_elements}")
        return False
    
    print("✅ 板块分析模板检查通过")
    return True

def test_css_styles():
    """测试CSS样式实现"""
    print("=== 测试CSS样式 ===")
    
    css_path = "static/css/components.css"
    if not os.path.exists(css_path):
        print(f"❌ CSS文件不存在: {css_path}")
        return False
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必要的CSS类
    required_styles = [
        '.stock-item',
        '.history-item',
        '.sector-chart-container',
        '#sectorChart',
        '.status-indicator',
        '.loading-pulse',
        '.rank-badge',
        '.change-positive',
        '.change-negative',
        '.chart-toggle-btn',
        '.stats-card',
        '.action-buttons',
    ]
    
    missing_styles = []
    for style in required_styles:
        if style not in content:
            missing_styles.append(style)
    
    if missing_styles:
        print(f"❌ 缺少必要样式: {missing_styles}")
        return False
    
    print("✅ CSS样式检查通过")
    return True

def test_api_client_methods():
    """测试API客户端方法"""
    print("=== 测试API客户端方法 ===")
    
    api_path = "static/js/api.js"
    if not os.path.exists(api_path):
        print(f"❌ API文件不存在: {api_path}")
        return False
    
    with open(api_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必要的API方法
    required_methods = [
        # 股票池相关API
        'async getStockPool(',
        'async addToStockPool(',
        'async updateStockPool(',
        'async removeFromStockPool(',
        
        # 板块分析相关API
        'async getSectorRanking(',
        'async refreshSectorData(',
        'async getSectorHistory(',
        'async getTopPerformingSectors(',
    ]
    
    missing_methods = []
    for method in required_methods:
        if method not in content:
            missing_methods.append(method)
    
    if missing_methods:
        print(f"❌ 缺少必要API方法: {missing_methods}")
        return False
    
    print("✅ API客户端方法检查通过")
    return True

def test_javascript_functionality():
    """测试JavaScript功能实现"""
    print("=== 测试JavaScript功能 ===")
    
    # 检查股票池JavaScript
    stock_pool_path = "templates/stock_pool.html"
    with open(stock_pool_path, 'r', encoding='utf-8') as f:
        stock_pool_content = f.read()
    
    # 检查板块分析JavaScript
    sector_analysis_path = "templates/sector_analysis.html"
    with open(sector_analysis_path, 'r', encoding='utf-8') as f:
        sector_analysis_content = f.read()
    
    # 检查股票池关键功能
    stock_pool_functions = [
        'loadStockPool()',
        'renderStockPools()',
        'renderPoolSection(',
        'updatePoolStats()',
        'submitAddStock()',
        'editStock(',
        'moveStock(',
        'removeStock(',
        'setupFormValidation()',
    ]
    
    missing_stock_functions = []
    for func in stock_pool_functions:
        if func not in stock_pool_content:
            missing_stock_functions.append(func)
    
    if missing_stock_functions:
        print(f"❌ 股票池缺少JavaScript函数: {missing_stock_functions}")
        return False
    
    # 检查板块分析关键功能
    sector_functions = [
        'loadSectorRanking()',
        'renderSectorRanking()',
        'renderSectorTable()',
        'renderSectorChart()',
        'toggleChartView()',
        'filterSectorRanking()',
        'loadTopPerformers()',
        'renderTopPerformers(',
        'loadSectorHistory()',
        'renderSectorHistory(',
    ]
    
    missing_sector_functions = []
    for func in sector_functions:
        if func not in sector_analysis_content:
            missing_sector_functions.append(func)
    
    if missing_sector_functions:
        print(f"❌ 板块分析缺少JavaScript函数: {missing_sector_functions}")
        return False
    
    print("✅ JavaScript功能检查通过")
    return True

def test_responsive_design():
    """测试响应式设计"""
    print("=== 测试响应式设计 ===")
    
    css_path = "static/css/components.css"
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查媒体查询
    media_queries = [
        '@media (max-width: 768px)',
        '@media (max-width: 576px)',
    ]
    
    missing_queries = []
    for query in media_queries:
        if query not in content:
            missing_queries.append(query)
    
    if missing_queries:
        print(f"❌ 缺少媒体查询: {missing_queries}")
        return False
    
    print("✅ 响应式设计检查通过")
    return True

def test_requirements_coverage():
    """测试需求覆盖情况"""
    print("=== 测试需求覆盖情况 ===")
    
    requirements = {
        "3.1": "股票池管理界面 - 待观测池和待买入池",
        "3.2": "股票状态切换功能 - 移动和编辑功能",
        "8.1": "板块排名表格展示",
        "8.2": "板块数据刷新功能",
        "8.3": "TOPK板块统计展示",
        "8.4": "板块筛选和搜索功能",
    }
    
    # 检查股票池模板
    with open("templates/stock_pool.html", 'r', encoding='utf-8') as f:
        stock_pool_content = f.read()
    
    # 检查板块分析模板
    with open("templates/sector_analysis.html", 'r', encoding='utf-8') as f:
        sector_content = f.read()
    
    coverage_checks = {
        "3.1": 'id="watch-pool"' in stock_pool_content and 'id="buy-pool"' in stock_pool_content,
        "3.2": 'moveStock(' in stock_pool_content and 'editStock(' in stock_pool_content,
        "8.1": 'id="sector-ranking-tbody"' in sector_content,
        "8.2": 'refreshSectorData()' in sector_content,
        "8.3": 'id="top-performers-result"' in sector_content,
        "8.4": 'filterSectorRanking()' in sector_content,
    }
    
    failed_requirements = []
    for req_id, covered in coverage_checks.items():
        if not covered:
            failed_requirements.append(f"{req_id}: {requirements[req_id]}")
    
    if failed_requirements:
        print(f"❌ 未覆盖的需求: {failed_requirements}")
        return False
    
    print("✅ 需求覆盖检查通过")
    return True

def main():
    """主测试函数"""
    print("开始测试股票池和板块分析前端页面实现...")
    print("=" * 60)
    
    tests = [
        test_stock_pool_template,
        test_sector_analysis_template,
        test_css_styles,
        test_api_client_methods,
        test_javascript_functionality,
        test_responsive_design,
        test_requirements_coverage,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ 测试执行出错: {e}")
            print()
    
    print("=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！股票池和板块分析前端页面实现完成。")
        return True
    else:
        print("❌ 部分测试失败，请检查实现。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)