"""
性能优化测试运行器
验证缓存机制、优化查询和API端点
"""
import time
import requests
import json
from app import create_app
from extensions import db
from services.cache_service import CacheService
from services.optimized_analytics_service import OptimizedAnalyticsService


def test_cache_service():
    """测试缓存服务"""
    print("=== 测试缓存服务 ===")
    
    app = create_app()
    with app.app_context():
        # 测试设置和获取缓存
        test_data = {'test': 'cache_data', 'number': 123}
        cache_key = 'test_performance_cache'
        
        print("1. 设置缓存...")
        CacheService.set_cached_result(
            cache_key, test_data, CacheService.ANALYTICS_OVERALL, 30
        )
        
        print("2. 获取缓存...")
        cached_result = CacheService.get_cached_result(cache_key)
        
        if cached_result and cached_result['test'] == 'cache_data':
            print("✓ 缓存服务正常工作")
        else:
            print("✗ 缓存服务异常")
        
        # 测试缓存统计
        print("3. 获取缓存统计...")
        stats = CacheService.get_cache_stats()
        print(f"   缓存条目数: {stats['total_entries']}")
        print(f"   过期条目数: {stats['expired_count']}")


def test_optimized_queries():
    """测试优化查询性能"""
    print("\n=== 测试优化查询性能 ===")
    
    app = create_app()
    with app.app_context():
        # 测试总体统计查询
        print("1. 测试总体统计查询...")
        start_time = time.time()
        try:
            stats = OptimizedAnalyticsService.get_overall_statistics()
            query_time = time.time() - start_time
            print(f"   查询时间: {query_time:.3f}秒")
            print(f"   数据项数: {len(stats)}")
            print("✓ 总体统计查询成功")
        except Exception as e:
            print(f"✗ 总体统计查询失败: {str(e)}")
        
        # 测试持仓查询
        print("2. 测试持仓查询...")
        start_time = time.time()
        try:
            holdings = OptimizedAnalyticsService._get_optimized_current_holdings()
            query_time = time.time() - start_time
            print(f"   查询时间: {query_time:.3f}秒")
            print(f"   持仓股票数: {len(holdings)}")
            print("✓ 持仓查询成功")
        except Exception as e:
            print(f"✗ 持仓查询失败: {str(e)}")
        
        # 测试缓存效果
        print("3. 测试缓存效果...")
        start_time = time.time()
        try:
            # 第二次调用应该使用缓存
            stats2 = OptimizedAnalyticsService.get_overall_statistics()
            cached_time = time.time() - start_time
            print(f"   缓存查询时间: {cached_time:.3f}秒")
            print("✓ 缓存机制正常工作")
        except Exception as e:
            print(f"✗ 缓存机制异常: {str(e)}")


def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    
    app = create_app()
    
    with app.test_client() as client:
        # 测试总体统计API
        print("1. 测试总体统计API...")
        start_time = time.time()
        response = client.get('/api/optimized-analytics/overall')
        api_time = time.time() - start_time
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   API响应时间: {api_time:.3f}秒")
            print(f"   响应状态: {data.get('success', False)}")
            print("✓ 总体统计API正常")
        else:
            print(f"✗ 总体统计API异常: {response.status_code}")
        
        # 测试缓存统计API
        print("2. 测试缓存统计API...")
        response = client.get('/api/optimized-analytics/cache/stats')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            cache_data = data.get('data', {})
            print(f"   缓存条目数: {cache_data.get('total_entries', 0)}")
            print("✓ 缓存统计API正常")
        else:
            print(f"✗ 缓存统计API异常: {response.status_code}")
        
        # 测试性能基准API
        print("3. 测试性能基准API...")
        response = client.get('/api/optimized-analytics/benchmark')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            benchmark_data = data.get('data', {})
            summary = benchmark_data.get('summary', {})
            print(f"   平均查询时间: {summary.get('average_time_ms', 0)}ms")
            print("✓ 性能基准API正常")
        else:
            print(f"✗ 性能基准API异常: {response.status_code}")
        
        # 测试健康检查API
        print("4. 测试健康检查API...")
        response = client.get('/api/optimized-analytics/health')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            health_data = data.get('data', {})
            print(f"   系统状态: {health_data.get('status', 'unknown')}")
            print(f"   数据库状态: {health_data.get('database', 'unknown')}")
            print("✓ 健康检查API正常")
        else:
            print(f"✗ 健康检查API异常: {response.status_code}")


def test_performance_comparison():
    """测试性能对比"""
    print("\n=== 性能对比测试 ===")
    
    app = create_app()
    with app.app_context():
        # 清除缓存以确保公平对比
        CacheService.invalidate_analytics_cache()
        
        # 测试优化版本性能
        print("1. 测试优化版本性能...")
        start_time = time.time()
        try:
            optimized_stats = OptimizedAnalyticsService.get_overall_statistics()
            optimized_time = time.time() - start_time
            print(f"   优化版本查询时间: {optimized_time:.3f}秒")
        except Exception as e:
            print(f"✗ 优化版本查询失败: {str(e)}")
            return
        
        # 测试原始版本性能
        print("2. 测试原始版本性能...")
        start_time = time.time()
        try:
            from services.analytics_service import AnalyticsService
            original_stats = AnalyticsService.get_overall_statistics()
            original_time = time.time() - start_time
            print(f"   原始版本查询时间: {original_time:.3f}秒")
        except Exception as e:
            print(f"✗ 原始版本查询失败: {str(e)}")
            return
        
        # 计算性能提升
        if original_time > 0:
            improvement = ((original_time - optimized_time) / original_time) * 100
            print(f"3. 性能提升: {improvement:.1f}%")
            
            if improvement > 0:
                print("✓ 性能优化有效")
            else:
                print("⚠ 性能优化效果不明显")
        
        # 验证数据一致性
        print("4. 验证数据一致性...")
        try:
            # 比较关键数据字段
            key_fields = ['total_investment', 'current_holdings_count']
            consistent = True
            
            for field in key_fields:
                if abs(optimized_stats.get(field, 0) - original_stats.get(field, 0)) > 0.01:
                    print(f"   ✗ 字段 {field} 数据不一致")
                    consistent = False
            
            if consistent:
                print("✓ 数据一致性验证通过")
            else:
                print("✗ 数据一致性验证失败")
        except Exception as e:
            print(f"✗ 数据一致性验证异常: {str(e)}")


def main():
    """主测试函数"""
    print("开始性能优化测试...")
    print("=" * 50)
    
    try:
        test_cache_service()
        test_optimized_queries()
        test_api_endpoints()
        test_performance_comparison()
        
        print("\n" + "=" * 50)
        print("性能优化测试完成！")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()