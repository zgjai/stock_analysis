"""
性能优化工具类
"""
import time
import logging
from functools import wraps
from typing import Dict, Any, List, Optional
from sqlalchemy import text, Index
from extensions import db
from flask import current_app

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """性能优化器"""
    
    @staticmethod
    def create_database_indexes():
        """创建数据库索引以优化查询性能"""
        try:
            logger.info("开始创建数据库索引")
            
            # 历史交易表索引
            historical_trade_indexes = [
                # 复合索引：股票代码 + 完成日期
                "CREATE INDEX IF NOT EXISTS idx_historical_stock_completion ON historical_trades(stock_code, completion_date DESC)",
                
                # 复合索引：收益率 + 完成日期
                "CREATE INDEX IF NOT EXISTS idx_historical_return_completion ON historical_trades(return_rate DESC, completion_date DESC)",
                
                # 复合索引：持仓天数 + 完成日期
                "CREATE INDEX IF NOT EXISTS idx_historical_holding_completion ON historical_trades(holding_days, completion_date DESC)",
                
                # 复合索引：是否盈利 + 收益率
                "CREATE INDEX IF NOT EXISTS idx_historical_profitable_return ON historical_trades((CASE WHEN total_return > 0 THEN 1 ELSE 0 END), return_rate DESC)",
                
                # 买入日期索引
                "CREATE INDEX IF NOT EXISTS idx_historical_buy_date ON historical_trades(buy_date DESC)",
                
                # 卖出日期索引
                "CREATE INDEX IF NOT EXISTS idx_historical_sell_date ON historical_trades(sell_date DESC)",
            ]
            
            # 复盘记录表索引
            review_indexes = [
                # 复合索引：历史交易ID + 创建时间
                "CREATE INDEX IF NOT EXISTS idx_review_trade_created ON trade_reviews(historical_trade_id, created_at DESC)",
                
                # 复合索引：复盘类型 + 总体评分
                "CREATE INDEX IF NOT EXISTS idx_review_type_score ON trade_reviews(review_type, overall_score DESC)",
                
                # 复合索引：总体评分 + 创建时间
                "CREATE INDEX IF NOT EXISTS idx_review_score_created ON trade_reviews(overall_score DESC, created_at DESC)",
                
                # 策略评分索引
                "CREATE INDEX IF NOT EXISTS idx_review_strategy_score ON trade_reviews(strategy_score DESC)",
                
                # 时机评分索引
                "CREATE INDEX IF NOT EXISTS idx_review_timing_score ON trade_reviews(timing_score DESC)",
                
                # 风险控制评分索引
                "CREATE INDEX IF NOT EXISTS idx_review_risk_score ON trade_reviews(risk_control_score DESC)",
            ]
            
            # 复盘图片表索引
            image_indexes = [
                # 复合索引：复盘ID + 显示顺序
                "CREATE INDEX IF NOT EXISTS idx_image_review_order ON review_images(trade_review_id, display_order ASC)",
                
                # 文件名索引（用于快速查找）
                "CREATE INDEX IF NOT EXISTS idx_image_filename ON review_images(filename)",
                
                # 文件大小索引（用于统计）
                "CREATE INDEX IF NOT EXISTS idx_image_size ON review_images(file_size DESC)",
            ]
            
            # 执行索引创建
            all_indexes = historical_trade_indexes + review_indexes + image_indexes
            
            for index_sql in all_indexes:
                try:
                    db.session.execute(text(index_sql))
                    logger.info(f"索引创建成功: {index_sql}")
                except Exception as e:
                    logger.warning(f"索引创建失败: {index_sql}, 错误: {str(e)}")
            
            db.session.commit()
            logger.info("数据库索引创建完成")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建数据库索引失败: {str(e)}")
            raise
    
    @staticmethod
    def optimize_query_performance():
        """优化查询性能设置"""
        try:
            logger.info("开始优化查询性能设置")
            
            # SQLite 性能优化设置
            optimization_queries = [
                # 启用 WAL 模式以提高并发性能
                "PRAGMA journal_mode=WAL",
                
                # 设置同步模式为 NORMAL 以平衡性能和安全性
                "PRAGMA synchronous=NORMAL",
                
                # 增加缓存大小 (10MB)
                "PRAGMA cache_size=10000",
                
                # 启用内存映射 I/O (64MB)
                "PRAGMA mmap_size=67108864",
                
                # 设置临时存储为内存
                "PRAGMA temp_store=MEMORY",
                
                # 优化查询计划器
                "PRAGMA optimize",
            ]
            
            for query in optimization_queries:
                try:
                    db.session.execute(text(query))
                    logger.info(f"性能优化设置成功: {query}")
                except Exception as e:
                    logger.warning(f"性能优化设置失败: {query}, 错误: {str(e)}")
            
            db.session.commit()
            logger.info("查询性能优化完成")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"优化查询性能失败: {str(e)}")
            raise
    
    @staticmethod
    def analyze_table_statistics():
        """分析表统计信息以优化查询计划"""
        try:
            logger.info("开始分析表统计信息")
            
            # 更新表统计信息
            tables = ['historical_trades', 'trade_reviews', 'review_images']
            
            for table in tables:
                try:
                    # 分析表统计信息
                    db.session.execute(text(f"ANALYZE {table}"))
                    logger.info(f"表统计信息分析完成: {table}")
                except Exception as e:
                    logger.warning(f"表统计信息分析失败: {table}, 错误: {str(e)}")
            
            db.session.commit()
            logger.info("表统计信息分析完成")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"分析表统计信息失败: {str(e)}")
            raise
    
    @staticmethod
    def get_query_performance_stats() -> Dict[str, Any]:
        """获取查询性能统计信息"""
        try:
            stats = {}
            
            # 获取数据库大小
            result = db.session.execute(text("PRAGMA page_count")).fetchone()
            page_count = result[0] if result else 0
            
            result = db.session.execute(text("PRAGMA page_size")).fetchone()
            page_size = result[0] if result else 0
            
            stats['database_size_mb'] = (page_count * page_size) / (1024 * 1024)
            
            # 获取缓存统计
            result = db.session.execute(text("PRAGMA cache_size")).fetchone()
            stats['cache_size'] = result[0] if result else 0
            
            # 获取表行数统计
            for table in ['historical_trades', 'trade_reviews', 'review_images']:
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                    stats[f'{table}_count'] = result[0] if result else 0
                except Exception as e:
                    logger.warning(f"获取表行数失败: {table}, 错误: {str(e)}")
                    stats[f'{table}_count'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"获取查询性能统计失败: {str(e)}")
            return {}


def performance_monitor(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 记录性能日志
            if execution_time > 1.0:  # 超过1秒的查询记录警告
                logger.warning(f"慢查询检测: {func.__name__} 执行时间: {execution_time:.2f}秒")
            else:
                logger.info(f"查询性能: {func.__name__} 执行时间: {execution_time:.2f}秒")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"查询失败: {func.__name__} 执行时间: {execution_time:.2f}秒, 错误: {str(e)}")
            raise
    
    return wrapper


class QueryOptimizer:
    """查询优化器"""
    
    @staticmethod
    def optimize_historical_trades_query(query, filters: Dict[str, Any] = None):
        """优化历史交易查询"""
        # 使用索引友好的查询顺序
        if filters:
            # 优先使用选择性高的条件
            if 'stock_code' in filters:
                # 股票代码是高选择性条件，优先使用
                query = query.filter_by(stock_code=filters['stock_code'])
            
            if 'is_profitable' in filters:
                # 盈利状态筛选，使用索引
                if filters['is_profitable']:
                    query = query.filter(query.model.total_return > 0)
                else:
                    query = query.filter(query.model.total_return <= 0)
        
        return query
    
    @staticmethod
    def optimize_pagination(query, page: int, per_page: int):
        """优化分页查询"""
        # 使用 LIMIT 和 OFFSET 优化
        if per_page > 100:
            per_page = 100  # 限制每页最大数量
        
        # 对于大偏移量，使用基于游标的分页
        if page > 100:
            logger.warning(f"大偏移量分页: page={page}, 建议使用基于游标的分页")
        
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
            max_per_page=100
        )


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self._cache = {}
        self._cache_ttl = {}
        self.default_ttl = 300  # 5分钟默认TTL
    
    def get(self, key: str) -> Any:
        """获取缓存值"""
        if key in self._cache:
            # 检查TTL
            if key in self._cache_ttl:
                if time.time() > self._cache_ttl[key]:
                    # 缓存过期
                    del self._cache[key]
                    del self._cache_ttl[key]
                    return None
            
            return self._cache[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """设置缓存值"""
        self._cache[key] = value
        
        if ttl is None:
            ttl = self.default_ttl
        
        self._cache_ttl[key] = time.time() + ttl
    
    def delete(self, key: str) -> None:
        """删除缓存值"""
        if key in self._cache:
            del self._cache[key]
        
        if key in self._cache_ttl:
            del self._cache_ttl[key]
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._cache_ttl.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'cache_size': len(self._cache),
            'cache_keys': list(self._cache.keys())
        }


# 全局缓存管理器实例
cache_manager = CacheManager()