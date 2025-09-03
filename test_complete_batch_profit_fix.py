#!/usr/bin/env python3
"""
完整测试分批止盈创建流程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from extensions import db
from services.trading_service import TradingService
from datetime import datetime
import json

def create_test_app():
    """创建测试应用"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    db.init_app(app)
    
    return app

def test_complete_batch_profit_creation():
    """测试完整的分批止盈创建流程"""
    print("=== 测试完整的分批止盈创建流程 ===")
    
    app = create_test_app()
    
    with app.app_context():
        try:
            # 创建数据库表
            db.create_all()
            
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
            print(json.dumps(test_data, default=str, indent=2, ensure_ascii=False))
            
            # 测试数据提取
            print("\n1. 测试数据提取:")
            profit_targets = TradingService._extract_batch_profit_data(test_data)
            clean_data = TradingService._clean_trade_data(test_data)
            
            print(f"提取的止盈目标: {profit_targets}")
            print(f"清理后的数据: {clean_data}")
            
            # 测试创建交易记录（模拟，不实际调用数据库）
            print("\n2. 数据验证:")
            print(f"- 使用分批止盈: {clean_data.get('use_batch_profit_taking')}")
            print(f"- 止盈目标数量: {len(profit_targets)}")
            print(f"- 清理后字段数量: {len(clean_data)}")
            
            # 验证数据完整性
            print("\n3. 数据完整性验证:")
            required_fields = ['stock_code', 'stock_name', 'trade_type', 'price', 'quantity', 'reason']
            missing_fields = [field for field in required_fields if field not in clean_data]
            
            if missing_fields:
                print(f"❌ 缺少必填字段: {missing_fields}")
                return False
            else:
                print("✅ 所有必填字段都存在")
            
            # 验证止盈目标
            print("\n4. 止盈目标验证:")
            for i, target in enumerate(profit_targets):
                print(f"目标 {i+1}:")
                print(f"  - 序列: {target['sequence_order']}")
                print(f"  - 止盈比例: {target['profit_ratio']*100}%")
                print(f"  - 卖出比例: {target['sell_ratio']*100}%")
                print(f"  - 目标价格: {target['target_price']}")
            
            # 验证不包含无效字段
            print("\n5. 无效字段检查:")
            invalid_fields = [key for key in clean_data.keys() if key.startswith('profit_ratio_') or key.startswith('target_price_') or key.startswith('sell_ratio_')]
            
            if invalid_fields:
                print(f"❌ 仍包含无效字段: {invalid_fields}")
                return False
            else:
                print("✅ 已清除所有分批止盈字段")
            
            print("\n=== 测试成功 ===")
            return True
            
        except Exception as e:
            print(f"\n=== 测试失败 ===")
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_complete_batch_profit_creation()
    if success:
        print("\n🎉 所有测试通过！修复应该能解决问题。")
    else:
        print("\n❌ 测试失败，需要进一步调试。")