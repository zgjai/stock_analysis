#!/usr/bin/env python3
"""
清理所有重复交易记录的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from models.trade_record import TradeRecord
from models.profit_taking_target import ProfitTakingTarget
from app import create_app
from datetime import datetime

def clean_all_duplicates():
    """清理所有重复记录"""
    print("🧹 开始清理所有重复交易记录...")
    
    # 获取所有交易记录，按关键字段分组
    all_records = TradeRecord.query.order_by(TradeRecord.created_at.asc()).all()
    
    print(f"📊 总记录数: {len(all_records)}")
    
    # 按关键字段分组
    groups = {}
    for record in all_records:
        # 使用股票代码、价格、数量、交易类型、原因作为唯一标识
        key = (
            record.stock_code,
            float(record.price),
            record.quantity,
            record.trade_type,
            record.reason
        )
        
        if key not in groups:
            groups[key] = []
        groups[key].append(record)
    
    # 找出重复组
    duplicate_groups = {k: v for k, v in groups.items() if len(v) > 1}
    
    print(f"🔍 发现 {len(duplicate_groups)} 组重复记录")
    
    total_deleted = 0
    
    for key, records in duplicate_groups.items():
        stock_code, price, quantity, trade_type, reason = key
        
        print(f"\n📋 处理重复组: {stock_code} - ¥{price} - {quantity}股 - {trade_type} - {reason}")
        print(f"   共 {len(records)} 条记录")
        
        # 保留最早的记录
        keep_record = records[0]
        delete_records = records[1:]
        
        print(f"   ✅ 保留: ID {keep_record.id} (创建于 {keep_record.created_at})")
        
        for record in delete_records:
            print(f"   🗑️  删除: ID {record.id} (创建于 {record.created_at})")
            
            # 删除关联的止盈目标
            targets = ProfitTakingTarget.query.filter_by(trade_record_id=record.id).all()
            for target in targets:
                db.session.delete(target)
                print(f"      删除止盈目标 ID: {target.id}")
            
            # 删除交易记录
            db.session.delete(record)
            total_deleted += 1
    
    try:
        db.session.commit()
        print(f"\n✅ 成功删除 {total_deleted} 条重复记录")
        
        # 显示清理后的统计
        remaining_count = TradeRecord.query.count()
        print(f"📊 剩余记录数: {remaining_count}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ 删除失败: {e}")
        return False

def show_final_stats():
    """显示最终统计信息"""
    print("\n📈 最终统计信息:")
    
    # 按股票代码统计
    from sqlalchemy import func
    stats = db.session.query(
        TradeRecord.stock_code,
        TradeRecord.stock_name,
        func.count(TradeRecord.id).label('count')
    ).group_by(TradeRecord.stock_code, TradeRecord.stock_name).all()
    
    print("   按股票统计:")
    for stat in stats:
        print(f"   - {stat.stock_code} ({stat.stock_name}): {stat.count} 条记录")
    
    # 按交易类型统计
    type_stats = db.session.query(
        TradeRecord.trade_type,
        func.count(TradeRecord.id).label('count')
    ).group_by(TradeRecord.trade_type).all()
    
    print("\n   按交易类型统计:")
    for stat in type_stats:
        print(f"   - {stat.trade_type}: {stat.count} 条记录")
    
    # 止盈目标统计
    target_count = ProfitTakingTarget.query.count()
    trades_with_targets = db.session.query(TradeRecord).join(ProfitTakingTarget).distinct().count()
    
    print(f"\n   止盈目标: {target_count} 个")
    print(f"   有止盈目标的交易: {trades_with_targets} 条")

def main():
    """主函数"""
    print("🚨 清理所有重复交易记录")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # 清理重复记录
            success = clean_all_duplicates()
            
            if success:
                # 显示最终统计
                show_final_stats()
                
                print("\n" + "=" * 50)
                print("✅ 清理完成!")
                print("\n建议:")
                print("1. 重启服务器")
                print("2. 清除浏览器缓存")
                print("3. 测试交易记录功能")
                print("4. 检查前端是否还有重复提交问题")
                
                return 0
            else:
                print("\n❌ 清理失败")
                return 1
                
        except Exception as e:
            print(f"\n❌ 清理过程中出现错误: {e}")
            return 1

if __name__ == "__main__":
    exit(main())