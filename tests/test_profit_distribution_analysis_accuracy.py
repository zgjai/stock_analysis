"""
收益分布分析准确性测试
测试交易配对逻辑、收益区间配置、分布计算准确性等
"""
import pytest
from datetime import datetime, date
from decimal import Decimal
from models.trade_record import TradeRecord
from models.profit_distribution_config import ProfitDistributionConfig
from services.trade_pair_analyzer import TradePairAnalyzer
from services.analytics_service import AnalyticsService


class TestProfitDistributionAnalysisAccuracy:
    """收益分布分析准确性测试类"""
    
    def test_simple_trade_pair_extraction(self, db_session):
        """测试简单交易配对提取"""
        # 创建完整的买卖周期
        trades = [
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 15), reason='买入'
            ),
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='sell', price=Decimal('12.00'), quantity=1000,
                trade_date=datetime(2024, 2, 15), reason='卖出'
            )
        ]
        
        db_session.add_all(trades)
        db_session.commit()
        
        # 分析交易配对
        analyzer = TradePairAnalyzer()
        pairs = analyzer.analyze_completed_trades()
        
        assert len(pairs) == 1
        pair = pairs[0]
        
        assert pair['stock_code'] == '000001'
        assert pair['buy_price'] == Decimal('10.00')
        assert pair['sell_price'] == Decimal('12.00')
        assert pair['quantity'] == 1000
        assert pair['profit'] == Decimal('2000.00')  # (12-10) * 1000
        assert pair['profit_rate'] == Decimal('0.20')  # 20%
    
    def test_multiple_buys_single_sell_pairing(self, db_session):
        """测试多次买入单次卖出的配对逻辑"""
        # 创建多次买入
        trades = [
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('10.00'), quantity=500,
                trade_date=datetime(2024, 1, 15), reason='第一次买入'
            ),
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('11.00'), quantity=500,
                trade_date=datetime(2024, 1, 20), reason='第二次买入'
            ),
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='sell', price=Decimal('12.00'), quantity=1000,
                trade_date=datetime(2024, 2, 15), reason='全部卖出'
            )
        ]
        
        db_session.add_all(trades)
        db_session.commit()
        
        analyzer = TradePairAnalyzer()
        pairs = analyzer.analyze_completed_trades()
        
        # 应该产生两个配对（FIFO原则）
        assert len(pairs) == 2
        
        # 第一个配对：第一次买入 vs 部分卖出
        pair1 = next(p for p in pairs if p['buy_price'] == Decimal('10.00'))
        assert pair1['quantity'] == 500
        assert pair1['profit'] == Decimal('1000.00')  # (12-10) * 500
        
        # 第二个配对：第二次买入 vs 剩余卖出
        pair2 = next(p for p in pairs if p['buy_price'] == Decimal('11.00'))
        assert pair2['quantity'] == 500
        assert pair2['profit'] == Decimal('500.00')  # (12-11) * 500
    
    def test_partial_sell_pairing(self, db_session):
        """测试部分卖出的配对逻辑"""
        trades = [
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 15), reason='买入'
            ),
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='sell', price=Decimal('11.00'), quantity=300,
                trade_date=datetime(2024, 2, 15), reason='第一次卖出'
            ),
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='sell', price=Decimal('12.00'), quantity=700,
                trade_date=datetime(2024, 3, 15), reason='第二次卖出'
            )
        ]
        
        db_session.add_all(trades)
        db_session.commit()
        
        analyzer = TradePairAnalyzer()
        pairs = analyzer.analyze_completed_trades()
        
        # 应该产生两个配对
        assert len(pairs) == 2
        
        # 第一个配对：买入 vs 第一次卖出
        pair1 = next(p for p in pairs if p['sell_price'] == Decimal('11.00'))
        assert pair1['quantity'] == 300
        assert pair1['profit'] == Decimal('300.00')  # (11-10) * 300
        
        # 第二个配对：买入 vs 第二次卖出
        pair2 = next(p for p in pairs if p['sell_price'] == Decimal('12.00'))
        assert pair2['quantity'] == 700
        assert pair2['profit'] == Decimal('1400.00')  # (12-10) * 700
    
    def test_multiple_stocks_pairing(self, db_session):
        """测试多只股票的配对分析"""
        trades = [
            # 股票1：盈利
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 15), reason='买入1'
            ),
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='sell', price=Decimal('12.00'), quantity=1000,
                trade_date=datetime(2024, 2, 15), reason='卖出1'
            ),
            # 股票2：亏损
            TradeRecord(
                stock_code='000002', stock_name='万科A',
                trade_type='buy', price=Decimal('15.00'), quantity=500,
                trade_date=datetime(2024, 1, 20), reason='买入2'
            ),
            TradeRecord(
                stock_code='000002', stock_name='万科A',
                trade_type='sell', price=Decimal('13.00'), quantity=500,
                trade_date=datetime(2024, 2, 20), reason='卖出2'
            )
        ]
        
        db_session.add_all(trades)
        db_session.commit()
        
        analyzer = TradePairAnalyzer()
        pairs = analyzer.analyze_completed_trades()
        
        assert len(pairs) == 2
        
        # 验证股票1的配对
        stock1_pair = next(p for p in pairs if p['stock_code'] == '000001')
        assert stock1_pair['profit'] == Decimal('2000.00')
        assert stock1_pair['profit_rate'] == Decimal('0.20')  # 20%
        
        # 验证股票2的配对
        stock2_pair = next(p for p in pairs if p['stock_code'] == '000002')
        assert stock2_pair['profit'] == Decimal('-1000.00')
        assert stock2_pair['profit_rate'] == Decimal('-0.1333')  # -13.33%
    
    def test_profit_distribution_config_creation(self, db_session):
        """测试收益分布配置创建"""
        # 创建默认收益区间配置
        configs = [
            ProfitDistributionConfig(
                range_name='大幅亏损',
                min_profit_rate=None,
                max_profit_rate=Decimal('-0.20'),
                sort_order=1
            ),
            ProfitDistributionConfig(
                range_name='中等亏损',
                min_profit_rate=Decimal('-0.20'),
                max_profit_rate=Decimal('-0.10'),
                sort_order=2
            ),
            ProfitDistributionConfig(
                range_name='小幅亏损',
                min_profit_rate=Decimal('-0.10'),
                max_profit_rate=Decimal('0.00'),
                sort_order=3
            ),
            ProfitDistributionConfig(
                range_name='小幅盈利',
                min_profit_rate=Decimal('0.00'),
                max_profit_rate=Decimal('0.10'),
                sort_order=4
            ),
            ProfitDistributionConfig(
                range_name='中等盈利',
                min_profit_rate=Decimal('0.10'),
                max_profit_rate=Decimal('0.30'),
                sort_order=5
            ),
            ProfitDistributionConfig(
                range_name='大幅盈利',
                min_profit_rate=Decimal('0.30'),
                max_profit_rate=None,
                sort_order=6
            )
        ]
        
        db_session.add_all(configs)
        db_session.commit()
        
        # 验证配置创建成功
        saved_configs = ProfitDistributionConfig.query.order_by(
            ProfitDistributionConfig.sort_order
        ).all()
        
        assert len(saved_configs) == 6
        assert saved_configs[0].range_name == '大幅亏损'
        assert saved_configs[-1].range_name == '大幅盈利'
    
    def test_profit_distribution_calculation(self, db_session):
        """测试收益分布计算"""
        # 创建收益区间配置
        configs = [
            ProfitDistributionConfig(
                range_name='亏损', min_profit_rate=None,
                max_profit_rate=Decimal('0.00'), sort_order=1
            ),
            ProfitDistributionConfig(
                range_name='小幅盈利', min_profit_rate=Decimal('0.00'),
                max_profit_rate=Decimal('0.10'), sort_order=2
            ),
            ProfitDistributionConfig(
                range_name='中等盈利', min_profit_rate=Decimal('0.10'),
                max_profit_rate=Decimal('0.30'), sort_order=3
            ),
            ProfitDistributionConfig(
                range_name='大幅盈利', min_profit_rate=Decimal('0.30'),
                max_profit_rate=None, sort_order=4
            )
        ]
        db_session.add_all(configs)
        
        # 创建不同收益率的交易
        trades = [
            # 亏损交易
            TradeRecord(
                stock_code='000001', stock_name='股票1',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 15), reason='买入1'
            ),
            TradeRecord(
                stock_code='000001', stock_name='股票1',
                trade_type='sell', price=Decimal('8.00'), quantity=1000,
                trade_date=datetime(2024, 2, 15), reason='卖出1'
            ),
            # 小幅盈利交易
            TradeRecord(
                stock_code='000002', stock_name='股票2',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 20), reason='买入2'
            ),
            TradeRecord(
                stock_code='000002', stock_name='股票2',
                trade_type='sell', price=Decimal('10.50'), quantity=1000,
                trade_date=datetime(2024, 2, 20), reason='卖出2'
            ),
            # 中等盈利交易
            TradeRecord(
                stock_code='000003', stock_name='股票3',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 25), reason='买入3'
            ),
            TradeRecord(
                stock_code='000003', stock_name='股票3',
                trade_type='sell', price=Decimal('12.00'), quantity=1000,
                trade_date=datetime(2024, 2, 25), reason='卖出3'
            ),
            # 大幅盈利交易
            TradeRecord(
                stock_code='000004', stock_name='股票4',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 30), reason='买入4'
            ),
            TradeRecord(
                stock_code='000004', stock_name='股票4',
                trade_type='sell', price=Decimal('15.00'), quantity=1000,
                trade_date=datetime(2024, 2, 28), reason='卖出4'
            )
        ]
        
        db_session.add_all(trades)
        db_session.commit()
        
        # 计算收益分布
        distribution = AnalyticsService.get_profit_distribution()
        
        # 验证分布结果
        assert len(distribution) == 4
        
        # 验证每个区间的交易数量
        loss_range = next(d for d in distribution if d['range_name'] == '亏损')
        assert loss_range['count'] == 1
        assert loss_range['percentage'] == 25.0
        
        small_profit_range = next(d for d in distribution if d['range_name'] == '小幅盈利')
        assert small_profit_range['count'] == 1
        assert small_profit_range['percentage'] == 25.0
        
        medium_profit_range = next(d for d in distribution if d['range_name'] == '中等盈利')
        assert medium_profit_range['count'] == 1
        assert medium_profit_range['percentage'] == 25.0
        
        large_profit_range = next(d for d in distribution if d['range_name'] == '大幅盈利')
        assert large_profit_range['count'] == 1
        assert large_profit_range['percentage'] == 25.0
    
    def test_profit_distribution_edge_cases(self, db_session):
        """测试收益分布边界条件"""
        # 创建边界值配置
        config = ProfitDistributionConfig(
            range_name='测试区间',
            min_profit_rate=Decimal('0.10'),
            max_profit_rate=Decimal('0.20'),
            sort_order=1
        )
        db_session.add(config)
        
        # 创建边界值交易
        trades = [
            # 正好等于下边界 (10%)
            TradeRecord(
                stock_code='000001', stock_name='股票1',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 15), reason='买入1'
            ),
            TradeRecord(
                stock_code='000001', stock_name='股票1',
                trade_type='sell', price=Decimal('11.00'), quantity=1000,
                trade_date=datetime(2024, 2, 15), reason='卖出1'
            ),
            # 正好等于上边界 (20%)
            TradeRecord(
                stock_code='000002', stock_name='股票2',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 20), reason='买入2'
            ),
            TradeRecord(
                stock_code='000002', stock_name='股票2',
                trade_type='sell', price=Decimal('12.00'), quantity=1000,
                trade_date=datetime(2024, 2, 20), reason='卖出2'
            )
        ]
        
        db_session.add_all(trades)
        db_session.commit()
        
        # 分析配对
        analyzer = TradePairAnalyzer()
        pairs = analyzer.analyze_completed_trades()
        
        # 验证边界值处理
        assert len(pairs) == 2
        
        # 验证收益率计算精度
        pair1 = next(p for p in pairs if p['stock_code'] == '000001')
        assert abs(float(pair1['profit_rate']) - 0.10) < 0.001
        
        pair2 = next(p for p in pairs if p['stock_code'] == '000002')
        assert abs(float(pair2['profit_rate']) - 0.20) < 0.001
    
    def test_incomplete_trades_exclusion(self, db_session):
        """测试未完成交易的排除"""
        trades = [
            # 完整交易
            TradeRecord(
                stock_code='000001', stock_name='股票1',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 15), reason='买入1'
            ),
            TradeRecord(
                stock_code='000001', stock_name='股票1',
                trade_type='sell', price=Decimal('12.00'), quantity=1000,
                trade_date=datetime(2024, 2, 15), reason='卖出1'
            ),
            # 未完成交易（只有买入）
            TradeRecord(
                stock_code='000002', stock_name='股票2',
                trade_type='buy', price=Decimal('15.00'), quantity=500,
                trade_date=datetime(2024, 1, 20), reason='买入2'
            )
        ]
        
        db_session.add_all(trades)
        db_session.commit()
        
        analyzer = TradePairAnalyzer()
        pairs = analyzer.analyze_completed_trades()
        
        # 只应该返回完整的交易配对
        assert len(pairs) == 1
        assert pairs[0]['stock_code'] == '000001'
    
    def test_profit_distribution_api_integration(self, client, db_session):
        """测试收益分布API集成"""
        # 创建配置
        config = ProfitDistributionConfig(
            range_name='测试区间',
            min_profit_rate=Decimal('0.00'),
            max_profit_rate=Decimal('0.20'),
            sort_order=1
        )
        db_session.add(config)
        
        # 创建交易数据
        trades = [
            TradeRecord(
                stock_code='000001', stock_name='测试股票',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 15), reason='买入'
            ),
            TradeRecord(
                stock_code='000001', stock_name='测试股票',
                trade_type='sell', price=Decimal('11.00'), quantity=1000,
                trade_date=datetime(2024, 2, 15), reason='卖出'
            )
        ]
        db_session.add_all(trades)
        db_session.commit()
        
        # 测试API
        response = client.get('/api/analytics/profit-distribution')
        assert response.status_code == 200
        
        distribution = response.get_json()
        assert len(distribution) >= 1
        
        test_range = next(d for d in distribution if d['range_name'] == '测试区间')
        assert test_range['count'] == 1