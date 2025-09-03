#!/usr/bin/env python3
"""
测试表单验证修复
"""
import requests
import json

def test_form_validation_fix():
    """测试表单验证修复是否生效"""
    print("=== 测试表单验证修复 ===")
    
    # 测试数据
    test_data = {
        "stock_code": "000776",
        "stock_name": "广发证券",
        "trade_type": "buy",
        "price": 19.453,
        "quantity": 31100,
        "trade_date": "2025-08-04T12:36",
        "reason": "单针二十战法"
    }
    
    try:
        # 测试API调用
        response = requests.post(
            'http://localhost:5001/api/trades',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"API响应状态: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ API调用成功!")
            print(f"交易ID: {result['data']['id']}")
            print(f"股票: {result['data']['stock_code']} - {result['data']['stock_name']}")
            print(f"价格: ¥{result['data']['price']}")
            print(f"数量: {result['data']['quantity']} 股")
            return True
        else:
            print("❌ API调用失败")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def check_template_changes():
    """检查模板文件的修改"""
    print("\n=== 检查模板修改 ===")
    
    try:
        with open('templates/trading_records.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('novalidate属性', 'novalidate' in content),
            ('移除pattern属性', 'pattern="[0-9]{6}"' not in content),
            ('移除maxlength="6"', 'maxlength="6"' not in content),
            ('修复脚本存在', 'fixFormValidationConflicts' in content)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}: {'通过' if passed else '失败'}")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except FileNotFoundError:
        print("❌ 模板文件不存在")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == '__main__':
    print("开始测试表单验证修复...")
    
    # 检查模板修改
    template_ok = check_template_changes()
    
    # 测试API
    api_ok = test_form_validation_fix()
    
    print("\n=== 测试结果 ===")
    if template_ok and api_ok:
        print("🎉 所有测试通过！表单验证问题已修复")
        print("\n📋 修复内容:")
        print("- 移除了HTML5 pattern验证属性")
        print("- 移除了maxlength限制")
        print("- 添加了novalidate属性")
        print("- 添加了验证冲突修复脚本")
        print("\n✅ 现在可以正常添加买入记录了！")
    else:
        print("❌ 还有问题需要解决")
        if not template_ok:
            print("- 模板修改不完整")
        if not api_ok:
            print("- API测试失败")