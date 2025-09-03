"""
历史交易复盘服务测试
"""
import os
import tempfile
import pytest
from datetime import datetime
from werkzeug.datastructures import FileStorage
from io import BytesIO

from app import create_app
from config import TestingConfig
from extensions import db
from models.historical_trade import HistoricalTrade
from models.trade_review import TradeReview, ReviewImage
from services.trade_review_service import TradeReviewService
from error_handlers import ValidationError, NotFoundError, DatabaseError


class TestTradeReviewService:
    """历史交易复盘服务测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
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
    
    def test_create_review_success(self):
        """测试成功创建复盘记录"""
        review_data = {
            'review_title': '测试复盘',
            'review_content': '这是一次成功的交易',
            'review_type': 'success',
            'strategy_score': 4,
            'timing_score': 5,
            'risk_control_score': 4,
            'overall_score': 4,
            'key_learnings': '学到了很多',
            'improvement_areas': '需要改进的地方'
        }
        
        review = TradeReviewService.create_review(self.historical_trade.id, review_data)
        
        assert review is not None
        assert review.historical_trade_id == self.historical_trade.id
        assert review.review_title == '测试复盘'
        assert review.review_type == 'success'
        assert review.strategy_score == 4
        assert review.overall_score == 4
    
    def test_create_review_duplicate(self):
        """测试创建重复复盘记录"""
        review_data = {
            'review_title': '测试复盘',
            'review_content': '这是一次成功的交易',
            'review_type': 'success'
        }
        
        # 创建第一个复盘记录
        TradeReviewService.create_review(self.historical_trade.id, review_data)
        
        # 尝试创建重复记录
        with pytest.raises(ValidationError, match="已存在复盘记录"):
            TradeReviewService.create_review(self.historical_trade.id, review_data)
    
    def test_create_review_invalid_historical_trade(self):
        """测试创建复盘记录时历史交易不存在"""
        review_data = {
            'review_title': '测试复盘',
            'review_content': '这是一次成功的交易'
        }
        
        with pytest.raises(NotFoundError, match="历史交易记录不存在"):
            TradeReviewService.create_review(99999, review_data)
    
    def test_create_review_invalid_data(self):
        """测试创建复盘记录时数据验证失败"""
        # 测试无效的复盘类型
        review_data = {
            'review_type': 'invalid_type'
        }
        
        with pytest.raises(ValidationError, match="复盘类型必须是"):
            TradeReviewService.create_review(self.historical_trade.id, review_data)
        
        # 测试无效的评分
        review_data = {
            'strategy_score': 6  # 超出范围
        }
        
        with pytest.raises(ValidationError, match="必须是1-5之间的整数"):
            TradeReviewService.create_review(self.historical_trade.id, review_data)
    
    def test_update_review_success(self):
        """测试成功更新复盘记录"""
        # 先创建复盘记录
        review_data = {
            'review_title': '原始复盘',
            'review_content': '原始内容',
            'strategy_score': 3
        }
        
        review = TradeReviewService.create_review(self.historical_trade.id, review_data)
        
        # 更新复盘记录
        update_data = {
            'review_title': '更新后的复盘',
            'review_content': '更新后的内容',
            'strategy_score': 4
        }
        
        updated_review = TradeReviewService.update_review(review.id, update_data)
        
        assert updated_review.review_title == '更新后的复盘'
        assert updated_review.review_content == '更新后的内容'
        assert updated_review.strategy_score == 4
    
    def test_update_review_not_found(self):
        """测试更新不存在的复盘记录"""
        update_data = {
            'review_title': '更新后的复盘'
        }
        
        with pytest.raises(NotFoundError):
            TradeReviewService.update_review(99999, update_data)
    
    def test_get_review_by_trade(self):
        """测试根据历史交易ID获取复盘记录"""
        # 创建复盘记录
        review_data = {
            'review_title': '测试复盘',
            'review_content': '测试内容'
        }
        
        created_review = TradeReviewService.create_review(self.historical_trade.id, review_data)
        
        # 获取复盘记录
        review = TradeReviewService.get_review_by_trade(self.historical_trade.id)
        
        assert review is not None
        assert review.id == created_review.id
        assert review.review_title == '测试复盘'
        
        # 测试不存在的情况
        review = TradeReviewService.get_review_by_trade(99999)
        assert review is None
    
    def test_get_reviews_list(self):
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
            
            review_data = {
                'review_title': f'复盘{i+1}',
                'review_type': 'success' if i % 2 == 0 else 'failure',
                'overall_score': i + 3
            }
            
            TradeReviewService.create_review(historical_trade.id, review_data)
        
        # 获取所有复盘记录
        result = TradeReviewService.get_reviews_list()
        
        assert 'reviews' in result
        assert 'total' in result
        assert result['total'] == 3
        assert len(result['reviews']) == 3
        
        # 测试筛选
        filters = {'review_type': 'success'}
        result = TradeReviewService.get_reviews_list(filters=filters)
        
        success_reviews = [r for r in result['reviews'] if r['review_type'] == 'success']
        assert len(success_reviews) == 2
        
        # 测试分页
        result = TradeReviewService.get_reviews_list(page=1, per_page=2)
        
        assert 'pagination' in result
        assert result['pagination']['page'] == 1
        assert result['pagination']['per_page'] == 2
        assert len(result['reviews']) == 2
    
    def test_delete_review(self):
        """测试删除复盘记录"""
        # 创建复盘记录
        review_data = {
            'review_title': '待删除的复盘',
            'review_content': '测试内容'
        }
        
        review = TradeReviewService.create_review(self.historical_trade.id, review_data)
        review_id = review.id
        
        # 删除复盘记录
        result = TradeReviewService.delete_review(review_id)
        
        assert result is True
        
        # 验证记录已删除
        with pytest.raises(NotFoundError):
            TradeReviewService.get_by_id(review_id)
    
    def test_upload_review_images(self):
        """测试上传复盘图片"""
        # 创建复盘记录
        review_data = {
            'review_title': '测试复盘',
            'review_content': '测试内容'
        }
        
        review = TradeReviewService.create_review(self.historical_trade.id, review_data)
        
        # 创建测试图片文件
        image_data = b'fake image data'
        files = [
            FileStorage(
                stream=BytesIO(image_data),
                filename='test1.jpg',
                content_type='image/jpeg'
            ),
            FileStorage(
                stream=BytesIO(image_data),
                filename='test2.png',
                content_type='image/png'
            )
        ]
        
        descriptions = ['测试图片1', '测试图片2']
        
        # 模拟上传目录
        with tempfile.TemporaryDirectory() as temp_dir:
            self.app.config['REVIEW_IMAGES_UPLOAD_FOLDER'] = temp_dir
            
            uploaded_images = TradeReviewService.upload_review_images(
                review.id, files, descriptions
            )
            
            assert len(uploaded_images) == 2
            assert uploaded_images[0].original_filename == 'test1.jpg'
            assert uploaded_images[1].original_filename == 'test2.png'
            assert uploaded_images[0].description == '测试图片1'
            assert uploaded_images[1].description == '测试图片2'
    
    def test_upload_invalid_image(self):
        """测试上传无效图片"""
        # 创建复盘记录
        review_data = {
            'review_title': '测试复盘',
            'review_content': '测试内容'
        }
        
        review = TradeReviewService.create_review(self.historical_trade.id, review_data)
        
        # 测试无效文件扩展名
        invalid_file = FileStorage(
            stream=BytesIO(b'fake data'),
            filename='test.txt',
            content_type='text/plain'
        )
        
        with pytest.raises(ValidationError, match="不支持的文件格式"):
            TradeReviewService.upload_review_images(review.id, [invalid_file])
        
        # 测试空文件
        empty_file = FileStorage(
            stream=BytesIO(b''),
            filename='test.jpg',
            content_type='image/jpeg'
        )
        
        with pytest.raises(ValidationError, match="文件不能为空"):
            TradeReviewService.upload_review_images(review.id, [empty_file])
    
    def test_get_review_images(self):
        """测试获取复盘图片列表"""
        # 创建复盘记录
        review_data = {
            'review_title': '测试复盘',
            'review_content': '测试内容'
        }
        
        review = TradeReviewService.create_review(self.historical_trade.id, review_data)
        
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
        
        # 获取图片列表
        images = TradeReviewService.get_review_images(review.id)
        
        assert len(images) == 2
        assert images[0].display_order == 0
        assert images[1].display_order == 1
    
    def test_delete_review_image(self):
        """测试删除复盘图片"""
        # 创建复盘记录
        review_data = {
            'review_title': '测试复盘',
            'review_content': '测试内容'
        }
        
        review = TradeReviewService.create_review(self.historical_trade.id, review_data)
        
        # 创建测试图片记录
        image = ReviewImage(
            trade_review_id=review.id,
            filename='test.jpg',
            original_filename='test.jpg',
            file_path='/fake/path/test.jpg'
        )
        image.save()
        image_id = image.id
        
        # 删除图片
        result = TradeReviewService.delete_review_image(image_id)
        
        assert result is True
        
        # 验证图片记录已删除
        deleted_image = ReviewImage.query.get(image_id)
        assert deleted_image is None
    
    def test_update_image_order(self):
        """测试更新图片显示顺序"""
        # 创建复盘记录
        review_data = {
            'review_title': '测试复盘',
            'review_content': '测试内容'
        }
        
        review = TradeReviewService.create_review(self.historical_trade.id, review_data)
        
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
        
        # 更新显示顺序
        image_orders = [
            {'image_id': image1.id, 'display_order': 1},
            {'image_id': image2.id, 'display_order': 0}
        ]
        
        result = TradeReviewService.update_image_order(review.id, image_orders)
        
        assert result is True
        
        # 验证顺序已更新
        updated_image1 = ReviewImage.query.get(image1.id)
        updated_image2 = ReviewImage.query.get(image2.id)
        
        assert updated_image1.display_order == 1
        assert updated_image2.display_order == 0
    
    def test_validate_review_data(self):
        """测试复盘数据验证"""
        # 测试有效数据
        valid_data = {
            'review_type': 'success',
            'strategy_score': 4,
            'timing_score': 5,
            'review_title': '有效的复盘标题'
        }
        
        # 不应该抛出异常
        TradeReviewService._validate_review_data(valid_data)
        
        # 测试无效复盘类型
        invalid_data = {'review_type': 'invalid'}
        with pytest.raises(ValidationError):
            TradeReviewService._validate_review_data(invalid_data)
        
        # 测试无效评分
        invalid_data = {'strategy_score': 0}
        with pytest.raises(ValidationError):
            TradeReviewService._validate_review_data(invalid_data)
        
        invalid_data = {'timing_score': 6}
        with pytest.raises(ValidationError):
            TradeReviewService._validate_review_data(invalid_data)
        
        # 测试标题过长
        invalid_data = {'review_title': 'x' * 201}
        with pytest.raises(ValidationError):
            TradeReviewService._validate_review_data(invalid_data)
    
    def test_validate_image_file(self):
        """测试图片文件验证"""
        # 测试有效图片
        valid_file = FileStorage(
            stream=BytesIO(b'fake image data'),
            filename='test.jpg',
            content_type='image/jpeg'
        )
        
        # 不应该抛出异常
        TradeReviewService._validate_image_file(valid_file)
        
        # 测试无效扩展名
        invalid_file = FileStorage(
            stream=BytesIO(b'fake data'),
            filename='test.txt',
            content_type='text/plain'
        )
        
        with pytest.raises(ValidationError):
            TradeReviewService._validate_image_file(invalid_file)
        
        # 测试空文件名
        invalid_file = FileStorage(
            stream=BytesIO(b'fake data'),
            filename='',
            content_type='image/jpeg'
        )
        
        with pytest.raises(ValidationError):
            TradeReviewService._validate_image_file(invalid_file)
        
        # 测试空文件
        invalid_file = FileStorage(
            stream=BytesIO(b''),
            filename='test.jpg',
            content_type='image/jpeg'
        )
        
        with pytest.raises(ValidationError):
            TradeReviewService._validate_image_file(invalid_file)