#!/usr/bin/env python3
"""
生产环境启动脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from config import ProductionConfig

def main():
    """主函数"""
    # 设置环境变量
    os.environ.setdefault('FLASK_ENV', 'production')
    
    # 创建应用
    app = create_app(ProductionConfig)
    
    # 获取配置
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    # 启动应用
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()