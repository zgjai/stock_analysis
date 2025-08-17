#!/usr/bin/env python3
"""
简单的前端功能测试脚本
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_trading_records_page():
    """测试交易记录页面是否可以正常访问"""
    try:
        response = requests.get(f"{BASE_URL}/trading-records")
        if response.status_code == 200:
            print("✓ 交易记录页面访问正常")
            
            # 检查页面是否包含必要的元素
            content = response.text
            required_elements = [
                'id="trades-table-body"',
                'id="addTradeModal"',
                'id="correctTradeModal"',
                'id="correctionHistoryModal"',
                'class="TradingRecordsManager"',
                'function filterTrades()',
                'function resetFilter()',
                'function refreshTrades()'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"✗ 页面缺少以下元素: {missing_elements}")
                return False
            else:
                print("✓ 页面包含所有必要的元素")
                return True
        else:
            print(f"✗ 页面访问失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 页面访问异常: {e}")
        return False

def test_api_endpoints():
    """测试API端点是否正常工作"""
    try:
        # 测试获取交易记录
        response = requests.get(f"{BASE_URL}/api/trades")
        if response.status_code == 200:
            print("✓ 获取交易记录API正常")
        else:
            print(f"✗ 获取交易记录API失败，状态码: {response.status_code}")
            return False
        
        # 测试获取买入原因配置
        response = requests.get(f"{BASE_URL}/api/trades/config/buy-reasons")
        if response.status_code == 200:
            print("✓ 获取买入原因配置API正常")
        else:
            print(f"✗ 获取买入原因配置API失败，状态码: {response.status_code}")
            return False
        
        # 测试获取卖出原因配置
        response = requests.get(f"{BASE_URL}/api/trades/config/sell-reasons")
        if response.status_code == 200:
            print("✓ 获取卖出原因配置API正常")
        else:
            print(f"✗ 获取卖出原因配置API失败，状态码: {response.status_code}")
            return False
        
        # 测试风险收益计算
        test_data = {
            "buy_price": 10.0,
            "stop_loss_price": 9.0,
            "take_profit_ratio": 0.2,
            "sell_ratio": 0.5
        }
        response = requests.post(f"{BASE_URL}/api/trades/calculate-risk-reward", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            print("✓ 风险收益计算API正常")
        else:
            print(f"✗ 风险收益计算API失败，状态码: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ API测试异常: {e}")
        return False

def test_create_trade():
    """测试创建交易记录"""
    try:
        trade_data = {
            "stock_code": "000001",
            "stock_name": "平安银行",
            "trade_type": "buy",
            "price": 12.50,
            "quantity": 1000,
            "reason": "少妇B1战法",
            "trade_date": datetime.now().isoformat(),
            "notes": "测试交易记录"
        }
        
        response = requests.post(f"{BASE_URL}/api/trades", 
                               json=trade_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 201:
            print("✓ 创建交易记录成功")
            result = response.json()
            trade_id = result['data']['id']
            
            # 测试获取单个交易记录
            response = requests.get(f"{BASE_URL}/api/trades/{trade_id}")
            if response.status_code == 200:
                print("✓ 获取单个交易记录成功")
                
                # 测试删除交易记录
                response = requests.delete(f"{BASE_URL}/api/trades/{trade_id}")
                if response.status_code == 200:
                    print("✓ 删除交易记录成功")
                    return True
                else:
                    print(f"✗ 删除交易记录失败，状态码: {response.status_code}")
                    return False
            else:
                print(f"✗ 获取单个交易记录失败，状态码: {response.status_code}")
                return False
        else:
            print(f"✗ 创建交易记录失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 创建交易记录测试异常: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试交易记录前端功能...")
    print("=" * 50)
    
    tests = [
        ("交易记录页面访问", test_trading_records_page),
        ("API端点测试", test_api_endpoints),
        ("创建交易记录测试", test_create_trade)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n测试: {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"✓ {test_name} 通过")
        else:
            print(f"✗ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！交易记录前端功能实现完成。")
        return True
    else:
        print("❌ 部分测试失败，请检查实现。")
        return False

if __name__ == "__main__":
    main()