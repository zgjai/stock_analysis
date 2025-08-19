"""
分批止盈功能数据兼容性处理工具
"""
from typing import Dict, List, Any, Optional
from extensions import db
from models.trade_record import TradeRecord
from models.profit_taking_target import ProfitTakingTarget
from services.profit_taking_service import ProfitTakingService
from error_handlers import ValidationError, DatabaseError


class BatchProfitCompatibilityHandler:
    """分批止盈功能兼容性处理器"""
    
    @classmethod
    def ensure_compatibility(cls) -> Dict[str, Any]:
        """确保数据兼容性，为现有交易记录设置默认值"""
        try:
            result = {
                'updated_records': 0,
                'errors': [],
                'warnings': []
            }
            
            # 1. 为现有交易记录设置默认的 use_batch_profit_taking = False
            updated_count = cls._set_default_batch_profit_flag()
            result['updated_records'] = updated_count
            
            # 2. 验证现有数据的完整性
            validation_result = cls._validate_existing_data()
            result['warnings'].extend(validation_result.get('warnings', []))
            result['errors'].extend(validation_result.get('errors', []))
            
            return result
            
        except Exception as e:
            raise DatabaseError(f"兼容性处理失败: {str(e)}")
    
    @classmethod
    def _set_default_batch_profit_flag(cls) -> int:
        """为现有交易记录设置默认的分批止盈标志"""
        try:
            # 查找所有 use_batch_profit_taking 为 NULL 的记录
            records_to_update = TradeRecord.query.filter(
                TradeRecord.use_batch_profit_taking.is_(None)
            ).all()
            
            updated_count = 0
            for record in records_to_update:
                record.use_batch_profit_taking = False
                updated_count += 1
            
            if updated_count > 0:
                db.session.commit()
            
            return updated_count
            
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"设置默认分批止盈标志失败: {str(e)}")
    
    @classmethod
    def _validate_existing_data(cls) -> Dict[str, List[str]]:
        """验证现有数据的完整性"""
        result = {
            'warnings': [],
            'errors': []
        }
        
        try:
            # 检查是否有使用分批止盈但没有止盈目标的记录
            batch_profit_records = TradeRecord.query.filter(
                TradeRecord.use_batch_profit_taking == True
            ).all()
            
            for record in batch_profit_records:
                targets_count = ProfitTakingTarget.query.filter(
                    ProfitTakingTarget.trade_record_id == record.id
                ).count()
                
                if targets_count == 0:
                    result['warnings'].append(
                        f"交易记录 {record.id} 启用了分批止盈但没有止盈目标"
                    )
            
            # 检查是否有孤立的止盈目标记录
            orphaned_targets = db.session.query(ProfitTakingTarget).outerjoin(
                TradeRecord, ProfitTakingTarget.trade_record_id == TradeRecord.id
            ).filter(TradeRecord.id.is_(None)).all()
            
            for target in orphaned_targets:
                result['errors'].append(
                    f"止盈目标 {target.id} 关联的交易记录不存在"
                )
            
            return result
            
        except Exception as e:
            result['errors'].append(f"数据验证失败: {str(e)}")
            return result
    
    @classmethod
    def migrate_single_to_batch_profit(cls, trade_id: int) -> Dict[str, Any]:
        """将单一止盈记录迁移为分批止盈"""
        try:
            trade = TradeRecord.query.get(trade_id)
            if not trade:
                raise ValidationError(f"交易记录 {trade_id} 不存在")
            
            if trade.use_batch_profit_taking:
                return {
                    'success': False,
                    'message': '该交易记录已经使用分批止盈'
                }
            
            if trade.trade_type != 'buy':
                return {
                    'success': False,
                    'message': '只有买入记录才能设置分批止盈'
                }
            
            # 检查是否有传统止盈设置
            if not trade.take_profit_ratio or not trade.sell_ratio:
                return {
                    'success': False,
                    'message': '该交易记录没有传统止盈设置，无法迁移'
                }
            
            # 创建分批止盈目标
            target_data = {
                'target_price': None,  # 将根据止盈比例计算
                'profit_ratio': float(trade.take_profit_ratio),
                'sell_ratio': float(trade.sell_ratio),
                'sequence_order': 1
            }
            
            # 计算止盈价格
            if trade.price:
                target_data['target_price'] = float(trade.price) * (1 + target_data['profit_ratio'])
            
            # 创建止盈目标
            ProfitTakingService.create_profit_targets(trade_id, [target_data])
            
            # 更新交易记录标志
            trade.use_batch_profit_taking = True
            trade.save()
            
            return {
                'success': True,
                'message': '成功迁移为分批止盈',
                'migrated_target': target_data
            }
            
        except Exception as e:
            db.session.rollback()
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"迁移失败: {str(e)}")
    
    @classmethod
    def migrate_batch_to_single_profit(cls, trade_id: int) -> Dict[str, Any]:
        """将分批止盈记录迁移为单一止盈"""
        try:
            trade = TradeRecord.query.get(trade_id)
            if not trade:
                raise ValidationError(f"交易记录 {trade_id} 不存在")
            
            if not trade.use_batch_profit_taking:
                return {
                    'success': False,
                    'message': '该交易记录没有使用分批止盈'
                }
            
            # 获取止盈目标
            targets = ProfitTakingService.get_profit_targets(trade_id)
            if not targets:
                return {
                    'success': False,
                    'message': '该交易记录没有止盈目标，无法迁移'
                }
            
            if len(targets) > 1:
                return {
                    'success': False,
                    'message': '该交易记录有多个止盈目标，无法直接迁移为单一止盈'
                }
            
            # 使用第一个（也是唯一的）止盈目标
            target = targets[0]
            
            # 更新交易记录的传统止盈字段
            trade.take_profit_ratio = target.profit_ratio
            trade.sell_ratio = target.sell_ratio
            trade.use_batch_profit_taking = False
            
            # 重新计算预期收益率
            trade._calculate_risk_reward()
            trade.save()
            
            # 保存交易记录更改
            trade.save()
            
            # 删除止盈目标记录
            ProfitTakingService.delete_profit_targets(trade_id)
            
            return {
                'success': True,
                'message': '成功迁移为单一止盈',
                'migrated_data': {
                    'take_profit_ratio': float(target.profit_ratio),
                    'sell_ratio': float(target.sell_ratio)
                }
            }
            
        except Exception as e:
            db.session.rollback()
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"迁移失败: {str(e)}")
    
    @classmethod
    def get_compatibility_status(cls) -> Dict[str, Any]:
        """获取兼容性状态报告"""
        try:
            # 统计各种类型的交易记录
            total_records = TradeRecord.query.count()
            batch_profit_records = TradeRecord.query.filter(
                TradeRecord.use_batch_profit_taking == True
            ).count()
            single_profit_records = TradeRecord.query.filter(
                TradeRecord.use_batch_profit_taking == False
            ).count()
            null_flag_records = TradeRecord.query.filter(
                TradeRecord.use_batch_profit_taking.is_(None)
            ).count()
            
            # 统计止盈目标
            total_targets = ProfitTakingTarget.query.count()
            
            # 检查数据一致性
            inconsistent_records = []
            
            # 检查启用分批止盈但没有目标的记录
            batch_without_targets = db.session.query(TradeRecord).outerjoin(
                ProfitTakingTarget, TradeRecord.id == ProfitTakingTarget.trade_record_id
            ).filter(
                TradeRecord.use_batch_profit_taking == True,
                ProfitTakingTarget.id.is_(None)
            ).count()
            
            if batch_without_targets > 0:
                inconsistent_records.append(
                    f"{batch_without_targets} 条记录启用了分批止盈但没有止盈目标"
                )
            
            # 检查有目标但未启用分批止盈的记录
            targets_without_batch = db.session.query(TradeRecord).join(
                ProfitTakingTarget, TradeRecord.id == ProfitTakingTarget.trade_record_id
            ).filter(
                TradeRecord.use_batch_profit_taking == False
            ).count()
            
            if targets_without_batch > 0:
                inconsistent_records.append(
                    f"{targets_without_batch} 条记录有止盈目标但未启用分批止盈"
                )
            
            return {
                'total_records': total_records,
                'batch_profit_records': batch_profit_records,
                'single_profit_records': single_profit_records,
                'null_flag_records': null_flag_records,
                'total_profit_targets': total_targets,
                'inconsistent_records': inconsistent_records,
                'is_compatible': null_flag_records == 0 and len(inconsistent_records) == 0
            }
            
        except Exception as e:
            raise DatabaseError(f"获取兼容性状态失败: {str(e)}")
    
    @classmethod
    def fix_data_inconsistencies(cls) -> Dict[str, Any]:
        """修复数据不一致问题"""
        try:
            result = {
                'fixed_records': 0,
                'errors': []
            }
            
            # 1. 修复启用分批止盈但没有目标的记录
            batch_without_targets = db.session.query(TradeRecord).outerjoin(
                ProfitTakingTarget, TradeRecord.id == ProfitTakingTarget.trade_record_id
            ).filter(
                TradeRecord.use_batch_profit_taking == True,
                ProfitTakingTarget.id.is_(None)
            ).all()
            
            for record in batch_without_targets:
                try:
                    # 如果有传统止盈设置，创建对应的止盈目标
                    if record.take_profit_ratio and record.sell_ratio:
                        target_data = {
                            'profit_ratio': float(record.take_profit_ratio),
                            'sell_ratio': float(record.sell_ratio),
                            'sequence_order': 1
                        }
                        
                        if record.price:
                            target_data['target_price'] = float(record.price) * (1 + target_data['profit_ratio'])
                        
                        ProfitTakingService.create_profit_targets(record.id, [target_data])
                        result['fixed_records'] += 1
                    else:
                        # 没有传统止盈设置，取消分批止盈标志
                        record.use_batch_profit_taking = False
                        record.save()
                        result['fixed_records'] += 1
                        
                except Exception as e:
                    result['errors'].append(f"修复记录 {record.id} 失败: {str(e)}")
            
            # 2. 修复有目标但未启用分批止盈的记录
            targets_without_batch = db.session.query(TradeRecord).join(
                ProfitTakingTarget, TradeRecord.id == ProfitTakingTarget.trade_record_id
            ).filter(
                TradeRecord.use_batch_profit_taking == False
            ).all()
            
            for record in targets_without_batch:
                try:
                    record.use_batch_profit_taking = True
                    record.save()
                    result['fixed_records'] += 1
                except Exception as e:
                    result['errors'].append(f"修复记录 {record.id} 失败: {str(e)}")
            
            if result['fixed_records'] > 0:
                db.session.commit()
            
            return result
            
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"修复数据不一致问题失败: {str(e)}")


class LegacyDataHandler:
    """遗留数据处理器"""
    
    @classmethod
    def get_legacy_profit_data(cls, trade: TradeRecord) -> Optional[Dict[str, Any]]:
        """获取遗留的止盈数据（用于向后兼容）"""
        if trade.use_batch_profit_taking:
            return None
        
        # 返回传统的止盈数据
        return {
            'take_profit_ratio': float(trade.take_profit_ratio) if trade.take_profit_ratio else None,
            'sell_ratio': float(trade.sell_ratio) if trade.sell_ratio else None,
            'expected_profit_ratio': float(trade.expected_profit_ratio) if trade.expected_profit_ratio else None
        }
    
    @classmethod
    def ensure_backward_compatibility(cls, trade_dict: Dict[str, Any]) -> Dict[str, Any]:
        """确保交易记录字典的向后兼容性"""
        # 如果没有使用分批止盈，确保传统字段存在
        if not trade_dict.get('use_batch_profit_taking', False):
            # 确保传统字段存在且有默认值
            trade_dict.setdefault('take_profit_ratio', None)
            trade_dict.setdefault('sell_ratio', None)
            trade_dict.setdefault('expected_profit_ratio', None)
        
        return trade_dict
    
    @classmethod
    def convert_to_legacy_format(cls, trade: TradeRecord) -> Dict[str, Any]:
        """将交易记录转换为遗留格式（不包含分批止盈信息）"""
        trade_dict = trade.to_dict()
        
        # 移除分批止盈相关字段
        legacy_dict = {k: v for k, v in trade_dict.items() 
                      if k not in ['use_batch_profit_taking', 'profit_targets', 
                                  'total_expected_profit_ratio', 'total_sell_ratio', 'targets_count']}
        
        return legacy_dict