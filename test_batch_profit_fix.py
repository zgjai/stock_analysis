#!/usr/bin/env python3
"""
测试分批止盈数据处理修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.trading_service import TradingService
from datetime import datetime

def test_batch_profit_extraction():
    """测试分批止盈数据提取"""
    print("=== 测试分批止盈数据提取 ===")
    
    # 模拟日志中的数据
    test_data = {
        'stock_code': '000776',
        'stock_name': '广发证券',
        'trade_type': 'buy',
        'trade_date': datetime(2025, 8, 4, 16, 2),
        'price': 19.453,
        'quantity': 31100,
        'reason': '单针二十战法',
        'use_batch_profit_taking': 'on',
        'stop_loss_price': '19',
        'profit_ratio_1': '10',
        'target_price_1': '21.40',
        'sell_ratio_1': '20',
        'profit_ratio_2': '20',
        'target_price_2': '23.34',
        'sell_ratio_2': '40',
        'profit_ratio_3': '30',
        'target_price_3': '25.29',
        'sell_ratio_3': '40',
        'notes': ''
    }
    
    print("原始数据:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # 测试提取分批止盈数据
    print("\n提取分批止盈数据:")
    profit_targets = TradingService._extract_batch_profit_data(test_data)
    print(f"提取的止盈目标: {profit_targets}")
    
    # 测试清理数据
    print("\n清理交易数据:")
    clean_data = TradingService._clean_trade_data(test_data)
    print("清理后的数据:")
    for key, value in clean_data.items():
        print(f"  {key}: {value}")
    
    return profit_targets, clean_data

if __name__ == "__main__":
    try:
        profit_targets, clean_data = test_batch_profit_extraction()
        print("\n=== 测试成功 ===")
        print(f"提取了 {len(profit_targets)} 个止盈目标")
        print(f"清理后保留了 {len(clean_data)} 个字段")
    except Exception as e:
        print(f"\n=== 测试失败 ===")
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()