"""
交易记录数据模型
"""
from datetime import datetime
from extensions import db
from models.base import BaseModel
from utils.validators import validate_stock_code, validate_price, validate_quantity, validate_trade_type, validate_ratio
from error_handlers import ValidationError


class TradeRecord(BaseModel):
    """交易记录模型"""
    
    __tablename__ = 'trade_records'
    
    # 基本交易信息
    stock_code = db.Column(db.String(10), nullable=False, index=True)
    stock_name = db.Column(db.String(50), nullable=False)
    trade_type = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    trade_date = db.Column(db.DateTime, nullable=False, index=True)
    reason = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)
    
    # 止损止盈设置 (仅买入记录需要)
    stop_loss_price = db.Column(db.Numeric(10, 2))
    take_profit_ratio = db.Column(db.Numeric(5, 4))  # 支持到万分位精度
    sell_ratio = db.Column(db.Numeric(5, 4))         # 支持到万分位精度
    
    # 自动计算字段
    expected_loss_ratio = db.Column(db.Numeric(5, 4))
    expected_profit_ratio = db.Column(db.Numeric(5, 4))
    
    # 分批止盈相关字段
    use_batch_profit_taking = db.Column(db.Boolean, default=False)
    
    # 订正相关字段
    is_corrected = db.Column(db.Boolean, default=False)
    original_record_id = db.Column(db.Integer, db.ForeignKey('trade_records.id'))
    correction_reason = db.Column(db.Text)
    
    # 关系定义
    original_record = db.relationship('TradeRecord', remote_side='TradeRecord.id', backref='corrections')
    
    # 表约束
    __table_args__ = (
        db.CheckConstraint("trade_type IN ('buy', 'sell')", name='check_trade_type'),
        db.Index('idx_stock_date', 'stock_code', 'trade_date'),
    )
    
    def __init__(self, **kwargs):
        from flask import current_app
        current_app.logger.info(f"=== TradeRecord.__init__ 开始 ===")
        current_app.logger.info(f"初始化参数: {kwargs}")
        
        # 数据验证
        current_app.logger.info("开始数据验证")
        self._validate_data(kwargs)
        current_app.logger.info("数据验证通过")
        
        current_app.logger.info("调用父类构造函数")
        super().__init__(**kwargs)
        current_app.logger.info("父类构造函数完成")
        
        # 如果是买入记录，自动计算止损止盈比例
        if self.trade_type == 'buy' and self.price:
            current_app.logger.info("开始计算风险收益比")
            self._calculate_risk_reward()
            current_app.logger.info("风险收益比计算完成")
        
        current_app.logger.info("=== TradeRecord.__init__ 完成 ===")
    
    def _validate_data(self, data):
        """验证交易记录数据"""
        from flask import current_app
        current_app.logger.info(f"=== _validate_data 开始 ===")
        current_app.logger.info(f"验证数据: {data}")
        
        if 'stock_code' in data:
            current_app.logger.info(f"验证股票代码: {data['stock_code']}")
            validate_stock_code(data['stock_code'])
        
        if 'price' in data:
            current_app.logger.info(f"验证价格: {data['price']}")
            data['price'] = validate_price(data['price'])
            current_app.logger.info(f"价格验证后: {data['price']}")
        
        if 'quantity' in data:
            stock_code = data.get('stock_code')
            current_app.logger.info(f"验证数量: {data['quantity']}, 股票代码: {stock_code}")
            data['quantity'] = validate_quantity(data['quantity'], stock_code)
            current_app.logger.info(f"数量验证后: {data['quantity']}")
        
        if 'trade_type' in data:
            current_app.logger.info(f"验证交易类型: {data['trade_type']}")
            validate_trade_type(data['trade_type'])
        
        if 'take_profit_ratio' in data and data['take_profit_ratio'] is not None:
            current_app.logger.info(f"验证止盈比例: {data['take_profit_ratio']}")
            data['take_profit_ratio'] = validate_ratio(data['take_profit_ratio'], 'take_profit_ratio')
            current_app.logger.info(f"止盈比例验证后: {data['take_profit_ratio']}")
        
        if 'sell_ratio' in data and data['sell_ratio'] is not None:
            current_app.logger.info(f"验证卖出比例: {data['sell_ratio']}")
            data['sell_ratio'] = validate_ratio(data['sell_ratio'], 'sell_ratio')
            current_app.logger.info(f"卖出比例验证后: {data['sell_ratio']}")
        
        # 验证止损价格
        if 'stop_loss_price' in data and data['stop_loss_price'] is not None:
            current_app.logger.info(f"验证止损价格: {data['stop_loss_price']}")
            # 先验证并转换止损价格为数值类型
            data['stop_loss_price'] = validate_price(data['stop_loss_price'])
            current_app.logger.info(f"止损价格验证后: {data['stop_loss_price']}")
            
            # 然后进行价格比较
            if 'price' in data and data['stop_loss_price'] >= data['price']:
                current_app.logger.error(f"止损价格 {data['stop_loss_price']} >= 买入价格 {data['price']}")
                raise ValidationError("止损价格必须小于买入价格", "stop_loss_price")
        
        # 验证交易日期
        if 'trade_date' in data and data['trade_date'] is None:
            current_app.logger.error("交易日期为None")
            raise ValidationError("交易日期不能为空", "trade_date")
        
        # 验证原因
        if 'reason' in data and not data['reason']:
            current_app.logger.error(f"交易原因为空: {data['reason']}")
            raise ValidationError("交易原因不能为空", "reason")
        
        current_app.logger.info("=== _validate_data 完成 ===")
    
    def _calculate_risk_reward(self):
        """计算风险收益比"""
        if self.stop_loss_price and self.price:
            price_float = float(self.price)
            stop_loss_float = float(self.stop_loss_price)
            self.expected_loss_ratio = (price_float - stop_loss_float) / price_float
        
        if self.use_batch_profit_taking:
            # 使用分批止盈时，从止盈目标计算总预期收益
            self.expected_profit_ratio = self.calculate_total_expected_profit()
        elif self.take_profit_ratio and self.sell_ratio:
            # 传统单一止盈计算
            take_profit_float = float(self.take_profit_ratio)
            sell_ratio_float = float(self.sell_ratio)
            self.expected_profit_ratio = take_profit_float * sell_ratio_float
    
    @classmethod
    def get_by_stock_code(cls, stock_code):
        """根据股票代码获取交易记录"""
        return cls.query.filter_by(stock_code=stock_code).all()
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        """根据日期范围获取交易记录"""
        return cls.query.filter(
            cls.trade_date >= start_date,
            cls.trade_date <= end_date
        ).order_by(cls.trade_date.desc()).all()
    
    @classmethod
    def get_uncorrected_records(cls):
        """获取未被订正的记录"""
        return cls.query.filter_by(is_corrected=False).all()
    
    def calculate_total_expected_profit(self):
        """计算所有止盈目标的总预期收益率"""
        if not self.use_batch_profit_taking:
            return float(self.expected_profit_ratio or 0)
        
        if not hasattr(self, 'profit_targets') or not self.profit_targets:
            return 0.0
        
        total_expected_profit = 0.0
        for target in self.profit_targets:
            # 确保每个目标都有计算过的预期收益率
            if not target.expected_profit_ratio and target.profit_ratio and target.sell_ratio:
                target._calculate_expected_profit()
            
            if target.expected_profit_ratio:
                total_expected_profit += float(target.expected_profit_ratio)
        
        return total_expected_profit
    
    def validate_profit_targets(self):
        """验证止盈目标设置的合理性"""
        if not self.use_batch_profit_taking:
            return True
        
        if not hasattr(self, 'profit_targets') or not self.profit_targets:
            raise ValidationError("使用分批止盈时必须设置至少一个止盈目标", "profit_targets")
        
        # 验证每个止盈目标
        total_sell_ratio = 0
        for target in self.profit_targets:
            target.validate_against_buy_price(self.price)
            total_sell_ratio += float(target.sell_ratio)
        
        # 验证总卖出比例
        if total_sell_ratio > 1.0:
            raise ValidationError("所有止盈目标的卖出比例总和不能超过100%", "total_sell_ratio")
        
        return True
    
    def to_dict(self):
        """转换为字典，包含特殊字段处理"""
        result = super().to_dict()
        # 转换Decimal类型为float
        for field in ['price', 'stop_loss_price', 'take_profit_ratio', 'sell_ratio', 
                     'expected_loss_ratio', 'expected_profit_ratio']:
            if result.get(field) is not None:
                result[field] = float(result[field])
        
        # 确保 use_batch_profit_taking 字段有默认值
        if result.get('use_batch_profit_taking') is None:
            result['use_batch_profit_taking'] = False
        
        # 如果使用分批止盈，包含止盈目标数据
        if self.use_batch_profit_taking and hasattr(self, 'profit_targets'):
            result['profit_targets'] = [target.to_dict() for target in self.profit_targets]
            result['total_expected_profit_ratio'] = float(self.calculate_total_expected_profit())
            result['total_sell_ratio'] = sum(float(target.sell_ratio) for target in self.profit_targets)
        else:
            # 为单一止盈模式确保传统字段存在
            result.setdefault('take_profit_ratio', None)
            result.setdefault('sell_ratio', None)
            result.setdefault('expected_profit_ratio', None)
        
        return result
    
    def __repr__(self):
        return f'<TradeRecord {self.stock_code} {self.trade_type} {self.price}>'


class TradeCorrection(BaseModel):
    """交易记录订正表"""
    
    __tablename__ = 'trade_corrections'
    
    original_trade_id = db.Column(db.Integer, db.ForeignKey('trade_records.id'), nullable=False)
    corrected_trade_id = db.Column(db.Integer, db.ForeignKey('trade_records.id'), nullable=False)
    correction_reason = db.Column(db.Text, nullable=False)
    corrected_fields = db.Column(db.Text, nullable=False)  # JSON格式记录修改的字段
    created_by = db.Column(db.String(50), default='user')
    
    # 关系定义
    original_trade = db.relationship('TradeRecord', foreign_keys=[original_trade_id])
    corrected_trade = db.relationship('TradeRecord', foreign_keys=[corrected_trade_id])
    
    # 索引
    __table_args__ = (
        db.Index('idx_corrections_original', 'original_trade_id'),
        db.Index('idx_corrections_corrected', 'corrected_trade_id'),
    )
    
    def __repr__(self):
        return f'<TradeCorrection {self.original_trade_id} -> {self.corrected_trade_id}>'