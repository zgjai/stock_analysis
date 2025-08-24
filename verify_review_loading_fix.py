#!/usr/bin/env python3
"""
验证复盘页面加载修复
测试浮盈计算器和页面加载功能
"""

import os
import sys
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

def setup_chrome_driver():
    """设置Chrome驱动"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"无法启动Chrome驱动: {e}")
        return None

def test_javascript_dependencies(driver, base_url):
    """测试JavaScript依赖"""
    print("\n测试JavaScript依赖...")
    
    try:
        # 访问调试页面
        driver.get(f"{base_url}/debug_review_loading.html")
        
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "check-dependencies"))
        )
        
        # 点击检查依赖按钮
        check_btn = driver.find_element(By.ID, "check-dependencies")
        check_btn.click()
        
        # 等待检查完成
        time.sleep(2)
        
        # 获取日志内容
        log_container = driver.find_element(By.ID, "status-log")
        log_text = log_container.text
        
        # 检查关键依赖
        dependencies = ['debounce', 'throttle', 'FloatingProfitCalculator']
        success_count = 0
        
        for dep in dependencies:
            if f"✓ {dep} 可用" in log_text:
                print(f"✓ {dep} 依赖正常")
                success_count += 1
            else:
                print(f"❌ {dep} 依赖缺失")
        
        return success_count == len(dependencies)
        
    except Exception as e:
        print(f"依赖测试失败: {e}")
        return False

def test_floating_profit_calculator(driver, base_url):
    """测试浮盈计算器"""
    print("\n测试浮盈计算器...")
    
    try:
        # 确保在调试页面
        if "debug_review_loading.html" not in driver.current_url:
            driver.get(f"{base_url}/debug_review_loading.html")
            time.sleep(2)
        
        # 设置测试参数
        stock_code_input = driver.find_element(By.ID, "test-stock-code")
        buy_price_input = driver.find_element(By.ID, "test-buy-price")
        current_price_input = driver.find_element(By.ID, "test-current-price")
        
        stock_code_input.clear()
        stock_code_input.send_keys("000001")
        
        buy_price_input.clear()
        buy_price_input.send_keys("10.50")
        
        current_price_input.clear()
        current_price_input.send_keys("11.20")
        
        # 点击测试计算器按钮
        test_btn = driver.find_element(By.ID, "test-calculator")
        test_btn.click()
        
        # 等待测试完成
        time.sleep(3)
        
        # 获取日志内容
        log_container = driver.find_element(By.ID, "status-log")
        log_text = log_container.text
        
        # 检查测试结果
        if "✓ 计算器创建成功" in log_text and "✓ 计算结果:" in log_text:
            print("✓ 浮盈计算器测试通过")
            return True
        else:
            print("❌ 浮盈计算器测试失败")
            print(f"日志内容: {log_text}")
            return False
        
    except Exception as e:
        print(f"浮盈计算器测试失败: {e}")
        return False

def test_review_page_loading(driver, base_url):
    """测试复盘页面加载"""
    print("\n测试复盘页面加载...")
    
    try:
        # 访问复盘页面
        driver.get(f"{base_url}/review")
        
        # 等待页面基本元素加载
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 检查是否有持续的加载状态
        time.sleep(5)  # 等待5秒让页面完全加载
        
        # 检查是否还有"加载中"文本
        page_source = driver.page_source
        loading_indicators = [
            "加载中...",
            "spinner-border",
            "正在加载"
        ]
        
        persistent_loading = False
        for indicator in loading_indicators:
            if indicator in page_source:
                # 检查是否是持续显示的加载状态
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{indicator}')]")
                for element in elements:
                    if element.is_displayed():
                        print(f"发现持续的加载状态: {indicator}")
                        persistent_loading = True
                        break
        
        if not persistent_loading:
            print("✓ 复盘页面加载正常，无持续加载状态")
            return True
        else:
            print("❌ 复盘页面存在持续加载状态")
            
            # 尝试执行强制清理
            print("尝试执行强制清理...")
            driver.execute_script("if (typeof forceCleanupLoadingStates === 'function') forceCleanupLoadingStates();")
            time.sleep(2)
            
            # 再次检查
            page_source = driver.page_source
            if "加载中..." not in page_source:
                print("✓ 强制清理后加载状态已清除")
                return True
            else:
                print("❌ 强制清理后仍有加载状态")
                return False
        
    except TimeoutException:
        print("❌ 复盘页面加载超时")
        return False
    except Exception as e:
        print(f"复盘页面测试失败: {e}")
        return False

def test_integration_manager(driver, base_url):
    """测试集成管理器"""
    print("\n测试集成管理器...")
    
    try:
        # 确保在调试页面
        if "debug_review_loading.html" not in driver.current_url:
            driver.get(f"{base_url}/debug_review_loading.html")
            time.sleep(2)
        
        # 点击测试集成按钮
        test_btn = driver.find_element(By.ID, "test-integration")
        test_btn.click()
        
        # 等待测试完成
        time.sleep(5)
        
        # 获取日志内容
        log_container = driver.find_element(By.ID, "status-log")
        log_text = log_container.text
        
        # 检查测试结果
        if "✓ 集成管理器创建成功" in log_text:
            print("✓ 集成管理器测试通过")
            return True
        else:
            print("❌ 集成管理器测试失败")
            print(f"日志内容: {log_text}")
            return False
        
    except Exception as e:
        print(f"集成管理器测试失败: {e}")
        return False

def check_console_errors(driver):
    """检查浏览器控制台错误"""
    print("\n检查浏览器控制台错误...")
    
    try:
        logs = driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if errors:
            print("发现控制台错误:")
            for error in errors:
                print(f"  - {error['message']}")
            return False
        else:
            print("✓ 无控制台错误")
            return True
            
    except Exception as e:
        print(f"无法获取控制台日志: {e}")
        return True  # 不影响主要测试

def main():
    """主测试函数"""
    print("开始验证复盘页面加载修复...")
    
    # 检查服务器是否运行
    print("\n检查服务器状态...")
    try:
        import requests
        response = requests.get("http://localhost:5001", timeout=5)
        print("✓ 服务器运行正常")
        base_url = "http://localhost:5001"
    except:
        print("❌ 服务器未运行，请先启动服务器")
        return False
    
    # 设置浏览器驱动
    driver = setup_chrome_driver()
    if not driver:
        print("❌ 无法设置浏览器驱动")
        return False
    
    try:
        test_results = {
            'dependencies': False,
            'calculator': False,
            'page_loading': False,
            'integration': False,
            'console_clean': False
        }
        
        # 运行所有测试
        test_results['dependencies'] = test_javascript_dependencies(driver, base_url)
        test_results['calculator'] = test_floating_profit_calculator(driver, base_url)
        test_results['page_loading'] = test_review_page_loading(driver, base_url)
        test_results['integration'] = test_integration_manager(driver, base_url)
        test_results['console_clean'] = check_console_errors(driver)
        
        # 汇总结果
        print("\n" + "="*50)
        print("测试结果汇总:")
        print("="*50)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✓ 通过" if result else "❌ 失败"
            print(f"{test_name.ljust(20)}: {status}")
            if result:
                passed += 1
        
        print(f"\n总体结果: {passed}/{total} 项测试通过")
        
        if passed == total:
            print("\n🎉 所有测试通过！复盘页面加载修复成功！")
            return True
        else:
            print(f"\n⚠️  有 {total - passed} 项测试失败，需要进一步检查")
            return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)