"""
数据一致性和完整性测试
测试数据库约束、关系完整性、事务一致性等
"""
import pytest
from datetime import datetime, date, timedelta
from extensions import db
from models.trade_record import TradeRecord
from models.review_record import ReviewRecord
from models.stock_pool import StockPool
from models.case_study import CaseStudy
from models.stock_price import StockPrice
from models.sector_data import SectorData
from models.trading_strategy import TradingStrategy
from models.configuration import Configuration
from sqlalchemy.exc import IntegrityError
import json


class TestDataConsistencyIntegrity:
    """数据一致性和完整性测试"""
    
    def test_trade_record_constraints(self, client, db_session):
        """测试交易记录数据约束"""
        
        # 1. 测试必填字段约束
        with pytest.raises(IntegrityError):
            trade = TradeRecord(
                # 缺少stock_code
                stock_name='测试股票',
                trade_type='buy',
                price=10.00,
                quantity=1000,
                trade_date=datetime.now(),
                reason='测试'
            )
            db_session.add(trade)
            db_session.commit()
        
        db_session.rollback()
        
        # 2. 测试交易类型约束
        with pytest.raises(IntegrityError):
            trade = TradeRecord(
                stock_code='000001',
                stock_name='测试股票',
                trade_type='invalid_type',  # 无效的交易类型
                price=10.00,
                quantity=1000,
                trade_date=datetime.now(),
                reason='测试'
            )
            db_session.add(trade)
            db_session.commit()
        
        db_session.rollback()
        
        # 3. 测试价格和数量的正数约束
        with pytest.raises(IntegrityError):
            trade = TradeRecord(
                stock_code='000001',
                stock_name='测试股票',
                trade_type='buy',
                price=-10.00,  # 负价格
                quantity=1000,
                trade_date=datetime.now(),
                reason='测试'
            )
            db_session.add(trade)
            db_session.commit()
        
        db_session.rollback()
        
        # 4. 测试订正记录的外键约束
        # 先创建原始记录
        original_trade = TradeRecord(
            stock_code='000001',
            stock_name='测试股票',
            trade_type='buy',
            price=10.00,
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试'
        )
        db_session.add(original_trade)
        db_session.commit()
        
        # 创建订正记录
        corrected_trade = TradeRecord(
            stock_code='000001',
            stock_name='测试股票',
            trade_type='buy',
            price=10.50,
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试',
            original_record_id=original_trade.id,
            correction_reason='价格订正'
        )
        db_session.add(corrected_trade)
        db_session.commit()
        
        # 验证外键关系
        assert corrected_trade.original_record_id == original_trade.id
        
        # 5. 测试删除原始记录时的约束（应该失败，因为有订正记录引用）
        with pytest.raises(IntegrityError):
            db_session.delete(original_trade)
            db_session.commit()
        
        db_session.rollback()
        
    def test_review_record_constraints(self, client, db_session):
        """测试复盘记录数据约束"""
        
        # 1. 测试评分范围约束
        with pytest.raises(IntegrityError):
            review = ReviewRecord(
                stock_code='000001',
                review_date=date.today(),
                price_up_score=2,  # 超出范围 (0-1)
                bbi_score=1,
                volume_score=1,
                trend_score=1,
                j_score=1,
                total_score=6,
                analysis='测试',
                decision='hold',
                reason='测试',
                holding_days=5
            )
            db_session.add(review)
            db_session.commit()
        
        db_session.rollback()
        
        # 2. 测试总分范围约束
        with pytest.raises(IntegrityError):
            review = ReviewRecord(
                stock_code='000001',
                review_date=date.today(),
                price_up_score=1,
                bbi_score=1,
                volume_score=1,
                trend_score=1,
                j_score=1,
                total_score=6,  # 超出范围 (0-5)
                analysis='测试',
                decision='hold',
                reason='测试',
                holding_days=5
            )
            db_session.add(review)
            db_session.commit()
        
        db_session.rollback()
        
        # 3. 测试决策类型约束
        with pytest.raises(IntegrityError):
            review = ReviewRecord(
                stock_code='000001',
                review_date=date.today(),
                price_up_score=1,
                bbi_score=1,
                volume_score=1,
                trend_score=1,
                j_score=1,
                total_score=5,
                analysis='测试',
                decision='invalid_decision',  # 无效决策
                reason='测试',
                holding_days=5
            )
            db_session.add(review)
            db_session.commit()
        
        db_session.rollback()
        
        # 4. 测试唯一约束（同一股票同一日期不能重复）
        review1 = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            price_up_score=1,
            bbi_score=1,
            volume_score=1,
            trend_score=1,
            j_score=1,
            total_score=5,
            analysis='测试1',
            decision='hold',
            reason='测试1',
            holding_days=5
        )
        db_session.add(review1)
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            review2 = ReviewRecord(
                stock_code='000001',
                review_date=date.today(),  # 同一日期
                price_up_score=0,
                bbi_score=0,
                volume_score=0,
                trend_score=0,
                j_score=0,
                total_score=0,
                analysis='测试2',
                decision='sell_all',
                reason='测试2',
                holding_days=6
            )
            db_session.add(review2)
            db_session.commit()
        
        db_session.rollback()
        
    def test_stock_pool_constraints(self, client, db_session):
        """测试股票池数据约束"""
        
        # 1. 测试池类型约束
        with pytest.raises(IntegrityError):
            pool = StockPool(
                stock_code='000001',
                stock_name='测试股票',
                pool_type='invalid_type',  # 无效池类型
                target_price=10.00,
                add_reason='测试',
                status='active'
            )
            db_session.add(pool)
            db_session.commit()
        
        db_session.rollback()
        
        # 2. 测试状态约束
        with pytest.raises(IntegrityError):
            pool = StockPool(
                stock_code='000001',
                stock_name='测试股票',
                pool_type='watch',
                target_price=10.00,
                add_reason='测试',
                status='invalid_status'  # 无效状态
            )
            db_session.add(pool)
            db_session.commit()
        
        db_session.rollback()
        
        # 3. 测试目标价格的正数约束
        with pytest.raises(IntegrityError):
            pool = StockPool(
                stock_code='000001',
                stock_name='测试股票',
                pool_type='watch',
                target_price=-10.00,  # 负价格
                add_reason='测试',
                status='active'
            )
            db_session.add(pool)
            db_session.commit()
        
        db_session.rollback()
        
    def test_stock_price_constraints(self, client, db_session):
        """测试股票价格数据约束"""
        
        # 1. 测试唯一约束（同一股票同一日期不能重复）
        price1 = StockPrice(
            stock_code='000001',
            stock_name='测试股票',
            current_price=10.00,
            change_percent=2.5,
            record_date=date.today()
        )
        db_session.add(price1)
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            price2 = StockPrice(
                stock_code='000001',
                stock_name='测试股票',
                current_price=10.50,
                change_percent=3.0,
                record_date=date.today()  # 同一日期
            )
            db_session.add(price2)
            db_session.commit()
        
        db_session.rollback()
        
        # 2. 测试价格的正数约束
        with pytest.raises(IntegrityError):
            price = StockPrice(
                stock_code='000001',
                stock_name='测试股票',
                current_price=-10.00,  # 负价格
                change_percent=2.5,
                record_date=date.today()
            )
            db_session.add(price)
            db_session.commit()
        
        db_session.rollback()
        
    def test_sector_data_constraints(self, client, db_session):
        """测试板块数据约束"""
        
        # 1. 测试唯一约束（同一板块同一日期不能重复）
        sector1 = SectorData(
            sector_name='银行',
            sector_code='BK0475',
            change_percent=2.15,
            record_date=date.today(),
            rank_position=1,
            volume=1500000000,
            market_cap=850000000000.0
        )
        db_session.add(sector1)
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            sector2 = SectorData(
                sector_name='银行',  # 同一板块
                sector_code='BK0475',
                change_percent=2.25,
                record_date=date.today(),  # 同一日期
                rank_position=2,
                volume=1600000000,
                market_cap=860000000000.0
            )
            db_session.add(sector2)
            db_session.commit()
        
        db_session.rollback()
        
        # 2. 测试排名位置的正数约束
        with pytest.raises(IntegrityError):
            sector = SectorData(
                sector_name='银行',
                sector_code='BK0475',
                change_percent=2.15,
                record_date=date.today(),
                rank_position=-1,  # 负排名
                volume=1500000000,
                market_cap=850000000000.0
            )
            db_session.add(sector)
            db_session.commit()
        
        db_session.rollback()
        
    def test_data_relationships_integrity(self, client, db_session):
        """测试数据关系完整性"""
        
        # 1. 测试交易记录和复盘记录的关系
        # 创建买入记录
        buy_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=10.00,
            quantity=1000,
            trade_date=datetime.now() - timedelta(days=5),
            reason='测试买入'
        )
        db_session.add(buy_trade)
        db_session.commit()
        
        # 创建复盘记录
        review = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            price_up_score=1,
            bbi_score=1,
            volume_score=1,
            trend_score=1,
            j_score=1,
            total_score=5,
            analysis='测试复盘',
            decision='hold',
            reason='继续持有',
            holding_days=5
        )
        db_session.add(review)
        db_session.commit()
        
        # 验证可以通过股票代码关联查询
        trades = db_session.query(TradeRecord).filter_by(stock_code='000001').all()
        reviews = db_session.query(ReviewRecord).filter_by(stock_code='000001').all()
        
        assert len(trades) == 1
        assert len(reviews) == 1
        assert trades[0].stock_code == reviews[0].stock_code
        
        # 2. 测试持仓计算的一致性
        # 添加卖出记录
        sell_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='sell',
            price=12.00,
            quantity=300,
            trade_date=datetime.now() - timedelta(days=2),
            reason='部分止盈'
        )
        db_session.add(sell_trade)
        db_session.commit()
        
        # 计算持仓
        all_trades = db_session.query(TradeRecord).filter_by(stock_code='000001').all()
        total_buy = sum(t.quantity for t in all_trades if t.trade_type == 'buy')
        total_sell = sum(t.quantity for t in all_trades if t.trade_type == 'sell')
        holding_quantity = total_buy - total_sell
        
        assert holding_quantity == 700  # 1000 - 300
        
        # 3. 测试价格数据和交易记录的时间一致性
        price = StockPrice(
            stock_code='000001',
            stock_name='平安银行',
            current_price=11.50,
            change_percent=15.0,
            record_date=date.today()
        )
        db_session.add(price)
        db_session.commit()
        
        # 验证价格记录日期不早于最后交易日期
        latest_trade = db_session.query(TradeRecord).filter_by(stock_code='000001').order_by(TradeRecord.trade_date.desc()).first()
        price_record = db_session.query(StockPrice).filter_by(stock_code='000001').first()
        
        assert price_record.record_date >= latest_trade.trade_date.date()
        
    def test_transaction_consistency(self, client, db_session):
        """测试事务一致性"""
        
        # 1. 测试事务回滚
        try:
            # 开始事务
            trade1 = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=10.00,
                quantity=1000,
                trade_date=datetime.now(),
                reason='测试买入1'
            )
            db_session.add(trade1)
            
            trade2 = TradeRecord(
                stock_code='000002',
                stock_name='万科A',
                trade_type='buy',
                price=15.00,
                quantity=500,
                trade_date=datetime.now(),
                reason='测试买入2'
            )
            db_session.add(trade2)
            
            # 故意创建一个会失败的记录
            invalid_trade = TradeRecord(
                stock_code='000003',
                stock_name='招商银行',
                trade_type='invalid_type',  # 无效类型，会导致失败
                price=20.00,
                quantity=800,
                trade_date=datetime.now(),
                reason='测试买入3'
            )
            db_session.add(invalid_trade)
            
            # 提交事务（应该失败）
            db_session.commit()
            
        except IntegrityError:
            # 事务回滚
            db_session.rollback()
            
            # 验证所有记录都没有被保存
            trades = db_session.query(TradeRecord).all()
            assert len(trades) == 0
        
        # 2. 测试成功的事务
        trade1 = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=10.00,
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试买入1'
        )
        db_session.add(trade1)
        
        trade2 = TradeRecord(
            stock_code='000002',
            stock_name='万科A',
            trade_type='buy',
            price=15.00,
            quantity=500,
            trade_date=datetime.now(),
            reason='测试买入2'
        )
        db_session.add(trade2)
        
        db_session.commit()
        
        # 验证记录都被保存
        trades = db_session.query(TradeRecord).all()
        assert len(trades) == 2
        
    def test_data_validation_consistency(self, client, db_session):
        """测试数据验证一致性"""
        
        # 1. 测试止损止盈计算的一致性
        trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=10.00,
            quantity=1000,
            trade_date=datetime.now(),
            reason='测试买入',
            stop_loss_price=9.00,
            take_profit_ratio=0.20,
            sell_ratio=0.50
        )
        
        # 手动计算预期值
        expected_loss_ratio = (10.00 - 9.00) / 10.00  # 0.1
        expected_profit_ratio = 0.20 * 0.50  # 0.1
        
        trade.expected_loss_ratio = expected_loss_ratio
        trade.expected_profit_ratio = expected_profit_ratio
        
        db_session.add(trade)
        db_session.commit()
        
        # 验证计算结果
        saved_trade = db_session.query(TradeRecord).filter_by(stock_code='000001').first()
        assert abs(saved_trade.expected_loss_ratio - 0.1) < 0.001
        assert abs(saved_trade.expected_profit_ratio - 0.1) < 0.001
        
        # 2. 测试复盘总分计算的一致性
        review = ReviewRecord(
            stock_code='000001',
            review_date=date.today(),
            price_up_score=1,
            bbi_score=1,
            volume_score=0,
            trend_score=1,
            j_score=1,
            analysis='测试复盘',
            decision='hold',
            reason='继续持有',
            holding_days=5
        )
        
        # 计算总分
        total_score = (review.price_up_score + review.bbi_score + 
                      review.volume_score + review.trend_score + review.j_score)
        review.total_score = total_score
        
        db_session.add(review)
        db_session.commit()
        
        # 验证总分计算
        saved_review = db_session.query(ReviewRecord).filter_by(stock_code='000001').first()
        assert saved_review.total_score == 4
        
        # 3. 测试持仓数量计算的一致性
        # 添加更多交易记录
        trades_data = [
            ('buy', 10.00, 1000),
            ('buy', 11.00, 500),
            ('sell', 12.00, 300),
            ('sell', 13.00, 200)
        ]
        
        for trade_type, price, quantity in trades_data:
            trade = TradeRecord(
                stock_code='000002',
                stock_name='万科A',
                trade_type=trade_type,
                price=price,
                quantity=quantity,
                trade_date=datetime.now(),
                reason=f'测试{trade_type}'
            )
            db_session.add(trade)
        
        db_session.commit()
        
        # 计算持仓
        all_trades = db_session.query(TradeRecord).filter_by(stock_code='000002').all()
        total_buy = sum(t.quantity for t in all_trades if t.trade_type == 'buy')
        total_sell = sum(t.quantity for t in all_trades if t.trade_type == 'sell')
        holding_quantity = total_buy - total_sell
        
        assert total_buy == 1500  # 1000 + 500
        assert total_sell == 500   # 300 + 200
        assert holding_quantity == 1000  # 1500 - 500
        
    def test_configuration_data_integrity(self, client, db_session):
        """测试配置数据完整性"""
        
        # 1. 测试配置键的唯一性
        config1 = Configuration(
            config_key='test_config',
            config_value='["选项1", "选项2"]',
            description='测试配置'
        )
        db_session.add(config1)
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            config2 = Configuration(
                config_key='test_config',  # 重复的键
                config_value='["选项3", "选项4"]',
                description='重复配置'
            )
            db_session.add(config2)
            db_session.commit()
        
        db_session.rollback()
        
        # 2. 测试JSON格式验证
        config = Configuration(
            config_key='json_config',
            config_value='["选项1", "选项2", "选项3"]',
            description='JSON配置测试'
        )
        db_session.add(config)
        db_session.commit()
        
        # 验证可以解析JSON
        saved_config = db_session.query(Configuration).filter_by(config_key='json_config').first()
        try:
            parsed_value = json.loads(saved_config.config_value)
            assert isinstance(parsed_value, list)
            assert len(parsed_value) == 3
        except json.JSONDecodeError:
            pytest.fail("配置值不是有效的JSON格式")
        
    def test_cascade_operations(self, client, db_session):
        """测试级联操作"""
        
        # 1. 测试订正记录的级联关系
        # 创建原始记录
        original_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=10.00,
            quantity=1000,
            trade_date=datetime.now(),
            reason='原始记录'
        )
        db_session.add(original_trade)
        db_session.commit()
        
        # 创建订正记录
        corrected_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=10.50,
            quantity=1000,
            trade_date=datetime.now(),
            reason='订正记录',
            original_record_id=original_trade.id,
            correction_reason='价格订正'
        )
        db_session.add(corrected_trade)
        db_session.commit()
        
        # 验证关系
        assert corrected_trade.original_record_id == original_trade.id
        
        # 2. 测试数据更新的一致性
        # 更新原始记录状态
        original_trade.is_corrected = True
        db_session.commit()
        
        # 验证更新
        updated_trade = db_session.query(TradeRecord).get(original_trade.id)
        assert updated_trade.is_corrected == True
        
        # 验证订正记录仍然存在且关系正确
        correction = db_session.query(TradeRecord).get(corrected_trade.id)
        assert correction.original_record_id == original_trade.id
        
    def test_data_archival_consistency(self, client, db_session):
        """测试数据归档一致性"""
        
        # 1. 创建历史数据
        historical_dates = [date.today() - timedelta(days=i) for i in range(30, 0, -1)]
        
        for i, test_date in enumerate(historical_dates):
            # 创建交易记录
            trade = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy' if i % 2 == 0 else 'sell',
                price=10.00 + i * 0.1,
                quantity=100 * (i + 1),
                trade_date=datetime.combine(test_date, datetime.min.time()),
                reason=f'历史交易{i}'
            )
            db_session.add(trade)
            
            # 创建价格记录
            if i % 3 == 0:  # 每3天一个价格记录
                price = StockPrice(
                    stock_code='000001',
                    stock_name='平安银行',
                    current_price=10.00 + i * 0.1,
                    change_percent=i * 0.1,
                    record_date=test_date
                )
                db_session.add(price)
        
        db_session.commit()
        
        # 2. 验证数据完整性
        all_trades = db_session.query(TradeRecord).filter_by(stock_code='000001').all()
        all_prices = db_session.query(StockPrice).filter_by(stock_code='000001').all()
        
        assert len(all_trades) == 30
        assert len(all_prices) == 10  # 30/3 = 10
        
        # 3. 验证时间序列的一致性
        trades_by_date = sorted(all_trades, key=lambda x: x.trade_date)
        prices_by_date = sorted(all_prices, key=lambda x: x.record_date)
        
        # 验证交易记录时间顺序
        for i in range(1, len(trades_by_date)):
            assert trades_by_date[i].trade_date >= trades_by_date[i-1].trade_date
        
        # 验证价格记录时间顺序
        for i in range(1, len(prices_by_date)):
            assert prices_by_date[i].record_date >= prices_by_date[i-1].record_date
        
        # 4. 验证数据范围查询的一致性
        start_date = date.today() - timedelta(days=15)
        end_date = date.today() - timedelta(days=5)
        
        range_trades = db_session.query(TradeRecord).filter(
            TradeRecord.stock_code == '000001',
            TradeRecord.trade_date >= datetime.combine(start_date, datetime.min.time()),
            TradeRecord.trade_date <= datetime.combine(end_date, datetime.max.time())
        ).all()
        
        range_prices = db_session.query(StockPrice).filter(
            StockPrice.stock_code == '000001',
            StockPrice.record_date >= start_date,
            StockPrice.record_date <= end_date
        ).all()
        
        # 验证范围查询结果
        assert len(range_trades) == 11  # 15-5+1 = 11天
        assert len(range_prices) >= 3   # 至少3个价格记录
        
        # 验证所有记录都在指定范围内
        for trade in range_trades:
            assert start_date <= trade.trade_date.date() <= end_date
        
        for price in range_prices:
            assert start_date <= price.record_date <= end_date