"""
优化的统计分析服务
使用缓存和优化的数据库查询提高性能
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from collections import defaultdict
from sqlalchemy import func, and_, or_, desc, asc, extract, text
from sqlalchemy.orm import joinedload
from extensions import db
from models.trade_record import TradeRecord
from models.stock_price import StockPrice
from models.profit_distribution_config import ProfitDistributionConfig
from services.base_service import BaseService
from services.cache_service import CacheService, invalidate_cache_on_trade_change
from services.trade_pair_analyzer import TradePairAnalyzer
from error_handlers import ValidationError, DatabaseError


class OptimizedAnalyticsService(BaseService):
    """优化的统计分析服务"""
    
    @classmethod
    @CacheService.cache_analytics_data
    def get_overall_statistics(cls) -> Dict[str, Any]:
        """获取总体收益统计概览（缓存版本）
        
        Requirements: 1.1, 1.2, 1.3, 1.4, 5.1, 5.2
        - 显示总体收益概览
        - 显示已清仓收益、持仓浮盈浮亏、总收益率
        - 新增：已清仓收益和当前持仓收益的独立显示
        """
        try:
            # 使用优化的查询获取交易数据
            trade_summary = cls._get_optimized_trade_summary()
            
            # 计算持仓情况（使用缓存）
            holdings = cls._get_optimized_current_holdings()
            
            # 计算已清仓收益
            realized_profit = trade_summary['realized_profit']
            
            # 计算当前持仓收益
            current_holdings_profit = sum(
                holding['profit_amount'] for holding in holdings.values()
            )
            
            # 计算总投入资金
            total_investment = trade_summary['total_buy_amount']
            
            # 计算总收益率
            total_profit = realized_profit + current_holdings_profit
            total_return_rate = (total_profit / total_investment * 100) if total_investment > 0 else 0
            
            # 计算成功率
            success_rate = cls._calculate_optimized_success_rate()
            
            return {
                'total_investment': float(total_investment),
                'realized_profit': float(realized_profit),
                'current_holdings_profit': float(current_holdings_profit),
                # 保持向后兼容性
                'closed_profit': float(realized_profit),
                'floating_profit': float(current_holdings_profit),
                'total_profit': float(total_profit),
                'total_return_rate': float(total_return_rate),
                'current_holdings_count': len(holdings),
                'total_buy_count': trade_summary['buy_count'],
                'total_sell_count': trade_summary['sell_count'],
                'success_rate': float(success_rate),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            raise DatabaseError(f"获取总体统计失败: {str(e)}")
    
    @classmethod
    @CacheService.cache_profit_distribution
    def get_profit_distribution(cls, use_trade_pairs: bool = True) -> Dict[str, Any]:
        """获取收益分布区间分析（缓存版本）
        
        Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
        """
        try:
            # 获取活跃的收益分布配置
            profit_configs = ProfitDistributionConfig.get_active_configs()
            
            if not profit_configs:
                ProfitDistributionConfig.create_default_configs()
                profit_configs = ProfitDistributionConfig.get_active_configs()
            
            if use_trade_pairs:
                return cls._get_optimized_trade_pair_distribution(profit_configs)
            else:
                return cls._get_optimized_legacy_distribution(profit_configs)
        except Exception as e:
            raise DatabaseError(f"获取收益分布失败: {str(e)}")
    
    @classmethod
    @CacheService.cache_analytics_data
    def get_monthly_statistics(cls, year: int = None) -> Dict[str, Any]:
        """获取月度交易统计和收益率（缓存版本）
        
        Requirements: 5.1, 5.2, 5.3, 5.4
        """
        try:
            if year is None:
                year = datetime.now().year
            
            # 验证年份范围
            current_year = datetime.now().year
            if year < 2000 or year > current_year + 1:
                raise ValidationError(f"年份必须在2000到{current_year + 1}之间")
            
            # 使用优化的查询获取年度数据
            monthly_data = cls._get_optimized_monthly_data(year)
            
            # 计算年度汇总
            year_summary = cls._calculate_year_summary(monthly_data, year)
            
            return {
                'year_summary': year_summary,
                'monthly_data': monthly_data
            }
        except ValidationError as e:
            raise e
        except Exception as e:
            raise DatabaseError(f"获取月度统计失败: {str(e)}")
    
    @classmethod
    @CacheService.cache_current_holdings
    def get_current_holdings_with_performance(cls) -> Dict[str, Any]:
        """获取当前持仓及性能数据（缓存版本）"""
        try:
            holdings = cls._get_optimized_current_holdings()
            
            # 计算性能指标
            total_cost = sum(holding['total_cost'] for holding in holdings.values())
            total_market_value = sum(holding['market_value'] for holding in holdings.values())
            total_profit = sum(holding['profit_amount'] for holding in holdings.values())
            
            return {
                'holdings': holdings,
                'summary': {
                    'total_stocks': len(holdings),
                    'total_cost': float(total_cost),
                    'total_market_value': float(total_market_value),
                    'total_profit': float(total_profit),
                    'total_profit_rate': float(total_profit / total_cost * 100) if total_cost > 0 else 0
                }
            }
        except Exception as e:
            raise DatabaseError(f"获取持仓数据失败: {str(e)}")
    
    @classmethod
    def _get_optimized_trade_summary(cls) -> Dict[str, Any]:
        """使用优化查询获取交易汇总数据"""
        # 使用原生SQL查询获取汇总数据
        sql = text("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN trade_type = 'buy' THEN 1 ELSE 0 END) as buy_count,
                SUM(CASE WHEN trade_type = 'sell' THEN 1 ELSE 0 END) as sell_count,
                SUM(CASE WHEN trade_type = 'buy' THEN price * quantity ELSE 0 END) as total_buy_amount,
                SUM(CASE WHEN trade_type = 'sell' THEN price * quantity ELSE 0 END) as total_sell_amount
            FROM trade_records 
            WHERE is_corrected = 0
        """)
        
        result = db.session.execute(sql).fetchone()
        
        # 计算已清仓收益
        realized_profit = cls._calculate_optimized_realized_profit()
        
        return {
            'total_trades': result.total_trades or 0,
            'buy_count': result.buy_count or 0,
            'sell_count': result.sell_count or 0,
            'total_buy_amount': float(result.total_buy_amount or 0),
            'total_sell_amount': float(result.total_sell_amount or 0),
            'realized_profit': realized_profit
        }
    
    @classmethod
    def _calculate_optimized_realized_profit(cls) -> float:
        """使用优化查询计算已清仓收益"""
        # 使用SQL查询直接计算已清仓股票的收益
        sql = text("""
            WITH stock_positions AS (
                SELECT 
                    stock_code,
                    SUM(CASE WHEN trade_type = 'buy' THEN quantity ELSE -quantity END) as net_position,
                    SUM(CASE WHEN trade_type = 'buy' THEN price * quantity ELSE 0 END) as total_cost,
                    SUM(CASE WHEN trade_type = 'sell' THEN price * quantity ELSE 0 END) as total_revenue
                FROM trade_records 
                WHERE is_corrected = 0
                GROUP BY stock_code
            )
            SELECT COALESCE(SUM(total_revenue - total_cost), 0) as realized_profit
            FROM stock_positions 
            WHERE net_position = 0
        """)
        
        result = db.session.execute(sql).fetchone()
        return float(result.realized_profit) if result else 0.0
    
    @classmethod
    def _get_optimized_current_holdings(cls) -> Dict[str, Dict[str, Any]]:
        """使用优化查询获取当前持仓"""
        # 使用SQL查询直接计算持仓
        sql = text("""
            WITH stock_positions AS (
                SELECT 
                    stock_code,
                    MAX(stock_name) as stock_name,
                    SUM(CASE WHEN trade_type = 'buy' THEN quantity ELSE -quantity END) as net_quantity,
                    SUM(CASE WHEN trade_type = 'buy' THEN price * quantity ELSE 0 END) as total_cost
                FROM trade_records 
                WHERE is_corrected = 0
                GROUP BY stock_code
                HAVING SUM(CASE WHEN trade_type = 'buy' THEN quantity ELSE -quantity END) > 0
            )
            SELECT * FROM stock_positions
        """)
        
        results = db.session.execute(sql).fetchall()
        holdings = {}
        
        for row in results:
            stock_code = row.stock_code
            quantity = int(row.net_quantity or 0)
            total_cost = float(row.total_cost or 0)
            avg_cost = total_cost / quantity if quantity > 0 else 0
            
            # 获取当前价格
            latest_price = StockPrice.get_latest_price(stock_code)
            current_price = float(latest_price.current_price) if latest_price and latest_price.current_price else avg_cost
            
            market_value = current_price * quantity
            profit_amount = market_value - total_cost
            profit_rate = profit_amount / total_cost if total_cost > 0 else 0
            
            holdings[stock_code] = {
                'stock_name': row.stock_name or '',
                'quantity': quantity,
                'total_cost': total_cost,
                'avg_cost': avg_cost,
                'current_price': current_price,
                'market_value': market_value,
                'profit_amount': profit_amount,
                'profit_rate': profit_rate
            }
        
        return holdings
    
    @classmethod
    def _calculate_optimized_success_rate(cls) -> float:
        """使用优化查询计算成功率"""
        sql = text("""
            WITH stock_positions AS (
                SELECT 
                    stock_code,
                    SUM(CASE WHEN trade_type = 'buy' THEN quantity ELSE -quantity END) as net_position,
                    SUM(CASE WHEN trade_type = 'buy' THEN price * quantity ELSE 0 END) as total_cost,
                    SUM(CASE WHEN trade_type = 'sell' THEN price * quantity ELSE 0 END) as total_revenue
                FROM trade_records 
                WHERE is_corrected = 0
                GROUP BY stock_code
            ),
            closed_positions AS (
                SELECT 
                    COUNT(*) as total_closed,
                    SUM(CASE WHEN total_revenue > total_cost THEN 1 ELSE 0 END) as profitable_closed
                FROM stock_positions 
                WHERE net_position = 0
            )
            SELECT 
                COALESCE(profitable_closed, 0) as profitable_closed,
                COALESCE(total_closed, 0) as total_closed
            FROM closed_positions
        """)
        
        result = db.session.execute(sql).fetchone()
        if result and result.total_closed > 0:
            return float(result.profitable_closed / result.total_closed * 100)
        return 0.0
    
    @classmethod
    def _get_optimized_monthly_data(cls, year: int) -> List[Dict[str, Any]]:
        """使用优化查询获取月度数据"""
        # 使用单个查询获取年度所有月份的数据
        sql = text("""
            SELECT 
                CAST(strftime('%m', trade_date) AS INTEGER) as month,
                COUNT(*) as total_trades,
                SUM(CASE WHEN trade_type = 'buy' THEN 1 ELSE 0 END) as buy_count,
                SUM(CASE WHEN trade_type = 'sell' THEN 1 ELSE 0 END) as sell_count,
                SUM(CASE WHEN trade_type = 'buy' THEN price * quantity ELSE 0 END) as buy_amount,
                SUM(CASE WHEN trade_type = 'sell' THEN price * quantity ELSE 0 END) as sell_amount,
                COUNT(DISTINCT stock_code) as unique_stocks
            FROM trade_records 
            WHERE CAST(strftime('%Y', trade_date) AS INTEGER) = :year 
                AND is_corrected = 0
            GROUP BY CAST(strftime('%m', trade_date) AS INTEGER)
            ORDER BY month
        """)
        
        results = db.session.execute(sql, {'year': year}).fetchall()
        
        # 初始化所有月份的数据
        monthly_stats = {}
        for month in range(1, 13):
            monthly_stats[month] = {
                'month': month,
                'month_name': f"{year}-{month:02d}",
                'buy_count': 0,
                'sell_count': 0,
                'total_trades': 0,
                'buy_amount': 0,
                'sell_amount': 0,
                'profit_amount': 0,
                'profit_rate': None,
                'success_count': 0,
                'success_rate': 0,
                'unique_stocks': 0,
                'has_data': False
            }
        
        # 填充实际数据
        for row in results:
            month = int(row.month)
            monthly_stats[month].update({
                'buy_count': row.buy_count,
                'sell_count': row.sell_count,
                'total_trades': row.total_trades,
                'buy_amount': float(row.buy_amount or 0),
                'sell_amount': float(row.sell_amount or 0),
                'unique_stocks': row.unique_stocks,
                'has_data': True
            })
            
            # 计算月度收益率（简化版本，可以进一步优化）
            if row.buy_amount and row.buy_amount > 0:
                profit = float(row.sell_amount or 0) - float(row.buy_amount or 0)
                monthly_stats[month]['profit_amount'] = profit
                monthly_stats[month]['profit_rate'] = profit / float(row.buy_amount)
        
        return list(monthly_stats.values())
    
    @classmethod
    def _calculate_year_summary(cls, monthly_data: List[Dict], year: int) -> Dict[str, Any]:
        """计算年度汇总数据"""
        valid_months = [stats for stats in monthly_data if stats['has_data']]
        
        return {
            'year': year,
            'total_buy_count': sum(stats['buy_count'] for stats in monthly_data),
            'total_sell_count': sum(stats['sell_count'] for stats in monthly_data),
            'total_trades': sum(stats['total_trades'] for stats in monthly_data),
            'total_buy_amount': sum(stats['buy_amount'] for stats in monthly_data),
            'total_sell_amount': sum(stats['sell_amount'] for stats in monthly_data),
            'total_profit': sum(stats['profit_amount'] for stats in monthly_data),
            'average_success_rate': sum(stats['success_rate'] for stats in valid_months) / len(valid_months) if valid_months else 0,
            'months_with_data': len(valid_months),
            'average_monthly_return': sum(stats['profit_rate'] for stats in valid_months if stats['profit_rate'] is not None) / len([s for s in valid_months if s['profit_rate'] is not None]) if any(s['profit_rate'] is not None for s in valid_months) else 0
        }
    
    @classmethod
    def _get_optimized_trade_pair_distribution(cls, profit_configs: List) -> Dict[str, Any]:
        """使用优化的交易配对分析获取收益分布"""
        # 使用缓存的交易配对数据
        cache_key = CacheService.generate_cache_key('trade_pairs_analysis')
        cached_pairs = CacheService.get_cached_result(cache_key)
        
        if cached_pairs is None:
            # 如果缓存中没有，重新计算
            completed_pairs = TradePairAnalyzer.analyze_completed_trades()
            CacheService.set_cached_result(
                cache_key, completed_pairs, CacheService.TRADE_PAIRS, 60
            )
        else:
            completed_pairs = cached_pairs
        
        if not completed_pairs:
            return {
                'total_trades': 0,
                'distribution': [],
                'summary': {
                    'total_profit': 0,
                    'average_profit_rate': 0,
                    'win_rate': 0
                }
            }
        
        # 计算分布
        distribution = []
        for config in profit_configs:
            distribution.append({
                'range_name': config.range_name,
                'min_rate': config.min_profit_rate,
                'max_rate': config.max_profit_rate,
                'count': 0,
                'percentage': 0,
                'total_profit': 0
            })
        
        # 统计分布
        total_trades = len(completed_pairs)
        total_profit = 0
        winning_trades = 0
        
        for pair in completed_pairs:
            profit_rate = pair['profit_rate']
            total_profit += pair['profit']
            
            if pair['profit'] > 0:
                winning_trades += 1
            
            # 分配到对应区间
            for dist_item in distribution:
                min_rate = dist_item['min_rate']
                max_rate = dist_item['max_rate']
                
                in_range = True
                if min_rate is not None and profit_rate < min_rate:
                    in_range = False
                if max_rate is not None and profit_rate >= max_rate:
                    in_range = False
                
                if in_range:
                    dist_item['count'] += 1
                    dist_item['total_profit'] += pair['profit']
                    break
        
        # 计算百分比
        for dist_item in distribution:
            if total_trades > 0:
                dist_item['percentage'] = (dist_item['count'] / total_trades) * 100
        
        # 计算汇总统计
        average_profit_rate = sum(pair['profit_rate'] for pair in completed_pairs) / total_trades if total_trades > 0 else 0
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'distribution': distribution,
            'summary': {
                'total_profit': total_profit,
                'average_profit_rate': average_profit_rate,
                'win_rate': win_rate
            }
        }
    
    @classmethod
    def _get_optimized_legacy_distribution(cls, profit_configs: List) -> Dict[str, Any]:
        """优化的传统收益分布分析"""
        # 获取缓存的持仓数据
        holdings = cls._get_optimized_current_holdings()
        
        # 获取已清仓股票数据
        closed_positions = cls._get_optimized_closed_positions()
        
        # 初始化分布统计
        distribution = []
        for config in profit_configs:
            distribution.append({
                'range_name': config.range_name,
                'min_rate': config.min_profit_rate,
                'max_rate': config.max_profit_rate,
                'count': 0,
                'percentage': 0,
                'total_profit': 0,
                'stocks': []
            })
        
        # 统计持仓股票分布
        for stock_code, holding in holdings.items():
            profit_rate = holding['profit_rate']
            for dist_item in distribution:
                min_rate = dist_item['min_rate']
                max_rate = dist_item['max_rate']
                
                in_range = True
                if min_rate is not None and profit_rate < min_rate:
                    in_range = False
                if max_rate is not None and profit_rate >= max_rate:
                    in_range = False
                
                if in_range:
                    dist_item['count'] += 1
                    dist_item['total_profit'] += holding['profit_amount']
                    dist_item['stocks'].append({
                        'stock_code': stock_code,
                        'stock_name': holding['stock_name'],
                        'profit_rate': profit_rate,
                        'profit_amount': holding['profit_amount'],
                        'status': 'holding'
                    })
                    break
        
        # 统计已清仓股票分布
        for position in closed_positions:
            profit_rate = position['profit_rate']
            for dist_item in distribution:
                min_rate = dist_item['min_rate']
                max_rate = dist_item['max_rate']
                
                in_range = True
                if min_rate is not None and profit_rate < min_rate:
                    in_range = False
                if max_rate is not None and profit_rate >= max_rate:
                    in_range = False
                
                if in_range:
                    dist_item['count'] += 1
                    dist_item['total_profit'] += position['profit_amount']
                    dist_item['stocks'].append({
                        'stock_code': position['stock_code'],
                        'stock_name': position['stock_name'],
                        'profit_rate': profit_rate,
                        'profit_amount': position['profit_amount'],
                        'status': 'closed'
                    })
                    break
        
        # 计算总股票数和百分比
        total_stocks = sum(dist_item['count'] for dist_item in distribution)
        for dist_item in distribution:
            dist_item['percentage'] = (dist_item['count'] / total_stocks * 100) if total_stocks > 0 else 0
        
        return {
            'total_trades': total_stocks,
            'distribution': distribution,
            'summary': {
                'total_profit': sum(dist_item['total_profit'] for dist_item in distribution),
                'average_profit_rate': 0,
                'win_rate': 0
            },
            'holding_stocks': len(holdings),
            'closed_stocks': len(closed_positions)
        }
    
    @classmethod
    def _get_optimized_closed_positions(cls) -> List[Dict[str, Any]]:
        """使用优化查询获取已清仓股票详情"""
        sql = text("""
            WITH stock_positions AS (
                SELECT 
                    stock_code,
                    MAX(stock_name) as stock_name,
                    SUM(CASE WHEN trade_type = 'buy' THEN quantity ELSE -quantity END) as net_position,
                    SUM(CASE WHEN trade_type = 'buy' THEN price * quantity ELSE 0 END) as total_cost,
                    SUM(CASE WHEN trade_type = 'sell' THEN price * quantity ELSE 0 END) as total_revenue
                FROM trade_records 
                WHERE is_corrected = 0
                GROUP BY stock_code
                HAVING SUM(CASE WHEN trade_type = 'buy' THEN quantity ELSE -quantity END) = 0
            )
            SELECT 
                stock_code,
                stock_name,
                total_cost,
                total_revenue,
                (total_revenue - total_cost) as profit_amount,
                CASE 
                    WHEN total_cost > 0 THEN (total_revenue - total_cost) / total_cost
                    ELSE 0 
                END as profit_rate
            FROM stock_positions
        """)
        
        results = db.session.execute(sql).fetchall()
        
        return [
            {
                'stock_code': row.stock_code,
                'stock_name': row.stock_name,
                'total_cost': float(row.total_cost),
                'total_revenue': float(row.total_revenue),
                'profit_amount': float(row.profit_amount),
                'profit_rate': float(row.profit_rate)
            }
            for row in results
        ]
    
    @classmethod
    @invalidate_cache_on_trade_change
    def invalidate_cache_on_data_change(cls):
        """数据变更时使缓存失效"""
        CacheService.invalidate_analytics_cache()
    
    @classmethod
    def get_performance_metrics(cls) -> Dict[str, Any]:
        """获取系统性能指标"""
        try:
            # 获取缓存统计
            cache_stats = CacheService.get_cache_stats()
            
            # 获取数据库统计
            db_stats = cls._get_database_stats()
            
            # 获取查询性能统计
            query_stats = cls._get_query_performance_stats()
            
            return {
                'cache_stats': cache_stats,
                'database_stats': db_stats,
                'query_performance': query_stats,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            raise DatabaseError(f"获取性能指标失败: {str(e)}")
    
    @classmethod
    def _get_database_stats(cls) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            # 获取表记录数
            trade_count = TradeRecord.query.count()
            price_count = StockPrice.query.count()
            
            # 获取数据库大小（SQLite特定）
            db_size_result = db.session.execute(text("PRAGMA page_count")).fetchone()
            page_size_result = db.session.execute(text("PRAGMA page_size")).fetchone()
            
            db_size = (db_size_result[0] * page_size_result[0]) if db_size_result and page_size_result else 0
            
            return {
                'trade_records_count': trade_count,
                'stock_prices_count': price_count,
                'database_size_bytes': db_size,
                'database_size_mb': round(db_size / 1024 / 1024, 2)
            }
        except Exception as e:
            return {
                'error': f"获取数据库统计失败: {str(e)}",
                'trade_records_count': 0,
                'stock_prices_count': 0,
                'database_size_bytes': 0,
                'database_size_mb': 0
            }
    
    @classmethod
    def _get_query_performance_stats(cls) -> Dict[str, Any]:
        """获取查询性能统计"""
        import time
        
        performance_tests = []
        
        # 测试基本查询性能
        start_time = time.time()
        TradeRecord.query.filter_by(is_corrected=False).count()
        basic_query_time = time.time() - start_time
        performance_tests.append({
            'test_name': 'basic_trade_count',
            'execution_time_ms': round(basic_query_time * 1000, 2)
        })
        
        # 测试复杂聚合查询性能
        start_time = time.time()
        cls._get_optimized_trade_summary()
        complex_query_time = time.time() - start_time
        performance_tests.append({
            'test_name': 'complex_trade_summary',
            'execution_time_ms': round(complex_query_time * 1000, 2)
        })
        
        # 测试持仓查询性能
        start_time = time.time()
        cls._get_optimized_current_holdings()
        holdings_query_time = time.time() - start_time
        performance_tests.append({
            'test_name': 'current_holdings',
            'execution_time_ms': round(holdings_query_time * 1000, 2)
        })
        
        return {
            'performance_tests': performance_tests,
            'average_query_time_ms': round(
                sum(test['execution_time_ms'] for test in performance_tests) / len(performance_tests), 2
            )
        }