"""
复盘保存API功能测试
测试扩展的复盘保存API功能，包括新字段支持、数据验证和完整性检查
"""
import pytest
import json
from datetime import date, datetime
from models.review_record import ReviewRecord
from models.trade_record import TradeRecord
from services.review_service import ReviewService


class TestReviewSaveAPI:
    """复盘保存API测试"""
    
    def test_create_review_with_floating_profit_fields(self, client, db_session):
        """测试创建包含浮盈字段的复盘记录"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 0,
            'trend_score': 1,
            'j_score': 0,
            'analysis': '今日表现良好',
            'decision': 'hold',
            'reason': '继续观察',
            'holding_days': 5,
            'current_price': 12.50,
            'buy_price': 11.00,
            'floating_profit_ratio': 0.1364  # (12.50 - 11.00) / 11.00
        }
        
        response = client.post('/api/reviews', 
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['stock_code'] == '000001'
        assert data['data']['current_price'] == 12.50
        assert data['data']['buy_price'] == 11.00
        assert abs(data['data']['floating_profit_ratio'] - 0.1364) < 0.001
        assert data['message'] == '复盘记录创建成功'
    
    def test_create_review_auto_calculate_floating_profit(self, client, db_session):
        """测试创建复盘记录时自动计算浮盈比例"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'current_price': 12.50,
            'buy_price': 10.00
            # 不提供 floating_profit_ratio，应该自动计算
        }
        
        response = client.post('/api/reviews', 
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['current_price'] == 12.50
        assert data['data']['buy_price'] == 10.00
        # 应该自动计算 (12.50 - 10.00) / 10.00 = 0.25
        assert abs(data['data']['floating_profit_ratio'] - 0.25) < 0.001
    
    def test_create_review_with_trade_record_buy_price(self, client, db_session):
        """测试创建复盘记录时从交易记录获取买入价格"""
        # 先创建交易记录
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
        
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'current_price': 12.50
            # 不提供 buy_price，应该从交易记录获取
        }
        
        response = client.post('/api/reviews', 
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['current_price'] == 12.50
        assert data['data']['buy_price'] == 11.50  # 从交易记录获取
        # 应该自动计算浮盈比例
        expected_ratio = (12.50 - 11.50) / 11.50
        assert abs(data['data']['floating_profit_ratio'] - expected_ratio) < 0.001
    
    def test_create_review_invalid_current_price(self, client, db_session):
        """测试创建复盘记录时当前价格无效"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'current_price': -5.00  # 负数价格
        }
        
        response = client.post('/api/reviews',
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '当前价格不能为负数' in data['error']['message']
    
    def test_create_review_invalid_buy_price(self, client, db_session):
        """测试创建复盘记录时买入价格无效"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'buy_price': 'invalid_price'  # 无效价格格式
        }
        
        response = client.post('/api/reviews',
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '买入价格必须是有效数字' in data['error']['message']
    
    def test_create_review_invalid_floating_profit_ratio(self, client, db_session):
        """测试创建复盘记录时浮盈比例无效"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'floating_profit_ratio': -1.5  # 亏损超过100%
        }
        
        response = client.post('/api/reviews',
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '浮盈比例不能小于-100%' in data['error']['message']
    
    def test_update_review_with_floating_profit_fields(self, client, db_session):
        """测试更新复盘记录的浮盈字段"""
        # 创建初始记录
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'current_price': 12.00,
            'buy_price': 10.00
        }
        review = ReviewService.create_review(review_data)
        
        # 更新记录
        update_data = {
            'current_price': 13.50,
            'analysis': '价格上涨，继续持有'
        }
        
        response = client.put(f'/api/reviews/{review.id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['current_price'] == 13.50
        assert data['data']['buy_price'] == 10.00  # 保持原值
        # 应该重新计算浮盈比例
        expected_ratio = (13.50 - 10.00) / 10.00
        assert abs(data['data']['floating_profit_ratio'] - expected_ratio) < 0.001
        assert data['data']['analysis'] == '价格上涨，继续持有'
    
    def test_update_review_inconsistent_floating_profit_data(self, client, db_session):
        """测试更新复盘记录时浮盈数据不一致"""
        # 创建初始记录
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1
        }
        review = ReviewService.create_review(review_data)
        
        # 更新记录，提供不一致的数据
        update_data = {
            'current_price': 12.00,
            'buy_price': 10.00,
            'floating_profit_ratio': 0.5  # 错误的比例，应该是0.2
        }
        
        response = client.put(f'/api/reviews/{review.id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '浮盈比例与当前价格和买入价格不一致' in data['error']['message']
    
    def test_validate_review_data_success(self, client, db_session):
        """测试验证复盘数据成功"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'bbi_score': 1,
            'current_price': 12.50,
            'buy_price': 10.00
        }
        
        response = client.post('/api/reviews/validate',
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['is_valid'] is True
        assert len(data['data']['errors']) == 0
        # 应该有自动修正的浮盈比例
        assert len(data['data']['auto_corrections']) == 1
        assert data['data']['auto_corrections'][0]['field'] == 'floating_profit_ratio'
    
    def test_validate_review_data_with_errors(self, client, db_session):
        """测试验证复盘数据有错误"""
        review_data = {
            'stock_code': '',  # 空股票代码
            'review_date': '2024-01-15',
            'price_up_score': 2,  # 无效评分
            'current_price': -5.00  # 负价格
        }
        
        response = client.post('/api/reviews/validate',
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['is_valid'] is False
        assert len(data['data']['errors']) > 0
        # 应该包含各种错误信息
        error_messages = ' '.join(data['data']['errors'])
        assert 'stock_code不能为空' in error_messages
        assert 'price_up_score必须是0或1' in error_messages
        assert '当前价格不能为负数' in error_messages
    
    def test_create_review_malformed_json(self, client, db_session):
        """测试创建复盘记录时JSON格式错误"""
        response = client.post('/api/reviews',
                             data='{"invalid": json}',  # 无效JSON
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '请求数据格式错误' in data['error']['message']
    
    def test_update_review_malformed_json(self, client, db_session):
        """测试更新复盘记录时JSON格式错误"""
        # 创建初始记录
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1
        }
        review = ReviewService.create_review(review_data)
        
        response = client.put(f'/api/reviews/{review.id}',
                            data='{"invalid": json}',  # 无效JSON
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '请求数据格式错误' in data['error']['message']
    
    def test_create_review_empty_request_body(self, client, db_session):
        """测试创建复盘记录时请求体为空"""
        response = client.post('/api/reviews',
                             data=json.dumps(None),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '请求数据不能为空' in data['error']['message']
    
    def test_update_review_empty_request_body(self, client, db_session):
        """测试更新复盘记录时请求体为空"""
        # 创建初始记录
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1
        }
        review = ReviewService.create_review(review_data)
        
        response = client.put(f'/api/reviews/{review.id}',
                            data=json.dumps(None),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '请求数据不能为空' in data['error']['message']
    
    def test_create_review_with_extreme_floating_profit_ratio(self, client, db_session):
        """测试创建复盘记录时浮盈比例极值"""
        # 测试极大的浮盈比例
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'floating_profit_ratio': 15.0  # 1500%盈利
        }
        
        response = client.post('/api/reviews',
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '浮盈比例不能大于1000%' in data['error']['message']
    
    def test_create_review_data_integrity_check(self, client, db_session):
        """测试创建复盘记录时的数据完整性检查"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 0,
            'trend_score': 1,
            'j_score': 1,
            'analysis': '技术面良好',
            'decision': 'hold',
            'reason': '符合持有条件',
            'holding_days': 10,
            'current_price': 12.50,
            'buy_price': 10.00
            # 不提供浮盈比例，应该自动计算并保存
        }
        
        response = client.post('/api/reviews', 
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证所有字段都正确保存
        saved_review = data['data']
        assert saved_review['stock_code'] == '000001'
        assert saved_review['total_score'] == 4  # 1+1+0+1+1
        assert saved_review['analysis'] == '技术面良好'
        assert saved_review['decision'] == 'hold'
        assert saved_review['reason'] == '符合持有条件'
        assert saved_review['holding_days'] == 10
        assert saved_review['current_price'] == 12.50
        assert saved_review['buy_price'] == 10.00
        
        # 验证自动计算的浮盈比例
        expected_ratio = (12.50 - 10.00) / 10.00
        assert abs(saved_review['floating_profit_ratio'] - expected_ratio) < 0.001
        
        # 验证浮盈显示格式
        assert 'floating_profit_display' in saved_review
        assert saved_review['floating_profit_display']['color'] == 'text-success'
        assert '+25.00%' in saved_review['floating_profit_display']['display']


class TestReviewSaveServiceIntegration:
    """复盘保存服务集成测试"""
    
    def test_save_review_with_multiple_trade_records(self, app, db_session):
        """测试保存复盘记录时处理多个交易记录"""
        # 创建多个买入记录
        trade_records = [
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
            }
        ]
        
        for trade_data in trade_records:
            TradeRecord(**trade_data).save()
        
        # 创建复盘记录，应该使用加权平均买入价格
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'current_price': 13.00
        }
        
        review = ReviewService.create_review(review_data)
        
        # 验证使用了加权平均价格
        # 加权平均 = (10.00 * 1000 + 12.00 * 500) / (1000 + 500) = 16000 / 1500 = 10.67
        expected_avg_price = (10.00 * 1000 + 12.00 * 500) / (1000 + 500)
        assert abs(float(review.buy_price) - expected_avg_price) < 0.01
        
        # 验证浮盈比例计算正确
        expected_ratio = (13.00 - expected_avg_price) / expected_avg_price
        assert abs(float(review.floating_profit_ratio) - expected_ratio) < 0.001
    
    def test_save_review_data_consistency_across_updates(self, app, db_session):
        """测试复盘记录更新时数据一致性"""
        # 创建初始记录
        initial_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'current_price': 12.00,
            'buy_price': 10.00,
            'analysis': '初始分析'
        }
        
        review = ReviewService.create_review(initial_data)
        initial_ratio = float(review.floating_profit_ratio)
        
        # 第一次更新：只更新分析内容
        update_data_1 = {
            'analysis': '更新后的分析'
        }
        updated_review_1 = ReviewService.update_review(review.id, update_data_1)
        
        # 验证浮盈数据保持不变
        assert float(updated_review_1.current_price) == 12.00
        assert float(updated_review_1.buy_price) == 10.00
        assert abs(float(updated_review_1.floating_profit_ratio) - initial_ratio) < 0.001
        assert updated_review_1.analysis == '更新后的分析'
        
        # 第二次更新：更新当前价格
        update_data_2 = {
            'current_price': 15.00
        }
        updated_review_2 = ReviewService.update_review(review.id, update_data_2)
        
        # 验证浮盈比例重新计算
        expected_new_ratio = (15.00 - 10.00) / 10.00
        assert float(updated_review_2.current_price) == 15.00
        assert float(updated_review_2.buy_price) == 10.00
        assert abs(float(updated_review_2.floating_profit_ratio) - expected_new_ratio) < 0.001
    
    def test_save_review_error_handling_and_rollback(self, app, db_session):
        """测试复盘记录保存错误处理和回滚"""
        # 创建一个有效的复盘记录
        valid_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'current_price': 12.00,
            'buy_price': 10.00
        }
        
        review = ReviewService.create_review(valid_data)
        original_count = ReviewRecord.query.count()
        
        # 尝试创建重复的记录（应该失败）
        with pytest.raises(Exception):  # 应该抛出ValidationError
            ReviewService.create_review(valid_data)
        
        # 验证数据库状态没有改变
        assert ReviewRecord.query.count() == original_count
        
        # 验证原记录仍然存在且数据正确
        existing_review = ReviewService.get_by_id(review.id)
        assert existing_review is not None
        assert float(existing_review.current_price) == 12.00
        assert float(existing_review.buy_price) == 10.00