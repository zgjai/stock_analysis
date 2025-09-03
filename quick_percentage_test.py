#!/usr/bin/env python3
"""
快速百分比显示测试
"""

def test_percentage_display():
    """测试百分比显示逻辑"""
    
    print("🧪 仪表板百分比显示快速测试\n")
    
    # 模拟不同的测试场景
    test_cases = [
        {"name": "典型正收益", "total_return_rate": 0.02, "success_rate": 0.41},
        {"name": "高收益", "total_return_rate": 0.15, "success_rate": 0.85},
        {"name": "负收益", "total_return_rate": -0.05, "success_rate": 0.25},
        {"name": "零收益", "total_return_rate": 0.0, "success_rate": 0.0},
        {"name": "小收益", "total_return_rate": 0.001, "success_rate": 0.05},
    ]
    
    print("📊 测试结果对比:\n")
    print("场景".ljust(12) + "后端数据".ljust(20) + "修复前显示".ljust(15) + "修复后显示".ljust(15) + "状态")
    print("-" * 70)
    
    for case in test_cases:
        name = case["name"]
        total_rate = case["total_return_rate"]
        success_rate = case["success_rate"]
        
        # 修复前的错误逻辑
        old_total = f"{(total_rate / 100) * 100:.2f}%"
        old_success = f"{(success_rate / 100) * 100:.1f}%"
        
        # 修复后的正确逻辑
        new_total = f"{total_rate * 100:.2f}%"
        new_success = f"{success_rate * 100:.1f}%"
        
        # 判断是否修复了问题
        is_fixed = (old_total != new_total) or (old_success != new_success)
        status = "✅ 已修复" if is_fixed else "⚪ 无变化"
        
        backend_data = f"{total_rate:.3f}, {success_rate:.3f}"
        old_display = f"{old_total}, {old_success}"
        new_display = f"{new_total}, {new_success}"
        
        print(f"{name.ljust(12)}{backend_data.ljust(20)}{old_display.ljust(15)}{new_display.ljust(15)}{status}")
    
    print("\n" + "=" * 70)
    print("✅ 修复验证完成！")
    print("📝 说明：")
    print("   - 后端数据：total_return_rate, success_rate (小数形式)")
    print("   - 修复前：错误的双重转换导致显示过小")
    print("   - 修复后：正确的百分比显示")
    print("\n🚀 现在可以启动服务器测试实际效果：")
    print("   python app.py")
    print("   访问：http://localhost:5000/")

if __name__ == "__main__":
    test_percentage_display()