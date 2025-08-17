#!/usr/bin/env python3
"""
WebDriver设置脚本
用于检查和安装浏览器驱动程序
"""

import os
import sys
import subprocess
import platform
import requests
import zipfile
import tarfile
from pathlib import Path

class WebDriverSetup:
    def __init__(self):
        self.system = platform.system().lower()
        self.drivers_dir = Path("drivers")
        self.drivers_dir.mkdir(exist_ok=True)
        
    def check_chrome_installed(self):
        """检查Chrome是否已安装"""
        try:
            if self.system == "windows":
                result = subprocess.run(["where", "chrome"], capture_output=True, text=True)
                return result.returncode == 0
            else:
                result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True)
                if result.returncode != 0:
                    result = subprocess.run(["which", "chromium"], capture_output=True, text=True)
                return result.returncode == 0
        except:
            return False
    
    def check_firefox_installed(self):
        """检查Firefox是否已安装"""
        try:
            if self.system == "windows":
                result = subprocess.run(["where", "firefox"], capture_output=True, text=True)
            else:
                result = subprocess.run(["which", "firefox"], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def install_chromedriver_via_webdriver_manager(self):
        """使用webdriver-manager安装ChromeDriver"""
        try:
            print("📦 安装webdriver-manager...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
            
            print("🔧 设置ChromeDriver...")
            # 创建测试脚本来初始化ChromeDriver
            test_script = '''
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

try:
    service = Service(ChromeDriverManager().install())
    print("✅ ChromeDriver安装成功")
except Exception as e:
    print(f"❌ ChromeDriver安装失败: {e}")
'''
            with open("temp_chrome_setup.py", "w") as f:
                f.write(test_script)
            
            result = subprocess.run([sys.executable, "temp_chrome_setup.py"], 
                                  capture_output=True, text=True)
            os.remove("temp_chrome_setup.py")
            
            if "ChromeDriver安装成功" in result.stdout:
                print("✅ ChromeDriver设置完成")
                return True
            else:
                print(f"❌ ChromeDriver设置失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ ChromeDriver安装失败: {e}")
            return False
    
    def install_geckodriver_via_webdriver_manager(self):
        """使用webdriver-manager安装GeckoDriver"""
        try:
            print("🔧 设置GeckoDriver...")
            # 创建测试脚本来初始化GeckoDriver
            test_script = '''
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service

try:
    service = Service(GeckoDriverManager().install())
    print("✅ GeckoDriver安装成功")
except Exception as e:
    print(f"❌ GeckoDriver安装失败: {e}")
'''
            with open("temp_gecko_setup.py", "w") as f:
                f.write(test_script)
            
            result = subprocess.run([sys.executable, "temp_gecko_setup.py"], 
                                  capture_output=True, text=True)
            os.remove("temp_gecko_setup.py")
            
            if "GeckoDriver安装成功" in result.stdout:
                print("✅ GeckoDriver设置完成")
                return True
            else:
                print(f"❌ GeckoDriver设置失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ GeckoDriver安装失败: {e}")
            return False
    
    def test_webdrivers(self):
        """测试WebDriver是否正常工作"""
        print("\n🧪 测试WebDriver...")
        
        # 测试Chrome
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=options)
            driver.get("https://www.google.com")
            driver.quit()
            print("✅ Chrome WebDriver测试成功")
            
        except Exception as e:
            print(f"❌ Chrome WebDriver测试失败: {e}")
        
        # 测试Firefox
        try:
            from selenium import webdriver
            from selenium.webdriver.firefox.options import Options
            
            options = Options()
            options.add_argument("--headless")
            
            driver = webdriver.Firefox(options=options)
            driver.get("https://www.google.com")
            driver.quit()
            print("✅ Firefox WebDriver测试成功")
            
        except Exception as e:
            print(f"❌ Firefox WebDriver测试失败: {e}")
    
    def setup_all(self):
        """设置所有WebDriver"""
        print("🚀 开始设置WebDriver...")
        print("=" * 50)
        
        # 检查浏览器安装情况
        print("🔍 检查浏览器安装情况...")
        chrome_installed = self.check_chrome_installed()
        firefox_installed = self.check_firefox_installed()
        
        print(f"Chrome: {'✅ 已安装' if chrome_installed else '❌ 未安装'}")
        print(f"Firefox: {'✅ 已安装' if firefox_installed else '❌ 未安装'}")
        
        if not chrome_installed and not firefox_installed:
            print("❌ 未检测到Chrome或Firefox浏览器，请先安装浏览器")
            return False
        
        # 安装webdriver-manager
        success = True
        
        if chrome_installed:
            if not self.install_chromedriver_via_webdriver_manager():
                success = False
        
        if firefox_installed:
            if not self.install_geckodriver_via_webdriver_manager():
                success = False
        
        # 测试WebDriver
        if success:
            self.test_webdrivers()
        
        return success

def main():
    """主函数"""
    setup = WebDriverSetup()
    
    print("🌐 WebDriver设置工具")
    print("=" * 30)
    
    try:
        if setup.setup_all():
            print("\n🎉 WebDriver设置完成！")
            print("现在可以运行浏览器兼容性测试了：")
            print("python test_browser_compatibility.py")
            return 0
        else:
            print("\n⚠️ WebDriver设置过程中出现问题")
            print("请检查错误信息并手动安装相关驱动")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ 设置被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 设置过程中出现错误: {e}")
        return 1

if __name__ == "__main__":
    exit(main())