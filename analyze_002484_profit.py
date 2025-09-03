#!/usr/bin/env python3
"""
分析002484江海股份的收益计算过程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from models.historical_trade import HistoricalTrade
from services.historical_trade_service import HistoricalTradeService
from datetime import datetime

def analyze_002484_profit():
    """分析002484江海股份的收益计算"""
    app = create_app()
    
    with app.app_context():
        print("=== 002484 江海股份收益计算分析 ===\n")
        
        stock_code = "002484"
        
        # 1. 获取所有交易记录
        all_trades = TradeRecord.query.filter_by(
            stock_code=stock_code,
            is_corrected=False
        ).order_by(TradeRecord.trade_date.asc()).all()
        
        if not all_trades:
            print(f"❌ 未找到股票 {stock_code} 的交易记录")
            return
        
        print(f"📊 找到 {len(all_trades)} 条交易记录:")
        print("-" * 80)
        
        total_buy_amount = 0
        total_sell_amount = 0
        current_position = 0
        
        for i, trade in enumerate(all_trades, 1):
            amount = float(trade.price * trade.quantity)
            
            if trade.trade_type == 'buy':
                total_buy_amount += amount
                current_position += trade.quantity
                position_change = f"+{trade.quantity}"
            else:
                total_sell_amount += amount
                current_position -= trade.quantity
                position_change = f"-{trade.quantity}"
            
            print(f"{i:2d}. {trade.trade_date.strftime('%Y-%m-%d')} "
                  f"{trade.trade_type:4s} {trade.quantity:6d}股 "
                  f"@{trade.price:7.2f}元 = {amount:10.2f}元 "
                  f"持仓:{current_position:6d}股 ({position_change})")
        
        print("-" * 80)
        print(f"📈 交易汇总:")
        print(f"   总买入金额: ¥{total_buy_amount:,.2f}")
        print(f"   总卖出金额: ¥{total_sell_amount:,.2f}")
        print(f"   简单差额:   ¥{total_sell_amount - total_buy_amount:,.2f}")
        print(f"   最终持仓:   {current_position} 股")
        print()
        
        # 2. 查看历史交易记录
        historical_trades = HistoricalTrade.query.filter_by(stock_code=stock_code).all()
        
        if historical_trades:
            print(f"📋 历史交易记录 ({len(historical_trades)} 条):")
            print("-" * 80)
            
            for i, ht in enumerate(historical_trades, 1):
                print(f"{i}. 交易周期: {ht.buy_date.strftime('%Y-%m-%d')} → {ht.sell_date.strftime('%Y-%m-%d')}")
                print(f"   持仓天数: {ht.holding_days} 天")
                print(f"   投入本金: ¥{float(ht.total_investment):,.2f}")
                print(f"   实际收益: ¥{float(ht.total_return):,.2f}")
                print(f"   收益率:   {float(ht.return_rate)*100:.2f}%")
                
                # 显示关联的交易记录
                buy_ids = ht.buy_records_list
                sell_ids = ht.sell_records_list
                
                if buy_ids:
                    buy_records = TradeRecord.query.filter(TradeRecord.id.in_(buy_ids)).all()
                    print(f"   买入记录 ({len(buy_records)} 条):")
                    buy_total = 0
                    for br in buy_records:
                        amount = float(br.price * br.quantity)
                        buy_total += amount
                        print(f"     {br.trade_date.strftime('%Y-%m-%d')} 买入 {br.quantity}股 @{br.price:.2f}元 = ¥{amount:.2f}")
                    print(f"     买入小计: ¥{buy_total:.2f}")
                
                if sell_ids:
                    sell_records = TradeRecord.query.filter(TradeRecord.id.in_(sell_ids)).all()
                    print(f"   卖出记录 ({len(sell_records)} 条):")
                    sell_total = 0
                    for sr in sell_records:
                        amount = float(sr.price * sr.quantity)
                        sell_total += amount
                        print(f"     {sr.trade_date.strftime('%Y-%m-%d')} 卖出 {sr.quantity}股 @{sr.price:.2f}元 = ¥{amount:.2f}")
                    print(f"     卖出小计: ¥{sell_total:.2f}")
                
                print(f"   验证计算: ¥{sell_total:.2f} - ¥{buy_total:.2f} = ¥{sell_total - buy_total:.2f}")
                print()
        else:
            print("❌ 未找到历史交易记录")
            print("🔄 尝试识别完整交易...")
            
            # 3. 使用服务识别完整交易
            try:
                completed_trades = HistoricalTradeService._analyze_stock_trades(stock_code, all_trades)
                
                if completed_trades:
                    print(f"✅ 识别出 {len(completed_trades)} 个完整交易:")
                    print("-" * 80)
                    
                    for i, ct in enumerate(completed_trades, 1):
                        print(f"{i}. 完整交易周期:")
                        print(f"   买入日期: {ct['buy_date'].strftime('%Y-%m-%d')}")
                        print(f"   卖出日期: {ct['sell_date'].strftime('%Y-%m-%d')}")
                        print(f"   持仓天数: {ct['holding_days']} 天")
                        print(f"   投入本金: ¥{float(ct['total_investment']):,.2f}")
                        print(f"   实际收益: ¥{float(ct['total_return']):,.2f}")
                        print(f"   收益率:   {float(ct['return_rate'])*100:.2f}%")
                        print()
                else:
                    print("❌ 未识别出完整交易（可能仍有持仓）")
                    
            except Exception as e:
                print(f"❌ 识别完整交易时出错: {str(e)}")
        
        # 4. 分析为什么是-91906.00
        print("🔍 收益计算分析:")
        print("-" * 50)
        
        if current_position == 0:
            actual_profit = total_sell_amount - total_buy_amount
            print(f"✅ 已完全清仓，实际收益应为: ¥{actual_profit:,.2f}")
            
            if abs(actual_profit - (-91906.00)) < 1:
                print("✅ 计算结果与显示一致")
            else:
                print(f"❌ 计算结果与显示不一致")
                print(f"   显示收益: ¥-91,906.00")
                print(f"   计算收益: ¥{actual_profit:,.2f}")
                print(f"   差异:     ¥{actual_profit - (-91906.00):,.2f}")
        else:
            print(f"⚠️  仍有持仓 {current_position} 股，可能不是完整交易")
            print(f"   已实现收益: ¥{total_sell_amount - total_buy_amount:,.2f}")

if __name__ == "__main__":
    analyze_002484_profit()