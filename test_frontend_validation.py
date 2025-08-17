#!/usr/bin/env python3
"""
前端表单验证和用户体验优化测试脚本
测试任务18的实现：前端表单验证和用户体验优化
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FrontendValidationTester:
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:5000"
        self.test_results = []
        
    def setup_driver(self):
        """设置Chrome驱动"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"❌ 无法启动Chrome驱动: {e}")
            return False
    
    def start_server(self):
        """启动Flask服务器"""
        try:
            # 检查服务器是否已经运行
            import requests
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ 服务器已在运行")
                return True
        except:
            pass
        
        print("🚀 启动Flask服务器...")
        try:
            # 启动服务器进程
            self.server_process = subprocess.Popen(
                [sys.executable, "run.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服务器启动
            time.sleep(5)
            
            # 验证服务器是否启动成功
            import requests
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                print("✅ 服务器启动成功")
                return True
            else:
                print(f"❌ 服务器响应异常: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 启动服务器失败: {e}")
            return False
    
    def test_form_validation_scripts_loaded(self):
        """测试表单验证脚本是否正确加载"""
        print("\n📋 测试1: 验证脚本加载")
        
        try:
            self.driver.get(f"{self.base_url}/trading-records")
            
            # 检查必要的JavaScript对象是否存在
            scripts_to_check = [
                "typeof FormValidator !== 'undefined'",
                "typeof FormEnhancer !== 'undefined'",
                "typeof UXUtils !== 'undefined'",
                "typeof FormUtils !== 'undefined'",
                "typeof Validators !== 'undefined'"
            ]
            
            for script in scripts_to_check:
                result = self.driver.execute_script(f"return {script}")
                if result:
                    print(f"  ✅ {script.split()[1]} 已加载")
                else:
                    print(f"  ❌ {script.split()[1]} 未加载")
                    self.test_results.append(f"脚本加载失败: {script}")
                    
            return True
            
        except Exception as e:
            print(f"  ❌ 脚本加载测试失败: {e}")
            self.test_results.append(f"脚本加载测试失败: {e}")
            return False
    
    def test_real_time_validation(self):
        """测试实时表单验证"""
        print("\n📋 测试2: 实时表单验证")
        
        try:
            self.driver.get(f"{self.base_url}/trading-records")
            
            # 点击添加交易按钮
            add_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-bs-target='#addTradeModal']"))
            )
            add_btn.click()
            
            # 等待模态框出现
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "addTradeModal"))
            )
            
            # 测试股票代码验证
            stock_code_input = self.driver.find_element(By.ID, "stock-code")
            
            # 输入无效的股票代码
            stock_code_input.clear()
            stock_code_input.send_keys("123")  # 无效：少于6位
            stock_code_input.click()
            
            # 点击其他地方触发blur事件
            self.driver.find_element(By.ID, "stock-name").click()
            
            time.sleep(1)  # 等待验证
            
            # 检查是否显示错误状态
            if "is-invalid" in stock_code_input.get_attribute("class"):
                print("  ✅ 股票代码实时验证正常")
            else:
                print("  ❌ 股票代码实时验证失败")
                self.test_results.append("股票代码实时验证失败")
            
            # 输入有效的股票代码
            stock_code_input.clear()
            stock_code_input.send_keys("000001")  # 有效：6位数字
            self.driver.find_element(By.ID, "stock-name").click()
            
            time.sleep(1)  # 等待验证
            
            # 检查是否显示成功状态
            if "is-valid" in stock_code_input.get_attribute("class"):
                print("  ✅ 股票代码成功状态显示正常")
            else:
                print("  ❌ 股票代码成功状态显示失败")
                self.test_results.append("股票代码成功状态显示失败")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 实时验证测试失败: {e}")
            self.test_results.append(f"实时验证测试失败: {e}")
            return False
    
    def test_form_submission_validation(self):
        """测试表单提交验证"""
        print("\n📋 测试3: 表单提交验证")
        
        try:
            # 确保在交易记录页面
            self.driver.get(f"{self.base_url}/trading-records")
            
            # 点击添加交易按钮
            add_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-bs-target='#addTradeModal']"))
            )
            add_btn.click()
            
            # 等待模态框出现
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "addTradeModal"))
            )
            
            # 尝试提交空表单
            save_btn = self.driver.find_element(By.ID, "save-trade-btn")
            save_btn.click()
            
            time.sleep(2)  # 等待验证
            
            # 检查是否显示验证错误
            invalid_fields = self.driver.find_elements(By.CSS_SELECTOR, ".is-invalid")
            if len(invalid_fields) > 0:
                print(f"  ✅ 表单提交验证正常，发现 {len(invalid_fields)} 个错误字段")
            else:
                print("  ❌ 表单提交验证失败，未发现错误字段")
                self.test_results.append("表单提交验证失败")
            
            # 检查是否显示错误反馈
            error_feedbacks = self.driver.find_elements(By.CSS_SELECTOR, ".invalid-feedback")
            if len(error_feedbacks) > 0:
                print(f"  ✅ 错误反馈显示正常，共 {len(error_feedbacks)} 条")
            else:
                print("  ❌ 错误反馈显示失败")
                self.test_results.append("错误反馈显示失败")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 表单提交验证测试失败: {e}")
            self.test_results.append(f"表单提交验证测试失败: {e}")
            return False
    
    def test_loading_states(self):
        """测试加载状态和进度指示器"""
        print("\n📋 测试4: 加载状态和进度指示器")
        
        try:
            self.driver.get(f"{self.base_url}/trading-records")
            
            # 测试页面加载状态
            loading_elements = self.driver.find_elements(By.CSS_SELECTOR, ".spinner-border")
            if len(loading_elements) > 0:
                print("  ✅ 发现加载指示器")
            else:
                print("  ⚠️  未发现加载指示器（可能已加载完成）")
            
            # 测试Toast容器是否存在
            toast_container = self.driver.find_element(By.ID, "toast-container")
            if toast_container:
                print("  ✅ Toast容器存在")
            else:
                print("  ❌ Toast容器不存在")
                self.test_results.append("Toast容器不存在")
            
            # 测试加载模态框是否存在
            loading_modal = self.driver.find_element(By.ID, "loadingModal")
            if loading_modal:
                print("  ✅ 加载模态框存在")
            else:
                print("  ❌ 加载模态框不存在")
                self.test_results.append("加载模态框不存在")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 加载状态测试失败: {e}")
            self.test_results.append(f"加载状态测试失败: {e}")
            return False
    
    def test_responsive_design(self):
        """测试响应式设计"""
        print("\n📋 测试5: 响应式设计")
        
        try:
            self.driver.get(f"{self.base_url}/trading-records")
            
            # 测试桌面视图
            self.driver.set_window_size(1920, 1080)
            time.sleep(1)
            
            sidebar = self.driver.find_element(By.ID, "sidebar")
            if sidebar.is_displayed():
                print("  ✅ 桌面视图侧边栏显示正常")
            else:
                print("  ❌ 桌面视图侧边栏显示异常")
                self.test_results.append("桌面视图侧边栏显示异常")
            
            # 测试移动视图
            self.driver.set_window_size(375, 667)  # iPhone尺寸
            time.sleep(1)
            
            # 检查侧边栏是否隐藏
            sidebar_classes = sidebar.get_attribute("class")
            print(f"  📱 移动视图侧边栏类: {sidebar_classes}")
            
            # 检查是否有响应式类
            main_content = self.driver.find_element(By.CSS_SELECTOR, ".main-content")
            if main_content:
                print("  ✅ 主内容区域存在")
            else:
                print("  ❌ 主内容区域不存在")
                self.test_results.append("主内容区域不存在")
            
            # 恢复桌面尺寸
            self.driver.set_window_size(1920, 1080)
            
            return True
            
        except Exception as e:
            print(f"  ❌ 响应式设计测试失败: {e}")
            self.test_results.append(f"响应式设计测试失败: {e}")
            return False
    
    def test_user_feedback_messages(self):
        """测试用户反馈消息"""
        print("\n📋 测试6: 用户反馈消息")
        
        try:
            self.driver.get(f"{self.base_url}/trading-records")
            
            # 测试JavaScript消息函数
            test_script = """
                try {
                    UXUtils.showSuccess('测试成功消息');
                    UXUtils.showError('测试错误消息');
                    UXUtils.showWarning('测试警告消息');
                    UXUtils.showInfo('测试信息消息');
                    return true;
                } catch (e) {
                    return false;
                }
            """
            
            result = self.driver.execute_script(test_script)
            if result:
                print("  ✅ 消息函数执行成功")
                
                # 等待Toast出现
                time.sleep(2)
                
                # 检查Toast是否出现
                toasts = self.driver.find_elements(By.CSS_SELECTOR, ".toast")
                if len(toasts) > 0:
                    print(f"  ✅ 发现 {len(toasts)} 个Toast消息")
                else:
                    print("  ❌ 未发现Toast消息")
                    self.test_results.append("Toast消息显示失败")
            else:
                print("  ❌ 消息函数执行失败")
                self.test_results.append("消息函数执行失败")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 用户反馈消息测试失败: {e}")
            self.test_results.append(f"用户反馈消息测试失败: {e}")
            return False
    
    def test_character_counter(self):
        """测试字符计数器"""
        print("\n📋 测试7: 字符计数器")
        
        try:
            self.driver.get(f"{self.base_url}/trading-records")
            
            # 点击添加交易按钮
            add_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-bs-target='#addTradeModal']"))
            )
            add_btn.click()
            
            # 等待模态框出现
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "addTradeModal"))
            )
            
            # 查找有maxlength属性的字段
            notes_field = self.driver.find_element(By.ID, "notes")
            if notes_field.get_attribute("maxlength"):
                print("  ✅ 发现带maxlength的字段")
                
                # 输入一些文本
                notes_field.clear()
                notes_field.send_keys("这是一个测试备注")
                
                time.sleep(1)  # 等待字符计数器更新
                
                # 查找字符计数器
                char_counter = self.driver.find_elements(By.CSS_SELECTOR, ".char-counter")
                if len(char_counter) > 0:
                    print("  ✅ 字符计数器显示正常")
                    print(f"  📊 计数器内容: {char_counter[0].text}")
                else:
                    print("  ❌ 字符计数器未显示")
                    self.test_results.append("字符计数器未显示")
            else:
                print("  ⚠️  未发现带maxlength的字段")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 字符计数器测试失败: {e}")
            self.test_results.append(f"字符计数器测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始前端表单验证和用户体验优化测试")
        print("=" * 60)
        
        # 启动服务器
        if not self.start_server():
            return False
        
        # 设置驱动
        if not self.setup_driver():
            return False
        
        try:
            # 运行所有测试
            tests = [
                self.test_form_validation_scripts_loaded,
                self.test_real_time_validation,
                self.test_form_submission_validation,
                self.test_loading_states,
                self.test_responsive_design,
                self.test_user_feedback_messages,
                self.test_character_counter
            ]
            
            passed_tests = 0
            total_tests = len(tests)
            
            for test in tests:
                try:
                    if test():
                        passed_tests += 1
                except Exception as e:
                    print(f"  ❌ 测试执行异常: {e}")
                    self.test_results.append(f"测试执行异常: {e}")
            
            # 输出测试结果
            print("\n" + "=" * 60)
            print("📊 测试结果汇总")
            print(f"✅ 通过测试: {passed_tests}/{total_tests}")
            
            if self.test_results:
                print(f"❌ 失败项目: {len(self.test_results)}")
                for i, error in enumerate(self.test_results, 1):
                    print(f"   {i}. {error}")
            else:
                print("🎉 所有测试都通过了！")
            
            return len(self.test_results) == 0
            
        finally:
            if self.driver:
                self.driver.quit()
            
            # 停止服务器
            if hasattr(self, 'server_process'):
                self.server_process.terminate()
                self.server_process.wait()

def main():
    """主函数"""
    tester = FrontendValidationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 前端表单验证和用户体验优化测试全部通过！")
        print("✅ 任务18实现成功")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查实现")
        return 1

if __name__ == "__main__":
    exit(main())