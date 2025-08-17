"""
数据模型单元测试
"""
import pytest
from datetime import datetime, date
from decimal import Decimal
from models.trade_record import TradeRecord, TradeCorrection
from models.review_record import ReviewRecord
from models.stock_pool import StockPool
from models.case_study import CaseStudy
from models.stock_price import StockPrice
from models.sector_data import SectorData, SectorRanking
from models.trading_strategy import TradingStrategy
from models.configuration import Configuration
from error_handlers import ValidationError


class TestTradeRecord:
    """交易记录模型测试"""
    
    def test_create_valid_trade_record(self, db_session, sample_trade_data):
        """测试创建有效的交易记录"""
        trade = TradeRecord(**sample_trade_data)
        trade.save()
        
        assert trade.id is not None
        assert trade.stock_code == '000001'
        assert trade.trade_type == 'buy'
        assert float(trade.price) == 12.50
        assert trade.quantity == 1000
        assert trade.expected_loss_ratio is not None
        assert trade.expected_profit_ratio is not None
    
    def test_invalid_stock_code(self, db_session):
        """测试无效股票代码"""
        with pytest.raises(ValidationError) as exc_info:
            TradeRecord(
                stock_code='INVALID',
                stock_name='测试股票',
                trade_type='buy',
                price=10.0,
                quantity=100,
                trade_date=datetime.now(),
                reason='测试'
            )
        assert '股票代码格式不正确' in str(exc_info.value)
    
    def test_invalid_price(self, db_session):
        """测试无效价格"""
        with pytest.raises(ValidationError) as exc_info:
            TradeRecord(
                stock_code='000001',
                stock_name='测试股票',
                trade_type='buy',
                price=-10.0,
                quantity=100,
                trade_date=datetime.now(),
                reason='测试'
            )
        assert '价格必须大于0' in str(exc_info.value)
    
    def test_invalid_quantity(self, db_session):
        """测试无效数量"""
        with pytest.raises(ValidationError) as exc_info:
            TradeRecord(
                stock_code='000001',
                stock_name='测试股票',
                trade_type='buy',
                price=10.0,
                quantity=0,
                trade_date=datetime.now(),
                reason='测试'
            )
        assert '数量必须大于0' in str(exc_info.value)
    
    def test_invalid_trade_type(self, db_session):
        """测试无效交易类型"""
        with pytest.raises(ValidationError) as exc_info:
            TradeRecord(
                stock_code='000001',
                stock_name='测试股票',
                trade_type='invalid',
                price=10.0,
                quantity=100,
                trade_date=datetime.now(),
                reason='测试'
            )
        assert '交易类型必须是buy或sell' in str(exc_info.value)
    
    def test_invalid_stop_loss_price(self, db_session):
        """测试无效止损价格"""
        with pytest.raises(ValidationError) as exc_info:
            TradeRecord(
                stock_code='000001',
                stock_name='测试股票',
                trade_type='buy',
                price=10.0,
                quantity=100,
                trade_date=datetime.now(),
                reason='测试',
                stop_loss_price=12.0  # 止损价格高于买入价格
            )
        assert '止损价格必须小于买入价格' in str(exc_info.value)
    
    def test_calculate_risk_reward(self, db_session):
        """测试风险收益比计算"""
        trade = TradeRecord(
            stock_code='000001',
            stock_name='测试股票',
            trade_type='buy',
            price=10.0,
            quantity=100,
            trade_date=datetime.now(),
            reason='测试',
            stop_loss_price=9.0,
            take_profit_ratio=0.2,
            sell_ratio=0.5
        )
        
        # 预计亏损比例 = (10.0 - 9.0) / 10.0 = 0.1
        assert float(trade.expected_loss_ratio) == 0.1
        # 预计收益率 = 0.2 * 0.5 = 0.1
        assert float(trade.expected_profit_ratio) == 0.1
    
    def test_get_by_stock_code(self, db_session, sample_trade_data):
        """测试根据股票代码查询"""
        trade = TradeRecord(**sample_trade_data)
        trade.save()
        
        results = TradeRecord.get_by_stock_code('000001')
        assert len(results) == 1
        assert results[0].stock_code == '000001'
    
    def test_to_dict(self, db_session, sample_trade_data):
        """测试转换为字典"""
        trade = TradeRecord(**sample_trade_data)
        trade.save()
        
        trade_dict = trade.to_dict()
        assert trade_dict['stock_code'] == '000001'
        assert isinstance(trade_dict['price'], float)
        assert isinstance(trade_dict['expected_loss_ratio'], float)


class TestReviewRecord:
    """复盘记录模型测试"""
    
    def test_create_valid_review_record(self, db_session, sample_review_data):
        """测试创建有效的复盘记录"""
        review = ReviewRecord(**sample_review_data)
        review.save()
        
        assert review.id is not None
        assert review.stock_code == '000001'
        assert review.total_score == 4  # 1+1+0+1+1
    
    def test_invalid_stock_code(self, db_session):
        """测试无效股票代码"""
        with pytest.raises(ValidationError) as exc_info:
            ReviewRecord(
                stock_code='INVALID',
                review_date=date.today(),
                price_up_score=1
            )
        assert '股票代码格式不正确' in str(exc_info.value)
    
    def test_invalid_score_value(self, db_session):
        """测试无效评分值"""
        with pytest.raises(ValidationError) as exc_info:
            ReviewRecord(
                stock_code='000001',
                review_date=date.today(),
                price_up_score=2  # 应该是0或1
            )
        assert 'price_up_score必须是0或1' in str(exc_info.value)
    
    def test_invalid_decision(self, db_session):
        """测试无效决策类型"""
        with pytest.raises(ValidationError) as exc_info:
            ReviewRecord(
                stock_code='000001',
                review_date=date.today(),
                decision='invalid'
            )
        assert '决策类型必须是hold、sell_all或sell_partial' in str(exc_info.value)
    
    def test_invalid_holding_days(self, db_session):
        """测试无效持仓天数"""
        with pytest.raises(ValidationError) as exc_info:
            ReviewRecord(
                stock_code='000001',
                review_date=date.today(),
                holding_days=-1
            )
        assert '持仓天数不能为负数' in str(exc_info.value)
    
    def test_calculate_total_score(self, db_session):
        """测试总分计算"""
        review = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            price_up_score=1,
            bbi_score=1,
            volume_score=0,
            trend_score=1,
            j_score=0
        )
        
        assert review.total_score == 3
    
    def test_update_scores(self, db_session, sample_review_data):
        """测试更新评分"""
        review = ReviewRecord(**sample_review_data)
        review.save()
        
        review.update_scores(price_up_score=0, bbi_score=0)
        assert review.total_score == 2  # 0+0+0+1+1


class TestStockPool:
    """股票池模型测试"""
    
    def test_create_valid_stock_pool(self, db_session, sample_stock_pool_data):
        """测试创建有效的股票池记录"""
        stock = StockPool(**sample_stock_pool_data)
        stock.save()
        
        assert stock.id is not None
        assert stock.stock_code == '000002'
        assert stock.pool_type == 'watch'
        assert stock.status == 'active'
    
    def test_invalid_stock_code(self, db_session):
        """测试无效股票代码"""
        with pytest.raises(ValidationError) as exc_info:
            StockPool(
                stock_code='INVALID',
                stock_name='测试股票',
                pool_type='watch'
            )
        assert '股票代码格式不正确' in str(exc_info.value)
    
    def test_invalid_pool_type(self, db_session):
        """测试无效池类型"""
        with pytest.raises(ValidationError) as exc_info:
            StockPool(
                stock_code='000001',
                stock_name='测试股票',
                pool_type='invalid'
            )
        assert '池类型必须是watch或buy_ready' in str(exc_info.value)
    
    def test_invalid_status(self, db_session):
        """测试无效状态"""
        with pytest.raises(ValidationError) as exc_info:
            StockPool(
                stock_code='000001',
                stock_name='测试股票',
                pool_type='watch',
                status='invalid'
            )
        assert '状态必须是active、moved或removed' in str(exc_info.value)
    
    def test_move_to_pool(self, db_session, sample_stock_pool_data):
        """测试移动到另一个池"""
        stock = StockPool(**sample_stock_pool_data)
        stock.save()
        
        new_stock = stock.move_to_pool('buy_ready', '技术突破')
        
        # 原记录状态变为moved
        assert stock.status == 'moved'
        # 新记录创建成功
        assert new_stock.pool_type == 'buy_ready'
        assert new_stock.status == 'active'
        assert '技术突破' in new_stock.add_reason
    
    def test_remove_from_pool(self, db_session, sample_stock_pool_data):
        """测试从池中移除"""
        stock = StockPool(**sample_stock_pool_data)
        stock.save()
        
        stock.remove_from_pool('不符合条件')
        
        assert stock.status == 'removed'
        assert '不符合条件' in stock.add_reason
    
    def test_get_by_pool_type(self, db_session, sample_stock_pool_data):
        """测试根据池类型查询"""
        stock = StockPool(**sample_stock_pool_data)
        stock.save()
        
        watch_stocks = StockPool.get_watch_pool()
        assert len(watch_stocks) == 1
        assert watch_stocks[0].pool_type == 'watch'
        
        buy_ready_stocks = StockPool.get_buy_ready_pool()
        assert len(buy_ready_stocks) == 0


class TestCaseStudy:
    """案例研究模型测试"""
    
    def test_create_valid_case_study(self, db_session, sample_case_study_data):
        """测试创建有效的案例研究"""
        case = CaseStudy(**sample_case_study_data)
        case.save()
        
        assert case.id is not None
        assert case.stock_code == '000001'
        assert case.title == '平安银行突破案例'
        assert len(case.tags_list) == 3
    
    def test_invalid_stock_code(self, db_session):
        """测试无效股票代码"""
        with pytest.raises(ValidationError) as exc_info:
            CaseStudy(
                stock_code='INVALID',
                title='测试案例',
                image_path='/uploads/test.png'
            )
        assert '股票代码格式不正确' in str(exc_info.value)
    
    def test_empty_title(self, db_session):
        """测试空标题"""
        with pytest.raises(ValidationError) as exc_info:
            CaseStudy(
                stock_code='000001',
                title='',
                image_path='/uploads/test.png'
            )
        assert '案例标题不能为空' in str(exc_info.value)
    
    def test_invalid_image_extension(self, db_session):
        """测试无效图片扩展名"""
        with pytest.raises(ValidationError) as exc_info:
            CaseStudy(
                stock_code='000001',
                title='测试案例',
                image_path='/uploads/test.txt'
            )
        assert '不支持的图片格式' in str(exc_info.value)
    
    def test_tags_management(self, db_session, sample_case_study_data):
        """测试标签管理"""
        case = CaseStudy(**sample_case_study_data)
        case.save()
        
        # 添加标签
        case.add_tag('新标签')
        assert '新标签' in case.tags_list
        
        # 移除标签
        case.remove_tag('突破')
        assert '突破' not in case.tags_list
    
    def test_search_by_keyword(self, db_session, sample_case_study_data):
        """测试关键词搜索"""
        case = CaseStudy(**sample_case_study_data)
        case.save()
        
        results = CaseStudy.search_by_keyword('平安银行')
        assert len(results) == 1
        assert results[0].title == '平安银行突破案例'


class TestStockPrice:
    """股票价格模型测试"""
    
    def test_create_valid_stock_price(self, db_session, sample_stock_price_data):
        """测试创建有效的股票价格记录"""
        price = StockPrice(**sample_stock_price_data)
        price.save()
        
        assert price.id is not None
        assert price.stock_code == '000001'
        assert float(price.current_price) == 12.80
        assert float(price.change_percent) == 2.40
    
    def test_invalid_stock_code(self, db_session):
        """测试无效股票代码"""
        with pytest.raises(ValidationError) as exc_info:
            StockPrice(
                stock_code='INVALID',
                current_price=10.0,
                record_date=date.today()
            )
        assert '股票代码格式不正确' in str(exc_info.value)
    
    def test_invalid_price(self, db_session):
        """测试无效价格"""
        with pytest.raises(ValidationError) as exc_info:
            StockPrice(
                stock_code='000001',
                current_price=-10.0,
                record_date=date.today()
            )
        assert '价格必须大于0' in str(exc_info.value)
    
    def test_invalid_change_percent(self, db_session):
        """测试无效涨跌幅"""
        with pytest.raises(ValidationError) as exc_info:
            StockPrice(
                stock_code='000001',
                current_price=10.0,
                change_percent=150.0,  # 超过100%
                record_date=date.today()
            )
        assert '涨跌幅必须在-100%到100%之间' in str(exc_info.value)
    
    def test_update_or_create(self, db_session):
        """测试更新或创建价格记录"""
        # 第一次创建
        price1 = StockPrice.update_or_create(
            stock_code='000001',
            stock_name='平安银行',
            current_price=10.0,
            change_percent=1.0,
            record_date=date.today()
        )
        assert price1.id is not None
        
        # 第二次更新
        price2 = StockPrice.update_or_create(
            stock_code='000001',
            stock_name='平安银行',
            current_price=10.5,
            change_percent=5.0,
            record_date=date.today()
        )
        
        # 应该是同一条记录
        assert price1.id == price2.id
        assert float(price2.current_price) == 10.5
    
    def test_get_latest_price(self, db_session, sample_stock_price_data):
        """测试获取最新价格"""
        price = StockPrice(**sample_stock_price_data)
        price.save()
        
        latest = StockPrice.get_latest_price('000001')
        assert latest is not None
        assert latest.stock_code == '000001'


class TestSectorData:
    """板块数据模型测试"""
    
    def test_create_valid_sector_data(self, db_session, sample_sector_data):
        """测试创建有效的板块数据"""
        sector = SectorData(**sample_sector_data)
        sector.save()
        
        assert sector.id is not None
        assert sector.sector_name == '银行'
        assert float(sector.change_percent) == 1.85
        assert sector.rank_position == 5
    
    def test_empty_sector_name(self, db_session):
        """测试空板块名称"""
        with pytest.raises(ValidationError) as exc_info:
            SectorData(
                sector_name='',
                change_percent=1.0,
                record_date=date.today()
            )
        assert '板块名称不能为空' in str(exc_info.value)
    
    def test_invalid_change_percent(self, db_session):
        """测试无效涨跌幅"""
        with pytest.raises(ValidationError) as exc_info:
            SectorData(
                sector_name='银行',
                change_percent=150.0,
                record_date=date.today()
            )
        assert '涨跌幅必须在-100%到100%之间' in str(exc_info.value)
    
    def test_invalid_rank_position(self, db_session):
        """测试无效排名位置"""
        with pytest.raises(ValidationError) as exc_info:
            SectorData(
                sector_name='银行',
                change_percent=1.0,
                record_date=date.today(),
                rank_position=0
            )
        assert '排名位置必须大于0' in str(exc_info.value)
    
    def test_invalid_volume(self, db_session):
        """测试无效成交量"""
        with pytest.raises(ValidationError) as exc_info:
            SectorData(
                sector_name='银行',
                change_percent=1.0,
                record_date=date.today(),
                volume=-1000
            )
        assert '成交量不能为负数' in str(exc_info.value)
    
    def test_get_latest_ranking(self, db_session, sample_sector_data):
        """测试获取最新排名"""
        sector = SectorData(**sample_sector_data)
        sector.save()
        
        ranking = SectorData.get_latest_ranking()
        assert len(ranking) == 1
        assert ranking[0].sector_name == '银行'
    
    def test_has_data_for_date(self, db_session, sample_sector_data):
        """测试检查日期数据"""
        sector = SectorData(**sample_sector_data)
        sector.save()
        
        assert SectorData.has_data_for_date(date(2024, 1, 16)) == True
        assert SectorData.has_data_for_date(date(2024, 1, 17)) == False


class TestTradingStrategy:
    """交易策略模型测试"""
    
    def test_create_valid_trading_strategy(self, db_session, sample_trading_strategy_data):
        """测试创建有效的交易策略"""
        strategy = TradingStrategy(**sample_trading_strategy_data)
        strategy.save()
        
        assert strategy.id is not None
        assert strategy.strategy_name == '测试策略'
        assert strategy.is_active == True
        assert len(strategy.rules_list['rules']) == 1
    
    def test_empty_strategy_name(self, db_session):
        """测试空策略名称"""
        with pytest.raises(ValidationError) as exc_info:
            TradingStrategy(
                strategy_name='',
                rules='{"rules": []}'
            )
        assert '策略名称不能为空' in str(exc_info.value)
    
    def test_empty_rules(self, db_session):
        """测试空策略规则"""
        with pytest.raises(ValidationError) as exc_info:
            TradingStrategy(
                strategy_name='测试策略',
                rules=''
            )
        assert '策略规则不能为空' in str(exc_info.value)
    
    def test_invalid_json_rules(self, db_session):
        """测试无效JSON规则"""
        with pytest.raises(ValidationError) as exc_info:
            TradingStrategy(
                strategy_name='测试策略',
                rules='invalid json'
            )
        assert '策略规则必须是有效的JSON格式' in str(exc_info.value)
    
    def test_activate_deactivate(self, db_session, sample_trading_strategy_data):
        """测试激活和停用策略"""
        strategy = TradingStrategy(**sample_trading_strategy_data)
        strategy.save()
        
        # 停用策略
        strategy.deactivate()
        assert strategy.is_active == False
        
        # 激活策略
        strategy.activate()
        assert strategy.is_active == True
    
    def test_get_active_strategies(self, db_session, sample_trading_strategy_data):
        """测试获取激活的策略"""
        strategy = TradingStrategy(**sample_trading_strategy_data)
        strategy.save()
        
        active_strategies = TradingStrategy.get_active_strategies()
        assert len(active_strategies) == 1
        assert active_strategies[0].strategy_name == '测试策略'


class TestConfiguration:
    """配置模型测试"""
    
    def test_create_valid_configuration(self, db_session, sample_configuration_data):
        """测试创建有效的配置"""
        config = Configuration(**sample_configuration_data)
        config.save()
        
        assert config.id is not None
        assert config.config_key == 'test_config'
        assert config.config_value == '["选项1", "选项2", "选项3"]'
    
    def test_empty_config_key(self, db_session):
        """测试空配置键"""
        with pytest.raises(ValidationError) as exc_info:
            Configuration(
                config_key='',
                config_value='test_value'
            )
        assert '配置键不能为空' in str(exc_info.value)
    
    def test_none_config_value(self, db_session):
        """测试空配置值"""
        with pytest.raises(ValidationError) as exc_info:
            Configuration(
                config_key='test_key',
                config_value=None
            )
        assert '配置值不能为空' in str(exc_info.value)
    
    def test_get_set_value(self, db_session):
        """测试获取和设置配置值"""
        # 设置配置值
        config = Configuration.set_value('test_key', ['选项1', '选项2'], '测试配置')
        assert config.config_key == 'test_key'
        
        # 获取配置值
        value = Configuration.get_value('test_key')
        assert value == ['选项1', '选项2']
        
        # 获取不存在的配置
        value = Configuration.get_value('nonexistent', 'default')
        assert value == 'default'
    
    def test_buy_sell_reasons(self, db_session):
        """测试买入卖出原因配置"""
        buy_reasons = ['原因1', '原因2']
        sell_reasons = ['原因A', '原因B']
        
        Configuration.set_buy_reasons(buy_reasons)
        Configuration.set_sell_reasons(sell_reasons)
        
        assert Configuration.get_buy_reasons() == buy_reasons
        assert Configuration.get_sell_reasons() == sell_reasons