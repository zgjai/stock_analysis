"""
分批止盈服务
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from extensions import db
from models.profit_taking_target import ProfitTakingTarget
from models.trade_record import TradeRecord
from services.base_service import BaseService
from error_handlers import ValidationError, NotFoundError, DatabaseError


class ProfitTakingService(BaseService):
    """分批止盈管理服务"""
    
    model = ProfitTakingTarget
    
    @classmethod
    def create_profit_targets(cls, trade_id: int, targets: List[Dict]) -> List[ProfitTakingTarget]:
        """
        为指定交易记录创建止盈目标
        
        Args:
            trade_id: 交易记录ID
            targets: 止盈目标数据列表
            
        Returns:
            List[ProfitTakingTarget]: 创建的止盈目标列表
            
        Raises:
            ValidationError: 数据验证失败
            NotFoundError: 交易记录不存在
            DatabaseError: 数据库操作失败
        """
        try:
            # 验证交易记录是否存在
            trade_record = TradeRecord.get_by_id(trade_id)
            if not trade_record:
                raise NotFoundError(f"交易记录 {trade_id} 不存在")
            
            # 验证交易记录是否为买入记录
            if trade_record.trade_type != 'buy':
                raise ValidationError("只有买入记录才能设置止盈目标", "trade_type")
            
            # 获取买入价格用于验证
            buy_price = float(trade_record.price)
            
            # 验证止盈目标数据
            cls.validate_targets_total_ratio(targets)
            cls.validate_targets_against_buy_price(buy_price, targets)
            
            # 删除现有的止盈目标
            ProfitTakingTarget.delete_by_trade_record(trade_id)
            
            # 创建新的止盈目标
            created_targets = []
            
            for i, target_data in enumerate(targets):
                # 标准化字段名格式（前端格式 → 数据库格式）
                normalized_data = {
                    'trade_record_id': trade_id,
                    'sequence_order': i + 1
                }
                
                # 处理止盈价格
                target_price = target_data.get('target_price') or target_data.get('targetPrice')
                if target_price is not None:
                    normalized_data['target_price'] = target_price
                
                # 处理止盈比例
                profit_ratio = target_data.get('profit_ratio') or target_data.get('profitRatio')
                if profit_ratio is not None:
                    # 如果是百分比格式（>1），转换为小数格式
                    if float(profit_ratio) > 1:
                        normalized_data['profit_ratio'] = float(profit_ratio) / 100
                    else:
                        normalized_data['profit_ratio'] = float(profit_ratio)
                
                # 处理卖出比例
                sell_ratio = target_data.get('sell_ratio') or target_data.get('sellRatio')
                if sell_ratio is not None:
                    # 如果是百分比格式（>1），转换为小数格式
                    if float(sell_ratio) > 1:
                        normalized_data['sell_ratio'] = float(sell_ratio) / 100
                    else:
                        normalized_data['sell_ratio'] = float(sell_ratio)
                
                # 处理序列顺序
                sequence_order = target_data.get('sequence_order') or target_data.get('sequenceOrder')
                if sequence_order is not None:
                    normalized_data['sequence_order'] = int(sequence_order)
                
                # 创建止盈目标
                target = ProfitTakingTarget(**normalized_data)
                
                # 验证相对于买入价格的合理性（模型级别验证）
                target.validate_against_buy_price(buy_price)
                
                # 保存到数据库
                target.save()
                created_targets.append(target)
            
            # 更新交易记录的分批止盈标志
            trade_record.use_batch_profit_taking = True
            trade_record.save()
            
            return created_targets
            
        except Exception as e:
            db.session.rollback()
            if isinstance(e, (ValidationError, NotFoundError)):
                raise e
            raise DatabaseError(f"创建止盈目标失败: {str(e)}")
    
    @classmethod
    def update_profit_targets(cls, trade_id: int, targets: List[Dict]) -> List[ProfitTakingTarget]:
        """
        更新指定交易记录的止盈目标
        
        Args:
            trade_id: 交易记录ID
            targets: 止盈目标数据列表
            
        Returns:
            List[ProfitTakingTarget]: 更新后的止盈目标列表
            
        Raises:
            ValidationError: 数据验证失败
            NotFoundError: 交易记录不存在
            DatabaseError: 数据库操作失败
        """
        try:
            # 验证交易记录是否存在
            trade_record = TradeRecord.get_by_id(trade_id)
            if not trade_record:
                raise NotFoundError(f"交易记录 {trade_id} 不存在")
            
            # 获取买入价格用于验证
            buy_price = float(trade_record.price)
            
            # 验证止盈目标数据
            cls.validate_targets_total_ratio(targets)
            cls.validate_targets_against_buy_price(buy_price, targets)
            
            # 重新创建所有止盈目标（简化更新逻辑）
            return cls.create_profit_targets(trade_id, targets)
            
        except Exception as e:
            if isinstance(e, (ValidationError, NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"更新止盈目标失败: {str(e)}")
    
    @classmethod
    def get_profit_targets(cls, trade_id: int) -> List[ProfitTakingTarget]:
        """
        获取指定交易记录的所有止盈目标
        
        Args:
            trade_id: 交易记录ID
            
        Returns:
            List[ProfitTakingTarget]: 止盈目标列表
            
        Raises:
            NotFoundError: 交易记录不存在
        """
        try:
            # 验证交易记录是否存在
            trade_record = TradeRecord.get_by_id(trade_id)
            if not trade_record:
                raise NotFoundError(f"交易记录 {trade_id} 不存在")
            
            return ProfitTakingTarget.get_by_trade_record(trade_id)
            
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise e
            raise DatabaseError(f"获取止盈目标失败: {str(e)}")
    
    @classmethod
    def delete_profit_targets(cls, trade_id: int) -> bool:
        """
        删除指定交易记录的所有止盈目标
        
        Args:
            trade_id: 交易记录ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            NotFoundError: 交易记录不存在
            DatabaseError: 数据库操作失败
        """
        try:
            # 验证交易记录是否存在
            trade_record = TradeRecord.get_by_id(trade_id)
            if not trade_record:
                raise NotFoundError(f"交易记录 {trade_id} 不存在")
            
            # 删除止盈目标
            ProfitTakingTarget.delete_by_trade_record(trade_id)
            
            # 更新交易记录的分批止盈标志
            trade_record.use_batch_profit_taking = False
            trade_record.save()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            if isinstance(e, NotFoundError):
                raise e
            raise DatabaseError(f"删除止盈目标失败: {str(e)}")
    
    @classmethod
    def validate_targets_total_ratio(cls, targets: List[Dict]) -> bool:
        """
        验证止盈目标的卖出比例总和
        
        Args:
            targets: 止盈目标数据列表
            
        Returns:
            bool: 验证是否通过
            
        Raises:
            ValidationError: 验证失败
        """
        if not targets:
            return True  # 允许空目标，不强制要求
        
        total_sell_ratio = Decimal('0')
        validation_errors = {}
        
        for i, target in enumerate(targets):
            target_errors = {}
            
            # 验证必需字段 - 支持多种字段名
            sell_ratio_value = target.get('sell_ratio') or target.get('sellRatio')
            if sell_ratio_value is None or sell_ratio_value == '':
                target_errors['sell_ratio'] = "卖出比例不能为空"
            else:
                try:
                    sell_ratio = Decimal(str(sell_ratio_value))
                    
                    # 验证卖出比例范围 - 智能识别百分比和小数格式
                    if sell_ratio <= 0:
                        target_errors['sell_ratio'] = "卖出比例必须大于0"
                    elif sell_ratio > 100:  # 百分比格式最大100
                        target_errors['sell_ratio'] = "卖出比例不能超过100%"
                    else:
                        # 如果是百分比格式（>1），转换为小数格式进行累计
                        if sell_ratio > 1:
                            total_sell_ratio += sell_ratio / 100
                        else:
                            total_sell_ratio += sell_ratio
                        
                except (ValueError, TypeError, Exception):
                    target_errors['sell_ratio'] = "卖出比例格式无效"
            
            # 验证止盈价格（如果提供）
            target_price_value = target.get('target_price') or target.get('targetPrice')
            if target_price_value is not None and target_price_value != '':
                try:
                    target_price = Decimal(str(target_price_value))
                    if target_price <= 0:
                        target_errors['target_price'] = "止盈价格必须大于0"
                except (ValueError, TypeError, Exception):
                    target_errors['target_price'] = "止盈价格格式无效"
            
            # 验证止盈比例（如果提供）
            profit_ratio_value = target.get('profit_ratio') or target.get('profitRatio')
            if profit_ratio_value is not None and profit_ratio_value != '':
                try:
                    profit_ratio = Decimal(str(profit_ratio_value))
                    if profit_ratio < 0:
                        target_errors['profit_ratio'] = "止盈比例不能为负数"
                    elif profit_ratio > 1000:  # 支持百分比格式，最大1000%
                        target_errors['profit_ratio'] = "止盈比例不能超过1000%"
                except (ValueError, TypeError, Exception):
                    target_errors['profit_ratio'] = "止盈比例格式无效"
            
            # 验证序列顺序（如果提供）
            sequence_order_value = target.get('sequence_order') or target.get('sequenceOrder')
            if sequence_order_value is not None and sequence_order_value != '':
                try:
                    sequence_order = int(sequence_order_value)
                    if sequence_order <= 0:
                        target_errors['sequence_order'] = "序列顺序必须是正整数"
                except (ValueError, TypeError):
                    target_errors['sequence_order'] = "序列顺序格式无效"
            
            if target_errors:
                validation_errors[f'targets[{i}]'] = target_errors
        
        # 验证总卖出比例不能超过100% - 智能处理百分比和小数格式
        max_ratio = Decimal('1')  # 小数格式的100%
        display_ratio = float(total_sell_ratio) * 100
        
        if total_sell_ratio > max_ratio:
            validation_errors['total_sell_ratio'] = f"所有止盈目标的卖出比例总和不能超过100%，当前为{display_ratio:.2f}%"
        
        # 如果有验证错误，抛出详细的错误信息
        if validation_errors:
            error = ValidationError("止盈目标数据验证失败", "profit_targets")
            error.details = validation_errors
            raise error
        
        return True
    
    @classmethod
    def validate_targets_against_buy_price(cls, buy_price: float, targets: List[Dict]) -> bool:
        """
        验证止盈目标相对于买入价格的合理性
        
        Args:
            buy_price: 买入价格
            targets: 止盈目标数据列表
            
        Returns:
            bool: 验证是否通过
            
        Raises:
            ValidationError: 验证失败
        """
        if not buy_price or buy_price <= 0:
            raise ValidationError("买入价格必须大于0", "buy_price")
        
        validation_errors = {}
        buy_price_decimal = Decimal(str(buy_price))
        
        for i, target in enumerate(targets):
            target_errors = {}
            
            # 验证止盈价格必须大于买入价格
            target_price_value = target.get('target_price') or target.get('targetPrice')
            if target_price_value is not None and target_price_value != '':
                try:
                    target_price = Decimal(str(target_price_value))
                    if target_price <= buy_price_decimal:
                        target_errors['target_price'] = f"止盈价格({target_price})必须大于买入价格({buy_price})"
                    elif target_price > buy_price_decimal * Decimal('10'):  # 防止设置过高的止盈价格
                        target_errors['target_price'] = f"止盈价格不应超过买入价格的10倍"
                except (ValueError, TypeError, Exception):
                    target_errors['target_price'] = "止盈价格格式无效"
            
            # 验证止盈比例的合理性
            if 'profit_ratio' in target and target['profit_ratio'] is not None:
                try:
                    profit_ratio = Decimal(str(target['profit_ratio']))
                    if profit_ratio < 0:
                        target_errors['profit_ratio'] = "止盈比例不能为负数"
                    elif profit_ratio > Decimal('9'):  # 900%
                        target_errors['profit_ratio'] = "止盈比例不应超过900%"
                except (ValueError, TypeError, Exception):
                    target_errors['profit_ratio'] = "止盈比例格式无效"
            
            # 如果同时提供了止盈价格和止盈比例，验证它们的一致性
            if ('target_price' in target and target['target_price'] is not None and
                'profit_ratio' in target and target['profit_ratio'] is not None):
                try:
                    target_price = Decimal(str(target['target_price']))
                    profit_ratio = Decimal(str(target['profit_ratio']))
                    
                    # 根据价格计算的比例
                    calculated_ratio = (target_price - buy_price_decimal) / buy_price_decimal
                    
                    # 允许5%的误差范围
                    if abs(calculated_ratio - profit_ratio) > Decimal('0.05'):
                        target_errors['consistency'] = "止盈价格和止盈比例不一致"
                        
                except (ValueError, TypeError, ZeroDivisionError, Exception):
                    pass  # 格式错误已在上面处理
            
            if target_errors:
                validation_errors[f'targets[{i}]'] = target_errors
        
        # 如果有验证错误，抛出详细的错误信息
        if validation_errors:
            error = ValidationError("止盈目标与买入价格验证失败", "profit_targets_buy_price")
            error.details = validation_errors
            raise error
        
        return True
    
    @classmethod
    def calculate_targets_expected_profit(cls, buy_price: float, targets: List[Dict]) -> Dict[str, Any]:
        """
        计算止盈目标的预期收益信息
        
        Args:
            buy_price: 买入价格
            targets: 止盈目标数据列表
            
        Returns:
            Dict: 包含总体预期收益率、总卖出比例等信息
            
        Raises:
            ValidationError: 数据验证失败
        """
        if not buy_price or buy_price <= 0:
            raise ValidationError("买入价格必须大于0", "buy_price")
        
        if not targets:
            return {
                'total_expected_profit_ratio': 0.0,
                'total_sell_ratio': 0.0,
                'targets_detail': []
            }
        
        total_expected_profit = Decimal('0')
        total_sell_ratio = Decimal('0')
        targets_detail = []
        
        buy_price_decimal = Decimal(str(buy_price))
        
        for i, target in enumerate(targets):
            try:
                # 支持多种字段名和格式
                sell_ratio_value = target.get('sell_ratio') or target.get('sellRatio', 0)
                sell_ratio = Decimal(str(sell_ratio_value))
                
                # 如果是百分比格式（>1），转换为小数格式
                if sell_ratio > 1:
                    sell_ratio = sell_ratio / 100
                
                # 计算止盈比例
                profit_ratio = Decimal('0')
                target_price_value = target.get('target_price') or target.get('targetPrice')
                if target_price_value:
                    try:
                        target_price = Decimal(str(target_price_value))
                        if target_price > buy_price_decimal:
                            profit_ratio = (target_price - buy_price_decimal) / buy_price_decimal
                    except (ValueError, TypeError, Exception):
                        raise ValidationError(f"第{i+1}个止盈目标的价格格式无效", f"targets[{i}]")
                elif 'profit_ratio' in target and target['profit_ratio']:
                    try:
                        profit_ratio = Decimal(str(target['profit_ratio']))
                    except (ValueError, TypeError, Exception):
                        raise ValidationError(f"第{i+1}个止盈目标的比例格式无效", f"targets[{i}]")
                
                # 计算预期收益率
                expected_profit_ratio = profit_ratio * sell_ratio
                
                # 累计总值
                total_expected_profit += expected_profit_ratio
                total_sell_ratio += sell_ratio
                
                # 记录详细信息
                targets_detail.append({
                    'sequence_order': i + 1,
                    'target_price': float(target.get('target_price', 0)) if target.get('target_price') else None,
                    'profit_ratio': float(profit_ratio),
                    'sell_ratio': float(sell_ratio),
                    'expected_profit_ratio': float(expected_profit_ratio)
                })
                
            except (ValueError, TypeError) as e:
                raise ValidationError(f"第{i+1}个止盈目标的数据格式无效: {str(e)}", f"targets[{i}]")
        
        return {
            'total_expected_profit_ratio': float(total_expected_profit),
            'total_sell_ratio': float(total_sell_ratio),
            'targets_detail': targets_detail
        }
    
    @classmethod
    def get_targets_summary(cls, trade_id: int) -> Dict[str, Any]:
        """
        获取指定交易记录的止盈目标汇总信息
        
        Args:
            trade_id: 交易记录ID
            
        Returns:
            Dict: 止盈目标汇总信息
            
        Raises:
            NotFoundError: 交易记录不存在
        """
        try:
            # 获取交易记录
            trade_record = TradeRecord.get_by_id(trade_id)
            if not trade_record:
                raise NotFoundError(f"交易记录 {trade_id} 不存在")
            
            # 获取止盈目标
            targets = cls.get_profit_targets(trade_id)
            
            if not targets:
                return {
                    'trade_id': trade_id,
                    'use_batch_profit_taking': trade_record.use_batch_profit_taking,
                    'total_expected_profit_ratio': 0.0,
                    'total_sell_ratio': 0.0,
                    'targets_count': 0,
                    'targets': []
                }
            
            # 转换为字典格式
            targets_data = [target.to_dict() for target in targets]
            
            # 计算汇总信息
            buy_price = float(trade_record.price)
            summary = cls.calculate_targets_expected_profit(buy_price, targets_data)
            
            return {
                'trade_id': trade_id,
                'use_batch_profit_taking': trade_record.use_batch_profit_taking,
                'total_expected_profit_ratio': summary['total_expected_profit_ratio'],
                'total_sell_ratio': summary['total_sell_ratio'],
                'targets_count': len(targets),
                'targets': targets_data
            }
            
        except Exception as e:
            if isinstance(e, (NotFoundError, ValidationError)):
                raise e
            raise DatabaseError(f"获取止盈目标汇总信息失败: {str(e)}")
    
    @classmethod
    def delete_profit_targets(cls, trade_id: int) -> bool:
        """
        删除指定交易记录的所有止盈目标
        
        Args:
            trade_id: 交易记录ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            NotFoundError: 交易记录不存在
            DatabaseError: 数据库操作失败
        """
        try:
            # 验证交易记录是否存在
            trade_record = TradeRecord.get_by_id(trade_id)
            if not trade_record:
                raise NotFoundError(f"交易记录 {trade_id} 不存在")
            
            # 直接删除所有相关的止盈目标记录
            deleted_count = ProfitTakingTarget.query.filter_by(trade_record_id=trade_id).delete()
            
            # 更新交易记录的分批止盈标志
            if deleted_count > 0:
                trade_record.use_batch_profit_taking = False
                trade_record.save()
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            if isinstance(e, NotFoundError):
                raise e
            raise DatabaseError(f"删除止盈目标失败: {str(e)}")