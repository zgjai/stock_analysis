#!/usr/bin/env python3
"""
调试服务器错误
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from services.expectation_comparison_service import ExpectationComparisonService
import traceback

def debug_server_error():
    """调试服务器错误"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 调试服务器错误 ===\n")
            
            # 尝试调用期望对比服务
            print("1. 测试期望对比服务...")
            data = ExpectationComparisonService.get_expectation_comparison('all', 3200000)
            print("✅ 期望对比服务调用成功")
            
        except Exception as e:
            print(f"❌ 期望对比服务调用失败: {e}")
            print("\n详细错误信息:")
            traceback.print_exc()
            
            # 尝试分步调试
            print("\n2. 分步调试...")
            try:
                # 测试期望指标计算
                print("   测试期望指标计算...")
                expectation = ExpectationComparisonService.calculate_expectation_metrics(3200000)
                print(f"   ✅ 期望指标: {expectation}")
                
                # 测试获取交易记录
                print("   测试获取交易记录...")
                trades = ExpectationComparisonService._get_trades_by_time_range('all')
                print(f"   ✅ 交易记录数: {len(trades)}")
                
                # 测试实际指标计算
                print("   测试实际指标计算...")
                actual = ExpectationComparisonService.calculate_actual_metrics(trades, 3200000)
                print(f"   ✅ 实际指标: {actual}")
                
            except Exception as e2:
                print(f"   ❌ 分步调试失败: {e2}")
                traceback.print_exc()

if __name__ == "__main__":
    debug_server_error()