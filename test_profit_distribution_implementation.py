#!/usr/bin/env python3
"""
测试收益分布配置功能实现
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.profit_distribution_config import ProfitDistributionConfig
from services.trade_pair_analyzer import TradePairAnalyzer
from services.analytics_service import AnalyticsService
from models.trade_record import TradeRecord
from datetime import datetime, timedelta
from decimal import Decimal


def test_profit_distribution_config():
    """测试收益分布配置功能"""
    app = create_app()
    
    with app.app_context():
        print("=== 测试收益分布配置功能 ===")
        
        # 1. 测试创建默认配置
        print("\n1. 创建默认配置...")
        ProfitDistributionConfig.create_default_configs()
        configs = ProfitDistributionConfig.get_active_configs()
        print(f"创建了 {len(configs)} 个默认配置")
        
        for config in configs:
            print(f"  - {config.range_name}: {config.min_profit_rate} ~ {config.max_profit_rate}")
        
        # 2. 测试创建示例交易数据
        print("\n2. 创建示例交易数据...")
        create_sample_trades()
        
        # 3. 测试交易配对分析
        print("\n3. 测试交易配对分析...")
        pairs = TradePairAnalyzer.analyze_completed_trades()
        print(f"分析出 {len(pairs)} 个交易配对")
        
        for pair in pairs[:3]:  # 显示前3个配对
            print(f"  - {pair['stock_code']}: 买入价 {pair['buy_price']}, 卖出价 {pair['sell_price']}, 收益率 {pair['profit_rate']:.2%}")
        
        # 4. 测试收益分布分析
        print("\n4. 测试收益分布分析...")
        result = TradePairAnalyzer.get_profit_distribution_data(configs)
        
        print(f"总交易数: {result['total_trades']}")
        print(f"总收益: {result['summary']['total_profit']:.2f}")
        print(f"平均收益率: {result['summary']['average_profit_rate']:.2%}")
        print(f"胜率: {result['summary']['win_rate']:.1f}%")
        
        print("\n收益分布:")
        for dist in result['distribution']:
            if dist['count'] > 0:
                print(f"  - {dist['range_name']}: {dist['count']}笔 ({dist['percentage']:.1f}%)")
        
        # 5. 测试AnalyticsService增强
        print("\n5. 测试AnalyticsService增强...")
        analytics_result = AnalyticsService.get_profit_distribution(use_trade_pairs=True)
        print(f"AnalyticsService 分析结果: {analytics_result['total_trades']} 笔交易")
        
        print("\n=== 测试完成 ===")


def create_sample_trades():
    """创建示例交易数据"""
    # 清除现有交易记录
    TradeRecord.query.delete()
    db.session.commit()
    
    trades = [
        # 股票A - 盈利交易 (收益率20%)
        TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            quantity=1000,
            price=Decimal('10.00'),
            trade_date=datetime.now() - timedelta(days=30),
            reason='技术分析'
        ),
        TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='sell',
            quantity=1000,
            price=Decimal('12.00'),
            trade_date=datetime.now() - timedelta(days=10),
            reason='止盈'
        ),
        
        # 股票B - 亏损交易 (收益率-10%)
        TradeRecord(
            stock_code='000002',
            stock_name='万科A',
            trade_type='buy',
            quantity=500,
            price=Decimal('20.00'),
            trade_date=datetime.now() - timedelta(days=25),
            reason='基本面分析'
        ),
        TradeRecord(
            stock_code='000002',
            stock_name='万科A',
            trade_type='sell',
            quantity=500,
            price=Decimal('18.00'),
            trade_date=datetime.now() - timedelta(days=5),
            reason='止损'
        ),
        
        # 股票C - 小幅盈利 (收益率3%)
        TradeRecord(
            stock_code='000003',
            stock_name='中国平安',
            trade_type='buy',
            quantity=200,
            price=Decimal('50.00'),
            trade_date=datetime.now() - timedelta(days=20),
            reason='价值投资'
        ),
        TradeRecord(
            stock_code='000003',
            stock_name='中国平安',
            trade_type='sell',
            quantity=200,
            price=Decimal('51.50'),
            trade_date=datetime.now() - timedelta(days=3),
            reason='获利了结'
        ),
        
        # 股票D - 大幅盈利 (收益率35%)
        TradeRecord(
            stock_code='000004',
            stock_name='招商银行',
            trade_type='buy',
            quantity=300,
            price=Decimal('40.00'),
            trade_date=datetime.now() - timedelta(days=40),
            reason='技术突破'
        ),
        TradeRecord(
            stock_code='000004',
            stock_name='招商银行',
            trade_type='sell',
            quantity=300,
            price=Decimal('54.00'),
            trade_date=datetime.now() - timedelta(days=8),
            reason='止盈'
        ),
        
        # 股票E - 当前持仓（未完成交易）
        TradeRecord(
            stock_code='000005',
            stock_name='五粮液',
            trade_type='buy',
            quantity=100,
            price=Decimal('200.00'),
            trade_date=datetime.now() - timedelta(days=15),
            reason='长期投资'
        )
    ]
    
    for trade in trades:
        db.session.add(trade)
    
    db.session.commit()
    print(f"创建了 {len(trades)} 条交易记录")


if __name__ == '__main__':
    test_profit_distribution_config()