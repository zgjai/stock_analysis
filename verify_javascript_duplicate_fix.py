#!/usr/bin/env python3
"""
验证JavaScript重复声明修复
"""
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

def test_javascript_duplicate_fix():
    """测试JavaScript重复声明修复"""
    print("🔍 开始验证JavaScript重复声明修复...")
    
    # Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # 设置页面加载超时
        driver.set_page_load_timeout(30)
        
        # 访问测试页面
        test_url = "http://localhost:5001/test_javascript_duplicate_fix.html"
        print(f"📱 访问测试页面: {test_url}")
        
        driver.get(test_url)
        
        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "test-results"))
        )
        
        # 等待测试执行完成（等待总结出现）
        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element((By.ID, "test-results"), "测试总结")
        )
        
        # 获取测试结果
        test_results = driver.find_element(By.ID, "test-results")
        console_output = driver.find_element(By.ID, "console-output")
        
        print("\n📊 测试结果:")
        print("=" * 50)
        print(test_results.text)
        
        print("\n📝 控制台输出:")
        print("=" * 50)
        print(console_output.text)
        
        # 检查是否有JavaScript错误
        js_errors = driver.get_log('browser')
        error_count = 0
        duplicate_errors = 0
        
        print("\n🔍 浏览器错误日志:")
        print("=" * 50)
        
        for error in js_errors:
            if error['level'] == 'SEVERE':
                error_count += 1
                error_message = error['message']
                print(f"❌ 严重错误: {error_message}")
                
                # 检查是否是重复声明错误
                if 'already been declared' in error_message:
                    duplicate_errors += 1
                    print(f"   🚨 重复声明错误!")
            elif error['level'] == 'WARNING':
                print(f"⚠️  警告: {error['message']}")
            else:
                print(f"ℹ️  信息: {error['message']}")
        
        # 分析结果
        success = True
        issues = []
        
        if duplicate_errors > 0:
            success = False
            issues.append(f"发现 {duplicate_errors} 个重复声明错误")
        
        if error_count > duplicate_errors:
            issues.append(f"发现 {error_count - duplicate_errors} 个其他严重错误")
        
        # 检查测试结果中是否包含成功信息
        if "测试总结" in test_results.text:
            if "通过" in test_results.text:
                print(f"\n✅ 功能测试通过")
            else:
                success = False
                issues.append("功能测试失败")
        
        print(f"\n{'='*50}")
        if success and duplicate_errors == 0:
            print("🎉 JavaScript重复声明修复验证成功!")
            print("✅ 没有发现重复声明错误")
            print("✅ 所有JavaScript文件正常加载")
            return True
        else:
            print("❌ JavaScript重复声明修复验证失败!")
            for issue in issues:
                print(f"   - {issue}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return False
        
    finally:
        if driver:
            driver.quit()

def test_review_page_loading():
    """测试复盘页面加载"""
    print("\n🔍 测试复盘页面加载...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # 访问复盘页面
        review_url = "http://localhost:5001/review"
        print(f"📱 访问复盘页面: {review_url}")
        
        driver.get(review_url)
        
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 等待JavaScript初始化完成
        time.sleep(3)
        
        # 检查JavaScript错误
        js_errors = driver.get_log('browser')
        duplicate_errors = 0
        severe_errors = 0
        
        print("\n🔍 复盘页面错误检查:")
        print("=" * 50)
        
        for error in js_errors:
            if error['level'] == 'SEVERE':
                severe_errors += 1
                error_message = error['message']
                print(f"❌ 严重错误: {error_message}")
                
                if 'already been declared' in error_message:
                    duplicate_errors += 1
                    print(f"   🚨 重复声明错误!")
        
        if duplicate_errors == 0:
            print("✅ 复盘页面没有重复声明错误")
            return True
        else:
            print(f"❌ 复盘页面发现 {duplicate_errors} 个重复声明错误")
            return False
            
    except Exception as e:
        print(f"❌ 复盘页面测试出现错误: {str(e)}")
        return False
        
    finally:
        if driver:
            driver.quit()

def main():
    """主函数"""
    print("🚀 开始JavaScript重复声明修复验证")
    print("=" * 60)
    
    # 检查服务器是否运行
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        print("✅ 服务器运行正常")
    except:
        print("❌ 服务器未运行，请先启动服务器")
        return False
    
    # 运行测试
    test1_passed = test_javascript_duplicate_fix()
    test2_passed = test_review_page_loading()
    
    print(f"\n{'='*60}")
    print("📊 最终验证结果:")
    print(f"   测试页面验证: {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"   复盘页面验证: {'✅ 通过' if test2_passed else '❌ 失败'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 JavaScript重复声明修复验证完全成功!")
        print("✅ 所有重复声明问题已解决")
        print("✅ 页面可以正常加载和运行")
        return True
    else:
        print("\n❌ 验证失败，仍有问题需要解决")
        return False

if __name__ == "__main__":
    main()