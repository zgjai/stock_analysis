"""
交易记录管理服务
"""
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from sqlalchemy import and_, or_, desc, asc
from extensions import db
from models.trade_record import TradeRecord, TradeCorrection
from models.configuration import Configuration
from services.base_service import BaseService
from error_handlers import ValidationError, NotFoundError, DatabaseError


class TradingService(BaseService):
    """交易记录管理服务"""
    
    model = TradeRecord
    
    @classmethod
    def create_trade(cls, data: Dict[str, Any]) -> TradeRecord:
        """创建交易记录"""
        try:
            # 验证交易原因是否在配置的选项中
            cls._validate_trade_reason(data.get('trade_type'), data.get('reason'))
            
            # 设置交易日期（如果未提供）
            if 'trade_date' not in data or data['trade_date'] is None:
                data['trade_date'] = datetime.now()
            
            # 创建交易记录
            trade = cls.create(data)
            
            return trade
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise e
            raise DatabaseError(f"创建交易记录失败: {str(e)}")
    
    @classmethod
    def update_trade(cls, trade_id: int, data: Dict[str, Any]) -> TradeRecord:
        """更新交易记录"""
        try:
            # 验证交易原因是否在配置的选项中
            if 'reason' in data:
                trade = cls.get_by_id(trade_id)
                trade_type = data.get('trade_type', trade.trade_type)
                cls._validate_trade_reason(trade_type, data.get('reason'))
            
            # 更新交易记录
            trade = cls.update(trade_id, data)
            
            # 如果是买入记录且更新了相关字段，重新计算止损止盈
            if trade.trade_type == 'buy':
                trade._calculate_risk_reward()
                trade.save()
            
            return trade
        except Exception as e:
            if isinstance(e, (ValidationError, NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"更新交易记录失败: {str(e)}")
    
    @classmethod
    def get_trades(cls, filters: Dict[str, Any] = None, 
                   page: int = None, per_page: int = None,
                   sort_by: str = 'trade_date', sort_order: str = 'desc') -> Dict[str, Any]:
        """获取交易记录列表，支持筛选、分页和排序"""
        try:
            query = cls.model.query
            
            # 应用筛选条件
            if filters:
                query = cls._apply_filters(query, filters)
            
            # 应用排序
            query = cls._apply_sorting(query, sort_by, sort_order)
            
            # 应用分页
            if page and per_page:
                pagination = query.paginate(
                    page=page, 
                    per_page=per_page, 
                    error_out=False
                )
                return {
                    'trades': [trade.to_dict() for trade in pagination.items],
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': pagination.page,
                    'per_page': pagination.per_page,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            else:
                trades = query.all()
                return {
                    'trades': [trade.to_dict() for trade in trades],
                    'total': len(trades)
                }
        except Exception as e:
            raise DatabaseError(f"获取交易记录列表失败: {str(e)}")
    
    @classmethod
    def get_trade_by_id(cls, trade_id: int) -> TradeRecord:
        """根据ID获取交易记录详情"""
        return cls.get_by_id(trade_id)
    
    @classmethod
    def delete_trade(cls, trade_id: int) -> bool:
        """删除交易记录"""
        try:
            # 检查是否有订正记录关联
            corrections = TradeCorrection.query.filter(
                or_(
                    TradeCorrection.original_trade_id == trade_id,
                    TradeCorrection.corrected_trade_id == trade_id
                )
            ).first()
            
            if corrections:
                raise ValidationError("无法删除有订正记录关联的交易记录")
            
            return cls.delete(trade_id)
        except Exception as e:
            if isinstance(e, (ValidationError, NotFoundError)):
                raise e
            raise DatabaseError(f"删除交易记录失败: {str(e)}")
    
    @classmethod
    def calculate_risk_reward(cls, buy_price: float, stop_loss_price: float = None,
                            take_profit_ratio: float = None, sell_ratio: float = None) -> Dict[str, float]:
        """计算止损止盈预期"""
        try:
            result = {}
            
            # 计算预计亏损比例
            if stop_loss_price and buy_price:
                if stop_loss_price >= buy_price:
                    raise ValidationError("止损价格必须小于买入价格")
                result['expected_loss_ratio'] = (buy_price - stop_loss_price) / buy_price
            else:
                result['expected_loss_ratio'] = 0.0
            
            # 计算预计收益率
            if take_profit_ratio and sell_ratio:
                result['expected_profit_ratio'] = take_profit_ratio * sell_ratio
            else:
                result['expected_profit_ratio'] = 0.0
            
            # 计算风险收益比
            if result['expected_loss_ratio'] > 0:
                result['risk_reward_ratio'] = result['expected_profit_ratio'] / result['expected_loss_ratio']
            else:
                result['risk_reward_ratio'] = float('inf') if result['expected_profit_ratio'] > 0 else 0.0
            
            return result
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"计算止损止盈预期失败: {str(e)}")
    
    @classmethod
    def correct_trade_record(cls, original_trade_id: int, corrected_data: Dict[str, Any], 
                           reason: str) -> TradeRecord:
        """订正交易记录"""
        try:
            # 获取原始记录
            original_trade = cls.get_by_id(original_trade_id)
            
            # 验证订正原因
            if not reason or not reason.strip():
                raise ValidationError("订正原因不能为空")
            
            # 标记原始记录为已订正
            original_trade.is_corrected = True
            original_trade.save()
            
            # 创建订正后的新记录
            corrected_data['original_record_id'] = original_trade_id
            corrected_data['correction_reason'] = reason
            corrected_trade = cls.create_trade(corrected_data)
            
            # 记录订正历史
            changed_fields = cls._get_changed_fields(original_trade, corrected_data)
            correction_record = TradeCorrection(
                original_trade_id=original_trade_id,
                corrected_trade_id=corrected_trade.id,
                correction_reason=reason,
                corrected_fields=json.dumps(changed_fields, ensure_ascii=False)
            )
            correction_record.save()
            
            return corrected_trade
        except Exception as e:
            if isinstance(e, (ValidationError, NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"订正交易记录失败: {str(e)}")
    
    @classmethod
    def get_correction_history(cls, trade_id: int) -> List[Dict[str, Any]]:
        """获取交易记录的订正历史"""
        try:
            corrections = TradeCorrection.query.filter(
                or_(
                    TradeCorrection.original_trade_id == trade_id,
                    TradeCorrection.corrected_trade_id == trade_id
                )
            ).order_by(TradeCorrection.created_at.desc()).all()
            
            result = []
            for correction in corrections:
                correction_dict = correction.to_dict()
                correction_dict['corrected_fields'] = json.loads(correction.corrected_fields)
                result.append(correction_dict)
            
            return result
        except Exception as e:
            raise DatabaseError(f"获取订正历史失败: {str(e)}")
    
    @classmethod
    def _validate_trade_reason(cls, trade_type: str, reason: str):
        """验证交易原因是否在配置的选项中"""
        if not reason:
            raise ValidationError("交易原因不能为空")
        
        if trade_type == 'buy':
            valid_reasons = Configuration.get_buy_reasons()
        elif trade_type == 'sell':
            valid_reasons = Configuration.get_sell_reasons()
        else:
            raise ValidationError("无效的交易类型")
        
        if valid_reasons and reason not in valid_reasons:
            raise ValidationError(f"无效的{trade_type}原因: {reason}")
    
    @classmethod
    def _apply_filters(cls, query, filters: Dict[str, Any]):
        """应用筛选条件"""
        if 'stock_code' in filters and filters['stock_code']:
            query = query.filter(cls.model.stock_code == filters['stock_code'])
        
        if 'stock_name' in filters and filters['stock_name']:
            query = query.filter(cls.model.stock_name.like(f"%{filters['stock_name']}%"))
        
        if 'trade_type' in filters and filters['trade_type']:
            query = query.filter(cls.model.trade_type == filters['trade_type'])
        
        if 'reason' in filters and filters['reason']:
            query = query.filter(cls.model.reason == filters['reason'])
        
        if 'start_date' in filters and filters['start_date']:
            start_date = cls._parse_date(filters['start_date'])
            query = query.filter(cls.model.trade_date >= start_date)
        
        if 'end_date' in filters and filters['end_date']:
            end_date = cls._parse_date(filters['end_date'])
            # 结束日期包含当天，所以加1天
            from datetime import timedelta
            end_date = end_date + timedelta(days=1)
            query = query.filter(cls.model.trade_date < end_date)
        
        if 'min_price' in filters and filters['min_price']:
            query = query.filter(cls.model.price >= float(filters['min_price']))
        
        if 'max_price' in filters and filters['max_price']:
            query = query.filter(cls.model.price <= float(filters['max_price']))
        
        if 'is_corrected' in filters:
            query = query.filter(cls.model.is_corrected == bool(filters['is_corrected']))
        
        return query
    
    @classmethod
    def _apply_sorting(cls, query, sort_by: str, sort_order: str):
        """应用排序"""
        if not hasattr(cls.model, sort_by):
            sort_by = 'trade_date'  # 默认按交易日期排序
        
        sort_column = getattr(cls.model, sort_by)
        
        if sort_order.lower() == 'asc':
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        return query
    
    @classmethod
    def _parse_date(cls, date_str: str) -> datetime:
        """解析日期字符串"""
        try:
            if isinstance(date_str, str):
                # 支持多种日期格式
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"无法解析日期格式: {date_str}")
            elif isinstance(date_str, date):
                return datetime.combine(date_str, datetime.min.time())
            elif isinstance(date_str, datetime):
                return date_str
            else:
                raise ValueError(f"无效的日期类型: {type(date_str)}")
        except Exception as e:
            raise ValidationError(f"日期格式错误: {str(e)}")
    
    @classmethod
    def _get_changed_fields(cls, original: TradeRecord, corrected_data: Dict[str, Any]) -> Dict[str, Any]:
        """比较并返回修改的字段"""
        changes = {}
        for field, new_value in corrected_data.items():
            if field in ['original_record_id', 'correction_reason']:
                continue  # 跳过订正相关字段
            
            original_value = getattr(original, field, None)
            if original_value != new_value:
                changes[field] = {
                    'old_value': str(original_value) if original_value is not None else None,
                    'new_value': str(new_value) if new_value is not None else None
                }
        return changes


class TradingConfigService:
    """交易配置管理服务"""
    
    @classmethod
    def get_buy_reasons(cls) -> List[str]:
        """获取买入原因选项"""
        return Configuration.get_buy_reasons()
    
    @classmethod
    def get_sell_reasons(cls) -> List[str]:
        """获取卖出原因选项"""
        return Configuration.get_sell_reasons()
    
    @classmethod
    def set_buy_reasons(cls, reasons: List[str]) -> bool:
        """设置买入原因选项"""
        try:
            if not isinstance(reasons, list):
                raise ValidationError("买入原因必须是列表格式")
            
            if not reasons:
                raise ValidationError("买入原因列表不能为空")
            
            Configuration.set_buy_reasons(reasons)
            return True
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"设置买入原因失败: {str(e)}")
    
    @classmethod
    def set_sell_reasons(cls, reasons: List[str]) -> bool:
        """设置卖出原因选项"""
        try:
            if not isinstance(reasons, list):
                raise ValidationError("卖出原因必须是列表格式")
            
            if not reasons:
                raise ValidationError("卖出原因列表不能为空")
            
            Configuration.set_sell_reasons(reasons)
            return True
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"设置卖出原因失败: {str(e)}")
    
    @classmethod
    def get_all_config(cls) -> Dict[str, List[str]]:
        """获取所有交易配置"""
        return {
            'buy_reasons': cls.get_buy_reasons(),
            'sell_reasons': cls.get_sell_reasons()
        }