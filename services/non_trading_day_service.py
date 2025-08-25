"""
非交易日服务类
"""
from datetime import date, timedelta
from typing import List, Dict, Optional
from models.non_trading_day import NonTradingDay
from .base_service import BaseService
from error_handlers import ValidationError, DatabaseError


class NonTradingDayService(BaseService):
    """非交易日服务类，提供交易日判断和持仓天数计算功能"""
    
    model = NonTradingDay
    
    @classmethod
    def is_trading_day(cls, check_date) -> bool:
        """判断是否为交易日"""
        try:
            return cls.model.is_trading_day(check_date)
        except Exception as e:
            raise DatabaseError(f"判断交易日失败: {str(e)}")
    
    @classmethod
    def calculate_trading_days(cls, start_date, end_date) -> int:
        """计算两个日期之间的交易日数量"""
        try:
            return cls.model.calculate_trading_days(start_date, end_date)
        except Exception as e:
            raise DatabaseError(f"计算交易日数量失败: {str(e)}")
    
    @classmethod
    def calculate_holding_days(cls, buy_date, sell_date=None) -> int:
        """计算实际持仓交易日数"""
        try:
            if isinstance(buy_date, str):
                buy_date = date.fromisoformat(buy_date)
            
            end_date = sell_date
            if end_date is None:
                end_date = date.today()
            elif isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)
            
            return cls.model.calculate_trading_days(buy_date, end_date)
        except Exception as e:
            raise DatabaseError(f"计算持仓天数失败: {str(e)}")
    
    @classmethod
    def get_non_trading_days_in_range(cls, start_date, end_date) -> List[Dict]:
        """获取指定日期范围内的非交易日"""
        try:
            non_trading_days = cls.model.get_non_trading_days_in_range(start_date, end_date)
            return [day.to_dict() for day in non_trading_days]
        except Exception as e:
            raise DatabaseError(f"获取非交易日列表失败: {str(e)}")
    
    @classmethod
    def add_holiday(cls, holiday_date, name, description=None) -> Dict:
        """添加节假日"""
        try:
            # 验证日期格式
            if isinstance(holiday_date, str):
                holiday_date = date.fromisoformat(holiday_date)
            
            # 检查是否已存在
            existing = cls.model.query.filter_by(date=holiday_date).first()
            if existing:
                raise ValidationError(f"日期 {holiday_date} 已存在非交易日配置")
            
            # 创建新的非交易日记录
            data = {
                'date': holiday_date,
                'name': name,
                'type': 'holiday',
                'description': description
            }
            
            holiday = cls.create(data)
            return holiday.to_dict()
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseError(f"添加节假日失败: {str(e)}")
    
    @classmethod
    def remove_holiday(cls, holiday_date) -> bool:
        """移除节假日"""
        try:
            if isinstance(holiday_date, str):
                holiday_date = date.fromisoformat(holiday_date)
            
            holiday = cls.model.query.filter_by(date=holiday_date).first()
            if not holiday:
                raise ValidationError(f"日期 {holiday_date} 不存在非交易日配置")
            
            return holiday.delete()
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseError(f"移除节假日失败: {str(e)}")
    
    @classmethod
    def get_holidays_by_year(cls, year: int) -> List[Dict]:
        """获取指定年份的所有节假日"""
        try:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            
            holidays = cls.model.query.filter(
                cls.model.date >= start_date,
                cls.model.date <= end_date,
                cls.model.type == 'holiday'
            ).order_by(cls.model.date).all()
            
            return [holiday.to_dict() for holiday in holidays]
        except Exception as e:
            raise DatabaseError(f"获取年度节假日失败: {str(e)}")
    
    @classmethod
    def get_next_trading_day(cls, check_date) -> Optional[str]:
        """获取指定日期之后的下一个交易日"""
        try:
            next_day = cls.model.get_next_trading_day(check_date)
            return next_day.isoformat() if next_day else None
        except Exception as e:
            raise DatabaseError(f"获取下一个交易日失败: {str(e)}")
    
    @classmethod
    def get_previous_trading_day(cls, check_date) -> Optional[str]:
        """获取指定日期之前的上一个交易日"""
        try:
            prev_day = cls.model.get_previous_trading_day(check_date)
            return prev_day.isoformat() if prev_day else None
        except Exception as e:
            raise DatabaseError(f"获取上一个交易日失败: {str(e)}")
    
    @classmethod
    def bulk_add_holidays(cls, holidays_data: List[Dict]) -> List[Dict]:
        """批量添加节假日"""
        try:
            added_holidays = []
            for holiday_data in holidays_data:
                try:
                    holiday = cls.add_holiday(
                        holiday_data.get('date'),
                        holiday_data.get('name'),
                        holiday_data.get('description')
                    )
                    added_holidays.append(holiday)
                except ValidationError:
                    # 跳过已存在的日期
                    continue
            
            return added_holidays
        except Exception as e:
            raise DatabaseError(f"批量添加节假日失败: {str(e)}")
    
    @classmethod
    def get_trading_calendar(cls, year: int) -> Dict:
        """获取指定年份的交易日历"""
        try:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            
            # 获取所有非交易日
            non_trading_days = cls.get_non_trading_days_in_range(start_date, end_date)
            
            # 计算总交易日数
            total_trading_days = cls.calculate_trading_days(start_date, end_date)
            
            # 按月份统计交易日
            monthly_trading_days = {}
            for month in range(1, 13):
                month_start = date(year, month, 1)
                # 获取月末日期
                if month == 12:
                    month_end = date(year, 12, 31)
                else:
                    month_end = date(year, month + 1, 1) - timedelta(days=1)
                
                monthly_trading_days[month] = cls.calculate_trading_days(month_start, month_end)
            
            return {
                'year': year,
                'total_trading_days': total_trading_days,
                'monthly_trading_days': monthly_trading_days,
                'non_trading_days': non_trading_days,
                'total_non_trading_days': len(non_trading_days)
            }
        except Exception as e:
            raise DatabaseError(f"获取交易日历失败: {str(e)}")