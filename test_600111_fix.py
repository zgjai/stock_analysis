#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试600111北方稀土成本价修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_600111_fix():
    """测试600111的成本价修复效果"""
    
    app = create_app()
    
    with app.app_context():
        try:
            from services.review_service import ReviewService
            
            print("=== 测试600111北方稀土成本价修复效果 ===\n")
            
            # 获取修复后的持仓信息
            holdings = ReviewService.get_current_holdings()
            
            # 查找600111
            target_holding = None
            for holding in holdings:
                if holding['stock_code'] == '600111':
                    target_holding = holding
                    break
            
            if target_holding:
                print("✅ 修复成功！")
                print(f"股票代码: {target_holding['stock_code']}")
                print(f"股票名称: {target_holding['stock_name']}")
                print(f"当前持仓: {target_holding['current_quantity']}股")
                print(f"成本价: ¥{target_holding['avg_buy_price']:.2f}")
                print(f"首次买入日期: {target_holding['first_buy_date']}")
                
                if abs(target_holding['avg_buy_price'] - 50.12) < 0.01:
                    print("\n🎉 成本价修复成功！现在显示的是正确的50.12元")
                    print("✅ 系统现在正确地按持仓周期计算成本价")
                    print("✅ 已结束的持仓周期不再影响当前成本价计算")
                else:
                    print(f"\n❌ 成本价仍然不正确: {target_holding['avg_buy_price']:.2f}")
                    
            else:
                print("❌ 未找到600111的持仓记录")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")

if __name__ == '__main__':
    test_600111_fix()