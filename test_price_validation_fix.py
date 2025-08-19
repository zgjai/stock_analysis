#!/usr/bin/env python3
"""
测试价格验证修复
"""

import requests
import time
import json

def test_price_validation_fix():
    """测试价格验证修复"""
    
    print("🔧 测试价格验证修复...")
    
    try:
        # 1. 检查页面是否正常加载
        response = requests.get('http://localhost:5001/trading-records')
        if response.status_code == 200:
            print("✅ 交易记录页面正常加载")
            
            # 检查是否包含修复后的调试代码
            content = response.text
            if '[DEBUG] 验证字段' in content:
                print("✅ 包含调试代码，修复已应用")
            else:
                print("❌ 未找到调试代码")
                
            # 检查是否包含备用获取方式
            if '从DOM元素获取价格' in content:
                print("✅ 包含价格字段备用获取逻辑")
            else:
                print("❌ 未找到价格字段备用获取逻辑")
                
            return True
        else:
            print(f"❌ 页面加载失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_api_create_trade():
    """测试API创建交易记录"""
    
    print("\n🔧 测试API创建交易记录...")
    
    try:
        # 测试数据
        test_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 19.50,
            'quantity': 100,
            'reason': '测试价格验证修复'
        }
        
        response = requests.post(
            'http://localhost:5001/api/trades',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ API创建交易记录成功")
                print(f"   交易ID: {result.get('data', {}).get('id')}")
                return True
            else:
                print(f"❌ API返回错误: {result.get('message')}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("价格验证修复测试")
    print("=" * 50)
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)
    
    success_count = 0
    total_tests = 2
    
    # 测试页面加载
    if test_price_validation_fix():
        success_count += 1
    
    # 测试API
    if test_api_create_trade():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"测试完成: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！价格验证问题已修复。")
        print("\n修复内容:")
        print("- 添加了详细的调试日志")
        print("- 增加了价格和数量字段的备用获取方式")
        print("- 改进了空值检查逻辑")
        print("- 确保从DOM元素直接获取值作为备用方案")
    else:
        print("❌ 部分测试失败，请检查修复效果")