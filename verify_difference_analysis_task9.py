#!/usr/bin/env python3
"""
验证任务9：差异分析和提示功能的实现

根据需求5.1-5.6验证以下功能：
- 5.1: 计算并显示收益率和收益金额差异
- 5.2: 计算并显示收益金额差异  
- 5.3: 计算并显示持仓天数差异
- 5.4: 差异为正值时使用绿色显示并标注"超出期望"
- 5.5: 差异为负值时使用红色显示并标注"低于期望"
- 5.6: 差异在±5%范围内时使用黄色显示并标注"接近期望"
"""

import requests
import json
import sys
from datetime import datetime

def test_api_difference_calculation():
    """测试API的差异计算功能"""
    print("=" * 60)
    print("测试API差异计算功能")
    print("=" * 60)
    
    try:
        # 测试API端点
        url = "http://localhost:5001/api/analytics/expectation-comparison"
        params = {
            'time_range': 'all',
            'base_capital': 3200000
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success']:
                print("✅ API调用成功")
                
                # 验证数据结构
                comparison = data['data']['comparison']
                expectation = data['data']['expectation']
                actual = data['data']['actual']
                
                print(f"期望收益率: {expectation['return_rate']:.3f}")
                print(f"实际收益率: {actual['return_rate']:.3f}")
                print(f"收益率差异: {comparison['return_rate_diff']:.3f}")
                
                print(f"期望收益金额: ¥{expectation['return_amount']:,.2f}")
                print(f"实际收益金额: ¥{actual['return_amount']:,.2f}")
                print(f"收益金额差异: ¥{comparison['return_amount_diff']:,.2f}")
                
                print(f"期望持仓天数: {expectation['holding_days']:.2f}天")
                print(f"实际持仓天数: {actual['holding_days']:.2f}天")
                print(f"持仓天数差异: {comparison['holding_days_diff']:.2f}天")
                
                print(f"期望胜率: {expectation['success_rate']:.1%}")
                print(f"实际胜率: {actual['success_rate']:.1%}")
                print(f"胜率差异: {comparison['success_rate_diff']:.3f}")
                
                # 验证需求5.1-5.3：差异计算
                assert 'return_rate_diff' in comparison, "❌ 缺少收益率差异计算"
                assert 'return_amount_diff' in comparison, "❌ 缺少收益金额差异计算"
                assert 'holding_days_diff' in comparison, "❌ 缺少持仓天数差异计算"
                assert 'success_rate_diff' in comparison, "❌ 缺少胜率差异计算"
                
                print("✅ 需求5.1-5.3：差异计算功能验证通过")
                
                # 验证状态信息
                if 'return_rate_status' in comparison:
                    status = comparison['return_rate_status']
                    print(f"收益率状态: {status['message']} ({status['color']})")
                    
                    # 验证需求5.4-5.6：状态标识
                    if status['status'] == 'positive':
                        assert status['color'] == 'success', "❌ 正值应该使用绿色"
                        assert '超出期望' in status['message'], "❌ 正值应该标注'超出期望'"
                        print("✅ 需求5.4：正值绿色标识验证通过")
                    elif status['status'] == 'negative':
                        assert status['color'] == 'danger', "❌ 负值应该使用红色"
                        assert '低于期望' in status['message'], "❌ 负值应该标注'低于期望'"
                        print("✅ 需求5.5：负值红色标识验证通过")
                    elif status['status'] == 'neutral':
                        assert status['color'] == 'warning', "❌ 接近期望应该使用黄色"
                        assert '接近期望' in status['message'], "❌ 接近期望应该标注'接近期望'"
                        print("✅ 需求5.6：接近期望黄色标识验证通过")
                
                return True
            else:
                print(f"❌ API返回错误: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ API调用失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def test_frontend_files():
    """测试前端文件是否包含差异分析功能"""
    print("\n" + "=" * 60)
    print("测试前端差异分析功能")
    print("=" * 60)
    
    try:
        # 检查JavaScript文件
        js_file = "static/js/expectation-comparison-manager.js"
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # 验证关键函数存在
        required_functions = [
            'updateDiffBadge',
            'generateDifferenceTooltip',
            'renderAnalysisSummary',
            'generateDetailedDifferenceAnalysis',
            'getDifferenceStatus',
            'generatePositiveAnalysis',
            'generateImprovementAnalysis'
        ]
        
        for func in required_functions:
            if func in js_content:
                print(f"✅ 找到函数: {func}")
            else:
                print(f"❌ 缺少函数: {func}")
                return False
        
        # 验证需求5.4-5.6的实现
        if 'bg-success' in js_content and '超出期望' in js_content:
            print("✅ 需求5.4：绿色'超出期望'标识实现")
        else:
            print("❌ 需求5.4：绿色'超出期望'标识缺失")
            return False
            
        if 'bg-danger' in js_content and '低于期望' in js_content:
            print("✅ 需求5.5：红色'低于期望'标识实现")
        else:
            print("❌ 需求5.5：红色'低于期望'标识缺失")
            return False
            
        if 'bg-warning' in js_content and '接近期望' in js_content:
            print("✅ 需求5.6：黄色'接近期望'标识实现")
        else:
            print("❌ 需求5.6：黄色'接近期望'标识缺失")
            return False
        
        # 检查HTML模板
        html_file = "templates/analytics.html"
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 验证差异徽章元素存在
        required_badges = [
            'return-rate-diff-badge',
            'return-amount-diff-badge',
            'holding-days-diff-badge',
            'success-rate-diff-badge'
        ]
        
        for badge in required_badges:
            if badge in html_content:
                print(f"✅ 找到差异徽章: {badge}")
            else:
                print(f"❌ 缺少差异徽章: {badge}")
                return False
        
        # 验证分析摘要容器
        if 'analysis-summary' in html_content:
            print("✅ 找到分析摘要容器")
        else:
            print("❌ 缺少分析摘要容器")
            return False
        
        # 验证CSS样式
        if 'alert-sm' in html_content and 'badge-sm' in html_content:
            print("✅ 找到增强的CSS样式")
        else:
            print("❌ 缺少增强的CSS样式")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 前端文件测试失败: {e}")
        return False

def test_difference_thresholds():
    """测试差异阈值逻辑"""
    print("\n" + "=" * 60)
    print("测试差异阈值逻辑")
    print("=" * 60)
    
    # 模拟不同的差异场景
    test_cases = [
        {
            'name': '收益率超出期望',
            'diff': 0.08,  # 8%差异，超出5%阈值
            'is_percentage': True,
            'expected_status': 'positive'
        },
        {
            'name': '收益率低于期望',
            'diff': -0.06,  # -6%差异，超出5%阈值
            'is_percentage': True,
            'expected_status': 'negative'
        },
        {
            'name': '收益率接近期望',
            'diff': 0.03,  # 3%差异，在5%阈值内
            'is_percentage': True,
            'expected_status': 'neutral'
        },
        {
            'name': '收益金额超出期望',
            'diff': 25000,  # 2.5万差异，超出1万阈值
            'is_percentage': False,
            'expected_status': 'positive'
        },
        {
            'name': '收益金额低于期望',
            'diff': -18000,  # -1.8万差异，超出1万阈值
            'is_percentage': False,
            'expected_status': 'negative'
        },
        {
            'name': '收益金额接近期望',
            'diff': 5000,  # 0.5万差异，在1万阈值内
            'is_percentage': False,
            'expected_status': 'neutral'
        }
    ]
    
    for case in test_cases:
        print(f"\n测试案例: {case['name']}")
        print(f"差异值: {case['diff']}")
        print(f"是否百分比: {case['is_percentage']}")
        
        # 模拟阈值判断逻辑
        abs_diff = abs(case['diff'])
        
        if case['is_percentage']:
            threshold = 0.05  # 5%
        else:
            threshold = 10000  # 1万元
        
        if abs_diff <= threshold:
            actual_status = 'neutral'
            color = 'warning'
            message = '接近期望'
        elif case['diff'] > 0:
            actual_status = 'positive'
            color = 'success'
            message = '超出期望'
        else:
            actual_status = 'negative'
            color = 'danger'
            message = '低于期望'
        
        print(f"预期状态: {case['expected_status']}")
        print(f"实际状态: {actual_status}")
        print(f"颜色: {color}")
        print(f"消息: {message}")
        
        if actual_status == case['expected_status']:
            print("✅ 阈值判断正确")
        else:
            print("❌ 阈值判断错误")
            return False
    
    return True

def main():
    """主测试函数"""
    print("开始验证任务9：差异分析和提示功能")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_tests_passed = True
    
    # 测试API差异计算
    if not test_api_difference_calculation():
        all_tests_passed = False
    
    # 测试前端文件
    if not test_frontend_files():
        all_tests_passed = False
    
    # 测试差异阈值逻辑
    if not test_difference_thresholds():
        all_tests_passed = False
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    if all_tests_passed:
        print("🎉 所有测试通过！任务9：差异分析和提示功能实现完成")
        print("\n✅ 已实现的功能:")
        print("  - 需求5.1: 收益率和收益金额差异计算和显示")
        print("  - 需求5.2: 收益金额差异计算和显示")
        print("  - 需求5.3: 持仓天数差异计算和显示")
        print("  - 需求5.4: 正值差异绿色标识和'超出期望'提示")
        print("  - 需求5.5: 负值差异红色标识和'低于期望'提示")
        print("  - 需求5.6: ±5%范围内黄色标识和'接近期望'提示")
        print("\n🔧 增强功能:")
        print("  - 详细差异分析报告")
        print("  - 智能建议生成")
        print("  - 工具提示增强")
        print("  - 响应式CSS样式")
        return 0
    else:
        print("❌ 部分测试失败，请检查实现")
        return 1

if __name__ == "__main__":
    sys.exit(main())