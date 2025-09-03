#!/usr/bin/env python3
"""
清理历史交易表中的测试数据
"""

from app import create_app
from models.historical_trade import HistoricalTrade
from extensions import db

def clean_test_historical_trades():
    """清理测试的历史交易记录"""
    app = create_app()
    
    with app.app_context():
        print("=== 清理历史交易表中的测试数据 ===")
        
        # 查找测试记录
        test_codes = ['000001', '000002', '000004']
        test_records = []
        
        for code in test_codes:
            records = HistoricalTrade.query.filter_by(stock_code=code).all()
            for record in records:
                # 检查是否是测试数据（通过日期判断，2024年的数据很可能是测试数据）
                if record.buy_date.year == 2024:
                    test_records.append(record)
                    print(f"发现测试记录: ID={record.id}, 股票={record.stock_code} {record.stock_name}, 买入日期={record.buy_date}")
        
        if not test_records:
            print("未找到需要清理的测试记录")
            return
        
        # 确认删除
        print(f"\n找到 {len(test_records)} 条测试记录")
        confirm = input("确定要删除这些测试记录吗？(y/N): ").strip().lower()
        
        if confirm != 'y':
            print("操作已取消")
            return
        
        # 删除测试记录
        try:
            # 首先删除相关的复盘记录
            from models.trade_review import TradeReview
            
            # 使用no_autoflush避免自动刷新问题
            with db.session.no_autoflush:
                for record in test_records:
                    # 查找相关的复盘记录
                    reviews = TradeReview.query.filter_by(historical_trade_id=record.id).all()
                    if reviews:
                        print(f"删除 {len(reviews)} 条相关复盘记录 (历史交易ID: {record.id})")
                        for review in reviews:
                            db.session.delete(review)
                    
                    print(f"删除历史交易记录: ID={record.id}, 股票={record.stock_code} {record.stock_name}")
                    db.session.delete(record)
            
            db.session.commit()
            print(f"\n成功删除 {len(test_records)} 条测试记录及其相关复盘记录")
            
            # 验证删除结果
            remaining_test_records = []
            for code in test_codes:
                records = HistoricalTrade.query.filter_by(stock_code=code).all()
                remaining_test_records.extend(records)
            
            if remaining_test_records:
                print(f"警告: 仍有 {len(remaining_test_records)} 条相关记录未删除")
                for record in remaining_test_records:
                    print(f"  ID={record.id}, 股票={record.stock_code} {record.stock_name}, 买入日期={record.buy_date}")
            else:
                print("所有测试记录已成功删除")
                
        except Exception as e:
            db.session.rollback()
            print(f"删除失败: {str(e)}")
            raise

if __name__ == '__main__':
    clean_test_historical_trades()