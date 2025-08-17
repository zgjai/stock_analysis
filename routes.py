from flask import Blueprint, render_template, request, jsonify, current_app
import os

# 创建前端路由蓝图
frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    """首页重定向到仪表板"""
    return render_template('dashboard.html')

@frontend_bp.route('/dashboard')
def dashboard():
    """仪表板页面"""
    return render_template('dashboard.html')

@frontend_bp.route('/trading-records')
def trading_records():
    """交易记录页面"""
    return render_template('trading_records.html')

@frontend_bp.route('/review')
def review():
    """复盘分析页面"""
    return render_template('review.html')

@frontend_bp.route('/stock-pool')
def stock_pool():
    """股票池管理页面"""
    return render_template('stock_pool.html')

@frontend_bp.route('/sector-analysis')
def sector_analysis():
    """板块分析页面"""
    return render_template('sector_analysis.html')

@frontend_bp.route('/cases')
def cases():
    """案例管理页面"""
    return render_template('cases.html')

@frontend_bp.route('/analytics')
def analytics():
    """统计分析页面"""
    return render_template('analytics.html')

@frontend_bp.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': '系统运行正常'
    })

@frontend_bp.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return render_template('404.html'), 404

@frontend_bp.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return render_template('500.html'), 500