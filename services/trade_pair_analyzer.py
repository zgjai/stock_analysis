"""
交易配对分析服务
用于分析完整的买卖周期和计算收益分布
"""
from typing import List, Dict, Tuple, Optional
from decimal import Decimal
from collections import defaultdict
from models.trade_record import TradeRecord
from sqlalchemy import func


class TradePairAnalyzer:
    """交易配对分析器"""
    
    @classmethod
    def analyze_completed_trades(cls) -> List[Dict]:
        """
        分析已完成的交易配对
        返回完整买卖周期的列表
        """
        trades_by_stock = cls._group_trades_by_stock()
        completed_pairs = []
        
        for stock_code, trades in trades_by_stock.items():
            pairs = cls._extract_trade_pairs(trades)
            completed_pairs.extend(pairs)
        
        return completed_pairs
    
    @classmethod
    def _group_trades_by_stock(cls) -> Dict[str, List[TradeRecord]]:
        """按股票代码分组交易记录"""
        trades = TradeRecord.query.order_by(
            TradeRecord.stock_code, 
            TradeRecord.trade_date
        ).all()
        
        trades_by_stock = defaultdict(list)
        for trade in trades:
            trades_by_stock[trade.stock_code].append(trade)
        
        return dict(trades_by_stock)
    
    @classmethod
    def _extract_trade_pairs(cls, trades: List[TradeRecord]) -> List[Dict]:
        """
        从交易记录中提取买卖配对
        使用FIFO（先进先出）原则进行配对
        """
        buy_queue = []  # 买入队列：[(trade, remaining_quantity), ...]
        completed_pairs = []
        
        for trade in trades:
            if trade.trade_type == 'buy':
                # 买入交易加入队列
                buy_queue.append({
                    'trade': trade,
                    'remaining_quantity': trade.quantity,
                    'remaining_cost': trade.quantity * trade.price
                })
            
            elif trade.trade_type == 'sell':
                # 卖出交易，与买入队列配对
                sell_quantity = trade.quantity
                sell_amount = trade.quantity * trade.price
                
                while sell_quantity > 0 and buy_queue:
                    buy_item = buy_queue[0]
                    buy_trade = buy_item['trade']
                    buy_remaining = buy_item['remaining_quantity']
                    
                    # 计算本次配对的数量
                    pair_quantity = min(sell_quantity, buy_remaining)
                    
                    # 计算成本和收入
                    cost_per_share = buy_item['remaining_cost'] / buy_item['remaining_quantity']
                    pair_cost = pair_quantity * cost_per_share
                    pair_revenue = pair_quantity * trade.price
                    
                    # 创建配对记录
                    pair = {
                        'stock_code': trade.stock_code,
                        'buy_trade_id': buy_trade.id,
                        'sell_trade_id': trade.id,
                        'buy_date': buy_trade.trade_date,
                        'sell_date': trade.trade_date,
                        'quantity': pair_quantity,
                        'buy_price': cost_per_share,
                        'sell_price': trade.price,
                        'cost': pair_cost,
                        'revenue': pair_revenue,
                        'profit': pair_revenue - pair_cost,
                        'profit_rate': (pair_revenue - pair_cost) / pair_cost if pair_cost > 0 else 0,
                        'holding_days': (trade.trade_date - buy_trade.trade_date).days
                    }
                    completed_pairs.append(pair)
                    
                    # 更新剩余数量
                    sell_quantity -= pair_quantity
                    buy_item['remaining_quantity'] -= pair_quantity
                    buy_item['remaining_cost'] -= pair_cost
                    
                    # 如果买入记录已完全配对，从队列中移除
                    if buy_item['remaining_quantity'] <= 0:
                        buy_queue.pop(0)
        
        return completed_pairs
    
    @classmethod
    def get_profit_distribution_data(cls, profit_configs: List) -> Dict:
        """
        根据配置的收益区间计算收益分布
        """
        completed_pairs = cls.analyze_completed_trades()
        
        if not completed_pairs:
            return {
                'total_trades': 0,
                'distribution': [],
                'summary': {
                    'total_profit': 0,
                    'average_profit_rate': 0,
                    'win_rate': 0
                }
            }
        
        # 初始化分布统计
        distribution = []
        for config in profit_configs:
            distribution.append({
                'range_name': config.range_name,
                'min_rate': config.min_profit_rate,
                'max_rate': config.max_profit_rate,
                'count': 0,
                'percentage': 0,
                'total_profit': 0
            })
        
        # 统计每个交易对属于哪个区间
        total_trades = len(completed_pairs)
        total_profit = 0
        winning_trades = 0
        
        for pair in completed_pairs:
            profit_rate = pair['profit_rate']
            total_profit += pair['profit']
            
            if pair['profit'] > 0:
                winning_trades += 1
            
            # 找到对应的区间
            for dist_item in distribution:
                min_rate = dist_item['min_rate']
                max_rate = dist_item['max_rate']
                
                # 检查是否在区间内
                in_range = True
                if min_rate is not None and profit_rate < min_rate:
                    in_range = False
                if max_rate is not None and profit_rate >= max_rate:
                    in_range = False
                
                if in_range:
                    dist_item['count'] += 1
                    dist_item['total_profit'] += pair['profit']
                    break
        
        # 计算百分比
        for dist_item in distribution:
            if total_trades > 0:
                dist_item['percentage'] = (dist_item['count'] / total_trades) * 100
        
        # 计算汇总统计
        average_profit_rate = sum(pair['profit_rate'] for pair in completed_pairs) / total_trades if total_trades > 0 else 0
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'distribution': distribution,
            'summary': {
                'total_profit': total_profit,
                'average_profit_rate': average_profit_rate,
                'win_rate': win_rate
            },
            'completed_pairs': completed_pairs  # 用于调试和详细分析
        }
    
    @classmethod
    def get_current_holdings_summary(cls) -> Dict:
        """获取当前持仓汇总"""
        trades_by_stock = cls._group_trades_by_stock()
        current_holdings = {}
        
        for stock_code, trades in trades_by_stock.items():
            total_buy_quantity = 0
            total_sell_quantity = 0
            total_cost = 0
            
            for trade in trades:
                if trade.trade_type == 'buy':
                    total_buy_quantity += trade.quantity
                    total_cost += trade.quantity * trade.price
                elif trade.trade_type == 'sell':
                    total_sell_quantity += trade.quantity
            
            current_quantity = total_buy_quantity - total_sell_quantity
            
            if current_quantity > 0:
                average_cost = total_cost / total_buy_quantity if total_buy_quantity > 0 else 0
                current_holdings[stock_code] = {
                    'quantity': current_quantity,
                    'average_cost': average_cost,
                    'total_cost': current_quantity * average_cost
                }
        
        return current_holdings