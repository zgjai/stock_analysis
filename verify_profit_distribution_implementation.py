#!/usr/bin/env python3
"""
验证收益分布配置功能完整实现
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


def verify_implementation():
    """验证完整实现"""
    app = create_app()
    
    with app.app_context():
        print("=== 验证收益分布配置功能完整实现 ===")
        
        # 1. 验证数据模型
        print("\n1. 验证数据模型...")
        verify_data_model()
        
        # 2. 验证交易配对分析
        print("\n2. 验证交易配对分析...")
        verify_trade_pair_analyzer()
        
        # 3. 验证AnalyticsService增强
        print("\n3. 验证AnalyticsService增强...")
        verify_analytics_service()
        
        # 4. 验证API端点
        print("\n4. 验证API端点...")
        verify_api_endpoints()
        
        print("\n=== 验证完成 ===")
        print("✅ 所有功能已成功实现并通过验证")


def verify_data_model():
    """验证数据模型"""
    # 清理现有数据
    ProfitDistributionConfig.query.delete()
    db.session.commit()
    
    # 创建默认配置
    ProfitDistributionConfig.create_default_configs()
    configs = ProfitDistributionConfig.get_active_configs()
    
    assert len(configs) == 8, f"应该有8个默认配置，实际有{len(configs)}个"
    print(f"✅ 创建了{len(configs)}个默认配置")
    
    # 测试创建自定义配置
    custom_config = ProfitDistributionConfig(
        range_name='自定义测试区间',
        min_profit_rate=Decimal('2.0'),
        max_profit_rate=Decimal('3.0'),
        sort_order=99
    )
    db.session.add(custom_config)
    db.session.commit()
    
    assert custom_config.id is not None, "自定义配置应该被成功保存"
    print("✅ 自定义配置创建成功")
    
    # 测试转换为字典
    config_dict = custom_config.to_dict()
    assert config_dict['range_name'] == '自定义测试区间'
    assert config_dict['min_profit_rate'] == 2.0
    print("✅ 配置转换为字典成功")


def verify_trade_pair_analyzer():
    """验证交易配对分析器"""
    # 清理现有交易记录
    TradeRecord.query.delete()
    db.session.commit()
    
    # 创建测试交易数据
    create_test_trades()
    
    # 测试交易配对分析
    pairs = TradePairAnalyzer.analyze_completed_trades()
    assert len(pairs) > 0, "应该有完成的交易配对"
    print(f"✅ 分析出{len(pairs)}个交易配对")
    
    # 验证配对数据结构
    pair = pairs[0]
    required_fields = [
        'stock_code', 'buy_trade_id', 'sell_trade_id',
        'buy_date', 'sell_date', 'quantity',
        'buy_price', 'sell_price', 'cost', 'revenue',
        'profit', 'profit_rate', 'holding_days'
    ]
    
    for field in required_fields:
        assert field in pair, f"配对数据缺少字段: {field}"
    print("✅ 交易配对数据结构正确")
    
    # 测试收益分布数据
    configs = ProfitDistributionConfig.get_active_configs()
    result = TradePairAnalyzer.get_profit_distribution_data(configs)
    
    assert 'total_trades' in result
    assert 'distribution' in result
    assert 'summary' in result
    print("✅ 收益分布数据生成成功")
    
    # 测试当前持仓汇总
    holdings = TradePairAnalyzer.get_current_holdings_summary()
    assert isinstance(holdings, dict)
    print("✅ 当前持仓汇总生成成功")


def verify_analytics_service():
    """验证AnalyticsService增强"""
    # 测试新的收益分布方法
    result_new = AnalyticsService.get_profit_distribution(use_trade_pairs=True)
    result_legacy = AnalyticsService.get_profit_distribution(use_trade_pairs=False)
    
    # 验证结果结构
    for result in [result_new, result_legacy]:
        assert 'total_trades' in result
        assert 'distribution' in result
        assert 'summary' in result
    
    print("✅ AnalyticsService增强功能正常")
    print(f"  - 新方法分析了{result_new['total_trades']}笔交易")
    print(f"  - 传统方法分析了{result_legacy['total_trades']}个股票")


def verify_api_endpoints():
    """验证API端点"""
    app = create_app()
    
    with app.test_client() as client:
        # 测试获取配置列表
        response = client.get('/api/profit-distribution/configs')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        print(f"✅ 获取配置列表API正常，返回{len(data['data'])}个配置")
        
        # 测试获取分析结果
        response = client.get('/api/profit-distribution/analysis?use_trade_pairs=true')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        print("✅ 获取分析结果API正常")
        
        # 测试获取交易配对分析
        response = client.get('/api/profit-distribution/trade-pairs')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        print("✅ 获取交易配对分析API正常")
        
        # 测试创建配置
        new_config = {
            'range_name': 'API测试区间',
            'min_profit_rate': 5.0,  # 500%
            'max_profit_rate': 10.0,  # 1000%
            'sort_order': 100,
            'is_active': True
        }
        response = client.post('/api/profit-distribution/configs',
                             json=new_config,
                             content_type='application/json')
        assert response.status_code == 200
        created_data = response.get_json()
        assert created_data['success'] is True
        config_id = created_data['data']['id']
        print("✅ 创建配置API正常")
        
        # 测试删除配置
        response = client.delete(f'/api/profit-distribution/configs/{config_id}')
        assert response.status_code == 200
        print("✅ 删除配置API正常")


def create_test_trades():
    """创建测试交易数据"""
    trades = [
        # 完整的买卖周期 - 盈利
        TradeRecord(
            stock_code='000001',
            stock_name='测试股票1',
            trade_type='buy',
            quantity=1000,
            price=Decimal('10.00'),
            trade_date=datetime.now() - timedelta(days=30),
            reason='测试买入'
        ),
        TradeRecord(
            stock_code='000001',
            stock_name='测试股票1',
            trade_type='sell',
            quantity=1000,
            price=Decimal('15.00'),
            trade_date=datetime.now() - timedelta(days=10),
            reason='测试卖出'
        ),
        
        # 完整的买卖周期 - 亏损
        TradeRecord(
            stock_code='000002',
            stock_name='测试股票2',
            trade_type='buy',
            quantity=500,
            price=Decimal('20.00'),
            trade_date=datetime.now() - timedelta(days=25),
            reason='测试买入'
        ),
        TradeRecord(
            stock_code='000002',
            stock_name='测试股票2',
            trade_type='sell',
            quantity=500,
            price=Decimal('18.00'),
            trade_date=datetime.now() - timedelta(days=5),
            reason='测试卖出'
        ),
        
        # 当前持仓
        TradeRecord(
            stock_code='000003',
            stock_name='测试股票3',
            trade_type='buy',
            quantity=200,
            price=Decimal('50.00'),
            trade_date=datetime.now() - timedelta(days=15),
            reason='测试买入'
        )
    ]
    
    for trade in trades:
        db.session.add(trade)
    
    db.session.commit()
    print(f"创建了{len(trades)}条测试交易记录")


if __name__ == '__main__':
    verify_implementation()