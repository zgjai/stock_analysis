#!/usr/bin/env python3
"""
快速测试复盘页面修复效果
"""

import requests
import sys
import time

def test_server_response():
    """测试服务器响应"""
    print("测试服务器连接...")
    try:
        response = requests.get("http://localhost:5001", timeout=10)
        if response.status_code == 200:
            print("✓ 服务器连接正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接服务器: {e}")
        return False

def test_review_page():
    """测试复盘页面"""
    print("测试复盘页面...")
    try:
        response = requests.get("http://localhost:5001/review", timeout=15)
        if response.status_code == 200:
            content = response.text
            
            # 检查关键JavaScript文件是否被引用
            js_files = [
                'utils.js',
                'floating-profit-calculator.js', 
                'review-integration.js',
                'loading-cleanup.js'
            ]
            
            missing_files = []
            for js_file in js_files:
                if js_file not in content:
                    missing_files.append(js_file)
            
            if missing_files:
                print(f"❌ 缺少JavaScript文件引用: {missing_files}")
                return False
            else:
                print("✓ 所有必要的JavaScript文件都已引用")
                return True
        else:
            print(f"❌ 复盘页面响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法访问复盘页面: {e}")
        return False

def test_static_files():
    """测试静态文件"""
    print("测试关键静态文件...")
    
    files_to_test = [
        '/static/js/utils.js',
        '/static/js/floating-profit-calculator.js',
        '/static/js/review-integration.js',
        '/static/js/loading-cleanup.js'
    ]
    
    all_good = True
    for file_path in files_to_test:
        try:
            response = requests.get(f"http://localhost:5001{file_path}", timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # 检查文件内容
                if file_path.endswith('utils.js'):
                    if 'debounce' in content and 'throttle' in content:
                        print(f"✓ {file_path} - 包含debounce和throttle函数")
                    else:
                        print(f"❌ {file_path} - 缺少debounce或throttle函数")
                        all_good = False
                
                elif file_path.endswith('floating-profit-calculator.js'):
                    if 'this.calculateProfit.bind(this)' not in content:
                        print(f"✓ {file_path} - 已修复绑定错误")
                    else:
                        print(f"❌ {file_path} - 仍存在绑定错误")
                        all_good = False
                
                elif file_path.endswith('loading-cleanup.js'):
                    if 'forceCleanupLoadingStates' in content:
                        print(f"✓ {file_path} - 包含清理函数")
                    else:
                        print(f"❌ {file_path} - 缺少清理函数")
                        all_good = False
                
                else:
                    print(f"✓ {file_path} - 文件可访问")
            else:
                print(f"❌ {file_path} - 响应异常: {response.status_code}")
                all_good = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {file_path} - 无法访问: {e}")
            all_good = False
    
    return all_good

def test_test_pages():
    """测试调试页面"""
    print("测试调试页面...")
    
    test_pages = [
        '/test_review_fix_simple.html',
        '/debug_review_loading.html'
    ]
    
    all_good = True
    for page in test_pages:
        try:
            response = requests.get(f"http://localhost:5001{page}", timeout=10)
            if response.status_code == 200:
                print(f"✓ {page} - 可访问")
            else:
                print(f"❌ {page} - 响应异常: {response.status_code}")
                all_good = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {page} - 无法访问: {e}")
            all_good = False
    
    return all_good

def main():
    """主测试函数"""
    print("=" * 50)
    print("复盘页面修复快速验证")
    print("=" * 50)
    
    tests = [
        ("服务器连接", test_server_response),
        ("复盘页面", test_review_page),
        ("静态文件", test_static_files),
        ("调试页面", test_test_pages)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}测试:")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"✓ {test_name}测试通过")
        else:
            print(f"❌ {test_name}测试失败")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 所有测试通过！修复成功！")
        print("\n下一步:")
        print("1. 访问 http://localhost:5001/review 查看复盘页面")
        print("2. 访问 http://localhost:5001/test_review_fix_simple.html 进行详细测试")
        print("3. 如果页面卡在加载中，在浏览器控制台执行: forceCleanupLoadingStates()")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        print("\n建议:")
        print("1. 检查服务器是否正常运行在端口5001")
        print("2. 确认所有修复的文件都已保存")
        print("3. 重启服务器后重新测试")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)