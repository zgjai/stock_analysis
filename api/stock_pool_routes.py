"""
股票池管理API路由
"""
from flask import request, jsonify
from datetime import datetime
from . import api_bp
from extensions import db
from services.stock_pool_service import StockPoolService
from error_handlers import create_success_response, ValidationError, NotFoundError


@api_bp.route('/stock-pool', methods=['GET'])
def get_stock_pool():
    """获取股票池列表"""
    try:
        # 获取查询参数
        filters = {}
        
        # 基本筛选参数
        if request.args.get('stock_code'):
            filters['stock_code'] = request.args.get('stock_code')
        
        if request.args.get('stock_name'):
            filters['stock_name'] = request.args.get('stock_name')
        
        if request.args.get('pool_type'):
            filters['pool_type'] = request.args.get('pool_type')
        
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        
        if request.args.get('add_reason'):
            filters['add_reason'] = request.args.get('add_reason')
        
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        
        if request.args.get('min_target_price'):
            filters['min_target_price'] = request.args.get('min_target_price')
        
        if request.args.get('max_target_price'):
            filters['max_target_price'] = request.args.get('max_target_price')
        
        # 分页参数
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int, default=20)
        
        # 排序参数
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 获取股票池列表
        result = StockPoolService.search_stocks(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return create_success_response(
            data=result,
            message='获取股票池列表成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool', methods=['POST'])
def create_stock_pool_entry():
    """添加股票到池中"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        # 必填字段验证
        required_fields = ['stock_code', 'stock_name', 'pool_type']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"{field}不能为空")
        
        # 创建股票池条目
        stock_pool = StockPoolService.create_stock_pool_entry(data)
        
        return create_success_response(
            data=stock_pool.to_dict(),
            message='股票添加到池中成功'
        ), 201
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool/<int:stock_id>', methods=['GET'])
def get_stock_pool_entry(stock_id):
    """获取单个股票池条目详情"""
    try:
        stock_pool = StockPoolService.get_by_id(stock_id)
        
        return create_success_response(
            data=stock_pool.to_dict(),
            message='获取股票池条目成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool/<int:stock_id>', methods=['PUT'])
def update_stock_pool_entry(stock_id):
    """更新股票池条目"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        # 更新股票池条目
        stock_pool = StockPoolService.update(stock_id, data)
        
        return create_success_response(
            data=stock_pool.to_dict(),
            message='股票池条目更新成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool/<int:stock_id>', methods=['DELETE'])
def delete_stock_pool_entry(stock_id):
    """删除股票池条目"""
    try:
        StockPoolService.delete(stock_id)
        
        return create_success_response(
            message='股票池条目删除成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool/watch', methods=['GET'])
def get_watch_pool():
    """获取待观测池"""
    try:
        # 获取查询参数
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int, default=20)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        status = request.args.get('status', 'active')
        
        result = StockPoolService.get_watch_pool(
            status=status,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return create_success_response(
            data=result,
            message='获取待观测池成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool/buy-ready', methods=['GET'])
def get_buy_ready_pool():
    """获取待买入池"""
    try:
        # 获取查询参数
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int, default=20)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        status = request.args.get('status', 'active')
        
        result = StockPoolService.get_buy_ready_pool(
            status=status,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return create_success_response(
            data=result,
            message='获取待买入池成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool/<int:stock_id>/move', methods=['POST'])
def move_stock_to_pool(stock_id):
    """移动股票到另一个池"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        new_pool_type = data.get('new_pool_type')
        if not new_pool_type:
            raise ValidationError("目标池类型不能为空")
        
        if new_pool_type not in ['watch', 'buy_ready']:
            raise ValidationError("目标池类型必须是watch或buy_ready")
        
        reason = data.get('reason', f"移动到{new_pool_type}池")
        
        # 移动股票
        new_stock = StockPoolService.move_stock_to_pool(stock_id, new_pool_type, reason)
        
        return create_success_response(
            data=new_stock.to_dict(),
            message='股票移动成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool/<int:stock_id>/remove', methods=['POST'])
def remove_stock_from_pool(stock_id):
    """从池中移除股票"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', '手动移除')
        
        # 移除股票
        stock = StockPoolService.remove_stock_from_pool(stock_id, reason)
        
        return create_success_response(
            data=stock.to_dict(),
            message='股票移除成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool/batch/move', methods=['POST'])
def batch_move_stocks():
    """批量移动股票"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        stock_ids = data.get('stock_ids')
        if not stock_ids or not isinstance(stock_ids, list):
            raise ValidationError("股票ID列表不能为空")
        
        new_pool_type = data.get('new_pool_type')
        if not new_pool_type:
            raise ValidationError("目标池类型不能为空")
        
        if new_pool_type not in ['watch', 'buy_ready']:
            raise ValidationError("目标池类型必须是watch或buy_ready")
        
        reason = data.get('reason', f"批量移动到{new_pool_type}池")
        
        # 批量移动股票
        results = StockPoolService.batch_move_stocks(stock_ids, new_pool_type, reason)
        
        return create_success_response(
            data=results,
            message=f'批量移动完成，成功: {len(results["success"])}，失败: {len(results["failed"])}'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool/batch/remove', methods=['POST'])
def batch_remove_stocks():
    """批量移除股票"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        stock_ids = data.get('stock_ids')
        if not stock_ids or not isinstance(stock_ids, list):
            raise ValidationError("股票ID列表不能为空")
        
        reason = data.get('reason', '批量移除')
        
        # 批量移除股票
        results = StockPoolService.batch_remove_stocks(stock_ids, reason)
        
        return create_success_response(
            data=results,
            message=f'批量移除完成，成功: {len(results["success"])}，失败: {len(results["failed"])}'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool/history/<stock_code>', methods=['GET'])
def get_stock_history(stock_code):
    """获取股票在池中的流转历史"""
    try:
        history = StockPoolService.get_stock_history(stock_code)
        
        return create_success_response(
            data={'stock_code': stock_code, 'history': history},
            message='获取股票历史成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/stock-pool/stats', methods=['GET'])
def get_stock_pool_stats():
    """获取股票池统计信息"""
    try:
        stats = StockPoolService.get_pool_statistics()
        
        return create_success_response(
            data=stats,
            message='获取股票池统计成功'
        )
    
    except Exception as e:
        raise e