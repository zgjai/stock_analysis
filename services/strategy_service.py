"""
交易策略服务
"""
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy import func, and_, or_, desc, asc
from extensions import db
from services.base_service import BaseService
from services.review_service import HoldingService
from models.trading_strategy import TradingStrategy
from models.stock_price import StockPrice
from error_handlers import ValidationError, NotFoundError, DatabaseError


class StrategyService(BaseService):
    """交易策略服务"""
    
    model = TradingStrategy
    
    @classmethod
    def create_strategy(cls, data: Dict[str, Any]) -> TradingStrategy:
        """创建交易策略"""
        try:
            # 验证必填字段
            required_fields = ['strategy_name', 'rules']
            for field in required_fields:
                if field not in data or data[field] is None:
                    raise ValidationError(f"{field}不能为空")
            
            # 验证策略规则格式
            cls._validate_strategy_rules(data['rules'])
            
            # 创建策略
            strategy = TradingStrategy(**data)
            return strategy.save()
            
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise e
            raise DatabaseError(f"创建交易策略失败: {str(e)}")
    
    @classmethod
    def update_strategy(cls, strategy_id: int, data: Dict[str, Any]) -> TradingStrategy:
        """更新交易策略"""
        try:
            strategy = cls.get_by_id(strategy_id)
            
            # 验证策略规则格式（如果有更新）
            if 'rules' in data:
                cls._validate_strategy_rules(data['rules'])
            
            # 更新字段
            for key, value in data.items():
                if hasattr(strategy, key):
                    setattr(strategy, key, value)
            
            return strategy.save()
            
        except Exception as e:
            if isinstance(e, (ValidationError, NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"更新交易策略失败: {str(e)}")
    
    @classmethod
    def get_strategies(cls, filters: Dict[str, Any] = None, page: int = None, 
                      per_page: int = None, sort_by: str = 'created_at', 
                      sort_order: str = 'desc') -> Dict[str, Any]:
        """获取交易策略列表"""
        try:
            query = TradingStrategy.query
            
            # 应用筛选条件
            if filters:
                if filters.get('is_active') is not None:
                    query = query.filter(TradingStrategy.is_active == filters['is_active'])
                
                if filters.get('strategy_name'):
                    query = query.filter(TradingStrategy.strategy_name.like(f"%{filters['strategy_name']}%"))
            
            # 应用排序
            if hasattr(TradingStrategy, sort_by):
                order_func = desc if sort_order.lower() == 'desc' else asc
                query = query.order_by(order_func(getattr(TradingStrategy, sort_by)))
            
            # 应用分页
            if page and per_page:
                pagination = query.paginate(
                    page=page,
                    per_page=per_page,
                    error_out=False
                )
                
                return {
                    'strategies': [strategy.to_dict() for strategy in pagination.items],
                    'pagination': {
                        'page': pagination.page,
                        'per_page': pagination.per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_prev': pagination.has_prev,
                        'has_next': pagination.has_next
                    }
                }
            else:
                strategies = query.all()
                return {
                    'strategies': [strategy.to_dict() for strategy in strategies],
                    'total': len(strategies)
                }
                
        except Exception as e:
            raise DatabaseError(f"获取交易策略失败: {str(e)}")
    
    @classmethod
    def activate_strategy(cls, strategy_id: int) -> TradingStrategy:
        """激活策略"""
        try:
            strategy = cls.get_by_id(strategy_id)
            return strategy.activate()
        except Exception as e:
            if isinstance(e, (NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"激活策略失败: {str(e)}")
    
    @classmethod
    def deactivate_strategy(cls, strategy_id: int) -> TradingStrategy:
        """停用策略"""
        try:
            strategy = cls.get_by_id(strategy_id)
            return strategy.deactivate()
        except Exception as e:
            if isinstance(e, (NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"停用策略失败: {str(e)}")
    
    @classmethod
    def get_active_strategies(cls) -> List[TradingStrategy]:
        """获取所有激活的策略"""
        try:
            return TradingStrategy.get_active_strategies()
        except Exception as e:
            raise DatabaseError(f"获取激活策略失败: {str(e)}")
    
    @classmethod
    def _validate_strategy_rules(cls, rules):
        """验证策略规则格式"""
        if isinstance(rules, str):
            import json
            try:
                rules = json.loads(rules)
            except json.JSONDecodeError:
                raise ValidationError("策略规则必须是有效的JSON格式")
        
        if not isinstance(rules, dict) or 'rules' not in rules:
            raise ValidationError("策略规则必须包含rules字段")
        
        if not isinstance(rules['rules'], list):
            raise ValidationError("策略规则的rules字段必须是数组")
        
        # 验证每个规则的格式
        for i, rule in enumerate(rules['rules']):
            if not isinstance(rule, dict):
                raise ValidationError(f"第{i+1}个规则必须是对象")
            
            # 验证必填字段
            required_fields = ['day_range', 'action', 'condition']
            for field in required_fields:
                if field not in rule:
                    raise ValidationError(f"第{i+1}个规则缺少必填字段: {field}")
            
            # 验证day_range格式
            if not isinstance(rule['day_range'], list) or len(rule['day_range']) != 2:
                raise ValidationError(f"第{i+1}个规则的day_range必须是包含两个元素的数组")
            
            # 验证action值
            valid_actions = ['sell_all', 'sell_partial', 'hold']
            if rule['action'] not in valid_actions:
                raise ValidationError(f"第{i+1}个规则的action必须是: {', '.join(valid_actions)}")
            
            # 如果是部分卖出，必须有sell_ratio
            if rule['action'] == 'sell_partial' and 'sell_ratio' not in rule:
                raise ValidationError(f"第{i+1}个规则的部分卖出操作必须包含sell_ratio字段")


class StrategyEvaluator:
    """策略评估引擎"""
    
    @classmethod
    def evaluate_all_holdings(cls) -> List[Dict[str, Any]]:
        """评估所有持仓的策略提醒"""
        try:
            # 获取当前持仓
            holdings = HoldingService.get_current_holdings()
            
            if not holdings:
                return []
            
            # 获取激活的策略
            active_strategies = StrategyService.get_active_strategies()
            
            if not active_strategies:
                return []
            
            alerts = []
            for holding in holdings:
                stock_code = holding['stock_code']
                
                # 获取当前价格
                current_price = cls._get_current_price(stock_code)
                if current_price is None:
                    continue
                
                # 评估每个激活的策略
                for strategy in active_strategies:
                    alert = cls.evaluate_holding_with_strategy(
                        holding, current_price, strategy
                    )
                    if alert:
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            raise DatabaseError(f"评估持仓策略失败: {str(e)}")
    
    @classmethod
    def evaluate_holding_with_strategy(cls, holding: Dict[str, Any], 
                                     current_price: float, 
                                     strategy: TradingStrategy) -> Optional[Dict[str, Any]]:
        """使用特定策略评估单个持仓"""
        try:
            stock_code = holding['stock_code']
            stock_name = holding['stock_name']
            holding_days = holding['holding_days']
            avg_buy_price = holding['avg_buy_price']
            current_quantity = holding['current_quantity']
            
            # 计算盈亏比例
            profit_loss_ratio = (current_price - avg_buy_price) / avg_buy_price
            
            # 获取策略规则
            rules = strategy.rules_list.get('rules', [])
            
            # 评估每个规则
            for rule in rules:
                if cls._rule_applies_to_holding_days(rule, holding_days):
                    if cls._rule_triggered(rule, profit_loss_ratio, holding_days):
                        return cls._create_holding_alert(
                            stock_code, stock_name, holding_days, avg_buy_price,
                            current_price, current_quantity, profit_loss_ratio,
                            rule, strategy
                        )
            
            return None
            
        except Exception as e:
            raise DatabaseError(f"评估持仓策略失败: {str(e)}")
    
    @classmethod
    def evaluate_single_holding(cls, stock_code: str) -> List[Dict[str, Any]]:
        """评估单个股票的持仓策略"""
        try:
            # 获取持仓信息
            holding = HoldingService.get_holding_by_stock(stock_code)
            if not holding:
                return []
            
            # 获取当前价格
            current_price = cls._get_current_price(stock_code)
            if current_price is None:
                return []
            
            # 获取激活的策略
            active_strategies = StrategyService.get_active_strategies()
            
            alerts = []
            for strategy in active_strategies:
                alert = cls.evaluate_holding_with_strategy(
                    holding, current_price, strategy
                )
                if alert:
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            raise DatabaseError(f"评估单个持仓策略失败: {str(e)}")
    
    @classmethod
    def _rule_applies_to_holding_days(cls, rule: Dict[str, Any], holding_days: int) -> bool:
        """判断规则是否适用于当前持仓天数"""
        day_range = rule.get('day_range', [])
        if len(day_range) != 2:
            return False
        
        start_day, end_day = day_range
        return start_day <= holding_days <= end_day
    
    @classmethod
    def _rule_triggered(cls, rule: Dict[str, Any], profit_loss_ratio: float, 
                       holding_days: int) -> bool:
        """判断策略规则是否触发"""
        condition = rule.get('condition', '')
        
        if condition == 'loss_exceed':
            # 亏损超过阈值
            loss_threshold = rule.get('loss_threshold', 0)
            return profit_loss_ratio <= loss_threshold
        
        elif condition == 'profit_below':
            # 盈利低于阈值
            profit_threshold = rule.get('profit_threshold', 0)
            return profit_loss_ratio < profit_threshold
        
        elif condition == 'profit_exceed':
            # 盈利超过阈值
            profit_threshold = rule.get('profit_threshold', 0)
            return profit_loss_ratio >= profit_threshold
        
        elif condition == 'profit_below_or_drawdown':
            # 盈利低于阈值或回撤超过阈值
            profit_threshold = rule.get('profit_threshold', 0)
            drawdown_threshold = rule.get('drawdown_threshold', 0)
            
            # 这里简化处理，实际应该计算从最高点的回撤
            # 暂时使用当前盈亏比例作为回撤判断
            profit_below = profit_loss_ratio < profit_threshold
            drawdown_exceed = profit_loss_ratio <= -drawdown_threshold
            
            return profit_below or drawdown_exceed
        
        return False
    
    @classmethod
    def _create_holding_alert(cls, stock_code: str, stock_name: str, holding_days: int,
                            buy_price: float, current_price: float, current_quantity: int,
                            profit_loss_ratio: float, rule: Dict[str, Any], 
                            strategy: TradingStrategy) -> Dict[str, Any]:
        """创建持仓提醒"""
        action = rule.get('action', 'hold')
        sell_ratio = rule.get('sell_ratio', 0) if action == 'sell_partial' else 1.0
        
        # 生成提醒消息
        alert_message = cls._generate_alert_message(
            stock_code, holding_days, profit_loss_ratio, rule
        )
        
        return {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'holding_days': holding_days,
            'buy_price': buy_price,
            'current_price': current_price,
            'current_quantity': current_quantity,
            'profit_loss_ratio': round(profit_loss_ratio, 4),
            'profit_loss_amount': round((current_price - buy_price) * current_quantity, 2),
            'alert_type': action,
            'alert_message': alert_message,
            'sell_ratio': sell_ratio,
            'suggested_sell_quantity': int(current_quantity * sell_ratio) if action != 'hold' else 0,
            'strategy_name': strategy.strategy_name,
            'strategy_rule': cls._format_rule_description(rule),
            'triggered_condition': rule.get('condition', ''),
            'created_at': datetime.now().isoformat()
        }
    
    @classmethod
    def _generate_alert_message(cls, stock_code: str, holding_days: int, 
                              profit_loss_ratio: float, rule: Dict[str, Any]) -> str:
        """生成提醒消息"""
        action = rule.get('action', 'hold')
        condition = rule.get('condition', '')
        
        profit_loss_pct = round(profit_loss_ratio * 100, 2)
        
        if action == 'sell_all':
            if condition == 'loss_exceed':
                return f"持仓{holding_days}天，当前亏损{abs(profit_loss_pct)}%，建议全部清仓止损"
            elif condition == 'profit_below':
                profit_threshold = rule.get('profit_threshold', 0) * 100
                return f"持仓{holding_days}天，当前盈利{profit_loss_pct}%低于预期{profit_threshold}%，建议全部清仓"
            elif condition == 'profit_below_or_drawdown':
                return f"持仓{holding_days}天，盈利不达预期或回撤过大，建议全部清仓"
        
        elif action == 'sell_partial':
            sell_ratio = rule.get('sell_ratio', 0) * 100
            return f"持仓{holding_days}天，当前盈利{profit_loss_pct}%，建议部分止盈{sell_ratio}%"
        
        return f"持仓{holding_days}天，当前盈亏{profit_loss_pct}%，建议继续持有"
    
    @classmethod
    def _format_rule_description(cls, rule: Dict[str, Any]) -> str:
        """格式化规则描述"""
        day_range = rule.get('day_range', [])
        action = rule.get('action', 'hold')
        condition = rule.get('condition', '')
        
        day_desc = f"{day_range[0]}-{day_range[1]}天" if len(day_range) == 2 else "未知天数"
        
        if condition == 'loss_exceed':
            threshold = abs(rule.get('loss_threshold', 0) * 100)
            return f"{day_desc}：亏损超过{threshold}%时{cls._get_action_desc(action, rule)}"
        elif condition == 'profit_below':
            threshold = rule.get('profit_threshold', 0) * 100
            return f"{day_desc}：盈利低于{threshold}%时{cls._get_action_desc(action, rule)}"
        elif condition == 'profit_exceed':
            threshold = rule.get('profit_threshold', 0) * 100
            return f"{day_desc}：盈利超过{threshold}%时{cls._get_action_desc(action, rule)}"
        elif condition == 'profit_below_or_drawdown':
            profit_threshold = rule.get('profit_threshold', 0) * 100
            drawdown_threshold = rule.get('drawdown_threshold', 0) * 100
            return f"{day_desc}：盈利低于{profit_threshold}%或回撤超过{drawdown_threshold}%时{cls._get_action_desc(action, rule)}"
        
        return f"{day_desc}：{cls._get_action_desc(action, rule)}"
    
    @classmethod
    def _get_action_desc(cls, action: str, rule: Dict[str, Any]) -> str:
        """获取操作描述"""
        if action == 'sell_all':
            return "全部清仓"
        elif action == 'sell_partial':
            sell_ratio = rule.get('sell_ratio', 0) * 100
            return f"部分止盈{sell_ratio}%"
        else:
            return "继续持有"
    
    @classmethod
    def _get_current_price(cls, stock_code: str) -> Optional[float]:
        """获取股票当前价格"""
        try:
            # 从股票价格缓存表获取最新价格
            latest_price = StockPrice.query.filter_by(stock_code=stock_code)\
                .order_by(StockPrice.record_date.desc()).first()
            
            if latest_price:
                return float(latest_price.current_price)
            
            return None
            
        except Exception as e:
            print(f"获取股票{stock_code}价格失败: {e}")
            return None


class HoldingAlertService:
    """持仓提醒服务"""
    
    @classmethod
    def get_all_alerts(cls) -> List[Dict[str, Any]]:
        """获取所有持仓提醒"""
        return StrategyEvaluator.evaluate_all_holdings()
    
    @classmethod
    def get_alerts_by_stock(cls, stock_code: str) -> List[Dict[str, Any]]:
        """获取特定股票的持仓提醒"""
        return StrategyEvaluator.evaluate_single_holding(stock_code)
    
    @classmethod
    def get_alerts_by_type(cls, alert_type: str) -> List[Dict[str, Any]]:
        """按提醒类型筛选提醒"""
        all_alerts = cls.get_all_alerts()
        return [alert for alert in all_alerts if alert['alert_type'] == alert_type]
    
    @classmethod
    def get_urgent_alerts(cls) -> List[Dict[str, Any]]:
        """获取紧急提醒（止损提醒）"""
        all_alerts = cls.get_all_alerts()
        urgent_alerts = []
        
        for alert in all_alerts:
            # 亏损超过5%或触发止损条件的提醒视为紧急
            if (alert['profit_loss_ratio'] <= -0.05 or 
                alert['triggered_condition'] == 'loss_exceed'):
                urgent_alerts.append(alert)
        
        return urgent_alerts
    
    @classmethod
    def get_profit_alerts(cls) -> List[Dict[str, Any]]:
        """获取止盈提醒"""
        all_alerts = cls.get_all_alerts()
        return [alert for alert in all_alerts 
                if alert['alert_type'] in ['sell_all', 'sell_partial'] 
                and alert['profit_loss_ratio'] > 0]
    
    @classmethod
    def get_alerts_summary(cls) -> Dict[str, Any]:
        """获取提醒汇总信息"""
        all_alerts = cls.get_all_alerts()
        
        summary = {
            'total_alerts': len(all_alerts),
            'urgent_alerts': len(cls.get_urgent_alerts()),
            'profit_alerts': len(cls.get_profit_alerts()),
            'sell_all_alerts': len([a for a in all_alerts if a['alert_type'] == 'sell_all']),
            'sell_partial_alerts': len([a for a in all_alerts if a['alert_type'] == 'sell_partial']),
            'hold_alerts': len([a for a in all_alerts if a['alert_type'] == 'hold']),
            'alerts_by_stock': {}
        }
        
        # 按股票分组统计
        for alert in all_alerts:
            stock_code = alert['stock_code']
            if stock_code not in summary['alerts_by_stock']:
                summary['alerts_by_stock'][stock_code] = {
                    'stock_name': alert['stock_name'],
                    'alert_count': 0,
                    'most_urgent_alert': None
                }
            
            summary['alerts_by_stock'][stock_code]['alert_count'] += 1
            
            # 记录最紧急的提醒
            current_urgent = summary['alerts_by_stock'][stock_code]['most_urgent_alert']
            if (current_urgent is None or 
                alert['profit_loss_ratio'] < current_urgent.get('profit_loss_ratio', 0)):
                summary['alerts_by_stock'][stock_code]['most_urgent_alert'] = alert
        
        return summary