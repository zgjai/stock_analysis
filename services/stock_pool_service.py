"""
股票池管理服务
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy import and_, or_, desc, asc
from extensions import db
from models.stock_pool import StockPool
from services.base_service import BaseService
from error_handlers import ValidationError, NotFoundError, DatabaseError


class StockPoolService(BaseService):
    """股票池管理服务"""
    
    model = StockPool
    
    @classmethod
    def create_stock_pool_entry(cls, data: Dict[str, Any]) -> StockPool:
        """创建股票池条目"""
        try:
            # 检查是否已存在相同股票的活跃记录
            existing = cls.get_active_by_stock_code(data.get('stock_code'), data.get('pool_type'))
            if existing:
                raise ValidationError(f"股票 {data.get('stock_code')} 已在 {data.get('pool_type')} 池中")
            
            # 直接创建股票池记录，避免BaseService的异常处理
            stock_pool = cls.model(**data)
            return stock_pool.save()
            
        except ValidationError:
            # 重新抛出验证错误
            raise
        except Exception as e:
            if isinstance(e, DatabaseError):
                raise e
            raise DatabaseError(f"创建股票池条目失败: {str(e)}")
    
    @classmethod
    def get_active_by_stock_code(cls, stock_code: str, pool_type: str = None) -> Optional[StockPool]:
        """获取股票的活跃记录"""
        query = cls.model.query.filter_by(stock_code=stock_code, status='active')
        if pool_type:
            query = query.filter_by(pool_type=pool_type)
        return query.first()
    
    @classmethod
    def get_by_pool_type(cls, pool_type: str, status: str = 'active', 
                        page: int = None, per_page: int = None,
                        sort_by: str = 'created_at', sort_order: str = 'desc') -> Dict[str, Any]:
        """根据池类型获取股票列表"""
        try:
            query = cls.model.query.filter_by(pool_type=pool_type, status=status)
            
            # 排序
            if hasattr(cls.model, sort_by):
                order_func = desc if sort_order.lower() == 'desc' else asc
                query = query.order_by(order_func(getattr(cls.model, sort_by)))
            
            # 分页
            if page and per_page:
                pagination = query.paginate(
                    page=page, per_page=per_page, error_out=False
                )
                return {
                    'items': [item.to_dict() for item in pagination.items],
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': page,
                    'per_page': per_page,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            else:
                items = query.all()
                return {
                    'items': [item.to_dict() for item in items],
                    'total': len(items)
                }
        except Exception as e:
            raise DatabaseError(f"获取股票池列表失败: {str(e)}")
    
    @classmethod
    def get_watch_pool(cls, **kwargs) -> Dict[str, Any]:
        """获取待观测池"""
        return cls.get_by_pool_type('watch', **kwargs)
    
    @classmethod
    def get_buy_ready_pool(cls, **kwargs) -> Dict[str, Any]:
        """获取待买入池"""
        return cls.get_by_pool_type('buy_ready', **kwargs)
    
    @classmethod
    def get_stock_history(cls, stock_code: str) -> List[Dict[str, Any]]:
        """获取股票在池中的流转历史"""
        try:
            records = cls.model.query.filter_by(stock_code=stock_code)\
                                   .order_by(desc(cls.model.created_at)).all()
            return [record.to_dict() for record in records]
        except Exception as e:
            raise DatabaseError(f"获取股票历史失败: {str(e)}")
    
    @classmethod
    def move_stock_to_pool(cls, stock_id: int, new_pool_type: str, reason: str = None) -> StockPool:
        """移动股票到另一个池"""
        try:
            stock = cls.get_by_id(stock_id)
            
            if stock.status != 'active':
                raise ValidationError("只能移动活跃状态的股票")
            
            if stock.pool_type == new_pool_type:
                raise ValidationError(f"股票已在 {new_pool_type} 池中")
            
            # 检查目标池中是否已存在该股票
            existing = cls.get_active_by_stock_code(stock.stock_code, new_pool_type)
            if existing:
                raise ValidationError(f"股票 {stock.stock_code} 已在 {new_pool_type} 池中")
            
            # 移动股票
            new_stock = stock.move_to_pool(new_pool_type, reason)
            
            return new_stock
        except Exception as e:
            if isinstance(e, (ValidationError, NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"移动股票失败: {str(e)}")
    
    @classmethod
    def remove_stock_from_pool(cls, stock_id: int, reason: str = None) -> StockPool:
        """从池中移除股票"""
        try:
            stock = cls.get_by_id(stock_id)
            
            if stock.status != 'active':
                raise ValidationError("只能移除活跃状态的股票")
            
            # 移除股票
            stock.remove_from_pool(reason)
            
            return stock
        except Exception as e:
            if isinstance(e, (ValidationError, NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"移除股票失败: {str(e)}")
    
    @classmethod
    def batch_move_stocks(cls, stock_ids: List[int], new_pool_type: str, reason: str = None) -> Dict[str, Any]:
        """批量移动股票"""
        try:
            results = {
                'success': [],
                'failed': []
            }
            
            for stock_id in stock_ids:
                try:
                    new_stock = cls.move_stock_to_pool(stock_id, new_pool_type, reason)
                    results['success'].append({
                        'stock_id': stock_id,
                        'new_record_id': new_stock.id,
                        'stock_code': new_stock.stock_code
                    })
                except Exception as e:
                    results['failed'].append({
                        'stock_id': stock_id,
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            raise DatabaseError(f"批量移动股票失败: {str(e)}")
    
    @classmethod
    def batch_remove_stocks(cls, stock_ids: List[int], reason: str = None) -> Dict[str, Any]:
        """批量移除股票"""
        try:
            results = {
                'success': [],
                'failed': []
            }
            
            for stock_id in stock_ids:
                try:
                    stock = cls.remove_stock_from_pool(stock_id, reason)
                    results['success'].append({
                        'stock_id': stock_id,
                        'stock_code': stock.stock_code
                    })
                except Exception as e:
                    results['failed'].append({
                        'stock_id': stock_id,
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            raise DatabaseError(f"批量移除股票失败: {str(e)}")
    
    @classmethod
    def search_stocks(cls, filters: Dict[str, Any], 
                     page: int = None, per_page: int = None,
                     sort_by: str = 'created_at', sort_order: str = 'desc') -> Dict[str, Any]:
        """搜索股票池"""
        try:
            query = cls.model.query
            
            # 应用筛选条件
            if filters.get('stock_code'):
                query = query.filter(cls.model.stock_code.like(f"%{filters['stock_code']}%"))
            
            if filters.get('stock_name'):
                query = query.filter(cls.model.stock_name.like(f"%{filters['stock_name']}%"))
            
            if filters.get('pool_type'):
                query = query.filter_by(pool_type=filters['pool_type'])
            
            if filters.get('status'):
                query = query.filter_by(status=filters['status'])
            else:
                query = query.filter_by(status='active')  # 默认只显示活跃记录
            
            if filters.get('add_reason'):
                query = query.filter(cls.model.add_reason.like(f"%{filters['add_reason']}%"))
            
            if filters.get('start_date'):
                start_date = datetime.fromisoformat(filters['start_date'])
                query = query.filter(cls.model.created_at >= start_date)
            
            if filters.get('end_date'):
                end_date = datetime.fromisoformat(filters['end_date'])
                query = query.filter(cls.model.created_at <= end_date)
            
            if filters.get('min_target_price'):
                query = query.filter(cls.model.target_price >= float(filters['min_target_price']))
            
            if filters.get('max_target_price'):
                query = query.filter(cls.model.target_price <= float(filters['max_target_price']))
            
            # 排序
            if hasattr(cls.model, sort_by):
                order_func = desc if sort_order.lower() == 'desc' else asc
                query = query.order_by(order_func(getattr(cls.model, sort_by)))
            
            # 分页
            if page and per_page:
                pagination = query.paginate(
                    page=page, per_page=per_page, error_out=False
                )
                return {
                    'items': [item.to_dict() for item in pagination.items],
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': page,
                    'per_page': per_page,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            else:
                items = query.all()
                return {
                    'items': [item.to_dict() for item in items],
                    'total': len(items)
                }
        except Exception as e:
            raise DatabaseError(f"搜索股票池失败: {str(e)}")
    
    @classmethod
    def get_pool_statistics(cls) -> Dict[str, Any]:
        """获取股票池统计信息"""
        try:
            from sqlalchemy import func
            
            # 按池类型和状态统计
            stats = db.session.query(
                cls.model.pool_type,
                cls.model.status,
                func.count(cls.model.id).label('count')
            ).group_by(cls.model.pool_type, cls.model.status).all()
            
            # 整理统计数据
            pool_stats = {
                'watch': {'active': 0, 'moved': 0, 'removed': 0},
                'buy_ready': {'active': 0, 'moved': 0, 'removed': 0}
            }
            
            for stat in stats:
                pool_stats[stat.pool_type][stat.status] = stat.count
            
            # 总计
            total_active = pool_stats['watch']['active'] + pool_stats['buy_ready']['active']
            total_moved = pool_stats['watch']['moved'] + pool_stats['buy_ready']['moved']
            total_removed = pool_stats['watch']['removed'] + pool_stats['buy_ready']['removed']
            
            return {
                'pool_stats': pool_stats,
                'totals': {
                    'active': total_active,
                    'moved': total_moved,
                    'removed': total_removed,
                    'all': total_active + total_moved + total_removed
                }
            }
        except Exception as e:
            raise DatabaseError(f"获取股票池统计失败: {str(e)}")