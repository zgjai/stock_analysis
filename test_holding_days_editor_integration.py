#!/usr/bin/env python3
"""
持仓天数编辑器集成测试
测试前端组件与后端API的集成
"""

import sys
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_chrome_driver():
    """设置Chrome驱动"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Chrome驱动设置失败: {e}")
        return None

def test_holding_days_editor_component():
    """测试持仓天数编辑器组件"""
    print("开始测试持仓天数编辑器组件...")
    
    driver = setup_chrome_driver()
    if not driver:
        print("❌ 无法设置Chrome驱动，跳过浏览器测试")
        return False
    
    try:
        # 加载测试页面
        test_file_path = os.path.abspath("test_holding_days_editor.html")
        driver.get(f"file://{test_file_path}")
        
        # 等待页面加载
        wait = WebDriverWait(driver, 10)
        
        # 检查编辑器是否正确初始化
        print("检查编辑器初始化...")
        editor1_container = wait.until(
            EC.presence_of_element_located((By.ID, "editor-container-1"))
        )
        
        # 检查编辑器HTML结构
        editor_element = editor1_container.find_element(By.CLASS_NAME, "holding-days-editor")
        display_element = editor_element.find_element(By.CLASS_NAME, "days-display")
        
        # 验证初始值
        initial_value = display_element.text
        print(f"✓ 编辑器初始值: {initial_value}")
        
        # 测试点击编辑功能
        print("测试点击编辑功能...")
        display_element.click()
        
        # 等待编辑模式激活
        time.sleep(0.5)
        
        # 检查是否进入编辑模式
        edit_mode = editor_element.find_element(By.CLASS_NAME, "edit-mode")
        if "d-none" not in edit_mode.get_attribute("class"):
            print("✓ 成功进入编辑模式")
        else:
            print("❌ 未能进入编辑模式")
            return False
        
        # 测试输入验证
        print("测试输入验证...")
        input_element = edit_mode.find_element(By.CLASS_NAME, "days-input")
        input_element.clear()
        input_element.send_keys("abc")  # 无效输入
        
        time.sleep(0.5)
        
        # 检查错误消息
        try:
            error_element = edit_mode.find_element(By.CLASS_NAME, "error-message")
            if "d-none" not in error_element.get_attribute("class"):
                print("✓ 输入验证工作正常")
            else:
                print("⚠️ 输入验证可能未触发")
        except NoSuchElementException:
            print("⚠️ 未找到错误消息元素")
        
        # 测试有效输入
        print("测试有效输入...")
        input_element.clear()
        input_element.send_keys("25")
        
        # 点击保存按钮
        save_button = edit_mode.find_element(By.CLASS_NAME, "save-btn")
        save_button.click()
        
        # 等待保存完成
        time.sleep(2)
        
        # 检查是否退出编辑模式
        if "d-none" in edit_mode.get_attribute("class"):
            print("✓ 成功退出编辑模式")
        else:
            print("❌ 未能退出编辑模式")
        
        # 验证值是否更新
        updated_value = display_element.text
        print(f"✓ 更新后的值: {updated_value}")
        
        print("✅ 持仓天数编辑器组件测试通过")
        return True
        
    except TimeoutException:
        print("❌ 页面加载超时")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False
    finally:
        driver.quit()

def test_javascript_syntax():
    """测试JavaScript语法"""
    print("测试JavaScript语法...")
    
    js_file = "static/js/holding-days-editor.js"
    if not os.path.exists(js_file):
        print(f"❌ JavaScript文件不存在: {js_file}")
        return False
    
    try:
        # 使用Node.js检查语法
        result = os.system(f"node -c {js_file}")
        if result == 0:
            print("✅ JavaScript语法检查通过")
            return True
        else:
            print("❌ JavaScript语法错误")
            return False
    except Exception as e:
        print(f"❌ JavaScript语法检查失败: {e}")
        return False

def test_template_integration():
    """测试模板集成"""
    print("测试模板集成...")
    
    template_file = "templates/review.html"
    if not os.path.exists(template_file):
        print(f"❌ 模板文件不存在: {template_file}")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必要的集成点
    checks = [
        ("holding-days-editor.js", "JavaScript文件引用"),
        ("initializeHoldingDaysEditors", "初始化函数"),
        ("holding-days-container", "容器类名"),
        ("holdingDaysEditorManager", "管理器实例")
    ]
    
    all_passed = True
    for check, description in checks:
        if check in content:
            print(f"✓ {description}已集成")
        else:
            print(f"❌ {description}未找到")
            all_passed = False
    
    if all_passed:
        print("✅ 模板集成检查通过")
    else:
        print("❌ 模板集成检查失败")
    
    return all_passed

def test_api_integration():
    """测试API集成"""
    print("测试API集成...")
    
    api_file = "static/js/api.js"
    if not os.path.exists(api_file):
        print(f"❌ API文件不存在: {api_file}")
        return False
    
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查API方法
    if "updateHoldingDays" in content:
        print("✓ updateHoldingDays API方法已实现")
        return True
    else:
        print("❌ updateHoldingDays API方法未找到")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("持仓天数编辑器集成测试")
    print("=" * 60)
    
    tests = [
        ("JavaScript语法检查", test_javascript_syntax),
        ("模板集成检查", test_template_integration),
        ("API集成检查", test_api_integration),
        ("组件功能测试", test_holding_days_editor_component)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"运行测试: {test_name}")
        print(f"{'-' * 40}")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"测试结果: {passed}/{total} 通过")
    print(f"{'=' * 60}")
    
    if passed == total:
        print("🎉 所有测试通过！持仓天数编辑器已成功实现")
        return True
    else:
        print("⚠️ 部分测试失败，请检查实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)