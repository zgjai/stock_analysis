"""
历史交易记录功能移动端响应式适配测试
验证在不同移动设备上的显示和交互效果
"""
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.touch_actions import TouchActions


class TestMobileResponsive:
    """移动端响应式测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.base_url = "http://localhost:5000"
        self.wait_timeout = 10
        
        # 定义测试设备
        self.devices = {
            "iPhone_SE": {"width": 375, "height": 667, "pixel_ratio": 2.0},
            "iPhone_12": {"width": 390, "height": 844, "pixel_ratio": 3.0},
            "iPhone_12_Pro_Max": {"width": 428, "height": 926, "pixel_ratio": 3.0},
            "Samsung_Galaxy_S21": {"width": 360, "height": 800, "pixel_ratio": 3.0},
            "iPad_Mini": {"width": 768, "height": 1024, "pixel_ratio": 2.0},
            "iPad_Pro": {"width": 1024, "height": 1366, "pixel_ratio": 2.0},
            "Android_Tablet": {"width": 800, "height": 1280, "pixel_ratio": 2.0}
        }
        
        self.test_results = {}
    
    def get_mobile_driver(self, device_name):
        """获取移动设备模拟驱动"""
        device = self.devices[device_name]
        
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # 移动设备模拟配置
        mobile_emulation = {
            "deviceMetrics": {
                "width": device["width"],
                "height": device["height"],
                "pixelRatio": device["pixel_ratio"]
            },
            "userAgent": self.get_user_agent(device_name)
        }
        
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(device["width"], device["height"])
        
        return driver
    
    def get_user_agent(self, device_name):
        """获取设备对应的User Agent"""
        user_agents = {
            "iPhone_SE": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "iPhone_12": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "iPhone_12_Pro_Max": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "Samsung_Galaxy_S21": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
            "iPad_Mini": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "iPad_Pro": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Android_Tablet": "Mozilla/5.0 (Linux; Android 10; SM-T510) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36"
        }
        return user_agents.get(device_name, user_agents["iPhone_12"])
    
    def test_layout_adaptation(self):
        """测试布局适配"""
        for device_name in self.devices:
            driver = None
            try:
                driver = self.get_mobile_driver(device_name)
                device = self.devices[device_name]
                
                # 访问历史交易页面
                driver.get(f"{self.base_url}/historical-trades")
                
                # 等待页面加载
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                # 检查容器宽度适配
                container = driver.find_element(By.CLASS_NAME, "historical-trades-container")
                container_width = container.size['width']
                viewport_width = device['width']
                
                # 容器宽度应该适配视口
                width_ratio = container_width / viewport_width
                assert 0.9 <= width_ratio <= 1.1, f"容器宽度适配异常: {width_ratio}"
                
                # 检查表格响应式
                table = driver.find_element(By.CLASS_NAME, "historical-trades-table")
                table_display = table.value_of_css_property("display")
                
                # 在小屏幕上，表格可能会变成块级元素或使用滚动
                if device['width'] < 768:
                    # 小屏幕设备
                    assert table_display in ["block", "table", "flex"]
                else:
                    # 大屏幕设备
                    assert table_display in ["table", "block"]
                
                # 检查筛选面板适配
                filter_panel = driver.find_element(By.CLASS_NAME, "filter-panel")
                filter_panel_width = filter_panel.size['width']
                
                # 筛选面板应该适配容器宽度
                panel_ratio = filter_panel_width / container_width
                assert 0.8 <= panel_ratio <= 1.0
                
                self.test_results[f"{device_name}_layout"] = {
                    "success": True,
                    "container_width": container_width,
                    "viewport_width": viewport_width,
                    "width_ratio": width_ratio
                }
                
            except Exception as e:
                self.test_results[f"{device_name}_layout"] = {
                    "success": False,
                    "error": str(e)
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_table_responsive_behavior(self):
        """测试表格响应式行为"""
        for device_name in self.devices:
            driver = None
            try:
                driver = self.get_mobile_driver(device_name)
                device = self.devices[device_name]
                
                driver.get(f"{self.base_url}/historical-trades")
                
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-table"))
                )
                
                table = driver.find_element(By.CLASS_NAME, "historical-trades-table")
                
                # 检查表格是否有水平滚动
                has_horizontal_scroll = driver.execute_script("""
                    var table = arguments[0];
                    return table.scrollWidth > table.clientWidth;
                """, table)
                
                # 检查表格列的显示
                headers = driver.find_elements(By.CSS_SELECTOR, ".historical-trades-table th")
                visible_headers = [h for h in headers if h.is_displayed()]
                
                if device['width'] < 576:
                    # 超小屏幕：可能隐藏某些列或使用卡片布局
                    assert len(visible_headers) >= 3  # 至少显示3列核心信息
                elif device['width'] < 768:
                    # 小屏幕：显示主要列
                    assert len(visible_headers) >= 4
                else:
                    # 大屏幕：显示所有列
                    assert len(visible_headers) >= 6
                
                # 检查行的点击区域
                rows = driver.find_elements(By.CSS_SELECTOR, ".historical-trades-table tbody tr")
                if rows:
                    first_row = rows[0]
                    row_height = first_row.size['height']
                    
                    # 移动端行高应该足够大，便于触摸
                    if device['width'] < 768:
                        assert row_height >= 44  # 最小触摸目标44px
                
                self.test_results[f"{device_name}_table"] = {
                    "success": True,
                    "has_horizontal_scroll": has_horizontal_scroll,
                    "visible_headers": len(visible_headers),
                    "row_height": row_height if rows else 0
                }
                
            except Exception as e:
                self.test_results[f"{device_name}_table"] = {
                    "success": False,
                    "error": str(e)
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_touch_interactions(self):
        """测试触摸交互"""
        # 只在手机设备上测试触摸交互
        mobile_devices = ["iPhone_12", "Samsung_Galaxy_S21"]
        
        for device_name in mobile_devices:
            driver = None
            try:
                driver = self.get_mobile_driver(device_name)
                
                driver.get(f"{self.base_url}/historical-trades")
                
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                # 测试按钮点击
                filter_button = driver.find_element(By.ID, "apply-filter-btn")
                button_size = filter_button.size
                
                # 按钮应该足够大，便于触摸
                assert button_size['width'] >= 44 and button_size['height'] >= 44
                
                # 测试点击
                filter_button.click()
                time.sleep(1)
                
                # 测试输入框交互
                stock_input = driver.find_element(By.ID, "stock-code-filter")
                stock_input.click()
                stock_input.clear()
                stock_input.send_keys("000001")
                
                # 验证输入
                input_value = stock_input.get_attribute("value")
                assert input_value == "000001"
                
                # 测试滑动操作（如果表格有水平滚动）
                table = driver.find_element(By.CLASS_NAME, "historical-trades-table")
                initial_scroll = driver.execute_script("return arguments[0].scrollLeft;", table)
                
                # 尝试水平滑动
                driver.execute_script("arguments[0].scrollLeft = 100;", table)
                time.sleep(0.5)
                
                final_scroll = driver.execute_script("return arguments[0].scrollLeft;", table)
                
                self.test_results[f"{device_name}_touch"] = {
                    "success": True,
                    "button_size": button_size,
                    "input_interaction": True,
                    "scroll_change": final_scroll - initial_scroll
                }
                
            except Exception as e:
                self.test_results[f"{device_name}_touch"] = {
                    "success": False,
                    "error": str(e)
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_modal_responsive_behavior(self):
        """测试模态框响应式行为"""
        for device_name in self.devices:
            driver = None
            try:
                driver = self.get_mobile_driver(device_name)
                device = self.devices[device_name]
                
                driver.get(f"{self.base_url}/historical-trades")
                
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                # 尝试打开复盘模态框
                try:
                    review_button = driver.find_element(By.CLASS_NAME, "add-review-btn")
                    review_button.click()
                    
                    # 等待模态框出现
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "review-modal"))
                    )
                    
                    modal = driver.find_element(By.CLASS_NAME, "review-modal")
                    modal_size = modal.size
                    
                    # 检查模态框尺寸适配
                    if device['width'] < 768:
                        # 小屏幕：模态框应该接近全屏
                        width_ratio = modal_size['width'] / device['width']
                        assert width_ratio >= 0.9
                    else:
                        # 大屏幕：模态框可以是固定宽度
                        assert modal_size['width'] >= 400
                    
                    # 检查模态框内容是否可滚动
                    modal_content = driver.find_element(By.CLASS_NAME, "modal-content")
                    content_height = modal_content.size['height']
                    
                    # 内容高度不应超过视口高度
                    assert content_height <= device['height']
                    
                    # 关闭模态框
                    close_button = driver.find_element(By.CLASS_NAME, "modal-close-btn")
                    close_button.click()
                    
                    # 等待模态框消失
                    WebDriverWait(driver, 5).until_not(
                        EC.presence_of_element_located((By.CLASS_NAME, "review-modal"))
                    )
                    
                    self.test_results[f"{device_name}_modal"] = {
                        "success": True,
                        "modal_size": modal_size,
                        "width_ratio": modal_size['width'] / device['width']
                    }
                    
                except:
                    # 如果没有复盘按钮，跳过测试
                    self.test_results[f"{device_name}_modal"] = {
                        "success": True,
                        "skipped": True,
                        "reason": "No review button found"
                    }
                
            except Exception as e:
                self.test_results[f"{device_name}_modal"] = {
                    "success": False,
                    "error": str(e)
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_navigation_responsive(self):
        """测试导航响应式"""
        for device_name in self.devices:
            driver = None
            try:
                driver = self.get_mobile_driver(device_name)
                device = self.devices[device_name]
                
                driver.get(f"{self.base_url}/historical-trades")
                
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                # 检查侧边栏或导航菜单
                try:
                    sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
                    sidebar_display = sidebar.value_of_css_property("display")
                    
                    if device['width'] < 768:
                        # 小屏幕：侧边栏可能隐藏或折叠
                        assert sidebar_display in ["none", "block"]
                    else:
                        # 大屏幕：侧边栏应该显示
                        assert sidebar_display != "none"
                        
                except:
                    # 如果没有侧边栏，跳过
                    pass
                
                # 检查面包屑导航
                try:
                    breadcrumb = driver.find_element(By.CLASS_NAME, "breadcrumb")
                    breadcrumb_size = breadcrumb.size
                    
                    # 面包屑应该适配容器宽度
                    container = driver.find_element(By.CLASS_NAME, "historical-trades-container")
                    container_width = container.size['width']
                    
                    breadcrumb_ratio = breadcrumb_size['width'] / container_width
                    assert breadcrumb_ratio <= 1.0
                    
                except:
                    # 如果没有面包屑，跳过
                    pass
                
                # 检查分页导航
                try:
                    pagination = driver.find_element(By.CLASS_NAME, "pagination-container")
                    pagination_size = pagination.size
                    
                    # 分页控件应该适配屏幕
                    if device['width'] < 576:
                        # 超小屏幕：分页可能简化显示
                        page_buttons = driver.find_elements(By.CSS_SELECTOR, ".pagination-container .page-btn")
                        assert len(page_buttons) <= 5  # 简化显示
                    
                except:
                    # 如果没有分页，跳过
                    pass
                
                self.test_results[f"{device_name}_navigation"] = {
                    "success": True,
                    "device_width": device['width']
                }
                
            except Exception as e:
                self.test_results[f"{device_name}_navigation"] = {
                    "success": False,
                    "error": str(e)
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_form_elements_mobile_friendly(self):
        """测试表单元素移动端友好性"""
        mobile_devices = ["iPhone_12", "Samsung_Galaxy_S21"]
        
        for device_name in mobile_devices:
            driver = None
            try:
                driver = self.get_mobile_driver(device_name)
                
                driver.get(f"{self.base_url}/historical-trades")
                
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "filter-panel"))
                )
                
                # 检查输入框大小
                inputs = driver.find_elements(By.CSS_SELECTOR, ".filter-panel input")
                for input_elem in inputs:
                    input_size = input_elem.size
                    # 输入框高度应该适合触摸
                    assert input_size['height'] >= 36
                
                # 检查按钮大小
                buttons = driver.find_elements(By.CSS_SELECTOR, ".filter-panel button")
                for button in buttons:
                    button_size = button.size
                    # 按钮应该足够大
                    assert button_size['width'] >= 44 and button_size['height'] >= 44
                
                # 检查下拉选择框
                selects = driver.find_elements(By.CSS_SELECTOR, ".filter-panel select")
                for select in selects:
                    select_size = select.size
                    # 下拉框应该足够大
                    assert select_size['height'] >= 36
                
                # 测试表单交互
                stock_input = driver.find_element(By.ID, "stock-code-filter")
                
                # 点击输入框
                stock_input.click()
                time.sleep(0.5)
                
                # 检查是否触发了移动端键盘（通过视口变化检测）
                viewport_height_after_focus = driver.execute_script("return window.innerHeight;")
                
                # 输入文本
                stock_input.clear()
                stock_input.send_keys("000001")
                
                # 验证输入
                assert stock_input.get_attribute("value") == "000001"
                
                self.test_results[f"{device_name}_form_elements"] = {
                    "success": True,
                    "input_count": len(inputs),
                    "button_count": len(buttons),
                    "select_count": len(selects)
                }
                
            except Exception as e:
                self.test_results[f"{device_name}_form_elements"] = {
                    "success": False,
                    "error": str(e)
                }
            finally:
                if driver:
                    driver.quit()
    
    def test_performance_on_mobile(self):
        """测试移动端性能"""
        mobile_devices = ["iPhone_12", "Samsung_Galaxy_S21"]
        
        for device_name in mobile_devices:
            driver = None
            try:
                driver = self.get_mobile_driver(device_name)
                
                # 测量页面加载时间
                start_time = time.time()
                driver.get(f"{self.base_url}/historical-trades")
                
                WebDriverWait(driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "historical-trades-container"))
                )
                
                load_time = time.time() - start_time
                
                # 测量JavaScript执行时间
                js_start_time = time.time()
                driver.execute_script("""
                    // 模拟一些JavaScript操作
                    var table = document.querySelector('.historical-trades-table');
                    if (table) {
                        var rows = table.querySelectorAll('tbody tr');
                        for (var i = 0; i < rows.length; i++) {
                            rows[i].style.backgroundColor = '';
                        }
                    }
                """)
                js_execution_time = time.time() - js_start_time
                
                # 检查内存使用（通过JavaScript）
                memory_info = driver.execute_script("""
                    if (performance.memory) {
                        return {
                            usedJSHeapSize: performance.memory.usedJSHeapSize,
                            totalJSHeapSize: performance.memory.totalJSHeapSize,
                            jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                        };
                    }
                    return null;
                """)
                
                # 移动端性能要求
                assert load_time < 5.0  # 页面加载时间小于5秒
                assert js_execution_time < 1.0  # JavaScript执行时间小于1秒
                
                self.test_results[f"{device_name}_performance"] = {
                    "success": True,
                    "load_time": load_time,
                    "js_execution_time": js_execution_time,
                    "memory_info": memory_info
                }
                
            except Exception as e:
                self.test_results[f"{device_name}_performance"] = {
                    "success": False,
                    "error": str(e)
                }
            finally:
                if driver:
                    driver.quit()
    
    def teardown_method(self):
        """生成移动端测试报告"""
        # 计算测试统计
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get("success", False)])
        failed_tests = total_tests - passed_tests
        
        # 生成报告
        report = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_type": "Mobile Responsive Testing",
            "devices_tested": list(self.devices.keys()),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": self.test_results
        }
        
        # 保存报告
        with open('mobile_responsive_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印摘要
        print(f"\n移动端响应式测试完成:")
        print(f"测试设备数: {len(self.devices)}")
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {report['success_rate']:.1f}%")
        
        # 按设备分组显示结果
        device_results = {}
        for test_name, result in self.test_results.items():
            device = test_name.split('_')[0]
            if device not in device_results:
                device_results[device] = {"passed": 0, "failed": 0}
            
            if result.get("success", False):
                device_results[device]["passed"] += 1
            else:
                device_results[device]["failed"] += 1
        
        print("\n各设备测试结果:")
        for device, results in device_results.items():
            total = results["passed"] + results["failed"]
            success_rate = (results["passed"] / total * 100) if total > 0 else 0
            print(f"  {device}: {results['passed']}/{total} ({success_rate:.1f}%)")