#!/usr/bin/env python3
"""
测试股票代码验证修复
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.validators import validate_stock_code
from error_handlers import ValidationError

def test_stock_code_validation():
    """测试股票代码验证功能"""
    print("=== 测试股票代码验证修复 ===")
    
    # 测试用例
    test_cases = [
        # 有效的股票代码
        ("000776", True, "有效的股票代码"),
        ("000001", True, "有效的股票代码"),
        ("600000", True, "有效的股票代码"),
        ("300001", True, "有效的股票代码"),
        
        # 无效的股票代码
        ("", False, "空字符串"),
        ("00077", False, "少于6位"),
        ("0007766", False, "多于6位"),
        ("00077a", False, "包含字母"),
        ("000-77", False, "包含特殊字符"),
        (None, False, "None值"),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for stock_code, should_pass, description in test_cases:
        try:
            result = validate_stock_code(stock_code)
            if should_pass:
                print(f"✓ {description}: {stock_code} - 验证通过")
                success_count += 1
            else:
                print(f"✗ {description}: {stock_code} - 应该失败但通过了")
        except ValidationError as e:
            if not should_pass:
                print(f"✓ {description}: {stock_code} - 正确拒绝: {e.message}")
                success_count += 1
            else:
                print(f"✗ {description}: {stock_code} - 应该通过但失败了: {e.message}")
        except Exception as e:
            print(f"✗ {description}: {stock_code} - 意外错误: {e}")
    
    print(f"\n测试结果: {success_count}/{total_count} 通过")
    return success_count == total_count

if __name__ == '__main__':
    print("开始测试股票代码验证修复...")
    
    validation_ok = test_stock_code_validation()
    
    if validation_ok:
        print("\n🎉 股票代码验证修复成功！")
        print("\n修复说明:")
        print("- 修复了 utils/validators.py 中 validate_stock_code 函数的正则表达式语法错误")
        print("- 原来的正则表达式缺少结束符号，导致验证失败")
        print("- 现在股票代码验证应该正常工作")
        print("\n问题原因:")
        print("- 前端表单正确填写了股票代码 000776")
        print("- 但后端验证器因为正则表达式语法错误而无法正确验证")
        print("- 修复后，000776 这样的6位数字股票代码应该能正常通过验证")
    else:
        print("\n❌ 还有问题需要解决")
        sys.exit(1)