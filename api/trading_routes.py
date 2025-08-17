"""
交易记录管理API路由
"""
from flask import request, jsonify
from datetime import datetime
from . import api_bp
from extensions import db
from services.trading_service import TradingService, TradingConfigService
from error_handlers import create_success_response, ValidationError, NotFoundError


@api_bp.route('/trades', methods=['GET'])
def get_trades():
    """获取交易记录列表"""
    try:
        # 获取查询参数
        filters = {}
        
        # 基本筛选参数
        if request.args.get('stock_code'):
            filters['stock_code'] = request.args.get('stock_code')
        
        if request.args.get('stock_name'):
            filters['stock_name'] = request.args.get('stock_name')
        
        if request.args.get('trade_type'):
            filters['trade_type'] = request.args.get('trade_type')
        
        if request.args.get('reason'):
            filters['reason'] = request.args.get('reason')
        
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        
        if request.args.get('min_price'):
            filters['min_price'] = request.args.get('min_price')
        
        if request.args.get('max_price'):
            filters['max_price'] = request.args.get('max_price')
        
        if request.args.get('is_corrected') is not None:
            filters['is_corrected'] = request.args.get('is_corrected').lower() == 'true'
        
        # 分页参数
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int, default=20)
        
        # 排序参数
        sort_by = request.args.get('sort_by', 'trade_date')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 获取交易记录
        result = TradingService.get_trades(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return create_success_response(
            data=result,
            message='获取交易记录成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades', methods=['POST'])
def create_trade():
    """创建交易记录"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        # 必填字段验证
        required_fields = ['stock_code', 'stock_name', 'trade_type', 'price', 'quantity', 'reason']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"{field}不能为空")
        
        # 设置交易日期（如果未提供）
        if 'trade_date' not in data or not data['trade_date']:
            data['trade_date'] = datetime.now()
        elif isinstance(data['trade_date'], str):
            try:
                data['trade_date'] = datetime.fromisoformat(data['trade_date'].replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("交易日期格式不正确")
        
        # 创建交易记录
        trade = TradingService.create_trade(data)
        
        return create_success_response(
            data=trade.to_dict(),
            message='交易记录创建成功'
        ), 201
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>', methods=['GET'])
def get_trade(trade_id):
    """获取单个交易记录详情"""
    try:
        trade = TradingService.get_trade_by_id(trade_id)
        
        return create_success_response(
            data=trade.to_dict(),
            message='获取交易记录成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>', methods=['PUT'])
def update_trade(trade_id):
    """更新交易记录"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        # 处理交易日期
        if 'trade_date' in data and isinstance(data['trade_date'], str):
            try:
                data['trade_date'] = datetime.fromisoformat(data['trade_date'].replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("交易日期格式不正确")
        
        # 更新交易记录
        trade = TradingService.update_trade(trade_id, data)
        
        return create_success_response(
            data=trade.to_dict(),
            message='交易记录更新成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    """删除交易记录"""
    try:
        TradingService.delete_trade(trade_id)
        
        return create_success_response(
            message='交易记录删除成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/calculate-risk-reward', methods=['POST'])
def calculate_risk_reward():
    """计算止损止盈预期"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        buy_price = data.get('buy_price')
        if not buy_price:
            raise ValidationError("买入价格不能为空")
        
        stop_loss_price = data.get('stop_loss_price')
        take_profit_ratio = data.get('take_profit_ratio')
        sell_ratio = data.get('sell_ratio')
        
        result = TradingService.calculate_risk_reward(
            buy_price=float(buy_price),
            stop_loss_price=float(stop_loss_price) if stop_loss_price else None,
            take_profit_ratio=float(take_profit_ratio) if take_profit_ratio else None,
            sell_ratio=float(sell_ratio) if sell_ratio else None
        )
        
        return create_success_response(
            data=result,
            message='计算止损止盈预期成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>/correct', methods=['POST'])
def correct_trade(trade_id):
    """订正交易记录"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        reason = data.get('reason')
        if not reason:
            raise ValidationError("订正原因不能为空")
        
        corrected_data = data.get('corrected_data', {})
        if not corrected_data:
            raise ValidationError("订正数据不能为空")
        
        # 处理交易日期
        if 'trade_date' in corrected_data and isinstance(corrected_data['trade_date'], str):
            try:
                corrected_data['trade_date'] = datetime.fromisoformat(corrected_data['trade_date'].replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("交易日期格式不正确")
        
        # 订正交易记录
        corrected_trade = TradingService.correct_trade_record(
            original_trade_id=trade_id,
            corrected_data=corrected_data,
            reason=reason
        )
        
        return create_success_response(
            data=corrected_trade.to_dict(),
            message='交易记录订正成功'
        ), 201
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>/history', methods=['GET'])
def get_correction_history(trade_id):
    """获取交易记录订正历史"""
    try:
        history = TradingService.get_correction_history(trade_id)
        
        return create_success_response(
            data=history,
            message='获取订正历史成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/config', methods=['GET'])
def get_trade_config():
    """获取交易配置"""
    try:
        config = TradingConfigService.get_all_config()
        
        return create_success_response(
            data=config,
            message='获取交易配置成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/config/buy-reasons', methods=['GET'])
def get_buy_reasons():
    """获取买入原因选项"""
    try:
        reasons = TradingConfigService.get_buy_reasons()
        
        return create_success_response(
            data={'buy_reasons': reasons},
            message='获取买入原因成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/config/buy-reasons', methods=['PUT'])
def set_buy_reasons():
    """设置买入原因选项"""
    try:
        data = request.get_json()
        
        if not data or 'buy_reasons' not in data:
            raise ValidationError("买入原因列表不能为空")
        
        reasons = data['buy_reasons']
        TradingConfigService.set_buy_reasons(reasons)
        
        return create_success_response(
            data={'buy_reasons': reasons},
            message='设置买入原因成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/config/sell-reasons', methods=['GET'])
def get_sell_reasons():
    """获取卖出原因选项"""
    try:
        reasons = TradingConfigService.get_sell_reasons()
        
        return create_success_response(
            data={'sell_reasons': reasons},
            message='获取卖出原因成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/config/sell-reasons', methods=['PUT'])
def set_sell_reasons():
    """设置卖出原因选项"""
    try:
        data = request.get_json()
        
        if not data or 'sell_reasons' not in data:
            raise ValidationError("卖出原因列表不能为空")
        
        reasons = data['sell_reasons']
        TradingConfigService.set_sell_reasons(reasons)
        
        return create_success_response(
            data={'sell_reasons': reasons},
            message='设置卖出原因成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/stats', methods=['GET'])
def get_trade_stats():
    """获取交易统计信息"""
    try:
        # 获取基本统计信息
        from models.trade_record import TradeRecord
        from sqlalchemy import func
        
        # 总交易记录数
        total_trades = TradeRecord.query.count()
        
        # 买入和卖出记录数
        buy_count = TradeRecord.query.filter_by(trade_type='buy').count()
        sell_count = TradeRecord.query.filter_by(trade_type='sell').count()
        
        # 被订正的记录数
        corrected_count = TradeRecord.query.filter_by(is_corrected=True).count()
        
        # 按股票代码分组统计
        from sqlalchemy import case
        stock_stats = db.session.query(
            TradeRecord.stock_code,
            TradeRecord.stock_name,
            func.count(TradeRecord.id).label('trade_count'),
            func.sum(case((TradeRecord.trade_type == 'buy', 1), else_=0)).label('buy_count'),
            func.sum(case((TradeRecord.trade_type == 'sell', 1), else_=0)).label('sell_count')
        ).group_by(TradeRecord.stock_code, TradeRecord.stock_name).all()
        
        stock_stats_list = []
        for stat in stock_stats:
            stock_stats_list.append({
                'stock_code': stat.stock_code,
                'stock_name': stat.stock_name,
                'trade_count': stat.trade_count,
                'buy_count': stat.buy_count,
                'sell_count': stat.sell_count
            })
        
        stats = {
            'total_trades': total_trades,
            'buy_count': buy_count,
            'sell_count': sell_count,
            'corrected_count': corrected_count,
            'stock_stats': stock_stats_list
        }
        
        return create_success_response(
            data=stats,
            message='获取交易统计成功'
        )
    
    except Exception as e:
        raise e