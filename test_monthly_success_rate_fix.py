#!/usr/bin/env python3
"""
测试月度成功率计算修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app import create_app
from services.analytics_service import AnalyticsService

def test_monthly_success_rate():
    """测试月度成功率计算"""
    print("=== 月度成功率计算修复测试 ===\n")
    
    # 创建Flask应用上下文
    app = create_app()
    
    with app.app_context():
        try:
            # 获取2025年的月度统计
            monthly_stats = AnalyticsService.get_monthly_statistics(2025)
            
            print("修复前后对比:")
            print("问题: 成功率超过100%，原因是success_count按交易批次计算，而不是按股票数量")
            print("修复: 改为计算该月盈利股票数占该月交易股票数的比例\n")
            
            for month_data in monthly_stats['monthly_data']:
                if month_data['has_data']:
                    month_name = month_data['month_name']
                    success_count = month_data['success_count']
                    unique_stocks = month_data['unique_stocks']
                    success_rate = month_data['success_rate']
                    
                    print(f"{month_name}:")
                    print(f"  交易股票数: {unique_stocks}")
                    print(f"  盈利股票数: {success_count}")
                    print(f"  成功率: {success_rate:.1f}%")
                    
                    # 验证成功率是否合理
                    if success_rate > 100:
                        print(f"  ❌ 成功率仍然超过100%!")
                    elif success_count > unique_stocks:
                        print(f"  ❌ 盈利股票数({success_count})超过交易股票数({unique_stocks})!")
                    else:
                        print(f"  ✅ 成功率计算正常")
                    print()
            
            # 显示计算逻辑
            print("成功率计算逻辑:")
            print("1. 统计该月有交易的股票数量 (unique_stocks)")
            print("2. 计算每只股票的总体收益 (已实现收益 + 持仓浮盈浮亏)")
            print("3. 统计盈利股票数量 (success_count)")
            print("4. 成功率 = (盈利股票数 / 交易股票数) × 100%")
            print("5. 确保: 0% ≤ 成功率 ≤ 100%")
            
        except Exception as e:
            print(f"测试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_monthly_success_rate()