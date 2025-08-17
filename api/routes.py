"""
API路由定义
"""
from flask import jsonify
from . import api_bp
from error_handlers import create_success_response

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return create_success_response(
        data={'status': 'healthy', 'service': 'stock-trading-journal'},
        message='服务运行正常'
    )

@api_bp.route('/', methods=['GET'])
def api_info():
    """API信息端点"""
    return create_success_response(
        data={
            'name': '股票交易记录和复盘系统 API',
            'version': '1.0.0',
            'description': '个人投资管理工具API接口'
        }
    )