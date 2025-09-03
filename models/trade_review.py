"""
交易复盘记录数据模型
"""
from extensions import db
from models.base import BaseModel
from error_handlers import ValidationError


class TradeReview(BaseModel):
    """交易复盘记录模型"""
    
    __tablename__ = 'trade_reviews'
    
    # 关联历史交易
    historical_trade_id = db.Column(db.Integer, db.ForeignKey('historical_trades.id'), nullable=False, index=True)
    
    # 复盘内容
    review_title = db.Column(db.String(200))
    review_content = db.Column(db.Text)
    
    # 复盘分类
    review_type = db.Column(db.String(20), default='general')  # general, success, failure, lesson
    
    # 评分系统 (1-5分)
    strategy_score = db.Column(db.Integer)      # 策略执行评分
    timing_score = db.Column(db.Integer)        # 时机把握评分
    risk_control_score = db.Column(db.Integer)  # 风险控制评分
    overall_score = db.Column(db.Integer)       # 总体评分
    
    # 关键学习点
    key_learnings = db.Column(db.Text)
    improvement_areas = db.Column(db.Text)
    
    # 表约束
    __table_args__ = (
        db.CheckConstraint("review_type IN ('general', 'success', 'failure', 'lesson')", name='check_review_type'),
        db.CheckConstraint("strategy_score IS NULL OR (strategy_score >= 1 AND strategy_score <= 5)", name='check_strategy_score'),
        db.CheckConstraint("timing_score IS NULL OR (timing_score >= 1 AND timing_score <= 5)", name='check_timing_score'),
        db.CheckConstraint("risk_control_score IS NULL OR (risk_control_score >= 1 AND risk_control_score <= 5)", name='check_risk_control_score'),
        db.CheckConstraint("overall_score IS NULL OR (overall_score >= 1 AND overall_score <= 5)", name='check_overall_score'),
        db.Index('idx_review_historical_trade', 'historical_trade_id'),
        db.Index('idx_review_type', 'review_type'),
    )
    
    def __init__(self, **kwargs):
        """初始化复盘记录"""
        from flask import current_app
        current_app.logger.info(f"=== TradeReview.__init__ 开始 ===")
        current_app.logger.info(f"初始化参数: {kwargs}")
        
        # 数据验证
        self._validate_data(kwargs)
        
        # 调用父类构造函数
        super().__init__(**kwargs)
        
        current_app.logger.info("=== TradeReview.__init__ 完成 ===")
    
    def _validate_data(self, data):
        """验证复盘数据"""
        from flask import current_app
        current_app.logger.info(f"=== _validate_data 开始 ===")
        
        # 验证历史交易ID
        if 'historical_trade_id' in data:
            if data['historical_trade_id'] is None:
                raise ValidationError("历史交易ID不能为空", "historical_trade_id")
        
        # 验证复盘类型
        if 'review_type' in data and data['review_type']:
            valid_types = ['general', 'success', 'failure', 'lesson']
            if data['review_type'] not in valid_types:
                raise ValidationError(f"复盘类型必须是{', '.join(valid_types)}之一", "review_type")
        
        # 验证评分范围
        score_fields = ['strategy_score', 'timing_score', 'risk_control_score', 'overall_score']
        for field in score_fields:
            if field in data and data[field] is not None:
                score = data[field]
                if not isinstance(score, int) or score < 1 or score > 5:
                    raise ValidationError(f"{field}必须是1-5之间的整数", field)
        
        current_app.logger.info("=== _validate_data 完成 ===")
    
    @property
    def average_score(self):
        """计算平均评分"""
        scores = [
            self.strategy_score,
            self.timing_score,
            self.risk_control_score,
            self.overall_score
        ]
        valid_scores = [score for score in scores if score is not None]
        
        if not valid_scores:
            return None
        
        return sum(valid_scores) / len(valid_scores)
    
    @classmethod
    def get_by_historical_trade(cls, historical_trade_id):
        """根据历史交易ID获取复盘记录"""
        return cls.query.filter_by(historical_trade_id=historical_trade_id).first()
    
    @classmethod
    def get_by_review_type(cls, review_type):
        """根据复盘类型获取记录"""
        return cls.query.filter_by(review_type=review_type).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_high_score_reviews(cls, min_score=4):
        """获取高评分的复盘记录"""
        return cls.query.filter(
            cls.overall_score >= min_score
        ).order_by(cls.overall_score.desc()).all()
    
    def update_scores(self, **scores):
        """更新评分"""
        score_fields = ['strategy_score', 'timing_score', 'risk_control_score', 'overall_score']
        
        for field, value in scores.items():
            if field in score_fields:
                if value is not None and (not isinstance(value, int) or value < 1 or value > 5):
                    raise ValidationError(f"{field}必须是1-5之间的整数", field)
                setattr(self, field, value)
        
        self.save()
    
    def to_dict(self):
        """转换为字典，包含特殊字段处理"""
        result = super().to_dict()
        
        # 添加平均评分
        result['average_score'] = self.average_score
        
        # 添加评分统计
        result['score_summary'] = {
            'strategy_score': self.strategy_score,
            'timing_score': self.timing_score,
            'risk_control_score': self.risk_control_score,
            'overall_score': self.overall_score,
            'average_score': self.average_score
        }
        
        return result
    
    def __repr__(self):
        return f'<TradeReview {self.historical_trade_id} {self.review_type}>'


class ReviewImage(BaseModel):
    """复盘图片模型"""
    
    __tablename__ = 'review_images'
    
    # 关联复盘记录
    trade_review_id = db.Column(db.Integer, db.ForeignKey('trade_reviews.id'), nullable=False, index=True)
    
    # 图片信息
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    # 图片描述
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)
    
    # 表约束
    __table_args__ = (
        db.CheckConstraint("file_size IS NULL OR file_size > 0", name='check_positive_file_size'),
        db.CheckConstraint("display_order >= 0", name='check_non_negative_display_order'),
        db.Index('idx_review_image_trade_review', 'trade_review_id'),
        db.Index('idx_review_image_order', 'trade_review_id', 'display_order'),
    )
    
    def __init__(self, **kwargs):
        """初始化复盘图片"""
        from flask import current_app
        current_app.logger.info(f"=== ReviewImage.__init__ 开始 ===")
        current_app.logger.info(f"初始化参数: {kwargs}")
        
        # 数据验证
        self._validate_data(kwargs)
        
        # 调用父类构造函数
        super().__init__(**kwargs)
        
        current_app.logger.info("=== ReviewImage.__init__ 完成 ===")
    
    def _validate_data(self, data):
        """验证图片数据"""
        from flask import current_app
        current_app.logger.info(f"=== _validate_data 开始 ===")
        
        # 验证复盘记录ID
        if 'trade_review_id' in data:
            if data['trade_review_id'] is None:
                raise ValidationError("复盘记录ID不能为空", "trade_review_id")
        
        # 验证文件名
        if 'filename' in data:
            if not data['filename'] or not data['filename'].strip():
                raise ValidationError("文件名不能为空", "filename")
        
        # 验证原始文件名
        if 'original_filename' in data:
            if not data['original_filename'] or not data['original_filename'].strip():
                raise ValidationError("原始文件名不能为空", "original_filename")
        
        # 验证文件路径
        if 'file_path' in data:
            if not data['file_path'] or not data['file_path'].strip():
                raise ValidationError("文件路径不能为空", "file_path")
        
        # 验证文件大小
        if 'file_size' in data and data['file_size'] is not None:
            if data['file_size'] <= 0:
                raise ValidationError("文件大小必须大于0", "file_size")
        
        # 验证显示顺序
        if 'display_order' in data and data['display_order'] is not None:
            if data['display_order'] < 0:
                raise ValidationError("显示顺序不能为负数", "display_order")
        
        # 验证MIME类型
        if 'mime_type' in data and data['mime_type']:
            valid_mime_types = [
                'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
                'image/bmp', 'image/webp', 'image/svg+xml'
            ]
            if data['mime_type'] not in valid_mime_types:
                raise ValidationError("不支持的图片格式", "mime_type")
        
        current_app.logger.info("=== _validate_data 完成 ===")
    
    @classmethod
    def get_by_review(cls, trade_review_id):
        """根据复盘记录ID获取图片列表"""
        return cls.query.filter_by(trade_review_id=trade_review_id).order_by(cls.display_order.asc()).all()
    
    @classmethod
    def get_by_filename(cls, filename):
        """根据文件名获取图片记录"""
        return cls.query.filter_by(filename=filename).first()
    
    def update_display_order(self, new_order):
        """更新显示顺序"""
        if new_order < 0:
            raise ValidationError("显示顺序不能为负数", "display_order")
        
        self.display_order = new_order
        self.save()
    
    def get_file_extension(self):
        """获取文件扩展名"""
        if self.original_filename:
            return self.original_filename.split('.')[-1].lower() if '.' in self.original_filename else ''
        return ''
    
    def is_valid_image_format(self):
        """检查是否为有效的图片格式"""
        valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
        return self.get_file_extension() in valid_extensions
    
    def to_dict(self):
        """转换为字典，包含特殊字段处理"""
        result = super().to_dict()
        
        # 添加文件信息
        result['file_extension'] = self.get_file_extension()
        result['is_valid_format'] = self.is_valid_image_format()
        
        # 格式化文件大小
        if self.file_size:
            if self.file_size < 1024:
                result['file_size_formatted'] = f"{self.file_size} B"
            elif self.file_size < 1024 * 1024:
                result['file_size_formatted'] = f"{self.file_size / 1024:.1f} KB"
            else:
                result['file_size_formatted'] = f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            result['file_size_formatted'] = "未知"
        
        return result
    
    def __repr__(self):
        return f'<ReviewImage {self.filename} for review {self.trade_review_id}>'


# 设置关系
TradeReview.historical_trade = db.relationship('HistoricalTrade', backref='reviews')
ReviewImage.trade_review = db.relationship('TradeReview', backref='images')