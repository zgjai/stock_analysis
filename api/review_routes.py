"""
复盘记录和持仓管理API路由
"""
from flask import request, jsonify
from datetime import datetime, date
from . import api_bp
from extensions import db
from services.review_service import ReviewService, HoldingService
from error_handlers import create_success_response, ValidationError, NotFoundError


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
        data = request.get_json()
        
        if data is None:
            raise ValidationError("请求数据不能为空")
        
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
        holdings = HoldingService.get_current_holdings()
        
        return create_success_response(
            data=holdings,
            message='获取当前持仓成功'
        )
    
    except Exception as e:
        raise e


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


@api_bp.route('/holdings/<string:stock_code>/days', methods=['PUT'])
def update_holding_days(stock_code):
    """更新持仓天数"""
    try:
        data = request.get_json()
        
        if data is None or 'holding_days' not in data:
            raise ValidationError("持仓天数不能为空")
        
        holding_days = data['holding_days']
        
        try:
            holding_days = int(holding_days)
        except (ValueError, TypeError):
            raise ValidationError("持仓天数必须是整数")
        
        # 更新持仓天数
        review = HoldingService.update_holding_days(stock_code, holding_days)
        
        return create_success_response(
            data=review,
            message=f'更新股票{stock_code}持仓天数成功'
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