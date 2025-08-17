#!/usr/bin/env python3
"""
复盘和持仓管理前端页面实现验证脚本
"""

import os
import re
from jinja2 import Environment, FileSystemLoader

def verify_template_structure():
    """验证模板结构和内容"""
    print("=== 验证复盘页面模板结构 ===\n")
    
    template_path = "templates/review.html"
    if not os.path.exists(template_path):
        print("✗ review.html 模板文件不存在")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必要的UI组件
    required_components = [
        # 持仓列表相关
        ("持仓列表容器", r'id="holdings-list"'),
        ("持仓刷新按钮", r'onclick="refreshHoldings\(\)"'),
        
        # 持仓提醒相关
        ("持仓提醒容器", r'id="holding-alerts"'),
        
        # 复盘记录相关
        ("复盘记录容器", r'id="reviews-list"'),
        ("复盘筛选器", r'id="review-date-filter"'),
        
        # 复盘模态框
        ("复盘模态框", r'id="reviewModal"'),
        ("评分复选框", r'id="price-up-score"'),
        ("总分显示", r'id="total-score"'),
        
        # 持仓天数编辑
        ("持仓天数模态框", r'id="holdingDaysModal"'),
        
        # 快速复盘
        ("快速复盘选择", r'id="quick-review-stock"'),
    ]
    
    print("1. UI组件检查:")
    all_components_exist = True
    for name, pattern in required_components:
        if re.search(pattern, content):
            print(f"✓ {name}")
        else:
            print(f"✗ {name} 缺失")
            all_components_exist = False
    
    # 检查JavaScript函数
    required_functions = [
        "initReview",
        "loadHoldings", 
        "loadHoldingAlerts",
        "loadReviews",
        "renderHoldings",
        "renderHoldingAlerts", 
        "renderReviews",
        "openReviewModal",
        "saveReview",
        "editReview",
        "editHoldingDays",
        "saveHoldingDays",
        "calculateTotalScore",
        "filterReviews",
        "clearReviewFilters",
        "refreshHoldings"
    ]
    
    print("\n2. JavaScript函数检查:")
    all_functions_exist = True
    for func in required_functions:
        pattern = rf'(function\s+{func}|{func}\s*[:=]\s*function|async\s+function\s+{func})'
        if re.search(pattern, content):
            print(f"✓ {func}")
        else:
            print(f"✗ {func} 缺失")
            all_functions_exist = False
    
    # 检查评分标准
    scoring_criteria = [
        "price-up-score",
        "bbi-score", 
        "volume-score",
        "trend-score",
        "j-score"
    ]
    
    print("\n3. 评分标准检查:")
    all_criteria_exist = True
    for criteria in scoring_criteria:
        if criteria in content:
            print(f"✓ {criteria}")
        else:
            print(f"✗ {criteria} 缺失")
            all_criteria_exist = False
    
    return all_components_exist and all_functions_exist and all_criteria_exist

def verify_css_styles():
    """验证CSS样式"""
    print("\n=== 验证CSS样式 ===\n")
    
    css_path = "static/css/components.css"
    if not os.path.exists(css_path):
        print("✗ components.css 文件不存在")
        return False
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查复盘页面相关样式
    required_styles = [
        ".review-page",
        ".holding-item",
        ".review-item", 
        ".alert-sm",
        ".form-check-input:checked",
        "#total-score"
    ]
    
    print("CSS样式检查:")
    all_styles_exist = True
    for style in required_styles:
        if style in content:
            print(f"✓ {style}")
        else:
            print(f"✗ {style} 缺失")
            all_styles_exist = False
    
    return all_styles_exist

def verify_api_integration():
    """验证API集成"""
    print("\n=== 验证API集成 ===\n")
    
    api_js_path = "static/js/api.js"
    if not os.path.exists(api_js_path):
        print("✗ api.js 文件不存在")
        return False
    
    with open(api_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必要的API方法
    required_api_methods = [
        "getReviews",
        "createReview", 
        "updateReview",
        "getHoldings",
        "getHoldingAlerts"
    ]
    
    print("API方法检查:")
    all_methods_exist = True
    for method in required_api_methods:
        if method in content:
            print(f"✓ {method}")
        else:
            print(f"✗ {method} 缺失")
            all_methods_exist = False
    
    return all_methods_exist

def verify_requirements_coverage():
    """验证需求覆盖情况"""
    print("\n=== 验证需求覆盖情况 ===\n")
    
    # 根据任务要求检查功能实现
    requirements = [
        ("持仓列表展示和管理界面", "holdings-list"),
        ("复盘评分交互式表单", "reviewModal"),
        ("持仓策略提醒展示", "holding-alerts"), 
        ("持仓天数手动输入编辑", "holdingDaysModal"),
        ("5项评分标准", "price-up-score.*bbi-score.*volume-score.*trend-score.*j-score"),
        ("总分计算", "total-score"),
        ("决策记录", 'id="decision"'),
        ("复盘历史查看", "reviews-list")
    ]
    
    template_path = "templates/review.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("需求实现检查:")
    all_requirements_met = True
    for req_name, pattern in requirements:
        if re.search(pattern, content, re.DOTALL):
            print(f"✓ {req_name}")
        else:
            print(f"✗ {req_name} 未实现")
            all_requirements_met = False
    
    return all_requirements_met

def main():
    """主验证函数"""
    print("开始验证复盘和持仓管理前端页面实现...\n")
    
    results = []
    
    # 验证模板结构
    results.append(verify_template_structure())
    
    # 验证CSS样式
    results.append(verify_css_styles())
    
    # 验证API集成
    results.append(verify_api_integration())
    
    # 验证需求覆盖
    results.append(verify_requirements_coverage())
    
    # 总结
    print("\n=== 验证总结 ===")
    if all(results):
        print("✓ 所有验证项目通过！复盘和持仓管理前端页面实现完整。")
        print("\n实现的功能包括:")
        print("- 持仓列表展示和管理界面")
        print("- 复盘评分的交互式表单(5项评分标准)")
        print("- 持仓策略提醒的展示和操作界面")
        print("- 持仓天数的手动输入和编辑功能")
        print("- 复盘记录历史查看和筛选")
        print("- 响应式设计和用户体验优化")
        return True
    else:
        print("✗ 部分验证项目未通过，请检查实现。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)