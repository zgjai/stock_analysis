#!/usr/bin/env python3
"""
测试 take_profit_ratio 修复是否有效
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.validators import validate_ratio

def test_fix():
    """测试修复后的验证器"""
    print("=== 测试 take_profit_ratio 修复 ===\n")
    
    # 模拟用户在界面上输入的值
    test_cases = [
        ("10", "用户输入10%"),
        ("20", "用户输入20%"),
        ("30", "用户输入30%"),
        ("0.1", "用户输入0.1（已经是小数格式）"),
        ("0.2", "用户输入0.2（已经是小数格式）"),
        ("100", "用户输入100%"),
        ("0", "用户输入0%"),
        ("1", "用户输入1%"),
    ]
    
    for value, description in test_cases:
        print(f"测试: {description}")
        try:
            result = validate_ratio(value, "take_profit_ratio")
            print(f"  输入: {value} -> 结果: {result} ✅")
        except Exception as e:
            print(f"  输入: {value} -> 错误: {e} ❌")
        print()
    
    print("=== 测试边界情况 ===\n")
    
    edge_cases = [
        ("101", "超过100%"),
        ("-10", "负数"),
        ("abc", "非数字"),
        ("", "空字符串"),
        (None, "None值"),
    ]
    
    for value, description in edge_cases:
        print(f"测试: {description}")
        try:
            result = validate_ratio(value, "take_profit_ratio")
            print(f"  输入: {value} -> 结果: {result} ⚠️")
        except Exception as e:
            print(f"  输入: {value} -> 错误: {e} ✅ (预期错误)")
        print()

if __name__ == "__main__":
    test_fix()