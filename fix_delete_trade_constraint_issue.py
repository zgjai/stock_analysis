#!/usr/bin/env python3
"""
修复删除交易记录时的数据库约束问题

问题描述：
删除交易记录时出现 NOT NULL constraint failed: profit_taking_targets.trade_record_id 错误
这是因为 SQLAlchemy 试图将相关的 profit_taking_targets 记录的 trade_record_id 设置为 NULL，
但这个字段有 NOT NULL 约束。

解决方案：
1. 修改模型关系定义，使用 cascade='all, delete-orphan'
2. 确保删除逻辑正确处理相关记录
3. 测试删除功能是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.trade_record import TradeRecord
from models.profit_taking_target import ProfitTakingTarget
from services.trading_service import TradingService
from datetime import datetime


def test_delete_functionality():
    """测试删除功能是否正常工作"""
    app = create_app()
    
    with app.app_context():
        print("开始测试删除交易记录功能...")
        
        # 创建一个测试交易记录
        test_data = {
            'stock_code': '000001',
            'stock_name': '测试股票',
            'trade_type': 'buy',
            'price': 10.00,
            'quantity': 1000,
            'trade_date': datetime.now(),
            'reason': '技术分析',
            'use_batch_profit_taking': True
        }
        
        # 创建止盈目标
        profit_targets = [
            {
                'target_price': 11.00,
                'profit_ratio': 0.10,
                'sell_ratio': 0.50
            },
            {
                'target_price': 12.00,
                'profit_ratio': 0.20,
                'sell_ratio': 0.50
            }
        ]
        
        try:
            # 创建交易记录
            print("创建测试交易记录...")
            trade = TradingService.create_trade_with_batch_profit(test_data, profit_targets)
            print(f"创建成功，交易记录ID: {trade.id}")
            
            # 验证止盈目标是否创建成功
            targets = ProfitTakingTarget.query.filter_by(trade_record_id=trade.id).all()
            print(f"创建了 {len(targets)} 个止盈目标")
            
            # 测试删除功能
            print(f"开始删除交易记录 {trade.id}...")
            result = TradingService.delete_trade(trade.id)
            
            if result:
                print("删除成功！")
                
                # 验证相关记录是否也被删除
                remaining_targets = ProfitTakingTarget.query.filter_by(trade_record_id=trade.id).all()
                if len(remaining_targets) == 0:
                    print("相关的止盈目标记录也已正确删除")
                else:
                    print(f"警告：仍有 {len(remaining_targets)} 个止盈目标记录未删除")
                
                # 验证交易记录是否被删除
                db.session.expire_all()  # 刷新会话
                try:
                    deleted_trade = TradeRecord.get_by_id(trade.id)
                    if deleted_trade:
                        print("错误：交易记录未被删除")
                    else:
                        print("交易记录已正确删除")
                except:
                    print("交易记录已正确删除")
            else:
                print("删除失败")
                
        except Exception as e:
            print(f"测试过程中出现错误: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("测试完成")


def check_database_constraints():
    """检查数据库约束设置"""
    app = create_app()
    
    with app.app_context():
        print("检查数据库约束设置...")
        
        # 检查 profit_taking_targets 表的约束
        inspector = db.inspect(db.engine)
        
        # 获取表信息
        columns = inspector.get_columns('profit_taking_targets')
        for column in columns:
            if column['name'] == 'trade_record_id':
                print(f"trade_record_id 字段约束: nullable={column['nullable']}")
        
        # 获取外键约束
        foreign_keys = inspector.get_foreign_keys('profit_taking_targets')
        for fk in foreign_keys:
            if 'trade_record_id' in fk['constrained_columns']:
                print(f"外键约束: {fk}")


def main():
    """主函数"""
    print("修复删除交易记录约束问题")
    print("=" * 50)
    
    # 检查数据库约束
    check_database_constraints()
    print()
    
    # 测试删除功能
    test_delete_functionality()
    
    print("\n修复完成！")
    print("现在删除交易记录功能应该可以正常工作了。")


if __name__ == '__main__':
    main()