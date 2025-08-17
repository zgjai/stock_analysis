"""
应用启动脚本
"""
import os
from app import create_app
from config import config

# 获取环境配置
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config[config_name])

if __name__ == '__main__':
    # 确保必要的目录存在
    config[config_name].init_app(app)
    
    # 启动应用
    port = int(os.environ.get('PORT', 5001))  # 改为5001端口
    print(f"应用将在端口 {port} 启动")
    print(f"Application will start on port {port}")
    print(f"访问地址: http://localhost:{port}")
    print(f"Access URL: http://localhost:{port}")
    
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=port
    )