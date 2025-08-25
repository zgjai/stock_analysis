"""
分批止盈目标数据模型
"""
from extensions import db
from models.base import BaseModel
from utils.validators import validate_price, validate_ratio
from error_handlers import ValidationError


class ProfitTakingTarget(BaseModel):
    """分批止盈目标模型"""
    
    __tablename__ = 'profit_taking_targets'
    
    # 关联字段
    trade_record_id = db.Column(db.Integer, db.ForeignKey('trade_records.id'), nullable=False)
    
    # 止盈目标字段
    target_price = db.Column(db.Numeric(10, 2))  # 止盈价格
    profit_ratio = db.Column(db.Numeric(5, 4))   # 止盈比例 (支持到万分位精度)
    sell_ratio = db.Column(db.Numeric(5, 4), nullable=False)  # 卖出比例 (支持到万分位精度)
    expected_profit_ratio = db.Column(db.Numeric(5, 4))  # 预期收益率
    sequence_order = db.Column(db.Integer, nullable=False, default=1)  # 序列顺序
    
    # 关系定义
    trade_record = db.relationship('TradeRecord', backref=db.backref('profit_targets', cascade='all, delete-orphan'))
    
    # 表约束
    __table_args__ = (
        db.CheckConstraint("sell_ratio > 0 AND sell_ratio <= 10", name='check_sell_ratio_range'),  # 允许大于100%的卖出比例
        db.CheckConstraint("profit_ratio >= 0 AND profit_ratio <= 10", name='check_profit_ratio_range'),  # 允许大于10%的止盈比例
        db.CheckConstraint("sequence_order > 0", name='check_sequence_order_positive'),
        db.Index('idx_profit_targets_trade', 'trade_record_id'),
        db.Index('idx_profit_targets_sequence', 'trade_record_id', 'sequence_order'),
    )
    
    def __init__(self, **kwargs):
        # 数据验证
        self._validate_data(kwargs)
        super().__init__(**kwargs)
        # 自动计算预期收益率
        if self.profit_ratio and self.sell_ratio:
            self._calculate_expected_profit()
    
    def _validate_data(self, data):
        """验证止盈目标数据"""
        validation_errors = {}
        
        # 验证止盈价格
        if 'target_price' in data and data['target_price'] is not None:
            try:
                data['target_price'] = validate_price(data['target_price'])
            except ValidationError as e:
                validation_errors['target_price'] = e.message
        
        # 验证止盈比例 - 支持大于10%的止盈比例
        if 'profit_ratio' in data and data['profit_ratio'] is not None:
            try:
                profit_ratio = float(data['profit_ratio'])
                if profit_ratio < 0:
                    validation_errors['profit_ratio'] = "止盈比例不能为负数"
                elif profit_ratio > 10:  # 允许大于10%的止盈比例，最大1000%
                    validation_errors['profit_ratio'] = "止盈比例不能超过1000%"
                else:
                    data['profit_ratio'] = profit_ratio
            except (ValueError, TypeError):
                validation_errors['profit_ratio'] = "止盈比例格式无效"
        
        # 验证卖出比例 - 支持大于100%的卖出比例
        if 'sell_ratio' in data and data['sell_ratio'] is not None:
            try:
                sell_ratio = float(data['sell_ratio'])
                if sell_ratio <= 0:
                    validation_errors['sell_ratio'] = "卖出比例必须大于0"
                elif sell_ratio > 10:  # 允许大于100%的卖出比例，最大1000%
                    validation_errors['sell_ratio'] = "卖出比例不能超过1000%"
                else:
                    data['sell_ratio'] = sell_ratio
            except (ValueError, TypeError):
                validation_errors['sell_ratio'] = "卖出比例格式无效"
        else:
            validation_errors['sell_ratio'] = "卖出比例不能为空"
        
        # 验证序列顺序
        if 'sequence_order' in data and data['sequence_order'] is not None:
            try:
                sequence_order = int(data['sequence_order'])
                if sequence_order <= 0:
                    validation_errors['sequence_order'] = "序列顺序必须是正整数"
                else:
                    data['sequence_order'] = sequence_order
            except (ValueError, TypeError):
                validation_errors['sequence_order'] = "序列顺序必须是正整数"
        
        # 如果有验证错误，抛出详细的错误信息
        if validation_errors:
            error = ValidationError("止盈目标数据验证失败", "profit_taking_target")
            error.details = validation_errors
            raise error
    
    def _calculate_expected_profit(self):
        """计算预期收益率"""
        if self.profit_ratio and self.sell_ratio:
            profit_float = float(self.profit_ratio)
            sell_float = float(self.sell_ratio)
            self.expected_profit_ratio = profit_float * sell_float
    
    def validate_against_buy_price(self, buy_price):
        """验证止盈目标相对于买入价格的合理性"""
        if not buy_price:
            raise ValidationError("买入价格不能为空", "buy_price")
        
        buy_price_float = float(buy_price)
        validation_errors = {}
        
        # 验证止盈价格必须大于买入价格
        if self.target_price:
            target_price_float = float(self.target_price)
            if target_price_float <= buy_price_float:
                validation_errors['target_price'] = f"止盈价格({target_price_float})必须大于买入价格({buy_price_float})"
            elif target_price_float > buy_price_float * 10:  # 防止设置过高的止盈价格
                validation_errors['target_price'] = "止盈价格不应超过买入价格的10倍"
        
        # 验证止盈比例的合理性 - 允许大于10%的止盈比例
        if self.profit_ratio:
            profit_ratio_float = float(self.profit_ratio)
            if profit_ratio_float < 0:
                validation_errors['profit_ratio'] = "止盈比例不能为负数"
            elif profit_ratio_float > 10:  # 允许最大1000%
                validation_errors['profit_ratio'] = "止盈比例不应超过1000%"
        
        # 如果同时有止盈价格和止盈比例，验证一致性
        if self.target_price and self.profit_ratio:
            target_price_float = float(self.target_price)
            profit_ratio_float = float(self.profit_ratio)
            
            # 根据价格计算的比例
            calculated_ratio = (target_price_float - buy_price_float) / buy_price_float
            
            # 允许5%的误差范围
            if abs(calculated_ratio - profit_ratio_float) > 0.05:
                validation_errors['consistency'] = "止盈价格和止盈比例不一致"
        
        # 如果有验证错误，抛出详细的错误信息
        if validation_errors:
            error = ValidationError("止盈目标与买入价格验证失败", "profit_target_buy_price")
            error.details = validation_errors
            raise error
        
        # 如果有止盈价格但没有止盈比例，自动计算止盈比例
        if self.target_price and not self.profit_ratio:
            target_price_float = float(self.target_price)
            self.profit_ratio = (target_price_float - buy_price_float) / buy_price_float
            self._calculate_expected_profit()
        
        return True
    
    def update_profit_ratio_from_price(self, buy_price):
        """根据买入价格和止盈价格更新止盈比例"""
        if not self.target_price or not buy_price:
            return
        
        buy_price_float = float(buy_price)
        target_price_float = float(self.target_price)
        
        if target_price_float > buy_price_float:
            self.profit_ratio = (target_price_float - buy_price_float) / buy_price_float
            self._calculate_expected_profit()
    
    def update_target_price_from_ratio(self, buy_price):
        """根据买入价格和止盈比例更新止盈价格"""
        if not self.profit_ratio or not buy_price:
            return
        
        buy_price_float = float(buy_price)
        profit_ratio_float = float(self.profit_ratio)
        
        if profit_ratio_float > 0:
            self.target_price = buy_price_float * (1 + profit_ratio_float)
            self._calculate_expected_profit()
    
    @classmethod
    def get_by_trade_record(cls, trade_record_id):
        """根据交易记录ID获取所有止盈目标"""
        return cls.query.filter_by(trade_record_id=trade_record_id).order_by(cls.sequence_order).all()
    
    @classmethod
    def delete_by_trade_record(cls, trade_record_id):
        """删除指定交易记录的所有止盈目标"""
        try:
            cls.query.filter_by(trade_record_id=trade_record_id).delete()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def to_dict(self):
        """转换为字典，包含特殊字段处理"""
        result = super().to_dict()
        # 转换Decimal类型为float
        for field in ['target_price', 'profit_ratio', 'sell_ratio', 'expected_profit_ratio']:
            if result.get(field) is not None:
                result[field] = float(result[field])
        
        return result
    
    def __repr__(self):
        return f'<ProfitTakingTarget {self.trade_record_id} #{self.sequence_order} {self.target_price}>'