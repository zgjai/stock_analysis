"""
pytest配置文件
"""
import pytest
import tempfile
import os
from flask import Flask
from extensions import db
from models import *  # 导入所有模型


@pytest.fixture(scope='session')
def app():
    """创建测试应用"""
    app = Flask(__name__)
    
    # 使用临时数据库文件
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    # 初始化扩展
    db.init_app(app)
    
    # 注册API蓝图
    from api import api_bp
    from api.sector_routes import sector_bp
    from api.case_routes import case_bp
    from error_handlers import register_error_handlers
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(sector_bp)
    app.register_blueprint(case_bp)
    register_error_handlers(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        yield app
        
        # 清理
        db.drop_all()
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """创建数据库会话"""
    with app.app_context():
        # 清理所有表数据
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        yield db.session
        db.session.rollback()


@pytest.fixture
def sample_trade_data():
    """示例交易记录数据"""
    from datetime import datetime
    return {
        'stock_code': '000001',
        'stock_name': '平安银行',
        'trade_type': 'buy',
        'price': 12.50,
        'quantity': 1000,
        'trade_date': datetime(2024, 1, 15, 9, 30, 0),
        'reason': '少妇B1战法',
        'notes': '测试买入',
        'stop_loss_price': 11.25,
        'take_profit_ratio': 0.15,
        'sell_ratio': 0.5
    }


@pytest.fixture
def sample_review_data():
    """示例复盘记录数据"""
    from datetime import date
    return {
        'stock_code': '000001',
        'review_date': date(2024, 1, 16),
        'price_up_score': 1,
        'bbi_score': 1,
        'volume_score': 0,
        'trend_score': 1,
        'j_score': 1,
        'analysis': '整体表现良好',
        'decision': 'hold',
        'reason': '继续观察',
        'holding_days': 5
    }


@pytest.fixture
def sample_stock_pool_data():
    """示例股票池数据"""
    return {
        'stock_code': '000002',
        'stock_name': '万科A',
        'pool_type': 'watch',
        'target_price': 15.80,
        'add_reason': '技术形态良好',
        'status': 'active'
    }


@pytest.fixture
def sample_case_study_data():
    """示例案例研究数据"""
    return {
        'stock_code': '000001',
        'title': '平安银行突破案例',
        'image_path': '/uploads/case_001.png',
        'tags': ['突破', '银行股', 'B1战法'],
        'notes': '经典的B1战法突破案例'
    }


@pytest.fixture
def sample_stock_price_data():
    """示例股票价格数据"""
    from datetime import date
    return {
        'stock_code': '000001',
        'stock_name': '平安银行',
        'current_price': 12.80,
        'change_percent': 2.40,
        'record_date': date(2024, 1, 16)
    }


@pytest.fixture
def sample_sector_data():
    """示例板块数据"""
    from datetime import date
    return {
        'sector_name': '银行',
        'sector_code': 'BK0475',
        'change_percent': 1.85,
        'record_date': date(2024, 1, 16),
        'rank_position': 5,
        'volume': 1500000000,
        'market_cap': 850000000000.0
    }


@pytest.fixture
def sample_trading_strategy_data():
    """示例交易策略数据"""
    return {
        'strategy_name': '测试策略',
        'is_active': True,
        'rules': {
            'rules': [
                {
                    'day_range': [1, 5],
                    'loss_threshold': -0.05,
                    'action': 'sell_all',
                    'condition': 'loss_exceed'
                }
            ]
        },
        'description': '测试用策略'
    }


@pytest.fixture
def sample_configuration_data():
    """示例配置数据"""
    return {
        'config_key': 'test_config',
        'config_value': '["选项1", "选项2", "选项3"]',
        'description': '测试配置项'
    }