#!/usr/bin/env python3
"""
测试完整的数据流，模拟用户提交表单的过程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.trade_record import TradeRecord
from datetime import datetime

def test_trade_creation():
    """测试交易记录创建"""
    print("=== 测试交易记录创建 ===\n")
    
    # 模拟前端传来的数据（用户输入10%，前端没有转换）
    test_data = {
        'stock_code': '000001',
        'stock_name': '平安银行',
        'trade_type': 'buy',
        'price': 12.50,
        'quantity': 1000,
        'trade_date': datetime.now(),
        'reason': '技术突破',
        'take_profit_ratio': '10',  # 用户输入的原始值：10（表示10%）
        'sell_ratio': '50',         # 用户输入的原始值：50（表示50%）
        'stop_loss_price': 11.00,
        'notes': '测试修复'
    }
    
    print("模拟数据:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    print()
    
    try:
        # 尝试创建交易记录
        print("尝试创建交易记录...")
        trade = TradeRecord(**test_data)
        print("✅ 交易记录创建成功！")
        
        # 检查转换后的值
        print(f"转换后的 take_profit_ratio: {trade.take_profit_ratio}")
        print(f"转换后的 sell_ratio: {trade.sell_ratio}")
        
        # 验证值是否在正确范围内
        if 0 <= float(trade.take_profit_ratio) <= 1:
            print("✅ take_profit_ratio 在有效范围内")
        else:
            print("❌ take_profit_ratio 超出有效范围")
            
        if 0 <= float(trade.sell_ratio) <= 1:
            print("✅ sell_ratio 在有效范围内")
        else:
            print("❌ sell_ratio 超出有效范围")
            
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        print(f"错误类型: {type(e).__name__}")

if __name__ == "__main__":
    test_trade_creation()