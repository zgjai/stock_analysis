"""
历史交易记录数据模型
"""
import json
from datetime import datetime
from decimal import Decimal
from extensions import db
from models.base import BaseModel
from utils.validators import validate_stock_code, validate_price
from error_handlers import ValidationError


class HistoricalTrade(BaseModel):
    """历史交易记录模型 - 存储已完成的完整交易"""
    
    __tablename__ = 'historical_trades'
    
    # 基本信息
    stock_code = db.Column(db.String(10), nullable=False, index=True)
    stock_name = db.Column(db.String(50), nullable=False)
    
    # 交易周期信息
    buy_date = db.Column(db.DateTime, nullable=False, index=True)
    sell_date = db.Column(db.DateTime, nullable=False, index=True)
    holding_days = db.Column(db.Integer, nullable=False)
    
    # 财务数据
    total_investment = db.Column(db.Numeric(12, 2), nullable=False)  # 总投入本金
    total_return = db.Column(db.Numeric(12, 2), nullable=False)      # 总实际收益
    return_rate = db.Column(db.Numeric(8, 4), nullable=False)        # 实际收益率
    
    # 交易记录关联
    buy_records_ids = db.Column(db.Text)   # JSON格式存储买入记录ID列表
    sell_records_ids = db.Column(db.Text)  # JSON格式存储卖出记录ID列表
    
    # 状态标识
    is_completed = db.Column(db.Boolean, default=True, nullable=False)
    completion_date = db.Column(db.DateTime, nullable=False)
    
    # 表约束和索引
    __table_args__ = (
        db.CheckConstraint("total_investment > 0", name='check_positive_investment'),
        db.CheckConstraint("holding_days >= 0", name='check_non_negative_holding_days'),
        db.CheckConstraint("sell_date >= buy_date", name='check_date_order'),
        db.Index('idx_historical_stock_date', 'stock_code', 'buy_date'),
        db.Index('idx_historical_completion', 'completion_date', 'is_completed'),
        db.Index('idx_historical_return_rate', 'return_rate'),
    )
    
    def __init__(self, **kwargs):
        """初始化历史交易记录"""
        from flask import current_app
        current_app.logger.info(f"=== HistoricalTrade.__init__ 开始 ===")
        current_app.logger.info(f"初始化参数: {kwargs}")
        
        # 数据验证
        self._validate_data(kwargs)
        
        # 调用父类构造函数
        super().__init__(**kwargs)
        
        current_app.logger.info("=== HistoricalTrade.__init__ 完成 ===")
    
    def _validate_data(self, data):
        """验证历史交易数据"""
        from flask import current_app
        current_app.logger.info(f"=== _validate_data 开始 ===")
        
        # 验证股票代码
        if 'stock_code' in data:
            validate_stock_code(data['stock_code'])
        
        # 验证投入本金
        if 'total_investment' in data:
            if data['total_investment'] is None or float(data['total_investment']) <= 0:
                raise ValidationError("总投入本金必须大于0", "total_investment")
        
        # 验证持仓天数
        if 'holding_days' in data:
            if data['holding_days'] is None or data['holding_days'] < 0:
                raise ValidationError("持仓天数不能为负数", "holding_days")
        
        # 验证日期顺序
        if 'buy_date' in data and 'sell_date' in data:
            if data['buy_date'] and data['sell_date'] and data['sell_date'] < data['buy_date']:
                raise ValidationError("卖出日期不能早于买入日期", "sell_date")
        
        # 验证记录ID列表格式
        for field in ['buy_records_ids', 'sell_records_ids']:
            if field in data and data[field] is not None:
                try:
                    if isinstance(data[field], str):
                        json.loads(data[field])
                    elif isinstance(data[field], list):
                        data[field] = json.dumps(data[field])
                except (json.JSONDecodeError, TypeError):
                    raise ValidationError(f"{field}必须是有效的JSON格式", field)
        
        current_app.logger.info("=== _validate_data 完成 ===")
    
    @property
    def buy_records_list(self):
        """获取买入记录ID列表"""
        if not self.buy_records_ids:
            return []
        try:
            return json.loads(self.buy_records_ids)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @buy_records_list.setter
    def buy_records_list(self, value):
        """设置买入记录ID列表"""
        if value is None:
            self.buy_records_ids = None
        else:
            self.buy_records_ids = json.dumps(value)
    
    @property
    def sell_records_list(self):
        """获取卖出记录ID列表"""
        if not self.sell_records_ids:
            return []
        try:
            return json.loads(self.sell_records_ids)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @sell_records_list.setter
    def sell_records_list(self, value):
        """设置卖出记录ID列表"""
        if value is None:
            self.sell_records_ids = None
        else:
            self.sell_records_ids = json.dumps(value)
    
    @classmethod
    def get_by_stock_code(cls, stock_code):
        """根据股票代码获取历史交易记录"""
        return cls.query.filter_by(stock_code=stock_code).order_by(cls.completion_date.desc()).all()
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        """根据完成日期范围获取历史交易记录"""
        return cls.query.filter(
            cls.completion_date >= start_date,
            cls.completion_date <= end_date
        ).order_by(cls.completion_date.desc()).all()
    
    @classmethod
    def get_completed_trades(cls):
        """获取所有已完成的交易记录"""
        return cls.query.filter_by(is_completed=True).order_by(cls.completion_date.desc()).all()
    
    @classmethod
    def get_profitable_trades(cls):
        """获取盈利的交易记录"""
        return cls.query.filter(cls.total_return > 0).order_by(cls.return_rate.desc()).all()
    
    @classmethod
    def get_loss_trades(cls):
        """获取亏损的交易记录"""
        return cls.query.filter(cls.total_return < 0).order_by(cls.return_rate.asc()).all()
    
    def calculate_metrics(self):
        """计算交易指标"""
        metrics = {
            'total_investment': float(self.total_investment) if self.total_investment else 0,
            'total_return': float(self.total_return) if self.total_return else 0,
            'return_rate': float(self.return_rate) if self.return_rate else 0,
            'holding_days': self.holding_days,
            'is_profitable': self.total_return > 0 if self.total_return else False,
            'daily_return_rate': float(self.return_rate) / self.holding_days if self.holding_days > 0 and self.return_rate else 0
        }
        return metrics
    
    def to_dict(self):
        """转换为字典，包含特殊字段处理"""
        result = super().to_dict()
        
        # 转换Decimal类型为float
        for field in ['total_investment', 'total_return', 'return_rate']:
            if result.get(field) is not None:
                result[field] = float(result[field])
        
        # 添加记录ID列表
        result['buy_records_list'] = self.buy_records_list
        result['sell_records_list'] = self.sell_records_list
        
        # 添加计算指标
        result['metrics'] = self.calculate_metrics()
        
        return result
    
    def __repr__(self):
        return f'<HistoricalTrade {self.stock_code} {self.buy_date.strftime("%Y-%m-%d")} -> {self.sell_date.strftime("%Y-%m-%d")}>'