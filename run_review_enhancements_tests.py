#!/usr/bin/env python3
"""
复盘功能增强测试执行脚本
运行所有相关的集成测试和端到端测试
"""
import sys
import os
import subprocess
from pathlib import Path


def setup_test_environment():
    """设置测试环境"""
    print("设置测试环境...")
    
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 检查必要的依赖
    try:
        import pytest
        print("✅ pytest 已安装")
    except ImportError:
        print("❌ pytest 未安装，请运行: pip install pytest")
        return False
    
    try:
        import flask
        print("✅ Flask 已安装")
    except ImportError:
        print("❌ Flask 未安装，请运行: pip install flask")
        return False
    
    # 检查测试文件是否存在
    test_files = [
        'tests/test_review_enhancements_integration.py',
        'tests/test_review_enhancements_e2e.py',
        'tests/test_review_enhancements_runner.py'
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✅ {test_file} 存在")
        else:
            print(f"❌ {test_file} 不存在")
            return False
    
    return True


def run_individual_tests():
    """运行单独的测试文件"""
    print("\n" + "=" * 60)
    print("运行单独的测试文件")
    print("=" * 60)
    
    test_commands = [
        {
            'name': '持仓天数编辑集成测试',
            'command': [
                sys.executable, '-m', 'pytest',
                'tests/test_review_enhancements_integration.py::TestHoldingDaysEditingIntegration',
                '-v', '--tb=short'
            ]
        },
        {
            'name': '复盘保存集成测试',
            'command': [
                sys.executable, '-m', 'pytest',
                'tests/test_review_enhancements_integration.py::TestReviewSaveIntegration',
                '-v', '--tb=short'
            ]
        },
        {
            'name': '浮盈计算集成测试',
            'command': [
                sys.executable, '-m', 'pytest',
                'tests/test_review_enhancements_integration.py::TestFloatingProfitCalculationIntegration',
                '-v', '--tb=short'
            ]
        },
        {
            'name': '错误处理和边界条件测试',
            'command': [
                sys.executable, '-m', 'pytest',
                'tests/test_review_enhancements_integration.py::TestErrorHandlingAndBoundaryConditions',
                '-v', '--tb=short'
            ]
        },
        {
            'name': '数据一致性和完整性测试',
            'command': [
                sys.executable, '-m', 'pytest',
                'tests/test_review_enhancements_integration.py::TestDataConsistencyAndIntegrity',
                '-v', '--tb=short'
            ]
        },
        {
            'name': '端到端测试',
            'command': [
                sys.executable, '-m', 'pytest',
                'tests/test_review_enhancements_e2e.py',
                '-v', '--tb=short'
            ]
        }
    ]
    
    results = []
    
    for test_info in test_commands:
        print(f"\n运行: {test_info['name']}")
        print("-" * 40)
        
        try:
            result = subprocess.run(
                test_info['command'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            results.append({
                'name': test_info['name'],
                'success': success,
                'stdout': result.stdout,
                'stderr': result.stderr
            })
            
            if success:
                print(f"✅ {test_info['name']} - 通过")
            else:
                print(f"❌ {test_info['name']} - 失败")
                if result.stderr:
                    print(f"错误信息: {result.stderr[:200]}...")
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_info['name']} - 超时")
            results.append({
                'name': test_info['name'],
                'success': False,
                'stdout': '',
                'stderr': 'Test timeout'
            })
        except Exception as e:
            print(f"💥 {test_info['name']} - 异常: {e}")
            results.append({
                'name': test_info['name'],
                'success': False,
                'stdout': '',
                'stderr': str(e)
            })
    
    return results


def run_comprehensive_tests():
    """运行综合测试"""
    print("\n" + "=" * 60)
    print("运行综合测试")
    print("=" * 60)
    
    try:
        # 运行所有复盘增强相关测试
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/test_review_enhancements_integration.py',
            'tests/test_review_enhancements_e2e.py',
            '-v',
            '--tb=short',
            '--maxfail=5'  # 最多失败5个就停止
        ]
        
        print("执行命令:", ' '.join(cmd))
        result = subprocess.run(cmd, timeout=600)  # 10分钟超时
        
        if result.returncode == 0:
            print("✅ 所有测试通过")
            return True
        else:
            print("❌ 部分测试失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ 综合测试超时")
        return False
    except Exception as e:
        print(f"💥 运行综合测试时发生异常: {e}")
        return False


def generate_summary_report(individual_results, comprehensive_success):
    """生成总结报告"""
    print("\n" + "=" * 80)
    print("测试总结报告")
    print("=" * 80)
    
    # 统计个别测试结果
    total_tests = len(individual_results)
    passed_tests = sum(1 for r in individual_results if r['success'])
    failed_tests = total_tests - passed_tests
    
    print(f"\n📊 个别测试统计:")
    print(f"  总测试套件数: {total_tests}")
    print(f"  通过: {passed_tests} ✅")
    print(f"  失败: {failed_tests} ❌")
    print(f"  成功率: {(passed_tests/total_tests*100):.1f}%")
    
    print(f"\n📋 详细结果:")
    for result in individual_results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['name']}")
        if not result['success'] and result['stderr']:
            print(f"    错误: {result['stderr'][:100]}...")
    
    print(f"\n🎯 综合测试: {'✅ 通过' if comprehensive_success else '❌ 失败'}")
    
    # 总体评估
    print(f"\n💡 总体评估:")
    if passed_tests == total_tests and comprehensive_success:
        print("  🎉 所有测试都通过了！复盘功能增强实现质量优秀。")
    elif passed_tests >= total_tests * 0.8:
        print("  👍 大部分测试通过，功能基本正常，建议修复失败的测试。")
    else:
        print("  ⚠️  多个测试失败，需要重点检查和修复问题。")
    
    # 功能覆盖评估
    print(f"\n🎯 功能覆盖评估:")
    feature_coverage = {
        '持仓天数编辑': any('持仓天数' in r['name'] for r in individual_results if r['success']),
        '复盘保存': any('复盘保存' in r['name'] for r in individual_results if r['success']),
        '浮盈计算': any('浮盈计算' in r['name'] for r in individual_results if r['success']),
        '错误处理': any('错误处理' in r['name'] for r in individual_results if r['success']),
        '数据一致性': any('数据一致性' in r['name'] for r in individual_results if r['success']),
        '端到端流程': any('端到端' in r['name'] for r in individual_results if r['success'])
    }
    
    for feature, covered in feature_coverage.items():
        status = "✅ 已覆盖" if covered else "❌ 未覆盖"
        print(f"  {feature}: {status}")
    
    return passed_tests == total_tests and comprehensive_success


def main():
    """主函数"""
    print("复盘功能增强 - 集成测试和端到端测试")
    print("=" * 80)
    
    # 设置测试环境
    if not setup_test_environment():
        print("❌ 测试环境设置失败")
        return 1
    
    # 运行单独测试
    individual_results = run_individual_tests()
    
    # 运行综合测试
    comprehensive_success = run_comprehensive_tests()
    
    # 生成总结报告
    overall_success = generate_summary_report(individual_results, comprehensive_success)
    
    # 返回适当的退出码
    return 0 if overall_success else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)