#!/usr/bin/env python3
"""
调试 take_profit_ratio 验证问题
"""

def validate_ratio(ratio, field_name):
    """验证比例值（0-1之间）"""
    print(f"验证 {field_name}: {ratio} (类型: {type(ratio)})")
    
    if ratio is None:
        print(f"  -> {field_name} 为 None，返回 None")
        return None
    
    try:
        ratio_float = float(ratio)
        print(f"  -> 转换为 float: {ratio_float}")
        
        # 智能转换：如果值大于1，假设是百分比形式，自动转换为小数
        if ratio_float > 1:
            # 如果值在1-100之间，假设是百分比，除以100
            if ratio_float <= 100:
                print(f"  -> 🔄 检测到百分比格式，自动转换: {ratio_float} -> {ratio_float / 100}")
                ratio_float = ratio_float / 100
            else:
                # 如果值大于100，可能是错误输入
                print(f"  -> ❌ {field_name} 值过大: {ratio_float}")
                raise ValueError(f"{field_name}值过大，请输入0-100之间的百分比或0-1之间的小数")
        
        if ratio_float < 0 or ratio_float > 1:
            print(f"  -> ❌ {field_name} 超出范围 (0-1): {ratio_float}")
            raise ValueError(f"{field_name}必须在0-1之间")
        
        print(f"  -> ✅ {field_name} 验证通过: {ratio_float}")
        return ratio_float
    except (ValueError, TypeError) as e:
        print(f"  -> ❌ {field_name} 格式错误: {e}")
        raise ValueError(f"{field_name}格式不正确")

def test_ratio_validation():
    """测试不同的比例值"""
    test_cases = [
        # (输入值, 描述)
        (None, "None值"),
        ("", "空字符串"),
        ("0", "0%"),
        ("0.1", "10% (正确格式)"),
        ("0.5", "50% (正确格式)"),
        ("1.0", "100% (正确格式)"),
        ("10", "10 (错误：应该是0.1)"),
        ("50", "50 (错误：应该是0.5)"),
        ("100", "100 (错误：应该是1.0)"),
        ("1.5", "150% (超出范围)"),
        ("abc", "非数字字符串"),
        (0.1, "0.1 (float类型)"),
        (10, "10 (int类型)"),
    ]
    
    print("=== 测试 take_profit_ratio 验证逻辑 ===\n")
    
    for value, description in test_cases:
        print(f"测试用例: {description}")
        try:
            result = validate_ratio(value, "take_profit_ratio")
            print(f"  结果: {result}\n")
        except Exception as e:
            print(f"  异常: {e}\n")

if __name__ == "__main__":
    test_ratio_validation()
    
    print("\n=== 分析问题 ===")
    print("根据错误信息 'take_profit_ratio格式不正确'，可能的原因：")
    print("1. 前端传递的值超出了 0-1 范围（比如传递了 10 而不是 0.1）")
    print("2. 前端传递的值格式不正确（比如传递了非数字字符串）")
    print("3. 数据在传输过程中被错误处理")
    
    print("\n=== 建议的修复方案 ===")
    print("1. 检查前端数据转换逻辑，确保百分比正确转换为小数")
    print("2. 在后端添加更详细的错误日志，记录实际接收到的值")
    print("3. 考虑在验证器中添加自动转换逻辑（如果值 > 1，自动除以100）")