"""
交易策略和持仓提醒API路由
"""
from flask import request, jsonify
from datetime import datetime, date
from . import api_bp
from extensions import db
from services.strategy_service import StrategyService, StrategyEvaluator, HoldingAlertService
from error_handlers import create_success_response, ValidationError, NotFoundError, DatabaseError
import logging

logger = logging.getLogger(__name__)


@api_bp.route('/strategies', methods=['GET'])
def get_strategies():
    """获取交易策略列表"""
    try:
        # 获取查询参数
        filters = {}
        
        if request.args.get('is_active') is not None:
            filters['is_active'] = request.args.get('is_active').lower() == 'true'
        
        if request.args.get('strategy_name'):
            filters['strategy_name'] = request.args.get('strategy_name')
        
        # 分页参数
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int, default=20)
        
        # 排序参数
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 获取策略列表
        result = StrategyService.get_strategies(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return create_success_response(
            data=result,
            message='获取交易策略成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/strategies', methods=['POST'])
def create_strategy():
    """创建交易策略"""
    try:
        data = request.get_json()
        
        if data is None:
            raise ValidationError("请求数据不能为空")
        
        # 必填字段验证
        required_fields = ['strategy_name', 'rules']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"{field}不能为空")
        
        # 创建策略
        strategy = StrategyService.create_strategy(data)
        
        return create_success_response(
            data=strategy.to_dict(),
            message='交易策略创建成功'
        ), 201
    
    except Exception as e:
        raise e


@api_bp.route('/strategies/<int:strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    """获取单个交易策略详情"""
    try:
        strategy = StrategyService.get_by_id(strategy_id)
        
        return create_success_response(
            data=strategy.to_dict(),
            message='获取交易策略成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/strategies/<int:strategy_id>', methods=['PUT'])
def update_strategy(strategy_id):
    """更新交易策略"""
    try:
        data = request.get_json()
        
        if data is None:
            raise ValidationError("请求数据不能为空")
        
        # 更新策略
        strategy = StrategyService.update_strategy(strategy_id, data)
        
        return create_success_response(
            data=strategy.to_dict(),
            message='交易策略更新成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/strategies/<int:strategy_id>', methods=['DELETE'])
def delete_strategy(strategy_id):
    """删除交易策略"""
    try:
        StrategyService.delete(strategy_id)
        
        return create_success_response(
            message='交易策略删除成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/strategies/<int:strategy_id>/activate', methods=['POST'])
def activate_strategy(strategy_id):
    """激活交易策略"""
    try:
        strategy = StrategyService.activate_strategy(strategy_id)
        
        return create_success_response(
            data=strategy.to_dict(),
            message='交易策略激活成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/strategies/<int:strategy_id>/deactivate', methods=['POST'])
def deactivate_strategy(strategy_id):
    """停用交易策略"""
    try:
        strategy = StrategyService.deactivate_strategy(strategy_id)
        
        return create_success_response(
            data=strategy.to_dict(),
            message='交易策略停用成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/strategies/active', methods=['GET'])
def get_active_strategies():
    """获取所有激活的交易策略"""
    try:
        strategies = StrategyService.get_active_strategies()
        
        return create_success_response(
            data=[strategy.to_dict() for strategy in strategies],
            message='获取激活策略成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/strategies/validate-rules', methods=['POST'])
def validate_strategy_rules():
    """验证策略规则格式"""
    try:
        data = request.get_json()
        
        if data is None or 'rules' not in data:
            raise ValidationError("策略规则不能为空")
        
        # 验证规则格式
        StrategyService._validate_strategy_rules(data['rules'])
        
        return create_success_response(
            message='策略规则格式验证通过'
        )
    
    except Exception as e:
        raise e


# Commented out holding alerts API routes as the UI modules have been removed
# These can be re-enabled if needed in the future

# @api_bp.route('/holdings/alerts', methods=['GET'])
# def get_holding_alerts():
#     """获取持仓策略提醒"""
#     try:
#         # 获取查询参数
#         alert_type = request.args.get('type')  # 'all', 'urgent', 'profit', 'sell_all', 'sell_partial'
#         stock_code = request.args.get('stock_code')
#         
#         if stock_code:
#             # 获取特定股票的提醒
#             alerts = HoldingAlertService.get_alerts_by_stock(stock_code)
#         elif alert_type == 'urgent':
#             # 获取紧急提醒
#             alerts = HoldingAlertService.get_urgent_alerts()
#         elif alert_type == 'profit':
#             # 获取止盈提醒
#             alerts = HoldingAlertService.get_profit_alerts()
#         elif alert_type in ['sell_all', 'sell_partial', 'hold']:
#             # 按提醒类型筛选
#             alerts = HoldingAlertService.get_alerts_by_type(alert_type)
#         else:
#             # 获取所有提醒
#             alerts = HoldingAlertService.get_all_alerts()
#         
#         return create_success_response(
#             data=alerts,
#             message='获取持仓提醒成功'
#         )
#     
#     except ValidationError as e:
#         raise e
#     except NotFoundError as e:
#         raise e
#     except DatabaseError as e:
#         raise e
#     except Exception as e:
#         logger.error(f"获取持仓提醒时发生未知错误: {e}")
#         return create_success_response(
#             data=[],
#             message='获取提醒数据时遇到问题，但系统仍可正常使用',
#             warning=str(e)
#         )


# @api_bp.route('/holdings/alerts/summary', methods=['GET'])
# def get_alerts_summary():
#     """获取持仓提醒汇总信息"""
#     try:
#         summary = HoldingAlertService.get_alerts_summary()
#         
#         return create_success_response(
#             data=summary,
#             message='获取提醒汇总成功'
#         )
#     
#     except Exception as e:
#         raise e


@api_bp.route('/holdings/alerts/evaluate', methods=['POST'])
def evaluate_holdings():
    """手动触发持仓策略评估"""
    try:
        # 处理可能没有JSON数据的情况
        try:
            data = request.get_json() or {}
        except:
            data = {}
        stock_code = data.get('stock_code')
        
        if stock_code:
            # 评估特定股票
            alerts = StrategyEvaluator.evaluate_single_holding(stock_code)
            message = f'评估股票{stock_code}持仓策略成功'
        else:
            # 评估所有持仓
            alerts = StrategyEvaluator.evaluate_all_holdings()
            message = '评估所有持仓策略成功'
        
        return create_success_response(
            data=alerts,
            message=message
        )
    
    except Exception as e:
        raise e


@api_bp.route('/strategies/test-rule', methods=['POST'])
def test_strategy_rule():
    """测试策略规则"""
    try:
        data = request.get_json()
        
        if data is None:
            raise ValidationError("请求数据不能为空")
        
        # 必填字段验证
        required_fields = ['rule', 'holding_days', 'profit_loss_ratio']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"{field}不能为空")
        
        rule = data['rule']
        holding_days = int(data['holding_days'])
        profit_loss_ratio = float(data['profit_loss_ratio'])
        
        # 测试规则是否适用
        applies = StrategyEvaluator._rule_applies_to_holding_days(rule, holding_days)
        
        # 测试规则是否触发
        triggered = False
        if applies:
            triggered = StrategyEvaluator._rule_triggered(rule, profit_loss_ratio, holding_days)
        
        result = {
            'rule_applies': applies,
            'rule_triggered': triggered,
            'rule_description': StrategyEvaluator._format_rule_description(rule),
            'test_parameters': {
                'holding_days': holding_days,
                'profit_loss_ratio': profit_loss_ratio,
                'profit_loss_percent': round(profit_loss_ratio * 100, 2)
            }
        }
        
        if triggered:
            result['alert_message'] = StrategyEvaluator._generate_alert_message(
                'TEST', holding_days, profit_loss_ratio, rule
            )
        
        return create_success_response(
            data=result,
            message='策略规则测试完成'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/strategies/default', methods=['GET'])
def get_default_strategy():
    """获取默认策略"""
    try:
        from models.trading_strategy import TradingStrategy
        
        default_strategy = TradingStrategy.get_default_strategy()
        
        if not default_strategy:
            raise NotFoundError("默认策略不存在")
        
        return create_success_response(
            data=default_strategy.to_dict(),
            message='获取默认策略成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/strategies/default/reset', methods=['POST'])
def reset_default_strategy():
    """重置默认策略"""
    try:
        from models.trading_strategy import TradingStrategy
        
        # 获取或创建默认策略
        default_strategy = TradingStrategy.get_default_strategy()
        
        # 默认策略规则
        default_rules = {
            "rules": [
                {"day_range": [1, 1], "loss_threshold": -0.05, "action": "sell_all", "condition": "loss_exceed"},
                {"day_range": [2, 4], "loss_threshold": -0.03, "action": "sell_all", "condition": "loss_exceed"},
                {"day_range": [5, 5], "loss_threshold": -0.02, "action": "sell_all", "condition": "loss_exceed"},
                {"day_range": [6, 6], "profit_threshold": 0.03, "action": "sell_all", "condition": "profit_below"},
                {"day_range": [7, 10], "profit_threshold": 0.07, "action": "sell_all", "condition": "profit_below"},
                {"day_range": [7, 10], "profit_threshold": 0.10, "action": "sell_partial", "sell_ratio": 0.3, "condition": "profit_exceed"},
                {"day_range": [11, 15], "profit_threshold": 0.15, "drawdown_threshold": 0.10, "action": "sell_all", "condition": "profit_below_or_drawdown"},
                {"day_range": [11, 15], "profit_threshold": 0.20, "action": "sell_partial", "sell_ratio": 0.3, "condition": "profit_exceed"},
                {"day_range": [16, 20], "profit_threshold": 0.25, "drawdown_threshold": 0.15, "action": "sell_all", "condition": "profit_below_or_drawdown"},
                {"day_range": [16, 20], "profit_threshold": 0.30, "action": "sell_partial", "sell_ratio": 0.2, "condition": "profit_exceed"},
                {"day_range": [21, 30], "profit_threshold": 0.30, "drawdown_threshold": 0.15, "action": "sell_all", "condition": "profit_below_or_drawdown"}
            ]
        }
        
        if default_strategy:
            # 更新现有默认策略
            default_strategy.rules_list = default_rules
            default_strategy.is_active = True
            default_strategy.save()
        else:
            # 创建新的默认策略
            default_strategy = TradingStrategy(
                strategy_name='默认持仓策略',
                is_active=True,
                description='基于持仓天数的动态止损止盈策略'
            )
            default_strategy.rules_list = default_rules
            default_strategy.save()
        
        return create_success_response(
            data=default_strategy.to_dict(),
            message='默认策略重置成功'
        )
    
    except Exception as e:
        raise e