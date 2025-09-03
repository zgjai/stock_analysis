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
    
    # 浮盈计算相关字段
    current_price = db.Column(db.Numeric(10, 2))  # 当前价格
    floating_profit_ratio = db.Column(db.Numeric(5, 4))  # 浮盈比例
    buy_price = db.Column(db.Numeric(10, 2))  # 成本价（冗余存储，便于计算）
    
    # 表约束
    __table_args__ = (
        db.CheckConstraint("price_up_score IN (0, 1)", name='check_price_up_score'),
        db.CheckConstraint("bbi_score IN (0, 1)", name='check_bbi_score'),
        db.CheckConstraint("volume_score IN (0, 1)", name='check_volume_score'),
        db.CheckConstraint("trend_score IN (0, 1)", name='check_trend_score'),
        db.CheckConstraint("j_score IN (0, 1)", name='check_j_score'),
        db.CheckConstraint("total_score BETWEEN 0 AND 5", name='check_total_score'),
        db.CheckConstraint("decision IN ('hold', 'sell_all', 'sell_partial')", name='check_decision'),
        db.CheckConstraint("current_price >= 0", name='check_current_price_positive'),
        db.CheckConstraint("buy_price >= 0", name='check_buy_price_positive'),
        db.UniqueConstraint('stock_code', 'review_date', name='unique_stock_review_date'),
        db.Index('idx_review_stock_date', 'stock_code', 'review_date'),
        db.Index('idx_review_current_price', 'current_price'),
        db.Index('idx_review_floating_profit', 'floating_profit_ratio'),
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
                if holding_days <= 0:
                    raise ValidationError("持仓天数必须是正整数", "holding_days")
                data['holding_days'] = holding_days
            except (ValueError, TypeError):
                raise ValidationError("持仓天数必须是正整数", "holding_days")
        
        # 验证当前价格
        if 'current_price' in data and data['current_price'] is not None:
            try:
                current_price = float(data['current_price'])
                if current_price < 0:
                    raise ValidationError("当前价格不能为负数", "current_price")
                data['current_price'] = current_price
            except (ValueError, TypeError):
                raise ValidationError("当前价格必须是数字", "current_price")
        
        # 验证买入价格
        if 'buy_price' in data and data['buy_price'] is not None:
            try:
                buy_price = float(data['buy_price'])
                if buy_price < 0:
                    raise ValidationError("买入价格不能为负数", "buy_price")
                data['buy_price'] = buy_price
            except (ValueError, TypeError):
                raise ValidationError("买入价格必须是数字", "buy_price")
        
        # 验证浮盈比例
        if 'floating_profit_ratio' in data and data['floating_profit_ratio'] is not None:
            try:
                floating_profit_ratio = float(data['floating_profit_ratio'])
                # 浮盈比例可以为负数（亏损）
                data['floating_profit_ratio'] = floating_profit_ratio
            except (ValueError, TypeError):
                raise ValidationError("浮盈比例必须是数字", "floating_profit_ratio")
    
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
    
    def calculate_floating_profit(self, current_price):
        """计算浮盈比例"""
        if not self.buy_price or not current_price:
            return None
        
        try:
            buy_price_float = float(self.buy_price)
            current_price_float = float(current_price)
            
            if buy_price_float <= 0:
                return None
            
            profit_ratio = (current_price_float - buy_price_float) / buy_price_float
            self.current_price = current_price_float
            self.floating_profit_ratio = profit_ratio
            return profit_ratio
        except (ValueError, TypeError, ZeroDivisionError):
            return None
    
    def update_floating_profit(self, current_price, buy_price=None):
        """更新浮盈相关数据"""
        if buy_price is not None:
            self.buy_price = buy_price
        
        return self.calculate_floating_profit(current_price)
    
    def get_floating_profit_display(self):
        """获取格式化的浮盈显示"""
        if self.floating_profit_ratio is None:
            return {
                'ratio': None,
                'display': '无法计算',
                'color': 'text-muted'
            }
        
        ratio = float(self.floating_profit_ratio)
        percentage = ratio * 100
        
        if ratio > 0:
            return {
                'ratio': ratio,
                'display': f'+{percentage:.2f}%',
                'color': 'text-danger'
            }
        elif ratio < 0:
            return {
                'ratio': ratio,
                'display': f'{percentage:.2f}%',
                'color': 'text-success'
            }
        else:
            return {
                'ratio': ratio,
                'display': '0.00%',
                'color': 'text-muted'
            }
    
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
    
    @classmethod
    def get_buy_price_from_trades(cls, stock_code):
        """从交易记录中获取买入价格"""
        from models.trade_record import TradeRecord
        
        # 获取该股票的最新买入记录
        buy_record = TradeRecord.query.filter_by(
            stock_code=stock_code,
            trade_type='buy'
        ).order_by(TradeRecord.trade_date.desc()).first()
        
        if buy_record:
            return float(buy_record.price)
        return None
    
    def to_dict(self):
        """转换为字典，包含特殊字段处理"""
        result = super().to_dict()
        # 转换date类型为字符串
        if result.get('review_date') is not None:
            if hasattr(self.review_date, 'isoformat'):
                result['review_date'] = self.review_date.isoformat()
        
        # 转换Decimal类型为float
        for field in ['current_price', 'floating_profit_ratio', 'buy_price']:
            if result.get(field) is not None:
                result[field] = float(result[field])
        
        # 添加格式化的浮盈显示
        result['floating_profit_display'] = self.get_floating_profit_display()
        
        return result
    
    def __repr__(self):
        return f'<ReviewRecord {self.stock_code} {self.review_date} {self.total_score}/5>'