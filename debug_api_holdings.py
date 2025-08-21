#!/usr/bin/env python3
"""
调试API holdings端点的问题
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db

def test_holdings_api():
    """测试holdings API端点"""
    app = create_app()
    
    with app.app_context():
        try:
            # 测试导入
            from services.review_service import HoldingService
            print("✅ HoldingService导入成功")
            
            # 测试获取持仓
            holdings = HoldingService.get_current_holdings()
            print(f"✅ 获取持仓成功，数量: {len(holdings)}")
            
            if holdings:
                print("持仓详情:")
                for holding in holdings:
                    print(f"  - {holding['stock_code']}: {holding['stock_name']}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()

def test_alerts_api():
    """测试alerts API端点"""
    app = create_app()
    
    with app.app_context():
        try:
            # 测试导入
            from services.strategy_service import HoldingAlertService
            print("✅ HoldingAlertService导入成功")
            
            # 测试获取提醒
            alerts = HoldingAlertService.get_all_alerts()
            print(f"✅ 获取提醒成功，数量: {len(alerts)}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=== 测试Holdings API ===")
    test_holdings_api()
    
    print("\n=== 测试Alerts API ===")
    test_alerts_api()