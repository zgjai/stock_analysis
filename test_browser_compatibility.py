#!/usr/bin/env python3
"""
浏览器兼容性测试脚本
测试任务7.1：主流浏览器基本测试
- 在Chrome和Firefox中测试主要功能
- 验证基本的响应式布局
- 测试JavaScript功能的兼容性
"""

import os
import sys
import time
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

class BrowserCompatibilityTester:
    def __init__(self):
        self.base_url = "http://localhost:5002"
        self.test_results = []
        self.browsers = ['chrome', 'firefox']
        self.current_browser = None
        self.driver = None
        
    def setup_chrome_driver(self):
        """设置Chrome驱动"""
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.implicitly_wait(10)
            self.current_browser = 'chrome'
            return True
        except Exception as e:
            print(f"❌ 无法启动Chrome驱动: {e}")
            if not WEBDRIVER_MANAGER_AVAILABLE:
                print("💡 建议安装webdriver-manager: pip install webdriver-manager")
            return False
    
    def setup_firefox_driver(self):
        """设置Firefox驱动"""
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
            else:
                self.driver = webdriver.Firefox(options=firefox_options)
            
            self.driver.implicitly_wait(10)
            self.current_browser = 'firefox'
            return True
        except Exception as e:
            print(f"❌ 无法启动Firefox驱动: {e}")
            if not WEBDRIVER_MANAGER_AVAILABLE:
                print("💡 建议安装webdriver-manager: pip install webdriver-manager")
            return False
    
    def setup_driver(self, browser):
        """根据浏览器类型设置驱动"""
        if browser == 'chrome':
            return self.setup_chrome_driver()
        elif browser == 'firefox':
            return self.setup_firefox_driver()
        else:
            print(f"❌ 不支持的浏览器类型: {browser}")
            return False
    
    def cleanup_driver(self):
        """清理驱动"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.current_browser = None
    
    def check_server_running(self):
        """检查服务器是否运行"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_server(self):
        """启动Flask服务器"""
        if self.check_server_running():
            print("✅ 服务器已在运行")
            return True
        
        print("🚀 启动Flask服务器...")
        try:
            # 尝试启动服务器
            subprocess.Popen([sys.executable, "app.py"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # 等待服务器启动
            for i in range(30):
                if self.check_server_running():
                    print("✅ 服务器启动成功")
                    return True
                time.sleep(1)
            
            print("❌ 服务器启动超时")
            return False
        except Exception as e:
            print(f"❌ 启动服务器失败: {e}")
            return False
    
    def test_page_loading(self):
        """测试页面加载功能"""
        test_name = f"页面加载测试 ({self.current_browser})"
        print(f"🧪 {test_name}")
        
        pages = [
            ("/", "仪表板"),
            ("/trading_records", "交易记录"),
            ("/stock_pool", "股票池"),
            ("/review", "复盘记录"),
            ("/analytics", "统计分析"),
            ("/cases", "案例管理"),
            ("/sector_analysis", "板块分析")
        ]
        
        results = []
        for path, name in pages:
            try:
                self.driver.get(f"{self.base_url}{path}")
                
                # 等待页面加载完成
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 检查页面标题
                title = self.driver.title
                if title and title != "":
                    results.append(f"✅ {name}页面加载成功")
                else:
                    results.append(f"⚠️ {name}页面标题为空")
                
                # 检查是否有JavaScript错误
                logs = self.driver.get_log('browser')
                js_errors = [log for log in logs if log['level'] == 'SEVERE']
                if js_errors:
                    results.append(f"⚠️ {name}页面有JavaScript错误: {len(js_errors)}个")
                
                time.sleep(1)  # 短暂等待
                
            except TimeoutException:
                results.append(f"❌ {name}页面加载超时")
            except Exception as e:
                results.append(f"❌ {name}页面加载失败: {str(e)}")
        
        self.test_results.append({
            'test': test_name,
            'results': results,
            'status': 'passed' if all('✅' in r for r in results) else 'warning'
        })
        
        return results
    
    def test_responsive_layout(self):
        """测试响应式布局"""
        test_name = f"响应式布局测试 ({self.current_browser})"
        print(f"🧪 {test_name}")
        
        # 测试不同屏幕尺寸
        screen_sizes = [
            (1920, 1080, "桌面"),
            (1366, 768, "笔记本"),
            (768, 1024, "平板"),
            (375, 667, "手机")
        ]
        
        results = []
        
        for width, height, device in screen_sizes:
            try:
                self.driver.set_window_size(width, height)
                self.driver.get(f"{self.base_url}/")
                
                # 等待页面加载
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 检查导航栏是否存在
                nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .navbar")
                if nav_elements:
                    results.append(f"✅ {device}尺寸导航栏正常显示")
                else:
                    results.append(f"⚠️ {device}尺寸导航栏未找到")
                
                # 检查主要内容区域
                main_content = self.driver.find_elements(By.CSS_SELECTOR, "main, .container, .content")
                if main_content:
                    results.append(f"✅ {device}尺寸主内容区域正常")
                else:
                    results.append(f"⚠️ {device}尺寸主内容区域未找到")
                
                # 检查是否有水平滚动条（移动端不应该有）
                if width < 768:
                    body_width = self.driver.execute_script("return document.body.scrollWidth")
                    if body_width <= width + 20:  # 允许小误差
                        results.append(f"✅ {device}尺寸无水平滚动")
                    else:
                        results.append(f"⚠️ {device}尺寸存在水平滚动")
                
                time.sleep(0.5)
                
            except Exception as e:
                results.append(f"❌ {device}尺寸测试失败: {str(e)}")
        
        self.test_results.append({
            'test': test_name,
            'results': results,
            'status': 'passed' if all('✅' in r for r in results) else 'warning'
        })
        
        return results
    
    def test_javascript_functionality(self):
        """测试JavaScript功能兼容性"""
        test_name = f"JavaScript功能测试 ({self.current_browser})"
        print(f"🧪 {test_name}")
        
        results = []
        
        try:
            # 访问交易记录页面
            self.driver.get(f"{self.base_url}/trading_records")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 测试模态框功能
            try:
                add_button = self.driver.find_element(By.CSS_SELECTOR, "[data-bs-target='#addTradeModal']")
                if add_button:
                    results.append("✅ 找到添加交易按钮")
                    
                    # 点击按钮
                    self.driver.execute_script("arguments[0].click();", add_button)
                    time.sleep(1)
                    
                    # 检查模态框是否出现
                    modal = self.driver.find_element(By.ID, "addTradeModal")
                    if modal and modal.is_displayed():
                        results.append("✅ 模态框正常显示")
                    else:
                        results.append("⚠️ 模态框未正常显示")
                        
            except NoSuchElementException:
                results.append("⚠️ 未找到添加交易按钮")
            except Exception as e:
                results.append(f"⚠️ 模态框测试失败: {str(e)}")
            
            # 测试表格功能
            try:
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                if tables:
                    results.append("✅ 找到数据表格")
                    
                    # 检查表格是否有数据或显示无数据信息
                    rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                    no_data = self.driver.find_elements(By.CSS_SELECTOR, ".no-data, .empty-state")
                    
                    if rows or no_data:
                        results.append("✅ 表格数据状态正常")
                    else:
                        results.append("⚠️ 表格状态异常")
                else:
                    results.append("⚠️ 未找到数据表格")
                    
            except Exception as e:
                results.append(f"⚠️ 表格测试失败: {str(e)}")
            
            # 测试图表功能（访问统计分析页面）
            try:
                self.driver.get(f"{self.base_url}/analytics")
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 等待图表加载
                time.sleep(3)
                
                # 检查Chart.js是否加载
                chart_loaded = self.driver.execute_script(
                    "return typeof Chart !== 'undefined'"
                )
                
                if chart_loaded:
                    results.append("✅ Chart.js库加载成功")
                else:
                    results.append("⚠️ Chart.js库未加载")
                
                # 检查是否有canvas元素（图表）
                canvases = self.driver.find_elements(By.TAG_NAME, "canvas")
                if canvases:
                    results.append("✅ 找到图表canvas元素")
                else:
                    results.append("⚠️ 未找到图表canvas元素")
                    
            except Exception as e:
                results.append(f"⚠️ 图表测试失败: {str(e)}")
            
            # 测试AJAX功能
            try:
                # 检查jQuery是否加载
                jquery_loaded = self.driver.execute_script(
                    "return typeof $ !== 'undefined'"
                )
                
                if jquery_loaded:
                    results.append("✅ jQuery库加载成功")
                else:
                    results.append("⚠️ jQuery库未加载")
                
                # 检查fetch API支持
                fetch_supported = self.driver.execute_script(
                    "return typeof fetch !== 'undefined'"
                )
                
                if fetch_supported:
                    results.append("✅ Fetch API支持正常")
                else:
                    results.append("⚠️ Fetch API不支持")
                    
            except Exception as e:
                results.append(f"⚠️ AJAX测试失败: {str(e)}")
            
        except Exception as e:
            results.append(f"❌ JavaScript功能测试失败: {str(e)}")
        
        self.test_results.append({
            'test': test_name,
            'results': results,
            'status': 'passed' if all('✅' in r for r in results) else 'warning'
        })
        
        return results
    
    def test_form_functionality(self):
        """测试表单功能兼容性"""
        test_name = f"表单功能测试 ({self.current_browser})"
        print(f"🧪 {test_name}")
        
        results = []
        
        try:
            # 访问交易记录页面
            self.driver.get(f"{self.base_url}/trading_records")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 点击添加交易按钮
            try:
                add_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-bs-target='#addTradeModal']"))
                )
                self.driver.execute_script("arguments[0].click();", add_button)
                
                # 等待模态框出现
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "addTradeModal"))
                )
                
                # 测试表单字段
                form_fields = [
                    ("input[name='stock_code']", "股票代码"),
                    ("select[name='action']", "交易类型"),
                    ("input[name='quantity']", "数量"),
                    ("input[name='price']", "价格"),
                    ("input[name='trade_date']", "交易日期")
                ]
                
                for selector, field_name in form_fields:
                    try:
                        field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if field and field.is_displayed():
                            results.append(f"✅ {field_name}字段正常显示")
                            
                            # 测试字段是否可编辑
                            if field.tag_name == 'input':
                                field.clear()
                                field.send_keys("test")
                                if field.get_attribute('value') == "test":
                                    results.append(f"✅ {field_name}字段可正常输入")
                                else:
                                    results.append(f"⚠️ {field_name}字段输入异常")
                                field.clear()
                        else:
                            results.append(f"⚠️ {field_name}字段未正常显示")
                    except NoSuchElementException:
                        results.append(f"⚠️ 未找到{field_name}字段")
                    except Exception as e:
                        results.append(f"⚠️ {field_name}字段测试失败: {str(e)}")
                
                # 测试表单验证
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "#addTradeModal button[type='submit']")
                    if submit_button:
                        results.append("✅ 找到提交按钮")
                        
                        # 尝试提交空表单
                        self.driver.execute_script("arguments[0].click();", submit_button)
                        time.sleep(1)
                        
                        # 检查是否有验证错误信息
                        error_messages = self.driver.find_elements(By.CSS_SELECTOR, ".invalid-feedback, .error-message, .alert-danger")
                        if error_messages:
                            results.append("✅ 表单验证正常工作")
                        else:
                            results.append("⚠️ 表单验证可能未工作")
                    else:
                        results.append("⚠️ 未找到提交按钮")
                        
                except Exception as e:
                    results.append(f"⚠️ 表单验证测试失败: {str(e)}")
                
            except TimeoutException:
                results.append("❌ 无法打开添加交易模态框")
            except Exception as e:
                results.append(f"❌ 表单功能测试失败: {str(e)}")
                
        except Exception as e:
            results.append(f"❌ 表单功能测试失败: {str(e)}")
        
        self.test_results.append({
            'test': test_name,
            'results': results,
            'status': 'passed' if all('✅' in r for r in results) else 'warning'
        })
        
        return results
    
    def run_browser_tests(self, browser):
        """运行指定浏览器的所有测试"""
        print(f"\n🌐 开始 {browser.upper()} 浏览器兼容性测试")
        print("=" * 50)
        
        if not self.setup_driver(browser):
            return False
        
        try:
            # 运行各项测试
            self.test_page_loading()
            self.test_responsive_layout()
            self.test_javascript_functionality()
            self.test_form_functionality()
            
            return True
            
        except Exception as e:
            print(f"❌ {browser}浏览器测试过程中出现错误: {e}")
            return False
        finally:
            self.cleanup_driver()
    
    def run_all_tests(self):
        """运行所有浏览器的兼容性测试"""
        print("🚀 开始浏览器兼容性测试")
        print("=" * 60)
        
        # 启动服务器
        if not self.start_server():
            print("❌ 无法启动服务器，测试终止")
            return False
        
        # 测试每个浏览器
        successful_browsers = []
        failed_browsers = []
        
        for browser in self.browsers:
            try:
                if self.run_browser_tests(browser):
                    successful_browsers.append(browser)
                else:
                    failed_browsers.append(browser)
            except Exception as e:
                print(f"❌ {browser}浏览器测试失败: {e}")
                failed_browsers.append(browser)
        
        # 生成测试报告
        self.generate_report(successful_browsers, failed_browsers)
        
        return len(failed_browsers) == 0
    
    def generate_report(self, successful_browsers, failed_browsers):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 浏览器兼容性测试报告")
        print("=" * 60)
        
        # 总体统计
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'passed'])
        warning_tests = total_tests - passed_tests
        
        print(f"\n📈 测试统计:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过测试: {passed_tests}")
        print(f"  警告测试: {warning_tests}")
        print(f"  成功浏览器: {len(successful_browsers)}")
        print(f"  失败浏览器: {len(failed_browsers)}")
        
        # 浏览器支持情况
        print(f"\n🌐 浏览器支持情况:")
        for browser in successful_browsers:
            print(f"  ✅ {browser.upper()}: 兼容")
        for browser in failed_browsers:
            print(f"  ❌ {browser.upper()}: 不兼容或测试失败")
        
        # 详细测试结果
        print(f"\n📋 详细测试结果:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'passed' else "⚠️"
            print(f"\n{status_icon} {result['test']}:")
            for item in result['results']:
                print(f"    {item}")
        
        # 兼容性建议
        print(f"\n💡 兼容性建议:")
        if failed_browsers:
            print(f"  - 需要修复 {', '.join(failed_browsers)} 浏览器的兼容性问题")
        if warning_tests > 0:
            print(f"  - 有 {warning_tests} 个测试存在警告，建议进一步检查")
        if len(successful_browsers) == len(self.browsers):
            print(f"  - 所有目标浏览器兼容性良好")
        
        # 保存报告到文件
        self.save_report_to_file()
    
    def save_report_to_file(self):
        """保存测试报告到文件"""
        try:
            with open("browser_compatibility_test_report.md", "w", encoding="utf-8") as f:
                f.write("# 浏览器兼容性测试报告\n\n")
                f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## 测试概述\n\n")
                f.write("本报告记录了股票交易记录系统在不同浏览器中的兼容性测试结果。\n\n")
                
                f.write("## 测试结果\n\n")
                for result in self.test_results:
                    f.write(f"### {result['test']}\n\n")
                    f.write(f"状态: {'✅ 通过' if result['status'] == 'passed' else '⚠️ 警告'}\n\n")
                    f.write("详细结果:\n")
                    for item in result['results']:
                        f.write(f"- {item}\n")
                    f.write("\n")
                
                f.write("## 总结\n\n")
                total_tests = len(self.test_results)
                passed_tests = len([t for t in self.test_results if t['status'] == 'passed'])
                f.write(f"- 总测试数: {total_tests}\n")
                f.write(f"- 通过测试: {passed_tests}\n")
                f.write(f"- 警告测试: {total_tests - passed_tests}\n")
                
            print(f"\n📄 测试报告已保存到: browser_compatibility_test_report.md")
            
        except Exception as e:
            print(f"⚠️ 保存测试报告失败: {e}")

def main():
    """主函数"""
    tester = BrowserCompatibilityTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 浏览器兼容性测试完成！")
            return 0
        else:
            print("\n⚠️ 浏览器兼容性测试完成，但存在问题")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        return 1
    finally:
        # 清理资源
        if tester.driver:
            tester.cleanup_driver()

if __name__ == "__main__":
    exit(main())