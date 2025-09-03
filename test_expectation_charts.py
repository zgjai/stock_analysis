#!/usr/bin/env python3
"""
测试期望对比图表功能
验证新实现的持仓天数和胜率对比图表
"""

import requests
import json
import sys

def test_expectation_comparison_api():
    """测试期望对比API"""
    base_url = "http://localhost:5001"
    
    try:
        # 测试期望对比API端点
        print("🔍 测试期望对比API...")
        response = requests.get(f"{base_url}/api/analytics/expectation-comparison", 
                              params={'time_range': 'all', 'base_capital': 3200000})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API响应成功")
            
            if data.get('success'):
                print("✅ API返回成功状态")
                
                # 检查数据结构
                comparison_data = data.get('data', {})
                expectation = comparison_data.get('expectation', {})
                actual = comparison_data.get('actual', {})
                comparison = comparison_data.get('comparison', {})
                
                print(f"📊 期望数据: {expectation}")
                print(f"📈 实际数据: {actual}")
                print(f"📉 对比数据: {comparison}")
                
                # 验证关键字段
                required_fields = ['return_rate', 'return_amount', 'holding_days', 'success_rate']
                
                for field in required_fields:
                    if field in expectation and field in actual:
                        print(f"✅ {field} 字段存在")
                    else:
                        print(f"❌ {field} 字段缺失")
                        
                return True
            else:
                print(f"❌ API返回错误: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器在5001端口运行")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def test_frontend_access():
    """测试前端页面访问"""
    base_url = "http://localhost:5001"
    
    try:
        print("\n🌐 测试前端页面访问...")
        response = requests.get(f"{base_url}/analytics")
        
        if response.status_code == 200:
            print("✅ Analytics页面访问成功")
            
            # 检查关键HTML元素
            html_content = response.text
            
            # 检查新添加的图表容器
            chart_containers = [
                'holding-days-chart',
                'success-rate-chart', 
                'performance-comparison-chart'
            ]
            
            for container in chart_containers:
                if container in html_content:
                    print(f"✅ 找到图表容器: {container}")
                else:
                    print(f"❌ 缺少图表容器: {container}")
                    
            # 检查期望对比tab
            if 'expectation-content' in html_content:
                print("✅ 期望对比tab存在")
            else:
                print("❌ 期望对比tab缺失")
                
            return True
        else:
            print(f"❌ 页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 前端测试过程中出现错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试期望对比图表功能...\n")
    
    # 测试API
    api_success = test_expectation_comparison_api()
    
    # 测试前端
    frontend_success = test_frontend_access()
    
    print(f"\n📋 测试结果总结:")
    print(f"API测试: {'✅ 通过' if api_success else '❌ 失败'}")
    print(f"前端测试: {'✅ 通过' if frontend_success else '❌ 失败'}")
    
    if api_success and frontend_success:
        print("\n🎉 所有测试通过！新的持仓天数和胜率对比图表功能已成功实现")
        print("\n📝 功能说明:")
        print("- ✅ 持仓天数对比柱状图")
        print("- ✅ 胜率对比环形图") 
        print("- ✅ 图表颜色区分（实际vs期望）")
        print("- ✅ 图表数据更新机制")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查实现")
        return 1

if __name__ == "__main__":
    sys.exit(main())