#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修补ReviewService的成本价计算逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 读取原文件内容
def patch_review_service():
    """修补ReviewService的get_current_holdings方法"""
    
    # 新的持仓周期计算方法
    new_method = '''
    @classmethod
    def _get_current_holding_period(cls, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取股票当前活跃持仓周期的信息（修复成本价计算）"""
        
        # 获取所有交易记录，按时间排序
        trades = TradeRecord.query.filter(
            and_(
                TradeRecord.stock_code == stock_code,
                TradeRecord.is_corrected == False
            )
        ).order_by(TradeRecord.trade_date.asc()).all()
        
        if not trades:
            return None
        
        # 分析持仓周期
        current_period = None
        running_quantity = 0
        
        for trade in trades:
            if trade.trade_type == 'buy':
                if current_period is None:
                    # 开始新的持仓周期
                    current_period = {
                        'stock_code': stock_code,
                        'stock_name': trade.stock_name,
                        'start_date': trade.trade_date,
                        'buy_trades': [],
                        'sell_trades': [],
                        'total_buy_quantity': 0,
                        'total_sell_quantity': 0,
                        'total_cost': 0
                    }
                
                current_period['buy_trades'].append(trade)
                current_period['total_buy_quantity'] += trade.quantity
                current_period['total_cost'] += trade.price * trade.quantity
                running_quantity += trade.quantity
                
            elif trade.trade_type == 'sell':
                if current_period is not None:
                    current_period['sell_trades'].append(trade)
                    current_period['total_sell_quantity'] += trade.quantity
                    running_quantity -= trade.quantity
                    
                    # 如果卖完了，结束当前持仓周期
                    if running_quantity <= 0:
                        current_period = None
                        running_quantity = 0
        
        # 返回当前活跃的持仓周期
        if current_period is not None and running_quantity > 0:
            current_period['current_quantity'] = running_quantity
            current_period['avg_buy_price'] = current_period['total_cost'] / current_period['total_buy_quantity']
            return current_period
        
        return None
'''
    
    print("=== 修补ReviewService成本价计算逻辑 ===")
    print("新增方法: _get_current_holding_period")
    print("该方法将正确处理持仓周期，避免已结束持仓影响当前成本价计算")
    
    # 读取原文件
    with open('services/review_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到合适的插入位置（在get_current_holdings方法之前）
    insert_position = content.find('    @classmethod\n    def get_current_holdings(')
    
    if insert_position == -1:
        print("❌ 未找到get_current_holdings方法")
        return False
    
    # 插入新方法
    new_content = content[:insert_position] + new_method + '\n    ' + content[insert_position:]
    
    # 备份原文件
    backup_file = 'services/review_service.py.backup_cost_price_fix'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 原文件已备份到: {backup_file}")
    
    # 写入修改后的文件
    with open('services/review_service.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ 已添加新的持仓周期计算方法")
    
    return True

def create_fixed_get_current_holdings():
    """创建修复后的get_current_holdings方法的替换代码"""
    
    replacement_code = '''    @classmethod
    def get_current_holdings(cls, force_refresh_prices: bool = False) -> List[Dict[str, Any]]:
        """获取当前持仓列表（修复版：按持仓周期计算成本价）"""
        try:
            # 获取所有有交易记录的股票代码
            stock_codes = db.session.query(TradeRecord.stock_code).filter(
                TradeRecord.is_corrected == False
            ).distinct().all()
            
            holdings = []
            
            for (stock_code,) in stock_codes:
                period = cls._get_current_holding_period(stock_code)
                
                if period and period['current_quantity'] > 0:
                    # 获取最新复盘记录
                    latest_review = cls.get_latest_review_by_stock(stock_code)
                    
                    # 获取当前持仓的实际开始日期
                    current_holding_start_date = period['start_date']
                    
                    # 计算实际持仓交易日数
                    actual_holding_days = cls._calculate_actual_holding_days(
                        current_holding_start_date,
                        latest_review.holding_days if latest_review else None
                    )
                    
                    # 保持原有的持仓天数计算（兼容性）
                    holding_days = cls._calculate_holding_days(
                        current_holding_start_date,
                        latest_review.holding_days if latest_review else None
                    )
                    
                    # 获取当前价格
                    current_price = cls._get_current_price(stock_code, force_refresh_prices)
                    
                    holding = {
                        'stock_code': period['stock_code'],
                        'stock_name': period['stock_name'],
                        'current_quantity': period['current_quantity'],
                        'total_buy_quantity': period['total_buy_quantity'],
                        'total_sell_quantity': period['total_sell_quantity'],
                        'avg_buy_price': float(period['avg_buy_price']),
                        'avg_price': float(period['avg_buy_price']),  # 兼容字段
                        'current_price': current_price,
                        'first_buy_date': current_holding_start_date.isoformat(),
                        'last_buy_date': period['buy_trades'][-1].trade_date.isoformat() if period['buy_trades'] else current_holding_start_date.isoformat(),
                        'holding_days': holding_days,
                        'actual_holding_days': actual_holding_days,
                        'latest_review': latest_review.to_dict() if latest_review else None
                    }
                    holdings.append(holding)
            
            return holdings
            
        except Exception as e:
            raise DatabaseError(f"获取当前持仓失败: {str(e)}")'''
    
    print("\n=== 创建修复后的get_current_holdings方法 ===")
    print("该方法将使用新的持仓周期计算逻辑")
    
    return replacement_code

if __name__ == '__main__':
    # 第一步：添加新的辅助方法
    if patch_review_service():
        print("\n" + "="*50)
        
        # 第二步：显示需要替换的方法代码
        replacement = create_fixed_get_current_holdings()
        print("接下来需要手动替换get_current_holdings方法的实现")
        print("替换代码已准备好，需要手动应用")
        
        # 保存替换代码到文件
        with open('get_current_holdings_replacement.py', 'w', encoding='utf-8') as f:
            f.write(replacement)
        print("✅ 替换代码已保存到: get_current_holdings_replacement.py")
        
        print("\n🔧 修复步骤:")
        print("1. ✅ 已添加 _get_current_holding_period 辅助方法")
        print("2. ⏳ 需要手动替换 get_current_holdings 方法的实现")
        print("3. ⏳ 测试修复效果")
    else:
        print("❌ 修补失败")