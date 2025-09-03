"""
数据同步服务 - 负责历史交易数据的同步和初始化
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import and_, or_, func, text
from extensions import db
from models.trade_record import TradeRecord
from models.historical_trade import HistoricalTrade
from services.historical_trade_service import HistoricalTradeService
from error_handlers import ValidationError, DatabaseError


class DataSyncService:
    """数据同步服务类"""
    
    @classmethod
    def initialize_historical_data(cls, force_regenerate: bool = False) -> Dict[str, Any]:
        """
        初始化历史交易数据
        
        Args:
            force_regenerate: 是否强制重新生成所有数据
            
        Returns:
            Dict: 初始化结果
        """
        try:
            from flask import current_app
            current_app.logger.info("=== initialize_historical_data 开始 ===")
            current_app.logger.info(f"强制重新生成: {force_regenerate}")
            
            # 数据完整性检查
            integrity_check = cls.check_data_integrity()
            current_app.logger.info(f"数据完整性检查结果: {integrity_check}")
            
            # 如果强制重新生成或数据不完整，执行完整初始化
            if force_regenerate or not integrity_check['is_valid']:
                current_app.logger.info("执行完整数据初始化")
                result = HistoricalTradeService.generate_historical_records(force_regenerate=True)
            else:
                current_app.logger.info("执行增量同步")
                result = cls.incremental_sync()
            
            # 更新同步状态
            cls._update_sync_status('initialize', result['success'])
            
            # 添加完整性检查结果
            result['integrity_check'] = integrity_check
            result['sync_type'] = 'full_initialize' if force_regenerate else 'incremental'
            
            current_app.logger.info(f"数据初始化完成: {result}")
            current_app.logger.info("=== initialize_historical_data 完成 ===")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"初始化历史数据失败: {str(e)}")
            cls._update_sync_status('initialize', False, str(e))
            raise DatabaseError(f"初始化历史数据失败: {str(e)}")
    
    @classmethod
    def incremental_sync(cls) -> Dict[str, Any]:
        """
        增量同步 - 只同步新的或更新的交易记录
        
        Returns:
            Dict: 同步结果
        """
        try:
            from flask import current_app
            current_app.logger.info("=== incremental_sync 开始 ===")
            
            # 获取上次同步时间
            last_sync_time = cls._get_last_sync_time()
            current_app.logger.info(f"上次同步时间: {last_sync_time}")
            
            # 获取需要同步的交易记录
            new_or_updated_trades = cls._get_trades_to_sync(last_sync_time)
            current_app.logger.info(f"发现 {len(new_or_updated_trades)} 条需要同步的交易记录")
            
            if not new_or_updated_trades:
                current_app.logger.info("没有需要同步的数据")
                return {
                    'sync_type': 'incremental',
                    'last_sync_time': last_sync_time.isoformat() if last_sync_time else None,
                    'checked_records': 0,
                    'created_count': 0,
                    'updated_count': 0,
                    'error_count': 0,
                    'errors': [],
                    'success': True,
                    'message': '没有需要同步的数据'
                }
            
            # 执行增量同步
            result = HistoricalTradeService.sync_historical_records()
            
            # 更新同步状态
            cls._update_sync_status('incremental_sync', result['success'])
            
            result['sync_type'] = 'incremental'
            result['checked_records'] = len(new_or_updated_trades)
            
            current_app.logger.info(f"增量同步完成: {result}")
            current_app.logger.info("=== incremental_sync 完成 ===")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"增量同步失败: {str(e)}")
            cls._update_sync_status('incremental_sync', False, str(e))
            raise DatabaseError(f"增量同步失败: {str(e)}")
    
    @classmethod
    def check_data_integrity(cls) -> Dict[str, Any]:
        """
        检查数据完整性
        
        Returns:
            Dict: 完整性检查结果
        """
        try:
            from flask import current_app
            current_app.logger.info("=== check_data_integrity 开始 ===")
            
            issues = []
            warnings = []
            
            # 1. 检查基础数据统计
            total_trade_records = TradeRecord.query.filter_by(is_corrected=False).count()
            total_historical_trades = HistoricalTrade.query.count()
            
            current_app.logger.info(f"交易记录总数: {total_trade_records}")
            current_app.logger.info(f"历史交易记录总数: {total_historical_trades}")
            
            # 2. 检查是否有孤立的交易记录（买入但没有对应卖出）
            orphaned_buys = cls._check_orphaned_buy_records()
            if orphaned_buys:
                warnings.append(f"发现 {len(orphaned_buys)} 条孤立的买入记录（没有对应的卖出记录）")
            
            # 3. 检查历史交易记录的数据一致性
            inconsistent_records = cls._check_historical_trade_consistency()
            if inconsistent_records:
                issues.extend(inconsistent_records)
            
            # 4. 检查重复的历史交易记录
            duplicate_records = cls._check_duplicate_historical_trades()
            if duplicate_records:
                issues.append(f"发现 {len(duplicate_records)} 条重复的历史交易记录")
            
            # 5. 检查数据类型和约束
            constraint_violations = cls._check_data_constraints()
            if constraint_violations:
                issues.extend(constraint_violations)
            
            # 6. 检查关联记录的有效性
            invalid_references = cls._check_record_references()
            if invalid_references:
                issues.extend(invalid_references)
            
            # 7. 统计分析
            statistics = cls._calculate_integrity_statistics()
            
            # 判断整体完整性
            is_valid = len(issues) == 0
            severity = 'error' if issues else ('warning' if warnings else 'ok')
            
            result = {
                'is_valid': is_valid,
                'severity': severity,
                'total_trade_records': total_trade_records,
                'total_historical_trades': total_historical_trades,
                'issues': issues,
                'warnings': warnings,
                'statistics': statistics,
                'check_time': datetime.now().isoformat(),
                'orphaned_buys_count': len(orphaned_buys),
                'duplicate_records_count': len(duplicate_records) if duplicate_records else 0
            }
            
            current_app.logger.info(f"数据完整性检查完成: {result}")
            current_app.logger.info("=== check_data_integrity 完成 ===")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"数据完整性检查失败: {str(e)}")
            raise DatabaseError(f"数据完整性检查失败: {str(e)}")
    
    @classmethod
    def repair_data_integrity(cls, repair_options: Dict[str, bool] = None) -> Dict[str, Any]:
        """
        修复数据完整性问题
        
        Args:
            repair_options: 修复选项
                - remove_duplicates: 删除重复记录
                - fix_inconsistencies: 修复数据不一致
                - update_references: 更新无效引用
                
        Returns:
            Dict: 修复结果
        """
        try:
            from flask import current_app
            current_app.logger.info("=== repair_data_integrity 开始 ===")
            current_app.logger.info(f"修复选项: {repair_options}")
            
            if not repair_options:
                repair_options = {
                    'remove_duplicates': True,
                    'fix_inconsistencies': True,
                    'update_references': True
                }
            
            repair_results = []
            
            # 1. 删除重复记录
            if repair_options.get('remove_duplicates', False):
                duplicate_result = cls._remove_duplicate_records()
                repair_results.append(duplicate_result)
            
            # 2. 修复数据不一致
            if repair_options.get('fix_inconsistencies', False):
                consistency_result = cls._fix_data_inconsistencies()
                repair_results.append(consistency_result)
            
            # 3. 更新无效引用
            if repair_options.get('update_references', False):
                reference_result = cls._fix_invalid_references()
                repair_results.append(reference_result)
            
            # 提交所有修复
            db.session.commit()
            
            # 重新检查完整性
            post_repair_check = cls.check_data_integrity()
            
            result = {
                'repair_actions': repair_results,
                'post_repair_check': post_repair_check,
                'success': post_repair_check['is_valid'],
                'repair_time': datetime.now().isoformat()
            }
            
            current_app.logger.info(f"数据完整性修复完成: {result}")
            current_app.logger.info("=== repair_data_integrity 完成 ===")
            
            return result
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"数据完整性修复失败: {str(e)}")
            raise DatabaseError(f"数据完整性修复失败: {str(e)}")
    
    @classmethod
    def get_sync_status(cls) -> Dict[str, Any]:
        """
        获取同步状态信息
        
        Returns:
            Dict: 同步状态
        """
        try:
            # 获取最后同步时间
            last_sync_time = cls._get_last_sync_time()
            
            # 获取同步统计
            sync_stats = cls._get_sync_statistics()
            
            # 检查是否需要同步
            needs_sync = cls._check_if_sync_needed()
            
            return {
                'last_sync_time': last_sync_time.isoformat() if last_sync_time else None,
                'needs_sync': needs_sync,
                'sync_statistics': sync_stats,
                'status_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise DatabaseError(f"获取同步状态失败: {str(e)}")
    
    # 私有方法
    
    @classmethod
    def _get_last_sync_time(cls) -> Optional[datetime]:
        """获取最后同步时间"""
        # 从最新的历史交易记录获取创建时间作为最后同步时间
        last_record = HistoricalTrade.query.order_by(
            HistoricalTrade.created_at.desc()
        ).first()
        
        return last_record.created_at if last_record else None
    
    @classmethod
    def _get_trades_to_sync(cls, last_sync_time: Optional[datetime]) -> List[TradeRecord]:
        """获取需要同步的交易记录"""
        query = TradeRecord.query.filter_by(is_corrected=False)
        
        if last_sync_time:
            # 获取在最后同步时间之后更新的记录
            query = query.filter(
                or_(
                    TradeRecord.created_at > last_sync_time,
                    TradeRecord.updated_at > last_sync_time
                )
            )
        
        return query.order_by(TradeRecord.trade_date.asc()).all()
    
    @classmethod
    def _check_orphaned_buy_records(cls) -> List[Dict[str, Any]]:
        """检查孤立的买入记录"""
        # 获取所有买入记录
        buy_records = TradeRecord.query.filter(
            and_(
                TradeRecord.trade_type == 'buy',
                TradeRecord.is_corrected == False
            )
        ).all()
        
        orphaned_buys = []
        
        # 按股票代码分组检查
        stock_codes = set(record.stock_code for record in buy_records)
        
        for stock_code in stock_codes:
            stock_buys = [r for r in buy_records if r.stock_code == stock_code]
            stock_sells = TradeRecord.query.filter(
                and_(
                    TradeRecord.stock_code == stock_code,
                    TradeRecord.trade_type == 'sell',
                    TradeRecord.is_corrected == False
                )
            ).all()
            
            # 计算买入和卖出的数量
            total_buy_quantity = sum(r.quantity for r in stock_buys)
            total_sell_quantity = sum(r.quantity for r in stock_sells)
            
            # 如果买入数量大于卖出数量，说明有未完成的持仓
            if total_buy_quantity > total_sell_quantity:
                orphaned_buys.append({
                    'stock_code': stock_code,
                    'total_buy_quantity': total_buy_quantity,
                    'total_sell_quantity': total_sell_quantity,
                    'remaining_quantity': total_buy_quantity - total_sell_quantity,
                    'buy_records_count': len(stock_buys)
                })
        
        return orphaned_buys
    
    @classmethod
    def _check_historical_trade_consistency(cls) -> List[str]:
        """检查历史交易记录的数据一致性"""
        issues = []
        
        # 获取所有历史交易记录
        historical_trades = HistoricalTrade.query.all()
        
        for trade in historical_trades:
            try:
                # 检查买入记录ID列表
                buy_records_ids = trade.buy_records_list
                sell_records_ids = trade.sell_records_list
                
                if not buy_records_ids or not sell_records_ids:
                    issues.append(f"历史交易记录 {trade.id} 缺少买入或卖出记录ID")
                    continue
                
                # 验证记录是否存在
                buy_records = TradeRecord.query.filter(
                    TradeRecord.id.in_(buy_records_ids)
                ).all()
                
                sell_records = TradeRecord.query.filter(
                    TradeRecord.id.in_(sell_records_ids)
                ).all()
                
                if len(buy_records) != len(buy_records_ids):
                    issues.append(f"历史交易记录 {trade.id} 的买入记录ID列表包含无效ID")
                
                if len(sell_records) != len(sell_records_ids):
                    issues.append(f"历史交易记录 {trade.id} 的卖出记录ID列表包含无效ID")
                
                # 验证计算结果
                if buy_records and sell_records:
                    calculated_metrics = HistoricalTradeService.calculate_trade_metrics(
                        buy_records, sell_records
                    )
                    
                    # 检查投入本金
                    if abs(float(trade.total_investment) - calculated_metrics['total_investment']) > 0.01:
                        issues.append(f"历史交易记录 {trade.id} 的总投入本金计算不正确")
                    
                    # 检查收益
                    if abs(float(trade.total_return) - calculated_metrics['total_return']) > 0.01:
                        issues.append(f"历史交易记录 {trade.id} 的总收益计算不正确")
                
            except Exception as e:
                issues.append(f"检查历史交易记录 {trade.id} 时发生错误: {str(e)}")
        
        return issues
    
    @classmethod
    def _check_duplicate_historical_trades(cls) -> List[Dict[str, Any]]:
        """检查重复的历史交易记录"""
        # 使用SQL查询查找重复记录
        duplicate_query = db.session.query(
            HistoricalTrade.stock_code,
            HistoricalTrade.buy_date,
            HistoricalTrade.sell_date,
            func.count(HistoricalTrade.id).label('count')
        ).group_by(
            HistoricalTrade.stock_code,
            HistoricalTrade.buy_date,
            HistoricalTrade.sell_date
        ).having(func.count(HistoricalTrade.id) > 1)
        
        duplicates = []
        for row in duplicate_query.all():
            # 获取重复记录的详细信息
            duplicate_records = HistoricalTrade.query.filter(
                and_(
                    HistoricalTrade.stock_code == row.stock_code,
                    HistoricalTrade.buy_date == row.buy_date,
                    HistoricalTrade.sell_date == row.sell_date
                )
            ).all()
            
            duplicates.append({
                'stock_code': row.stock_code,
                'buy_date': row.buy_date.isoformat(),
                'sell_date': row.sell_date.isoformat(),
                'count': row.count,
                'record_ids': [r.id for r in duplicate_records]
            })
        
        return duplicates
    
    @classmethod
    def _check_data_constraints(cls) -> List[str]:
        """检查数据约束违反"""
        issues = []
        
        # 检查历史交易记录的约束
        invalid_investments = HistoricalTrade.query.filter(
            HistoricalTrade.total_investment <= 0
        ).count()
        
        if invalid_investments > 0:
            issues.append(f"发现 {invalid_investments} 条总投入本金小于等于0的记录")
        
        invalid_holding_days = HistoricalTrade.query.filter(
            HistoricalTrade.holding_days < 0
        ).count()
        
        if invalid_holding_days > 0:
            issues.append(f"发现 {invalid_holding_days} 条持仓天数为负数的记录")
        
        invalid_date_order = HistoricalTrade.query.filter(
            HistoricalTrade.sell_date < HistoricalTrade.buy_date
        ).count()
        
        if invalid_date_order > 0:
            issues.append(f"发现 {invalid_date_order} 条卖出日期早于买入日期的记录")
        
        return issues
    
    @classmethod
    def _check_record_references(cls) -> List[str]:
        """检查记录引用的有效性"""
        issues = []
        
        # 检查历史交易记录中引用的交易记录ID是否有效
        historical_trades = HistoricalTrade.query.all()
        
        for trade in historical_trades:
            try:
                buy_ids = trade.buy_records_list
                sell_ids = trade.sell_records_list
                
                # 检查买入记录引用
                if buy_ids:
                    existing_buy_count = TradeRecord.query.filter(
                        TradeRecord.id.in_(buy_ids)
                    ).count()
                    
                    if existing_buy_count != len(buy_ids):
                        issues.append(f"历史交易记录 {trade.id} 引用了不存在的买入记录ID")
                
                # 检查卖出记录引用
                if sell_ids:
                    existing_sell_count = TradeRecord.query.filter(
                        TradeRecord.id.in_(sell_ids)
                    ).count()
                    
                    if existing_sell_count != len(sell_ids):
                        issues.append(f"历史交易记录 {trade.id} 引用了不存在的卖出记录ID")
                        
            except Exception as e:
                issues.append(f"检查历史交易记录 {trade.id} 的引用时发生错误: {str(e)}")
        
        return issues
    
    @classmethod
    def _calculate_integrity_statistics(cls) -> Dict[str, Any]:
        """计算完整性统计信息"""
        # 基础统计
        total_trades = HistoricalTrade.query.count()
        profitable_trades = HistoricalTrade.query.filter(
            HistoricalTrade.total_return > 0
        ).count()
        
        # 数据覆盖率统计
        total_trade_records = TradeRecord.query.filter_by(is_corrected=False).count()
        
        # 最新记录时间
        latest_trade_record = TradeRecord.query.filter_by(is_corrected=False).order_by(
            TradeRecord.trade_date.desc()
        ).first()
        
        latest_historical_trade = HistoricalTrade.query.order_by(
            HistoricalTrade.completion_date.desc()
        ).first()
        
        return {
            'total_historical_trades': total_trades,
            'profitable_trades': profitable_trades,
            'loss_trades': total_trades - profitable_trades,
            'win_rate': (profitable_trades / total_trades * 100) if total_trades > 0 else 0,
            'total_trade_records': total_trade_records,
            'latest_trade_record_date': latest_trade_record.trade_date.isoformat() if latest_trade_record else None,
            'latest_historical_trade_date': latest_historical_trade.completion_date.isoformat() if latest_historical_trade else None,
            'data_coverage_ratio': (total_trades / (total_trade_records / 2)) if total_trade_records > 0 else 0  # 假设平均每个完整交易包含2条记录
        }
    
    @classmethod
    def _remove_duplicate_records(cls) -> Dict[str, Any]:
        """删除重复记录"""
        duplicates = cls._check_duplicate_historical_trades()
        removed_count = 0
        
        for duplicate_group in duplicates:
            record_ids = duplicate_group['record_ids']
            # 保留最新的记录，删除其他的
            records_to_delete = record_ids[1:]  # 保留第一个，删除其余的
            
            for record_id in records_to_delete:
                record = HistoricalTrade.query.get(record_id)
                if record:
                    db.session.delete(record)
                    removed_count += 1
        
        return {
            'action': 'remove_duplicates',
            'removed_count': removed_count,
            'duplicate_groups': len(duplicates)
        }
    
    @classmethod
    def _fix_data_inconsistencies(cls) -> Dict[str, Any]:
        """修复数据不一致"""
        fixed_count = 0
        
        # 重新计算所有历史交易记录的指标
        historical_trades = HistoricalTrade.query.all()
        
        for trade in historical_trades:
            try:
                buy_records_ids = trade.buy_records_list
                sell_records_ids = trade.sell_records_list
                
                if buy_records_ids and sell_records_ids:
                    buy_records = TradeRecord.query.filter(
                        TradeRecord.id.in_(buy_records_ids)
                    ).all()
                    
                    sell_records = TradeRecord.query.filter(
                        TradeRecord.id.in_(sell_records_ids)
                    ).all()
                    
                    if buy_records and sell_records:
                        # 重新计算指标
                        metrics = HistoricalTradeService.calculate_trade_metrics(
                            buy_records, sell_records
                        )
                        
                        # 更新记录
                        trade.total_investment = metrics['total_investment']
                        trade.total_return = metrics['total_return']
                        trade.return_rate = metrics['return_rate']
                        trade.holding_days = metrics['holding_days']
                        
                        fixed_count += 1
                        
            except Exception as e:
                from flask import current_app
                current_app.logger.error(f"修复历史交易记录 {trade.id} 时发生错误: {str(e)}")
        
        return {
            'action': 'fix_inconsistencies',
            'fixed_count': fixed_count
        }
    
    @classmethod
    def _fix_invalid_references(cls) -> Dict[str, Any]:
        """修复无效引用"""
        fixed_count = 0
        
        # 删除引用了不存在记录的历史交易记录
        historical_trades = HistoricalTrade.query.all()
        
        for trade in historical_trades:
            try:
                buy_ids = trade.buy_records_list
                sell_ids = trade.sell_records_list
                
                # 检查引用的有效性
                valid_buy_ids = []
                valid_sell_ids = []
                
                if buy_ids:
                    existing_buys = TradeRecord.query.filter(
                        TradeRecord.id.in_(buy_ids)
                    ).all()
                    valid_buy_ids = [r.id for r in existing_buys]
                
                if sell_ids:
                    existing_sells = TradeRecord.query.filter(
                        TradeRecord.id.in_(sell_ids)
                    ).all()
                    valid_sell_ids = [r.id for r in existing_sells]
                
                # 如果引用无效，删除该历史交易记录
                if (buy_ids and len(valid_buy_ids) != len(buy_ids)) or \
                   (sell_ids and len(valid_sell_ids) != len(sell_ids)):
                    db.session.delete(trade)
                    fixed_count += 1
                    
            except Exception as e:
                from flask import current_app
                current_app.logger.error(f"修复历史交易记录 {trade.id} 的引用时发生错误: {str(e)}")
        
        return {
            'action': 'fix_invalid_references',
            'removed_count': fixed_count
        }
    
    @classmethod
    def _update_sync_status(cls, operation: str, success: bool, error_message: str = None):
        """更新同步状态（这里可以扩展为存储到数据库或缓存）"""
        from flask import current_app
        status = {
            'operation': operation,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'error_message': error_message
        }
        current_app.logger.info(f"同步状态更新: {status}")
    
    @classmethod
    def _get_sync_statistics(cls) -> Dict[str, Any]:
        """获取同步统计信息"""
        # 这里可以从数据库或缓存中获取同步统计
        return {
            'total_syncs': 0,  # 可以从日志或状态表中获取
            'successful_syncs': 0,
            'failed_syncs': 0,
            'last_error': None
        }
    
    @classmethod
    def _check_if_sync_needed(cls) -> bool:
        """检查是否需要同步"""
        last_sync_time = cls._get_last_sync_time()
        
        if not last_sync_time:
            return True  # 从未同步过
        
        # 检查是否有新的交易记录
        new_records_count = TradeRecord.query.filter(
            and_(
                TradeRecord.is_corrected == False,
                or_(
                    TradeRecord.created_at > last_sync_time,
                    TradeRecord.updated_at > last_sync_time
                )
            )
        ).count()
        
        return new_records_count > 0