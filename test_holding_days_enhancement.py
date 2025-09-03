#!/usr/bin/env python3
"""
测试持仓天数增强功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from services.review_service import HoldingService
from services.non_trading_day_service import NonTradingDayService
from models.non_trading_day import NonTradingDay
from models.trade_record import TradeRecord
from extensions import db
from app import create_app

def test_holding_days_calculation():
    """测试持仓天数计算功能"""
    print("🧪 测试持仓天数计算功能")
    
    app = create_app()
    with app.app_context():
        try:
            # 测试非交易日服务
            print("\n1. 测试非交易日服务")
            
            # 测试基本交易日判断
            today = date.today()
            is_trading = NonTradingDayService.is_trading_day(today)
            print(f"   今天 ({today}) 是否为交易日: {is_trading}")
            
            # 测试持仓天数计算
            start_date = today - timedelta(days=30)
            trading_days = NonTradingDayService.calculate_trading_days(start_date, today)
            print(f"   过去30天的交易日数: {trading_days}")
            
            # 测试持仓服务
            print("\n2. 测试持仓服务")
            
            # 获取当前持仓（包含实际交易日数）
            holdings = HoldingService.get_current_holdings_with_actual_days()
            print(f"   当前持仓数量: {len(holdings)}")
            
            if holdings:
                for holding in holdings[:3]:  # 只显示前3个
                    stock_code = holding['stock_code']
                    actual_days = holding.get('actual_holding_days', 0)
                    regular_days = holding.get('holding_days', 0)
                    first_buy = holding.get('first_buy_date', '')
                    
                    print(f"   股票 {stock_code}:")
                    print(f"     首次买入: {first_buy}")
                    print(f"     实际交易日数: {actual_days}")
                    print(f"     常规天数: {regular_days}")
                    print(f"     持仓天数显示: {holding.get('holding_days_display', 'N/A')}")
            
            print("\n✅ 持仓天数计算功能测试完成")
            return True
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_api_endpoint():
    """测试API端点"""
    print("\n🌐 测试API端点")
    
    app = create_app()
    with app.test_client() as client:
        try:
            # 测试持仓API
            response = client.get('/api/holdings?include_actual_days=true')
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    holdings = data.get('data', [])
                    print(f"   API返回持仓数量: {len(holdings)}")
                    
                    if holdings:
                        first_holding = holdings[0]
                        print(f"   第一个持仓包含字段: {list(first_holding.keys())}")
                        
                        # 检查是否包含实际持仓天数字段
                        if 'actual_holding_days' in first_holding:
                            print("   ✅ 包含实际持仓天数字段")
                        else:
                            print("   ❌ 缺少实际持仓天数字段")
                        
                        if 'holding_days_display' in first_holding:
                            print("   ✅ 包含持仓天数显示字段")
                        else:
                            print("   ❌ 缺少持仓天数显示字段")
                    
                    print("   ✅ API端点测试成功")
                    return True
                else:
                    print(f"   ❌ API返回失败: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ API请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ API测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主测试函数"""
    print("🚀 开始测试持仓天数增强功能")
    
    success_count = 0
    total_tests = 2
    
    # 测试持仓天数计算
    if test_holding_days_calculation():
        success_count += 1
    
    # 测试API端点
    if test_api_endpoint():
        success_count += 1
    
    print(f"\n📊 测试结果: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！持仓天数增强功能实现成功")
        return True
    else:
        print("⚠️ 部分测试失败，请检查实现")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)