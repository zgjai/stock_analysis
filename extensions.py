"""
Flask扩展初始化
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 初始化扩展实例
db = SQLAlchemy()
migrate = Migrate()