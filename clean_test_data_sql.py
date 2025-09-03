#!/usr/bin/env python3
"""
使用SQL直接删除测试数据
"""

from app import create_app
from extensions import db

def clean_test_data_with_sql():
    """使用SQL直接删除测试数据"""
    app = create_app()
    
    with app.app_context():
        print("=== 使用SQL清理测试数据 ===")
        
        # 查找测试的历史交易记录ID
        from sqlalchemy import text
        test_historical_trade_ids = []
        result = db.session.execute(
            text("SELECT id, stock_code, stock_name FROM historical_trades WHERE stock_code IN ('000001', '000002', '000004') AND strftime('%Y', buy_date) = '2024'")
        )
        
        for row in result:
            test_historical_trade_ids.append(row[0])
            print(f"发现测试记录: ID={row[0]}, 股票={row[1]} {row[2]}")
        
        if not test_historical_trade_ids:
            print("未找到需要清理的测试记录")
            return
        
        # 确认删除
        print(f"\n找到 {len(test_historical_trade_ids)} 条测试记录")
        confirm = input("确定要删除这些测试记录吗？(y/N): ").strip().lower()
        
        if confirm != 'y':
            print("操作已取消")
            return
        
        try:
            
            # 1. 删除复盘图片
            for trade_id in test_historical_trade_ids:
                # 查找相关的复盘记录ID
                review_result = db.session.execute(
                    text("SELECT id FROM trade_reviews WHERE historical_trade_id = :trade_id"), {"trade_id": trade_id}
                )
                review_ids = [row[0] for row in review_result]
                
                if review_ids:
                    # 删除复盘图片
                    for review_id in review_ids:
                        db.session.execute(
                            text("DELETE FROM review_images WHERE trade_review_id = :review_id"), {"review_id": review_id}
                        )
                        print(f"删除复盘ID {review_id} 的相关图片")
            
            # 2. 删除复盘记录
            for trade_id in test_historical_trade_ids:
                result = db.session.execute(
                    text("DELETE FROM trade_reviews WHERE historical_trade_id = :trade_id"), {"trade_id": trade_id}
                )
                if result.rowcount > 0:
                    print(f"删除历史交易ID {trade_id} 的 {result.rowcount} 条复盘记录")
            
            # 3. 删除历史交易记录
            for trade_id in test_historical_trade_ids:
                result = db.session.execute(
                    text("DELETE FROM historical_trades WHERE id = :trade_id"), {"trade_id": trade_id}
                )
                if result.rowcount > 0:
                    print(f"删除历史交易记录 ID {trade_id}")
            
            # 提交事务
            db.session.commit()
            print(f"\n成功删除 {len(test_historical_trade_ids)} 条测试记录及其相关数据")
            
            # 验证删除结果
            result = db.session.execute(
                text("SELECT COUNT(*) FROM historical_trades WHERE stock_code IN ('000001', '000002', '000004') AND strftime('%Y', buy_date) = '2024'")
            )
            remaining_count = result.scalar()
            
            if remaining_count > 0:
                print(f"警告: 仍有 {remaining_count} 条相关记录未删除")
            else:
                print("所有测试记录已成功删除")
                
        except Exception as e:
            db.session.rollback()
            print(f"删除失败: {str(e)}")
            raise

if __name__ == '__main__':
    clean_test_data_with_sql()