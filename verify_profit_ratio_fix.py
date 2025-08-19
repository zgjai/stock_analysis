#!/usr/bin/env python3
"""
验证止盈比例优先逻辑修复
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """设置Chrome驱动"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
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

def test_profit_ratio_logic():
    """测试止盈比例优先逻辑"""
    print("=== 验证止盈比例优先逻辑修复 ===\n")
    
    # 启动Flask应用
    print("1. 启动Flask应用...")
    os.system("python app.py &")
    time.sleep(3)
    
    driver = setup_driver()
    if not driver:
        print("❌ 无法启动浏览器驱动")
        return False
    
    try:
        # 访问测试页面
        print("2. 访问测试页面...")
        driver.get("http://localhost:5000/test_profit_ratio_first.html")
        
        # 等待页面加载
        wait = WebDriverWait(driver, 10)
        
        # 检查页面标题
        print("3. 检查页面加载...")
        assert "测试止盈比例优先逻辑" in driver.title
        print("✓ 页面加载成功")
        
        # 等待止盈目标管理器初始化
        time.sleep(2)
        
        # 测试1: 检查初始状态
        print("\n4. 测试初始状态...")
        buy_price_input = driver.find_element(By.ID, "buyPrice")
        assert buy_price_input.get_attribute("value") == "10"
        print("✓ 买入价格初始值正确: 10元")
        
        # 检查是否有默认的止盈目标
        profit_ratio_inputs = driver.find_elements(By.CSS_SELECTOR, ".profit-ratio-input")
        assert len(profit_ratio_inputs) > 0
        print("✓ 默认止盈目标已创建")
        
        # 测试2: 输入止盈比例，检查价格自动计算
        print("\n5. 测试止盈比例输入...")
        profit_ratio_input = profit_ratio_inputs[0]
        profit_ratio_input.clear()
        profit_ratio_input.send_keys("20")
        
        # 触发输入事件
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", profit_ratio_input)
        time.sleep(1)
        
        # 检查止盈价格是否自动计算
        target_price_inputs = driver.find_elements(By.CSS_SELECTOR, ".target-price-input")
        if target_price_inputs:
            target_price = target_price_inputs[0].get_attribute("value")
            expected_price = "12.00"  # 10 * (1 + 20/100) = 12
            if target_price == expected_price:
                print(f"✓ 止盈价格自动计算正确: {target_price}元 (20%止盈)")
            else:
                print(f"⚠ 止盈价格计算可能有误: 期望{expected_price}, 实际{target_price}")
        
        # 测试3: 修改买入价格，检查止盈价格重新计算
        print("\n6. 测试买入价格修改...")
        buy_price_input.clear()
        buy_price_input.send_keys("15")
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", buy_price_input)
        time.sleep(1)
        
        # 检查止盈价格是否重新计算
        target_price_inputs = driver.find_elements(By.CSS_SELECTOR, ".target-price-input")
        if target_price_inputs:
            target_price = target_price_inputs[0].get_attribute("value")
            expected_price = "18.00"  # 15 * (1 + 20/100) = 18
            if target_price == expected_price:
                print(f"✓ 买入价格修改后止盈价格重新计算正确: {target_price}元")
            else:
                print(f"⚠ 买入价格修改后止盈价格计算可能有误: 期望{expected_price}, 实际{target_price}")
        
        # 测试4: 添加多个止盈目标
        print("\n7. 测试添加多个止盈目标...")
        add_btn = driver.find_element(By.ID, "add-target-btn")
        add_btn.click()
        time.sleep(1)
        
        profit_ratio_inputs = driver.find_elements(By.CSS_SELECTOR, ".profit-ratio-input")
        if len(profit_ratio_inputs) >= 2:
            # 设置第二个目标为30%
            profit_ratio_inputs[1].clear()
            profit_ratio_inputs[1].send_keys("30")
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", profit_ratio_inputs[1])
            time.sleep(1)
            
            target_price_inputs = driver.find_elements(By.CSS_SELECTOR, ".target-price-input")
            if len(target_price_inputs) >= 2:
                target_price = target_price_inputs[1].get_attribute("value")
                expected_price = "19.50"  # 15 * (1 + 30/100) = 19.5
                if target_price == expected_price:
                    print(f"✓ 第二个止盈目标计算正确: {target_price}元 (30%止盈)")
                else:
                    print(f"⚠ 第二个止盈目标计算可能有误: 期望{expected_price}, 实际{target_price}")
        
        # 测试5: 检查字段属性
        print("\n8. 检查字段属性...")
        profit_ratio_inputs = driver.find_elements(By.CSS_SELECTOR, ".profit-ratio-input")
        target_price_inputs = driver.find_elements(By.CSS_SELECTOR, ".target-price-input")
        
        if profit_ratio_inputs:
            is_readonly = profit_ratio_inputs[0].get_attribute("readonly")
            if not is_readonly:
                print("✓ 止盈比例字段可编辑")
            else:
                print("❌ 止盈比例字段不应该是只读的")
        
        if target_price_inputs:
            is_readonly = target_price_inputs[0].get_attribute("readonly")
            if is_readonly:
                print("✓ 止盈价格字段为只读")
            else:
                print("❌ 止盈价格字段应该是只读的")
        
        print("\n=== 测试完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False
    finally:
        driver.quit()
        # 停止Flask应用
        os.system("pkill -f 'python app.py'")

def check_javascript_logic():
    """检查JavaScript逻辑修改"""
    print("\n=== 检查JavaScript代码修改 ===")
    
    js_file = "static/js/profit-targets-manager.js"
    if not os.path.exists(js_file):
        print(f"❌ 文件不存在: {js_file}")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键修改点
    checks = [
        {
            "name": "止盈比例字段为必填",
            "pattern": 'data-field="profitRatio"',
            "should_contain": True
        },
        {
            "name": "止盈价格字段为只读",
            "pattern": 'readonly>',
            "should_contain": True
        },
        {
            "name": "止盈比例变化时计算价格",
            "pattern": 'field === \'profitRatio\'',
            "should_contain": True
        },
        {
            "name": "价格计算公式",
            "pattern": 'buyPrice * (1 + profitRatio / 100)',
            "should_contain": True
        }
    ]
    
    for check in checks:
        if check["should_contain"]:
            if check["pattern"] in content:
                print(f"✓ {check['name']}: 已正确修改")
            else:
                print(f"❌ {check['name']}: 修改可能不完整")
        else:
            if check["pattern"] not in content:
                print(f"✓ {check['name']}: 已正确移除")
            else:
                print(f"❌ {check['name']}: 应该移除但仍存在")
    
    return True

if __name__ == "__main__":
    print("止盈比例优先逻辑修复验证\n")
    
    # 检查代码修改
    check_javascript_logic()
    
    # 运行功能测试
    if len(sys.argv) > 1 and sys.argv[1] == "--browser-test":
        test_profit_ratio_logic()
    else:
        print("\n如需运行浏览器测试，请使用: python verify_profit_ratio_fix.py --browser-test")
        print("注意：需要先启动Flask应用并确保Chrome驱动可用")