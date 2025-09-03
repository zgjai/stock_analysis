#!/usr/bin/env python3
"""
测试成功率显示修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app import create_app
from services.analytics_service import AnalyticsService

def test_success_rate_display():
    """测试成功率显示修复"""
    print("=== 成功率显示修复测试 ===\n")
    
    # 创建Flask应用上下文
    app = create_app()
    
    with app.app_context():
        try:
            # 获取总体统计
            overall_stats = AnalyticsService.get_overall_statistics()
            print("总体统计成功率:")
            print(f"  后端返回: {overall_stats['success_rate']}")
            print(f"  前端应显示: {overall_stats['success_rate']:.1f}%")
            print()
            
            # 获取2025年的月度统计
            monthly_stats = AnalyticsService.get_monthly_statistics(2025)
            
            print("月度统计成功率:")
            for month_data in monthly_stats['monthly_data']:
                if month_data['has_data']:
                    month_name = month_data['month_name']
                    success_rate = month_data['success_rate']
                    
                    print(f"{month_name}:")
                    print(f"  后端返回: {success_rate}")
                    print(f"  前端应显示: {success_rate:.1f}%")
                    
                    # 验证数据合理性
                    if success_rate > 100:
                        print(f"  ❌ 成功率仍然超过100%!")
                    else:
                        print(f"  ✅ 成功率在合理范围内")
                    print()
            
            print("修复说明:")
            print("1. 后端返回的success_rate已经是百分比形式（如54.7表示54.7%）")
            print("2. 前端不应该再乘以100，直接显示即可")
            print("3. 修复前：前端显示 (54.7 * 100).toFixed(1) = 5470.0%")
            print("4. 修复后：前端显示 54.7.toFixed(1) = 54.7%")
            
        except Exception as e:
            print(f"测试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_success_rate_display()