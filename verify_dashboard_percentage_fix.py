#!/usr/bin/env python3
"""
验证仪表板百分比显示修复
"""

import requests
import json
from datetime import datetime

def test_api_response():
    """测试API响应的数据格式"""
    
    print("=== 仪表板百分比显示修复验证 ===\n")
    
    try:
        # 测试总体统计API
        print("1. 测试总体统计API...")
        response = requests.get('http://localhost:5000/api/analytics/overall', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API响应成功")
            print(f"   状态码: {response.status_code}")
            
            # 检查关键字段
            total_return_rate = data.get('total_return_rate', 0)
            success_rate = data.get('success_rate', 0)
            
            print(f"\n📊 关键数据分析:")
            print(f"   total_return_rate: {total_return_rate} (原始值)")
            print(f"   success_rate: {success_rate} (原始值)")
            
            # 验证数据格式
            print(f"\n🔍 数据格式验证:")
            print(f"   total_return_rate 类型: {type(total_return_rate)}")
            print(f"   success_rate 类型: {type(success_rate)}")
            
            # 计算前端应该显示的值
            print(f"\n📱 前端显示计算:")
            print(f"   总收益率显示: {(total_return_rate * 100):.2f}%")
            print(f"   成功率显示: {(success_rate * 100):.1f}%")
            
            # 检查是否存在问题
            print(f"\n🚨 问题检查:")
            if total_return_rate < 0.001 and total_return_rate > 0:
                print(f"   ⚠️  总收益率可能过小: {total_return_rate}")
                print(f"   ⚠️  前端可能显示为: {(total_return_rate * 100):.2f}%")
            else:
                print(f"   ✅ 总收益率数值正常")
                
            if success_rate < 0.01 and success_rate > 0:
                print(f"   ⚠️  成功率可能过小: {success_rate}")
                print(f"   ⚠️  前端可能显示为: {(success_rate * 100):.1f}%")
            else:
                print(f"   ✅ 成功率数值正常")
            
            # 显示完整数据结构
            print(f"\n📋 完整API响应:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ API请求失败")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求错误: {e}")
        print("   请确保服务器正在运行 (python app.py)")
        
    except Exception as e:
        print(f"❌ 其他错误: {e}")

def test_percentage_logic():
    """测试百分比逻辑"""
    
    print(f"\n=== 百分比逻辑测试 ===\n")
    
    # 模拟后端返回的数据
    test_cases = [
        {"name": "正常情况", "total_return_rate": 0.02, "success_rate": 0.41},
        {"name": "负收益", "total_return_rate": -0.05, "success_rate": 0.25},
        {"name": "零值", "total_return_rate": 0.0, "success_rate": 0.0},
        {"name": "高收益", "total_return_rate": 0.15, "success_rate": 0.85},
        {"name": "小数值", "total_return_rate": 0.001, "success_rate": 0.05}
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['name']}:")
        
        total_return_rate = case['total_return_rate']
        success_rate = case['success_rate']
        
        # 旧逻辑（错误的）
        old_return_display = (total_return_rate / 100) * 100
        old_success_display = (success_rate / 100) * 100
        
        # 新逻辑（正确的）
        new_return_display = total_return_rate * 100
        new_success_display = success_rate * 100
        
        print(f"   后端返回: total_return_rate={total_return_rate}, success_rate={success_rate}")
        print(f"   旧逻辑显示: {old_return_display:.2f}%, {old_success_display:.1f}%")
        print(f"   新逻辑显示: {new_return_display:.2f}%, {new_success_display:.1f}%")
        
        # 检查是否修复了问题
        if abs(old_return_display - new_return_display) > 0.01:
            print(f"   🔧 修复效果: 总收益率从 {old_return_display:.2f}% 修正为 {new_return_display:.2f}%")
        
        if abs(old_success_display - new_success_display) > 0.1:
            print(f"   🔧 修复效果: 成功率从 {old_success_display:.1f}% 修正为 {new_success_display:.1f}%")
            
        print()

def test_frontend_formatters():
    """测试前端Formatters.percentage函数逻辑"""
    
    print(f"=== 前端Formatters.percentage测试 ===\n")
    
    # 模拟Formatters.percentage函数
    def formatters_percentage(value, decimals=2):
        if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
            return '--'
        try:
            return f"{float(value) * 100:.{decimals}f}%"
        except (ValueError, TypeError):
            return '--'
    
    test_values = [
        0.02,    # 2%
        0.41,    # 41%
        -0.05,   # -5%
        0.0,     # 0%
        1.5,     # 150%
        None,    # null
        '',      # 空字符串
        'invalid' # 无效值
    ]
    
    for value in test_values:
        result = formatters_percentage(value)
        print(f"   输入: {value} → 输出: {result}")

def generate_fix_summary():
    """生成修复总结"""
    
    print(f"\n=== 修复总结 ===\n")
    
    print("🔧 修复内容:")
    print("   1. static/js/dashboard.js")
    print("      - 移除总收益率的多余除法: (data.total_return_rate || 0) / 100 → data.total_return_rate || 0")
    print("      - 移除成功率的多余除法: (data.success_rate || 0) / 100 → data.success_rate || 0")
    print()
    print("   2. static/js/optimized-dashboard.js")
    print("      - 添加专门的百分比动画函数: animateValuePercentage()")
    print("      - 正确处理百分比值的动画效果")
    print()
    
    print("✅ 修复效果:")
    print("   - 总收益率: 0.02% → 2.00%")
    print("   - 成功率: 0.41% → 41.0%")
    print("   - 保持数据的正确性和一致性")
    print()
    
    print("🧪 测试方法:")
    print("   1. 运行服务器: python app.py")
    print("   2. 访问仪表板: http://localhost:5000/")
    print("   3. 检查总收益率和成功率显示")
    print("   4. 运行测试页面: http://localhost:5000/test_dashboard_percentage_fix.html")
    print()
    
    print("📝 注意事项:")
    print("   - 后端返回的是小数形式 (0.02 表示 2%)")
    print("   - 前端Formatters.percentage会自动乘以100并添加%符号")
    print("   - 不要在前端再次进行百分比转换")

if __name__ == "__main__":
    test_api_response()
    test_percentage_logic()
    test_frontend_formatters()
    generate_fix_summary()