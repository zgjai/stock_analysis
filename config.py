"""
应用配置文件
"""
import os
from pathlib import Path

basedir = Path(__file__).parent.absolute()

# 尝试加载环境变量（如果python-dotenv可用）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv未安装，跳过
    pass

class Config:
    """基础配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{basedir / "data" / "trading_journal.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据库引擎选项
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('SQLALCHEMY_ENGINE_OPTIONS_POOL_SIZE', 10)),
        'pool_recycle': int(os.environ.get('SQLALCHEMY_ENGINE_OPTIONS_POOL_RECYCLE', 3600)),
        'pool_pre_ping': os.environ.get('SQLALCHEMY_ENGINE_OPTIONS_POOL_PRE_PING', 'true').lower() == 'true'
    }
    
    # 文件上传配置
    UPLOAD_FOLDER = Path(os.environ.get('UPLOAD_FOLDER', basedir / 'uploads'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max file size
    
    # 允许的图片格式
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif').split(','))
    
    # 历史交易记录配置
    REVIEW_IMAGES_UPLOAD_FOLDER = Path(os.environ.get('REVIEW_IMAGES_UPLOAD_FOLDER', 
                                                     basedir / 'uploads' / 'reviews' / 'images'))
    REVIEW_IMAGES_MAX_SIZE = int(os.environ.get('REVIEW_IMAGES_MAX_SIZE', 5 * 1024 * 1024))  # 5MB per image
    REVIEW_IMAGES_MAX_COUNT = int(os.environ.get('REVIEW_IMAGES_MAX_COUNT', 10))  # Maximum images per review
    
    # AKShare配置
    AKSHARE_TIMEOUT = int(os.environ.get('AKSHARE_TIMEOUT', 30))  # API超时时间（秒）
    AKSHARE_RETRY_COUNT = int(os.environ.get('AKSHARE_RETRY_COUNT', 3))
    AKSHARE_CACHE_TIMEOUT = int(os.environ.get('AKSHARE_CACHE_TIMEOUT', 300))  # 5 minutes
    
    # 分页配置
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))
    MAX_ITEMS_PER_PAGE = int(os.environ.get('MAX_ITEMS_PER_PAGE', 100))
    
    # 安全配置
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'true').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = int(os.environ.get('WTF_CSRF_TIME_LIMIT', 3600))
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    LOG_MAX_SIZE = int(os.environ.get('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # 缓存配置
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    
    # 监控配置
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'false').lower() == 'true'
    METRICS_PORT = int(os.environ.get('METRICS_PORT', 9090))
    
    # 备份配置
    BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'false').lower() == 'true'
    BACKUP_SCHEDULE = os.environ.get('BACKUP_SCHEDULE', '0 2 * * *')  # Daily at 2 AM
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 30))
    BACKUP_LOCATION = Path(os.environ.get('BACKUP_LOCATION', basedir / 'backups'))
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    
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

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    REVIEW_IMAGES_UPLOAD_FOLDER = '/tmp/test_uploads'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 生产环境特定配置
    SQLALCHEMY_ECHO = False
    
    # 安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 强制HTTPS
    PREFERRED_URL_SCHEME = 'https'
    
    @classmethod
    def init_app(cls, app):
        """生产环境初始化"""
        super().init_app(app)
        
        # 配置日志
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            # 创建日志目录
            log_dir = Path(app.config['LOG_FILE']).parent
            log_dir.mkdir(exist_ok=True)
            
            # 配置文件日志处理器
            file_handler = RotatingFileHandler(
                app.config['LOG_FILE'],
                maxBytes=app.config['LOG_MAX_SIZE'],
                backupCount=app.config['LOG_BACKUP_COUNT']
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
            app.logger.info('Historical Trading Records startup')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}