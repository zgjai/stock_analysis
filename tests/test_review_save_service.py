"""
复盘保存服务功能测试
测试扩展的复盘保存服务功能，包括数据处理、验证和完整性检查
"""
import pytest
from datetime import date, datetime
from services.review_service import ReviewService
from models.review_record import ReviewRecord
from models.trade_record import TradeRecord
from error_handlers import ValidationError, DatabaseError


class TestReviewSaveService:
    """复盘保存服务测试"""
    
    def test_process_floating_profit_data_auto_calculate(self, app, db_session):
        """测试自动计算浮盈数据"""
        data = {
            'stock_code': '000001',
            'current_price': 12.50,
            'buy_price': 10.00
        }
        
        ReviewService._process_floating_profit_data(data)
        
        # 验证自动计算的浮盈比例
        expected_ratio = (12.50 - 10.00) / 10.00
        assert abs(data['floating_profit_ratio'] - expected_ratio) < 0.001
    
    def test_process_floating_profit_data_from_trade_records(self, app, db_session):
        """测试从交易记录获取买入价格"""
        # 创建交易记录
        trade_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 11.50,
            'quantity': 1000,
            'trade_date': datetime(2024, 1, 10),
            'reason': '买入原因'
        }
        TradeRecord(**trade_data).save()
        
        data = {
            'stock_code': '000001',
            'current_price': 13.00
        }
        
        ReviewService._process_floating_profit_data(data)
        
        # 验证从交易记录获取的买入价格
        assert data['buy_price'] == 11.50
        
        # 验证自动计算的浮盈比例
        expected_ratio = (13.00 - 11.50) / 11.50
        assert abs(data['floating_profit_ratio'] - expected_ratio) < 0.001
    
    def test_process_floating_profit_data_with_existing_review(self, app, db_session):
        """测试处理现有复盘记录的浮盈数据"""
        # 创建现有复盘记录
        existing_review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'buy_price': 10.50
        }
        existing_review = ReviewService.create_review(existing_review_data)
        
        # 更新数据，只提供当前价格
        data = {
            'current_price': 12.00
        }
        
        ReviewService._process_floating_profit_data(data, existing_review)
        
        # 验证使用现有记录的买入价格
        assert data['buy_price'] == 10.50
        
        # 验证自动计算的浮盈比例
        expected_ratio = (12.00 - 10.50) / 10.50
        assert abs(data['floating_profit_ratio'] - expected_ratio) < 0.001
    
    def test_process_floating_profit_data_consistency_check(self, app, db_session):
        """测试浮盈数据一致性检查"""
        data = {
            'stock_code': '000001',
            'current_price': 12.00,
            'buy_price': 10.00,
            'floating_profit_ratio': 0.15  # 错误的比例，应该是0.2
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ReviewService._process_floating_profit_data(data)
        
        assert "浮盈比例与当前价格和买入价格不一致" in str(exc_info.value)
    
    def test_process_floating_profit_data_no_buy_price_available(self, app, db_session):
        """测试没有可用买入价格时的处理"""
        data = {
            'stock_code': '999999',  # 不存在的股票
            'current_price': 12.00
        }
        
        # 应该不会抛出异常，但也不会计算浮盈比例
        ReviewService._process_floating_profit_data(data)
        
        assert 'floating_profit_ratio' not in data
        assert 'buy_price' not in data
    
    def test_validate_review_data_integrity_success(self, app, db_session):
        """测试数据完整性验证成功"""
        data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'bbi_score': 0,
            'volume_score': 1,
            'trend_score': 1,
            'j_score': 0,
            'current_price': 12.50,
            'buy_price': 10.00,
            'analysis': '技术面良好',
            'decision': 'hold'
        }
        
        result = ReviewService.validate_review_data_integrity(data)
        
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert len(result['auto_corrections']) == 1  # 自动计算浮盈比例
        assert result['auto_corrections'][0]['field'] == 'floating_profit_ratio'
    
    def test_validate_review_data_integrity_missing_required_fields(self, app, db_session):
        """测试数据完整性验证缺少必填字段"""
        data = {
            'price_up_score': 1,
            'analysis': '分析内容'
        }
        
        result = ReviewService.validate_review_data_integrity(data)
        
        assert result['is_valid'] is False
        assert len(result['errors']) >= 2  # stock_code和review_date都缺失
        
        error_messages = ' '.join(result['errors'])
        assert 'stock_code不能为空' in error_messages
        assert 'review_date不能为空' in error_messages
    
    def test_validate_review_data_integrity_invalid_scores(self, app, db_session):
        """测试数据完整性验证无效评分"""
        data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 2,  # 无效评分
            'bbi_score': -1,      # 无效评分
            'volume_score': 'invalid'  # 无效类型
        }
        
        result = ReviewService.validate_review_data_integrity(data)
        
        assert result['is_valid'] is False
        assert len(result['errors']) >= 3
        
        error_messages = ' '.join(result['errors'])
        assert 'price_up_score必须是0或1' in error_messages
        assert 'bbi_score必须是0或1' in error_messages
        assert 'volume_score必须是整数' in error_messages
    
    def test_validate_review_data_integrity_invalid_prices(self, app, db_session):
        """测试数据完整性验证无效价格"""
        data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'current_price': -5.00,  # 负价格
            'buy_price': 'invalid'   # 无效格式
        }
        
        result = ReviewService.validate_review_data_integrity(data)
        
        assert result['is_valid'] is False
        assert len(result['errors']) >= 2
        
        error_messages = ' '.join(result['errors'])
        assert '当前价格不能为负数' in error_messages
        assert '买入价格必须是有效数字' in error_messages
    
    def test_validate_review_data_integrity_with_warnings(self, app, db_session):
        """测试数据完整性验证带警告"""
        data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'current_price': 12.00,
            'buy_price': 10.00,
            'floating_profit_ratio': 0.15  # 错误的比例，应该是0.2
        }
        
        result = ReviewService.validate_review_data_integrity(data)
        
        assert result['is_valid'] is True  # 数据有效，但有警告
        assert len(result['warnings']) == 1
        assert len(result['auto_corrections']) == 1
        
        assert '浮盈比例将被自动修正' in result['warnings'][0]
        assert result['auto_corrections'][0]['field'] == 'floating_profit_ratio'
        assert result['auto_corrections'][0]['old_value'] == 0.15
        assert abs(result['auto_corrections'][0]['new_value'] - 0.2) < 0.001
    
    def test_create_review_with_data_integrity_processing(self, app, db_session):
        """测试创建复盘记录时的数据完整性处理"""
        # 创建交易记录
        trade_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 10.50,
            'quantity': 1000,
            'trade_date': datetime(2024, 1, 10),
            'reason': '买入原因'
        }
        TradeRecord(**trade_data).save()
        
        # 创建复盘记录，只提供当前价格
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'bbi_score': 1,
            'current_price': 12.60,
            'analysis': '表现良好'
        }
        
        review = ReviewService.create_review(review_data)
        
        # 验证自动填充的数据
        assert float(review.buy_price) == 10.50  # 从交易记录获取
        assert float(review.current_price) == 12.60
        
        # 验证自动计算的浮盈比例
        expected_ratio = (12.60 - 10.50) / 10.50
        assert abs(float(review.floating_profit_ratio) - expected_ratio) < 0.001
        
        # 验证其他字段
        assert review.total_score == 2  # 1+1+0+0+0
        assert review.analysis == '表现良好'
    
    def test_update_review_with_data_integrity_processing(self, app, db_session):
        """测试更新复盘记录时的数据完整性处理"""
        # 创建初始复盘记录
        initial_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'buy_price': 11.00,
            'current_price': 12.00
        }
        review = ReviewService.create_review(initial_data)
        
        # 更新当前价格
        update_data = {
            'current_price': 13.50,
            'volume_score': 1  # 同时更新评分
        }
        
        updated_review = ReviewService.update_review(review.id, update_data)
        
        # 验证价格更新
        assert float(updated_review.current_price) == 13.50
        assert float(updated_review.buy_price) == 11.00  # 保持不变
        
        # 验证浮盈比例重新计算
        expected_ratio = (13.50 - 11.00) / 11.00
        assert abs(float(updated_review.floating_profit_ratio) - expected_ratio) < 0.001
        
        # 验证评分更新
        assert updated_review.volume_score == 1
        assert updated_review.total_score == 2  # 1+0+1+0+0
    
    def test_create_review_data_validation_error_handling(self, app, db_session):
        """测试创建复盘记录时数据验证错误处理"""
        invalid_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'current_price': 12.00,
            'buy_price': 10.00,
            'floating_profit_ratio': 0.5  # 错误的比例
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ReviewService.create_review(invalid_data)
        
        assert "浮盈比例与当前价格和买入价格不一致" in str(exc_info.value)
        
        # 验证没有创建记录
        assert ReviewRecord.query.filter_by(stock_code='000001').count() == 0
    
    def test_update_review_data_validation_error_handling(self, app, db_session):
        """测试更新复盘记录时数据验证错误处理"""
        # 创建初始记录
        initial_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'buy_price': 10.00,
            'current_price': 11.00
        }
        review = ReviewService.create_review(initial_data)
        original_ratio = float(review.floating_profit_ratio)
        
        # 尝试更新为无效数据
        invalid_update = {
            'current_price': 12.00,
            'floating_profit_ratio': 0.5  # 错误的比例
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ReviewService.update_review(review.id, invalid_update)
        
        assert "浮盈比例与当前价格和买入价格不一致" in str(exc_info.value)
        
        # 验证原记录没有被修改
        unchanged_review = ReviewService.get_by_id(review.id)
        assert float(unchanged_review.current_price) == 11.00
        assert abs(float(unchanged_review.floating_profit_ratio) - original_ratio) < 0.001
    
    def test_get_buy_price_for_stock_multiple_trades(self, app, db_session):
        """测试从多个交易记录计算加权平均买入价格"""
        # 创建多个买入记录
        trades = [
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 10.00,
                'quantity': 1000,
                'trade_date': datetime(2024, 1, 10),
                'reason': '首次买入'
            },
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.00,
                'quantity': 500,
                'trade_date': datetime(2024, 1, 12),
                'reason': '加仓'
            },
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 11.00,
                'quantity': 1500,
                'trade_date': datetime(2024, 1, 14),
                'reason': '再次加仓'
            }
        ]
        
        for trade_data in trades:
            TradeRecord(**trade_data).save()
        
        buy_price = ReviewService.get_buy_price_for_stock('000001')
        
        # 计算加权平均价格
        # (10.00 * 1000 + 12.00 * 500 + 11.00 * 1500) / (1000 + 500 + 1500)
        # = (10000 + 6000 + 16500) / 3000 = 32500 / 3000 = 10.83
        expected_avg = (10.00 * 1000 + 12.00 * 500 + 11.00 * 1500) / (1000 + 500 + 1500)
        
        assert abs(buy_price - expected_avg) < 0.01
    
    def test_get_buy_price_for_stock_no_trades(self, app, db_session):
        """测试获取不存在交易记录的股票买入价格"""
        buy_price = ReviewService.get_buy_price_for_stock('999999')
        assert buy_price is None
    
    def test_get_buy_price_for_stock_only_sell_trades(self, app, db_session):
        """测试只有卖出记录的股票买入价格"""
        # 创建卖出记录
        sell_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'sell',
            'price': 12.00,
            'quantity': 500,
            'trade_date': datetime(2024, 1, 15),
            'reason': '止盈'
        }
        TradeRecord(**sell_data).save()
        
        buy_price = ReviewService.get_buy_price_for_stock('000001')
        assert buy_price is None