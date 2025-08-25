"""
API蓝图模块
"""
from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 导入所有路由模块
from . import routes
from . import trading_routes
from . import review_routes
from . import strategy_routes
from . import stock_pool_routes
from . import price_routes
from . import sector_routes
from . import analytics_routes
from . import non_trading_day_routes