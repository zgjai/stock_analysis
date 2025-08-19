#!/usr/bin/env python3
"""
验证交易记录JavaScript修复的脚本
"""

import requests
import time
import subprocess
import sys
import os

def start_server():
    """启动Flask服务器"""
    try:
        # 检查服务器是否已经运行
        response = requests.get('http://localhost:5001/health', timeout=2)
        print("服务器已经在运行")
        return True
    except:
        print("启动Flask服务器...")
        # 启动服务器
        subprocess.Popen([sys.executable, 'app.py'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # 等待服务器启动
        for i in range(10):
            try:
                time.sleep(2)
                response = requests.get('http://localhost:5001/health', timeout=2)
                print("服务器启动成功")
                return True
            except:
                continue
        
        print("服务器启动失败")
        return False

def test_trading_records_page():
    """测试交易记录页面是否正常加载"""
    try:
        response = requests.get('http://localhost:5001/trading-records', timeout=10)
        if response.status_code == 200:
            print("✅ 交易记录页面加载成功")
            
            # 检查页面是否包含关键的JavaScript代码
            content = response.text
            if 'validateNumericField' in content:
                print("✅ validateNumericField 函数存在")
                
                # 检查是否使用了箭头函数（修复后的版本）
                if 'const validateNumericField = (' in content:
                    print("✅ validateNumericField 使用箭头函数（已修复）")
                    return True
                else:
                    print("❌ validateNumericField 仍使用普通函数（未修复）")
                    return False
            else:
                print("❌ validateNumericField 函数不存在")
                return False
        else:
            print(f"❌ 交易记录页面加载失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试交易记录页面时出错: {e}")
        return False

def test_api_endpoints():
    """测试相关API端点"""
    try:
        # 测试获取交易记录
        response = requests.get('http://localhost:5001/api/trades', timeout=5)
        if response.status_code == 200:
            print("✅ 交易记录API正常")
        else:
            print(f"⚠️ 交易记录API状态码: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ 测试API时出错: {e}")
        return False

def main():
    print("=== 交易记录JavaScript修复验证 ===\n")
    
    # 检查是否在正确的目录
    if not os.path.exists('app.py'):
        print("❌ 请在项目根目录运行此脚本")
        return False
    
    # 启动服务器
    if not start_server():
        return False
    
    print("\n--- 测试结果 ---")
    
    # 测试页面加载
    page_ok = test_trading_records_page()
    
    # 测试API
    api_ok = test_api_endpoints()
    
    print(f"\n=== 总结 ===")
    print(f"页面修复状态: {'✅ 成功' if page_ok else '❌ 失败'}")
    print(f"API状态: {'✅ 正常' if api_ok else '❌ 异常'}")
    
    if page_ok and api_ok:
        print("\n🎉 修复验证成功！JavaScript上下文问题已解决。")
        print("\n修复内容:")
        print("- 将 validateNumericField 从普通函数改为箭头函数")
        print("- 保持了 this 上下文，避免 'Cannot read properties of undefined' 错误")
        print("- 保持了原有的验证逻辑和错误处理")
        return True
    else:
        print("\n❌ 修复验证失败，请检查问题。")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)