"""
非交易日数据模型
"""
from datetime import date, timedelta
from sqlalchemy import and_, or_
from extensions import db
from .base import BaseModel


class NonTradingDay(BaseModel):
    """非交易日配置模型"""
    
    __tablename__ = 'non_trading_days'
    
    date = db.Column(db.Date, nullable=False, unique=True, index=True)
    name = db.Column(db.String(100))  # 节假日名称
    type = db.Column(db.String(20), default='holiday')  # holiday, weekend, other
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<NonTradingDay {self.date} - {self.name}>'
    
    @classmethod
    def is_trading_day(cls, check_date):
        """判断是否为交易日"""
        if isinstance(check_date, str):
            check_date = date.fromisoformat(check_date)
        
        # 周六周日自动为非交易日
        if check_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            return False
        
        # 检查是否在配置的非交易日中
        non_trading = cls.query.filter_by(date=check_date).first()
        return non_trading is None
    
    @classmethod
    def calculate_trading_days(cls, start_date, end_date):
        """计算两个日期之间的交易日数量"""
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
            
        if start_date > end_date:
            return 0
            
        current_date = start_date
        trading_days = 0
        
        while current_date <= end_date:
            if cls.is_trading_day(current_date):
                trading_days += 1
            current_date += timedelta(days=1)
        
        return trading_days
    
    @classmethod
    def get_non_trading_days_in_range(cls, start_date, end_date):
        """获取指定日期范围内的非交易日"""
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
            
        return cls.query.filter(
            and_(cls.date >= start_date, cls.date <= end_date)
        ).order_by(cls.date).all()
    
    @classmethod
    def add_weekend_holidays(cls, year):
        """为指定年份添加周末作为非交易日（可选功能）"""
        # 这个方法可以用于批量添加周末，但通常周末在is_trading_day中自动处理
        pass
    
    @classmethod
    def get_next_trading_day(cls, check_date):
        """获取指定日期之后的下一个交易日"""
        if isinstance(check_date, str):
            check_date = date.fromisoformat(check_date)
            
        next_date = check_date + timedelta(days=1)
        max_attempts = 30  # 防止无限循环
        attempts = 0
        
        while not cls.is_trading_day(next_date) and attempts < max_attempts:
            next_date += timedelta(days=1)
            attempts += 1
            
        return next_date if attempts < max_attempts else None
    
    @classmethod
    def get_previous_trading_day(cls, check_date):
        """获取指定日期之前的上一个交易日"""
        if isinstance(check_date, str):
            check_date = date.fromisoformat(check_date)
            
        prev_date = check_date - timedelta(days=1)
        max_attempts = 30  # 防止无限循环
        attempts = 0
        
        while not cls.is_trading_day(prev_date) and attempts < max_attempts:
            prev_date -= timedelta(days=1)
            attempts += 1
            
        return prev_date if attempts < max_attempts else None
    
    def to_dict(self):
        """转换为字典格式"""
        result = super().to_dict()
        # 确保日期格式正确
        if self.date:
            result['date'] = self.date.isoformat()
        return result