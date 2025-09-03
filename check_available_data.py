#!/usr/bin/env python3
"""
检查数据库中可用的交易数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.trade_record import TradeRecord
from services.analytics_service import AnalyticsService
from datetime import datetime
from collections import defaultdict

def check_available_data():
    """检查可用的交易数据"""
    app = create_app()
    
    with app.app_context():
        print("=== 数据库交易记录概览 ===\n")
        
        # 获取所有交易记录
        all_trades = TradeRecord.query.order_by(TradeRecord.trade_date).all()
        
        if not all_trades:
            print("数据库中没有交易记录")
            return
        
        print(f"总交易记录数: {len(all_trades)}")
        print(f"最早交易日期: {all_trades[0].trade_date}")
        print(f"最晚交易日期: {all_trades[-1].trade_date}")
        print()
        
        # 按月份统计
        monthly_counts = defaultdict(int)
        monthly_amounts = defaultdict(float)
        
        for trade in all_trades:
            month_key = f"{trade.trade_date.year}-{trade.trade_date.month:02d}"
            monthly_counts[month_key] += 1
            monthly_amounts[month_key] += float(trade.quantity * trade.price)
        
        print("按月份统计:")
        print("-" * 50)
        print(f"{'月份':<10} {'交易笔数':<10} {'交易金额':<15}")
        print("-" * 50)
        
        for month in sorted(monthly_counts.keys()):
            print(f"{month:<10} {monthly_counts[month]:<10} {monthly_amounts[month]:<15.2f}")
        
        print()
        
        # 获取月度统计数据
        try:
            monthly_stats = AnalyticsService.get_monthly_statistics(2024)
            print("2024年月度收益统计:")
            print("-" * 80)
            print(f"{'月份':<6} {'收益金额':<12} {'收益率':<12} {'成功数':<8} {'成功率':<8}")
            print("-" * 80)
            
            for stat in monthly_stats:
                month = stat.get('month', 'N/A')
                profit_amount = stat.get('profit_amount', 0)
                profit_rate = stat.get('profit_rate')
                success_count = stat.get('success_count', 0)
                success_rate = stat.get('success_rate', 0)
                
                profit_rate_str = f"{profit_rate:.4f}" if profit_rate is not None else "无数据"
                
                print(f"{month:<6} {profit_amount:<12.2f} {profit_rate_str:<12} {success_count:<8} {success_rate:<8.2f}%")
                
        except Exception as e:
            print(f"获取月度统计时出错: {e}")
        
        # 选择一个有数据的月份进行详细分析
        if monthly_counts:
            # 找到交易最多的月份
            max_month = max(monthly_counts.keys(), key=lambda x: monthly_counts[x])
            year, month = max_month.split('-')
            year, month = int(year), int(month)
            
            print(f"\n=== {year}年{month}月详细分析 ===")
            analyze_specific_month(year, month)

def analyze_specific_month(year, month):
    """分析特定月份的收益计算"""
    from calendar import monthrange
    
    # 获取该月的交易记录
    month_start = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    month_end = datetime(year, month, last_day, 23, 59, 59)
    
    month_trades = TradeRecord.query.filter(
        TradeRecord.trade_date >= month_start,
        TradeRecord.trade_date <= month_end
    ).order_by(TradeRecord.trade_date, TradeRecord.stock_code).all()
    
    print(f"\n{year}年{month}月交易记录:")
    print("-" * 80)
    print(f"{'日期':<12} {'股票代码':<10} {'类型':<6} {'数量':<8} {'价格':<10} {'金额':<12}")
    print("-" * 80)
    
    month_buy_amount = 0
    month_sell_amount = 0
    
    for trade in month_trades:
        amount = float(trade.quantity * trade.price)
        if trade.trade_type == 'buy':
            month_buy_amount += amount
        else:
            month_sell_amount += amount
            
        print(f"{trade.trade_date.strftime('%Y-%m-%d'):<12} "
              f"{trade.stock_code:<10} "
              f"{trade.trade_type:<6} "
              f"{trade.quantity:<8} "
              f"{trade.price:<10.2f} "
              f"{amount:<12.2f}")
    
    print("-" * 80)
    print(f"{year}年{month}月买入总额: {month_buy_amount:.2f}")
    print(f"{year}年{month}月卖出总额: {month_sell_amount:.2f}")
    print(f"简单差额: {month_sell_amount - month_buy_amount:.2f}")
    
    # 计算系统的月度收益
    try:
        profit, success_count, cost = AnalyticsService._calculate_monthly_realized_profit_and_success(
            TradeRecord.query.all(), month, year
        )
        
        print(f"\n系统计算结果:")
        print(f"月度收益: {profit:.2f}")
        print(f"投入成本: {cost:.2f}")
        if cost > 0:
            print(f"收益率: {profit/cost:.4f} ({profit/cost*100:.2f}%)")
        print(f"成功股票数: {success_count}")
        
        print(f"\n计算逻辑说明:")
        print(f"1. 该月买入的股票总成本: {cost:.2f}")
        print(f"2. 这些股票产生的总收益: {profit:.2f}")
        print(f"   - 包括已实现收益（卖出部分）")
        print(f"   - 包括未实现收益（持仓部分的浮盈浮亏）")
        print(f"3. 月度收益率 = 总收益 / 总成本")
        
    except Exception as e:
        print(f"计算月度收益时出错: {e}")

if __name__ == "__main__":
    check_available_data()