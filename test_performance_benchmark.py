"""
性能基准测试
测试期望对比功能对系统性能的影响

Requirements: 8.5
- 测试不同数据量下的性能表现
- 对比新功能添加前后的性能差异
- 验证系统在高负载下的稳定性
"""

import time
import statistics
import json
import threading
import psutil
import os
from datetime import datetime, timedelta
from flask import Flask
from contextlib import contextmanager
from models.trade_record import TradeRecord
from services.analytics_service import AnalyticsService
from services.expectation_comparison_service import ExpectationComparisonService


class PerformanceBenchmark:
    """性能基准测试类"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.results = {}
        self.process = psutil.Process(os.getpid())
        
    @contextmanager
    def measure_performance(self, test_name):
        """性能测量上下文管理器"""
        # 记录开始状态
        start_time = time.time()
        start_memory = self.process.memory_info().rss
        start_cpu = self.process.cpu_percent()
        
        try:
            yield
        finally:
            # 记录结束状态
            end_time = time.time()
            end_memory = self.process.memory_info().rss
            end_cpu = self.process.cpu_percent()
            
            # 计算性能指标
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            cpu_usage = (start_cpu + end_cpu) / 2
            
            self.results[test_name] = {
                'duration': duration,
                'memory_delta': memory_delta,
                'cpu_usage': cpu_usage,
                'timestamp': datetime.now().isoformat()
            }
    
    def run_benchmark_suite(self):
        """运行完整的性能基准测试套件"""
        
        print("开始性能基准测试...")
        print("=" * 60)
        
        with self.app.app_context():
            # 1. 基础API性能测试
            self.test_basic_api_performance()
            
            # 2. 期望对比功能性能测试
            self.test_expectation_comparison_performance()
            
            # 3. 并发访问性能测试
            self.test_concurrent_access_performance()
            
            # 4. 大数据量性能测试
            self.test_large_dataset_performance()
            
            # 5. 内存使用测试
            self.test_memory_usage()
            
            # 6. 缓存性能测试
            self.test_caching_performance()
        
        # 生成性能报告
        self.generate_performance_report()
    
    def test_basic_api_performance(self):
        """测试基础API性能"""
        
        print("测试基础API性能...")
        
        # 测试总体统计API
        with self.measure_performance('analytics_overview'):
            for _ in range(10):
                AnalyticsService.get_overall_statistics()
        
        # 测试收益分布API
        with self.measure_performance('profit_distribution'):
            for _ in range(10):
                AnalyticsService.get_profit_distribution()
        
        # 测试月度统计API
        with self.measure_performance('monthly_statistics'):
            for _ in range(10):
                AnalyticsService.get_monthly_statistics(datetime.now().year)
        
        print("✓ 基础API性能测试完成")
    
    def test_expectation_comparison_performance(self):
        """测试期望对比功能性能"""
        
        print("测试期望对比功能性能...")
        
        time_ranges = ['30d', '90d', '1y', 'all']
        
        for time_range in time_ranges:
            test_name = f'expectation_comparison_{time_range}'
            
            with self.measure_performance(test_name):
                for _ in range(5):
                    ExpectationComparisonService.get_expectation_comparison(time_range)
        
        print("✓ 期望对比功能性能测试完成")
    
    def test_concurrent_access_performance(self):
        """测试并发访问性能"""
        
        print("测试并发访问性能...")
        
        def concurrent_request():
            """并发请求函数"""
            try:
                # 随机调用不同的API
                import random
                apis = [
                    lambda: AnalyticsService.get_overall_statistics(),
                    lambda: AnalyticsService.get_profit_distribution(),
                    lambda: ExpectationComparisonService.get_expectation_comparison('all'),
                    lambda: AnalyticsService.get_monthly_statistics(datetime.now().year)
                ]
                
                api = random.choice(apis)
                api()
                
            except Exception as e:
                print(f"并发请求异常: {e}")
        
        # 测试不同并发级别
        concurrency_levels = [5, 10, 20]
        
        for level in concurrency_levels:
            test_name = f'concurrent_access_{level}_threads'
            
            with self.measure_performance(test_name):
                threads = []
                
                for _ in range(level):
                    thread = threading.Thread(target=concurrent_request)
                    threads.append(thread)
                    thread.start()
                
                for thread in threads:
                    thread.join()
        
        print("✓ 并发访问性能测试完成")
    
    def test_large_dataset_performance(self):
        """测试大数据量性能"""
        
        print("测试大数据量性能...")
        
        # 获取当前数据量
        trade_count = TradeRecord.query.count()
        
        print(f"当前交易记录数量: {trade_count}")
        
        # 测试不同数据量下的性能
        with self.measure_performance('large_dataset_all_time'):
            # 全时间范围查询
            ExpectationComparisonService.get_expectation_comparison('all')
        
        with self.measure_performance('large_dataset_complex_query'):
            # 复杂查询组合
            AnalyticsService.get_overall_statistics()
            AnalyticsService.get_profit_distribution()
            ExpectationComparisonService.get_expectation_comparison('1y')
        
        print("✓ 大数据量性能测试完成")
    
    def test_memory_usage(self):
        """测试内存使用情况"""
        
        print("测试内存使用情况...")
        
        initial_memory = self.process.memory_info().rss
        
        # 连续执行多次API调用
        with self.measure_performance('memory_stress_test'):
            for i in range(50):
                AnalyticsService.get_overall_statistics()
                ExpectationComparisonService.get_expectation_comparison('all')
                
                # 每10次检查一次内存
                if i % 10 == 0:
                    current_memory = self.process.memory_info().rss
                    memory_increase = current_memory - initial_memory
                    
                    print(f"  第{i+1}次调用后内存增长: {memory_increase / 1024 / 1024:.2f}MB")
                    
                    # 如果内存增长超过100MB，可能存在内存泄漏
                    if memory_increase > 100 * 1024 * 1024:
                        print(f"⚠️  警告: 内存增长过多 ({memory_increase / 1024 / 1024:.2f}MB)")
                        break
        
        final_memory = self.process.memory_info().rss
        total_increase = final_memory - initial_memory
        
        self.results['memory_usage_summary'] = {
            'initial_memory_mb': initial_memory / 1024 / 1024,
            'final_memory_mb': final_memory / 1024 / 1024,
            'total_increase_mb': total_increase / 1024 / 1024
        }
        
        print("✓ 内存使用测试完成")
    
    def test_caching_performance(self):
        """测试缓存性能"""
        
        print("测试缓存性能...")
        
        # 第一次调用（冷缓存）
        with self.measure_performance('cold_cache_call'):
            ExpectationComparisonService.get_expectation_comparison('all')
        
        # 第二次调用（可能的热缓存）
        with self.measure_performance('warm_cache_call'):
            ExpectationComparisonService.get_expectation_comparison('all')
        
        # 连续调用测试
        with self.measure_performance('repeated_calls'):
            for _ in range(10):
                ExpectationComparisonService.get_expectation_comparison('all')
        
        print("✓ 缓存性能测试完成")
    
    def generate_performance_report(self):
        """生成性能报告"""
        
        print("\n" + "=" * 60)
        print("性能测试报告")
        print("=" * 60)
        
        # 按类别组织结果
        categories = {
            '基础API性能': ['analytics_overview', 'profit_distribution', 'monthly_statistics'],
            '期望对比功能': ['expectation_comparison_30d', 'expectation_comparison_90d', 
                         'expectation_comparison_1y', 'expectation_comparison_all'],
            '并发访问性能': ['concurrent_access_5_threads', 'concurrent_access_10_threads', 
                         'concurrent_access_20_threads'],
            '大数据量性能': ['large_dataset_all_time', 'large_dataset_complex_query'],
            '内存和缓存': ['memory_stress_test', 'cold_cache_call', 'warm_cache_call', 'repeated_calls']
        }
        
        for category, tests in categories.items():
            print(f"\n{category}:")
            print("-" * 40)
            
            for test in tests:
                if test in self.results:
                    result = self.results[test]
                    duration = result['duration']
                    memory_mb = result['memory_delta'] / 1024 / 1024
                    cpu = result['cpu_usage']
                    
                    print(f"  {test}:")
                    print(f"    耗时: {duration:.3f}秒")
                    print(f"    内存变化: {memory_mb:+.2f}MB")
                    print(f"    CPU使用: {cpu:.1f}%")
        
        # 性能摘要
        print(f"\n性能摘要:")
        print("-" * 40)
        
        all_durations = [r['duration'] for r in self.results.values() if 'duration' in r]
        if all_durations:
            print(f"  平均响应时间: {statistics.mean(all_durations):.3f}秒")
            print(f"  最快响应时间: {min(all_durations):.3f}秒")
            print(f"  最慢响应时间: {max(all_durations):.3f}秒")
            print(f"  响应时间标准差: {statistics.stdev(all_durations):.3f}秒")
        
        # 内存使用摘要
        if 'memory_usage_summary' in self.results:
            mem_summary = self.results['memory_usage_summary']
            print(f"  初始内存: {mem_summary['initial_memory_mb']:.2f}MB")
            print(f"  最终内存: {mem_summary['final_memory_mb']:.2f}MB")
            print(f"  内存增长: {mem_summary['total_increase_mb']:.2f}MB")
        
        # 性能评级
        self.calculate_performance_rating()
        
        # 保存详细报告
        self.save_detailed_report()
    
    def calculate_performance_rating(self):
        """计算性能评级"""
        
        print(f"\n性能评级:")
        print("-" * 40)
        
        # 基于响应时间的评级
        expectation_times = [
            self.results.get('expectation_comparison_all', {}).get('duration', 0),
            self.results.get('expectation_comparison_1y', {}).get('duration', 0),
            self.results.get('expectation_comparison_90d', {}).get('duration', 0),
            self.results.get('expectation_comparison_30d', {}).get('duration', 0)
        ]
        
        avg_expectation_time = statistics.mean([t for t in expectation_times if t > 0])
        
        if avg_expectation_time < 0.1:
            time_rating = "优秀"
        elif avg_expectation_time < 0.5:
            time_rating = "良好"
        elif avg_expectation_time < 1.0:
            time_rating = "一般"
        else:
            time_rating = "需要优化"
        
        print(f"  响应时间评级: {time_rating} (平均 {avg_expectation_time:.3f}秒)")
        
        # 基于内存使用的评级
        if 'memory_usage_summary' in self.results:
            memory_increase = self.results['memory_usage_summary']['total_increase_mb']
            
            if memory_increase < 10:
                memory_rating = "优秀"
            elif memory_increase < 50:
                memory_rating = "良好"
            elif memory_increase < 100:
                memory_rating = "一般"
            else:
                memory_rating = "需要优化"
            
            print(f"  内存使用评级: {memory_rating} (增长 {memory_increase:.2f}MB)")
        
        # 并发性能评级
        concurrent_results = [
            self.results.get('concurrent_access_5_threads', {}).get('duration', 0),
            self.results.get('concurrent_access_10_threads', {}).get('duration', 0),
            self.results.get('concurrent_access_20_threads', {}).get('duration', 0)
        ]
        
        max_concurrent_time = max([t for t in concurrent_results if t > 0])
        
        if max_concurrent_time < 2.0:
            concurrent_rating = "优秀"
        elif max_concurrent_time < 5.0:
            concurrent_rating = "良好"
        elif max_concurrent_time < 10.0:
            concurrent_rating = "一般"
        else:
            concurrent_rating = "需要优化"
        
        print(f"  并发性能评级: {concurrent_rating} (最大 {max_concurrent_time:.3f}秒)")
    
    def save_detailed_report(self):
        """保存详细报告到文件"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'performance_benchmark_report_{timestamp}.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'python_version': os.sys.version,
                'platform': os.name
            },
            'test_results': self.results,
            'summary': {
                'total_tests': len(self.results),
                'avg_response_time': statistics.mean([r.get('duration', 0) for r in self.results.values()]),
                'total_memory_usage': sum([r.get('memory_delta', 0) for r in self.results.values()])
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n详细报告已保存到: {filename}")


def run_performance_benchmark():
    """运行性能基准测试的主函数"""
    
    try:
        benchmark = PerformanceBenchmark()
        benchmark.run_benchmark_suite()
        
        print("\n🎉 性能基准测试完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 性能基准测试失败: {str(e)}")
        return False


if __name__ == '__main__':
    success = run_performance_benchmark()
    exit(0 if success else 1)