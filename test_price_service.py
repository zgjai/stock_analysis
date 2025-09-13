#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试实时价格服务
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_price_service():
    """测试实时价格服务"""
    
    app = create_app()
    
    with app.app_context():
        from services.review_service import HoldingService
        
        print("=== 测试实时价格服务 ===\n")
        
        # 测试600111的价格获取
        stock_code = '600111'
        print(f"测试股票: {stock_code}")
        
        try:
            # 测试不强制刷新
            print("1. 测试缓存价格获取...")
            price1 = HoldingService._get_current_price(stock_code, force_refresh=False)
            print(f"   缓存价格: {price1}")
            
            # 测试强制刷新
            print("2. 测试强制刷新价格...")
            price2 = HoldingService._get_current_price(stock_code, force_refresh=True)
            print(f"   刷新价格: {price2}")
            
            if price1 is None and price2 is None:
                print("❌ 价格获取失败，检查PriceService")
                
                # 直接测试PriceService
                from services.price_service import PriceService
                price_service = PriceService()
                
                print("3. 直接测试PriceService...")
                result = price_service.refresh_stock_price(stock_code, force_refresh=True)
                print(f"   PriceService结果: {result}")
                
            else:
                print("✅ 价格获取正常")
                
        except Exception as e:
            print(f"❌ 价格获取异常: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_price_service()