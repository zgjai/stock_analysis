#!/usr/bin/env python3
"""
前端JavaScript模块功能测试
测试历史交易功能的JavaScript模块是否正常工作
"""

import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class JavaScriptModulesTester:
    def __init__(self):
        self.driver = None
        self.wait = None
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
            self.wait = WebDriverWait(self.driver, 10)
            print("✓ Chrome驱动初始化成功")
            return True
        except Exception as e:
            print(f"✗ Chrome驱动初始化失败: {e}")
            return False
    
    def test_page_load(self):
        """测试页面加载"""
        try:
            self.driver.get(f"{self.base_url}/historical-trades")
            
            # 等待页面标题加载
            self.wait.until(EC.title_contains("历史交易"))
            
            # 检查关键元素是否存在
            elements_to_check = [
                "historical-trades-table",
                "statistics-cards",
                "filters-container"
            ]
            
            for element_id in elements_to_check:
                element = self.driver.find_element(By.ID, element_id)
                if element:
                    print(f"✓ 元素 {element_id} 存在")
                else:
                    print(f"✗ 元素 {element_id} 不存在")
                    return False
            
            self.test_results.append({
                "test": "page_load",
                "status": "passed",
                "message": "页面加载成功"
            })
            return True
            
        except Exception as e:
            print(f"✗ 页面加载测试失败: {e}")
            self.test_results.append({
                "test": "page_load",
                "status": "failed",
                "message": str(e)
            })
            return False
    
    def test_javascript_modules_loaded(self):
        """测试JavaScript模块是否加载"""
        try:
            # 检查全局对象是否存在
            modules_to_check = [
                "HistoricalTradesManager",
                "ReviewEditor", 
                "ReviewViewer",
                "ImageUploader",
                "ValidationUtils",
                "ResponsiveUtils",
                "HistoricalTradesIntegration"
            ]
            
            for module in modules_to_check:
                result = self.driver.execute_script(f"return typeof window.{module} !== 'undefined';")
                if result:
                    print(f"✓ 模块 {module} 已加载")
                else:
                    print(f"✗ 模块 {module} 未加载")
                    return False
            
            self.test_results.append({
                "test": "javascript_modules",
                "status": "passed", 
                "message": "所有JavaScript模块加载成功"
            })
            return True
            
        except Exception as e:
            print(f"✗ JavaScript模块测试失败: {e}")
            self.test_results.append({
                "test": "javascript_modules",
                "status": "failed",
                "message": str(e)
            })
            return False
    
    def test_historical_trades_manager(self):
        """测试历史交易管理器"""
        try:
            # 检查管理器实例是否创建
            manager_exists = self.driver.execute_script(
                "return typeof window.historicalTradesManager !== 'undefined';"
            )
            
            if not manager_exists:
                print("✗ HistoricalTradesManager实例未创建")
                return False
            
            # 测试管理器方法
            methods_to_test = [
                "loadHistoricalTrades",
                "applyFilters",
                "resetFilters",
                "validateFilterInput"
            ]
            
            for method in methods_to_test:
                method_exists = self.driver.execute_script(
                    f"return typeof window.historicalTradesManager.{method} === 'function';"
                )
                
                if method_exists:
                    print(f"✓ 方法 {method} 存在")
                else:
                    print(f"✗ 方法 {method} 不存在")
                    return False
            
            self.test_results.append({
                "test": "historical_trades_manager",
                "status": "passed",
                "message": "历史交易管理器功能正常"
            })
            return True
            
        except Exception as e:
            print(f"✗ 历史交易管理器测试失败: {e}")
            self.test_results.append({
                "test": "historical_trades_manager", 
                "status": "failed",
                "message": str(e)
            })
            return False
    
    def test_form_validation(self):
        """测试表单验证功能"""
        try:
            # 测试筛选表单验证
            stock_code_input = self.driver.find_element(By.ID, "stock-code-filter")
            
            # 输入无效股票代码
            stock_code_input.clear()
            stock_code_input.send_keys("12345")  # 5位数字，应该无效
            
            # 触发验证
            self.driver.execute_script(
                "window.historicalTradesManager.validateFilterInput(arguments[0]);",
                stock_code_input
            )
            
            # 检查是否显示验证错误
            time.sleep(0.5)
            has_error = stock_code_input.get_attribute("class").find("is-invalid") != -1
            
            if has_error:
                print("✓ 表单验证功能正常")
            else:
                print("✗ 表单验证功能异常")
                return False
            
            # 清除输入
            stock_code_input.clear()
            
            self.test_results.append({
                "test": "form_validation",
                "status": "passed",
                "message": "表单验证功能正常"
            })
            return True
            
        except Exception as e:
            print(f"✗ 表单验证测试失败: {e}")
            self.test_results.append({
                "test": "form_validation",
                "status": "failed", 
                "message": str(e)
            })
            return False
    
    def test_responsive_functionality(self):
        """测试响应式功能"""
        try:
            # 测试不同屏幕尺寸
            screen_sizes = [
                (1920, 1080),  # 桌面
                (768, 1024),   # 平板
                (375, 667)     # 手机
            ]
            
            for width, height in screen_sizes:
                self.driver.set_window_size(width, height)
                time.sleep(0.5)
                
                # 检查响应式工具是否正确识别设备类型
                breakpoint = self.driver.execute_script(
                    "return window.responsiveUtils.getCurrentBreakpoint();"
                )
                
                is_mobile = self.driver.execute_script(
                    "return window.responsiveUtils.isMobile();"
                )
                
                print(f"✓ 屏幕尺寸 {width}x{height}: 断点={breakpoint}, 移动端={is_mobile}")
            
            # 恢复默认尺寸
            self.driver.set_window_size(1920, 1080)
            
            self.test_results.append({
                "test": "responsive_functionality",
                "status": "passed",
                "message": "响应式功能正常"
            })
            return True
            
        except Exception as e:
            print(f"✗ 响应式功能测试失败: {e}")
            self.test_results.append({
                "test": "responsive_functionality",
                "status": "failed",
                "message": str(e)
            })
            return False
    
    def test_validation_utils(self):
        """测试验证工具"""
        try:
            # 测试股票代码验证
            valid_code_result = self.driver.execute_script("""
                return window.validationUtils.validate('000001', 'stockCode');
            """)
            
            invalid_code_result = self.driver.execute_script("""
                return window.validationUtils.validate('12345', 'stockCode');
            """)
            
            if valid_code_result['valid'] and not invalid_code_result['valid']:
                print("✓ 验证工具功能正常")
            else:
                print("✗ 验证工具功能异常")
                return False
            
            self.test_results.append({
                "test": "validation_utils",
                "status": "passed",
                "message": "验证工具功能正常"
            })
            return True
            
        except Exception as e:
            print(f"✗ 验证工具测试失败: {e}")
            self.test_results.append({
                "test": "validation_utils",
                "status": "failed",
                "message": str(e)
            })
            return False
    
    def test_error_handling(self):
        """测试错误处理"""
        try:
            # 模拟API错误
            error_handled = self.driver.execute_script("""
                try {
                    const error = new Error('Test error');
                    error.response = { status: 404, data: { message: 'Not found' } };
                    const message = window.historicalTradesManager.handleApiError(error);
                    return message.includes('资源不存在');
                } catch (e) {
                    return false;
                }
            """)
            
            if error_handled:
                print("✓ 错误处理功能正常")
            else:
                print("✗ 错误处理功能异常")
                return False
            
            self.test_results.append({
                "test": "error_handling",
                "status": "passed",
                "message": "错误处理功能正常"
            })
            return True
            
        except Exception as e:
            print(f"✗ 错误处理测试失败: {e}")
            self.test_results.append({
                "test": "error_handling",
                "status": "failed",
                "message": str(e)
            })
            return False
    
    def test_integration(self):
        """测试模块集成"""
        try:
            # 检查集成对象是否存在
            integration_exists = self.driver.execute_script(
                "return typeof window.historicalTradesIntegration !== 'undefined';"
            )
            
            if not integration_exists:
                print("✗ 集成对象不存在")
                return False
            
            # 检查各组件是否正确初始化
            components_initialized = self.driver.execute_script("""
                const integration = window.historicalTradesIntegration;
                return integration.manager !== null && 
                       integration.reviewEditor !== null && 
                       integration.reviewViewer !== null;
            """)
            
            if components_initialized:
                print("✓ 模块集成功能正常")
            else:
                print("✗ 模块集成功能异常")
                return False
            
            self.test_results.append({
                "test": "integration",
                "status": "passed",
                "message": "模块集成功能正常"
            })
            return True
            
        except Exception as e:
            print(f"✗ 模块集成测试失败: {e}")
            self.test_results.append({
                "test": "integration",
                "status": "failed",
                "message": str(e)
            })
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始前端JavaScript模块测试...")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        tests = [
            self.test_page_load,
            self.test_javascript_modules_loaded,
            self.test_historical_trades_manager,
            self.test_form_validation,
            self.test_responsive_functionality,
            self.test_validation_utils,
            self.test_error_handling,
            self.test_integration
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
                time.sleep(1)  # 测试间隔
            except Exception as e:
                print(f"✗ 测试执行失败: {e}")
        
        print("=" * 50)
        print(f"测试完成: {passed_tests}/{total_tests} 通过")
        
        # 保存测试结果
        self.save_test_results()
        
        return passed_tests == total_tests
    
    def save_test_results(self):
        """保存测试结果"""
        try:
            results = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tests": len(self.test_results),
                "passed_tests": len([r for r in self.test_results if r["status"] == "passed"]),
                "failed_tests": len([r for r in self.test_results if r["status"] == "failed"]),
                "results": self.test_results
            }
            
            with open("frontend_javascript_test_results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 测试结果已保存到 frontend_javascript_test_results.json")
            
        except Exception as e:
            print(f"✗ 保存测试结果失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        if self.driver:
            self.driver.quit()
            print("✓ 浏览器驱动已关闭")

def main():
    """主函数"""
    tester = JavaScriptModulesTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"测试执行失败: {e}")
        return 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())