#!/usr/bin/env python3
"""
复盘和持仓管理前端页面测试脚本
"""

import requests
import json
import sys
from datetime import datetime

def test_review_page():
    """测试复盘页面的基本功能"""
    base_url = "http://localhost:5001"
    
    print("=== 复盘和持仓管理前端页面测试 ===\n")
    
    # 1. 测试页面访问
    print("1. 测试复盘页面访问...")
    try:
        response = requests.get(f"{base_url}/review")
        if response.status_code == 200:
            print("✓ 复盘页面访问成功")
            # 检查页面是否包含关键元素
            if "当前持仓" in response.text and "持仓策略提醒" in response.text:
                print("✓ 页面包含必要的UI元素")
            else:
                print("✗ 页面缺少关键UI元素")
        else:
            print(f"✗ 复盘页面访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 复盘页面访问异常: {e}")
    
    # 2. 测试持仓数据API
    print("\n2. 测试持仓数据API...")
    try:
        response = requests.get(f"{base_url}/api/holdings")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 持仓数据API调用成功，返回 {len(data.get('data', []))} 条记录")
        else:
            print(f"✗ 持仓数据API调用失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 持仓数据API调用异常: {e}")
    
    # 3. 测试持仓提醒API
    print("\n3. 测试持仓提醒API...")
    try:
        response = requests.get(f"{base_url}/api/holdings/alerts")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 持仓提醒API调用成功，返回 {len(data.get('data', []))} 条提醒")
        else:
            print(f"✗ 持仓提醒API调用失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 持仓提醒API调用异常: {e}")
    
    # 4. 测试复盘记录API
    print("\n4. 测试复盘记录API...")
    try:
        response = requests.get(f"{base_url}/api/reviews")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 复盘记录API调用成功，返回 {len(data.get('data', []))} 条记录")
        else:
            print(f"✗ 复盘记录API调用失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 复盘记录API调用异常: {e}")
    
    # 5. 测试创建复盘记录
    print("\n5. 测试创建复盘记录...")
    try:
        review_data = {
            "stock_code": "000001",
            "review_date": datetime.now().strftime("%Y-%m-%d"),
            "holding_days": 5,
            "price_up_score": 1,
            "bbi_score": 1,
            "volume_score": 0,
            "trend_score": 1,
            "j_score": 1,
            "total_score": 4,
            "analysis": "测试复盘分析内容",
            "decision": "hold",
            "reason": "技术指标良好，继续持有"
        }
        
        response = requests.post(f"{base_url}/api/reviews", json=review_data)
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                print("✓ 复盘记录创建成功")
                review_id = data.get('data', {}).get('id')
                if review_id:
                    print(f"✓ 复盘记录ID: {review_id}")
            else:
                print(f"✗ 复盘记录创建失败: {data.get('message', '未知错误')}")
        else:
            print(f"✗ 复盘记录创建失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 复盘记录创建异常: {e}")
    
    print("\n=== 测试完成 ===")

def test_ui_components():
    """测试UI组件的完整性"""
    base_url = "http://localhost:5001"
    
    print("\n=== UI组件测试 ===\n")
    
    try:
        response = requests.get(f"{base_url}/review")
        if response.status_code == 200:
            content = response.text
            
            # 检查关键UI组件
            ui_components = [
                ("持仓列表", "holdings-list"),
                ("持仓提醒", "holding-alerts"),
                ("复盘记录", "reviews-list"),
                ("复盘模态框", "reviewModal"),
                ("持仓天数编辑模态框", "holdingDaysModal"),
                ("快速复盘", "quick-review-stock"),
                ("评分复选框", "price-up-score"),
                ("总分显示", "total-score"),
                ("筛选功能", "review-date-filter")
            ]
            
            for name, element_id in ui_components:
                if element_id in content:
                    print(f"✓ {name} 组件存在")
                else:
                    print(f"✗ {name} 组件缺失")
            
            # 检查JavaScript函数
            js_functions = [
                "initReview",
                "loadHoldings",
                "loadHoldingAlerts",
                "loadReviews",
                "openReviewModal",
                "saveReview",
                "editHoldingDays",
                "calculateTotalScore"
            ]
            
            print("\nJavaScript函数检查:")
            for func in js_functions:
                if f"function {func}" in content or f"{func}(" in content:
                    print(f"✓ {func} 函数存在")
                else:
                    print(f"✗ {func} 函数缺失")
                    
        else:
            print(f"✗ 无法访问复盘页面，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"✗ UI组件测试异常: {e}")

if __name__ == "__main__":
    print("开始测试复盘和持仓管理前端页面...")
    print("请确保应用服务器在 http://localhost:5001 上运行\n")
    
    test_review_page()
    test_ui_components()
    
    print("\n测试完成！")