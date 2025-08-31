#!/usr/bin/env python3
"""
分析收益分布统计范围
确认统计的是已清仓股票还是全部股票（包括持仓）
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from services.analytics_service import AnalyticsService
from services.trade_pair_analyzer import TradePairAnalyzer
from models.profit_distribution_config import ProfitDistributionConfig


def analyze_profit_distribution_scope():
    """分析收益分布统计的范围"""
    app = create_app()
    
    with app.app_context():
        print("🔍 分析收益分布统计范围...\n")
        
        # 1. 获取当前使用的方法
        print("1. 当前系统使用的统计方法:")
        
        # 默认使用trade_pairs=True
        distribution_new = AnalyticsService.get_profit_distribution(use_trade_pairs=True)
        distribution_legacy = AnalyticsService.get_profit_distribution(use_trade_pairs=False)
        
        print(f"   新方法 (use_trade_pairs=True):  统计 {distribution_new['total_trades']} 个单位")
        print(f"   旧方法 (use_trade_pairs=False): 统计 {distribution_legacy['total_trades']} 个单位")
        
        # 2. 分析新方法（交易配对）
        print("\n2. 新方法 (TradePairAnalyzer) 分析:")
        print("   📋 统计对象: 已完成的买卖配对交易")
        print("   📋 统计逻辑: 每个完整的买入-卖出周期算作一笔交易")
        print("   📋 包含范围: 仅已清仓的交易配对")
        print("   📋 不包含: 当前持仓股票")
        
        completed_pairs = TradePairAnalyzer.analyze_completed_trades()
        print(f"   📊 已完成交易配对数: {len(completed_pairs)}")
        
        if completed_pairs:
            print("   📊 配对示例 (前3个):")
            for i, pair in enumerate(completed_pairs[:3]):
                profit_rate = pair['profit_rate'] * 100
                print(f"      {i+1}. {pair['stock_code']}: 买入{pair['buy_price']:.2f} -> 卖出{pair['sell_price']:.2f}, 收益率{profit_rate:+.2f}%")
        
        # 3. 分析旧方法（股票维度）
        print("\n3. 旧方法 (_get_legacy_profit_distribution) 分析:")
        print("   📋 统计对象: 股票（包括持仓和已清仓）")
        print("   📋 统计逻辑: 每只股票算作一个单位")
        print("   📋 包含范围: 当前持仓股票 + 已清仓股票")
        
        # 获取详细的持仓和已清仓信息
        from models.trade_record import TradeRecord
        trades = TradeRecord.query.filter_by(is_corrected=False).all()
        holdings = AnalyticsService._calculate_current_holdings(trades)
        closed_positions = AnalyticsService._calculate_closed_positions_detail(trades)
        
        print(f"   📊 当前持仓股票数: {len(holdings)}")
        print(f"   📊 已清仓股票数: {len(closed_positions)}")
        print(f"   📊 总计股票数: {len(holdings) + len(closed_positions)}")
        
        # 4. 显示具体的分布差异
        print("\n4. 两种方法的分布对比:")
        print("   新方法 (交易配对) 分布:")
        for item in distribution_new['distribution'][:5]:  # 只显示前5个
            print(f"      {item['range_name']:15s}: {item['count']:3d}笔配对 ({item['percentage']:5.1f}%)")
        
        print("   旧方法 (股票维度) 分布:")
        for item in distribution_legacy['distribution'][:5]:  # 只显示前5个
            print(f"      {item['range_name']:15s}: {item['count']:3d}只股票 ({item['percentage']:5.1f}%)")
        
        # 5. 当前持仓股票的收益情况
        print("\n5. 当前持仓股票收益分布:")
        if holdings:
            holding_by_range = {}
            configs = ProfitDistributionConfig.get_active_configs()
            
            for config in configs:
                holding_by_range[config.range_name] = []
            
            for stock_code, holding in holdings.items():
                profit_rate = holding['profit_rate']
                
                # 找到对应区间
                for config in configs:
                    min_rate = config.min_profit_rate
                    max_rate = config.max_profit_rate
                    
                    in_range = True
                    if min_rate is not None and profit_rate < min_rate:
                        in_range = False
                    if max_rate is not None and profit_rate >= max_rate:
                        in_range = False
                    
                    if in_range:
                        holding_by_range[config.range_name].append({
                            'stock_code': stock_code,
                            'profit_rate': profit_rate * 100
                        })
                        break
            
            for range_name, stocks in holding_by_range.items():
                if stocks:
                    print(f"   {range_name:15s}: {len(stocks)}只持仓股票")
                    for stock in stocks[:2]:  # 只显示前2只
                        print(f"      - {stock['stock_code']}: {stock['profit_rate']:+.2f}%")
        
        # 6. 结论
        print("\n" + "="*60)
        print("📋 结论:")
        print("✅ 当前系统默认使用 use_trade_pairs=True")
        print("✅ 这意味着收益分布统计的是: 已完成的买卖配对交易")
        print("✅ 不包括当前持仓股票的浮盈浮亏")
        print("✅ 每个完整的买入-卖出周期算作一笔交易")
        print("")
        print("🤔 如果你希望包含当前持仓股票，需要:")
        print("   1. 修改前端调用，使用 use_trade_pairs=false")
        print("   2. 或者修改 TradePairAnalyzer 逻辑，包含持仓股票")
        print("="*60)


if __name__ == '__main__':
    analyze_profit_distribution_scope()