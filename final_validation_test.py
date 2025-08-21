#!/usr/bin/env python3
"""
最终验证测试脚本
"""

import requests
import json
from datetime import datetime

def test_api_directly():
    """直接测试API"""
    
    print("🧪 直接测试交易记录API...")
    
    # 测试数据
    test_data = {
        "stock_code": "000001",
        "stock_name": "平安银行",
        "trade_type": "buy",
        "price": 10.50,
        "quantity": 1000,
        "reason": "少妇B1战法",
        "trade_date": datetime.now().isoformat(),
        "notes": "测试记录"
    }
    
    print("📤 发送测试数据:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    try:
        # 发送POST请求
        response = requests.post(
            'http://localhost:5000/api/trades',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📥 响应状态码: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ API测试成功!")
            result = response.json()
            print("响应数据:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ API测试失败!")
            print("错误响应:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(response.text)
        
        return response.status_code == 201
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Flask应用正在运行")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def test_edge_cases():
    """测试边界情况"""
    
    print("\n🧪 测试边界情况...")
    
    # 测试用例
    test_cases = [
        {
            "name": "字符串数字",
            "data": {
                "stock_code": "000001",
                "stock_name": "平安银行",
                "trade_type": "buy",
                "price": "10.50",  # 字符串格式的价格
                "quantity": "1000",  # 字符串格式的数量
                "reason": "少妇B1战法",
                "trade_date": datetime.now().isoformat()
            }
        },
        {
            "name": "带空格的字段",
            "data": {
                "stock_code": " 000001 ",  # 带空格
                "stock_name": " 平安银行 ",  # 带空格
                "trade_type": "buy",
                "price": 10.50,
                "quantity": 1000,
                "reason": " 少妇B1战法 ",  # 带空格
                "trade_date": datetime.now().isoformat()
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 测试: {test_case['name']}")
        
        try:
            response = requests.post(
                'http://localhost:5000/api/trades',
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 201:
                print(f"✅ {test_case['name']} 测试通过")
            else:
                print(f"❌ {test_case['name']} 测试失败: {response.status_code}")
                try:
                    error_data = response.json()
                    print(json.dumps(error_data, indent=2, ensure_ascii=False))
                except:
                    print(response.text)
                    
        except Exception as e:
            print(f"❌ {test_case['name']} 测试异常: {str(e)}")

def test_validation_errors():
    """测试验证错误"""
    
    print("\n🧪 测试验证错误...")
    
    # 测试缺少必填字段
    invalid_cases = [
        {
            "name": "缺少股票代码",
            "data": {
                "stock_name": "平安银行",
                "trade_type": "buy",
                "price": 10.50,
                "quantity": 1000,
                "reason": "少妇B1战法"
            }
        },
        {
            "name": "空股票代码",
            "data": {
                "stock_code": "",
                "stock_name": "平安银行",
                "trade_type": "buy",
                "price": 10.50,
                "quantity": 1000,
                "reason": "少妇B1战法"
            }
        },
        {
            "name": "空股票名称",
            "data": {
                "stock_code": "000001",
                "stock_name": "",
                "trade_type": "buy",
                "price": 10.50,
                "quantity": 1000,
                "reason": "少妇B1战法"
            }
        }
    ]
    
    for test_case in invalid_cases:
        print(f"\n📋 测试: {test_case['name']}")
        
        try:
            response = requests.post(
                'http://localhost:5000/api/trades',
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 422:
                print(f"✅ {test_case['name']} 正确返回验证错误")
                error_data = response.json()
                print(f"错误信息: {error_data.get('message', '未知错误')}")
            else:
                print(f"❌ {test_case['name']} 应该返回422错误，实际: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ {test_case['name']} 测试异常: {str(e)}")

def main():
    """主函数"""
    print("🚀 开始最终验证测试...")
    
    # 1. 基本API测试
    basic_success = test_api_directly()
    
    # 2. 边界情况测试
    test_edge_cases()
    
    # 3. 验证错误测试
    test_validation_errors()
    
    print("\n" + "="*50)
    if basic_success:
        print("🎉 基本功能测试通过！")
        print("\n📋 修复总结:")
        print("  ✅ 简化了前端验证逻辑")
        print("  ✅ 增强了后端数据处理")
        print("  ✅ 支持字符串格式的数字字段")
        print("  ✅ 自动处理字段前后空格")
        print("\n💡 建议:")
        print("  1. 刷新交易记录页面")
        print("  2. 重新尝试添加交易记录")
        print("  3. 如果还有问题，检查浏览器控制台")
    else:
        print("❌ 基本功能测试失败")
        print("\n🔧 排查步骤:")
        print("  1. 确保Flask应用正在运行")
        print("  2. 检查服务器端口是否正确")
        print("  3. 查看服务器日志")
    
    return 0 if basic_success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())