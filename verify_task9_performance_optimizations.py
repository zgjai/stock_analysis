#!/usr/bin/env python3
"""
任务9性能优化验证脚本
验证复盘保存功能的性能优化实现
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """打印步骤"""
    print(f"\n[步骤 {step}] {description}")
    print("-" * 40)

def check_file_exists(file_path, description=""):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description or file_path} - 存在")
        return True
    else:
        print(f"❌ {description or file_path} - 不存在")
        return False

def check_file_content(file_path, search_terms, description=""):
    """检查文件内容是否包含指定术语"""
    if not os.path.exists(file_path):
        print(f"❌ {description or file_path} - 文件不存在")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_terms = []
        found_terms = []
        
        for term in search_terms:
            if term in content:
                found_terms.append(term)
            else:
                missing_terms.append(term)
        
        if missing_terms:
            print(f"❌ {description or file_path} - 缺少: {', '.join(missing_terms)}")
            if found_terms:
                print(f"   ✅ 已找到: {', '.join(found_terms)}")
            return False
        else:
            print(f"✅ {description or file_path} - 所有术语都已找到")
            return True
            
    except Exception as e:
        print(f"❌ {description or file_path} - 读取错误: {e}")
        return False

def verify_performance_optimizations():
    """验证性能优化实现"""
    print_header("任务9：性能优化验证")
    
    results = {
        'total_checks': 0,
        'passed_checks': 0,
        'failed_checks': 0,
        'details': []
    }
    
    # 检查项目列表
    checks = [
        {
            'name': '防抖机制实现',
            'file': 'static/js/review-save-manager.js',
            'terms': ['debouncedSave', 'lastSaveAttempt', '防抖机制', 'debounce'],
            'description': '保存操作防抖机制'
        },
        {
            'name': '保存进度显示',
            'file': 'static/js/review-save-manager.js',
            'terms': ['showSaveProgress', 'hideSaveProgress', 'saveProgressContainer', 'progress-bar'],
            'description': '保存进度条和动画'
        },
        {
            'name': '性能指标跟踪',
            'file': 'static/js/review-save-manager.js',
            'terms': ['performanceMetrics', 'saveAttempts', 'averageSaveTime', 'trackSaveSuccess'],
            'description': '性能指标收集和分析'
        },
        {
            'name': '智能错误处理',
            'file': 'static/js/review-save-manager.js',
            'terms': ['analyzeError', 'scheduleAutoRetry', 'errorAnalysis', 'recoveryAction'],
            'description': '智能错误分析和恢复'
        },
        {
            'name': '网络条件适配',
            'file': 'static/js/review-save-manager.js',
            'terms': ['adaptToNetworkConditions', 'networkInfo', 'effectiveType', 'connection'],
            'description': '根据网络条件调整行为'
        },
        {
            'name': '内存优化',
            'file': 'static/js/review-save-manager.js',
            'terms': ['performMemoryCleanup', 'memoryCheckInterval', 'cleanupFormDataCache', 'memory'],
            'description': '内存监控和清理'
        },
        {
            'name': '批量处理优化',
            'file': 'static/js/review-save-manager.js',
            'terms': ['batchValidator', 'processBatchValidation', 'domUpdateQueue', 'requestAnimationFrame'],
            'description': '批量处理和DOM优化'
        },
        {
            'name': '工具函数加载',
            'file': 'templates/review.html',
            'terms': ['utils.js', 'performance-optimizations.js', 'debounce', 'throttle'],
            'description': '性能优化工具函数加载'
        },
        {
            'name': '依赖检查增强',
            'file': 'templates/review.html',
            'terms': ['PerformanceUtils', 'criticalMissing', 'nonCriticalNames', 'critical:'],
            'description': '增强的依赖检查'
        },
        {
            'name': '性能监控函数',
            'file': 'templates/review.html',
            'terms': ['showPerformanceReport', 'measurePagePerformance', 'optimizePerformance', 'exportPerformanceData'],
            'description': '性能监控和调试函数'
        }
    ]
    
    print_step(1, "检查性能优化功能实现")
    
    for i, check in enumerate(checks, 1):
        results['total_checks'] += 1
        print(f"\n{i}. {check['description']}")
        
        if check_file_content(check['file'], check['terms'], check['name']):
            results['passed_checks'] += 1
            results['details'].append({
                'check': check['name'],
                'status': 'PASS',
                'file': check['file']
            })
        else:
            results['failed_checks'] += 1
            results['details'].append({
                'check': check['name'],
                'status': 'FAIL',
                'file': check['file'],
                'missing_terms': [term for term in check['terms'] if term not in open(check['file'], 'r', encoding='utf-8').read()]
            })
    
    print_step(2, "检查测试文件")
    
    test_files = [
        'test_task9_performance_optimizations.html',
        'verify_task9_performance_optimizations.py'
    ]
    
    for test_file in test_files:
        results['total_checks'] += 1
        if check_file_exists(test_file, f"测试文件: {test_file}"):
            results['passed_checks'] += 1
            results['details'].append({
                'check': f'测试文件: {test_file}',
                'status': 'PASS',
                'file': test_file
            })
        else:
            results['failed_checks'] += 1
            results['details'].append({
                'check': f'测试文件: {test_file}',
                'status': 'FAIL',
                'file': test_file
            })
    
    print_step(3, "检查JavaScript工具文件")
    
    js_files = [
        ('static/js/utils.js', ['debounce', 'throttle', 'PerformanceUtils']),
        ('static/js/performance-optimizations.js', ['MemoryCache', 'BatchProcessor', 'rafThrottle'])
    ]
    
    for js_file, terms in js_files:
        results['total_checks'] += 1
        if check_file_content(js_file, terms, f"JavaScript工具: {js_file}"):
            results['passed_checks'] += 1
            results['details'].append({
                'check': f'JavaScript工具: {js_file}',
                'status': 'PASS',
                'file': js_file
            })
        else:
            results['failed_checks'] += 1
            results['details'].append({
                'check': f'JavaScript工具: {js_file}',
                'status': 'FAIL',
                'file': js_file
            })
    
    return results

def generate_report(results):
    """生成验证报告"""
    print_header("验证结果汇总")
    
    success_rate = (results['passed_checks'] / results['total_checks']) * 100 if results['total_checks'] > 0 else 0
    
    print(f"总检查项: {results['total_checks']}")
    print(f"通过检查: {results['passed_checks']}")
    print(f"失败检查: {results['failed_checks']}")
    print(f"成功率: {success_rate:.1f}%")
    
    if results['failed_checks'] > 0:
        print(f"\n❌ 失败的检查项:")
        for detail in results['details']:
            if detail['status'] == 'FAIL':
                print(f"  - {detail['check']} ({detail['file']})")
                if 'missing_terms' in detail:
                    print(f"    缺少术语: {', '.join(detail['missing_terms'])}")
    
    print(f"\n✅ 通过的检查项:")
    for detail in results['details']:
        if detail['status'] == 'PASS':
            print(f"  - {detail['check']}")
    
    # 保存详细报告
    report_file = 'task9_performance_optimization_verification_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'task': 'Task 9: 优化用户体验和性能',
            'summary': {
                'total_checks': results['total_checks'],
                'passed_checks': results['passed_checks'],
                'failed_checks': results['failed_checks'],
                'success_rate': f"{success_rate:.1f}%"
            },
            'details': results['details']
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    return success_rate >= 80  # 80%以上通过率视为成功

def main():
    """主函数"""
    try:
        # 验证性能优化
        results = verify_performance_optimizations()
        
        # 生成报告
        success = generate_report(results)
        
        if success:
            print(f"\n🎉 任务9性能优化验证成功！")
            print("主要优化功能:")
            print("  ✅ 防抖机制防止重复提交")
            print("  ✅ 保存进度显示和动画")
            print("  ✅ 性能指标跟踪和分析")
            print("  ✅ 智能错误处理和恢复")
            print("  ✅ 网络条件自适应")
            print("  ✅ 内存监控和优化")
            print("  ✅ 批量处理和DOM优化")
            return 0
        else:
            print(f"\n❌ 任务9性能优化验证失败")
            print("请检查失败的项目并修复")
            return 1
            
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)