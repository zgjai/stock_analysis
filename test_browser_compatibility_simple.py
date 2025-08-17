#!/usr/bin/env python3
"""
简化的浏览器兼容性测试脚本
用于验证基本功能
"""

import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

def test_chrome():
    """测试Chrome浏览器"""
    print("🧪 测试Chrome浏览器...")
    
    try:
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        # 测试基本功能
        driver.get("http://localhost:5002/")
        
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        title = driver.title
        print(f"✅ Chrome - 页面标题: {title}")
        
        # 检查页面元素
        nav_elements = driver.find_elements(By.CSS_SELECTOR, "nav, .navbar")
        print(f"✅ Chrome - 导航元素: {len(nav_elements)}个")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Chrome测试失败: {e}")
        return False

def test_firefox():
    """测试Firefox浏览器"""
    print("🧪 测试Firefox浏览器...")
    
    try:
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)
        else:
            driver = webdriver.Firefox(options=firefox_options)
        
        # 测试基本功能
        driver.get("http://localhost:5002/")
        
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        title = driver.title
        print(f"✅ Firefox - 页面标题: {title}")
        
        # 检查页面元素
        nav_elements = driver.find_elements(By.CSS_SELECTOR, "nav, .navbar")
        print(f"✅ Firefox - 导航元素: {len(nav_elements)}个")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Firefox测试失败: {e}")
        return False

def check_server():
    """检查服务器是否运行"""
    try:
        response = requests.get("http://localhost:5002/", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """主函数"""
    print("🌐 简化浏览器兼容性测试")
    print("=" * 40)
    
    # 检查服务器
    if not check_server():
        print("❌ 服务器未运行，请先启动服务器")
        return 1
    
    print("✅ 服务器运行正常")
    
    # 测试浏览器
    chrome_success = test_chrome()
    firefox_success = test_firefox()
    
    # 结果统计
    print("\n📊 测试结果:")
    print(f"Chrome: {'✅ 通过' if chrome_success else '❌ 失败'}")
    print(f"Firefox: {'✅ 通过' if firefox_success else '❌ 失败'}")
    
    if chrome_success or firefox_success:
        print("\n🎉 至少一个浏览器测试通过！")
        return 0
    else:
        print("\n❌ 所有浏览器测试都失败")
        return 1

if __name__ == "__main__":
    exit(main())