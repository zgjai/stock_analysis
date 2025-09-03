#!/usr/bin/env python3
"""
调试历史交易识别逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from services.historical_trade_service import HistoricalTradeService

def debug_historical_trade_logic():
    """调试历史交易识别逻辑"""
    app = create_app()
    
    with app.app_context():
        print("=== 调试历史交易识别逻辑 ===\n")
        
        stock_code = "002484"
        
        # 获取交易记录
        trades = TradeRecord.query.filter_by(
            stock_code=stock_code,
            is_corrected=False
        ).order_by(TradeRecord.trade_date.asc()).all()
        
        print("🔍 模拟 _analyze_stock_trades 逻辑:")
        print("-" * 60)
        
        completed_trades = []
        current_position = 0
        buy_records = []
        
        for i, trade in enumerate(trades, 1):
            print(f"\n步骤 {i}: 处理 {trade.trade_date.strftime('%Y-%m-%d')} {trade.trade_type} {trade.quantity}股")
            
            if trade.trade_type == 'buy':
                current_position += trade.quantity
                buy_records.append(trade)
                print(f"   买入后持仓: {current_position} 股")
                print(f"   买入记录列表: {[f'{r.trade_date.strftime('%m-%d')}买{r.quantity}股' for r in buy_records]}")
                
            elif trade.trade_type == 'sell':
                if current_position <= 0:
                    print(f"   ⚠️ 警告: 在没有持仓的情况下卖出")
                    continue
                
                sell_quantity = min(trade.quantity, current_position)
                current_position -= sell_quantity
                
                print(f"   卖出 {sell_quantity} 股，剩余持仓: {current_position} 股")
                
                # 关键逻辑：只有完全清仓才创建历史交易记录
                if current_position == 0 and buy_records:
                    print(f"   🎯 检测到完全清仓！创建历史交易记录")
                    print(f"   📝 买入记录: {[f'{r.trade_date.strftime('%m-%d')}买{r.quantity}股@{r.price}' for r in buy_records]}")
                    print(f"   📝 卖出记录: {trade.trade_date.strftime('%m-%d')}卖{trade.quantity}股@{trade.price}")
                    
                    # 这里是问题所在！只记录了最后一次卖出
                    completed_trade = {
                        'buy_records': buy_records.copy(),
                        'sell_records': [trade],  # 只有最后一次卖出！
                        'stock_code': stock_code
                    }
                    completed_trades.append(completed_trade)
                    
                    # 计算收益
                    total_buy = sum(float(r.price * r.quantity) for r in buy_records)
                    total_sell = float(trade.price * trade.quantity)  # 只计算最后一次卖出！
                    profit = total_sell - total_buy
                    
                    print(f"   💰 买入总额: ¥{total_buy:,.2f}")
                    print(f"   💰 卖出总额: ¥{total_sell:,.2f} (❌ 只计算了最后一次卖出)")
                    print(f"   💰 计算收益: ¥{profit:,.2f}")
                    
                    buy_records = []
                else:
                    print(f"   ⏳ 未完全清仓，继续持有")
        
        print(f"\n📊 识别结果: {len(completed_trades)} 个完整交易")
        
        print("\n🐛 问题分析:")
        print("=" * 60)
        print("❌ 系统逻辑错误：只有在完全清仓时才创建历史交易记录")
        print("❌ 但是只记录了最后一次卖出交易，忽略了之前的分批卖出")
        print("❌ 正确做法应该是记录所有相关的卖出交易")
        
        print("\n✅ 正确的计算应该是:")
        all_buy_amount = sum(float(t.price * t.quantity) for t in trades if t.trade_type == 'buy')
        all_sell_amount = sum(float(t.price * t.quantity) for t in trades if t.trade_type == 'sell')
        correct_profit = all_sell_amount - all_buy_amount
        
        print(f"   总买入: ¥{all_buy_amount:,.2f}")
        print(f"   总卖出: ¥{all_sell_amount:,.2f}")
        print(f"   正确收益: ¥{correct_profit:,.2f}")

if __name__ == "__main__":
    debug_historical_trade_logic()