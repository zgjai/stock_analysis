#!/usr/bin/env python3
"""
启动测试服务器来验证历史交易修复
"""
import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import sqlalchemy
        print("✓ Flask和SQLAlchemy已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install flask sqlalchemy")
        return False

def start_server():
    """启动Flask服务器"""
    if not check_dependencies():
        return False
    
    # 检查主应用文件
    app_files = ['app.py', 'run.py', 'start.py']
    app_file = None
    
    for file in app_files:
        if os.path.exists(file):
            app_file = file
            break
    
    if not app_file:
        print("✗ 未找到Flask应用文件 (app.py, run.py, start.py)")
        return False
    
    print(f"✓ 找到应用文件: {app_file}")
    
    # 设置环境变量
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '1'
    
    try:
        print("🚀 启动Flask服务器...")
        print("📝 请在浏览器中访问: http://localhost:5000/historical-trades")
        print("🔧 或者打开测试页面: test_historical_trades_fixes.html")
        print("⏹️  按 Ctrl+C 停止服务器")
        
        # 启动服务器
        process = subprocess.Popen(
            [sys.executable, app_file],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 等待服务器启动
        time.sleep(3)
        
        # 尝试打开浏览器
        try:
            webbrowser.open('http://localhost:5000/historical-trades')
        except:
            pass
        
        # 输出服务器日志
        for line in process.stdout:
            print(line.rstrip())
            
    except KeyboardInterrupt:
        print("\n⏹️  服务器已停止")
        process.terminate()
        return True
    except Exception as e:
        print(f"✗ 启动服务器失败: {e}")
        return False

def show_test_instructions():
    """显示测试说明"""
    print("\n=== 测试说明 ===")
    print("1. 访问历史交易页面: http://localhost:5000/historical-trades")
    print("2. 检查统计卡片是否为横排布局")
    print("3. 检查平均收益率是否正确显示")
    print("4. 测试排序功能:")
    print("   - 选择不同的排序字段（收益率、持仓天数等）")
    print("   - 切换排序方向（升序/降序）")
    print("   - 点击'应用排序'按钮")
    print("5. 检查数字格式化是否使用千分位分隔符")
    print("6. 测试响应式布局（调整浏览器窗口大小）")
    print("\n=== 备用测试 ===")
    print("如果服务器无法启动，可以直接打开:")
    print("- test_historical_trades_fixes.html (静态UI测试)")
    print("- 运行: python test_historical_trades_sorting.py (API测试)")

if __name__ == "__main__":
    print("=== 历史交易修复测试服务器 ===\n")
    
    show_test_instructions()
    
    print("\n是否启动测试服务器? (y/n): ", end="")
    choice = input().lower().strip()
    
    if choice in ['y', 'yes', '']:
        start_server()
    else:
        print("测试服务器未启动。")
        print("您可以手动启动应用并访问历史交易页面进行测试。")