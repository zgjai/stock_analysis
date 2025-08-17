"""
股票价格API路由
"""
from flask import request, jsonify
from datetime import date, datetime
import logging

from . import api_bp
from services.price_service import PriceService
from error_handlers import ValidationError, ExternalAPIError
from utils.validators import validate_stock_code


logger = logging.getLogger(__name__)

# 初始化服务
price_service = PriceService()


@api_bp.route('/prices/refresh', methods=['POST'])
def refresh_prices():
    """手动刷新股票价格"""
    try:
        data = request.get_json() or {}
        
        # 获取参数
        stock_codes = data.get('stock_codes', [])
        force_refresh = data.get('force_refresh', False)
        
        if not stock_codes:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '请提供股票代码列表'
                }
            }), 400
        
        # 如果只有一个股票代码，使用单个刷新
        if len(stock_codes) == 1:
            result = price_service.refresh_stock_price(stock_codes[0], force_refresh)
            return jsonify(result)
        
        # 批量刷新
        results = price_service.refresh_multiple_stocks(stock_codes, force_refresh)
        
        return jsonify({
            'success': True,
            'message': f'批量刷新完成，成功 {results["success_count"]} 个，失败 {results["failed_count"]} 个',
            'data': results
        })
        
    except ValidationError as e:
        logger.error(f"价格刷新验证失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    
    except ExternalAPIError as e:
        logger.error(f"外部API调用失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXTERNAL_API_ERROR',
                'message': str(e)
            }
        }), 503
    
    except Exception as e:
        logger.error(f"刷新价格时发生未知错误: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误'
            }
        }), 500


@api_bp.route('/prices/<stock_code>', methods=['GET'])
def get_stock_price(stock_code):
    """获取特定股票价格"""
    try:
        # 获取查询参数
        target_date_str = request.args.get('date')
        target_date = None
        
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': '日期格式不正确，请使用YYYY-MM-DD格式'
                    }
                }), 400
        
        # 获取价格数据
        price_data = price_service.get_stock_price(stock_code, target_date)
        
        if price_data:
            return jsonify({
                'success': True,
                'data': price_data
            })
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': f'未找到股票 {stock_code} 的价格数据'
                }
            }), 404
    
    except ValidationError as e:
        logger.error(f"获取股票价格验证失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    
    except ExternalAPIError as e:
        logger.error(f"获取股票价格失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXTERNAL_API_ERROR',
                'message': str(e)
            }
        }), 503
    
    except Exception as e:
        logger.error(f"获取股票价格时发生未知错误: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误'
            }
        }), 500


@api_bp.route('/prices/<stock_code>/latest', methods=['GET'])
def get_latest_price(stock_code):
    """获取股票最新价格"""
    try:
        price_data = price_service.get_latest_price(stock_code)
        
        if price_data:
            return jsonify({
                'success': True,
                'data': price_data
            })
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': f'未找到股票 {stock_code} 的价格数据'
                }
            }), 404
    
    except ValidationError as e:
        logger.error(f"获取最新价格验证失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    
    except ExternalAPIError as e:
        logger.error(f"获取最新价格失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXTERNAL_API_ERROR',
                'message': str(e)
            }
        }), 503
    
    except Exception as e:
        logger.error(f"获取最新价格时发生未知错误: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误'
            }
        }), 500


@api_bp.route('/prices/<stock_code>/history', methods=['GET'])
def get_price_history(stock_code):
    """获取股票价格历史"""
    try:
        # 获取查询参数
        days = request.args.get('days', 30, type=int)
        
        if days <= 0:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '天数必须大于0'
                }
            }), 400
        
        price_history = price_service.get_price_history(stock_code, days)
        
        return jsonify({
            'success': True,
            'data': price_history
        })
    
    except ValidationError as e:
        logger.error(f"获取价格历史验证失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    
    except ExternalAPIError as e:
        logger.error(f"获取价格历史失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXTERNAL_API_ERROR',
                'message': str(e)
            }
        }), 503
    
    except Exception as e:
        logger.error(f"获取价格历史时发生未知错误: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误'
            }
        }), 500


@api_bp.route('/prices/cache/status', methods=['POST'])
def get_cache_status():
    """获取价格缓存状态"""
    try:
        data = request.get_json() or {}
        stock_codes = data.get('stock_codes', [])
        
        if not stock_codes:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '请提供股票代码列表'
                }
            }), 400
        
        cache_status = price_service.get_cache_status(stock_codes)
        
        return jsonify({
            'success': True,
            'data': cache_status
        })
    
    except Exception as e:
        logger.error(f"获取缓存状态时发生错误: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误'
            }
        }), 500


@api_bp.route('/prices/cache/cleanup', methods=['POST'])
def cleanup_cache():
    """清理旧的价格缓存"""
    try:
        data = request.get_json() or {}
        days_to_keep = data.get('days_to_keep', 90)
        
        if days_to_keep <= 0:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '保留天数必须大于0'
                }
            }), 400
        
        result = price_service.cleanup_old_prices(days_to_keep)
        
        return jsonify(result)
    
    except ExternalAPIError as e:
        logger.error(f"清理缓存失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXTERNAL_API_ERROR',
                'message': str(e)
            }
        }), 503
    
    except Exception as e:
        logger.error(f"清理缓存时发生未知错误: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误'
            }
        }), 500


@api_bp.route('/prices/batch', methods=['POST'])
def get_batch_prices():
    """批量获取股票价格"""
    try:
        data = request.get_json() or {}
        stock_codes = data.get('stock_codes', [])
        target_date_str = data.get('date')
        
        if not stock_codes:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '请提供股票代码列表'
                }
            }), 400
        
        target_date = None
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': '日期格式不正确，请使用YYYY-MM-DD格式'
                    }
                }), 400
        
        # 批量获取价格
        results = []
        for stock_code in stock_codes:
            try:
                price_data = price_service.get_stock_price(stock_code, target_date)
                results.append({
                    'stock_code': stock_code,
                    'success': True,
                    'data': price_data
                })
            except Exception as e:
                results.append({
                    'stock_code': stock_code,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'data': results
        })
    
    except Exception as e:
        logger.error(f"批量获取价格时发生未知错误: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误'
            }
        }), 500