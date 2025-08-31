#!/usr/bin/env python3
"""
测试卖出原因API，验证"见顶信号"选项是否已添加
"""

import requests
import json

def test_sell_reasons_api():
    """测试卖出原因API"""
    try:
        # 测试获取卖出原因API
        response = requests.get('http://localhost:5000/api/trades/config/sell-reasons')
        
        if response.status_code == 200:
            data = response.json()
            sell_reasons = data.get('sell_reasons', [])
            
            print("API响应成功！")
            print(f"卖出原因列表: {sell_reasons}")
            
            if "见顶信号" in sell_reasons:
                print("✓ '见顶信号'选项已成功添加到卖出原因中")
                return True
            else:
                print("✗ '见顶信号'选项未找到")
                return False
        else:
            print(f"✗ API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_sell_reasons_api()
    if success:
        print("\n测试通过！'见顶信号'选项已成功添加到交易记录的卖出操作原因中。")
    else:
        print("\n测试失败！请检查服务器状态或配置。")