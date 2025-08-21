"""
复盘记录和持仓管理API测试
"""
import pytest
import json
from datetime import date, datetime
from models.review_record import ReviewRecord
from models.trade_record import TradeRecord
from services.review_service import ReviewService


class TestReviewAPI:
    """复盘记录API测试"""
    
    def test_create_review_success(self, client, db_session):
        """测试成功创建复盘记录"""
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
            'holding_days': 5
        }
        
        response = client.post('/api/reviews', 
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['stock_code'] == '000001'
        assert data['data']['total_score'] == 3
        assert data['message'] == '复盘记录创建成功'
    
    def test_create_review_missing_fields(self, client, db_session):
        """测试创建复盘记录缺少必填字段"""
        review_data = {
            'price_up_score': 1
        }
        
        response = client.post('/api/reviews',
                             data=json.dumps(review_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'stock_code不能为空' in data['error']['message']
    
    def test_create_review_empty_request(self, client, db_session):
        """测试创建复盘记录空请求"""
        response = client.post('/api/reviews',
                             data=json.dumps(None),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '请求数据不能为空' in data['error']['message']
    
    def test_get_reviews_empty(self, client, db_session):
        """测试获取空复盘记录列表"""
        response = client.get('/api/reviews')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['reviews'] == []
        assert data['data']['total'] == 0
    
    def test_get_reviews_with_data(self, client, db_session):
        """测试获取有数据的复盘记录列表"""
        # 创建测试数据
        reviews_data = [
            {
                'stock_code': '000001',
                'review_date': '2024-01-15',
                'price_up_score': 1,
                'bbi_score': 1,
                'decision': 'hold'
            },
            {
                'stock_code': '000002',
                'review_date': '2024-01-16',
                'price_up_score': 0,
                'bbi_score': 0,
                'decision': 'sell_all'
            }
        ]
        
        for data in reviews_data:
            ReviewService.create_review(data)
        
        response = client.get('/api/reviews')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']['reviews']) == 2
        assert data['data']['total'] == 2
    
    def test_get_reviews_with_filters(self, client, db_session):
        """测试带筛选条件获取复盘记录"""
        # 创建测试数据
        reviews_data = [
            {
                'stock_code': '000001',
                'review_date': '2024-01-15',
                'price_up_score': 1,
                'bbi_score': 1,
                'decision': 'hold'
            },
            {
                'stock_code': '000002',
                'review_date': '2024-01-16',
                'price_up_score': 0,
                'bbi_score': 0,
                'decision': 'sell_all'
            }
        ]
        
        for data in reviews_data:
            ReviewService.create_review(data)
        
        # 测试按股票代码筛选
        response = client.get('/api/reviews?stock_code=000001')
        data = json.loads(response.data)
        assert len(data['data']['reviews']) == 1
        assert data['data']['reviews'][0]['stock_code'] == '000001'
        
        # 测试按决策筛选
        response = client.get('/api/reviews?decision=hold')
        data = json.loads(response.data)
        assert len(data['data']['reviews']) == 1
        assert data['data']['reviews'][0]['decision'] == 'hold'
        
        # 测试按评分筛选
        response = client.get('/api/reviews?min_score=2')
        data = json.loads(response.data)
        assert len(data['data']['reviews']) == 1
        assert data['data']['reviews'][0]['total_score'] >= 2
    
    def test_get_reviews_with_pagination(self, client, db_session):
        """测试分页获取复盘记录"""
        # 创建5条测试数据
        for i in range(5):
            review_data = {
                'stock_code': f'00000{i+1}',
                'review_date': f'2024-01-{15+i:02d}',
                'price_up_score': 1
            }
            ReviewService.create_review(review_data)
        
        # 测试第一页
        response = client.get('/api/reviews?page=1&per_page=2')
        data = json.loads(response.data)
        assert len(data['data']['reviews']) == 2
        assert data['data']['pagination']['page'] == 1
        assert data['data']['pagination']['total'] == 5
        
        # 测试第二页
        response = client.get('/api/reviews?page=2&per_page=2')
        data = json.loads(response.data)
        assert len(data['data']['reviews']) == 2
        assert data['data']['pagination']['page'] == 2
    
    def test_get_review_by_id(self, client, db_session):
        """测试根据ID获取复盘记录"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'analysis': '测试分析'
        }
        review = ReviewService.create_review(review_data)
        
        response = client.get(f'/api/reviews/{review.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['id'] == review.id
        assert data['data']['analysis'] == '测试分析'
    
    def test_get_review_by_id_not_found(self, client, db_session):
        """测试获取不存在的复盘记录"""
        response = client.get('/api/reviews/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_review_success(self, client, db_session):
        """测试成功更新复盘记录"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'bbi_score': 0
        }
        review = ReviewService.create_review(review_data)
        
        update_data = {
            'bbi_score': 1,
            'analysis': '更新后的分析',
            'decision': 'sell_partial'
        }
        
        response = client.put(f'/api/reviews/{review.id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['bbi_score'] == 1
        assert data['data']['total_score'] == 2
        assert data['data']['analysis'] == '更新后的分析'
    
    def test_update_review_not_found(self, client, db_session):
        """测试更新不存在的复盘记录"""
        update_data = {'analysis': '测试'}
        
        response = client.put('/api/reviews/999',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_delete_review_success(self, client, db_session):
        """测试成功删除复盘记录"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1
        }
        review = ReviewService.create_review(review_data)
        
        response = client.delete(f'/api/reviews/{review.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == '复盘记录删除成功'
        
        # 验证记录已被删除
        response = client.get(f'/api/reviews/{review.id}')
        assert response.status_code == 404
    
    def test_get_reviews_by_stock(self, client, db_session):
        """测试获取某股票的所有复盘记录"""
        stock_code = '000001'
        
        # 创建测试数据
        for i in range(3):
            review_data = {
                'stock_code': stock_code,
                'review_date': f'2024-01-{15+i:02d}',
                'price_up_score': 1
            }
            ReviewService.create_review(review_data)
        
        # 创建其他股票的记录
        ReviewService.create_review({
            'stock_code': '000002',
            'review_date': '2024-01-20',
            'price_up_score': 1
        })
        
        response = client.get(f'/api/reviews/stock/{stock_code}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 3
        for review in data['data']:
            assert review['stock_code'] == stock_code
    
    def test_get_latest_review_by_stock(self, client, db_session):
        """测试获取某股票最新的复盘记录"""
        stock_code = '000001'
        
        # 创建多条记录
        dates = ['2024-01-15', '2024-01-17', '2024-01-16']
        for i, date_str in enumerate(dates):
            review_data = {
                'stock_code': stock_code,
                'review_date': date_str,
                'price_up_score': 1 if i % 2 == 0 else 0,  # 确保评分值为0或1
                'analysis': f'分析{i}'
            }
            ReviewService.create_review(review_data)
        
        response = client.get(f'/api/reviews/stock/{stock_code}/latest')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['review_date'] == '2024-01-17'  # 最新日期
        assert data['data']['analysis'] == '分析1'
    
    def test_get_latest_review_by_stock_not_found(self, client, db_session):
        """测试获取不存在股票的最新复盘记录"""
        response = client.get('/api/reviews/stock/999999/latest')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        # 检查是否有data字段，如果没有则检查message
        if 'data' in data:
            assert data['data'] is None
        assert '暂无复盘记录' in data['message']
    
    def test_calculate_review_score(self, client, db_session):
        """测试计算复盘评分"""
        score_data = {
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 0,
            'trend_score': 1,
            'j_score': 0
        }
        
        response = client.post('/api/reviews/calculate-score',
                             data=json.dumps(score_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['total_score'] == 3
        assert data['data']['score_breakdown']['收盘价上升'] == 1
        assert data['data']['score_breakdown']['不破BBI线'] == 1
    
    def test_calculate_review_score_invalid(self, client, db_session):
        """测试计算无效的复盘评分"""
        score_data = {
            'price_up_score': 2,  # 无效值
            'bbi_score': 1
        }
        
        response = client.post('/api/reviews/calculate-score',
                             data=json.dumps(score_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'price_up_score必须是0或1' in data['error']['message']


class TestHoldingAPI:
    """持仓管理API测试"""
    
    def test_get_current_holdings_empty(self, client, db_session):
        """测试获取空持仓列表"""
        response = client.get('/api/holdings')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == []
    
    def test_get_current_holdings_with_data(self, client, db_session):
        """测试获取有数据的持仓列表"""
        # 创建买入记录
        buy_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime(2024, 1, 10),
            'reason': '买入原因'
        }
        TradeRecord(**buy_data).save()
        
        # 创建复盘记录
        review_data = {
            'stock_code': '000001',
            'review_date': date.today(),
            'holding_days': 8,
            'price_up_score': 1
        }
        ReviewService.create_review(review_data)
        
        response = client.get('/api/holdings')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 1
        
        holding = data['data'][0]
        assert holding['stock_code'] == '000001'
        assert holding['stock_name'] == '平安银行'
        assert holding['current_quantity'] == 1000
        assert holding['holding_days'] == 8
        assert holding['latest_review'] is not None
    
    def test_get_holding_by_stock(self, client, db_session):
        """测试获取特定股票的持仓信息"""
        # 创建买入记录
        buy_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime(2024, 1, 10),
            'reason': '买入原因'
        }
        TradeRecord(**buy_data).save()
        
        response = client.get('/api/holdings/000001')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['stock_code'] == '000001'
        assert data['data']['current_quantity'] == 1000
    
    def test_get_holding_by_stock_not_found(self, client, db_session):
        """测试获取不存在的股票持仓信息"""
        response = client.get('/api/holdings/999999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert '当前无持仓' in data['error']['message']
    
    def test_update_holding_days_success(self, client, db_session):
        """测试成功更新持仓天数"""
        stock_code = '000001'
        holding_days = 10
        
        update_data = {'holding_days': holding_days}
        
        response = client.put(f'/api/holdings/{stock_code}/days',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['holding_days'] == holding_days
        assert f'更新股票{stock_code}持仓天数成功' in data['message']
    
    def test_update_holding_days_missing_data(self, client, db_session):
        """测试更新持仓天数缺少数据"""
        response = client.put('/api/holdings/000001/days',
                            data=json.dumps({}),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '持仓天数不能为空' in data['error']['message']
    
    def test_update_holding_days_invalid_data(self, client, db_session):
        """测试更新无效的持仓天数"""
        update_data = {'holding_days': 'invalid'}
        
        response = client.put('/api/holdings/000001/days',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '持仓天数必须是正整数' in data['error']['message']
    
    def test_update_holding_days_negative_value(self, client, db_session):
        """测试更新负数持仓天数"""
        update_data = {'holding_days': -5}
        
        response = client.put('/api/holdings/000001/days',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '持仓天数必须是正整数' in data['error']['message']
    
    def test_update_holding_days_zero_value(self, client, db_session):
        """测试更新零值持仓天数"""
        update_data = {'holding_days': 0}
        
        response = client.put('/api/holdings/000001/days',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '持仓天数必须是正整数' in data['error']['message']
    
    def test_get_holding_days_success(self, client, db_session):
        """测试成功获取持仓天数"""
        stock_code = '000001'
        holding_days = 15
        
        # 先创建持仓天数记录
        create_data = {'holding_days': holding_days}
        client.post(f'/api/holdings/{stock_code}/days',
                   data=json.dumps(create_data),
                   content_type='application/json')
        
        # 获取持仓天数
        response = client.get(f'/api/holdings/{stock_code}/days')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['stock_code'] == stock_code
        assert data['data']['holding_days'] == holding_days
        assert f'获取股票{stock_code}持仓天数成功' in data['message']
    
    def test_get_holding_days_not_found(self, client, db_session):
        """测试获取不存在的持仓天数"""
        response = client.get('/api/holdings/999999/days')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['holding_days'] is None
    
    def test_create_holding_days_success(self, client, db_session):
        """测试成功创建持仓天数"""
        stock_code = '000001'
        holding_days = 10
        
        create_data = {'holding_days': holding_days}
        
        response = client.post(f'/api/holdings/{stock_code}/days',
                             data=json.dumps(create_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['holding_days'] == holding_days
        assert f'创建股票{stock_code}持仓天数成功' in data['message']
    
    def test_create_holding_days_missing_data(self, client, db_session):
        """测试创建持仓天数缺少数据"""
        response = client.post('/api/holdings/000001/days',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '持仓天数不能为空' in data['error']['message']
    
    def test_create_holding_days_invalid_data(self, client, db_session):
        """测试创建无效的持仓天数"""
        create_data = {'holding_days': 'invalid'}
        
        response = client.post('/api/holdings/000001/days',
                             data=json.dumps(create_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '持仓天数必须是正整数' in data['error']['message']
    
    def test_create_holding_days_negative_value(self, client, db_session):
        """测试创建负数持仓天数"""
        create_data = {'holding_days': -3}
        
        response = client.post('/api/holdings/000001/days',
                             data=json.dumps(create_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '持仓天数必须是正整数' in data['error']['message']
    
    def test_create_holding_days_already_exists(self, client, db_session):
        """测试创建已存在的持仓天数记录"""
        stock_code = '000001'
        holding_days = 10
        
        create_data = {'holding_days': holding_days}
        
        # 第一次创建
        response1 = client.post(f'/api/holdings/{stock_code}/days',
                              data=json.dumps(create_data),
                              content_type='application/json')
        assert response1.status_code == 201
        
        # 第二次创建应该失败
        response2 = client.post(f'/api/holdings/{stock_code}/days',
                              data=json.dumps(create_data),
                              content_type='application/json')
        
        assert response2.status_code == 400
        data = json.loads(response2.data)
        assert data['success'] is False
        assert '已存在复盘记录' in data['error']['message']
    
    def test_delete_holding_days_success(self, client, db_session):
        """测试成功删除持仓天数"""
        stock_code = '000001'
        holding_days = 10
        
        # 先创建持仓天数记录
        create_data = {'holding_days': holding_days}
        client.post(f'/api/holdings/{stock_code}/days',
                   data=json.dumps(create_data),
                   content_type='application/json')
        
        # 删除持仓天数
        response = client.delete(f'/api/holdings/{stock_code}/days')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert f'删除股票{stock_code}持仓天数成功' in data['message']
    
    def test_delete_holding_days_not_found(self, client, db_session):
        """测试删除不存在的持仓天数"""
        response = client.delete('/api/holdings/999999/days')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert '没有复盘记录' in data['error']['message']
    
    def test_get_holding_stats(self, client, db_session):
        """测试获取持仓统计信息"""
        # 创建多个持仓
        holdings_data = [
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'trade_date': datetime(2024, 1, 10),
                'reason': '买入原因'
            },
            {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'buy',
                'price': 8.00,
                'quantity': 2000,
                'trade_date': datetime(2024, 1, 12),
                'reason': '买入原因'
            }
        ]
        
        for data in holdings_data:
            TradeRecord(**data).save()
        
        # 创建复盘记录设置持仓天数
        ReviewService.create_review({
            'stock_code': '000001',
            'review_date': date.today(),
            'holding_days': 10,
            'price_up_score': 1
        })
        
        ReviewService.create_review({
            'stock_code': '000002',
            'review_date': date.today(),
            'holding_days': 8,
            'price_up_score': 1
        })
        
        response = client.get('/api/holdings/stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['total_holdings'] == 2
        assert data['data']['avg_holding_days'] == 9.0
        assert len(data['data']['holdings_by_days']) == 2
    
    def test_get_review_stats(self, client, db_session):
        """测试获取复盘统计信息"""
        # 创建测试数据
        reviews_data = [
            {
                'stock_code': '000001',
                'review_date': '2024-01-15',
                'price_up_score': 1,
                'bbi_score': 1,
                'decision': 'hold'
            },
            {
                'stock_code': '000002',
                'review_date': '2024-01-16',
                'price_up_score': 1,
                'bbi_score': 1,
                'volume_score': 1,
                'decision': 'sell_all'
            },
            {
                'stock_code': '000003',
                'review_date': date.today().isoformat(),  # 最近7天内
                'price_up_score': 0,
                'bbi_score': 0,
                'decision': 'hold'
            }
        ]
        
        for data in reviews_data:
            ReviewService.create_review(data)
        
        response = client.get('/api/reviews/stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['total_reviews'] == 3
        assert data['data']['avg_score'] > 0
        assert 'score_distribution' in data['data']
        assert 'decision_distribution' in data['data']
        assert data['data']['recent_reviews_7days'] >= 1