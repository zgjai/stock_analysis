"""
复盘记录和持仓管理API路由
"""
from flask import request, jsonify
from datetime import datetime, date
from . import api_bp
from extensions import db
from services.review_service import ReviewService, HoldingService
from error_handlers import create_success_response, ValidationError, NotFoundError, DatabaseError
import logging

logger = logging.getLogger(__name__)


@api_bp.route('/reviews', methods=['GET'])
def get_reviews():
    """获取复盘记录列表"""
    try:
        # 获取查询参数
        filters = {}
        
        # 基本筛选参数
        if request.args.get('stock_code'):
            filters['stock_code'] = request.args.get('stock_code')
        
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        
        if request.args.get('decision'):
            filters['decision'] = request.args.get('decision')
        
        if request.args.get('min_score') is not None:
            filters['min_score'] = int(request.args.get('min_score'))
        
        if request.args.get('max_score') is not None:
            filters['max_score'] = int(request.args.get('max_score'))
        
        if request.args.get('holding_days_min') is not None:
            filters['holding_days_min'] = int(request.args.get('holding_days_min'))
        
        if request.args.get('holding_days_max') is not None:
            filters['holding_days_max'] = int(request.args.get('holding_days_max'))
        
        # 分页参数
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int, default=20)
        
        # 排序参数
        sort_by = request.args.get('sort_by', 'review_date')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 获取复盘记录
        result = ReviewService.get_reviews(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return create_success_response(
            data=result,
            message='获取复盘记录成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/reviews', methods=['POST'])
def create_review():
    """创建复盘记录"""
    try:
        try:
            data = request.get_json()
        except Exception:
            raise ValidationError("请求数据格式错误")
        
        if data is None:
            raise ValidationError("请求数据不能为空")
        
        # 必填字段验证
        required_fields = ['stock_code', 'review_date']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"{field}不能为空")
        
        # 设置默认评分值
        score_fields = ['price_up_score', 'bbi_score', 'volume_score', 'trend_score', 'j_score']
        for field in score_fields:
            if field not in data:
                data[field] = 0
        
        # 验证和处理浮盈相关字段
        _validate_floating_profit_fields(data)
        
        # 创建复盘记录
        review = ReviewService.create_review(data)
        
        return create_success_response(
            data=review.to_dict(),
            message='复盘记录创建成功'
        ), 201
    
    except Exception as e:
        raise e


@api_bp.route('/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """获取单个复盘记录详情"""
    try:
        review = ReviewService.get_by_id(review_id)
        
        return create_success_response(
            data=review.to_dict(),
            message='获取复盘记录成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    """更新复盘记录"""
    try:
        try:
            data = request.get_json()
        except Exception:
            raise ValidationError("请求数据格式错误")
        
        if data is None:
            raise ValidationError("请求数据不能为空")
        
        # 验证和处理浮盈相关字段
        _validate_floating_profit_fields(data)
        
        # 更新复盘记录
        review = ReviewService.update_review(review_id, data)
        
        return create_success_response(
            data=review.to_dict(),
            message='复盘记录更新成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """删除复盘记录"""
    try:
        ReviewService.delete(review_id)
        
        return create_success_response(
            message='复盘记录删除成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/reviews/stock/<string:stock_code>', methods=['GET'])
def get_reviews_by_stock(stock_code):
    """获取某股票的所有复盘记录"""
    try:
        reviews = ReviewService.get_reviews_by_stock(stock_code)
        
        return create_success_response(
            data=[review.to_dict() for review in reviews],
            message=f'获取股票{stock_code}复盘记录成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/reviews/stock/<string:stock_code>/latest', methods=['GET'])
def get_latest_review_by_stock(stock_code):
    """获取某股票最新的复盘记录"""
    try:
        review = ReviewService.get_latest_review_by_stock(stock_code)
        
        if not review:
            return create_success_response(
                data=None,
                message=f'股票{stock_code}暂无复盘记录'
            )
        
        return create_success_response(
            data=review.to_dict(),
            message=f'获取股票{stock_code}最新复盘记录成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/holdings', methods=['GET'])
def get_current_holdings():
    """获取当前持仓列表"""
    try:
        # 检查是否需要强制刷新价格
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        holdings = HoldingService.get_current_holdings(force_refresh_prices=force_refresh)
        
        return create_success_response(
            data=holdings,
            message='获取当前持仓成功'
        )
    
    except ValidationError as e:
        raise e
    except NotFoundError as e:
        raise e
    except DatabaseError as e:
        raise e
    except Exception as e:
        logger.error(f"获取当前持仓时发生未知错误: {e}")
        return create_success_response(
            data=[],
            message='获取持仓数据时遇到问题，但系统仍可正常使用',
            warning=str(e)
        )


@api_bp.route('/holdings/<string:stock_code>', methods=['GET'])
def get_holding_by_stock(stock_code):
    """获取特定股票的持仓信息"""
    try:
        holding = HoldingService.get_holding_by_stock(stock_code)
        
        if not holding:
            raise NotFoundError(f"股票{stock_code}当前无持仓")
        
        return create_success_response(
            data=holding,
            message=f'获取股票{stock_code}持仓信息成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/holdings/<string:stock_code>/days', methods=['GET'])
def get_holding_days(stock_code):
    """获取持仓天数"""
    try:
        holding_days = HoldingService.get_holding_days(stock_code)
        
        return create_success_response(
            data={'stock_code': stock_code, 'holding_days': holding_days},
            message=f'获取股票{stock_code}持仓天数成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/holdings/<string:stock_code>/days', methods=['POST'])
def create_holding_days(stock_code):
    """创建持仓天数记录"""
    try:
        data = request.get_json()
        
        if data is None or 'holding_days' not in data:
            raise ValidationError("持仓天数不能为空")
        
        holding_days = data['holding_days']
        
        # 验证持仓天数格式
        if not isinstance(holding_days, int):
            try:
                holding_days = int(holding_days)
            except (ValueError, TypeError):
                raise ValidationError("持仓天数必须是正整数")
        
        # 验证持仓天数值
        if holding_days <= 0:
            raise ValidationError("持仓天数必须是正整数")
        
        # 创建持仓天数记录
        review = HoldingService.create_holding_days(stock_code, holding_days)
        
        return create_success_response(
            data=review,
            message=f'创建股票{stock_code}持仓天数成功'
        ), 201
    
    except Exception as e:
        raise e


@api_bp.route('/holdings/<string:stock_code>/days', methods=['PUT'])
def update_holding_days(stock_code):
    """更新持仓天数"""
    try:
        data = request.get_json()
        
        if data is None or 'holding_days' not in data:
            raise ValidationError("持仓天数不能为空")
        
        holding_days = data['holding_days']
        
        # 验证持仓天数格式
        if not isinstance(holding_days, int):
            try:
                holding_days = int(holding_days)
            except (ValueError, TypeError):
                raise ValidationError("持仓天数必须是正整数")
        
        # 验证持仓天数值
        if holding_days <= 0:
            raise ValidationError("持仓天数必须是正整数")
        
        # 更新持仓天数
        review = HoldingService.update_holding_days(stock_code, holding_days)
        
        return create_success_response(
            data=review,
            message=f'更新股票{stock_code}持仓天数成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/holdings/<string:stock_code>/days', methods=['DELETE'])
def delete_holding_days(stock_code):
    """删除/重置持仓天数"""
    try:
        HoldingService.delete_holding_days(stock_code)
        
        return create_success_response(
            message=f'删除股票{stock_code}持仓天数成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/holdings/stats', methods=['GET'])
def get_holding_stats():
    """获取持仓统计信息"""
    try:
        stats = HoldingService.get_holding_stats()
        
        return create_success_response(
            data=stats,
            message='获取持仓统计成功'
        )
    
    except Exception as e:
        raise e








@api_bp.route('/reviews/calculate-score', methods=['POST'])
def calculate_review_score():
    """计算复盘评分"""
    try:
        data = request.get_json()
        
        if data is None:
            raise ValidationError("请求数据不能为空")
        
        # 获取各项评分
        price_up_score = int(data.get('price_up_score', 0))
        bbi_score = int(data.get('bbi_score', 0))
        volume_score = int(data.get('volume_score', 0))
        trend_score = int(data.get('trend_score', 0))
        j_score = int(data.get('j_score', 0))
        
        # 验证评分值
        scores = [price_up_score, bbi_score, volume_score, trend_score, j_score]
        for i, score in enumerate(scores):
            if score not in [0, 1]:
                score_names = ['price_up_score', 'bbi_score', 'volume_score', 'trend_score', 'j_score']
                raise ValidationError(f"{score_names[i]}必须是0或1")
        
        # 计算总分
        total_score = sum(scores)
        
        result = {
            'price_up_score': price_up_score,
            'bbi_score': bbi_score,
            'volume_score': volume_score,
            'trend_score': trend_score,
            'j_score': j_score,
            'total_score': total_score,
            'score_breakdown': {
                '收盘价上升': price_up_score,
                '不破BBI线': bbi_score,
                '无放量阴线': volume_score,
                '趋势还在向上': trend_score,
                'J没死叉': j_score
            }
        }
        
        return create_success_response(
            data=result,
            message='计算复盘评分成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/reviews/calculate-floating-profit', methods=['POST'])
def calculate_floating_profit():
    """计算浮盈比例"""
    try:
        try:
            data = request.get_json()
        except Exception:
            raise ValidationError("请求数据格式错误")
        
        if data is None:
            raise ValidationError("请求数据不能为空")
        
        # 验证必填字段
        if 'stock_code' not in data or not data['stock_code']:
            raise ValidationError("股票代码不能为空")
        
        if 'current_price' not in data or data['current_price'] is None:
            raise ValidationError("当前价格不能为空")
        
        stock_code = data['stock_code']
        current_price = data['current_price']
        
        # 验证当前价格格式
        try:
            current_price = float(current_price)
            if current_price <= 0:
                raise ValidationError("当前价格必须大于0")
        except (ValueError, TypeError):
            raise ValidationError("当前价格必须是有效数字")
        
        # 使用服务层计算浮盈
        result = ReviewService.calculate_floating_profit(stock_code, current_price)
        
        return create_success_response(
            data=result,
            message='浮盈计算成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/reviews/stats', methods=['GET'])
def get_review_stats():
    """获取复盘统计信息"""
    try:
        from models.review_record import ReviewRecord
        from sqlalchemy import func
        
        # 总复盘记录数
        total_reviews = ReviewRecord.query.count()
        
        # 按评分分组统计
        score_stats = db.session.query(
            ReviewRecord.total_score,
            func.count(ReviewRecord.id).label('count')
        ).group_by(ReviewRecord.total_score).all()
        
        score_distribution = {}
        for stat in score_stats:
            score_distribution[stat.total_score] = stat.count
        
        # 按决策分组统计
        decision_stats = db.session.query(
            ReviewRecord.decision,
            func.count(ReviewRecord.id).label('count')
        ).filter(ReviewRecord.decision.isnot(None)).group_by(ReviewRecord.decision).all()
        
        decision_distribution = {}
        for stat in decision_stats:
            decision_distribution[stat.decision] = stat.count
        
        # 平均评分
        avg_score = db.session.query(func.avg(ReviewRecord.total_score)).scalar()
        
        # 最近7天的复盘记录数
        from datetime import timedelta
        seven_days_ago = date.today() - timedelta(days=7)
        recent_reviews = ReviewRecord.query.filter(
            ReviewRecord.review_date >= seven_days_ago
        ).count()
        
        stats = {
            'total_reviews': total_reviews,
            'avg_score': round(float(avg_score), 2) if avg_score else 0,
            'score_distribution': score_distribution,
            'decision_distribution': decision_distribution,
            'recent_reviews_7days': recent_reviews
        }
        
        return create_success_response(
            data=stats,
            message='获取复盘统计成功'
        )
    
    except Exception as e:
        raise e


def _validate_floating_profit_fields(data):
    """验证浮盈相关字段"""
    # 验证当前价格
    if 'current_price' in data and data['current_price'] is not None:
        try:
            current_price = float(data['current_price'])
            if current_price < 0:
                raise ValidationError("当前价格不能为负数")
            data['current_price'] = current_price
        except (ValueError, TypeError):
            raise ValidationError("当前价格必须是有效数字")
    
    # 验证买入价格
    if 'buy_price' in data and data['buy_price'] is not None:
        try:
            buy_price = float(data['buy_price'])
            if buy_price < 0:
                raise ValidationError("买入价格不能为负数")
            data['buy_price'] = buy_price
        except (ValueError, TypeError):
            raise ValidationError("买入价格必须是有效数字")
    
    # 验证浮盈比例
    if 'floating_profit_ratio' in data and data['floating_profit_ratio'] is not None:
        try:
            floating_profit_ratio = float(data['floating_profit_ratio'])
            # 浮盈比例可以为负数（亏损），但需要在合理范围内
            if floating_profit_ratio < -1:  # 不能亏损超过100%
                raise ValidationError("浮盈比例不能小于-100%")
            if floating_profit_ratio > 10:  # 不能盈利超过1000%（防止输入错误）
                raise ValidationError("浮盈比例不能大于1000%")
            data['floating_profit_ratio'] = floating_profit_ratio
        except (ValueError, TypeError):
            raise ValidationError("浮盈比例必须是有效数字")
    
    # 数据完整性检查：如果提供了当前价格和买入价格，验证浮盈比例
    if ('current_price' in data and data['current_price'] is not None and 
        'buy_price' in data and data['buy_price'] is not None):
        
        current_price = float(data['current_price'])
        buy_price = float(data['buy_price'])
        
        if buy_price > 0:
            calculated_ratio = (current_price - buy_price) / buy_price
            
            # 如果用户提供了浮盈比例，检查是否一致
            if ('floating_profit_ratio' in data and data['floating_profit_ratio'] is not None):
                provided_ratio = float(data['floating_profit_ratio'])
                if abs(provided_ratio - calculated_ratio) > 0.001:
                    raise ValidationError(
                        f"浮盈比例与当前价格和买入价格不一致。"
                        f"计算值: {calculated_ratio:.4f}, 提供值: {provided_ratio:.4f}"
                    )
            else:
                # 如果没有提供浮盈比例，自动计算
                data['floating_profit_ratio'] = calculated_ratio


@api_bp.route('/reviews/validate', methods=['POST'])
def validate_review_data():
    """验证复盘数据完整性"""
    try:
        try:
            data = request.get_json()
        except Exception:
            raise ValidationError("请求数据格式错误")
        
        if data is None:
            raise ValidationError("请求数据不能为空")
        
        # 验证数据完整性
        validation_result = ReviewService.validate_review_data_integrity(data)
        
        return create_success_response(
            data=validation_result,
            message='数据验证完成'
        )
    
    except Exception as e:
        raise e

@api_bp.route('/holdings/refresh-prices', methods=['POST'])
def refresh_holdings_prices():
    """批量刷新持仓股票价格"""
    try:
        data = request.get_json() or {}
        stock_codes = data.get('stock_codes', [])
        
        if not stock_codes:
            # 如果没有指定股票代码，获取所有持仓股票
            holdings = HoldingService.get_current_holdings(force_refresh_prices=False)
            stock_codes = [h['stock_code'] for h in holdings]
        
        if not stock_codes:
            return create_success_response(
                data={'message': '没有需要刷新的股票'},
                message='没有持仓股票需要刷新价格'
            )
        
        # 批量刷新价格
        result = HoldingService.refresh_all_holdings_prices(stock_codes)
        
        return create_success_response(
            data=result,
            message=f'批量刷新完成，成功: {result["success_count"]}, 失败: {result["failed_count"]}'
        )
    
    except Exception as e:
        logger.error(f"批量刷新价格失败: {e}")
        raise e


@api_bp.route('/price-service/cache-info', methods=['GET'])
def get_price_cache_info():
    """获取价格服务缓存信息"""
    try:
        from services.price_service import PriceService
        
        price_service = PriceService()
        cache_info = price_service.get_market_cache_info()
        
        return create_success_response(
            data=cache_info,
            message='获取缓存信息成功'
        )
        
    except Exception as e:
        logger.error(f"获取缓存信息失败: {e}")
        raise e
