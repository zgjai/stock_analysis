"""
历史交易复盘功能服务
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from sqlalchemy import and_, desc
from extensions import db
from services.base_service import BaseService
from models.trade_review import TradeReview, ReviewImage
from models.historical_trade import HistoricalTrade
from error_handlers import ValidationError, NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class TradeReviewService(BaseService):
    """历史交易复盘服务"""
    
    model = TradeReview
    
    # 支持的图片格式
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
        'image/bmp', 'image/webp'
    }
    
    # 文件大小限制 (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    @classmethod
    def create_review(cls, historical_trade_id: int, review_data: Dict[str, Any]) -> TradeReview:
        """创建复盘记录"""
        try:
            logger.info(f"创建复盘记录 - 历史交易ID: {historical_trade_id}")
            
            # 验证历史交易是否存在
            historical_trade = HistoricalTrade.query.get(historical_trade_id)
            if not historical_trade:
                raise NotFoundError(f"历史交易记录不存在: {historical_trade_id}")
            
            # 检查是否已存在复盘记录
            existing_review = TradeReview.query.filter_by(
                historical_trade_id=historical_trade_id
            ).first()
            
            if existing_review:
                raise ValidationError(f"历史交易 {historical_trade_id} 已存在复盘记录")
            
            # 验证复盘数据
            cls._validate_review_data(review_data)
            
            # 创建复盘记录
            review_data['historical_trade_id'] = historical_trade_id
            review = TradeReview(**review_data)
            review.save()
            
            logger.info(f"复盘记录创建成功 - ID: {review.id}")
            return review
            
        except Exception as e:
            logger.error(f"创建复盘记录失败: {str(e)}")
            if isinstance(e, (ValidationError, NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"创建复盘记录失败: {str(e)}")
    
    @classmethod
    def update_review(cls, review_id: int, review_data: Dict[str, Any]) -> TradeReview:
        """更新复盘记录"""
        try:
            logger.info(f"更新复盘记录 - ID: {review_id}")
            
            review = cls.get_by_id(review_id)
            
            # 验证复盘数据
            cls._validate_review_data(review_data, is_update=True)
            
            # 更新字段
            for key, value in review_data.items():
                if hasattr(review, key) and key != 'historical_trade_id':
                    setattr(review, key, value)
            
            review.save()
            
            logger.info(f"复盘记录更新成功 - ID: {review.id}")
            return review
            
        except Exception as e:
            logger.error(f"更新复盘记录失败: {str(e)}")
            if isinstance(e, (ValidationError, NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"更新复盘记录失败: {str(e)}")
    
    @classmethod
    def get_review_by_id(cls, review_id: int) -> TradeReview:
        """根据复盘ID获取复盘记录"""
        try:
            review = TradeReview.query.get(review_id)
            if not review:
                raise NotFoundError(f"复盘记录不存在: {review_id}")
            return review
        except Exception as e:
            logger.error(f"获取复盘记录失败: {str(e)}")
            if isinstance(e, NotFoundError):
                raise e
            raise DatabaseError(f"获取复盘记录失败: {str(e)}")
    
    @classmethod
    def get_review_by_trade(cls, historical_trade_id: int) -> Optional[TradeReview]:
        """根据历史交易ID获取复盘记录"""
        try:
            return TradeReview.query.filter_by(
                historical_trade_id=historical_trade_id
            ).first()
        except Exception as e:
            logger.error(f"获取复盘记录失败: {str(e)}")
            raise DatabaseError(f"获取复盘记录失败: {str(e)}")
    
    @classmethod
    def get_reviews_list(cls, filters: Dict[str, Any] = None, 
                        page: int = None, per_page: int = None) -> Dict[str, Any]:
        """获取复盘记录列表"""
        try:
            query = TradeReview.query.join(HistoricalTrade)
            
            # 应用筛选条件
            if filters:
                if filters.get('stock_code'):
                    query = query.filter(HistoricalTrade.stock_code == filters['stock_code'])
                
                if filters.get('review_type'):
                    query = query.filter(TradeReview.review_type == filters['review_type'])
                
                if filters.get('min_overall_score') is not None:
                    query = query.filter(TradeReview.overall_score >= filters['min_overall_score'])
                
                if filters.get('max_overall_score') is not None:
                    query = query.filter(TradeReview.overall_score <= filters['max_overall_score'])
                
                if filters.get('start_date'):
                    start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                    query = query.filter(HistoricalTrade.sell_date >= start_date)
                
                if filters.get('end_date'):
                    end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                    query = query.filter(HistoricalTrade.sell_date <= end_date)
            
            # 按创建时间倒序排列
            query = query.order_by(desc(TradeReview.created_at))
            
            # 应用分页
            if page and per_page:
                pagination = query.paginate(
                    page=page,
                    per_page=per_page,
                    error_out=False
                )
                
                reviews = []
                for review in pagination.items:
                    review_dict = review.to_dict()
                    # 添加历史交易信息
                    historical_trade = HistoricalTrade.query.get(review.historical_trade_id)
                    if historical_trade:
                        review_dict['historical_trade'] = historical_trade.to_dict()
                    reviews.append(review_dict)
                
                return {
                    'reviews': reviews,
                    'pagination': {
                        'page': pagination.page,
                        'per_page': pagination.per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_prev': pagination.has_prev,
                        'has_next': pagination.has_next
                    }
                }
            else:
                reviews = query.all()
                result_reviews = []
                for review in reviews:
                    review_dict = review.to_dict()
                    # 添加历史交易信息
                    historical_trade = HistoricalTrade.query.get(review.historical_trade_id)
                    if historical_trade:
                        review_dict['historical_trade'] = historical_trade.to_dict()
                    result_reviews.append(review_dict)
                
                return {
                    'reviews': result_reviews,
                    'total': len(result_reviews)
                }
                
        except Exception as e:
            logger.error(f"获取复盘记录列表失败: {str(e)}")
            raise DatabaseError(f"获取复盘记录列表失败: {str(e)}")
    
    @classmethod
    def delete_review(cls, review_id: int) -> bool:
        """删除复盘记录"""
        try:
            logger.info(f"删除复盘记录 - ID: {review_id}")
            
            review = cls.get_by_id(review_id)
            
            # 删除关联的图片文件和记录
            images = ReviewImage.query.filter_by(trade_review_id=review_id).all()
            for image in images:
                cls._delete_image_file(image.file_path)
                image.delete()
            
            # 删除复盘记录
            review.delete()
            
            logger.info(f"复盘记录删除成功 - ID: {review_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除复盘记录失败: {str(e)}")
            if isinstance(e, (NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"删除复盘记录失败: {str(e)}")
    
    @classmethod
    def upload_review_images(cls, review_id: int, files: List[FileStorage], 
                           descriptions: List[str] = None) -> List[ReviewImage]:
        """上传复盘图片"""
        try:
            logger.info(f"上传复盘图片 - 复盘ID: {review_id}, 文件数量: {len(files)}")
            
            # 验证复盘记录是否存在
            review = cls.get_by_id(review_id)
            
            uploaded_images = []
            
            for i, file in enumerate(files):
                if file and file.filename:
                    # 验证文件
                    cls._validate_image_file(file)
                    
                    # 生成安全的文件名
                    filename = cls._generate_secure_filename(file.filename)
                    
                    # 创建上传目录
                    upload_dir = cls._get_upload_directory()
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # 保存文件
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    
                    # 创建图片记录
                    image_data = {
                        'trade_review_id': review_id,
                        'filename': filename,
                        'original_filename': file.filename,
                        'file_path': file_path,
                        'file_size': os.path.getsize(file_path),
                        'mime_type': file.mimetype,
                        'display_order': i,
                        'description': descriptions[i] if descriptions and i < len(descriptions) else None
                    }
                    
                    image = ReviewImage(**image_data)
                    image.save()
                    uploaded_images.append(image)
            
            logger.info(f"图片上传成功 - 数量: {len(uploaded_images)}")
            return uploaded_images
            
        except Exception as e:
            logger.error(f"上传复盘图片失败: {str(e)}")
            if isinstance(e, (ValidationError, NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"上传复盘图片失败: {str(e)}")
    
    @classmethod
    def get_review_images(cls, review_id: int) -> List[ReviewImage]:
        """获取复盘图片列表"""
        try:
            return ReviewImage.query.filter_by(
                trade_review_id=review_id
            ).order_by(ReviewImage.display_order.asc()).all()
        except Exception as e:
            logger.error(f"获取复盘图片失败: {str(e)}")
            raise DatabaseError(f"获取复盘图片失败: {str(e)}")
    
    @classmethod
    def delete_review_image(cls, image_id: int) -> bool:
        """删除复盘图片"""
        try:
            logger.info(f"删除复盘图片 - ID: {image_id}")
            
            image = ReviewImage.query.get(image_id)
            if not image:
                raise NotFoundError(f"图片记录不存在: {image_id}")
            
            # 删除文件
            cls._delete_image_file(image.file_path)
            
            # 删除记录
            image.delete()
            
            logger.info(f"复盘图片删除成功 - ID: {image_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除复盘图片失败: {str(e)}")
            if isinstance(e, (NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"删除复盘图片失败: {str(e)}")
    
    @classmethod
    def update_image_order(cls, review_id: int, image_orders: List[Dict[str, int]]) -> bool:
        """更新图片显示顺序"""
        try:
            logger.info(f"更新图片显示顺序 - 复盘ID: {review_id}")
            
            for order_data in image_orders:
                image_id = order_data.get('image_id')
                new_order = order_data.get('display_order')
                
                if image_id and new_order is not None:
                    image = ReviewImage.query.filter_by(
                        id=image_id,
                        trade_review_id=review_id
                    ).first()
                    
                    if image:
                        image.display_order = new_order
                        image.save()
            
            logger.info(f"图片显示顺序更新成功")
            return True
            
        except Exception as e:
            logger.error(f"更新图片显示顺序失败: {str(e)}")
            raise DatabaseError(f"更新图片显示顺序失败: {str(e)}")
    
    @classmethod
    def _validate_review_data(cls, data: Dict[str, Any], is_update: bool = False) -> None:
        """验证复盘数据"""
        # 验证复盘类型
        if 'review_type' in data and data['review_type']:
            valid_types = ['general', 'success', 'failure', 'lesson']
            if data['review_type'] not in valid_types:
                raise ValidationError(f"复盘类型必须是{', '.join(valid_types)}之一")
        
        # 验证评分范围
        score_fields = ['strategy_score', 'timing_score', 'risk_control_score', 'overall_score']
        for field in score_fields:
            if field in data and data[field] is not None:
                try:
                    score = int(data[field])
                    if score < 1 or score > 5:
                        raise ValidationError(f"{field}必须是1-5之间的整数")
                except (ValueError, TypeError):
                    raise ValidationError(f"{field}必须是整数")
        
        # 验证标题长度
        if 'review_title' in data and data['review_title']:
            if len(data['review_title']) > 200:
                raise ValidationError("复盘标题不能超过200个字符")
    
    @classmethod
    def _validate_image_file(cls, file: FileStorage) -> None:
        """验证图片文件"""
        # 检查文件是否为空
        if not file or not file.filename:
            raise ValidationError("文件不能为空")
        
        # 检查文件扩展名
        filename = file.filename.lower()
        if '.' not in filename:
            raise ValidationError("文件必须有扩展名")
        
        extension = filename.rsplit('.', 1)[1]
        if extension not in cls.ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(f"不支持的文件格式，支持的格式: {', '.join(cls.ALLOWED_IMAGE_EXTENSIONS)}")
        
        # 检查MIME类型
        if file.mimetype and file.mimetype not in cls.ALLOWED_MIME_TYPES:
            raise ValidationError(f"不支持的文件类型: {file.mimetype}")
        
        # 检查文件大小
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        
        if file_size > cls.MAX_FILE_SIZE:
            raise ValidationError(f"文件大小不能超过 {cls.MAX_FILE_SIZE / (1024 * 1024):.1f} MB")
        
        if file_size == 0:
            raise ValidationError("文件不能为空")
    
    @classmethod
    def _generate_secure_filename(cls, filename: str) -> str:
        """生成安全的文件名"""
        # 获取文件扩展名
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        # 生成时间戳文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        secure_name = f"review_{timestamp}.{extension}"
        
        return secure_filename(secure_name)
    
    @classmethod
    def _get_upload_directory(cls) -> str:
        """获取上传目录"""
        from flask import current_app
        
        # 从配置获取上传目录，默认为 uploads/review_images
        upload_dir = current_app.config.get('REVIEW_IMAGES_UPLOAD_FOLDER', 'uploads/review_images')
        
        # 如果是相对路径，则相对于应用根目录
        if not os.path.isabs(upload_dir):
            upload_dir = os.path.join(current_app.root_path, upload_dir)
        
        return upload_dir
    
    @classmethod
    def _delete_image_file(cls, file_path: str) -> None:
        """删除图片文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"图片文件删除成功: {file_path}")
        except Exception as e:
            logger.warning(f"删除图片文件失败: {file_path}, 错误: {str(e)}")