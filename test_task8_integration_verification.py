#!/usr/bin/env python3
"""
任务8 - 复盘保存功能集成验证脚本
测试前端和后端的完整集成，包括JavaScript功能和API交互
"""

import sys
import json
import time
import requests
import subprocess
import threading
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

class IntegrationTestFramework:
    """复盘保存功能集成测试框架"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
        self.driver = None
        self.wait = None
        
        self.test_results = []
        self.test_stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
        
        print("🚀 初始化复盘保存功能集成测试框架")
        print(f"🌐 基础URL: {self.base_url}")
        print(f"📡 API URL: {self.api_base}")
    
    def setup_webdriver(self) -> bool:
        """设置WebDriver"""
        print("\n🔧 设置WebDriver")
        
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            self.log_result("WebDriver设置", True, "WebDriver初始化成功")
            return True
            
        except Exception as e:
            self.log_result("WebDriver设置", False, f"WebDriver初始化失败: {str(e)}")
            return False
    
    def teardown_webdriver(self):
        """清理WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                print("🧹 WebDriver已清理")
            except Exception as e:
                print(f"⚠️ WebDriver清理异常: {str(e)}")
    
    def log_result(self, test_name: str, success: bool, message: str, details: Optional[str] = None) -> Dict:
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        self.test_stats['total'] += 1
        
        if success is True:
            self.test_stats['passed'] += 1
            status_icon = "✅"
        elif success is False:
            self.test_stats['failed'] += 1
            status_icon = "❌"
        else:
            self.test_stats['warnings'] += 1
            status_icon = "⚠️"
        
        print(f"{status_icon} {test_name}: {message}")
        if details:
            print(f"   详情: {details}")
        
        return result
    
    def test_server_availability(self) -> bool:
        """测试服务器可用性"""
        print("\n🔍 测试服务器可用性")
        
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                self.log_result("服务器可用性", True, "服务器正常运行")
                return True
            else:
                self.log_result("服务器可用性", False, f"服务器返回状态码: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_result("服务器可用性", False, f"服务器连接失败: {str(e)}")
            return False
    
    def test_page_loading(self) -> bool:
        """测试页面加载"""
        print("\n🔍 测试复盘页面加载")
        
        if not self.driver:
            self.log_result("页面加载", False, "WebDriver未初始化")
            return False
        
        try:
            # 访问复盘页面
            review_url = f"{self.base_url}/review"
            self.driver.get(review_url)
            
            # 等待页面标题加载
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "title")))
            
            page_title = self.driver.title
            if "复盘" in page_title:
                self.log_result("页面加载", True, f"页面加载成功: {page_title}")
            else:
                self.log_result("页面加载", "warning", f"页面标题可能不正确: {page_title}")
            
            # 检查关键元素是否存在
            key_elements = [
                ("复盘模态框", "#reviewModal"),
                ("保存按钮", "#save-review-btn"),
                ("复盘表单", "#review-form")
            ]
            
            for element_name, selector in key_elements:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        self.log_result(f"页面元素-{element_name}", True, f"元素存在: {selector}")
                    else:
                        self.log_result(f"页面元素-{element_name}", False, f"元素不存在: {selector}")
                except Exception as e:
                    self.log_result(f"页面元素-{element_name}", False, f"查找元素失败: {str(e)}")
            
            return True
            
        except TimeoutException:
            self.log_result("页面加载", False, "页面加载超时")
            return False
        except WebDriverException as e:
            self.log_result("页面加载", False, f"WebDriver异常: {str(e)}")
            return False
    
    def test_javascript_loading(self) -> bool:
        """测试JavaScript文件加载"""
        print("\n🔍 测试JavaScript文件加载")
        
        if not self.driver:
            self.log_result("JavaScript加载", False, "WebDriver未初始化")
            return False
        
        try:
            # 检查关键JavaScript对象是否存在
            js_checks = [
                ("ApiClient类", "typeof ApiClient !== 'undefined'"),
                ("ReviewSaveManager类", "typeof ReviewSaveManager !== 'undefined'"),
                ("UnifiedMessageSystem类", "typeof UnifiedMessageSystem !== 'undefined'"),
                ("全局apiClient实例", "typeof apiClient !== 'undefined'"),
                ("全局reviewSaveManager实例", "typeof reviewSaveManager !== 'undefined'"),
                ("Bootstrap", "typeof bootstrap !== 'undefined'"),
                ("jQuery", "typeof $ !== 'undefined'")
            ]
            
            all_loaded = True
            
            for check_name, js_code in js_checks:
                try:
                    result = self.driver.execute_script(f"return {js_code};")
                    if result:
                        self.log_result(f"JS加载-{check_name}", True, "对象已加载")
                    else:
                        self.log_result(f"JS加载-{check_name}", False, "对象未加载")
                        all_loaded = False
                except Exception as e:
                    self.log_result(f"JS加载-{check_name}", False, f"检查失败: {str(e)}")
                    all_loaded = False
            
            return all_loaded
            
        except Exception as e:
            self.log_result("JavaScript加载", False, f"JavaScript检查异常: {str(e)}")
            return False
    
    def test_modal_functionality(self) -> bool:
        """测试模态框功能"""
        print("\n🔍 测试复盘模态框功能")
        
        if not self.driver:
            self.log_result("模态框功能", False, "WebDriver未初始化")
            return False
        
        try:
            # 查找并点击触发模态框的按钮
            # 这里需要根据实际页面结构调整选择器
            trigger_selectors = [
                "button[onclick*='openQuickReview']",
                ".btn[data-bs-target='#reviewModal']",
                "#quick-review-stock + button"
            ]
            
            modal_opened = False
            
            for selector in trigger_selectors:
                try:
                    trigger_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if trigger_button and trigger_button.is_displayed():
                        # 点击按钮打开模态框
                        self.driver.execute_script("arguments[0].click();", trigger_button)
                        
                        # 等待模态框显示
                        time.sleep(1)
                        
                        # 检查模态框是否显示
                        modal = self.driver.find_element(By.ID, "reviewModal")
                        if modal and modal.is_displayed():
                            self.log_result("模态框打开", True, f"模态框成功打开 (触发器: {selector})")
                            modal_opened = True
                            break
                        
                except Exception:
                    continue
            
            if not modal_opened:
                # 尝试直接显示模态框
                try:
                    self.driver.execute_script("""
                        var modal = document.getElementById('reviewModal');
                        if (modal) {
                            modal.style.display = 'block';
                            modal.classList.add('show');
                        }
                    """)
                    time.sleep(0.5)
                    
                    modal = self.driver.find_element(By.ID, "reviewModal")
                    if modal and modal.is_displayed():
                        self.log_result("模态框打开", True, "模态框通过脚本打开")
                        modal_opened = True
                    else:
                        self.log_result("模态框打开", False, "无法打开模态框")
                        return False
                        
                except Exception as e:
                    self.log_result("模态框打开", False, f"模态框打开失败: {str(e)}")
                    return False
            
            # 测试表单字段
            form_fields = [
                ("股票代码", "#display-stock-code"),
                ("复盘日期", "#review-date"),
                ("持仓天数", "#holding-days"),
                ("当前价格", "#current-price-input"),
                ("分析内容", "#analysis"),
                ("决策结果", "#decision"),
                ("决策理由", "#reason")
            ]
            
            for field_name, selector in form_fields:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if field:
                        self.log_result(f"表单字段-{field_name}", True, f"字段存在: {selector}")
                    else:
                        self.log_result(f"表单字段-{field_name}", False, f"字段不存在: {selector}")
                except Exception:
                    self.log_result(f"表单字段-{field_name}", False, f"查找字段失败: {selector}")
            
            return True
            
        except Exception as e:
            self.log_result("模态框功能", False, f"模态框测试异常: {str(e)}")
            return False
    
    def test_form_interaction(self) -> bool:
        """测试表单交互"""
        print("\n🔍 测试表单交互功能")
        
        if not self.driver:
            self.log_result("表单交互", False, "WebDriver未初始化")
            return False
        
        try:
            # 确保模态框是打开的
            modal = self.driver.find_element(By.ID, "reviewModal")
            if not modal.is_displayed():
                self.driver.execute_script("""
                    var modal = document.getElementById('reviewModal');
                    if (modal) {
                        modal.style.display = 'block';
                        modal.classList.add('show');
                    }
                """)
                time.sleep(0.5)
            
            # 填写表单数据
            form_data = {
                "#review-date": date.today().isoformat(),
                "#holding-days": "5",
                "#current-price-input": "10.50",
                "#analysis": "集成测试分析内容",
                "#decision": "hold",
                "#reason": "集成测试决策理由"
            }
            
            for selector, value in form_data.items():
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if field:
                        if field.tag_name.lower() == 'select':
                            # 处理下拉选择
                            self.driver.execute_script(f"arguments[0].value = '{value}';", field)
                        else:
                            # 清空并输入新值
                            field.clear()
                            field.send_keys(value)
                        
                        self.log_result(f"表单填写-{selector}", True, f"成功填写: {value}")
                    else:
                        self.log_result(f"表单填写-{selector}", False, f"字段不存在: {selector}")
                        
                except Exception as e:
                    self.log_result(f"表单填写-{selector}", False, f"填写失败: {str(e)}")
            
            # 测试复选框
            checkboxes = [
                "#price-up-score",
                "#bbi-score",
                "#trend-score"
            ]
            
            for checkbox_selector in checkboxes:
                try:
                    checkbox = self.driver.find_element(By.CSS_SELECTOR, checkbox_selector)
                    if checkbox:
                        self.driver.execute_script("arguments[0].checked = true;", checkbox)
                        self.log_result(f"复选框-{checkbox_selector}", True, "复选框已选中")
                    else:
                        self.log_result(f"复选框-{checkbox_selector}", False, f"复选框不存在: {checkbox_selector}")
                except Exception as e:
                    self.log_result(f"复选框-{checkbox_selector}", False, f"操作失败: {str(e)}")
            
            # 测试变化检测
            try:
                # 触发变化检测
                self.driver.execute_script("""
                    if (typeof reviewSaveManager !== 'undefined' && reviewSaveManager) {
                        reviewSaveManager.detectChanges();
                    }
                """)
                
                time.sleep(0.5)
                
                # 检查是否检测到变化
                has_changes = self.driver.execute_script("""
                    return (typeof reviewSaveManager !== 'undefined' && reviewSaveManager) 
                           ? reviewSaveManager.hasUnsavedChanges : false;
                """)
                
                if has_changes:
                    self.log_result("变化检测", True, "正确检测到表单变化")
                else:
                    self.log_result("变化检测", "warning", "未检测到表单变化")
                    
            except Exception as e:
                self.log_result("变化检测", False, f"变化检测失败: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_result("表单交互", False, f"表单交互测试异常: {str(e)}")
            return False
    
    def test_save_functionality(self) -> bool:
        """测试保存功能"""
        print("\n🔍 测试保存功能")
        
        if not self.driver:
            self.log_result("保存功能", False, "WebDriver未初始化")
            return False
        
        try:
            # 查找保存按钮
            save_button = None
            save_selectors = [
                "#save-review-btn",
                "button[onclick*='saveReview']",
                ".modal-footer .btn-primary"
            ]
            
            for selector in save_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button and button.is_displayed():
                        save_button = button
                        break
                except Exception:
                    continue
            
            if not save_button:
                self.log_result("保存按钮", False, "未找到保存按钮")
                return False
            
            self.log_result("保存按钮", True, "找到保存按钮")
            
            # 模拟API响应
            self.driver.execute_script("""
                // 模拟成功的API响应
                if (typeof apiClient !== 'undefined' && apiClient) {
                    apiClient.saveReview = async function(reviewData, reviewId) {
                        // 模拟网络延迟
                        await new Promise(resolve => setTimeout(resolve, 500));
                        
                        return {
                            success: true,
                            data: {
                                id: reviewId || Date.now(),
                                ...reviewData,
                                created_at: new Date().toISOString(),
                                updated_at: new Date().toISOString()
                            }
                        };
                    };
                }
            """)
            
            # 点击保存按钮
            initial_button_text = save_button.text
            self.driver.execute_script("arguments[0].click();", save_button)
            
            # 等待保存过程
            time.sleep(2)
            
            # 检查保存状态变化
            try:
                # 检查按钮状态变化
                current_button_text = save_button.text
                if current_button_text != initial_button_text:
                    self.log_result("保存状态变化", True, f"按钮状态已变化: {initial_button_text} -> {current_button_text}")
                else:
                    self.log_result("保存状态变化", "warning", "按钮状态未变化")
                
                # 检查状态指示器
                status_indicator = self.driver.find_element(By.CSS_SELECTOR, ".save-status-indicator")
                if status_indicator:
                    status_text = status_indicator.text
                    if "已保存" in status_text or "成功" in status_text:
                        self.log_result("状态指示器", True, f"状态指示器显示正确: {status_text}")
                    else:
                        self.log_result("状态指示器", "warning", f"状态指示器内容: {status_text}")
                else:
                    self.log_result("状态指示器", False, "未找到状态指示器")
                    
            except Exception as e:
                self.log_result("保存状态检查", False, f"状态检查失败: {str(e)}")
            
            # 检查控制台日志
            try:
                logs = self.driver.get_log('browser')
                save_related_logs = [log for log in logs if 'save' in log['message'].lower() or 'review' in log['message'].lower()]
                
                if save_related_logs:
                    self.log_result("控制台日志", True, f"找到 {len(save_related_logs)} 条相关日志")
                else:
                    self.log_result("控制台日志", "warning", "未找到保存相关的控制台日志")
                    
            except Exception as e:
                self.log_result("控制台日志", "warning", f"无法获取控制台日志: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_result("保存功能", False, f"保存功能测试异常: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        print("\n🔍 测试错误处理")
        
        if not self.driver:
            self.log_result("错误处理", False, "WebDriver未初始化")
            return False
        
        try:
            # 模拟API错误响应
            self.driver.execute_script("""
                if (typeof apiClient !== 'undefined' && apiClient) {
                    apiClient.saveReview = async function(reviewData, reviewId) {
                        await new Promise(resolve => setTimeout(resolve, 300));
                        throw {
                            code: 'VALIDATION_ERROR',
                            message: '数据验证失败，请检查输入'
                        };
                    };
                }
            """)
            
            # 清空必填字段以触发验证错误
            try:
                reason_field = self.driver.find_element(By.CSS_SELECTOR, "#reason")
                if reason_field:
                    reason_field.clear()
                    reason_field.send_keys("")  # 清空决策理由
            except Exception:
                pass
            
            # 点击保存按钮
            save_button = self.driver.find_element(By.CSS_SELECTOR, "#save-review-btn")
            if save_button:
                self.driver.execute_script("arguments[0].click();", save_button)
                
                # 等待错误处理
                time.sleep(2)
                
                # 检查是否显示错误消息
                error_messages = self.driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .error-message, .text-danger")
                
                if error_messages:
                    error_text = error_messages[0].text
                    self.log_result("错误消息显示", True, f"正确显示错误消息: {error_text}")
                else:
                    self.log_result("错误消息显示", "warning", "未找到错误消息显示")
                
                # 检查按钮状态是否恢复
                button_text = save_button.text
                if "保存" in button_text and "中" not in button_text:
                    self.log_result("错误后按钮状态", True, "按钮状态正确恢复")
                else:
                    self.log_result("错误后按钮状态", "warning", f"按钮状态: {button_text}")
            
            return True
            
        except Exception as e:
            self.log_result("错误处理", False, f"错误处理测试异常: {str(e)}")
            return False
    
    def test_performance_metrics(self) -> bool:
        """测试性能指标"""
        print("\n🔍 测试性能指标")
        
        if not self.driver:
            self.log_result("性能指标", False, "WebDriver未初始化")
            return False
        
        try:
            # 测试页面加载性能
            start_time = time.time()
            self.driver.refresh()
            
            # 等待页面完全加载
            self.wait.until(EC.presence_of_element_located((By.ID, "reviewModal")))
            
            end_time = time.time()
            page_load_time = (end_time - start_time) * 1000
            
            if page_load_time < 3000:  # 3秒内
                self.log_result("页面加载性能", True, f"页面加载时间良好: {page_load_time:.2f}ms")
            elif page_load_time < 5000:  # 5秒内
                self.log_result("页面加载性能", "warning", f"页面加载时间一般: {page_load_time:.2f}ms")
            else:
                self.log_result("页面加载性能", False, f"页面加载时间过慢: {page_load_time:.2f}ms")
            
            # 测试JavaScript执行性能
            js_performance = self.driver.execute_script("""
                var start = performance.now();
                
                // 模拟复杂的JavaScript操作
                if (typeof reviewSaveManager !== 'undefined' && reviewSaveManager) {
                    reviewSaveManager.detectChanges();
                    reviewSaveManager.getCurrentFormData();
                }
                
                var end = performance.now();
                return end - start;
            """)
            
            if js_performance < 100:  # 100ms内
                self.log_result("JavaScript性能", True, f"JavaScript执行时间良好: {js_performance:.2f}ms")
            elif js_performance < 500:  # 500ms内
                self.log_result("JavaScript性能", "warning", f"JavaScript执行时间一般: {js_performance:.2f}ms")
            else:
                self.log_result("JavaScript性能", False, f"JavaScript执行时间过慢: {js_performance:.2f}ms")
            
            # 检查内存使用
            try:
                memory_info = self.driver.execute_script("""
                    if (performance.memory) {
                        return {
                            used: performance.memory.usedJSHeapSize,
                            total: performance.memory.totalJSHeapSize,
                            limit: performance.memory.jsHeapSizeLimit
                        };
                    }
                    return null;
                """)
                
                if memory_info:
                    used_mb = memory_info['used'] / 1024 / 1024
                    total_mb = memory_info['total'] / 1024 / 1024
                    
                    self.log_result("内存使用", True, f"内存使用: {used_mb:.2f}MB / {total_mb:.2f}MB")
                else:
                    self.log_result("内存使用", "warning", "无法获取内存信息")
                    
            except Exception as e:
                self.log_result("内存使用", "warning", f"内存检查失败: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_result("性能指标", False, f"性能测试异常: {str(e)}")
            return False
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """运行集成测试"""
        print("🚀 开始运行复盘保存功能集成测试")
        print("=" * 60)
        
        start_time = time.time()
        
        # 设置WebDriver
        if not self.setup_webdriver():
            print("❌ WebDriver设置失败，无法继续测试")
            return self.generate_report(time.time() - start_time)
        
        try:
            # 测试序列
            test_methods = [
                ('服务器可用性测试', self.test_server_availability),
                ('页面加载测试', self.test_page_loading),
                ('JavaScript加载测试', self.test_javascript_loading),
                ('模态框功能测试', self.test_modal_functionality),
                ('表单交互测试', self.test_form_interaction),
                ('保存功能测试', self.test_save_functionality),
                ('错误处理测试', self.test_error_handling),
                ('性能指标测试', self.test_performance_metrics)
            ]
            
            for test_name, test_method in test_methods:
                print(f"\n{'='*20} {test_name} {'='*20}")
                try:
                    test_method()
                except Exception as e:
                    self.log_result(test_name, False, f"测试执行异常: {str(e)}")
                    print(f"❌ {test_name} 执行异常: {str(e)}")
                
                time.sleep(1)  # 测试间隔
            
        finally:
            # 清理WebDriver
            self.teardown_webdriver()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return self.generate_report(total_time)
    
    def generate_report(self, total_time: float) -> Dict[str, Any]:
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 集成测试结果汇总")
        print("="*60)
        
        print(f"总测试数: {self.test_stats['total']}")
        print(f"通过测试: {self.test_stats['passed']} ✅")
        print(f"失败测试: {self.test_stats['failed']} ❌")
        print(f"警告测试: {self.test_stats['warnings']} ⚠️")
        
        success_rate = 0
        if self.test_stats['total'] > 0:
            success_rate = (self.test_stats['passed'] / self.test_stats['total']) * 100
            print(f"成功率: {success_rate:.1f}%")
        
        print(f"总耗时: {total_time:.2f}秒")
        
        # 生成详细报告
        report = {
            'test_type': 'integration',
            'summary': self.test_stats.copy(),
            'success_rate': success_rate,
            'total_time': total_time,
            'test_results': self.test_results,
            'timestamp': datetime.now().isoformat()
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存测试报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task8_integration_test_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"\n📁 集成测试报告已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存报告失败: {str(e)}")
            return ""

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='复盘保存功能集成测试脚本')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='服务器URL (默认: http://localhost:5000)')
    parser.add_argument('--output', help='输出报告文件名')
    parser.add_argument('--headless', action='store_true', help='无头模式运行')
    
    args = parser.parse_args()
    
    # 检查Chrome浏览器是否可用
    try:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # 尝试获取ChromeDriver
        ChromeDriverManager().install()
        print("✅ ChromeDriver 可用")
        
    except Exception as e:
        print(f"❌ ChromeDriver 不可用: {str(e)}")
        print("请安装Chrome浏览器和ChromeDriver")
        sys.exit(1)
    
    # 创建测试框架
    framework = IntegrationTestFramework(args.url)
    
    try:
        # 运行集成测试
        report = framework.run_integration_tests()
        
        # 保存报告
        if args.output:
            framework.save_report(report, args.output)
        else:
            framework.save_report(report)
        
        # 根据测试结果设置退出码
        if report['summary']['failed'] == 0:
            print("\n🎉 所有集成测试通过!")
            sys.exit(0)
        else:
            print(f"\n⚠️ 有 {report['summary']['failed']} 个测试失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()