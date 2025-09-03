"""
缓存服务
用于缓存复杂计算结果，提高系统性能
"""
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
from functools import wraps
from extensions import db
from models.base import BaseModel


class CacheEntry(BaseModel):
    """缓存条目模型"""
    
    __tablename__ = 'cache_entries'
    
    cache_key = db.Column(db.String(255), nullable=False, unique=True, index=True)
    cache_value = db.Column(db.Text, nullable=False)  # JSON格式存储
    cache_type = db.Column(db.String(50), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    created_by = db.Column(db.String(50), default='system')
    
    # 索引
    __table_args__ = (
        db.Index('idx_cache_type_expires', 'cache_type', 'expires_at'),
    )
    
    @classmethod
    def get_valid_cache(cls, cache_key: str) -> Optional['CacheEntry']:
        """获取有效的缓存条目"""
        return cls.query.filter(
            cls.cache_key == cache_key,
            cls.expires_at > datetime.now()
        ).first()
    
    @classmethod
    def set_cache(cls, cache_key: str, value: Any, cache_type: str, 
                  expires_in_minutes: int = 30) -> 'CacheEntry':
        """设置缓存"""
        expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        
        # 删除旧的缓存条目
        cls.query.filter_by(cache_key=cache_key).delete()
        
        # 创建新的缓存条目
        cache_entry = cls(
            cache_key=cache_key,
            cache_value=json.dumps(value, default=str),
            cache_type=cache_type,
            expires_at=expires_at
        )
        
        db.session.add(cache_entry)
        db.session.commit()
        
        return cache_entry
    
    @classmethod
    def clear_cache_by_type(cls, cache_type: str):
        """清除指定类型的所有缓存"""
        cls.query.filter_by(cache_type=cache_type).delete()
        db.session.commit()
    
    @classmethod
    def clear_expired_cache(cls):
        """清除过期的缓存条目"""
        cls.query.filter(cls.expires_at <= datetime.now()).delete()
        db.session.commit()
    
    def get_value(self) -> Any:
        """获取缓存值"""
        return json.loads(self.cache_value)


class CacheService:
    """缓存服务"""
    
    # 缓存类型常量
    ANALYTICS_OVERALL = 'analytics_overall'
    ANALYTICS_MONTHLY = 'analytics_monthly'
    PROFIT_DISTRIBUTION = 'profit_distribution'
    CURRENT_HOLDINGS = 'current_holdings'
    TRADE_PAIRS = 'trade_pairs'
    STOCK_PRICES = 'stock_prices'
    
    @classmethod
    def generate_cache_key(cls, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将参数转换为字符串并排序
        key_parts = [prefix]
        
        # 添加位置参数
        for arg in args:
            key_parts.append(str(arg))
        
        # 添加关键字参数（按键排序）
        for key in sorted(kwargs.keys()):
            key_parts.append(f"{key}={kwargs[key]}")
        
        # 生成MD5哈希
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @classmethod
    def get_cached_result(cls, cache_key: str) -> Optional[Any]:
        """获取缓存结果"""
        cache_entry = CacheEntry.get_valid_cache(cache_key)
        if cache_entry:
            return cache_entry.get_value()
        return None
    
    @classmethod
    def set_cached_result(cls, cache_key: str, value: Any, cache_type: str, 
                         expires_in_minutes: int = 30) -> None:
        """设置缓存结果"""
        CacheEntry.set_cache(cache_key, value, cache_type, expires_in_minutes)
    
    @classmethod
    def invalidate_cache_by_type(cls, cache_type: str) -> None:
        """使指定类型的缓存失效"""
        CacheEntry.clear_cache_by_type(cache_type)
    
    @classmethod
    def cleanup_expired_cache(cls) -> None:
        """清理过期缓存"""
        CacheEntry.clear_expired_cache()
    
    @classmethod
    def cache_analytics_data(cls, func):
        """分析数据缓存装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = cls.generate_cache_key(
                f"analytics_{func.__name__}", *args, **kwargs
            )
            
            # 尝试从缓存获取结果
            cached_result = cls.get_cached_result(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行原函数
            result = func(*args, **kwargs)
            
            # 缓存结果（分析数据缓存30分钟）
            cls.set_cached_result(
                cache_key, result, cls.ANALYTICS_OVERALL, 30
            )
            
            return result
        return wrapper
    
    @classmethod
    def cache_profit_distribution(cls, func):
        """收益分布缓存装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = cls.generate_cache_key(
                f"profit_dist_{func.__name__}", *args, **kwargs
            )
            
            cached_result = cls.get_cached_result(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            
            # 收益分布数据缓存1小时
            cls.set_cached_result(
                cache_key, result, cls.PROFIT_DISTRIBUTION, 60
            )
            
            return result
        return wrapper
    
    @classmethod
    def cache_current_holdings(cls, func):
        """当前持仓缓存装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = cls.generate_cache_key(
                f"holdings_{func.__name__}", *args, **kwargs
            )
            
            cached_result = cls.get_cached_result(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            
            # 持仓数据缓存15分钟（因为价格变化较快）
            cls.set_cached_result(
                cache_key, result, cls.CURRENT_HOLDINGS, 15
            )
            
            return result
        return wrapper
    
    @classmethod
    def invalidate_analytics_cache(cls):
        """使分析相关缓存失效"""
        cls.invalidate_cache_by_type(cls.ANALYTICS_OVERALL)
        cls.invalidate_cache_by_type(cls.ANALYTICS_MONTHLY)
        cls.invalidate_cache_by_type(cls.PROFIT_DISTRIBUTION)
        cls.invalidate_cache_by_type(cls.CURRENT_HOLDINGS)
        cls.invalidate_cache_by_type(cls.TRADE_PAIRS)
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """获取缓存统计信息"""
        from sqlalchemy import func as sql_func
        
        # 按类型统计缓存条目数量
        cache_counts = db.session.query(
            CacheEntry.cache_type,
            sql_func.count(CacheEntry.id).label('count'),
            sql_func.min(CacheEntry.created_at).label('oldest'),
            sql_func.max(CacheEntry.created_at).label('newest')
        ).group_by(CacheEntry.cache_type).all()
        
        # 统计过期缓存
        expired_count = CacheEntry.query.filter(
            CacheEntry.expires_at <= datetime.now()
        ).count()
        
        # 统计总缓存大小（近似）
        total_size = db.session.query(
            sql_func.sum(sql_func.length(CacheEntry.cache_value))
        ).scalar() or 0
        
        return {
            'cache_types': [
                {
                    'type': row.cache_type,
                    'count': row.count,
                    'oldest': row.oldest.isoformat() if row.oldest else None,
                    'newest': row.newest.isoformat() if row.newest else None
                }
                for row in cache_counts
            ],
            'expired_count': expired_count,
            'total_size_bytes': total_size,
            'total_entries': sum(row.count for row in cache_counts)
        }


def invalidate_cache_on_trade_change(func):
    """交易数据变更时使缓存失效的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        # 交易数据变更后，使相关缓存失效
        CacheService.invalidate_analytics_cache()
        return result
    return wrapper