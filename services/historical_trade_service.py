"""
历史交易识别和数据生成服务
"""
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy import and_, or_, desc, asc, func
from extensions import db
from models.trade_record import TradeRecord
from models.historical_trade import HistoricalTrade
from services.base_service import BaseService
from error_handlers import ValidationError, NotFoundError, DatabaseError


class HistoricalTradeService(BaseService):
    """历史交易识别和数据生成服务"""
    
    model = HistoricalTrade
    
    @classmethod
    def identify_completed_trades(cls) -> List[Dict[str, Any]]:
        """
        识别已完成的交易（已完成清仓的交易）
        
        Returns:
            List[Dict]: 已完成交易的列表，每个字典包含交易的基本信息
        """
        try:
            from flask import current_app
            current_app.logger.info("=== identify_completed_trades 开始 ===")
            
            # 获取所有交易记录，按股票代码和交易日期排序
            all_trades = TradeRecord.query.filter_by(is_corrected=False).order_by(
                TradeRecord.stock_code.asc(),
                TradeRecord.trade_date.asc()
            ).all()
            
            current_app.logger.info(f"获取到 {len(all_trades)} 条交易记录")
            
            # 按股票代码分组
            trades_by_stock = {}
            for trade in all_trades:
                if trade.stock_code not in trades_by_stock:
                    trades_by_stock[trade.stock_code] = []
                trades_by_stock[trade.stock_code].append(trade)
            
            current_app.logger.info(f"按股票分组，共 {len(trades_by_stock)} 只股票")
            
            completed_trades = []
            
            # 对每只股票分析交易记录
            for stock_code, stock_trades in trades_by_stock.items():
                current_app.logger.info(f"分析股票 {stock_code}，共 {len(stock_trades)} 条记录")
                
                # 分析这只股票的完整交易周期
                stock_completed_trades = cls._analyze_stock_trades(stock_code, stock_trades)
                completed_trades.extend(stock_completed_trades)
                
                current_app.logger.info(f"股票 {stock_code} 识别出 {len(stock_completed_trades)} 个完整交易")
            
            current_app.logger.info(f"总共识别出 {len(completed_trades)} 个完整交易")
            current_app.logger.info("=== identify_completed_trades 完成 ===")
            
            return completed_trades
            
        except Exception as e:
            current_app.logger.error(f"识别已完成交易失败: {str(e)}")
            raise DatabaseError(f"识别已完成交易失败: {str(e)}")
    
    @classmethod
    def _analyze_stock_trades(cls, stock_code: str, trades: List[TradeRecord]) -> List[Dict[str, Any]]:
        """
        分析单只股票的交易记录，识别完整的交易周期
        
        Args:
            stock_code: 股票代码
            trades: 该股票的所有交易记录
            
        Returns:
            List[Dict]: 完整交易周期列表
        """
        from flask import current_app
        current_app.logger.info(f"=== _analyze_stock_trades 开始，股票: {stock_code} ===")
        
        completed_trades = []
        current_position = 0  # 当前持仓数量
        buy_records = []  # 当前持有的买入记录
        sell_records = []  # 当前交易周期的卖出记录
        
        for trade in trades:
            current_app.logger.info(f"处理交易记录: {trade.trade_type} {trade.quantity} 股，价格 {trade.price}")
            
            if trade.trade_type == 'buy':
                # 买入操作
                current_position += trade.quantity
                buy_records.append(trade)
                current_app.logger.info(f"买入后持仓: {current_position} 股")
                
            elif trade.trade_type == 'sell':
                # 卖出操作
                if current_position <= 0:
                    current_app.logger.warning(f"警告: 在没有持仓的情况下卖出 {trade.quantity} 股")
                    continue
                
                sell_quantity = min(trade.quantity, current_position)
                current_position -= sell_quantity
                
                # 记录所有卖出交易
                sell_records.append(trade)
                
                current_app.logger.info(f"卖出 {sell_quantity} 股，剩余持仓: {current_position} 股")
                
                # 如果完全清仓，创建一个完整交易记录
                if current_position == 0 and buy_records:
                    current_app.logger.info("检测到完全清仓，创建完整交易记录")
                    current_app.logger.info(f"买入记录数: {len(buy_records)}, 卖出记录数: {len(sell_records)}")
                    
                    completed_trade = cls._create_completed_trade_data(
                        stock_code, buy_records, sell_records
                    )
                    completed_trades.append(completed_trade)
                    
                    # 清空记录
                    buy_records = []
                    sell_records = []
                    current_app.logger.info("完整交易记录已创建，重置买入和卖出记录")
        
        current_app.logger.info(f"股票 {stock_code} 分析完成，识别出 {len(completed_trades)} 个完整交易")
        return completed_trades
    
    @classmethod
    def _create_completed_trade_data(cls, stock_code: str, buy_records: List[TradeRecord], 
                                   sell_records: List[TradeRecord]) -> Dict[str, Any]:
        """
        根据买入和卖出记录创建完整交易数据
        
        Args:
            stock_code: 股票代码
            buy_records: 买入记录列表
            sell_records: 卖出记录列表
            
        Returns:
            Dict: 完整交易数据
        """
        from flask import current_app
        current_app.logger.info(f"=== _create_completed_trade_data 开始 ===")
        current_app.logger.info(f"买入记录数: {len(buy_records)}, 卖出记录数: {len(sell_records)}")
        
        # 获取股票名称（从第一条记录获取）
        stock_name = buy_records[0].stock_name if buy_records else sell_records[0].stock_name
        
        # 计算交易日期范围
        buy_date = min(record.trade_date for record in buy_records)
        sell_date = max(record.trade_date for record in sell_records)
        
        # 计算持仓天数
        holding_days = (sell_date - buy_date).days
        
        # 计算总投入本金和总收益
        total_investment = sum(
            float(record.price) * record.quantity for record in buy_records
        )
        
        total_revenue = sum(
            float(record.price) * record.quantity for record in sell_records
        )
        
        total_return = total_revenue - total_investment
        return_rate = total_return / total_investment if total_investment > 0 else 0
        
        # 记录ID列表
        buy_records_ids = [record.id for record in buy_records]
        sell_records_ids = [record.id for record in sell_records]
        
        current_app.logger.info(f"交易指标计算完成:")
        current_app.logger.info(f"  持仓天数: {holding_days}")
        current_app.logger.info(f"  总投入: {total_investment}")
        current_app.logger.info(f"  总收益: {total_return}")
        current_app.logger.info(f"  收益率: {return_rate:.4f}")
        
        completed_trade_data = {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'buy_date': buy_date,
            'sell_date': sell_date,
            'holding_days': holding_days,
            'total_investment': Decimal(str(total_investment)),
            'total_return': Decimal(str(total_return)),
            'return_rate': Decimal(str(return_rate)),
            'buy_records_ids': json.dumps(buy_records_ids),
            'sell_records_ids': json.dumps(sell_records_ids),
            'is_completed': True,
            'completion_date': sell_date
        }
        
        current_app.logger.info("=== _create_completed_trade_data 完成 ===")
        return completed_trade_data
    
    @classmethod
    def calculate_trade_metrics(cls, buy_records: List[TradeRecord], 
                              sell_records: List[TradeRecord]) -> Dict[str, Any]:
        """
        计算交易指标（持仓天数、投入本金、收益率等）
        
        Args:
            buy_records: 买入记录列表
            sell_records: 卖出记录列表
            
        Returns:
            Dict: 交易指标字典
        """
        try:
            from flask import current_app
            current_app.logger.info("=== calculate_trade_metrics 开始 ===")
            
            if not buy_records or not sell_records:
                raise ValidationError("买入记录和卖出记录都不能为空")
            
            # 基本日期信息
            buy_date = min(record.trade_date for record in buy_records)
            sell_date = max(record.trade_date for record in sell_records)
            holding_days = (sell_date - buy_date).days
            
            # 数量统计
            total_buy_quantity = sum(record.quantity for record in buy_records)
            total_sell_quantity = sum(record.quantity for record in sell_records)
            
            # 财务计算
            total_investment = sum(
                float(record.price) * record.quantity for record in buy_records
            )
            
            total_revenue = sum(
                float(record.price) * record.quantity for record in sell_records
            )
            
            total_return = total_revenue - total_investment
            return_rate = total_return / total_investment if total_investment > 0 else 0
            
            # 平均价格
            avg_buy_price = total_investment / total_buy_quantity if total_buy_quantity > 0 else 0
            avg_sell_price = total_revenue / total_sell_quantity if total_sell_quantity > 0 else 0
            
            # 日均收益率
            daily_return_rate = return_rate / holding_days if holding_days > 0 else 0
            
            # 年化收益率（假设一年250个交易日）
            annualized_return_rate = daily_return_rate * 250 if holding_days > 0 else 0
            
            metrics = {
                'buy_date': buy_date,
                'sell_date': sell_date,
                'holding_days': holding_days,
                'total_buy_quantity': total_buy_quantity,
                'total_sell_quantity': total_sell_quantity,
                'total_investment': total_investment,
                'total_revenue': total_revenue,
                'total_return': total_return,
                'return_rate': return_rate,
                'avg_buy_price': avg_buy_price,
                'avg_sell_price': avg_sell_price,
                'daily_return_rate': daily_return_rate,
                'annualized_return_rate': annualized_return_rate,
                'is_profitable': total_return > 0,
                'profit_per_day': total_return / holding_days if holding_days > 0 else 0
            }
            
            current_app.logger.info(f"交易指标计算完成: {metrics}")
            current_app.logger.info("=== calculate_trade_metrics 完成 ===")
            
            return metrics
            
        except Exception as e:
            current_app.logger.error(f"计算交易指标失败: {str(e)}")
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"计算交易指标失败: {str(e)}")
    
    @classmethod
    def generate_historical_records(cls, force_regenerate: bool = False) -> Dict[str, Any]:
        """
        生成历史交易记录
        
        Args:
            force_regenerate: 是否强制重新生成（删除现有记录）
            
        Returns:
            Dict: 生成结果统计
        """
        try:
            from flask import current_app
            current_app.logger.info("=== generate_historical_records 开始 ===")
            current_app.logger.info(f"强制重新生成: {force_regenerate}")
            
            # 如果强制重新生成，删除现有记录
            if force_regenerate:
                current_app.logger.info("删除现有历史交易记录")
                deleted_count = HistoricalTrade.query.delete()
                db.session.commit()
                current_app.logger.info(f"删除了 {deleted_count} 条现有记录")
            
            # 识别已完成的交易
            completed_trades = cls.identify_completed_trades()
            current_app.logger.info(f"识别出 {len(completed_trades)} 个完整交易")
            
            # 统计信息
            created_count = 0
            skipped_count = 0
            error_count = 0
            errors = []
            
            # 创建历史交易记录
            for trade_data in completed_trades:
                try:
                    # 检查是否已存在相同的历史交易记录
                    existing_record = cls._find_existing_record(trade_data)
                    
                    if existing_record and not force_regenerate:
                        current_app.logger.info(f"跳过已存在的记录: {trade_data['stock_code']} {trade_data['buy_date']}")
                        skipped_count += 1
                        continue
                    
                    # 创建新的历史交易记录
                    historical_trade = cls.create(trade_data)
                    created_count += 1
                    
                    current_app.logger.info(f"创建历史交易记录: ID={historical_trade.id}, {trade_data['stock_code']}")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"创建记录失败 {trade_data['stock_code']}: {str(e)}"
                    errors.append(error_msg)
                    current_app.logger.error(error_msg)
            
            # 提交事务
            db.session.commit()
            
            result = {
                'total_identified': len(completed_trades),
                'created_count': created_count,
                'skipped_count': skipped_count,
                'error_count': error_count,
                'errors': errors,
                'success': error_count == 0
            }
            
            current_app.logger.info(f"历史交易记录生成完成: {result}")
            current_app.logger.info("=== generate_historical_records 完成 ===")
            
            return result
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"生成历史交易记录失败: {str(e)}")
            raise DatabaseError(f"生成历史交易记录失败: {str(e)}")
    
    @classmethod
    def sync_historical_records(cls) -> Dict[str, Any]:
        """
        同步历史交易记录（增量更新）
        
        Returns:
            Dict: 同步结果统计
        """
        try:
            from flask import current_app
            current_app.logger.info("=== sync_historical_records 开始 ===")
            
            # 获取最后一次同步的时间（从最新的历史交易记录获取）
            last_sync_record = HistoricalTrade.query.order_by(
                HistoricalTrade.created_at.desc()
            ).first()
            
            last_sync_time = last_sync_record.created_at if last_sync_record else datetime.min
            current_app.logger.info(f"上次同步时间: {last_sync_time}")
            
            # 识别新的完整交易
            all_completed_trades = cls.identify_completed_trades()
            
            # 过滤出需要同步的交易（新的或更新的）
            new_trades = []
            updated_trades = []
            
            for trade_data in all_completed_trades:
                existing_record = cls._find_existing_record(trade_data)
                
                if not existing_record:
                    # 新交易
                    new_trades.append(trade_data)
                else:
                    # 检查是否需要更新
                    if cls._needs_update(existing_record, trade_data):
                        updated_trades.append((existing_record, trade_data))
            
            current_app.logger.info(f"发现 {len(new_trades)} 个新交易，{len(updated_trades)} 个需要更新的交易")
            
            # 统计信息
            created_count = 0
            updated_count = 0
            error_count = 0
            errors = []
            
            # 创建新记录
            for trade_data in new_trades:
                try:
                    historical_trade = cls.create(trade_data)
                    created_count += 1
                    current_app.logger.info(f"创建新历史交易记录: ID={historical_trade.id}")
                except Exception as e:
                    error_count += 1
                    error_msg = f"创建新记录失败: {str(e)}"
                    errors.append(error_msg)
                    current_app.logger.error(error_msg)
            
            # 更新现有记录
            for existing_record, new_data in updated_trades:
                try:
                    # 更新记录
                    for key, value in new_data.items():
                        if key not in ['id', 'created_at']:  # 跳过不应更新的字段
                            setattr(existing_record, key, value)
                    
                    existing_record.save()
                    updated_count += 1
                    current_app.logger.info(f"更新历史交易记录: ID={existing_record.id}")
                except Exception as e:
                    error_count += 1
                    error_msg = f"更新记录失败: {str(e)}"
                    errors.append(error_msg)
                    current_app.logger.error(error_msg)
            
            # 提交事务
            db.session.commit()
            
            result = {
                'last_sync_time': last_sync_time.isoformat() if last_sync_time != datetime.min else None,
                'total_checked': len(all_completed_trades),
                'created_count': created_count,
                'updated_count': updated_count,
                'error_count': error_count,
                'errors': errors,
                'success': error_count == 0
            }
            
            current_app.logger.info(f"历史交易记录同步完成: {result}")
            current_app.logger.info("=== sync_historical_records 完成 ===")
            
            return result
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"同步历史交易记录失败: {str(e)}")
            raise DatabaseError(f"同步历史交易记录失败: {str(e)}")
    
    @classmethod
    def get_historical_trades(cls, filters: Dict[str, Any] = None, 
                            page: int = None, per_page: int = None,
                            sort_by: str = 'completion_date', sort_order: str = 'desc') -> Dict[str, Any]:
        """
        获取历史交易记录列表，支持筛选、分页和排序
        
        Args:
            filters: 筛选条件
            page: 页码
            per_page: 每页数量
            sort_by: 排序字段
            sort_order: 排序方向
            
        Returns:
            Dict: 历史交易记录列表和分页信息
        """
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
            raise DatabaseError(f"获取历史交易记录列表失败: {str(e)}")
    
    @classmethod
    def get_trade_statistics(cls) -> Dict[str, Any]:
        """
        获取历史交易统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            from flask import current_app
            current_app.logger.info("=== get_trade_statistics 开始 ===")
            
            # 基本统计
            total_trades = cls.model.query.count()
            profitable_trades = cls.model.query.filter(cls.model.total_return > 0).count()
            loss_trades = cls.model.query.filter(cls.model.total_return < 0).count()
            
            # 收益统计
            total_investment = db.session.query(func.sum(cls.model.total_investment)).scalar() or 0
            total_return = db.session.query(func.sum(cls.model.total_return)).scalar() or 0
            
            # 收益率统计
            avg_return_rate = db.session.query(func.avg(cls.model.return_rate)).scalar() or 0
            max_return_rate = db.session.query(func.max(cls.model.return_rate)).scalar() or 0
            min_return_rate = db.session.query(func.min(cls.model.return_rate)).scalar() or 0
            
            # 持仓天数统计
            avg_holding_days = db.session.query(func.avg(cls.model.holding_days)).scalar() or 0
            max_holding_days = db.session.query(func.max(cls.model.holding_days)).scalar() or 0
            min_holding_days = db.session.query(func.min(cls.model.holding_days)).scalar() or 0
            
            # 胜率
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            
            # 总收益率
            overall_return_rate = (float(total_return) / float(total_investment) * 100) if total_investment > 0 else 0
            
            statistics = {
                'total_trades': total_trades,
                'profitable_trades': profitable_trades,
                'loss_trades': loss_trades,
                'win_rate': round(win_rate, 1),
                'total_investment': float(total_investment),
                'total_return': float(total_return),
                'overall_return_rate': round(overall_return_rate, 2),
                'avg_return_rate': round(float(avg_return_rate) * 100, 2),
                'max_return_rate': round(float(max_return_rate) * 100, 2),
                'min_return_rate': round(float(min_return_rate) * 100, 2),
                'avg_holding_days': round(float(avg_holding_days), 1),
                'max_holding_days': int(max_holding_days) if max_holding_days else 0,
                'min_holding_days': int(min_holding_days) if min_holding_days else 0
            }
            
            current_app.logger.info(f"统计信息: {statistics}")
            current_app.logger.info("=== get_trade_statistics 完成 ===")
            
            return statistics
            
        except Exception as e:
            current_app.logger.error(f"获取交易统计失败: {str(e)}")
            raise DatabaseError(f"获取交易统计失败: {str(e)}")
    
    @classmethod
    def _find_existing_record(cls, trade_data: Dict[str, Any]) -> Optional[HistoricalTrade]:
        """
        查找是否存在相同的历史交易记录
        
        Args:
            trade_data: 交易数据
            
        Returns:
            HistoricalTrade: 存在的记录，如果不存在则返回None
        """
        return cls.model.query.filter(
            and_(
                cls.model.stock_code == trade_data['stock_code'],
                cls.model.buy_date == trade_data['buy_date'],
                cls.model.sell_date == trade_data['sell_date']
            )
        ).first()
    
    @classmethod
    def _needs_update(cls, existing_record: HistoricalTrade, new_data: Dict[str, Any]) -> bool:
        """
        检查现有记录是否需要更新
        
        Args:
            existing_record: 现有记录
            new_data: 新数据
            
        Returns:
            bool: 是否需要更新
        """
        # 比较关键字段
        key_fields = ['total_investment', 'total_return', 'return_rate', 'holding_days']
        
        for field in key_fields:
            existing_value = getattr(existing_record, field)
            new_value = new_data.get(field)
            
            if existing_value != new_value:
                return True
        
        return False
    
    @classmethod
    def _apply_filters(cls, query, filters: Dict[str, Any]):
        """应用筛选条件"""
        if 'stock_code' in filters and filters['stock_code']:
            query = query.filter(cls.model.stock_code == filters['stock_code'])
        
        if 'stock_name' in filters and filters['stock_name']:
            query = query.filter(cls.model.stock_name.like(f"%{filters['stock_name']}%"))
        
        if 'start_date' in filters and filters['start_date']:
            start_date = cls._parse_date(filters['start_date'])
            query = query.filter(cls.model.completion_date >= start_date)
        
        if 'end_date' in filters and filters['end_date']:
            end_date = cls._parse_date(filters['end_date'])
            # 结束日期包含当天，所以加1天
            end_date = end_date + timedelta(days=1)
            query = query.filter(cls.model.completion_date < end_date)
        
        if 'min_return_rate' in filters and filters['min_return_rate'] is not None:
            query = query.filter(cls.model.return_rate >= float(filters['min_return_rate']))
        
        if 'max_return_rate' in filters and filters['max_return_rate'] is not None:
            query = query.filter(cls.model.return_rate <= float(filters['max_return_rate']))
        
        if 'min_holding_days' in filters and filters['min_holding_days'] is not None:
            query = query.filter(cls.model.holding_days >= int(filters['min_holding_days']))
        
        if 'max_holding_days' in filters and filters['max_holding_days'] is not None:
            query = query.filter(cls.model.holding_days <= int(filters['max_holding_days']))
        
        if 'is_profitable' in filters and filters['is_profitable'] is not None:
            if filters['is_profitable']:
                query = query.filter(cls.model.total_return > 0)
            else:
                query = query.filter(cls.model.total_return <= 0)
        
        return query
    
    @classmethod
    def _apply_sorting(cls, query, sort_by: str, sort_order: str):
        """应用排序"""
        if not hasattr(cls.model, sort_by):
            sort_by = 'completion_date'  # 默认按完成日期排序
        
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
            elif isinstance(date_str, datetime):
                return date_str
            else:
                raise ValueError(f"无效的日期类型: {type(date_str)}")
        except Exception as e:
            raise ValidationError(f"日期格式错误: {str(e)}")