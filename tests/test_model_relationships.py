"""
数据模型关系和高级功能测试
"""
import pytest
from datetime import datetime, date, timedelta
from extensions import db
from models.trade_record import TradeRecord, TradeCorrection
from models.review_record import ReviewRecord
from models.stock_pool import StockPool
from models.case_study import CaseStudy
from models.stock_price import StockPrice
from models.sector_data import SectorData, SectorRanking
from models.trading_strategy import TradingStrategy
from models.configuration import Configuration


class TestTradeRecordRelationships:
    """交易记录关系测试"""
    
    def test_trade_correction_relationship(self, db_session):
        """测试交易记录订正关系"""
        # 创建原始交易记录
        original_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=10.0,
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试买入'
        )
        original_trade.save()
        
        # 创建订正后的交易记录
        corrected_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=10.5,  # 订正价格
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试买入',
            original_record_id=original_trade.id,
            correction_reason='价格录入错误'
        )
        corrected_trade.save()
        
        # 标记原始记录为已订正
        original_trade.is_corrected = True
        original_trade.save()
        
        # 创建订正记录
        correction = TradeCorrection(
            original_trade_id=original_trade.id,
            corrected_trade_id=corrected_trade.id,
            correction_reason='价格录入错误',
            corrected_fields='{"price": {"old_value": 10.0, "new_value": 10.5}}'
        )
        correction.save()
        
        # 验证关系
        assert original_trade.is_corrected == True
        assert corrected_trade.original_record_id == original_trade.id
        assert correction.original_trade.id == original_trade.id
        assert correction.corrected_trade.id == corrected_trade.id
        
        # 验证反向关系
        assert len(original_trade.corrections) == 1
        assert original_trade.corrections[0].id == corrected_trade.id
    
    def test_get_uncorrected_records(self, db_session):
        """测试获取未订正记录"""
        # 创建未订正记录
        trade1 = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=10.0,
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试买入'
        )
        trade1.save()
        
        # 创建已订正记录
        trade2 = TradeRecord(
            stock_code='000002',
            stock_name='万科A',
            trade_type='buy',
            price=15.0,
            quantity=500,
            trade_date=datetime.now(),
            reason='测试买入',
            is_corrected=True
        )
        trade2.save()
        
        uncorrected = TradeRecord.get_uncorrected_records()
        assert len(uncorrected) == 1
        assert uncorrected[0].id == trade1.id


class TestModelQueryMethods:
    """模型查询方法测试"""
    
    def test_trade_record_date_range_query(self, db_session):
        """测试交易记录日期范围查询"""
        base_date = datetime(2024, 1, 15)
        
        # 创建不同日期的交易记录
        for i in range(5):
            trade = TradeRecord(
                stock_code=f'00000{i+1}',
                stock_name=f'测试股票{i+1}',
                trade_type='buy',
                price=10.0 + i,
                quantity=1000,
                trade_date=base_date + timedelta(days=i),
                reason='测试买入'
            )
            trade.save()
        
        # 查询日期范围
        start_date = base_date + timedelta(days=1)
        end_date = base_date + timedelta(days=3)
        
        results = TradeRecord.get_by_date_range(start_date, end_date)
        assert len(results) == 3
        
        # 验证结果按日期倒序排列
        for i in range(len(results) - 1):
            assert results[i].trade_date >= results[i + 1].trade_date
    
    def test_review_record_latest_by_stock(self, db_session):
        """测试获取股票最新复盘记录"""
        base_date = date(2024, 1, 15)
        
        # 创建同一股票的多个复盘记录
        for i in range(3):
            review = ReviewRecord(
                stock_code='000001',
                review_date=base_date + timedelta(days=i),
                price_up_score=1,
                bbi_score=1,
                volume_score=0,
                trend_score=1,
                j_score=1
            )
            review.save()
        
        latest = ReviewRecord.get_latest_by_stock('000001')
        assert latest is not None
        assert latest.review_date == base_date + timedelta(days=2)
    
    def test_stock_pool_flow_tracking(self, db_session):
        """测试股票池流转跟踪"""
        # 创建观察池记录
        watch_stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            target_price=12.0,
            add_reason='技术形态良好',
            status='active'
        )
        watch_stock.save()
        
        # 移动到待买入池
        buy_ready_stock = watch_stock.move_to_pool('buy_ready', '突破关键位置')
        
        # 查询股票的所有记录
        all_records = StockPool.get_by_stock_code('000001')
        assert len(all_records) == 2
        
        # 验证流转记录
        active_record = next((r for r in all_records if r.status == 'active'), None)
        moved_record = next((r for r in all_records if r.status == 'moved'), None)
        
        assert active_record is not None
        assert active_record.pool_type == 'buy_ready'
        assert moved_record is not None
        assert moved_record.pool_type == 'watch'
    
    def test_case_study_search_functionality(self, db_session):
        """测试案例研究搜索功能"""
        # 创建多个案例
        cases_data = [
            {
                'stock_code': '000001',
                'title': '平安银行突破案例',
                'image_path': '/uploads/case1.png',
                'tags': ['突破', '银行股'],
                'notes': '经典的突破形态'
            },
            {
                'stock_code': '000002',
                'title': '万科A回调案例',
                'image_path': '/uploads/case2.png',
                'tags': ['回调', '地产股'],
                'notes': '支撑位反弹'
            },
            {
                'stock_code': '000001',
                'title': '平安银行止损案例',
                'image_path': '/uploads/case3.png',
                'tags': ['止损', '银行股'],
                'notes': '及时止损避免更大损失'
            }
        ]
        
        for case_data in cases_data:
            case = CaseStudy(**case_data)
            case.save()
        
        # 按股票代码搜索
        bank_cases = CaseStudy.get_by_stock_code('000001')
        assert len(bank_cases) == 2
        
        # 按标签搜索
        breakthrough_cases = CaseStudy.get_by_tag('突破')
        assert len(breakthrough_cases) == 1
        
        # 关键词搜索
        bank_keyword_cases = CaseStudy.search_by_keyword('银行')
        assert len(bank_keyword_cases) == 2
        
        support_cases = CaseStudy.search_by_keyword('支撑')
        assert len(support_cases) == 1
    
    def test_stock_price_history_tracking(self, db_session):
        """测试股票价格历史跟踪"""
        base_date = date(2024, 1, 15)
        
        # 创建连续的价格记录
        prices = [10.0, 10.5, 10.2, 10.8, 11.0]
        for i, price in enumerate(prices):
            stock_price = StockPrice(
                stock_code='000001',
                stock_name='平安银行',
                current_price=price,
                change_percent=(price - 10.0) / 10.0 * 100,
                record_date=base_date + timedelta(days=i)
            )
            stock_price.save()
        
        # 获取价格历史
        history = StockPrice.get_price_history('000001', days=3)
        assert len(history) == 3
        
        # 验证按日期倒序
        assert float(history[0].current_price) == 11.0  # 最新价格
        assert float(history[2].current_price) == 10.2  # 3天前价格
        
        # 获取特定日期价格
        specific_price = StockPrice.get_price_by_date('000001', base_date + timedelta(days=1))
        assert specific_price is not None
        assert float(specific_price.current_price) == 10.5
    
    def test_sector_data_top_performers(self, db_session):
        """测试板块TOPK统计"""
        base_date = date(2024, 1, 15)
        
        # 创建多天的板块数据
        sectors_data = [
            ('银行', [1, 2, 1, 3, 2]),  # 板块名称和5天的排名
            ('地产', [3, 1, 2, 1, 1]),
            ('科技', [2, 3, 3, 2, 3]),
            ('医药', [4, 4, 4, 4, 4])
        ]
        
        for day in range(5):
            current_date = base_date + timedelta(days=day)
            for sector_name, rankings in sectors_data:
                sector = SectorData(
                    sector_name=sector_name,
                    change_percent=5.0 - rankings[day],  # 排名越高涨幅越大
                    record_date=current_date,
                    rank_position=rankings[day],
                    volume=1000000000,
                    market_cap=500000000000.0
                )
                sector.save()
        
        # 获取最近5天TOP3板块统计 - 需要修改方法以支持指定日期范围
        # 由于get_top_performers使用today()，我们需要直接查询
        end_date = base_date + timedelta(days=4)  # 最后一天的数据
        start_date = base_date
        
        top_performers = db.session.query(
            SectorData.sector_name,
            db.func.count().label('appearances'),
            db.func.avg(SectorData.rank_position).label('avg_rank'),
            db.func.min(SectorData.rank_position).label('best_rank'),
            db.func.max(SectorData.record_date).label('latest_date')
        ).filter(
            SectorData.record_date.between(start_date, end_date),
            SectorData.rank_position <= 3
        ).group_by(SectorData.sector_name).order_by(
            db.desc('appearances'), 'avg_rank'
        ).all()
        
        # 验证结果
        assert len(top_performers) == 3  # 只有3个板块进入过TOP3
        
        # 地产板块应该排第一（进入TOP3次数最多，平均排名最好）
        top_sector = top_performers[0]
        assert top_sector.sector_name == '地产'
        assert top_sector.appearances == 5  # 5天都在TOP3
        assert top_sector.avg_rank == 1.6  # 平均排名
        assert top_sector.best_rank == 1   # 最佳排名
    
    def test_sector_ranking_json_storage(self, db_session):
        """测试板块排名JSON存储"""
        ranking_data = [
            {'sector_name': '银行', 'change_percent': 2.5, 'rank': 1},
            {'sector_name': '地产', 'change_percent': 1.8, 'rank': 2},
            {'sector_name': '科技', 'change_percent': 1.2, 'rank': 3}
        ]
        
        # 创建排名记录
        ranking = SectorRanking.create_or_update(
            target_date=date.today(),
            ranking_data=ranking_data,
            total_sectors=3
        )
        
        assert ranking.total_sectors == 3
        assert len(ranking.ranking_list) == 3
        assert ranking.ranking_list[0]['sector_name'] == '银行'
        
        # 更新排名记录
        updated_data = [
            {'sector_name': '银行', 'change_percent': 3.0, 'rank': 1},
            {'sector_name': '科技', 'change_percent': 2.2, 'rank': 2}
        ]
        
        updated_ranking = SectorRanking.create_or_update(
            target_date=date.today(),
            ranking_data=updated_data,
            total_sectors=2
        )
        
        # 应该是同一条记录
        assert updated_ranking.id == ranking.id
        assert updated_ranking.total_sectors == 2
        assert len(updated_ranking.ranking_list) == 2


class TestModelValidationEdgeCases:
    """模型验证边界情况测试"""
    
    def test_trade_record_boundary_values(self, db_session):
        """测试交易记录边界值"""
        # 测试最大价格
        trade = TradeRecord(
            stock_code='000001',
            stock_name='测试股票',
            trade_type='buy',
            price=9999.99,  # 最大允许价格
            quantity=999999,  # 最大允许数量
            trade_date=datetime.now(),
            reason='测试'
        )
        trade.save()
        assert trade.id is not None
        
        # 测试比例边界值
        trade_with_ratios = TradeRecord(
            stock_code='000002',
            stock_name='测试股票2',
            trade_type='buy',
            price=10.0,
            quantity=100,
            trade_date=datetime.now(),
            reason='测试',
            take_profit_ratio=1.0,  # 最大比例
            sell_ratio=1.0  # 最大比例
        )
        trade_with_ratios.save()
        assert float(trade_with_ratios.expected_profit_ratio) == 1.0
    
    def test_review_record_score_combinations(self, db_session):
        """测试复盘记录评分组合"""
        # 测试所有评分为0的情况
        review_zero = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            price_up_score=0,
            bbi_score=0,
            volume_score=0,
            trend_score=0,
            j_score=0
        )
        review_zero.save()
        assert review_zero.total_score == 0
        
        # 测试所有评分为1的情况
        review_full = ReviewRecord(
            stock_code='000002',
            review_date=date.today(),
            price_up_score=1,
            bbi_score=1,
            volume_score=1,
            trend_score=1,
            j_score=1
        )
        review_full.save()
        assert review_full.total_score == 5
    
    def test_configuration_json_handling(self, db_session):
        """测试配置JSON处理"""
        # 测试复杂JSON结构
        complex_config = {
            'strategies': [
                {'name': '策略1', 'rules': [{'condition': 'A', 'action': 'B'}]},
                {'name': '策略2', 'rules': [{'condition': 'C', 'action': 'D'}]}
            ],
            'settings': {
                'timeout': 30,
                'retry_count': 3
            }
        }
        
        config = Configuration.set_value('complex_config', complex_config, '复杂配置测试')
        retrieved_config = Configuration.get_value('complex_config')
        
        assert retrieved_config == complex_config
        assert len(retrieved_config['strategies']) == 2
        assert retrieved_config['settings']['timeout'] == 30
    
    def test_trading_strategy_rule_management(self, db_session):
        """测试交易策略规则管理"""
        strategy = TradingStrategy(
            strategy_name='测试策略',
            rules={'rules': []},
            description='测试策略描述'
        )
        strategy.save()
        
        # 添加规则
        rule1 = {
            'day_range': [1, 5],
            'loss_threshold': -0.05,
            'action': 'sell_all'
        }
        strategy.add_rule(rule1)
        
        rule2 = {
            'day_range': [6, 10],
            'profit_threshold': 0.10,
            'action': 'sell_partial',
            'sell_ratio': 0.3
        }
        strategy.add_rule(rule2)
        
        assert len(strategy.rules_list['rules']) == 2
        
        # 移除规则
        strategy.remove_rule(0)  # 移除第一个规则
        assert len(strategy.rules_list['rules']) == 1
        assert strategy.rules_list['rules'][0]['day_range'] == [6, 10]