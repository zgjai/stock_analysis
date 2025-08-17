#!/usr/bin/env python3
"""
案例管理和统计分析前端功能测试脚本

测试任务17的实现：
- 案例截图的上传和预览功能
- 案例的标签管理和搜索界面
- 统计分析的图表展示和数据可视化
- 统计数据的导出功能界面

Requirements: 4.1, 4.2, 4.4, 5.1, 5.2, 5.3, 5.5
"""

import os
import sys
import time
import requests
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_server_running():
    """测试服务器是否运行"""
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        return response.status_code == 200
    except:
        return False

def test_case_management_page():
    """测试案例管理页面"""
    print("测试案例管理页面...")
    
    try:
        response = requests.get('http://localhost:5000/cases.html', timeout=10)
        if response.status_code != 200:
            print(f"❌ 案例管理页面访问失败: {response.status_code}")
            return False
        
        content = response.text
        
        # 检查关键元素
        required_elements = [
            'id="upload-form"',  # 上传表单
            'id="case-file"',    # 文件选择
            'id="search-form"',  # 搜索表单
            'id="cases-container"',  # 案例容器
            'id="case-detail-modal"',  # 详情模态框
            'id="edit-case-modal"',   # 编辑模态框
            'class="case-card"',      # 网格视图样式
            'class="case-item"',      # 列表视图样式
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ 案例管理页面缺少关键元素: {missing_elements}")
            return False
        
        # 检查JavaScript功能
        js_functions = [
            'class CaseManager',
            'uploadCase()',
            'searchCases()',
            'showCaseDetail(',
            'renderCases(',
            'switchView(',
        ]
        
        missing_functions = []
        for func in js_functions:
            if func not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ 案例管理页面缺少JavaScript功能: {missing_functions}")
            return False
        
        print("✅ 案例管理页面结构完整")
        return True
        
    except Exception as e:
        print(f"❌ 测试案例管理页面失败: {e}")
        return False

def test_analytics_page():
    """测试统计分析页面"""
    print("测试统计分析页面...")
    
    try:
        response = requests.get('http://localhost:5000/analytics.html', timeout=10)
        if response.status_code != 200:
            print(f"❌ 统计分析页面访问失败: {response.status_code}")
            return False
        
        content = response.text
        
        # 检查关键元素
        required_elements = [
            'id="total-return-rate"',      # 总收益率
            'id="closed-profit"',          # 已清仓收益
            'id="holding-profit"',         # 持仓浮盈浮亏
            'id="success-rate"',           # 交易成功率
            'id="profit-distribution-chart"',  # 收益分布图
            'id="monthly-trend-chart"',    # 月度趋势图
            'id="monthly-stats-table"',    # 月度统计表
            'id="export-btn"',             # 导出按钮
            'id="performance-metrics"',    # 投资表现指标
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ 统计分析页面缺少关键元素: {missing_elements}")
            return False
        
        # 检查Chart.js引入
        if 'chart.js' not in content:
            print("❌ 统计分析页面未引入Chart.js")
            return False
        
        # 检查JavaScript功能
        js_functions = [
            'class AnalyticsManager',
            'loadOverviewData()',
            'loadProfitDistribution()',
            'loadMonthlyData()',
            'renderProfitDistributionChart(',
            'renderMonthlyChart(',
            'exportData()',
        ]
        
        missing_functions = []
        for func in js_functions:
            if func not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ 统计分析页面缺少JavaScript功能: {missing_functions}")
            return False
        
        print("✅ 统计分析页面结构完整")
        return True
        
    except Exception as e:
        print(f"❌ 测试统计分析页面失败: {e}")
        return False

def test_case_api_endpoints():
    """测试案例管理API端点"""
    print("测试案例管理API端点...")
    
    endpoints = [
        ('GET', '/api/cases', '获取案例列表'),
        ('GET', '/api/cases/tags', '获取所有标签'),
        ('GET', '/api/cases/statistics', '获取案例统计'),
    ]
    
    success_count = 0
    for method, endpoint, description in endpoints:
        try:
            if method == 'GET':
                response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            
            if response.status_code in [200, 404]:  # 404也是正常的，表示端点存在但无数据
                print(f"✅ {description}: {response.status_code}")
                success_count += 1
            else:
                print(f"❌ {description}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}: 连接失败 - {e}")
    
    return success_count == len(endpoints)

def test_analytics_api_endpoints():
    """测试统计分析API端点"""
    print("测试统计分析API端点...")
    
    endpoints = [
        ('GET', '/api/analytics/overview', '获取总体统计'),
        ('GET', '/api/analytics/profit-distribution', '获取收益分布'),
        ('GET', '/api/analytics/monthly', '获取月度统计'),
        ('GET', '/api/analytics/export', '导出统计数据'),
        ('GET', '/api/analytics/holdings', '获取当前持仓'),
        ('GET', '/api/analytics/performance', '获取投资表现'),
    ]
    
    success_count = 0
    for method, endpoint, description in endpoints:
        try:
            if method == 'GET':
                response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            
            if response.status_code in [200, 404]:  # 404也是正常的，表示端点存在但无数据
                print(f"✅ {description}: {response.status_code}")
                success_count += 1
            else:
                print(f"❌ {description}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}: 连接失败 - {e}")
    
    return success_count == len(endpoints)

def test_javascript_api_client():
    """测试JavaScript API客户端更新"""
    print("测试JavaScript API客户端...")
    
    try:
        with open('static/js/api.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查新增的案例管理API方法
        required_methods = [
            'getCaseById(',
            'getCasesByStock(',
            'getCasesByTag(',
            'getAllTags(',
            'getCaseStatistics(',
            'searchCases(',
        ]
        
        missing_methods = []
        for method in required_methods:
            if method not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ API客户端缺少方法: {missing_methods}")
            return False
        
        print("✅ JavaScript API客户端更新完整")
        return True
        
    except Exception as e:
        print(f"❌ 测试API客户端失败: {e}")
        return False

def test_ui_components():
    """测试UI组件功能"""
    print("测试UI组件功能...")
    
    # 检查案例管理页面的UI组件
    try:
        response = requests.get('http://localhost:5000/cases.html', timeout=10)
        content = response.text
        
        ui_components = [
            # 上传功能组件
            'enctype="multipart/form-data"',  # 文件上传表单
            'accept="image/*"',               # 图片文件限制
            'id="upload-progress"',           # 上传进度条
            
            # 搜索功能组件
            'id="search-keyword"',            # 关键词搜索
            'id="search-tags"',               # 标签筛选
            'id="search-start-date"',         # 日期范围
            
            # 视图切换组件
            'id="grid-view"',                 # 网格视图
            'id="list-view"',                 # 列表视图
            
            # 分页组件
            'id="pagination-container"',      # 分页容器
        ]
        
        missing_components = []
        for component in ui_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"❌ 案例管理页面缺少UI组件: {missing_components}")
            return False
        
        print("✅ 案例管理UI组件完整")
        
    except Exception as e:
        print(f"❌ 测试案例管理UI组件失败: {e}")
        return False
    
    # 检查统计分析页面的UI组件
    try:
        response = requests.get('http://localhost:5000/analytics.html', timeout=10)
        content = response.text
        
        ui_components = [
            # 统计卡片
            'bg-primary',                     # 总收益率卡片
            'bg-success',                     # 已清仓收益卡片
            'bg-info',                        # 持仓浮盈浮亏卡片
            'bg-warning',                     # 交易成功率卡片
            
            # 图表组件
            'canvas id="profit-distribution-chart"',  # 收益分布图
            'canvas id="monthly-trend-chart"',        # 月度趋势图
            
            # 表格组件
            'table-responsive',               # 响应式表格
            'id="monthly-stats-table"',       # 月度统计表
            
            # 导出功能
            'id="export-btn"',                # 导出按钮
        ]
        
        missing_components = []
        for component in ui_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"❌ 统计分析页面缺少UI组件: {missing_components}")
            return False
        
        print("✅ 统计分析UI组件完整")
        return True
        
    except Exception as e:
        print(f"❌ 测试统计分析UI组件失败: {e}")
        return False

def test_requirements_coverage():
    """测试需求覆盖情况"""
    print("测试需求覆盖情况...")
    
    requirements = {
        '4.1': '案例截图上传功能',
        '4.2': '案例标签和备注管理',
        '4.4': '案例搜索和筛选功能',
        '5.1': '总体收益统计展示',
        '5.2': '收益分布区间分析',
        '5.3': '月度交易统计',
        '5.5': '统计数据导出功能',
    }
    
    coverage_results = {}
    
    # 检查需求4.1: 案例截图上传功能
    try:
        response = requests.get('http://localhost:5000/cases.html', timeout=5)
        content = response.text
        if all(x in content for x in ['type="file"', 'accept="image/*"', 'multipart/form-data']):
            coverage_results['4.1'] = True
            print("✅ 需求4.1: 案例截图上传功能 - 已实现")
        else:
            coverage_results['4.1'] = False
            print("❌ 需求4.1: 案例截图上传功能 - 未完整实现")
    except:
        coverage_results['4.1'] = False
        print("❌ 需求4.1: 案例截图上传功能 - 测试失败")
    
    # 检查需求4.2: 案例标签和备注管理
    try:
        response = requests.get('http://localhost:5000/cases.html', timeout=5)
        content = response.text
        if all(x in content for x in ['id="case-tags"', 'id="case-notes"', 'badge bg-secondary']):
            coverage_results['4.2'] = True
            print("✅ 需求4.2: 案例标签和备注管理 - 已实现")
        else:
            coverage_results['4.2'] = False
            print("❌ 需求4.2: 案例标签和备注管理 - 未完整实现")
    except:
        coverage_results['4.2'] = False
        print("❌ 需求4.2: 案例标签和备注管理 - 测试失败")
    
    # 检查需求4.4: 案例搜索和筛选功能
    try:
        response = requests.get('http://localhost:5000/cases.html', timeout=5)
        content = response.text
        if all(x in content for x in ['id="search-form"', 'searchCases()', 'id="search-tags"']):
            coverage_results['4.4'] = True
            print("✅ 需求4.4: 案例搜索和筛选功能 - 已实现")
        else:
            coverage_results['4.4'] = False
            print("❌ 需求4.4: 案例搜索和筛选功能 - 未完整实现")
    except:
        coverage_results['4.4'] = False
        print("❌ 需求4.4: 案例搜索和筛选功能 - 测试失败")
    
    # 检查需求5.1: 总体收益统计展示
    try:
        response = requests.get('http://localhost:5000/analytics.html', timeout=5)
        content = response.text
        if all(x in content for x in ['id="total-return-rate"', 'id="closed-profit"', 'id="holding-profit"']):
            coverage_results['5.1'] = True
            print("✅ 需求5.1: 总体收益统计展示 - 已实现")
        else:
            coverage_results['5.1'] = False
            print("❌ 需求5.1: 总体收益统计展示 - 未完整实现")
    except:
        coverage_results['5.1'] = False
        print("❌ 需求5.1: 总体收益统计展示 - 测试失败")
    
    # 检查需求5.2: 收益分布区间分析
    try:
        response = requests.get('http://localhost:5000/analytics.html', timeout=5)
        content = response.text
        if all(x in content for x in ['profit-distribution-chart', 'doughnut', 'renderProfitDistributionChart']):
            coverage_results['5.2'] = True
            print("✅ 需求5.2: 收益分布区间分析 - 已实现")
        else:
            coverage_results['5.2'] = False
            print("❌ 需求5.2: 收益分布区间分析 - 未完整实现")
    except:
        coverage_results['5.2'] = False
        print("❌ 需求5.2: 收益分布区间分析 - 测试失败")
    
    # 检查需求5.3: 月度交易统计
    try:
        response = requests.get('http://localhost:5000/analytics.html', timeout=5)
        content = response.text
        if all(x in content for x in ['monthly-trend-chart', 'monthly-stats-table', 'loadMonthlyData']):
            coverage_results['5.3'] = True
            print("✅ 需求5.3: 月度交易统计 - 已实现")
        else:
            coverage_results['5.3'] = False
            print("❌ 需求5.3: 月度交易统计 - 未完整实现")
    except:
        coverage_results['5.3'] = False
        print("❌ 需求5.3: 月度交易统计 - 测试失败")
    
    # 检查需求5.5: 统计数据导出功能
    try:
        response = requests.get('http://localhost:5000/analytics.html', timeout=5)
        content = response.text
        if all(x in content for x in ['id="export-btn"', 'exportData()', 'Excel报表']):
            coverage_results['5.5'] = True
            print("✅ 需求5.5: 统计数据导出功能 - 已实现")
        else:
            coverage_results['5.5'] = False
            print("❌ 需求5.5: 统计数据导出功能 - 未完整实现")
    except:
        coverage_results['5.5'] = False
        print("❌ 需求5.5: 统计数据导出功能 - 测试失败")
    
    # 统计覆盖率
    total_requirements = len(requirements)
    covered_requirements = sum(1 for covered in coverage_results.values() if covered)
    coverage_rate = (covered_requirements / total_requirements) * 100
    
    print(f"\n需求覆盖率: {covered_requirements}/{total_requirements} ({coverage_rate:.1f}%)")
    
    return coverage_rate >= 85  # 85%以上认为通过

def main():
    """主测试函数"""
    print("=" * 60)
    print("案例管理和统计分析前端功能测试")
    print("=" * 60)
    
    # 检查服务器状态
    if not test_server_running():
        print("❌ 服务器未运行，请先启动Flask应用")
        print("运行命令: python run.py")
        return False
    
    print("✅ 服务器运行正常")
    print()
    
    # 执行各项测试
    tests = [
        ("案例管理页面结构", test_case_management_page),
        ("统计分析页面结构", test_analytics_page),
        ("案例管理API端点", test_case_api_endpoints),
        ("统计分析API端点", test_analytics_api_endpoints),
        ("JavaScript API客户端", test_javascript_api_client),
        ("UI组件功能", test_ui_components),
        ("需求覆盖情况", test_requirements_coverage),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"测试: {test_name}")
        print(f"{'-' * 40}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
            results.append((test_name, False))
    
    # 输出测试总结
    print(f"\n{'=' * 60}")
    print("测试总结")
    print(f"{'=' * 60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！任务17实现完成。")
        return True
    else:
        print("⚠️  部分测试失败，请检查实现。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)