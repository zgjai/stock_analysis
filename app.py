"""
股票交易记录和复盘系统 - 主应用入口
"""
from flask import Flask
from config import Config
from extensions import db, migrate
from api import api_bp
from error_handlers import register_error_handlers

# 导入所有模型以确保它们被SQLAlchemy注册
from models import *

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化应用配置
    config_class.init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 注册独立的功能蓝图
    from api.sector_routes import sector_bp
    from api.case_routes import case_bp
    app.register_blueprint(sector_bp)
    app.register_blueprint(case_bp)
    
    # 注册前端路由
    from routes import frontend_bp
    app.register_blueprint(frontend_bp)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5002)