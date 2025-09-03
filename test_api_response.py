#!/usr/bin/env python3
"""
测试API响应，验证后端返回的数据格式
"""

import requests
import json

def test_analytics_api():
    """测试分析API的响应"""
    
    print("=== 测试分析API响应 ===\n")
    
    try:
        # 测试本地API
        url = "http://localhost:5001/api/analytics/overview"
        
        print(f"请求URL: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                analytics_data = data.get('data', {})
                
                print("\n=== API返回的关键数据 ===")
                print(f"总收益率 (total_return_rate): {analytics_data.get('total_return_rate')}")
                print(f"成功率 (success_rate): {analytics_data.get('success_rate')}")
                print(f"已清仓收益 (closed_profit): {analytics_data.get('closed_profit')}")
                print(f"持仓收益 (holding_profit): {analytics_data.get('holding_profit')}")
                
                # 验证数据格式
                total_return_rate = analytics_data.get('total_return_rate', 0)
                success_rate = analytics_data.get('success_rate', 0)
                
                print(f"\n=== 数据格式验证 ===")
                print(f"总收益率类型: {type(total_return_rate)}")
                print(f"总收益率值: {total_return_rate}")
                print(f"前端应显示: {total_return_rate * 100:.2f}%")
                
                print(f"\n成功率类型: {type(success_rate)}")
                print(f"成功率值: {success_rate}")
                print(f"前端应显示: {success_rate * 100:.1f}%")
                
                # 检查是否是预期的小数格式
                if 0 < total_return_rate < 1:
                    print("\n✓ 总收益率格式正确 (小数形式)")
                else:
                    print(f"\n✗ 总收益率格式异常: {total_return_rate}")
                
                if 0 < success_rate < 1:
                    print("✓ 成功率格式正确 (小数形式)")
                else:
                    print(f"✗ 成功率格式异常: {success_rate}")
                    
            else:
                print(f"API返回错误: {data.get('message')}")
        else:
            print(f"HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        print("请确保服务器正在运行在 http://localhost:5001")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == '__main__':
    test_analytics_api()