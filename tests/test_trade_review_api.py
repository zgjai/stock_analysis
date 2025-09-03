"""
历史交易复盘API测试
"""
import json
import tempfile
from io import BytesIO
import pytest
from datetime import datetime

from app import create_app
from config import TestingConfig
from extensions import db
from models.historical_trade import HistoricalTrade
from models.trade_review import TradeReview, ReviewImage


class TestTradeReviewAPI:
    """历史交易复盘API测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # 创建测试数据库表
        db.create_all()
        
        # 创建测试历史交易记录
        self.historical_trade = HistoricalTrade(
            stock_code='000001',
            stock_name='平安银行',
            buy_date=datetime(2024, 1, 1),
            sell_date=datetime(2024, 2, 1),
            holding_days=31,
            total_investment=10000.00,
            total_return=1000.00,
            return_rate=0.10,
            buy_records_ids='[1,2]',
            sell_records_ids='[3,4]',
            is_completed=True,
            completion_date=datetime(2024, 2, 1)
        )
        self.historical_trade.save()
        
        yield
        
        # 清理
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_trade_review_not_exists(self):
        """测试获取不存在的复盘记录"""
        response = self.client.get(f'/api/trade-reviews/{self.historical_trade.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data.get('data') is None
        assert "暂无复盘记录" in data['message']
    
    def test_get_trade_review_exists(self):
        """测试获取存在的复盘记录"""
        # 先创建复盘记录
        review = TradeReview(
            historical_trade_id=self.historical_trade.id,
            review_title='测试复盘',
            review_content='测试内容',
            review_type='success',
            strategy_score=4,
            overall_score=4
        )
        review.save()
        
        response = self.client.get(f'/api/trade-reviews/{self.historical_trade.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] is not None
        assert data['data']['review_title'] == '测试复盘'
        assert data['data']['review_type'] == 'success'
        assert 'images' in data['data']
    
    def test_create_trade_review_success(self):
        """测试成功创建复盘记录"""
        review_data = {
            'historical_trade_id': self.historical_trade.id,
            'review_title': '新建复盘',
            'review_content': '这是一次成功的交易',
            'review_type': 'success',
            'strategy_score': 4,
            'timing_score': 5,
            'risk_control_score': 4,
            'overall_score': 4,
            'key_learnings': '学到了很多',
            'improvement_areas': '需要改进的地方'
        }
        
        response = self.client.post(
            '/api/trade-reviews',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['review_title'] == '新建复盘'
        assert data['data']['review_type'] == 'success'
        assert data['data']['strategy_score'] == 4
    
    def test_create_trade_review_invalid_data(self):
        """测试创建复盘记录时数据无效"""
        # 测试缺少历史交易ID
        review_data = {
            'review_title': '新建复盘',
            'review_content': '测试内容'
        }
        
        response = self.client.post(
            '/api/trade-reviews',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert "历史交易ID不能为空" in data['message']
        
        # 测试无效的评分
        review_data = {
            'historical_trade_id': self.historical_trade.id,
            'strategy_score': 6  # 超出范围
        }
        
        response = self.client.post(
            '/api/trade-reviews',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_create_trade_review_duplicate(self):
        """测试创建重复复盘记录"""
        # 先创建一个复盘记录
        review = TradeReview(
            historical_trade_id=self.historical_trade.id,
            review_title='已存在的复盘',
            review_content='测试内容'
        )
        review.save()
        
        # 尝试创建重复记录
        review_data = {
            'historical_trade_id': self.historical_trade.id,
            'review_title': '新建复盘',
            'review_content': '测试内容'
        }
        
        response = self.client.post(
            '/api/trade-reviews',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400  # 验证错误
        data = json.loads(response.data)
        assert data['success'] is False
        assert "已存在复盘记录" in data['message']
    
    def test_update_trade_review_success(self):
        """测试成功更新复盘记录"""
        # 先创建复盘记录
        review = TradeReview(
            historical_trade_id=self.historical_trade.id,
            review_title='原始复盘',
            review_content='原始内容',
            strategy_score=3
        )
        review.save()
        
        # 更新数据
        update_data = {
            'review_title': '更新后的复盘',
            'review_content': '更新后的内容',
            'strategy_score': 4
        }
        
        response = self.client.put(
            f'/api/trade-reviews/{review.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['review_title'] == '更新后的复盘'
        assert data['data']['strategy_score'] == 4
    
    def test_update_trade_review_not_found(self):
        """测试更新不存在的复盘记录"""
        update_data = {
            'review_title': '更新后的复盘'
        }
        
        response = self.client.put(
            '/api/trade-reviews/99999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_delete_trade_review_success(self):
        """测试成功删除复盘记录"""
        # 先创建复盘记录
        review = TradeReview(
            historical_trade_id=self.historical_trade.id,
            review_title='待删除的复盘',
            review_content='测试内容'
        )
        review.save()
        review_id = review.id
        
        response = self.client.delete(f'/api/trade-reviews/{review_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert "删除成功" in data['message']
        
        # 验证记录已删除
        deleted_review = TradeReview.query.get(review_id)
        assert deleted_review is None
    
    def test_delete_trade_review_not_found(self):
        """测试删除不存在的复盘记录"""
        response = self.client.delete('/api/trade-reviews/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_trade_reviews_list(self):
        """测试获取复盘记录列表"""
        # 创建多个复盘记录
        for i in range(3):
            historical_trade = HistoricalTrade(
                stock_code=f'00000{i+2}',
                stock_name=f'测试股票{i+2}',
                buy_date=datetime(2024, 1, 1),
                sell_date=datetime(2024, 2, 1),
                holding_days=31,
                total_investment=10000.00,
                total_return=1000.00,
                return_rate=0.10,
                is_completed=True,
                completion_date=datetime(2024, 2, 1)
            )
            historical_trade.save()
            
            review = TradeReview(
                historical_trade_id=historical_trade.id,
                review_title=f'复盘{i+1}',
                review_type='success' if i % 2 == 0 else 'failure',
                overall_score=i + 3
            )
            review.save()
        
        # 获取所有复盘记录
        response = self.client.get('/api/trade-reviews')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'reviews' in data['data']
        assert 'total' in data['data']
        assert data['data']['total'] == 3
        
        # 测试筛选
        response = self.client.get('/api/trade-reviews?review_type=success')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        success_reviews = [r for r in data['data']['reviews'] if r['review_type'] == 'success']
        assert len(success_reviews) == 2
        
        # 测试分页
        response = self.client.get('/api/trade-reviews?page=1&per_page=2')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'pagination' in data['data']
        assert data['data']['pagination']['page'] == 1
        assert data['data']['pagination']['per_page'] == 2
    
    def test_upload_review_images_success(self):
        """测试成功上传复盘图片"""
        # 先创建复盘记录
        review = TradeReview(
            historical_trade_id=self.historical_trade.id,
            review_title='测试复盘',
            review_content='测试内容'
        )
        review.save()
        
        # 创建测试图片数据
        image_data = b'fake image data'
        
        with tempfile.TemporaryDirectory() as temp_dir:
            self.app.config['REVIEW_IMAGES_UPLOAD_FOLDER'] = temp_dir
            
            response = self.client.post(
                f'/api/trade-reviews/{review.id}/images',
                data={
                    'images': [(BytesIO(image_data), 'test1.jpg'), (BytesIO(image_data), 'test2.png')],
                    'descriptions': ['测试图片1', '测试图片2']
                },
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['data']) == 2
            assert "成功上传" in data['message']
    
    def test_upload_review_images_no_files(self):
        """测试上传复盘图片时没有文件"""
        # 先创建复盘记录
        review = TradeReview(
            historical_trade_id=self.historical_trade.id,
            review_title='测试复盘',
            review_content='测试内容'
        )
        review.save()
        
        response = self.client.post(
            f'/api/trade-reviews/{review.id}/images',
            data={},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert "没有找到上传的图片文件" in data['message']
    
    def test_get_review_images(self):
        """测试获取复盘图片列表"""
        # 先创建复盘记录
        review = TradeReview(
            historical_trade_id=self.historical_trade.id,
            review_title='测试复盘',
            review_content='测试内容'
        )
        review.save()
        
        # 创建测试图片记录
        image1 = ReviewImage(
            trade_review_id=review.id,
            filename='test1.jpg',
            original_filename='test1.jpg',
            file_path='/fake/path/test1.jpg',
            display_order=0
        )
        image1.save()
        
        image2 = ReviewImage(
            trade_review_id=review.id,
            filename='test2.jpg',
            original_filename='test2.jpg',
            file_path='/fake/path/test2.jpg',
            display_order=1
        )
        image2.save()
        
        response = self.client.get(f'/api/trade-reviews/{review.id}/images')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 2
        assert data['data'][0]['display_order'] == 0
        assert data['data'][1]['display_order'] == 1
    
    def test_delete_review_image_success(self):
        """测试成功删除复盘图片"""
        # 先创建复盘记录和图片
        review = TradeReview(
            historical_trade_id=self.historical_trade.id,
            review_title='测试复盘',
            review_content='测试内容'
        )
        review.save()
        
        image = ReviewImage(
            trade_review_id=review.id,
            filename='test.jpg',
            original_filename='test.jpg',
            file_path='/fake/path/test.jpg'
        )
        image.save()
        image_id = image.id
        
        response = self.client.delete(f'/api/review-images/{image_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert "删除成功" in data['message']
        
        # 验证图片记录已删除
        deleted_image = ReviewImage.query.get(image_id)
        assert deleted_image is None
    
    def test_delete_review_image_not_found(self):
        """测试删除不存在的复盘图片"""
        response = self.client.delete('/api/review-images/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_reorder_review_images_success(self):
        """测试成功重新排序复盘图片"""
        # 先创建复盘记录和图片
        review = TradeReview(
            historical_trade_id=self.historical_trade.id,
            review_title='测试复盘',
            review_content='测试内容'
        )
        review.save()
        
        image1 = ReviewImage(
            trade_review_id=review.id,
            filename='test1.jpg',
            original_filename='test1.jpg',
            file_path='/fake/path/test1.jpg',
            display_order=0
        )
        image1.save()
        
        image2 = ReviewImage(
            trade_review_id=review.id,
            filename='test2.jpg',
            original_filename='test2.jpg',
            file_path='/fake/path/test2.jpg',
            display_order=1
        )
        image2.save()
        
        # 重新排序
        reorder_data = {
            'image_orders': [
                {'image_id': image1.id, 'display_order': 1},
                {'image_id': image2.id, 'display_order': 0}
            ]
        }
        
        response = self.client.put(
            f'/api/trade-reviews/{review.id}/images/reorder',
            data=json.dumps(reorder_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert "排序更新成功" in data['message']
        
        # 验证顺序已更新
        updated_image1 = ReviewImage.query.get(image1.id)
        updated_image2 = ReviewImage.query.get(image2.id)
        
        assert updated_image1.display_order == 1
        assert updated_image2.display_order == 0
    
    def test_reorder_review_images_invalid_data(self):
        """测试重新排序复盘图片时数据无效"""
        # 先创建复盘记录
        review = TradeReview(
            historical_trade_id=self.historical_trade.id,
            review_title='测试复盘',
            review_content='测试内容'
        )
        review.save()
        
        # 测试缺少排序数据
        response = self.client.put(
            f'/api/trade-reviews/{review.id}/images/reorder',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert "请提供图片排序数据" in data['message']
    
    def test_get_review_stats(self):
        """测试获取复盘统计信息"""
        # 创建多个复盘记录
        for i in range(3):
            historical_trade = HistoricalTrade(
                stock_code=f'00000{i+2}',
                stock_name=f'测试股票{i+2}',
                buy_date=datetime(2024, 1, 1),
                sell_date=datetime(2024, 2, 1),
                holding_days=31,
                total_investment=10000.00,
                total_return=1000.00,
                return_rate=0.10,
                is_completed=True,
                completion_date=datetime(2024, 2, 1)
            )
            historical_trade.save()
            
            review = TradeReview(
                historical_trade_id=historical_trade.id,
                review_title=f'复盘{i+1}',
                review_type='success' if i % 2 == 0 else 'failure',
                overall_score=i + 3,
                strategy_score=i + 2,
                timing_score=i + 3,
                risk_control_score=i + 2
            )
            review.save()
        
        response = self.client.get('/api/trade-reviews/stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        stats = data['data']
        assert 'total_reviews' in stats
        assert 'total_trades' in stats
        assert 'review_coverage' in stats
        assert 'type_distribution' in stats
        assert 'score_distribution' in stats
        assert 'average_scores' in stats
        
        assert stats['total_reviews'] == 3
        assert stats['total_trades'] == 4  # 包括setup中创建的1个
        assert stats['type_distribution']['success'] == 2
        assert stats['type_distribution']['failure'] == 1