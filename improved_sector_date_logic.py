#!/usr/bin/env python3
"""
改进的板块数据日期逻辑
考虑交易日、时区等因素
"""
from datetime import date, datetime, time
import pandas as pd

def get_trading_date() -> date:
    """
    获取交易日期
    考虑周末、节假日等因素
    """
    today = date.today()
    weekday = today.weekday()  # 0=Monday, 6=Sunday
    
    # 如果是周末，数据可能属于上一个交易日
    if weekday == 5:  # Saturday
        # 周六获取的数据可能是周五的
        return today
    elif weekday == 6:  # Sunday  
        # 周日获取的数据可能是周五的
        return today
    else:
        # 工作日，使用当天日期
        return today

def is_trading_time() -> bool:
    """
    判断是否在交易时间内
    A股交易时间：9:30-11:30, 13:00-15:00
    """
    now = datetime.now().time()
    
    # 上午交易时间 9:30-11:30
    morning_start = time(9, 30)
    morning_end = time(11, 30)
    
    # 下午交易时间 13:00-15:00
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)
    
    return (morning_start <= now <= morning_end) or (afternoon_start <= now <= afternoon_end)

def get_data_date_with_context() -> tuple[date, dict]:
    """
    获取数据日期，并返回上下文信息
    """
    current_date = date.today()
    current_time = datetime.now()
    trading_date = get_trading_date()
    is_trading = is_trading_time()
    
    context = {
        'current_date': current_date,
        'current_time': current_time,
        'trading_date': trading_date,
        'is_trading_time': is_trading,
        'weekday': current_date.weekday(),
        'weekday_name': current_date.strftime('%A'),
        'data_freshness': 'real-time' if is_trading else 'latest-available'
    }
    
    return trading_date, context

def analyze_data_quality(sector_df) -> dict:
    """
    分析数据质量，判断数据的时效性
    """
    if sector_df.empty:
        return {'quality': 'no-data', 'confidence': 0}
    
    # 检查涨跌幅分布
    change_col = '涨跌幅'
    if change_col not in sector_df.columns:
        return {'quality': 'unknown', 'confidence': 0}
    
    changes = sector_df[change_col]
    non_zero_count = (changes != 0).sum()
    total_count = len(changes)
    non_zero_ratio = non_zero_count / total_count if total_count > 0 else 0
    
    # 计算涨跌幅的标准差（活跃度指标）
    change_std = changes.std()
    
    # 判断数据质量
    if non_zero_ratio > 0.8 and change_std > 0.5:
        quality = 'high'  # 高质量实时数据
        confidence = 0.9
    elif non_zero_ratio > 0.5:
        quality = 'medium'  # 中等质量数据
        confidence = 0.7
    elif non_zero_ratio > 0.1:
        quality = 'low'  # 低质量数据
        confidence = 0.4
    else:
        quality = 'stale'  # 可能是过时数据
        confidence = 0.1
    
    return {
        'quality': quality,
        'confidence': confidence,
        'non_zero_ratio': non_zero_ratio,
        'change_std': change_std,
        'active_sectors': non_zero_count,
        'total_sectors': total_count
    }

# 示例使用
if __name__ == "__main__":
    print("=== 改进的日期逻辑测试 ===\n")
    
    # 获取数据日期和上下文
    data_date, context = get_data_date_with_context()
    
    print(f"数据日期: {data_date}")
    print(f"当前时间: {context['current_time']}")
    print(f"是否交易时间: {context['is_trading_time']}")
    print(f"星期: {context['weekday_name']}")
    print(f"数据新鲜度: {context['data_freshness']}")
    
    # 模拟数据质量分析
    try:
        import akshare as ak
        sector_df = ak.stock_board_industry_name_em()
        quality_info = analyze_data_quality(sector_df)
        
        print(f"\n数据质量分析:")
        print(f"质量等级: {quality_info['quality']}")
        print(f"置信度: {quality_info['confidence']:.1%}")
        print(f"活跃板块比例: {quality_info['non_zero_ratio']:.1%}")
        print(f"涨跌幅标准差: {quality_info['change_std']:.2f}")
        
    except Exception as e:
        print(f"无法获取实时数据进行分析: {e}")