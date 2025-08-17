#!/usr/bin/env python3
"""
验证集成测试设置
"""
import sys
import os
from pathlib import Path

def verify_test_files():
    """验证测试文件是否存在"""
    test_files = [
        'tests/test_end_to_end_workflows.py',
        'tests/test_comprehensive_api_integration.py',
        'tests/test_data_consistency_integrity.py',
        'tests/test_performance_concurrency.py',
        'tests/test_comprehensive_integration_runner.py'
    ]
    
    print("验证测试文件...")
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✓ {test_file}")
        else:
            print(f"✗ {test_file} - 文件不存在")
            return False
    
    return True

def verify_dependencies():
    """验证依赖包"""
    required_packages = [
        'pytest',
        'flask',
        'sqlalchemy'
    ]
    
    print("\n验证依赖包...")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - 包未安装")
            return False
    
    return True

def verify_project_structure():
    """验证项目结构"""
    required_dirs = [
        'tests',
        'models',
        'api',
        'services'
    ]
    
    print("\n验证项目结构...")
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/ - 目录不存在")
            return False
    
    return True

def verify_test_configuration():
    """验证测试配置"""
    config_files = [
        'tests/conftest.py',
        'pytest_integration.ini',
        'run_integration_tests.py'
    ]
    
    print("\n验证测试配置...")
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✓ {config_file}")
        else:
            print(f"✗ {config_file} - 配置文件不存在")
            return False
    
    return True

def main():
    """主函数"""
    print("股票交易记录系统 - 集成测试验证")
    print("="*50)
    
    all_checks_passed = True
    
    # 验证各个组件
    checks = [
        verify_project_structure,
        verify_dependencies,
        verify_test_files,
        verify_test_configuration
    ]
    
    for check in checks:
        if not check():
            all_checks_passed = False
    
    print("\n" + "="*50)
    if all_checks_passed:
        print("✅ 所有验证通过！集成测试环境设置正确。")
        print("\n可以运行以下命令开始测试：")
        print("  python run_integration_tests.py --health-check")
        print("  python run_integration_tests.py")
        return 0
    else:
        print("❌ 验证失败！请检查上述问题后重试。")
        return 1

if __name__ == '__main__':
    sys.exit(main())