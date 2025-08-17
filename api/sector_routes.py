"""
板块分析API路由
"""
from datetime import date, datetime
from flask import Blueprint, request, jsonify
from services.sector_service import SectorAnalysisService
from error_handlers import ValidationError, ExternalAPIError
from utils.validators import validate_date, validate_positive_integer


# 创建蓝图
sector_bp = Blueprint('sector', __name__, url_prefix='/api/sectors')

# 使用服务类
sector_service = SectorAnalysisService


@sector_bp.route('/refresh', methods=['POST'])
def refresh_sector_data():
    """手动刷新板块数据"""
    try:
        result = sector_service.refresh_sector_data()
        return jsonify({
            'success': True,
            'message': result['message'],
            'data': result
        }), 200
        
    except ExternalAPIError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXTERNAL_API_ERROR',
                'message': str(e)
            }
        }), 503
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'field': getattr(e, 'field', None)
            }
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '刷新板块数据时发生内部错误'
            }
        }), 500


@sector_bp.route('/ranking', methods=['GET'])
def get_sector_ranking():
    """获取板块涨幅排名"""
    try:
        # 获取查询参数
        date_str = request.args.get('date')
        limit = request.args.get('limit', type=int)
        
        # 验证参数
        target_date = None
        if date_str:
            target_date = validate_date(date_str)
        
        if limit is not None:
            validate_positive_integer(limit, 'limit')
        
        # 获取排名数据
        ranking_data = sector_service.get_sector_ranking(target_date, limit)
        
        return jsonify({
            'success': True,
            'data': ranking_data,
            'meta': {
                'date': target_date.isoformat() if target_date else date.today().isoformat(),
                'count': len(ranking_data),
                'limit': limit
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'field': getattr(e, 'field', None)
            }
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '获取板块排名时发生内部错误'
            }
        }), 500


@sector_bp.route('/history', methods=['GET'])
def get_sector_history():
    """获取板块历史表现"""
    try:
        # 获取查询参数
        sector_name = request.args.get('sector_name')
        days = request.args.get('days', default=30, type=int)
        
        # 验证参数
        if not sector_name:
            raise ValidationError("板块名称不能为空", "sector_name")
        
        validate_positive_integer(days, 'days')
        
        # 获取历史数据
        history_data = sector_service.get_sector_history(sector_name, days)
        
        return jsonify({
            'success': True,
            'data': history_data,
            'meta': {
                'sector_name': sector_name,
                'days': days,
                'count': len(history_data)
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'field': getattr(e, 'field', None)
            }
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '获取板块历史时发生内部错误'
            }
        }), 500


@sector_bp.route('/top-performers', methods=['GET'])
def get_top_performers():
    """获取最近N天TOPK板块统计"""
    try:
        # 获取查询参数
        days = request.args.get('days', default=30, type=int)
        top_k = request.args.get('top_k', default=10, type=int)
        
        # 验证参数
        validate_positive_integer(days, 'days')
        validate_positive_integer(top_k, 'top_k')
        
        # 获取TOPK数据
        top_performers = sector_service.get_top_performers(days, top_k)
        
        return jsonify({
            'success': True,
            'data': top_performers,
            'meta': {
                'days': days,
                'top_k': top_k,
                'count': len(top_performers)
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'field': getattr(e, 'field', None)
            }
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '获取TOPK板块统计时发生内部错误'
            }
        }), 500


@sector_bp.route('/summary', methods=['GET'])
def get_analysis_summary():
    """获取板块分析汇总信息"""
    try:
        # 获取查询参数
        days = request.args.get('days', default=30, type=int)
        
        # 验证参数
        validate_positive_integer(days, 'days')
        
        # 获取汇总数据
        summary = sector_service.get_sector_analysis_summary(days)
        
        return jsonify({
            'success': True,
            'data': summary
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'field': getattr(e, 'field', None)
            }
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '获取分析汇总时发生内部错误'
            }
        }), 500


@sector_bp.route('/dates', methods=['GET'])
def get_available_dates():
    """获取可用的数据日期列表"""
    try:
        # 获取查询参数
        limit = request.args.get('limit', default=30, type=int)
        
        # 验证参数
        validate_positive_integer(limit, 'limit')
        
        # 获取日期列表
        dates = sector_service.get_available_dates(limit)
        
        return jsonify({
            'success': True,
            'data': dates,
            'meta': {
                'count': len(dates),
                'limit': limit
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'field': getattr(e, 'field', None)
            }
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '获取可用日期时发生内部错误'
            }
        }), 500


@sector_bp.route('/data/<date_str>', methods=['DELETE'])
def delete_sector_data(date_str):
    """删除指定日期的板块数据"""
    try:
        # 验证日期格式
        target_date = validate_date(date_str)
        
        # 删除数据
        result = sector_service.delete_sector_data(target_date)
        
        return jsonify({
            'success': True,
            'message': result['message'],
            'data': result
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'field': getattr(e, 'field', None)
            }
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '删除板块数据时发生内部错误'
            }
        }), 500


# 错误处理
@sector_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': '请求的资源不存在'
        }
    }), 404


@sector_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'METHOD_NOT_ALLOWED',
            'message': '请求方法不被允许'
        }
    }), 405