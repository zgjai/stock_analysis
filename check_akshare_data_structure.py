#!/usr/bin/env python3
"""
检查AKShare板块数据的结构和日期信息
"""
import akshare as ak
import pandas as pd
from datetime import date, datetime

def check_akshare_sector_data():
    """检查AKShare板块数据结构"""
    
    print("=== AKShare板块数据结构检查 ===\n")
    
    try:
        # 获取板块数据
        print("1. 获取板块数据...")
        sector_df = ak.stock_board_industry_name_em()
        
        print(f"数据形状: {sector_df.shape}")
        print(f"列名: {list(sector_df.columns)}")
        
        print("\n2. 数据样例 (前5行):")
        print(sector_df.head())
        
        print("\n3. 数据类型:")
        print(sector_df.dtypes)
        
        print("\n4. 检查是否包含日期相关字段:")
        date_related_columns = [col for col in sector_df.columns if any(keyword in col.lower() for keyword in ['date', '日期', 'time', '时间'])]
        if date_related_columns:
            print(f"发现日期相关字段: {date_related_columns}")
            for col in date_related_columns:
                print(f"  {col}: {sector_df[col].iloc[0] if not sector_df.empty else 'N/A'}")
        else:
            print("未发现明确的日期字段")
        
        print("\n5. 检查数据获取时间:")
        current_time = datetime.now()
        print(f"当前系统时间: {current_time}")
        print(f"当前系统日期: {date.today()}")
        
        print("\n6. 分析数据时效性:")
        if not sector_df.empty:
            # 检查涨跌幅数据
            change_col = None
            for col in sector_df.columns:
                if '涨跌幅' in col or 'change' in col.lower():
                    change_col = col
                    break
            
            if change_col:
                print(f"涨跌幅字段: {change_col}")
                print(f"涨跌幅范围: {sector_df[change_col].min():.2f}% ~ {sector_df[change_col].max():.2f}%")
                
                # 检查是否有实时数据特征
                non_zero_changes = (sector_df[change_col] != 0).sum()
                total_sectors = len(sector_df)
                print(f"非零涨跌幅板块数: {non_zero_changes}/{total_sectors} ({non_zero_changes/total_sectors*100:.1f}%)")
                
                if non_zero_changes > 0:
                    print("✓ 数据显示有涨跌变化，可能是实时或当日数据")
                else:
                    print("⚠ 所有板块涨跌幅为0，可能是非交易时间或数据异常")
        
        print("\n7. 建议的日期策略:")
        print("由于AKShare数据不包含明确的日期字段，建议:")
        print("- 使用系统当前日期作为记录日期")
        print("- 在非交易时间获取的数据仍记录为当天")
        print("- 通过涨跌幅数据判断是否为有效交易数据")
        print("- 考虑添加数据获取时间戳用于追踪")
        
    except Exception as e:
        print(f"获取数据失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_akshare_sector_data()