#!/usr/bin/env python3
"""
测试止盈比例优先逻辑的验证脚本
"""

def test_profit_calculation():
    """测试止盈价格计算逻辑"""
    print("=== 测试止盈比例优先逻辑 ===\n")
    
    # 测试用例
    test_cases = [
        {
            "buy_price": 10.00,
            "profit_ratio": 20.0,  # 20%
            "expected_target_price": 12.00
        },
        {
            "buy_price": 15.50,
            "profit_ratio": 30.0,  # 30%
            "expected_target_price": 20.15
        },
        {
            "buy_price": 8.88,
            "profit_ratio": 15.5,  # 15.5%
            "expected_target_price": 10.26
        }
    ]
    
    print("测试止盈价格计算公式：止盈价格 = 买入价格 × (1 + 止盈比例/100)")
    print("-" * 60)
    
    for i, case in enumerate(test_cases, 1):
        buy_price = case["buy_price"]
        profit_ratio = case["profit_ratio"]
        expected = case["expected_target_price"]
        
        # 计算止盈价格
        calculated_target_price = buy_price * (1 + profit_ratio / 100)
        
        print(f"测试用例 {i}:")
        print(f"  买入价格: ¥{buy_price}")
        print(f"  止盈比例: {profit_ratio}%")
        print(f"  预期止盈价格: ¥{expected}")
        print(f"  计算止盈价格: ¥{calculated_target_price:.2f}")
        print(f"  计算正确: {'✓' if abs(calculated_target_price - expected) < 0.01 else '✗'}")
        print()

def test_reverse_calculation():
    """测试反向计算（从价格计算比例）- 旧逻辑"""
    print("=== 旧逻辑：从止盈价格计算止盈比例 ===\n")
    
    test_cases = [
        {
            "buy_price": 10.00,
            "target_price": 12.00,
            "expected_profit_ratio": 20.0
        },
        {
            "buy_price": 15.50,
            "target_price": 20.15,
            "expected_profit_ratio": 30.0
        }
    ]
    
    print("旧计算公式：止盈比例 = (止盈价格 - 买入价格) / 买入价格 × 100")
    print("-" * 60)
    
    for i, case in enumerate(test_cases, 1):
        buy_price = case["buy_price"]
        target_price = case["target_price"]
        expected = case["expected_profit_ratio"]
        
        # 计算止盈比例
        calculated_profit_ratio = ((target_price - buy_price) / buy_price) * 100
        
        print(f"测试用例 {i}:")
        print(f"  买入价格: ¥{buy_price}")
        print(f"  止盈价格: ¥{target_price}")
        print(f"  预期止盈比例: {expected}%")
        print(f"  计算止盈比例: {calculated_profit_ratio:.2f}%")
        print(f"  计算正确: {'✓' if abs(calculated_profit_ratio - expected) < 0.01 else '✗'}")
        print()

def demonstrate_new_logic():
    """演示新逻辑的优势"""
    print("=== 新逻辑的优势演示 ===\n")
    
    print("场景：用户想要设置多个止盈目标")
    print("- 第一个目标：10%止盈")
    print("- 第二个目标：20%止盈") 
    print("- 第三个目标：30%止盈")
    print()
    
    buy_price = 10.00
    profit_ratios = [10, 20, 30]
    
    print(f"买入价格: ¥{buy_price}")
    print("用户输入止盈比例，系统自动计算止盈价格：")
    print("-" * 40)
    
    for i, ratio in enumerate(profit_ratios, 1):
        target_price = buy_price * (1 + ratio / 100)
        print(f"目标 {i}: {ratio}% → ¥{target_price:.2f}")
    
    print()
    print("优势：")
    print("1. 用户思维更直观：我想要多少百分比的收益")
    print("2. 设置更简单：直接输入百分比，不需要心算价格")
    print("3. 一致性更好：所有目标都基于相同的比例逻辑")
    print("4. 修改买入价格时，所有止盈价格自动重新计算")

if __name__ == "__main__":
    test_profit_calculation()
    test_reverse_calculation()
    demonstrate_new_logic()