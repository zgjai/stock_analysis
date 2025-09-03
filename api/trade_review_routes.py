"""
历史交易复盘API路由
"""
import logging
from flask import request, jsonify, current_app
from werkzeug.datastructures import FileStorage
from . import api_bp
from services.trade_review_service import TradeReviewService
from error_handlers import create_success_response, ValidationError, NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


@api_bp.route('/trade-reviews/by-trade/<int:historical_trade_id>', methods=['GET'])
def get_trade_review_by_trade(historical_trade_id):
    """根据历史交易ID获取复盘记录"""
    try:
        logger.info(f"获取复盘记录 - 历史交易ID: {historical_trade_id}")
        
        review = TradeReviewService.get_review_by_trade(historical_trade_id)
        
        if not review:
            return create_success_response(
                data=None,
                message="该交易暂无复盘记录"
            )
        
        # 获取复盘图片
        images = TradeReviewService.get_review_images(review.id)
        
        review_data = review.to_dict()
        review_data['images'] = [image.to_dict() for image in images]
        
        return create_success_response(
            data=review_data,
            message="获取复盘记录成功"
        )
        
    except Exception as e:
        logger.error(f"获取复盘记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取复盘记录失败: {str(e)}"
        }), 500


@api_bp.route('/trade-reviews', methods=['POST'])
def create_trade_review():
    """创建复盘记录"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        historical_trade_id = data.get('historical_trade_id')
        if not historical_trade_id:
            raise ValidationError("历史交易ID不能为空")
        
        logger.info(f"创建复盘记录 - 历史交易ID: {historical_trade_id}")
        
        # 提取复盘数据
        review_data = {
            'review_title': data.get('review_title'),
            'review_content': data.get('review_content'),
            'review_type': data.get('review_type', 'general'),
            'strategy_score': data.get('strategy_score'),
            'timing_score': data.get('timing_score'),
            'risk_control_score': data.get('risk_control_score'),
            'overall_score': data.get('overall_score'),
            'key_learnings': data.get('key_learnings'),
            'improvement_areas': data.get('improvement_areas')
        }
        
        # 移除空值
        review_data = {k: v for k, v in review_data.items() if v is not None}
        
        review = TradeReviewService.create_review(historical_trade_id, review_data)
        
        return create_success_response(
            data=review.to_dict(),
            message="复盘记录创建成功"
        ), 201
        
    except ValidationError as e:
        logger.warning(f"创建复盘记录验证失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"创建复盘记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"创建复盘记录失败: {str(e)}"
        }), 500


@api_bp.route('/trade-reviews/<int:review_id>', methods=['GET'])
def get_trade_review(review_id):
    """根据复盘ID获取复盘记录"""
    try:
        logger.info(f"获取复盘记录 - 复盘ID: {review_id}")
        
        review = TradeReviewService.get_review_by_id(review_id)
        
        if not review:
            raise NotFoundError("复盘记录不存在")
        
        # 获取复盘图片
        images = TradeReviewService.get_review_images(review.id)
        
        review_data = review.to_dict()
        review_data['images'] = [image.to_dict() for image in images]
        
        return create_success_response(
            data=review_data,
            message="获取复盘记录成功"
        )
        
    except NotFoundError as e:
        logger.warning(f"复盘记录不存在: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"获取复盘记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取复盘记录失败: {str(e)}"
        }), 500


@api_bp.route('/trade-reviews/<int:review_id>', methods=['PUT'])
def update_trade_review(review_id):
    """更新复盘记录"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        logger.info(f"更新复盘记录 - ID: {review_id}")
        
        # 提取复盘数据
        review_data = {
            'review_title': data.get('review_title'),
            'review_content': data.get('review_content'),
            'review_type': data.get('review_type'),
            'strategy_score': data.get('strategy_score'),
            'timing_score': data.get('timing_score'),
            'risk_control_score': data.get('risk_control_score'),
            'overall_score': data.get('overall_score'),
            'key_learnings': data.get('key_learnings'),
            'improvement_areas': data.get('improvement_areas')
        }
        
        # 移除空值
        review_data = {k: v for k, v in review_data.items() if v is not None}
        
        review = TradeReviewService.update_review(review_id, review_data)
        
        return create_success_response(
            data=review.to_dict(),
            message="复盘记录更新成功"
        )
        
    except ValidationError as e:
        logger.warning(f"更新复盘记录验证失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except NotFoundError as e:
        logger.warning(f"复盘记录不存在: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"更新复盘记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"更新复盘记录失败: {str(e)}"
        }), 500


@api_bp.route('/trade-reviews/<int:review_id>', methods=['DELETE'])
def delete_trade_review(review_id):
    """删除复盘记录"""
    try:
        logger.info(f"删除复盘记录 - ID: {review_id}")
        
        TradeReviewService.delete_review(review_id)
        
        return create_success_response(
            data=None,
            message="复盘记录删除成功"
        )
        
    except NotFoundError as e:
        logger.warning(f"复盘记录不存在: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"删除复盘记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"删除复盘记录失败: {str(e)}"
        }), 500


@api_bp.route('/trade-reviews', methods=['GET'])
def get_trade_reviews_list():
    """获取复盘记录列表"""
    try:
        # 获取查询参数
        filters = {}
        
        if request.args.get('stock_code'):
            filters['stock_code'] = request.args.get('stock_code')
        
        if request.args.get('review_type'):
            filters['review_type'] = request.args.get('review_type')
        
        if request.args.get('min_overall_score') is not None:
            try:
                filters['min_overall_score'] = int(request.args.get('min_overall_score'))
            except ValueError:
                raise ValidationError("最低评分必须是整数")
        
        if request.args.get('max_overall_score') is not None:
            try:
                filters['max_overall_score'] = int(request.args.get('max_overall_score'))
            except ValueError:
                raise ValidationError("最高评分必须是整数")
        
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        
        # 分页参数
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int, default=20)
        
        logger.info(f"获取复盘记录列表 - 筛选条件: {filters}")
        
        result = TradeReviewService.get_reviews_list(
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        return create_success_response(
            data=result,
            message="获取复盘记录列表成功"
        )
        
    except ValidationError as e:
        logger.warning(f"获取复盘记录列表验证失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"获取复盘记录列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取复盘记录列表失败: {str(e)}"
        }), 500


@api_bp.route('/trade-reviews/<int:review_id>/images', methods=['POST'])
def upload_review_images(review_id):
    """上传复盘图片"""
    try:
        logger.info(f"上传复盘图片 - 复盘ID: {review_id}")
        
        # 检查是否有文件上传
        if 'images' not in request.files:
            raise ValidationError("没有找到上传的图片文件")
        
        files = request.files.getlist('images')
        if not files or all(not file.filename for file in files):
            raise ValidationError("请选择要上传的图片文件")
        
        # 获取图片描述
        descriptions = request.form.getlist('descriptions')
        
        # 上传图片
        uploaded_images = TradeReviewService.upload_review_images(
            review_id, files, descriptions
        )
        
        return create_success_response(
            data=[image.to_dict() for image in uploaded_images],
            message=f"成功上传 {len(uploaded_images)} 张图片"
        ), 201
        
    except ValidationError as e:
        logger.warning(f"上传复盘图片验证失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except NotFoundError as e:
        logger.warning(f"复盘记录不存在: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"上传复盘图片失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"上传复盘图片失败: {str(e)}"
        }), 500


@api_bp.route('/trade-reviews/<int:review_id>/images', methods=['GET'])
def get_review_images(review_id):
    """获取复盘图片列表"""
    try:
        logger.info(f"获取复盘图片列表 - 复盘ID: {review_id}")
        
        images = TradeReviewService.get_review_images(review_id)
        
        return create_success_response(
            data=[image.to_dict() for image in images],
            message="获取复盘图片列表成功"
        )
        
    except Exception as e:
        logger.error(f"获取复盘图片列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取复盘图片列表失败: {str(e)}"
        }), 500


@api_bp.route('/review-images/<int:image_id>', methods=['DELETE'])
def delete_review_image(image_id):
    """删除复盘图片"""
    try:
        logger.info(f"删除复盘图片 - ID: {image_id}")
        
        TradeReviewService.delete_review_image(image_id)
        
        return create_success_response(
            data=None,
            message="复盘图片删除成功"
        )
        
    except NotFoundError as e:
        logger.warning(f"复盘图片不存在: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"删除复盘图片失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"删除复盘图片失败: {str(e)}"
        }), 500


@api_bp.route('/trade-reviews/<int:review_id>/images/reorder', methods=['PUT'])
def reorder_review_images(review_id):
    """重新排序复盘图片"""
    try:
        data = request.get_json()
        
        if not data or 'image_orders' not in data:
            raise ValidationError("请提供图片排序数据")
        
        image_orders = data['image_orders']
        if not isinstance(image_orders, list):
            raise ValidationError("图片排序数据格式错误")
        
        logger.info(f"重新排序复盘图片 - 复盘ID: {review_id}")
        
        TradeReviewService.update_image_order(review_id, image_orders)
        
        return create_success_response(
            data=None,
            message="图片排序更新成功"
        )
        
    except ValidationError as e:
        logger.warning(f"重新排序复盘图片验证失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"重新排序复盘图片失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"重新排序复盘图片失败: {str(e)}"
        }), 500


@api_bp.route('/trade-reviews/stats', methods=['GET'])
def get_trade_review_stats():
    """获取复盘统计信息"""
    try:
        logger.info("获取复盘统计信息")
        
        from models.trade_review import TradeReview
        from models.historical_trade import HistoricalTrade
        from sqlalchemy import func
        
        # 基本统计
        total_reviews = TradeReview.query.count()
        total_trades = HistoricalTrade.query.count()
        review_coverage = (total_reviews / total_trades * 100) if total_trades > 0 else 0
        
        # 按复盘类型统计
        type_stats = TradeReview.query.with_entities(
            TradeReview.review_type,
            func.count(TradeReview.id).label('count')
        ).group_by(TradeReview.review_type).all()
        
        # 按评分统计
        score_stats = TradeReview.query.with_entities(
            TradeReview.overall_score,
            func.count(TradeReview.id).label('count')
        ).filter(TradeReview.overall_score.isnot(None)).group_by(TradeReview.overall_score).all()
        
        # 平均评分
        avg_scores = TradeReview.query.with_entities(
            func.avg(TradeReview.strategy_score).label('avg_strategy'),
            func.avg(TradeReview.timing_score).label('avg_timing'),
            func.avg(TradeReview.risk_control_score).label('avg_risk_control'),
            func.avg(TradeReview.overall_score).label('avg_overall')
        ).first()
        
        stats = {
            'total_reviews': total_reviews,
            'total_trades': total_trades,
            'review_coverage': round(review_coverage, 2),
            'type_distribution': {item.review_type: item.count for item in type_stats},
            'score_distribution': {item.overall_score: item.count for item in score_stats},
            'average_scores': {
                'strategy': round(float(avg_scores.avg_strategy), 2) if avg_scores.avg_strategy else None,
                'timing': round(float(avg_scores.avg_timing), 2) if avg_scores.avg_timing else None,
                'risk_control': round(float(avg_scores.avg_risk_control), 2) if avg_scores.avg_risk_control else None,
                'overall': round(float(avg_scores.avg_overall), 2) if avg_scores.avg_overall else None
            }
        }
        
        return create_success_response(
            data=stats,
            message="获取复盘统计信息成功"
        )
        
    except Exception as e:
        logger.error(f"获取复盘统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取复盘统计信息失败: {str(e)}"
        }), 500