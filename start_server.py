#!/usr/bin/env python3
"""
简单的服务器启动脚本
"""
import os
import sys
from app import create_app

def main():
    # 设置端口，避免与macOS AirPlay冲突
    port = 8080
    
    print(f"启动股票交易记录系统...")
    print(f"端口: {port}")
    print(f"访问地址: http://localhost:{port}")
    print(f"按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        app = create_app()
        app.run(
            debug=True,
            host='127.0.0.1',
            port=port,
            use_reloader=False  # 避免重复启动
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()