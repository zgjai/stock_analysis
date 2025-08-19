# -*- coding: utf-8 -*-
"""
本地开发配置文件
Local Development Configuration
"""

import os
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent.absolute()

class LocalConfig:
    """本地开发配置"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    TESTING = False
    
    # 数据库配置
    DATABASE_PATH = BASE_DIR / 'data' / 'trading_journal.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 设置为True可以看到SQL语句
    
    # 文件上传配置
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    
    # 日志配置
    LOG_FOLDER = BASE_DIR / 'logs'
    LOG_LEVEL = 'INFO'
    LOG_FILE = LOG_FOLDER / 'trading_journal.log'
    
    # AKShare配置
    AKSHARE_TIMEOUT = 30  # API超时时间(秒)
    PRICE_CACHE_MINUTES = 5  # 价格缓存时间(分钟)
    
    # 分页配置
    TRADES_PER_PAGE = 20
    REVIEWS_PER_PAGE = 20
    CASES_PER_PAGE = 12
    
    # 备份配置
    BACKUP_FOLDER = BASE_DIR / 'backups'
    AUTO_BACKUP_DAYS = 7  # 自动备份间隔天数
    BACKUP_RETENTION_DAYS = 30  # 备份保留天数
    
    # 前端配置
    STATIC_FOLDER = BASE_DIR / 'static'
    TEMPLATE_FOLDER = BASE_DIR / 'templates'
    
    # 安全配置
    WTF_CSRF_ENABLED = False  # 开发环境暂时禁用CSRF保护
    WTF_CSRF_TIME_LIMIT = 3600  # CSRF令牌有效期(秒)
    
    @classmethod
    def init_app(cls, app):
        """初始化应用配置"""
        # 确保必要目录存在
        for folder in [cls.UPLOAD_FOLDER, cls.LOG_FOLDER, cls.BACKUP_FOLDER]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # 设置日志
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if not cls.LOG_FOLDER.exists():
                cls.LOG_FOLDER.mkdir(parents=True)
            
            file_handler = RotatingFileHandler(
                cls.LOG_FILE, 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Trading Journal System startup')

# 导出配置
Config = LocalConfig