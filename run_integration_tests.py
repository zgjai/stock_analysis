#!/usr/bin/env python3
"""
集成测试执行脚本
运行完整的系统集成测试套件
"""
import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path


def setup_test_environment():
    """设置测试环境"""
    print("设置测试环境...")
    
    # 确保测试报告目录存在
    Path('test_reports').mkdir(exist_ok=True)
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'
    
    print("✓ 测试环境设置完成")


def run_test_suite(test_file, description):
    """运行单个测试套件"""
    print(f"\n{'='*60}")
    print(f"运行 {description}")
    print('='*60)
    
    start_time = time.time()
    
    try:
        # 运行pytest
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            f'tests/{test_file}',
            '-v',
            '--tb=short',
            '--color=yes',
            '--durations=10'
        ], capture_output=True, text=True, timeout=600)
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✓ {description} 通过 ({duration:.2f}秒)")
            return True, duration, result.stdout
        else:
            print(f"✗ {description} 失败 ({duration:.2f}秒)")
            print("错误输出:")
            print(result.stderr)
            return False, duration, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"✗ {description} 超时")
        return False, 600, "测试超时"
    except Exception as e:
        print(f"✗ {description} 异常: {e}")
        return False, 0, str(e)


def run_all_integration_tests():
    """运行所有集成测试"""
    print("开始运行股票交易记录系统集成测试")
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 设置测试环境
    setup_test_environment()
    
    # 定义测试套件
    test_suites = [
        ('test_end_to_end_workflows.py', '端到端工作流程测试'),
        ('test_comprehensive_api_integration.py', 'API集成测试'),
        ('test_data_consistency_integrity.py', '数据一致性和完整性测试'),
        ('test_performance_concurrency.py', '性能和并发测试'),
        ('test_comprehensive_integration_runner.py', '综合集成测试')
    ]
    
    # 运行测试套件
    results = []
    total_start_time = time.time()
    
    for test_file, description in test_suites:
        success, duration, output = run_test_suite(test_file, description)
        results.append({
            'test_file': test_file,
            'description': description,
            'success': success,
            'duration': duration,
            'output': output
        })
    
    total_duration = time.time() - total_start_time
    
    # 生成测试报告
    generate_test_report(results, total_duration)
    
    # 打印测试摘要
    print_test_summary(results, total_duration)
    
    # 返回整体测试结果
    return all(result['success'] for result in results)


def generate_test_report(results, total_duration):
    """生成测试报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = Path('test_reports') / f'integration_test_summary_{timestamp}.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("股票交易记录系统 - 集成测试报告\n")
        f.write("="*60 + "\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总耗时: {total_duration:.2f}秒\n\n")
        
        # 测试套件结果
        f.write("测试套件结果:\n")
        f.write("-"*60 + "\n")
        
        for result in results:
            status = "通过" if result['success'] else "失败"
            f.write(f"{result['description']}: {status} ({result['duration']:.2f}秒)\n")
        
        f.write("\n详细输出:\n")
        f.write("="*60 + "\n")
        
        for result in results:
            f.write(f"\n{result['description']}:\n")
            f.write("-"*40 + "\n")
            f.write(result['output'])
            f.write("\n")
    
    print(f"详细测试报告已保存到: {report_file}")


def print_test_summary(results, total_duration):
    """打印测试摘要"""
    print("\n" + "="*60)
    print("集成测试摘要")
    print("="*60)
    
    passed_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)
    success_rate = passed_tests / total_tests if total_tests > 0 else 0
    
    print(f"总测试套件: {total_tests}")
    print(f"通过套件: {passed_tests}")
    print(f"失败套件: {total_tests - passed_tests}")
    print(f"成功率: {success_rate:.1%}")
    print(f"总耗时: {total_duration:.2f}秒")
    
    print("\n各套件详情:")
    print("-"*60)
    
    for result in results:
        status_icon = "✓" if result['success'] else "✗"
        print(f"{status_icon} {result['description']}: {result['duration']:.2f}秒")
    
    print("="*60)
    
    if success_rate == 1.0:
        print("🎉 所有集成测试通过！系统集成验证成功。")
    elif success_rate >= 0.8:
        print("⚠️  大部分集成测试通过，但有部分测试失败，请检查失败的测试。")
    else:
        print("❌ 多个集成测试失败，系统可能存在严重问题，请仔细检查。")


def run_quick_health_check():
    """运行快速健康检查"""
    print("运行快速系统健康检查...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/test_comprehensive_integration_runner.py::TestComprehensiveIntegrationRunner::test_system_health_check',
            '-v'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✓ 系统健康检查通过")
            return True
        else:
            print("✗ 系统健康检查失败")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ 健康检查异常: {e}")
        return False


def main():
    """主函数"""
    print("股票交易记录系统 - 集成测试执行器")
    print("="*60)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 检查必要的包
    try:
        import pytest
        import flask
        import sqlalchemy
    except ImportError as e:
        print(f"错误: 缺少必要的包 - {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--health-check':
            success = run_quick_health_check()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--help':
            print("用法:")
            print("  python run_integration_tests.py           # 运行完整集成测试")
            print("  python run_integration_tests.py --health-check  # 快速健康检查")
            print("  python run_integration_tests.py --help          # 显示帮助")
            sys.exit(0)
    
    # 运行完整集成测试
    try:
        success = run_all_integration_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"测试执行异常: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()