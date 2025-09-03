#!/usr/bin/env python3
"""
修复历史交易记录计算错误
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.historical_trade import HistoricalTrade
from services.historical_trade_service import HistoricalTradeService
from extensions import db

def fix_historical_trades():
    """修复历史交易记录计算错误"""
    app = create_app()
    
    with app.app_context():
        print("=== 修复历史交易记录计算错误 ===\n")
        
        # 1. 删除所有现有的历史交易记录
        print("🗑️  删除现有的错误历史交易记录...")
        deleted_count = HistoricalTrade.query.delete()
        db.session.commit()
        print(f"✅ 删除了 {deleted_count} 条错误记录\n")
        
        # 2. 重新生成历史交易记录
        print("🔄 重新生成历史交易记录...")
        result = HistoricalTradeService.generate_historical_records(force_regenerate=True)
        
        print(f"📊 生成结果:")
        print(f"   识别交易数: {result['total_identified']}")
        print(f"   创建记录数: {result['created_count']}")
        print(f"   跳过记录数: {result['skipped_count']}")
        print(f"   错误记录数: {result['error_count']}")
        
        if result['errors']:
            print(f"❌ 错误详情:")
            for error in result['errors']:
                print(f"   - {error}")
        
        if result['success']:
            print("\n✅ 历史交易记录修复完成！")
        else:
            print("\n❌ 修复过程中出现错误")
        
        # 3. 验证002484的修复结果
        print("\n🔍 验证002484江海股份的修复结果:")
        print("-" * 50)
        
        stock_002484 = HistoricalTrade.query.filter_by(stock_code="002484").first()
        if stock_002484:
            print(f"✅ 找到修复后的记录:")
            print(f"   投入本金: ¥{float(stock_002484.total_investment):,.2f}")
            print(f"   实际收益: ¥{float(stock_002484.total_return):,.2f}")
            print(f"   收益率:   {float(stock_002484.return_rate)*100:.2f}%")
            print(f"   买入记录数: {len(stock_002484.buy_records_list)}")
            print(f"   卖出记录数: {len(stock_002484.sell_records_list)}")
            
            # 验证计算是否正确
            expected_profit = 30673.00  # 正确的收益
            actual_profit = float(stock_002484.total_return)
            
            if abs(actual_profit - expected_profit) < 1:
                print(f"✅ 收益计算正确！")
            else:
                print(f"❌ 收益计算仍有问题:")
                print(f"   期望收益: ¥{expected_profit:,.2f}")
                print(f"   实际收益: ¥{actual_profit:,.2f}")
        else:
            print("❌ 未找到002484的历史交易记录")

if __name__ == "__main__":
    fix_historical_trades()