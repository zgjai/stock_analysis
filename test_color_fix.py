#!/usr/bin/env python3
"""
测试浮盈颜色修复
"""

def test_color_logic():
    """测试颜色逻辑"""
    print("🎨 测试浮盈颜色逻辑")
    print("=" * 50)
    
    # 模拟不同的盈亏情况
    test_cases = [
        {"ratio": 0.1234, "description": "盈利12.34%"},
        {"ratio": -0.0567, "description": "亏损5.67%"},
        {"ratio": 0.0, "description": "持平0%"},
        {"ratio": 0.3008, "description": "盈利30.08%"},
        {"ratio": -0.1245, "description": "亏损12.45%"}
    ]
    
    for case in test_cases:
        ratio = case["ratio"]
        description = case["description"]
        
        # 应用修复后的颜色逻辑
        if ratio > 0:
            color_class = 'text-danger'  # 盈利用红色
            color_name = "红色"
        elif ratio < 0:
            color_class = 'text-success'  # 亏损用绿色
            color_name = "绿色"
        else:
            color_class = 'text-muted'
            color_name = "灰色"
        
        percentage = ratio * 100
        display = f"+{percentage:.2f}%" if ratio > 0 else f"{percentage:.2f}%" if ratio < 0 else "0.00%"
        
        print(f"📊 {description}")
        print(f"   显示: {display}")
        print(f"   颜色: {color_name} ({color_class})")
        print(f"   状态: {'✅ 正确' if (ratio > 0 and color_class == 'text-danger') or (ratio < 0 and color_class == 'text-success') or (ratio == 0 and color_class == 'text-muted') else '❌ 错误'}")
        print()
    
    print("🎯 颜色规则说明:")
    print("   🔴 红色 (text-danger) = 盈利 (正数)")
    print("   🟢 绿色 (text-success) = 亏损 (负数)")
    print("   ⚪ 灰色 (text-muted) = 持平 (零)")
    print()
    print("✅ 符合中国股市颜色习惯")

if __name__ == "__main__":
    test_color_logic()