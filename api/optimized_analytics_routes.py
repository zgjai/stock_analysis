"""
优化的分析API路由
提供高性能的数据分析接口
"""
from flask import Blueprint, request, jsonify
from services.optimized_analytics_service import OptimizedAnalyticsService
from services.cache_service import CacheService
from error_handlers import ValidationError, DatabaseError, create_success_response, create_error_response
import logging

# 创建蓝图
optimized_analytics_bp = Blueprint('optimized_analytics', __name__, url_prefix='/api/optimized-analytics')

logger = logging.getLogger(__name__)


@optimized_analytics_bp.route('/overall', methods=['GET'])
def get_overall_statistics():
    """获取总体统计数据（优化版本）"""
    try:
        data = OptimizedAnalyticsService.get_overall_statistics()
        return create_success_response(data, "获取总体统计成功")
    except Exception as e:
        logger.error(f"获取总体统计失败: {str(e)}")
        return create_error_response("ANALYTICS_ERROR", f"获取总体统计失败: {str(e)}", 500)


@optimized_analytics_bp.route('/monthly', methods=['GET'])
def get_monthly_statistics():
    """获取月度统计数据（优化版本）"""
    try:
        year = request.args.get('year', type=int)
        data = OptimizedAnalyticsService.get_monthly_statistics(year)
        return create_success_response(data, "获取月度统计成功")
    except ValidationError as e:
        return create_error_response("VALIDATION_ERROR", str(e), 400)
    except Exception as e:
        logger.error(f"获取月度统计失败: {str(e)}")
        return create_error_response("ANALYTICS_ERROR", f"获取月度统计失败: {str(e)}", 500)


@optimized_analytics_bp.route('/profit-distribution', methods=['GET'])
def get_profit_distribution():
    """获取收益分布数据（优化版本）"""
    try:
        use_trade_pairs = request.args.get('use_trade_pairs', 'true').lower() == 'true'
        data = OptimizedAnalyticsService.get_profit_distribution(use_trade_pairs)
        return create_success_response(data, "获取收益分布成功")
    except Exception as e:
        logger.error(f"获取收益分布失败: {str(e)}")
        return create_error_response("ANALYTICS_ERROR", f"获取收益分布失败: {str(e)}", 500)


@optimized_analytics_bp.route('/holdings', methods=['GET'])
def get_current_holdings():
    """获取当前持仓数据（优化版本）"""
    try:
        data = OptimizedAnalyticsService.get_current_holdings_with_performance()
        return create_success_response(data, "获取持仓数据成功")
    except Exception as e:
        logger.error(f"获取持仓数据失败: {str(e)}")
        return create_error_response("ANALYTICS_ERROR", f"获取持仓数据失败: {str(e)}", 500)


@optimized_analytics_bp.route('/performance', methods=['GET'])
def get_performance_metrics():
    """获取系统性能指标"""
    try:
        data = OptimizedAnalyticsService.get_performance_metrics()
        return create_success_response(data, "获取性能指标成功")
    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        return create_error_response("ANALYTICS_ERROR", f"获取性能指标失败: {str(e)}", 500)


@optimized_analytics_bp.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """获取缓存统计信息"""
    try:
        data = CacheService.get_cache_stats()
        return create_success_response(data, "获取缓存统计成功")
    except Exception as e:
        logger.error(f"获取缓存统计失败: {str(e)}")
        return create_error_response("CACHE_ERROR", f"获取缓存统计失败: {str(e)}", 500)


@optimized_analytics_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """清除缓存"""
    try:
        cache_type = request.json.get('cache_type') if request.json else None
        
        if cache_type:
            CacheService.invalidate_cache_by_type(cache_type)
            message = f"已清除 {cache_type} 类型的缓存"
        else:
            CacheService.invalidate_analytics_cache()
            message = "已清除所有分析相关缓存"
        
        return create_success_response({}, message)
    except Exception as e:
        logger.error(f"清除缓存失败: {str(e)}")
        return create_error_response("CACHE_ERROR", f"清除缓存失败: {str(e)}", 500)


@optimized_analytics_bp.route('/cache/cleanup', methods=['POST'])
def cleanup_expired_cache():
    """清理过期缓存"""
    try:
        CacheService.cleanup_expired_cache()
        return create_success_response({}, "已清理过期缓存")
    except Exception as e:
        logger.error(f"清理过期缓存失败: {str(e)}")
        return create_error_response("CACHE_ERROR", f"清理过期缓存失败: {str(e)}", 500)


@optimized_analytics_bp.route('/benchmark', methods=['GET'])
def run_performance_benchmark():
    """运行性能基准测试"""
    try:
        import time
        
        # 测试不同查询的性能
        benchmark_results = []
        
        # 测试总体统计查询
        start_time = time.time()
        OptimizedAnalyticsService.get_overall_statistics()
        overall_time = time.time() - start_time
        benchmark_results.append({
            'test_name': 'overall_statistics',
            'execution_time_ms': round(overall_time * 1000, 2),
            'description': '总体统计查询'
        })
        
        # 测试月度统计查询
        start_time = time.time()
        OptimizedAnalyticsService.get_monthly_statistics()
        monthly_time = time.time() - start_time
        benchmark_results.append({
            'test_name': 'monthly_statistics',
            'execution_time_ms': round(monthly_time * 1000, 2),
            'description': '月度统计查询'
        })
        
        # 测试收益分布查询
        start_time = time.time()
        OptimizedAnalyticsService.get_profit_distribution()
        distribution_time = time.time() - start_time
        benchmark_results.append({
            'test_name': 'profit_distribution',
            'execution_time_ms': round(distribution_time * 1000, 2),
            'description': '收益分布查询'
        })
        
        # 测试持仓查询
        start_time = time.time()
        OptimizedAnalyticsService.get_current_holdings_with_performance()
        holdings_time = time.time() - start_time
        benchmark_results.append({
            'test_name': 'current_holdings',
            'execution_time_ms': round(holdings_time * 1000, 2),
            'description': '当前持仓查询'
        })
        
        # 计算总体性能指标
        total_time = sum(result['execution_time_ms'] for result in benchmark_results)
        average_time = total_time / len(benchmark_results)
        
        data = {
            'benchmark_results': benchmark_results,
            'summary': {
                'total_time_ms': round(total_time, 2),
                'average_time_ms': round(average_time, 2),
                'fastest_query': min(benchmark_results, key=lambda x: x['execution_time_ms']),
                'slowest_query': max(benchmark_results, key=lambda x: x['execution_time_ms'])
            },
            'timestamp': time.time()
        }
        
        return create_success_response(data, "性能基准测试完成")
    except Exception as e:
        logger.error(f"性能基准测试失败: {str(e)}")
        return create_error_response("BENCHMARK_ERROR", f"性能基准测试失败: {str(e)}", 500)


@optimized_analytics_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        import time
        # 检查数据库连接
        from extensions import db
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text('SELECT 1')).fetchone()
        
        # 检查缓存服务
        cache_stats = CacheService.get_cache_stats()
        
        # 检查基本查询性能
        start_time = time.time()
        OptimizedAnalyticsService._get_optimized_trade_summary()
        query_time = time.time() - start_time
        
        health_data = {
            'status': 'healthy',
            'database': 'connected',
            'cache_entries': cache_stats['total_entries'],
            'query_performance_ms': round(query_time * 1000, 2),
            'timestamp': time.time()
        }
        
        return create_success_response(health_data, "系统健康状态良好")
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return create_error_response("HEALTH_CHECK_ERROR", f"系统健康检查失败: {str(e)}", 500)


# 错误处理
@optimized_analytics_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    return create_error_response("VALIDATION_ERROR", str(error), 400)


@optimized_analytics_bp.errorhandler(DatabaseError)
def handle_database_error(error):
    logger.error(f"数据库错误: {str(error)}")
    return create_error_response("DATABASE_ERROR", "数据库操作失败", 500)


@optimized_analytics_bp.errorhandler(Exception)
def handle_general_error(error):
    logger.error(f"未处理的错误: {str(error)}")
    return create_error_response("INTERNAL_ERROR", "服务器内部错误", 500)