#!/usr/bin/env python3
"""
测试路由修复是否成功
"""
import requests
import time
import subprocess
import sys
import os
from threading import Thread

def start_app_in_background():
    """在后台启动应用"""
    try:
        # 设置端口环境变量
        os.environ['PORT'] = '5003'
        subprocess.run([sys.executable, 'run.py'], check=True)
    except:
        pass

def test_routes():
    """测试主要路由"""
    base_url = "http://localhost:5003"
    
    # 等待应用启动
    print("等待应用启动...")
    time.sleep(3)
    
    routes_to_test = [
        ('/', '首页'),
        ('/dashboard', '仪表板'),
        ('/trading-records', '交易记录'),
        ('/review', '复盘分析'),
        ('/stock-pool', '股票池'),
        ('/sector-analysis', '板块分析'),
        ('/cases', '案例管理'),
        ('/analytics', '统计分析'),
        ('/health', '健康检查')
    ]
    
    print(f"测试应用路由: {base_url}")
    print("-" * 50)
    
    success_count = 0
    total_count = len(routes_to_test)
    
    for route, name in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} ({route}): 正常")
                success_count += 1
            else:
                print(f"❌ {name} ({route}): HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} ({route}): 连接失败 - {e}")
    
    print("-" * 50)
    print(f"测试结果: {success_count}/{total_count} 路由正常")
    
    if success_count == total_count:
        print("🎉 所有路由测试通过！URL路由修复成功！")
        return True
    else:
        print("⚠️  部分路由测试失败，请检查应用状态")
        return False

if __name__ == "__main__":
    print("股票交易记录系统 - 路由修复验证")
    print("=" * 50)
    
    # 在后台启动应用
    app_thread = Thread(target=start_app_in_background, daemon=True)
    app_thread.start()
    
    # 测试路由
    success = test_routes()
    
    if success:
        print("\n✅ 路由修复验证完成！")
        print("现在可以正常访问应用了。")
        print("启动命令: python3 start.py")
    else:
        print("\n❌ 路由修复验证失败！")
        print("请检查应用配置和依赖。")
    
    sys.exit(0 if success else 1)