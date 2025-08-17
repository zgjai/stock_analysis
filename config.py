"""
应用配置文件
"""
import os
from pathlib import Path

basedir = Path(__file__).parent.absolute()

class Config:
    """基础配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{basedir / "data" / "trading_journal.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = basedir / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # 允许的图片格式
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # AKShare配置
    AKSHARE_TIMEOUT = 30  # API超时时间（秒）
    
    # 分页配置
    ITEMS_PER_PAGE = 20
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建必要的目录
        data_dir = basedir / 'data'
        upload_dir = basedir / 'uploads'
        
        data_dir.mkdir(exist_ok=True)
        upload_dir.mkdir(exist_ok=True)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}