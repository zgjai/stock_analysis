#!/usr/bin/env python3
"""
交易记录页面功能测试
测试交易记录页面的JavaScript修复是否生效
"""

import requests
import json
import time
from datetime import datetime

# 服务器配置
BASE_URL = "http://localhost:5001"

def test_api_endpoints():
    """测试API端点"""
    print("🧪 测试API端点功能")
    print("=" * 60)
    
    endpoints = [
        ("/health", "健康检查"),
        ("/api/trades", "交易记录列表"),
        ("/api/trades/config", "交易配置"),
        ("/api/trades/stats", "交易统计"),
        ("/api/trades/config/buy-reasons", "买入原因配置"),
        ("/api/trades/config/sell-reasons", "卖出原因配置"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: {response.status_code}")
                success_count += 1
            else:
                print(f"❌ {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: 连接错误 - {str(e)}")
    
    print(f"\n📊 API测试结果: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    return success_count == total_count

def test_page_access():
    """测试页面访问"""
    print("\n🌐 测试页面访问")
    print("=" * 60)
    
    pages = [
        ("/", "仪表板"),
        ("/trading-records", "交易记录"),
        ("/stock-pool", "股票池"),
        ("/review", "复盘分析"),
    ]
    
    success_count = 0
    total_count = len(pages)
    
    for page, description in pages:
        try:
            response = requests.get(f"{BASE_URL}{page}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}页面: {response.status_code}")
                success_count += 1
                
                # 检查页面是否包含关键内容
                if "交易记录" in page and "TradingRecordsManager" in response.text:
                    print(f"  ✅ JavaScript类已加载")
                elif "交易记录" in page:
                    print(f"  ⚠️  JavaScript类可能未正确加载")
            else:
                print(f"❌ {description}页面: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}页面: 连接错误 - {str(e)}")
    
    print(f"\n📊 页面访问结果: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    return success_count == total_count

def test_create_trade():
    """测试创建交易记录"""
    print("\n📝 测试创建交易记录")
    print("=" * 60)
    
    # 测试数据
    trade_data = {
        "stock_code": "000001",
        "stock_name": "平安银行",
        "trade_type": "buy",
        "price": 13.50,
        "quantity": 500,
        "trade_date": datetime.now().isoformat(),
        "reason": "技术突破",
        "notes": "测试买入记录"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/trades",
            json=trade_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ 创建交易记录成功")
            print(f"  📋 记录ID: {result.get('data', {}).get('id', 'N/A')}")
            print(f"  💰 股票: {trade_data['stock_code']} - {trade_data['stock_name']}")
            print(f"  📈 类型: {trade_data['trade_type']}")
            print(f"  💵 价格: ¥{trade_data['price']}")
            print(f"  📊 数量: {trade_data['quantity']}")
            return True
        else:
            print(f"❌ 创建交易记录失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  错误信息: {error_data.get('message', '未知错误')}")
            except:
                print(f"  响应内容: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 创建交易记录异常: {str(e)}")
        return False

def test_query_trades():
    """测试查询交易记录"""
    print("\n🔍 测试查询交易记录")
    print("=" * 60)
    
    try:
        # 测试基本查询
        response = requests.get(f"{BASE_URL}/api/trades?page=1&per_page=5", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            trades = result.get('data', {}).get('trades', [])
            total = result.get('data', {}).get('total', 0)
            
            print(f"✅ 查询交易记录成功")
            print(f"  📊 总记录数: {total}")
            print(f"  📋 当前页记录数: {len(trades)}")
            
            if trades:
                print(f"  📈 最新记录:")
                latest = trades[0]
                print(f"    - {latest['stock_code']} {latest['stock_name']}")
                print(f"    - {latest['trade_type']} ¥{latest['price']} x {latest['quantity']}")
                print(f"    - {latest['trade_date']}")
            
            return True
        else:
            print(f"❌ 查询交易记录失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 查询交易记录异常: {str(e)}")
        return False

def test_risk_reward_calculation():
    """测试风险收益计算"""
    print("\n📊 测试风险收益计算")
    print("=" * 60)
    
    calc_data = {
        "buy_price": 10.0,
        "stop_loss_price": 9.0,
        "take_profit_ratio": 0.15,
        "sell_ratio": 0.5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/trades/calculate-risk-reward",
            json=calc_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            print(f"✅ 风险收益计算成功")
            print(f"  💰 买入价格: ¥{calc_data['buy_price']}")
            print(f"  🛑 止损价格: ¥{calc_data['stop_loss_price']}")
            print(f"  📈 止盈比例: {calc_data['take_profit_ratio']*100}%")
            print(f"  📊 卖出比例: {calc_data['sell_ratio']*100}%")
            print(f"  📉 预期亏损比例: {data.get('expected_loss_ratio', 0)*100:.2f}%")
            print(f"  📈 预期收益比例: {data.get('expected_profit_ratio', 0)*100:.2f}%")
            
            return True
        else:
            print(f"❌ 风险收益计算失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 风险收益计算异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 交易记录页面功能测试")
    print("=" * 60)
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 服务器地址: {BASE_URL}")
    print()
    
    # 执行测试
    tests = [
        ("API端点测试", test_api_endpoints),
        ("页面访问测试", test_page_access),
        ("创建交易记录测试", test_create_trade),
        ("查询交易记录测试", test_query_trades),
        ("风险收益计算测试", test_risk_reward_calculation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}执行异常: {str(e)}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n📈 总体成功率: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 测试基本通过，系统功能正常！")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统状态")
        return False

if __name__ == "__main__":
    main()