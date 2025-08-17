#!/usr/bin/env python3
"""
验证交易记录页面修复
"""

import requests
import json
import time

def test_trading_records_page():
    """测试交易记录页面"""
    
    base_url = 'http://localhost:8080'
    
    print("测试交易记录页面...")
    
    try:
        # 1. 测试页面加载
        print("1. 测试页面加载...")
        response = requests.get(f'{base_url}/trading-records', timeout=10)
        
        if response.status_code == 200:
            print("   ✓ 页面加载成功")
            
            # 检查页面内容
            content = response.text
            
            # 检查关键元素
            checks = [
                ('交易记录表格', 'id="trades-table-body"'),
                ('添加交易按钮', 'id="addTradeModal"'),
                ('JavaScript管理器', 'TradingRecordsManager'),
                ('API客户端', 'apiClient'),
                ('表单验证', 'FormValidator'),
            ]
            
            for name, pattern in checks:
                if pattern in content:
                    print(f"   ✓ {name}: 存在")
                else:
                    print(f"   ✗ {name}: 缺失")
        else:
            print(f"   ✗ 页面加载失败: {response.status_code}")
            return False
        
        # 2. 测试API端点
        print("\n2. 测试API端点...")
        
        api_tests = [
            ('/api/trades', '获取交易记录'),
            ('/api/trades/config/buy-reasons', '获取买入原因'),
            ('/api/trades/config/sell-reasons', '获取卖出原因'),
        ]
        
        for endpoint, name in api_tests:
            try:
                api_response = requests.get(f'{base_url}{endpoint}', timeout=5)
                if api_response.status_code == 200:
                    data = api_response.json()
                    if data.get('success'):
                        print(f"   ✓ {name}: 成功")
                    else:
                        print(f"   ⚠ {name}: API返回失败 - {data.get('error', {}).get('message', '未知错误')}")
                else:
                    print(f"   ✗ {name}: HTTP {api_response.status_code}")
            except Exception as e:
                print(f"   ✗ {name}: 异常 - {e}")
        
        # 3. 测试JavaScript文件
        print("\n3. 测试JavaScript文件...")
        
        js_files = [
            '/static/js/api.js',
            '/static/js/utils.js',
            '/static/js/form-validation.js',
            '/static/js/main.js'
        ]
        
        for js_file in js_files:
            try:
                js_response = requests.get(f'{base_url}{js_file}', timeout=5)
                if js_response.status_code == 200:
                    print(f"   ✓ {js_file}: 可访问 ({len(js_response.text)} 字符)")
                else:
                    print(f"   ✗ {js_file}: HTTP {js_response.status_code}")
            except Exception as e:
                print(f"   ✗ {js_file}: 异常 - {e}")
        
        return True
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        return False

def test_api_functionality():
    """测试API功能"""
    
    base_url = 'http://localhost:8080'
    
    print("\n测试API功能...")
    
    try:
        # 测试获取交易记录
        print("1. 测试获取交易记录...")
        response = requests.get(f'{base_url}/api/trades', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                trades = data.get('data', {}).get('trades', [])
                total = data.get('data', {}).get('total', 0)
                print(f"   ✓ 成功获取 {len(trades)} 条记录 (总计: {total})")
                
                # 显示前几条记录
                if trades:
                    print("   前3条记录:")
                    for i, trade in enumerate(trades[:3]):
                        print(f"     {i+1}. {trade.get('stock_code')} {trade.get('stock_name')} - {trade.get('trade_type')} - ¥{trade.get('price')}")
                
            else:
                print(f"   ✗ API返回失败: {data.get('error', {}).get('message', '未知错误')}")
        else:
            print(f"   ✗ HTTP错误: {response.status_code}")
        
        # 测试配置API
        print("\n2. 测试配置API...")
        
        config_apis = [
            ('/api/trades/config/buy-reasons', 'buy_reasons'),
            ('/api/trades/config/sell-reasons', 'sell_reasons')
        ]
        
        for endpoint, key in config_apis:
            response = requests.get(f'{base_url}{endpoint}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    reasons = data.get('data', {}).get(key, [])
                    print(f"   ✓ {key}: {len(reasons)} 个选项")
                    if reasons:
                        print(f"     示例: {', '.join(reasons[:3])}")
                else:
                    print(f"   ✗ {key}: API返回失败")
            else:
                print(f"   ✗ {key}: HTTP {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"API测试过程中出错: {e}")
        return False

def main():
    """主函数"""
    
    print("=" * 50)
    print("交易记录页面修复验证")
    print("=" * 50)
    
    # 等待服务器启动
    print("等待服务器响应...")
    time.sleep(2)
    
    # 运行测试
    page_ok = test_trading_records_page()
    api_ok = test_api_functionality()
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"页面测试: {'✓ 通过' if page_ok else '✗ 失败'}")
    print(f"API测试: {'✓ 通过' if api_ok else '✗ 失败'}")
    
    if page_ok and api_ok:
        print("\n🎉 所有测试通过！交易记录页面已修复。")
        print("\n建议:")
        print("1. 在浏览器中访问 http://localhost:8080/trading-records")
        print("2. 检查页面是否正常加载")
        print("3. 尝试添加一条新的交易记录")
        print("4. 测试筛选和排序功能")
    else:
        print("\n❌ 部分测试失败，需要进一步调试。")
    
    print("=" * 50)

if __name__ == '__main__':
    main()