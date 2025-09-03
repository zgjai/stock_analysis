#!/usr/bin/env python3
"""
测试类型转换修复
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from extensions import db
from models.trade_record import TradeRecord
from datetime import datetime

def test_type_conversion_fix():
    """测试类型转换修复"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # 测试数据 - 模拟前端发送的字符串类型数据
        test_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': '10.50',  # 字符串类型
            'quantity': '1000',
            'trade_date': datetime.now(),
            'reason': '技术分析买入',
            'stop_loss_price': '9.50',  # 字符串类型
            'take_profit_ratio': '0.15',
            'sell_ratio': '1.0'
        }
        
        print("=== 测试类型转换修复 ===")
        print(f"测试数据: {test_data}")
        
        try:
            # 创建交易记录
            trade = TradeRecord(**test_data)
            db.session.add(trade)
            db.session.commit()
            
            print("✅ 交易记录创建成功！")
            print(f"价格类型: {type(trade.price)}, 值: {trade.price}")
            print(f"止损价格类型: {type(trade.stop_loss_price)}, 值: {trade.stop_loss_price}")
            
            # 验证数据类型
            assert isinstance(float(trade.price), float), "价格应该是数值类型"
            assert isinstance(float(trade.stop_loss_price), float), "止损价格应该是数值类型"
            assert float(trade.stop_loss_price) < float(trade.price), "止损价格应该小于买入价格"
            
            print("✅ 所有验证通过！")
            return True
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_type_conversion_fix()
    if success:
        print("\n🎉 类型转换修复测试通过！")
    else:
        print("\n💥 类型转换修复测试失败！")
        sys.exit(1)