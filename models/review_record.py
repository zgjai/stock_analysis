"""
复盘记录数据模型
"""
from datetime import date
from extensions import db
from models.base import BaseModel
from utils.validators import validate_stock_code
from error_handlers import ValidationError


class ReviewRecord(BaseModel):
    """复盘记录模型"""
    
    __tablename__ = 'review_records'
    
    stock_code = db.Column(db.String(10), nullable=False, index=True)
    review_date = db.Column(db.Date, nullable=False, index=True)
    
    # 5项评分标准 (每项0-1分)
    price_up_score = db.Column(db.Integer, nullable=False, default=0)
    bbi_score = db.Column(db.Integer, nullable=False, default=0)
    volume_score = db.Column(db.Integer, nullable=False, default=0)
    trend_score = db.Column(db.Integer, nullable=False, default=0)
    j_score = db.Column(db.Integer, nullable=False, default=0)
    
    # 总分 (0-5分)
    total_score = db.Column(db.Integer, nullable=False, default=0)
    
    # 分析和决策
    analysis = db.Column(db.Text)
    decision = db.Column(db.String(20))  # 'hold', 'sell_all', 'sell_partial'
    reason = db.Column(db.Text)
    holding_days = db.Column(db.Integer)  # 手动输入的持仓天数
    
    # 表约束
    __table_args__ = (
        db.CheckConstraint("price_up_score IN (0, 1)", name='check_price_up_score'),
        db.CheckConstraint("bbi_score IN (0, 1)", name='check_bbi_score'),
        db.CheckConstraint("volume_score IN (0, 1)", name='check_volume_score'),
        db.CheckConstraint("trend_score IN (0, 1)", name='check_trend_score'),
        db.CheckConstraint("j_score IN (0, 1)", name='check_j_score'),
        db.CheckConstraint("total_score BETWEEN 0 AND 5", name='check_total_score'),
        db.CheckConstraint("decision IN ('hold', 'sell_all', 'sell_partial')", name='check_decision'),
        db.UniqueConstraint('stock_code', 'review_date', name='unique_stock_review_date'),
        db.Index('idx_review_stock_date', 'stock_code', 'review_date'),
    )
    
    def __init__(self, **kwargs):
        # 数据验证
        self._validate_data(kwargs)
        super().__init__(**kwargs)
        self._calculate_total_score()
    
    def _validate_data(self, data):
        """验证复盘记录数据"""
        if 'stock_code' in data:
            validate_stock_code(data['stock_code'])
        
        if 'review_date' in data and data['review_date'] is None:
            raise ValidationError("复盘日期不能为空", "review_date")
        
        # 验证评分值
        score_fields = ['price_up_score', 'bbi_score', 'volume_score', 'trend_score', 'j_score']
        for field in score_fields:
            if field in data and data[field] is not None:
                if data[field] not in [0, 1]:
                    raise ValidationError(f"{field}必须是0或1", field)
        
        # 验证决策类型
        if 'decision' in data and data['decision'] is not None:
            if data['decision'] not in ['hold', 'sell_all', 'sell_partial']:
                raise ValidationError("决策类型必须是hold、sell_all或sell_partial", "decision")
        
        # 验证持仓天数
        if 'holding_days' in data and data['holding_days'] is not None:
            try:
                holding_days = int(data['holding_days'])
                if holding_days < 0:
                    raise ValidationError("持仓天数不能为负数", "holding_days")
                data['holding_days'] = holding_days
            except (ValueError, TypeError):
                raise ValidationError("持仓天数必须是整数", "holding_days")
    
    def _calculate_total_score(self):
        """自动计算总分"""
        self.total_score = (
            (self.price_up_score or 0) +
            (self.bbi_score or 0) +
            (self.volume_score or 0) +
            (self.trend_score or 0) +
            (self.j_score or 0)
        )
    
    def update_scores(self, **scores):
        """更新评分并重新计算总分"""
        for field, value in scores.items():
            if hasattr(self, field) and field.endswith('_score'):
                setattr(self, field, value)
        self._calculate_total_score()
    
    @classmethod
    def get_by_stock_code(cls, stock_code):
        """根据股票代码获取复盘记录"""
        return cls.query.filter_by(stock_code=stock_code).order_by(cls.review_date.desc()).all()
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        """根据日期范围获取复盘记录"""
        return cls.query.filter(
            cls.review_date >= start_date,
            cls.review_date <= end_date
        ).order_by(cls.review_date.desc()).all()
    
    @classmethod
    def get_latest_by_stock(cls, stock_code):
        """获取某股票最新的复盘记录"""
        return cls.query.filter_by(stock_code=stock_code).order_by(cls.review_date.desc()).first()
    
    def to_dict(self):
        """转换为字典，包含特殊字段处理"""
        result = super().to_dict()
        # 转换date类型为字符串
        if result.get('review_date') is not None:
            if hasattr(self.review_date, 'isoformat'):
                result['review_date'] = self.review_date.isoformat()
        return result
    
    def __repr__(self):
        return f'<ReviewRecord {self.stock_code} {self.review_date} {self.total_score}/5>'