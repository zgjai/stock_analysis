#!/usr/bin/env python3
"""
测试仪表板修复
"""
import requests
import time
import json

def test_dashboard_apis():
    """测试仪表板相关的API"""
    base_url = "http://localhost:5001"
    
    apis_to_test = [
        "/health",
        "/api/analytics/overview", 
        "/api/trades?limit=5&order=desc",
        "/api/holdings/alerts",
        "/api/analytics/monthly",
        "/api/analytics/profit-distribution"
    ]
    
    print("测试仪表板API...")
    print("=" * 50)
    
    for api in apis_to_test:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{api}", timeout=10)
            end_time = time.time()
            
            print(f"✓ {api}")
            print(f"  状态码: {response.status_code}")
            print(f"  响应时间: {(end_time - start_time)*1000:.2f}ms")
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data:
                    print(f"  成功: {data['success']}")
                if 'message' in data:
                    print(f"  消息: {data['message']}")
            else:
                print(f"  错误: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"✗ {api} - 超时")
        except requests.exceptions.ConnectionError:
            print(f"✗ {api} - 连接失败")
        except Exception as e:
            print(f"✗ {api} - 错误: {str(e)}")
        
        print()

def test_dashboard_page():
    """测试仪表板页面加载"""
    try:
        print("测试仪表板页面...")
        response = requests.get("http://localhost:5001/dashboard", timeout=10)
        
        if response.status_code == 200:
            print("✓ 仪表板页面加载成功")
            
            # 检查关键元素
            content = response.text
            checks = [
                ('loadingModal', 'id="loadingModal"' in content),
                ('dashboard.js', 'dashboard.js' in content),
                ('api.js', 'api.js' in content),
                ('Chart.js', 'chart.min.js' in content),
                ('Bootstrap', 'bootstrap' in content)
            ]
            
            for name, check in checks:
                status = "✓" if check else "✗"
                print(f"  {status} {name}: {'已包含' if check else '未找到'}")
                
        else:
            print(f"✗ 仪表板页面加载失败: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 测试仪表板页面失败: {str(e)}")

if __name__ == "__main__":
    print("仪表板修复测试")
    print("=" * 50)
    
    # 测试API
    test_dashboard_apis()
    
    print("\n" + "=" * 50)
    
    # 测试页面
    test_dashboard_page()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("\n建议:")
    print("1. 如果所有API都正常，但页面仍然卡在加载状态，请检查浏览器控制台的JavaScript错误")
    print("2. 确保网络连接正常，CDN资源能够正常加载")
    print("3. 尝试清除浏览器缓存后重新加载页面")
    print("4. 检查浏览器是否阻止了某些JavaScript执行")