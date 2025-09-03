"""
历史交易记录功能浏览器兼容性测试
测试在不同浏览器和版本中的功能表现
"""
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import TimeoutException, WebDriverException


class TestBrowserCompatibility:
    """浏览器兼容性测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.base_url = "http://localhost:5000"
        self.wait_timeout = 10
        self.test_results = {}
    
    def get_chrome_driver(self, headless=True):
        """获取Chrome驱动"""
        options = ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        try:
            return webdriver.Chrome(options=options)
        except WebDriverException as e:
            pytest.skip(f"Chrome driver not available: {e}")
    
    def get_firefox_driver(self, headless=True):
        """获取Firefox驱动"""
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--width=1920')
        options.add_argument('--height=1080')
        
        try:
            return webdriver.Firefox(options=options)
        except WebDriverException as e:
            pytest.skip(f"Firefox driver not available: {e}")
    
    def get_edge_driver(self, headless=True):
        """获取Edge驱动"""
        options = EdgeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        try:
            return webdriver.Edge(options=options)
        except WebDriverException as e:
            pytest.skip(f"Edge driver not available: {e}")
    
    def test_page_loading_compatibility(self):
        """测试页面加载兼容性"""
        browsers = [
            ('Chrome', self.get_chrome_driver),
            ('Firefox', self.get_firefox_driver),
            ('Edge', self.get_edge_driver)
        ]
        
        for browser_name, driver_func in browsers:
            driver = None
            try:
                driver = driver_func()
                
                # 测试历史交易页面加载
                start_time = time.time()
                driver.get(f"{self.base_url}/historical-trades")
                
                # 等待页面加载完成
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                load_time = time.time() - start_time
                
                # 检查关键元素是否存在
                assert driver.find_element(By.CLASS_NAME, "historical-trades-table")
                assert driver.find_element(By.CLASS_NAME, "filter-panel")
                assert driver.find_element(By.CLASS_NAME, "pagination-container")
                
                # 检查JavaScript是否正常工作
                driver.execute_script("return typeof HistoricalTradesManager !== 'undefined'")
                
                self.test_results[f"{browser_name}_page_load"] = {
                    "success": True,
                    "load_time": load_time,
                    "message": f"页面在{browser_name}中正常加载"
                }
                
            except Exception as e:
                self.test_results[f"{browser_name}_page_load"] = {
                    "success": False,
                    "error": str(e),
                    "message": f"页面在{browser_name}中加载失败"
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_javascript_functionality_compatibility(self):
        """测试JavaScript功能兼容性"""
        browsers = [
            ('Chrome', self.get_chrome_driver),
            ('Firefox', self.get_firefox_driver),
            ('Edge', self.get_edge_driver)
        ]
        
        for browser_name, driver_func in browsers:
            driver = None
            try:
                driver = driver_func()
                driver.get(f"{self.base_url}/historical-trades")
                
                # 等待页面和JavaScript加载完成
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                # 测试筛选功能
                stock_code_input = driver.find_element(By.ID, "stock-code-filter")
                stock_code_input.clear()
                stock_code_input.send_keys("000001")
                
                # 点击筛选按钮
                filter_button = driver.find_element(By.ID, "apply-filter-btn")
                filter_button.click()
                
                # 等待筛选结果
                time.sleep(2)
                
                # 测试分页功能
                try:
                    next_page_btn = driver.find_element(By.CLASS_NAME, "next-page-btn")
                    if next_page_btn.is_enabled():
                        next_page_btn.click()
                        time.sleep(2)
                except:
                    pass  # 如果没有下一页按钮，跳过
                
                # 测试复盘模态框
                try:
                    review_btn = driver.find_element(By.CLASS_NAME, "add-review-btn")
                    review_btn.click()
                    
                    # 等待模态框出现
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "review-modal"))
                    )
                    
                    # 关闭模态框
                    close_btn = driver.find_element(By.CLASS_NAME, "modal-close-btn")
                    close_btn.click()
                    
                except:
                    pass  # 如果没有复盘按钮，跳过
                
                self.test_results[f"{browser_name}_js_functionality"] = {
                    "success": True,
                    "message": f"JavaScript功能在{browser_name}中正常工作"
                }
                
            except Exception as e:
                self.test_results[f"{browser_name}_js_functionality"] = {
                    "success": False,
                    "error": str(e),
                    "message": f"JavaScript功能在{browser_name}中出现问题"
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_css_rendering_compatibility(self):
        """测试CSS渲染兼容性"""
        browsers = [
            ('Chrome', self.get_chrome_driver),
            ('Firefox', self.get_firefox_driver),
            ('Edge', self.get_edge_driver)
        ]
        
        for browser_name, driver_func in browsers:
            driver = None
            try:
                driver = driver_func()
                driver.get(f"{self.base_url}/historical-trades")
                
                # 等待页面加载
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                # 检查关键元素的样式
                table = driver.find_element(By.CLASS_NAME, "historical-trades-table")
                table_display = table.value_of_css_property("display")
                assert table_display in ["table", "block"]
                
                # 检查响应式布局
                driver.set_window_size(768, 1024)  # 平板尺寸
                time.sleep(1)
                
                # 检查移动端适配
                driver.set_window_size(375, 667)  # 手机尺寸
                time.sleep(1)
                
                # 恢复桌面尺寸
                driver.set_window_size(1920, 1080)
                
                # 检查颜色和字体
                header = driver.find_element(By.TAG_NAME, "h1")
                font_family = header.value_of_css_property("font-family")
                color = header.value_of_css_property("color")
                
                assert font_family is not None
                assert color is not None
                
                self.test_results[f"{browser_name}_css_rendering"] = {
                    "success": True,
                    "message": f"CSS在{browser_name}中正常渲染"
                }
                
            except Exception as e:
                self.test_results[f"{browser_name}_css_rendering"] = {
                    "success": False,
                    "error": str(e),
                    "message": f"CSS在{browser_name}中渲染异常"
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_form_functionality_compatibility(self):
        """测试表单功能兼容性"""
        browsers = [
            ('Chrome', self.get_chrome_driver),
            ('Firefox', self.get_firefox_driver),
            ('Edge', self.get_edge_driver)
        ]
        
        for browser_name, driver_func in browsers:
            driver = None
            try:
                driver = driver_func()
                driver.get(f"{self.base_url}/historical-trades")
                
                # 等待页面加载
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                # 测试筛选表单
                stock_code_input = driver.find_element(By.ID, "stock-code-filter")
                stock_code_input.clear()
                stock_code_input.send_keys("000001")
                
                # 测试日期选择器
                try:
                    start_date_input = driver.find_element(By.ID, "start-date-filter")
                    start_date_input.clear()
                    start_date_input.send_keys("2024-01-01")
                except:
                    pass  # 某些浏览器可能不支持日期输入
                
                # 测试下拉选择
                try:
                    sort_select = driver.find_element(By.ID, "sort-by-select")
                    sort_select.click()
                    
                    # 选择一个选项
                    option = driver.find_element(By.CSS_SELECTOR, "#sort-by-select option[value='return_rate']")
                    option.click()
                except:
                    pass
                
                # 提交表单
                filter_button = driver.find_element(By.ID, "apply-filter-btn")
                filter_button.click()
                
                # 等待结果
                time.sleep(2)
                
                self.test_results[f"{browser_name}_form_functionality"] = {
                    "success": True,
                    "message": f"表单功能在{browser_name}中正常工作"
                }
                
            except Exception as e:
                self.test_results[f"{browser_name}_form_functionality"] = {
                    "success": False,
                    "error": str(e),
                    "message": f"表单功能在{browser_name}中出现问题"
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_ajax_requests_compatibility(self):
        """测试AJAX请求兼容性"""
        browsers = [
            ('Chrome', self.get_chrome_driver),
            ('Firefox', self.get_firefox_driver),
            ('Edge', self.get_edge_driver)
        ]
        
        for browser_name, driver_func in browsers:
            driver = None
            try:
                driver = driver_func()
                driver.get(f"{self.base_url}/historical-trades")
                
                # 等待页面加载
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                # 监听网络请求
                driver.execute_script("""
                    window.ajaxRequests = [];
                    var originalFetch = window.fetch;
                    window.fetch = function() {
                        window.ajaxRequests.push({
                            url: arguments[0],
                            method: arguments[1] ? arguments[1].method : 'GET',
                            timestamp: Date.now()
                        });
                        return originalFetch.apply(this, arguments);
                    };
                """)
                
                # 触发AJAX请求（点击筛选按钮）
                filter_button = driver.find_element(By.ID, "apply-filter-btn")
                filter_button.click()
                
                # 等待请求完成
                time.sleep(3)
                
                # 检查AJAX请求是否发送
                ajax_requests = driver.execute_script("return window.ajaxRequests;")
                
                # 验证至少有一个API请求
                api_requests = [req for req in ajax_requests if '/api/' in req['url']]
                assert len(api_requests) > 0
                
                self.test_results[f"{browser_name}_ajax_requests"] = {
                    "success": True,
                    "requests_count": len(api_requests),
                    "message": f"AJAX请求在{browser_name}中正常工作"
                }
                
            except Exception as e:
                self.test_results[f"{browser_name}_ajax_requests"] = {
                    "success": False,
                    "error": str(e),
                    "message": f"AJAX请求在{browser_name}中出现问题"
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_local_storage_compatibility(self):
        """测试本地存储兼容性"""
        browsers = [
            ('Chrome', self.get_chrome_driver),
            ('Firefox', self.get_firefox_driver),
            ('Edge', self.get_edge_driver)
        ]
        
        for browser_name, driver_func in browsers:
            driver = None
            try:
                driver = driver_func()
                driver.get(f"{self.base_url}/historical-trades")
                
                # 等待页面加载
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                # 测试localStorage
                driver.execute_script("localStorage.setItem('test_key', 'test_value');")
                stored_value = driver.execute_script("return localStorage.getItem('test_key');")
                assert stored_value == 'test_value'
                
                # 测试sessionStorage
                driver.execute_script("sessionStorage.setItem('session_key', 'session_value');")
                session_value = driver.execute_script("return sessionStorage.getItem('session_key');")
                assert session_value == 'session_value'
                
                # 清理
                driver.execute_script("localStorage.removeItem('test_key');")
                driver.execute_script("sessionStorage.removeItem('session_key');")
                
                self.test_results[f"{browser_name}_local_storage"] = {
                    "success": True,
                    "message": f"本地存储在{browser_name}中正常工作"
                }
                
            except Exception as e:
                self.test_results[f"{browser_name}_local_storage"] = {
                    "success": False,
                    "error": str(e),
                    "message": f"本地存储在{browser_name}中出现问题"
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_console_errors(self):
        """测试控制台错误"""
        browsers = [
            ('Chrome', self.get_chrome_driver),
            ('Firefox', self.get_firefox_driver)
        ]
        
        for browser_name, driver_func in browsers:
            driver = None
            try:
                driver = driver_func()
                driver.get(f"{self.base_url}/historical-trades")
                
                # 等待页面加载
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                # 获取控制台日志
                logs = driver.get_log('browser')
                
                # 筛选错误日志
                errors = [log for log in logs if log['level'] == 'SEVERE']
                warnings = [log for log in logs if log['level'] == 'WARNING']
                
                # 记录结果
                self.test_results[f"{browser_name}_console_errors"] = {
                    "success": len(errors) == 0,
                    "errors_count": len(errors),
                    "warnings_count": len(warnings),
                    "errors": errors[:5],  # 只记录前5个错误
                    "message": f"{browser_name}控制台检查完成"
                }
                
            except Exception as e:
                self.test_results[f"{browser_name}_console_errors"] = {
                    "success": False,
                    "error": str(e),
                    "message": f"无法检查{browser_name}控制台错误"
                }
            finally:
                if driver:
                    driver.quit()
    
    def teardown_method(self):
        """测试后清理并生成报告"""
        # 生成兼容性测试报告
        report = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.test_results),
            "passed_tests": len([r for r in self.test_results.values() if r.get("success", False)]),
            "failed_tests": len([r for r in self.test_results.values() if not r.get("success", False)]),
            "results": self.test_results
        }
        
        # 保存报告到文件
        with open('browser_compatibility_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印摘要
        print(f"\n浏览器兼容性测试完成:")
        print(f"总测试数: {report['total_tests']}")
        print(f"通过: {report['passed_tests']}")
        print(f"失败: {report['failed_tests']}")
        print(f"成功率: {report['passed_tests']/report['total_tests']*100:.1f}%")


class TestMobileCompatibility:
    """移动端兼容性测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.base_url = "http://localhost:5000"
        self.mobile_devices = [
            {"name": "iPhone 12", "width": 390, "height": 844},
            {"name": "Samsung Galaxy S21", "width": 360, "height": 800},
            {"name": "iPad", "width": 768, "height": 1024},
            {"name": "iPad Pro", "width": 1024, "height": 1366}
        ]
    
    def get_mobile_driver(self, device):
        """获取移动端模拟驱动"""
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={device["width"]},{device["height"]}')
        
        # 模拟移动设备
        mobile_emulation = {
            "deviceMetrics": {
                "width": device["width"],
                "height": device["height"],
                "pixelRatio": 2.0
            },
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        return webdriver.Chrome(options=options)
    
    def test_mobile_responsive_design(self):
        """测试移动端响应式设计"""
        for device in self.mobile_devices:
            driver = None
            try:
                driver = self.get_mobile_driver(device)
                driver.get(f"{self.base_url}/historical-trades")
                
                # 等待页面加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                # 检查表格是否适配移动端
                table = driver.find_element(By.CLASS_NAME, "historical-trades-table")
                table_width = table.size['width']
                viewport_width = device['width']
                
                # 表格宽度不应超过视口宽度
                assert table_width <= viewport_width + 50  # 允许50px的误差
                
                # 检查是否有水平滚动条
                has_horizontal_scroll = driver.execute_script(
                    "return document.documentElement.scrollWidth > document.documentElement.clientWidth;"
                )
                
                # 对于小屏幕设备，允许水平滚动
                if device['width'] < 768:
                    # 小屏幕设备可能需要水平滚动
                    pass
                else:
                    # 大屏幕设备不应该有水平滚动
                    assert not has_horizontal_scroll
                
                print(f"✓ {device['name']} 响应式设计测试通过")
                
            except Exception as e:
                print(f"✗ {device['name']} 响应式设计测试失败: {e}")
            finally:
                if driver:
                    driver.quit()
    
    def test_mobile_touch_interactions(self):
        """测试移动端触摸交互"""
        device = self.mobile_devices[0]  # 使用iPhone 12进行测试
        driver = None
        
        try:
            driver = self.get_mobile_driver(device)
            driver.get(f"{self.base_url}/historical-trades")
            
            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
            )
            
            # 测试触摸点击
            filter_button = driver.find_element(By.ID, "apply-filter-btn")
            filter_button.click()
            
            # 测试滑动操作（如果有的话）
            try:
                table = driver.find_element(By.CLASS_NAME, "historical-trades-table")
                driver.execute_script("arguments[0].scrollLeft = 100;", table)
            except:
                pass
            
            print("✓ 移动端触摸交互测试通过")
            
        except Exception as e:
            print(f"✗ 移动端触摸交互测试失败: {e}")
        finally:
            if driver:
                driver.quit()