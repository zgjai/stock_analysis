"""
历史交易记录相关模型单元测试
"""
import pytest
import json
from datetime import datetime, date
from decimal import Decimal
from models.historical_trade import HistoricalTrade
from models.trade_review import TradeReview, ReviewImage
from error_handlers import ValidationError


class TestHistoricalTrade:
    """历史交易记录模型测试"""
    
    def test_create_valid_historical_trade(self, db_session):
        """测试创建有效的历史交易记录"""
        trade_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'buy_date': datetime(2024, 1, 15),
            'sell_date': datetime(2024, 2, 15),
            'holding_days': 31,
            'total_investment': Decimal('10000.00'),
            'total_return': Decimal('1500.00'),
            'return_rate': Decimal('0.1500'),
            'buy_records_ids': json.dumps([1, 2, 3]),
            'sell_records_ids': json.dumps([4, 5]),
            'completion_date': datetime(2024, 2, 15)
        }
        
        trade = HistoricalTrade(**trade_data)
        trade.save()
        
        assert trade.id is not None
        assert trade.stock_code == '000001'
        assert trade.stock_name == '平安银行'
        assert trade.holding_days == 31
        assert float(trade.total_investment) == 10000.00
        assert float(trade.total_return) == 1500.00
        assert float(trade.return_rate) == 0.1500
        assert trade.is_completed == True
    
    def test_invalid_stock_code(self, db_session):
        """测试无效股票代码"""
        with pytest.raises(ValidationError) as exc_info:
            HistoricalTrade(
                stock_code='INVALID',
                stock_name='测试股票',
                buy_date=datetime(2024, 1, 15),
                sell_date=datetime(2024, 2, 15),
                holding_days=31,
                total_investment=Decimal('10000.00'),
                total_return=Decimal('1500.00'),
                return_rate=Decimal('0.1500'),
                completion_date=datetime(2024, 2, 15)
            )
        assert '股票代码格式不正确' in str(exc_info.value)
    
    def test_invalid_total_investment(self, db_session):
        """测试无效总投入本金"""
        with pytest.raises(ValidationError) as exc_info:
            HistoricalTrade(
                stock_code='000001',
                stock_name='平安银行',
                buy_date=datetime(2024, 1, 15),
                sell_date=datetime(2024, 2, 15),
                holding_days=31,
                total_investment=Decimal('-1000.00'),  # 负数投入
                total_return=Decimal('1500.00'),
                return_rate=Decimal('0.1500'),
                completion_date=datetime(2024, 2, 15)
            )
        assert '总投入本金必须大于0' in str(exc_info.value)
    
    def test_invalid_holding_days(self, db_session):
        """测试无效持仓天数"""
        with pytest.raises(ValidationError) as exc_info:
            HistoricalTrade(
                stock_code='000001',
                stock_name='平安银行',
                buy_date=datetime(2024, 1, 15),
                sell_date=datetime(2024, 2, 15),
                holding_days=-5,  # 负数持仓天数
                total_investment=Decimal('10000.00'),
                total_return=Decimal('1500.00'),
                return_rate=Decimal('0.1500'),
                completion_date=datetime(2024, 2, 15)
            )
        assert '持仓天数不能为负数' in str(exc_info.value)
    
    def test_invalid_date_order(self, db_session):
        """测试无效日期顺序"""
        with pytest.raises(ValidationError) as exc_info:
            HistoricalTrade(
                stock_code='000001',
                stock_name='平安银行',
                buy_date=datetime(2024, 2, 15),
                sell_date=datetime(2024, 1, 15),  # 卖出日期早于买入日期
                holding_days=31,
                total_investment=Decimal('10000.00'),
                total_return=Decimal('1500.00'),
                return_rate=Decimal('0.1500'),
                completion_date=datetime(2024, 2, 15)
            )
        assert '卖出日期不能早于买入日期' in str(exc_info.value)
    
    def test_invalid_records_ids_format(self, db_session):
        """测试无效记录ID格式"""
        with pytest.raises(ValidationError) as exc_info:
            HistoricalTrade(
                stock_code='000001',
                stock_name='平安银行',
                buy_date=datetime(2024, 1, 15),
                sell_date=datetime(2024, 2, 15),
                holding_days=31,
                total_investment=Decimal('10000.00'),
                total_return=Decimal('1500.00'),
                return_rate=Decimal('0.1500'),
                buy_records_ids='invalid json',  # 无效JSON格式
                completion_date=datetime(2024, 2, 15)
            )
        assert 'buy_records_ids必须是有效的JSON格式' in str(exc_info.value)
    
    def test_records_ids_properties(self, db_session):
        """测试记录ID列表属性"""
        trade = HistoricalTrade(
            stock_code='000001',
            stock_name='平安银行',
            buy_date=datetime(2024, 1, 15),
            sell_date=datetime(2024, 2, 15),
            holding_days=31,
            total_investment=Decimal('10000.00'),
            total_return=Decimal('1500.00'),
            return_rate=Decimal('0.1500'),
            completion_date=datetime(2024, 2, 15)
        )
        
        # 测试设置和获取买入记录ID列表
        buy_ids = [1, 2, 3]
        trade.buy_records_list = buy_ids
        assert trade.buy_records_list == buy_ids
        assert json.loads(trade.buy_records_ids) == buy_ids
        
        # 测试设置和获取卖出记录ID列表
        sell_ids = [4, 5]
        trade.sell_records_list = sell_ids
        assert trade.sell_records_list == sell_ids
        assert json.loads(trade.sell_records_ids) == sell_ids
    
    def test_get_by_stock_code(self, db_session):
        """测试根据股票代码查询"""
        trade1 = HistoricalTrade(
            stock_code='000001',
            stock_name='平安银行',
            buy_date=datetime(2024, 1, 15),
            sell_date=datetime(2024, 2, 15),
            holding_days=31,
            total_investment=Decimal('10000.00'),
            total_return=Decimal('1500.00'),
            return_rate=Decimal('0.1500'),
            completion_date=datetime(2024, 2, 15)
        )
        trade1.save()
        
        trade2 = HistoricalTrade(
            stock_code='000002',
            stock_name='万科A',
            buy_date=datetime(2024, 1, 20),
            sell_date=datetime(2024, 2, 20),
            holding_days=31,
            total_investment=Decimal('8000.00'),
            total_return=Decimal('-800.00'),
            return_rate=Decimal('-0.1000'),
            completion_date=datetime(2024, 2, 20)
        )
        trade2.save()
        
        results = HistoricalTrade.get_by_stock_code('000001')
        assert len(results) == 1
        assert results[0].stock_code == '000001'
    
    def test_get_profitable_and_loss_trades(self, db_session):
        """测试获取盈利和亏损交易"""
        # 创建盈利交易
        profitable_trade = HistoricalTrade(
            stock_code='000001',
            stock_name='平安银行',
            buy_date=datetime(2024, 1, 15),
            sell_date=datetime(2024, 2, 15),
            holding_days=31,
            total_investment=Decimal('10000.00'),
            total_return=Decimal('1500.00'),
            return_rate=Decimal('0.1500'),
            completion_date=datetime(2024, 2, 15)
        )
        profitable_trade.save()
        
        # 创建亏损交易
        loss_trade = HistoricalTrade(
            stock_code='000002',
            stock_name='万科A',
            buy_date=datetime(2024, 1, 20),
            sell_date=datetime(2024, 2, 20),
            holding_days=31,
            total_investment=Decimal('8000.00'),
            total_return=Decimal('-800.00'),
            return_rate=Decimal('-0.1000'),
            completion_date=datetime(2024, 2, 20)
        )
        loss_trade.save()
        
        # 测试获取盈利交易
        profitable_trades = HistoricalTrade.get_profitable_trades()
        assert len(profitable_trades) == 1
        assert profitable_trades[0].stock_code == '000001'
        
        # 测试获取亏损交易
        loss_trades = HistoricalTrade.get_loss_trades()
        assert len(loss_trades) == 1
        assert loss_trades[0].stock_code == '000002'
    
    def test_calculate_metrics(self, db_session):
        """测试计算交易指标"""
        trade = HistoricalTrade(
            stock_code='000001',
            stock_name='平安银行',
            buy_date=datetime(2024, 1, 15),
            sell_date=datetime(2024, 2, 15),
            holding_days=31,
            total_investment=Decimal('10000.00'),
            total_return=Decimal('1500.00'),
            return_rate=Decimal('0.1500'),
            completion_date=datetime(2024, 2, 15)
        )
        
        metrics = trade.calculate_metrics()
        
        assert metrics['total_investment'] == 10000.00
        assert metrics['total_return'] == 1500.00
        assert metrics['return_rate'] == 0.1500
        assert metrics['holding_days'] == 31
        assert metrics['is_profitable'] == True
        assert abs(metrics['daily_return_rate'] - (0.1500 / 31)) < 0.0001
    
    def test_to_dict(self, db_session):
        """测试转换为字典"""
        trade = HistoricalTrade(
            stock_code='000001',
            stock_name='平安银行',
            buy_date=datetime(2024, 1, 15),
            sell_date=datetime(2024, 2, 15),
            holding_days=31,
            total_investment=Decimal('10000.00'),
            total_return=Decimal('1500.00'),
            return_rate=Decimal('0.1500'),
            buy_records_ids=json.dumps([1, 2, 3]),
            sell_records_ids=json.dumps([4, 5]),
            completion_date=datetime(2024, 2, 15)
        )
        trade.save()
        
        trade_dict = trade.to_dict()
        
        assert trade_dict['stock_code'] == '000001'
        assert isinstance(trade_dict['total_investment'], float)
        assert isinstance(trade_dict['total_return'], float)
        assert isinstance(trade_dict['return_rate'], float)
        assert trade_dict['buy_records_list'] == [1, 2, 3]
        assert trade_dict['sell_records_list'] == [4, 5]
        assert 'metrics' in trade_dict


class TestTradeReview:
    """交易复盘记录模型测试"""
    
    def test_create_valid_trade_review(self, db_session):
        """测试创建有效的复盘记录"""
        # 先创建历史交易记录
        historical_trade = HistoricalTrade(
            stock_code='000001',
            stock_name='平安银行',
            buy_date=datetime(2024, 1, 15),
            sell_date=datetime(2024, 2, 15),
            holding_days=31,
            total_investment=Decimal('10000.00'),
            total_return=Decimal('1500.00'),
            return_rate=Decimal('0.1500'),
            completion_date=datetime(2024, 2, 15)
        )
        historical_trade.save()
        
        review_data = {
            'historical_trade_id': historical_trade.id,
            'review_title': '平安银行交易复盘',
            'review_content': '这是一次成功的交易，把握了技术突破的机会。',
            'review_type': 'success',
            'strategy_score': 4,
            'timing_score': 5,
            'risk_control_score': 3,
            'overall_score': 4,
            'key_learnings': '技术分析的重要性',
            'improvement_areas': '风险控制需要加强'
        }
        
        review = TradeReview(**review_data)
        review.save()
        
        assert review.id is not None
        assert review.historical_trade_id == historical_trade.id
        assert review.review_title == '平安银行交易复盘'
        assert review.review_type == 'success'
        assert review.strategy_score == 4
        assert review.timing_score == 5
        assert review.risk_control_score == 3
        assert review.overall_score == 4
    
    def test_invalid_historical_trade_id(self, db_session):
        """测试无效历史交易ID"""
        with pytest.raises(ValidationError) as exc_info:
            TradeReview(
                historical_trade_id=None,
                review_title='测试复盘',
                review_content='测试内容'
            )
        assert '历史交易ID不能为空' in str(exc_info.value)
    
    def test_invalid_review_type(self, db_session):
        """测试无效复盘类型"""
        with pytest.raises(ValidationError) as exc_info:
            TradeReview(
                historical_trade_id=1,
                review_type='invalid_type'
            )
        assert '复盘类型必须是' in str(exc_info.value)
    
    def test_invalid_score_values(self, db_session):
        """测试无效评分值"""
        # 测试评分超出范围
        with pytest.raises(ValidationError) as exc_info:
            TradeReview(
                historical_trade_id=1,
                strategy_score=6  # 超出1-5范围
            )
        assert 'strategy_score必须是1-5之间的整数' in str(exc_info.value)
        
        # 测试评分为0
        with pytest.raises(ValidationError) as exc_info:
            TradeReview(
                historical_trade_id=1,
                timing_score=0  # 小于1
            )
        assert 'timing_score必须是1-5之间的整数' in str(exc_info.value)
        
        # 测试评分为非整数
        with pytest.raises(ValidationError) as exc_info:
            TradeReview(
                historical_trade_id=1,
                risk_control_score=3.5  # 非整数
            )
        assert 'risk_control_score必须是1-5之间的整数' in str(exc_info.value)
    
    def test_average_score_calculation(self, db_session):
        """测试平均评分计算"""
        review = TradeReview(
            historical_trade_id=1,
            strategy_score=4,
            timing_score=5,
            risk_control_score=3,
            overall_score=4
        )
        
        # 平均分应该是 (4+5+3+4)/4 = 4.0
        assert review.average_score == 4.0
        
        # 测试部分评分为空的情况
        review_partial = TradeReview(
            historical_trade_id=1,
            strategy_score=4,
            timing_score=None,
            risk_control_score=3,
            overall_score=None
        )
        
        # 平均分应该是 (4+3)/2 = 3.5
        assert review_partial.average_score == 3.5
        
        # 测试所有评分为空的情况
        review_empty = TradeReview(
            historical_trade_id=1
        )
        
        assert review_empty.average_score is None
    
    def test_update_scores(self, db_session):
        """测试更新评分"""
        review = TradeReview(
            historical_trade_id=1,
            strategy_score=3,
            timing_score=3,
            risk_control_score=3,
            overall_score=3
        )
        review.save()
        
        # 更新部分评分
        review.update_scores(strategy_score=5, overall_score=4)
        
        assert review.strategy_score == 5
        assert review.timing_score == 3  # 未更新的保持原值
        assert review.risk_control_score == 3
        assert review.overall_score == 4
        
        # 测试更新无效评分
        with pytest.raises(ValidationError):
            review.update_scores(strategy_score=6)
    
    def test_get_by_historical_trade(self, db_session):
        """测试根据历史交易ID获取复盘记录"""
        review1 = TradeReview(historical_trade_id=1, review_type='success')
        review1.save()
        
        review2 = TradeReview(historical_trade_id=2, review_type='failure')
        review2.save()
        
        result = TradeReview.get_by_historical_trade(1)
        assert result is not None
        assert result.historical_trade_id == 1
        assert result.review_type == 'success'
    
    def test_get_by_review_type(self, db_session):
        """测试根据复盘类型获取记录"""
        review1 = TradeReview(historical_trade_id=1, review_type='success')
        review1.save()
        
        review2 = TradeReview(historical_trade_id=2, review_type='success')
        review2.save()
        
        review3 = TradeReview(historical_trade_id=3, review_type='failure')
        review3.save()
        
        success_reviews = TradeReview.get_by_review_type('success')
        assert len(success_reviews) == 2
        
        failure_reviews = TradeReview.get_by_review_type('failure')
        assert len(failure_reviews) == 1
    
    def test_get_high_score_reviews(self, db_session):
        """测试获取高评分复盘记录"""
        review1 = TradeReview(historical_trade_id=1, overall_score=5)
        review1.save()
        
        review2 = TradeReview(historical_trade_id=2, overall_score=4)
        review2.save()
        
        review3 = TradeReview(historical_trade_id=3, overall_score=3)
        review3.save()
        
        high_score_reviews = TradeReview.get_high_score_reviews(min_score=4)
        assert len(high_score_reviews) == 2
        
        very_high_score_reviews = TradeReview.get_high_score_reviews(min_score=5)
        assert len(very_high_score_reviews) == 1
    
    def test_to_dict(self, db_session):
        """测试转换为字典"""
        review = TradeReview(
            historical_trade_id=1,
            review_title='测试复盘',
            strategy_score=4,
            timing_score=5,
            risk_control_score=3,
            overall_score=4
        )
        review.save()
        
        review_dict = review.to_dict()
        
        assert review_dict['historical_trade_id'] == 1
        assert review_dict['review_title'] == '测试复盘'
        assert review_dict['average_score'] == 4.0
        assert 'score_summary' in review_dict
        assert review_dict['score_summary']['strategy_score'] == 4
        assert review_dict['score_summary']['average_score'] == 4.0


class TestReviewImage:
    """复盘图片模型测试"""
    
    def test_create_valid_review_image(self, db_session):
        """测试创建有效的复盘图片记录"""
        image_data = {
            'trade_review_id': 1,
            'filename': 'chart_analysis_20240215.jpg',
            'original_filename': '技术分析图表.jpg',
            'file_path': '/uploads/reviews/chart_analysis_20240215.jpg',
            'file_size': 1024000,
            'mime_type': 'image/jpeg',
            'description': '技术分析图表',
            'display_order': 1
        }
        
        image = ReviewImage(**image_data)
        image.save()
        
        assert image.id is not None
        assert image.trade_review_id == 1
        assert image.filename == 'chart_analysis_20240215.jpg'
        assert image.original_filename == '技术分析图表.jpg'
        assert image.file_size == 1024000
        assert image.mime_type == 'image/jpeg'
        assert image.display_order == 1
    
    def test_invalid_trade_review_id(self, db_session):
        """测试无效复盘记录ID"""
        with pytest.raises(ValidationError) as exc_info:
            ReviewImage(
                trade_review_id=None,
                filename='test.jpg',
                original_filename='test.jpg',
                file_path='/uploads/test.jpg'
            )
        assert '复盘记录ID不能为空' in str(exc_info.value)
    
    def test_invalid_filename(self, db_session):
        """测试无效文件名"""
        with pytest.raises(ValidationError) as exc_info:
            ReviewImage(
                trade_review_id=1,
                filename='',  # 空文件名
                original_filename='test.jpg',
                file_path='/uploads/test.jpg'
            )
        assert '文件名不能为空' in str(exc_info.value)
    
    def test_invalid_file_size(self, db_session):
        """测试无效文件大小"""
        with pytest.raises(ValidationError) as exc_info:
            ReviewImage(
                trade_review_id=1,
                filename='test.jpg',
                original_filename='test.jpg',
                file_path='/uploads/test.jpg',
                file_size=-1000  # 负数文件大小
            )
        assert '文件大小必须大于0' in str(exc_info.value)
    
    def test_invalid_display_order(self, db_session):
        """测试无效显示顺序"""
        with pytest.raises(ValidationError) as exc_info:
            ReviewImage(
                trade_review_id=1,
                filename='test.jpg',
                original_filename='test.jpg',
                file_path='/uploads/test.jpg',
                display_order=-1  # 负数显示顺序
            )
        assert '显示顺序不能为负数' in str(exc_info.value)
    
    def test_invalid_mime_type(self, db_session):
        """测试无效MIME类型"""
        with pytest.raises(ValidationError) as exc_info:
            ReviewImage(
                trade_review_id=1,
                filename='test.txt',
                original_filename='test.txt',
                file_path='/uploads/test.txt',
                mime_type='text/plain'  # 非图片MIME类型
            )
        assert '不支持的图片格式' in str(exc_info.value)
    
    def test_get_file_extension(self, db_session):
        """测试获取文件扩展名"""
        image = ReviewImage(
            trade_review_id=1,
            filename='test.jpg',
            original_filename='测试图片.JPG',
            file_path='/uploads/test.jpg'
        )
        
        assert image.get_file_extension() == 'jpg'
        
        # 测试无扩展名文件
        image_no_ext = ReviewImage(
            trade_review_id=1,
            filename='test',
            original_filename='test',
            file_path='/uploads/test'
        )
        
        assert image_no_ext.get_file_extension() == ''
    
    def test_is_valid_image_format(self, db_session):
        """测试检查有效图片格式"""
        valid_image = ReviewImage(
            trade_review_id=1,
            filename='test.jpg',
            original_filename='test.jpg',
            file_path='/uploads/test.jpg'
        )
        
        assert valid_image.is_valid_image_format() == True
        
        invalid_image = ReviewImage(
            trade_review_id=1,
            filename='test.txt',
            original_filename='test.txt',
            file_path='/uploads/test.txt'
        )
        
        assert invalid_image.is_valid_image_format() == False
    
    def test_update_display_order(self, db_session):
        """测试更新显示顺序"""
        image = ReviewImage(
            trade_review_id=1,
            filename='test.jpg',
            original_filename='test.jpg',
            file_path='/uploads/test.jpg',
            display_order=0
        )
        image.save()
        
        # 更新显示顺序
        image.update_display_order(5)
        assert image.display_order == 5
        
        # 测试无效显示顺序
        with pytest.raises(ValidationError):
            image.update_display_order(-1)
    
    def test_get_by_review(self, db_session):
        """测试根据复盘记录ID获取图片列表"""
        image1 = ReviewImage(
            trade_review_id=1,
            filename='test1.jpg',
            original_filename='test1.jpg',
            file_path='/uploads/test1.jpg',
            display_order=2
        )
        image1.save()
        
        image2 = ReviewImage(
            trade_review_id=1,
            filename='test2.jpg',
            original_filename='test2.jpg',
            file_path='/uploads/test2.jpg',
            display_order=1
        )
        image2.save()
        
        image3 = ReviewImage(
            trade_review_id=2,
            filename='test3.jpg',
            original_filename='test3.jpg',
            file_path='/uploads/test3.jpg',
            display_order=1
        )
        image3.save()
        
        images = ReviewImage.get_by_review(1)
        assert len(images) == 2
        # 应该按display_order排序
        assert images[0].display_order == 1
        assert images[1].display_order == 2
    
    def test_to_dict(self, db_session):
        """测试转换为字典"""
        image = ReviewImage(
            trade_review_id=1,
            filename='test.jpg',
            original_filename='测试图片.jpg',
            file_path='/uploads/test.jpg',
            file_size=1024000,
            mime_type='image/jpeg',
            description='测试图片',
            display_order=1
        )
        image.save()
        
        image_dict = image.to_dict()
        
        assert image_dict['trade_review_id'] == 1
        assert image_dict['filename'] == 'test.jpg'
        assert image_dict['file_extension'] == 'jpg'
        assert image_dict['is_valid_format'] == True
        assert image_dict['file_size_formatted'] == '1000.0 KB'