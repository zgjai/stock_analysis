#!/usr/bin/env python3
"""
交易日期工具函数
处理交易日、交易时间等逻辑
"""
from datetime import date, datetime, time, timedelta
from typing import Tuple


def get_trading_date() -> date:
    """
    获取当前数据应该归属的交易日期
    
    规则：
    1. 交易日当天8点之前 -> 上一个交易日
    2. 交易日当天8点之后 -> 当天
    3. 周末/节假日 -> 上一个交易日
    
    Returns:
        date: 数据应该归属的交易日期
    """
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()
    
    # 定义8点作为分界线
    cutoff_time = time(8, 0)  # 8:00 AM
    
    # 获取当前是星期几 (0=Monday, 6=Sunday)
    weekday = current_date.weekday()
    
    # 如果是周末，返回上一个交易日
    if weekday == 5:  # Saturday
        return current_date - timedelta(days=1)  # Friday
    elif weekday == 6:  # Sunday
        return current_date - timedelta(days=2)  # Friday
    
    # 如果是工作日但在8点之前，返回上一个交易日
    if current_time < cutoff_time:
        if weekday == 0:  # Monday
            return current_date - timedelta(days=3)  # Previous Friday
        else:
            return current_date - timedelta(days=1)  # Previous day
    
    # 工作日8点之后，返回当天
    return current_date


def get_previous_trading_date(target_date: date) -> date:
    """
    获取指定日期的上一个交易日
    
    Args:
        target_date: 目标日期
        
    Returns:
        date: 上一个交易日
    """
    weekday = target_date.weekday()
    
    if weekday == 0:  # Monday
        return target_date - timedelta(days=3)  # Previous Friday
    elif weekday == 6:  # Sunday
        return target_date - timedelta(days=2)  # Previous Friday
    elif weekday == 5:  # Saturday
        return target_date - timedelta(days=1)  # Previous Friday
    else:
        return target_date - timedelta(days=1)  # Previous day


def is_trading_day(target_date: date) -> bool:
    """
    判断是否为交易日（简单版本，只考虑周末）
    
    Args:
        target_date: 目标日期
        
    Returns:
        bool: 是否为交易日
    """
    weekday = target_date.weekday()
    return weekday < 5  # Monday to Friday


def is_trading_time(current_time: datetime = None) -> bool:
    """
    判断是否在交易时间内
    A股交易时间：9:30-11:30, 13:00-15:00
    
    Args:
        current_time: 当前时间，默认为系统当前时间
        
    Returns:
        bool: 是否在交易时间内
    """
    if current_time is None:
        current_time = datetime.now()
    
    time_only = current_time.time()
    
    # 上午交易时间 9:30-11:30
    morning_start = time(9, 30)
    morning_end = time(11, 30)
    
    # 下午交易时间 13:00-15:00
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)
    
    return (morning_start <= time_only <= morning_end) or (afternoon_start <= time_only <= afternoon_end)


def get_data_context() -> dict:
    """
    获取数据上下文信息
    
    Returns:
        dict: 包含各种时间和日期信息的上下文
    """
    now = datetime.now()
    current_date = now.date()
    trading_date = get_trading_date()
    
    return {
        'current_datetime': now,
        'current_date': current_date,
        'current_time': now.time(),
        'trading_date': trading_date,
        'is_trading_day': is_trading_day(current_date),
        'is_trading_time': is_trading_time(now),
        'weekday': current_date.weekday(),
        'weekday_name': current_date.strftime('%A'),
        'is_early_morning': now.time() < time(8, 0),
        'date_adjusted': trading_date != current_date,
        'adjustment_reason': _get_adjustment_reason(current_date, trading_date, now.time())
    }


def _get_adjustment_reason(current_date: date, trading_date: date, current_time: time) -> str:
    """
    获取日期调整的原因
    """
    if current_date == trading_date:
        return 'no_adjustment'
    
    weekday = current_date.weekday()
    
    if weekday >= 5:  # Weekend
        return 'weekend'
    elif current_time < time(8, 0):
        return 'early_morning'
    else:
        return 'other'


# 测试函数
def test_trading_date_logic():
    """测试交易日期逻辑"""
    print("=== 交易日期逻辑测试 ===\n")
    
    # 获取当前上下文
    context = get_data_context()
    
    print(f"当前时间: {context['current_datetime']}")
    print(f"当前日期: {context['current_date']}")
    print(f"交易日期: {context['trading_date']}")
    print(f"是否交易日: {context['is_trading_day']}")
    print(f"是否交易时间: {context['is_trading_time']}")
    print(f"星期: {context['weekday_name']}")
    print(f"是否早晨8点前: {context['is_early_morning']}")
    print(f"日期是否调整: {context['date_adjusted']}")
    print(f"调整原因: {context['adjustment_reason']}")
    
    # 测试不同时间点的情况
    print(f"\n=== 不同时间点测试 ===")
    
    test_cases = [
        datetime(2025, 8, 19, 7, 30),   # 周二早上7:30
        datetime(2025, 8, 19, 9, 30),   # 周二上午9:30
        datetime(2025, 8, 17, 10, 0),   # 周六上午10:00
        datetime(2025, 8, 18, 14, 0),   # 周日下午2:00
        datetime(2025, 8, 19, 15, 30),  # 周二下午3:30
    ]
    
    for test_time in test_cases:
        test_date = get_trading_date_for_time(test_time)
        print(f"{test_time.strftime('%Y-%m-%d %H:%M')} ({test_time.strftime('%A')}) -> {test_date}")


def get_trading_date_for_time(target_time: datetime) -> date:
    """
    为指定时间获取交易日期（用于测试）
    """
    current_date = target_time.date()
    current_time = target_time.time()
    
    # 定义8点作为分界线
    cutoff_time = time(8, 0)
    
    # 获取当前是星期几
    weekday = current_date.weekday()
    
    # 如果是周末，返回上一个交易日
    if weekday == 5:  # Saturday
        return current_date - timedelta(days=1)  # Friday
    elif weekday == 6:  # Sunday
        return current_date - timedelta(days=2)  # Friday
    
    # 如果是工作日但在8点之前，返回上一个交易日
    if current_time < cutoff_time:
        if weekday == 0:  # Monday
            return current_date - timedelta(days=3)  # Previous Friday
        else:
            return current_date - timedelta(days=1)  # Previous day
    
    # 工作日8点之后，返回当天
    return current_date


if __name__ == "__main__":
    test_trading_date_logic()