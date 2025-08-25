#!/usr/bin/env python3
"""
简单测试持仓服务
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_simple():
    """简单测试"""
    print("🧪 简单测试持仓服务")
    
    app = create_app()
    with app.app_context():
        try:
            from services.review_service import HoldingService
            
            print("✅ 成功导入 HoldingService")
            
            # 测试基本方法
            holdings = HoldingService.get_current_holdings()
            print(f"✅ get_current_holdings 返回 {len(holdings)} 个持仓")
            
            # 测试新方法
            holdings_with_days = HoldingService.get_current_holdings_with_actual_days()
            print(f"✅ get_current_holdings_with_actual_days 返回 {len(holdings_with_days)} 个持仓")
            
            return True
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_simple()
    sys.exit(0 if success else 1)