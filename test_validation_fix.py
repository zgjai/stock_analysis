#!/usr/bin/env python3
"""
测试持仓股票验证修复
"""

import subprocess
import time
import requests
import json

def test_validation_fix():
    """测试验证修复是否有效"""
    print("🧪 开始测试持仓股票验证修复...")
    
    # 启动测试服务器
    print("启动测试服务器...")
    try:
        # 检查服务器是否已经运行
        response = requests.get('http://localhost:8000/test_holding_stock_validation_fix.html', timeout=2)
        print("✅ 测试服务器已运行")
    except requests.exceptions.RequestException:
        print("❌ 测试服务器未运行，请手动启动：python -m http.server 8000")
        return False
    
    print("\n📋 测试步骤：")
    print("1. 打开浏览器访问: http://localhost:8000/test_holding_stock_validation_fix.html")
    print("2. 选择交易类型为'买入'")
    print("3. 填写以下测试数据：")
    print("   - 股票代码: 000001")
    print("   - 股票名称: 平安银行")
    print("   - 价格: 10.50")
    print("   - 数量: 1000")
    print("   - 操作原因: 技术分析")
    print("4. 点击'测试简单验证器'按钮")
    print("5. 检查验证结果是否通过（不应该有holding_stock相关的错误）")
    
    print("\n🔍 预期结果：")
    print("- 验证应该通过（✅ 通过）")
    print("- 表单数据中不应该包含holding_stock字段")
    print("- 不应该出现'请选择选择持仓股票'的错误信息")
    
    print("\n🚀 如果测试通过，说明修复成功！")
    return True

if __name__ == "__main__":
    test_validation_fix()