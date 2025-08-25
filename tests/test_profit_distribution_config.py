"""
收益分布配置功能测试
"""
import pytest
from decimal import Decimal
from extensions import db
from models.profit_distribution_config import ProfitDistributionConfig
from models.trade_record import TradeRecord
from services.trade_pair_analyzer import TradePairAnalyzer
from services.analytics_service import AnalyticsService


class TestProfitDistributionConfig:
    """收益分布配置模型测试"""
    
    def test_create_config(self, app):
        """测试创建配置"""
        with app.app_context():
            config = ProfitDistributionConfig(
                range_name='测试区间',
                min_profit_rate=Decimal('0.1'),
                max_profit_rate=Decimal('0.2'),
                sort_order=1
            )
            db.session.add(config)
            db.session.commit()
            
            assert config.id is not None
            assert config.range_name == '测试区间'
            assert config.min_profit_rate == Decimal('0.1')
            assert config.max_profit_rate == Decimal('0.2')
            assert config.is_active is True
    
    def test_create_default_configs(self, app):
        """测试创建默认配置"""
        with app.app_context():
            # 清空现有配置
            ProfitDistributionConfig.query.delete()
            db.session.commit()
            
            # 创建默认配置
            ProfitDistributionConfig.create_default_configs()
            
            configs = ProfitDistributionConfig.query.all()
            assert len(configs) == 8  # 默认有8个区间
            
            # 验证配置内容
            config_names = [c.range_name for c in configs]
            assert '严重亏损' in config_names
            assert '超高盈利' in config_names
    
    def test_get_active_configs(self, app):
        """测试获取活跃配置"""
        with app.app_context():
            # 创建测试配置
            config1 = ProfitDistributionConfig(
                range_name='活跃配置',
                sort_order=1,
                is_active=True
            )
            config2 = ProfitDistributionConfig(
                range_name='非活跃配置',
                sort_order=2,
                is_active=False
            )
            db.session.add_all([config1, config2])
            db.session.commit()
            
            active_configs = ProfitDistributionConfig.get_active_configs()
            active_names = [c.range_name for c in active_configs]
            
            assert '活跃配置' in active_names
            assert '非活跃配置' not in active_names
    
    def test_validate_range(self, app):
        """测试区间验证"""
        with app.app_context():
            # 测试有效区间
            config = ProfitDistributionConfig(
                range_name='有效区间',
                min_profit_rate=Decimal('0.1'),
                max_profit_rate=Decimal('0.2')
            )
            # 应该不抛出异常
            config.validate_range()
            
            # 测试无效区间（最小值大于最大值）
            invalid_config = ProfitDistributionConfig(
                range_name='无效区间',
                min_profit_rate=Decimal('0.2'),
                max_profit_rate=Decimal('0.1')
            )
            
            with pytest.raises(ValueError, match="最小收益率必须小于最大收益率"):
                invalid_config.validate_range()
    
    def test_to_dict(self, app):
        """测试转换为字典"""
        with app.app_context():
            config = ProfitDistributionConfig(
                range_name='测试区间',
                min_profit_rate=Decimal('0.1'),
                max_profit_rate=Decimal('0.2'),
                sort_order=1
            )
            db.session.add(config)
            db.session.commit()
            
            config_dict = config.to_dict()
            
            assert config_dict['range_name'] == '测试区间'
            assert config_dict['min_profit_rate'] == 0.1
            assert config_dict['max_profit_rate'] == 0.2
            assert config_dict['sort_order'] == 1
            assert config_dict['is_active'] is True


class TestTradePairAnalyzer:
    """交易配对分析器测试"""
    
    def test_analyze_completed_trades(self, app, sample_trades):
        """测试分析已完成交易"""
        with app.app_context():
            # 创建测试交易记录
            self._create_sample_trades()
            
            pairs = TradePairAnalyzer.analyze_completed_trades()
            
            # 验证配对结果
            assert len(pairs) > 0
            
            # 验证配对数据结构
            pair = pairs[0]
            required_fields = [
                'stock_code', 'buy_trade_id', 'sell_trade_id',
                'buy_date', 'sell_date', 'quantity',
                'buy_price', 'sell_price', 'cost', 'revenue',
                'profit', 'profit_rate', 'holding_days'
            ]
            
            for field in required_fields:
                assert field in pair
    
    def test_get_profit_distribution_data(self, app):
        """测试获取收益分布数据"""
        with app.app_context():
            # 创建默认配置
            ProfitDistributionConfig.create_default_configs()
            configs = ProfitDistributionConfig.get_active_configs()
            
            # 创建测试交易
            self._create_sample_trades()
            
            # 获取分布数据
            result = TradePairAnalyzer.get_profit_distribution_data(configs)
            
            # 验证结果结构
            assert 'total_trades' in result
            assert 'distribution' in result
            assert 'summary' in result
            
            # 验证分布数据
            distribution = result['distribution']
            assert len(distribution) == len(configs)
            
            for dist_item in distribution:
                assert 'range_name' in dist_item
                assert 'count' in dist_item
                assert 'percentage' in dist_item
                assert 'total_profit' in dist_item
    
    def test_get_current_holdings_summary(self, app):
        """测试获取当前持仓汇总"""
        with app.app_context():
            # 创建测试交易（包含未完成的持仓）
            self._create_sample_trades_with_holdings()
            
            holdings = TradePairAnalyzer.get_current_holdings_summary()
            
            # 验证持仓数据
            assert isinstance(holdings, dict)
            
            for stock_code, holding in holdings.items():
                assert 'quantity' in holding
                assert 'average_cost' in holding
                assert 'total_cost' in holding
                assert holding['quantity'] > 0
    
    def _create_sample_trades(self):
        """创建示例交易记录"""
        from datetime import datetime, timedelta
        
        # 创建完整的买卖周期
        trades = [
            # 股票A - 盈利交易
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
            # 股票B - 亏损交易
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
            )
        ]
        
        for trade in trades:
            db.session.add(trade)
        db.session.commit()
    
    def _create_sample_trades_with_holdings(self):
        """创建包含持仓的示例交易记录"""
        from datetime import datetime, timedelta
        
        trades = [
            # 完整交易周期
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
            # 当前持仓
            TradeRecord(
                stock_code='000002',
                stock_name='万科A',
                trade_type='buy',
                quantity=500,
                price=Decimal('20.00'),
                trade_date=datetime.now() - timedelta(days=15),
                reason='基本面分析'
            )
        ]
        
        for trade in trades:
            db.session.add(trade)
        db.session.commit()


class TestAnalyticsServiceEnhancement:
    """分析服务增强功能测试"""
    
    def test_get_profit_distribution_with_trade_pairs(self, app):
        """测试使用交易配对的收益分布分析"""
        with app.app_context():
            # 创建默认配置
            ProfitDistributionConfig.create_default_configs()
            
            # 创建测试交易
            self._create_sample_trades()
            
            # 测试新的分析方法
            result = AnalyticsService.get_profit_distribution(use_trade_pairs=True)
            
            # 验证结果结构
            assert 'total_trades' in result
            assert 'distribution' in result
            assert 'summary' in result
            
            # 验证汇总数据
            summary = result['summary']
            assert 'total_profit' in summary
            assert 'average_profit_rate' in summary
            assert 'win_rate' in summary
    
    def test_get_profit_distribution_legacy_mode(self, app):
        """测试传统模式的收益分布分析"""
        with app.app_context():
            # 创建默认配置
            ProfitDistributionConfig.create_default_configs()
            
            # 创建测试交易
            self._create_sample_trades()
            
            # 测试传统分析方法
            result = AnalyticsService.get_profit_distribution(use_trade_pairs=False)
            
            # 验证结果结构
            assert 'total_trades' in result
            assert 'distribution' in result
            assert 'summary' in result
    
    def _create_sample_trades(self):
        """创建示例交易记录"""
        from datetime import datetime, timedelta
        
        trades = [
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
            )
        ]
        
        for trade in trades:
            db.session.add(trade)
        db.session.commit()


@pytest.fixture
def sample_trades():
    """示例交易数据fixture"""
    return []