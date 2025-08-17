"""
股票池数据模型
"""
from extensions import db
from models.base import BaseModel
from utils.validators import validate_stock_code, validate_price
from error_handlers import ValidationError


class StockPool(BaseModel):
    """股票池模型"""
    
    __tablename__ = 'stock_pool'
    
    stock_code = db.Column(db.String(10), nullable=False, index=True)
    stock_name = db.Column(db.String(50), nullable=False)
    pool_type = db.Column(db.String(20), nullable=False)  # 'watch' or 'buy_ready'
    target_price = db.Column(db.Numeric(10, 2))
    add_reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # 'active', 'moved', 'removed'
    
    # 表约束
    __table_args__ = (
        db.CheckConstraint("pool_type IN ('watch', 'buy_ready')", name='check_pool_type'),
        db.CheckConstraint("status IN ('active', 'moved', 'removed')", name='check_status'),
        db.Index('idx_stock_pool_type', 'pool_type', 'status'),
        db.Index('idx_stock_code_status', 'stock_code', 'status'),
    )
    
    def __init__(self, **kwargs):
        # 数据验证
        self._validate_data(kwargs)
        super().__init__(**kwargs)
    
    def _validate_data(self, data):
        """验证股票池数据"""
        if 'stock_code' in data:
            validate_stock_code(data['stock_code'])
        
        if 'stock_name' in data and not data['stock_name']:
            raise ValidationError("股票名称不能为空", "stock_name")
        
        if 'pool_type' in data:
            if data['pool_type'] not in ['watch', 'buy_ready']:
                raise ValidationError("池类型必须是watch或buy_ready", "pool_type")
        
        if 'status' in data:
            if data['status'] not in ['active', 'moved', 'removed']:
                raise ValidationError("状态必须是active、moved或removed", "status")
        
        if 'target_price' in data and data['target_price'] is not None:
            data['target_price'] = validate_price(data['target_price'])
    
    @classmethod
    def get_by_pool_type(cls, pool_type, status='active'):
        """根据池类型获取股票"""
        return cls.query.filter_by(pool_type=pool_type, status=status).all()
    
    @classmethod
    def get_watch_pool(cls):
        """获取待观测池"""
        return cls.get_by_pool_type('watch')
    
    @classmethod
    def get_buy_ready_pool(cls):
        """获取待买入池"""
        return cls.get_by_pool_type('buy_ready')
    
    @classmethod
    def get_by_stock_code(cls, stock_code):
        """根据股票代码获取记录（包括历史记录）"""
        return cls.query.filter_by(stock_code=stock_code).order_by(cls.created_at.desc()).all()
    
    def move_to_pool(self, new_pool_type, reason=None):
        """移动到另一个池"""
        # 标记当前记录为已移动
        self.status = 'moved'
        self.save()
        
        # 创建新记录
        new_record = StockPool(
            stock_code=self.stock_code,
            stock_name=self.stock_name,
            pool_type=new_pool_type,
            target_price=self.target_price,
            add_reason=reason or f"从{self.pool_type}池移入",
            status='active'
        )
        return new_record.save()
    
    def remove_from_pool(self, reason=None):
        """从池中移除"""
        self.status = 'removed'
        if reason:
            self.add_reason = f"{self.add_reason} | 移除原因: {reason}"
        return self.save()
    
    def to_dict(self):
        """转换为字典，包含特殊字段处理"""
        result = super().to_dict()
        # 转换Decimal类型为float
        if result.get('target_price') is not None:
            result['target_price'] = float(result['target_price'])
        return result
    
    def __repr__(self):
        return f'<StockPool {self.stock_code} {self.pool_type} {self.status}>'