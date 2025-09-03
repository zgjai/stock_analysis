#!/usr/bin/env python3
"""
最终成功率修复验证
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app import create_app
from services.analytics_service import AnalyticsService

def verify_success_rate_fix():
    """验证成功率修复"""
    print("=== 最终成功率修复验证 ===\n")
    
    # 创建Flask应用上下文
    app = create_app()
    
    with app.app_context():
        try:
            print("1. 总体统计成功率验证:")
            overall_stats = AnalyticsService.get_overall_statistics()
            overall_success_rate = overall_stats['success_rate']
            print(f"   后端返回: {overall_success_rate:.2f}")
            print(f"   前端显示: {overall_success_rate:.1f}%")
            
            if 0 <= overall_success_rate <= 100:
                print("   ✅ 总体成功率在合理范围内")
            else:
                print("   ❌ 总体成功率超出合理范围")
            print()
            
            print("2. 月度统计成功率验证:")
            monthly_stats = AnalyticsService.get_monthly_statistics(2025)
            
            all_valid = True
            for month_data in monthly_stats['monthly_data']:
                if month_data['has_data']:
                    month_name = month_data['month_name']
                    success_rate = month_data['success_rate']
                    success_count = month_data['success_count']
                    unique_stocks = month_data['unique_stocks']
                    
                    print(f"   {month_name}:")
                    print(f"     交易股票数: {unique_stocks}")
                    print(f"     盈利股票数: {success_count}")
                    print(f"     后端返回: {success_rate:.2f}")
                    print(f"     前端显示: {success_rate:.1f}%")
                    
                    # 验证数据合理性
                    if success_rate > 100:
                        print(f"     ❌ 成功率超过100%")
                        all_valid = False
                    elif success_count > unique_stocks:
                        print(f"     ❌ 盈利股票数超过交易股票数")
                        all_valid = False
                    elif success_rate < 0:
                        print(f"     ❌ 成功率为负数")
                        all_valid = False
                    else:
                        print(f"     ✅ 成功率正常")
                    print()
            
            if all_valid:
                print("3. ✅ 所有成功率数据都在合理范围内")
            else:
                print("3. ❌ 仍有成功率数据异常")
            
            print("\n4. 修复总结:")
            print("   - 后端统一返回百分比格式（如41.5表示41.5%）")
            print("   - 前端直接显示，不再乘以100")
            print("   - 月度成功率按股票数量计算，而非交易批次")
            print("   - 确保所有成功率都在0%-100%范围内")
            
        except Exception as e:
            print(f"验证失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    verify_success_rate_fix()