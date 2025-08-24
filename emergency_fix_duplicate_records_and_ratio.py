#!/usr/bin/env python3
"""
紧急修复脚本：解决重复交易记录和卖出比例计算问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from models.trade_record import TradeRecord
from models.profit_taking_target import ProfitTakingTarget
from app import create_app
from datetime import datetime, timedelta

def fix_duplicate_records():
    """修复重复的交易记录"""
    print("🔍 检查重复交易记录...")
    
    # 查找重复记录（相同股票代码、价格、数量、交易类型的记录）
    duplicates = db.session.query(
        TradeRecord.stock_code,
        TradeRecord.price,
        TradeRecord.quantity,
        TradeRecord.trade_type,
        db.func.count(TradeRecord.id).label('count')
    ).group_by(
        TradeRecord.stock_code,
        TradeRecord.price,
        TradeRecord.quantity,
        TradeRecord.trade_type
    ).having(db.func.count(TradeRecord.id) > 1).all()
    
    if not duplicates:
        print("✅ 没有发现重复记录")
        return
    
    print(f"🚨 发现 {len(duplicates)} 组重复记录")
    
    total_deleted = 0
    
    for dup in duplicates:
        # 获取这组重复记录
        records = TradeRecord.query.filter_by(
            stock_code=dup.stock_code,
            price=dup.price,
            quantity=dup.quantity,
            trade_type=dup.trade_type
        ).order_by(TradeRecord.created_at.asc()).all()
        
        print(f"\n📊 处理重复记录组: {dup.stock_code} - {dup.price} - {dup.quantity} - {dup.trade_type}")
        print(f"   共 {len(records)} 条记录")
        
        if len(records) <= 1:
            print("   跳过：实际记录数不足2条")
            continue
        
        # 保留最早的记录，删除其他的
        keep_record = records[0]
        delete_records = records[1:]
        
        print(f"   保留记录 ID: {keep_record.id} (创建时间: {keep_record.created_at})")
        
        for record in delete_records:
            print(f"   删除记录 ID: {record.id} (创建时间: {record.created_at})")
            
            # 删除关联的止盈目标
            targets = ProfitTakingTarget.query.filter_by(trade_record_id=record.id).all()
            for target in targets:
                db.session.delete(target)
                print(f"     删除关联的止盈目标 ID: {target.id}")
            
            # 删除交易记录
            db.session.delete(record)
            total_deleted += 1
    
    try:
        db.session.commit()
        print(f"\n✅ 成功删除 {total_deleted} 条重复记录")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ 删除重复记录失败: {e}")
        raise

def check_ratio_calculation():
    """检查卖出比例计算问题"""
    print("\n🔍 检查卖出比例计算...")
    
    # 查找有止盈目标的交易记录
    trades_with_targets = db.session.query(TradeRecord).join(ProfitTakingTarget).distinct().all()
    
    if not trades_with_targets:
        print("✅ 没有找到有止盈目标的交易记录")
        return
    
    print(f"📊 找到 {len(trades_with_targets)} 条有止盈目标的交易记录")
    
    for trade in trades_with_targets:
        targets = ProfitTakingTarget.query.filter_by(trade_record_id=trade.id).all()
        
        # 计算总卖出比例
        total_sell_ratio = sum(float(target.sell_ratio) for target in targets)
        
        print(f"\n📈 交易记录 ID: {trade.id} ({trade.stock_code})")
        print(f"   止盈目标数量: {len(targets)}")
        
        for i, target in enumerate(targets, 1):
            sell_ratio_percent = float(target.sell_ratio) * 100
            profit_ratio_percent = float(target.profit_ratio) * 100 if target.profit_ratio else 0
            print(f"   目标 {i}: 卖出比例 {sell_ratio_percent:.2f}%, 止盈比例 {profit_ratio_percent:.2f}%")
        
        total_percent = total_sell_ratio * 100
        print(f"   总卖出比例: {total_percent:.2f}%")
        
        if total_sell_ratio > 1.0:
            print(f"   ⚠️  警告: 总卖出比例超过100%!")
        elif total_sell_ratio == 1.0:
            print(f"   ✅ 总卖出比例正好100%")
        else:
            print(f"   ℹ️  总卖出比例未达到100%")

def fix_frontend_ratio_display():
    """修复前端卖出比例显示问题"""
    print("\n🔧 修复前端卖出比例显示...")
    
    # 读取交易记录模板
    template_path = "templates/trading_records.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否需要修复
        fixes_needed = []
        
        # 检查卖出比例显示逻辑
        if "sellRatio * 100" not in content and "sell_ratio * 100" not in content:
            fixes_needed.append("需要添加卖出比例百分比转换")
        
        if fixes_needed:
            print(f"   发现需要修复的问题: {', '.join(fixes_needed)}")
            
            # 创建修复后的JavaScript代码片段
            fix_js = '''
            // 修复卖出比例显示的辅助函数
            function formatRatioAsPercent(ratio) {
                if (ratio === null || ratio === undefined) return '0.00%';
                // 如果是小数格式（0-1），转换为百分比
                if (ratio <= 1) {
                    return (ratio * 100).toFixed(2) + '%';
                }
                // 如果已经是百分比格式，直接显示
                return ratio.toFixed(2) + '%';
            }
            
            // 修复总卖出比例计算
            function calculateTotalSellRatio(targets) {
                if (!targets || targets.length === 0) return 0;
                
                let total = 0;
                targets.forEach(target => {
                    let sellRatio = parseFloat(target.sell_ratio || target.sellRatio || 0);
                    // 确保使用小数格式进行计算
                    if (sellRatio > 1) {
                        sellRatio = sellRatio / 100;
                    }
                    total += sellRatio;
                });
                
                return total;
            }
            '''
            
            # 在文件末尾添加修复代码
            if "formatRatioAsPercent" not in content:
                content = content.replace("</script>", fix_js + "\n</script>", 1)
                
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("   ✅ 已添加前端修复代码")
            else:
                print("   ✅ 前端修复代码已存在")
        else:
            print("   ✅ 前端代码无需修复")
            
    except FileNotFoundError:
        print(f"   ❌ 模板文件不存在: {template_path}")
    except Exception as e:
        print(f"   ❌ 修复前端代码失败: {e}")

def add_duplicate_prevention():
    """添加重复提交防护"""
    print("\n🛡️  添加重复提交防护...")
    
    template_path = "templates/trading_records.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已有防护代码
        if "isSubmitting" in content:
            print("   ✅ 重复提交防护已存在")
            return
        
        # 添加防护代码
        protection_js = '''
        // 重复提交防护
        let isSubmitting = false;
        
        // 重写saveTrade方法，添加防护
        const originalSaveTrade = TradingRecordsManager.prototype.saveTrade;
        TradingRecordsManager.prototype.saveTrade = async function() {
            if (isSubmitting) {
                console.log('正在提交中，忽略重复请求');
                return;
            }
            
            isSubmitting = true;
            try {
                await originalSaveTrade.call(this);
            } finally {
                isSubmitting = false;
            }
        };
        
        // 重写handleTradeFormSubmit方法，添加防护
        const originalHandleSubmit = TradingRecordsManager.prototype.handleTradeFormSubmit;
        TradingRecordsManager.prototype.handleTradeFormSubmit = async function(formData) {
            if (isSubmitting) {
                console.log('正在提交中，忽略重复请求');
                return;
            }
            
            isSubmitting = true;
            try {
                await originalHandleSubmit.call(this, formData);
            } finally {
                isSubmitting = false;
            }
        };
        '''
        
        # 在文件末尾添加防护代码
        content = content.replace("</script>", protection_js + "\n</script>", 1)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ 已添加重复提交防护代码")
        
    except Exception as e:
        print(f"   ❌ 添加防护代码失败: {e}")

def main():
    """主函数"""
    print("🚨 紧急修复：重复记录和卖出比例问题")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. 修复重复记录
            fix_duplicate_records()
            
            # 2. 检查卖出比例计算
            check_ratio_calculation()
            
            # 3. 修复前端显示问题
            fix_frontend_ratio_display()
            
            # 4. 添加重复提交防护
            add_duplicate_prevention()
            
            print("\n" + "=" * 50)
            print("✅ 紧急修复完成!")
            print("\n建议:")
            print("1. 重启服务器以应用前端修复")
            print("2. 清除浏览器缓存")
            print("3. 重新测试交易记录功能")
            
        except Exception as e:
            print(f"\n❌ 修复过程中出现错误: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())