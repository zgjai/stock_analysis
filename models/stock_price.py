"""
股票价格数据模型
"""
from datetime import date
from extensions import db
from models.base import BaseModel
from utils.validators import validate_stock_code, validate_price
from error_handlers import ValidationError


class StockPrice(BaseModel):
    """股票价格缓存模型"""
    
    __tablename__ = 'stock_prices'
    
    stock_code = db.Column(db.String(10), nullable=False, index=True)
    stock_name = db.Column(db.String(50))
    current_price = db.Column(db.Numeric(10, 2))
    change_percent = db.Column(db.Numeric(5, 2))
    record_date = db.Column(db.Date, nullable=False, index=True)
    
    # 表约束
    __table_args__ = (
        db.UniqueConstraint('stock_code', 'record_date', name='unique_stock_price_date'),
        db.Index('idx_stock_price_date', 'stock_code', 'record_date'),
    )
    
    def __init__(self, **kwargs):
        # 数据验证
        self._validate_data(kwargs)
        super().__init__(**kwargs)
    
    def _validate_data(self, data):
        """验证股票价格数据"""
        if 'stock_code' in data:
            validate_stock_code(data['stock_code'])
        
        if 'current_price' in data and data['current_price'] is not None:
            data['current_price'] = validate_price(data['current_price'])
        
        if 'change_percent' in data and data['change_percent'] is not None:
            try:
                change_percent = float(data['change_percent'])
                if change_percent < -100 or change_percent > 100:
                    raise ValidationError("涨跌幅必须在-100%到100%之间", "change_percent")
                data['change_percent'] = change_percent
            except (ValueError, TypeError):
                raise ValidationError("涨跌幅格式不正确", "change_percent")
        
        if 'record_date' in data and data['record_date'] is None:
            raise ValidationError("记录日期不能为空", "record_date")
    
    @classmethod
    def get_latest_price(cls, stock_code):
        """获取股票最新价格"""
        return cls.query.filter_by(stock_code=stock_code).order_by(cls.record_date.desc()).first()
    
    @classmethod
    def get_price_by_date(cls, stock_code, target_date):
        """获取指定日期的股票价格"""
        return cls.query.filter_by(stock_code=stock_code, record_date=target_date).first()
    
    @classmethod
    def get_price_history(cls, stock_code, days=30):
        """获取股票价格历史"""
        return cls.query.filter_by(stock_code=stock_code).order_by(
            cls.record_date.desc()
        ).limit(days).all()
    
    @classmethod
    def update_or_create(cls, stock_code, stock_name, current_price, change_percent, record_date=None):
        """更新或创建价格记录"""
        if record_date is None:
            record_date = date.today()
        
        # 查找是否存在记录
        existing = cls.query.filter_by(stock_code=stock_code, record_date=record_date).first()
        
        if existing:
            # 更新现有记录
            existing.stock_name = stock_name
            existing.current_price = current_price
            existing.change_percent = change_percent
            return existing.save()
        else:
            # 创建新记录
            new_price = cls(
                stock_code=stock_code,
                stock_name=stock_name,
                current_price=current_price,
                change_percent=change_percent,
                record_date=record_date
            )
            return new_price.save()
    
    def to_dict(self):
        """转换为字典，包含特殊字段处理"""
        result = super().to_dict()
        # 转换Decimal类型为float
        for field in ['current_price', 'change_percent']:
            if result.get(field) is not None:
                result[field] = float(result[field])
        # 转换日期
        if result.get('record_date'):
            result['record_date'] = result['record_date'].isoformat()
        return result
    
    def __repr__(self):
        return f'<StockPrice {self.stock_code} {self.current_price} {self.record_date}>'