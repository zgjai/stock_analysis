#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票交易记录和复盘系统启动脚本
Stock Trading Journal System Startup Script
"""

import os
import sys
import subprocess
import sqlite3
import socket
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python版本: {sys.version}")

def check_dependencies():
    """检查依赖包"""
    try:
        import flask
        import sqlalchemy
        import akshare
        from PIL import Image
        print("✓ 所有依赖包已安装")
    except ImportError as e:
        print(f"错误: 缺少依赖包 {e}")
        print("请运行: pip install -r requirements.txt")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

def initialize_database():
    """初始化数据库"""
    db_path = Path("data/trading_journal.db")
    
    if not db_path.exists():
        print("正在初始化数据库...")
        print("Initializing database...")
        
        # 确保data目录存在
        db_path.parent.mkdir(exist_ok=True)
        
        # 运行数据库初始化脚本
        try:
            subprocess.run([sys.executable, "init_db.py"], check=True)
            print("✓ 数据库初始化完成")
        except subprocess.CalledProcessError:
            print("错误: 数据库初始化失败")
            print("Error: Database initialization failed")
            sys.exit(1)
    else:
        print("✓ 数据库已存在")

def check_directories():
    """检查必要的目录结构"""
    directories = [
        "data",
        "uploads", 
        "static/css",
        "static/js",
        "templates",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ 目录结构检查完成")

def check_port_available(port):
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def find_available_port(start_port=5001):
    """查找可用端口"""
    for port in range(start_port, start_port + 100):
        if check_port_available(port):
            return port
    return None

def start_application():
    """启动应用程序"""
    print("\n" + "="*50)
    print("启动股票交易记录和复盘系统")
    print("Starting Stock Trading Journal System")
    print("="*50)
    
    # 检查端口可用性
    default_port = int(os.environ.get('PORT', 5001))
    if not check_port_available(default_port):
        print(f"端口 {default_port} 被占用，正在查找可用端口...")
        print(f"Port {default_port} is in use, finding available port...")
        
        available_port = find_available_port(default_port + 1)
        if available_port:
            os.environ['PORT'] = str(available_port)
            print(f"找到可用端口: {available_port}")
            print(f"Found available port: {available_port}")
        else:
            print("错误: 无法找到可用端口")
            print("Error: Cannot find available port")
            sys.exit(1)
    
    # 设置环境变量
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    try:
        # 启动Flask应用
        subprocess.run([sys.executable, "run.py"], check=True)
    except KeyboardInterrupt:
        print("\n应用程序已停止")
        print("Application stopped")
    except subprocess.CalledProcessError:
        print("错误: 应用程序启动失败")
        print("Error: Application startup failed")
        sys.exit(1)

def main():
    """主函数"""
    print("股票交易记录和复盘系统 - 启动检查")
    print("Stock Trading Journal System - Startup Check")
    print("-" * 50)
    
    # 执行启动前检查
    check_python_version()
    check_dependencies()
    check_directories()
    initialize_database()
    
    print("\n所有检查通过，正在启动应用...")
    print("All checks passed, starting application...")
    
    # 启动应用
    start_application()

if __name__ == "__main__":
    main()