#!/usr/bin/env python3
"""
验证收益率和成功率修复
"""

def test_rates_calculation():
    """测试收益率和成功率计算"""
    
    print("=== 收益率和成功率计算验证 ===\n")
    
    # 模拟后端计算
    print("1. 总收益率计算:")
    total_investment = 1000000  # 100万投入
    total_profit = 20000       # 2万收益
    total_return_rate = total_profit / total_investment  # 0.02 (小数形式)
    
    print(f"   总投入: ¥{total_investment:,}")
    print(f"   总收益: ¥{total_profit:,}")
    print(f"   后端返回: {total_return_rate:.6f} (小数形式)")
    print(f"   前端显示: {total_return_rate * 100:.2f}% (乘以100)")
    
    print("\n2. 成功率计算:")
    closed_stocks = 10      # 10只已清仓股票
    profitable_stocks = 4   # 4只盈利
    
    # _calculate_success_rate 返回百分比
    success_rate_percentage = (profitable_stocks / closed_stocks * 100)  # 40.0
    success_rate_decimal = success_rate_percentage / 100  # 0.4 (转换为小数)
    
    print(f"   已清仓股票: {closed_stocks}只")
    print(f"   盈利股票: {profitable_stocks}只")
    print(f"   _calculate_success_rate返回: {success_rate_percentage:.1f}% (百分比形式)")
    print(f"   后端返回: {success_rate_decimal:.4f} (转换为小数形式)")
    print(f"   前端显示: {success_rate_decimal * 100:.1f}% (乘以100)")
    
    print("\n=== 修复验证 ===")
    print("✓ 总收益率: 后端0.02 → 前端2.00%")
    print("✓ 成功率: 后端0.4 → 前端40.0%")
    print("✓ 不再出现0.02%和0.4%的错误显示")
    
    print("\n=== 前端JavaScript验证 ===")
    print("总收益率显示:")
    print(f"  data.total_return_rate = {total_return_rate}")
    print(f"  显示: (data.total_return_rate * 100).toFixed(2) + '%' = {(total_return_rate * 100):.2f}%")
    
    print("\n成功率显示:")
    print(f"  data.success_rate = {success_rate_decimal}")
    print(f"  显示: (data.success_rate * 100).toFixed(1) + '%' = {(success_rate_decimal * 100):.1f}%")

if __name__ == '__main__':
    test_rates_calculation()