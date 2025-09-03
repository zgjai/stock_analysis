"""
统计分析服务
"""
import io
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from collections import defaultdict
from sqlalchemy import func, and_, or_, desc, asc, extract
from extensions import db
from models.trade_record import TradeRecord
from models.stock_price import StockPrice
from models.profit_distribution_config import ProfitDistributionConfig
from services.base_service import BaseService
from services.trade_pair_analyzer import TradePairAnalyzer
from error_handlers import ValidationError, DatabaseError


class AnalyticsService(BaseService):
    """统计分析服务"""
    
    @classmethod
    def get_overall_statistics(cls) -> Dict[str, Any]:
        """获取总体收益统计概览
        
        Requirements: 1.1, 1.2, 1.3, 1.4, 5.1, 5.2
        - 显示总体收益概览
        - 显示已清仓收益、持仓浮盈浮亏、总收益率
        - 新增：已清仓收益和当前持仓收益的独立显示
        """
        try:
            # 获取所有交易记录
            trades = TradeRecord.query.filter_by(is_corrected=False).all()
            
            # 计算持仓情况
            holdings = cls._calculate_current_holdings(trades)
            
            # 计算已清仓收益（按股票分组计算完整买卖周期的收益）
            realized_profit = cls._calculate_realized_profit(trades)
            
            # 计算当前持仓收益（结合最新价格计算浮盈浮亏）
            current_holdings_profit = cls._calculate_current_holdings_profit(holdings)
            
            # 保持向后兼容性的旧字段
            closed_profit = cls._calculate_closed_positions_profit(trades)
            floating_profit = cls._calculate_floating_profit(holdings)
            
            # 计算总投入资金
            total_investment = cls._calculate_total_investment(trades)
            
            # 计算总收益率（以小数形式存储，前端显示时转换为百分比）
            total_profit = realized_profit + current_holdings_profit
            total_return_rate = (total_profit / total_investment) if total_investment > 0 else 0
            
            # 统计交易次数
            buy_count = len([t for t in trades if t.trade_type == 'buy'])
            sell_count = len([t for t in trades if t.trade_type == 'sell'])
            
            # 计算成功率（统一使用百分比形式）
            success_rate = cls._calculate_success_rate(trades)
            
            return {
                'total_investment': float(total_investment),
                # 新的准确收益指标
                'realized_profit': float(realized_profit),  # 已实现收益（包括分批止盈）
                'current_holdings_profit': float(current_holdings_profit),  # 当前持仓收益
                # 保持向后兼容性（旧字段）
                'closed_profit': float(realized_profit),  # 使用新的已实现收益
                'holding_profit': float(current_holdings_profit),  # 持仓浮盈浮亏
                'total_profit': float(total_profit),
                'total_return_rate': float(total_return_rate),  # 小数形式（如0.02表示2%）
                'current_holdings_count': len(holdings),
                'total_buy_count': buy_count,
                'total_sell_count': sell_count,
                'success_rate': float(success_rate),  # 百分比形式（如41.46表示41.46%）
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            raise DatabaseError(f"获取总体统计失败: {str(e)}")
    
    @classmethod
    def get_profit_distribution(cls, use_trade_pairs: bool = True) -> Dict[str, Any]:
        """获取收益分布区间分析
        
        Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
        - 分析已完成的交易配对（而非单个股票）
        - 将每个买入-卖出周期视为单独的交易
        - 显示每个收益区间的数量和百分比
        - 使用可配置的收益区间边界
        - 独立处理每个完整的买入-卖出周期
        """
        try:
            # 获取活跃的收益分布配置
            profit_configs = ProfitDistributionConfig.get_active_configs()
            
            if not profit_configs:
                # 如果没有配置，创建默认配置
                ProfitDistributionConfig.create_default_configs()
                profit_configs = ProfitDistributionConfig.get_active_configs()
            
            if use_trade_pairs:
                # 使用新的交易配对分析逻辑
                return TradePairAnalyzer.get_profit_distribution_data(profit_configs)
            else:
                # 保持向后兼容的旧逻辑（基于股票）
                return cls._get_legacy_profit_distribution(profit_configs)
        except Exception as e:
            raise DatabaseError(f"获取收益分布失败: {str(e)}")
    
    @classmethod
    def _get_legacy_profit_distribution(cls, profit_configs: List) -> Dict[str, Any]:
        """旧版收益分布分析（基于股票，保持向后兼容）"""
        # 获取所有交易记录
        trades = TradeRecord.query.filter_by(is_corrected=False).all()
        
        # 计算持仓情况
        holdings = cls._calculate_current_holdings(trades)
        
        # 计算已清仓股票的收益情况
        closed_positions = cls._calculate_closed_positions_detail(trades)
        
        # 初始化分布统计
        distribution = []
        for config in profit_configs:
            distribution.append({
                'range_name': config.range_name,
                'min_rate': config.min_profit_rate,
                'max_rate': config.max_profit_rate,
                'count': 0,
                'percentage': 0,
                'total_profit': 0,
                'stocks': []
            })
        
        # 统计持仓股票分布
        for stock_code, holding in holdings.items():
            profit_rate = holding['profit_rate']
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
                    dist_item['total_profit'] += holding['profit_amount']
                    dist_item['stocks'].append({
                        'stock_code': stock_code,
                        'stock_name': holding['stock_name'],
                        'profit_rate': profit_rate,
                        'profit_amount': holding['profit_amount'],
                        'status': 'holding'
                    })
                    break
        
        # 统计已清仓股票分布
        for position in closed_positions:
            profit_rate = position['profit_rate']
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
                    dist_item['total_profit'] += position['profit_amount']
                    dist_item['stocks'].append({
                        'stock_code': position['stock_code'],
                        'stock_name': position['stock_name'],
                        'profit_rate': profit_rate,
                        'profit_amount': position['profit_amount'],
                        'status': 'closed'
                    })
                    break
        
        # 计算总股票数和百分比
        total_stocks = sum(dist_item['count'] for dist_item in distribution)
        for dist_item in distribution:
            dist_item['percentage'] = (dist_item['count'] / total_stocks * 100) if total_stocks > 0 else 0
        
        return {
            'total_trades': total_stocks,
            'distribution': distribution,
            'summary': {
                'total_profit': sum(dist_item['total_profit'] for dist_item in distribution),
                'average_profit_rate': 0,  # 需要重新计算
                'win_rate': 0  # 需要重新计算
            },
            'holding_stocks': len(holdings),
            'closed_stocks': len(closed_positions)
        }
    
    @classmethod
    def get_monthly_statistics(cls, year: int = None) -> Dict[str, Any]:
        """获取月度交易统计和收益率
        
        Requirements: 5.1, 5.2, 5.3, 5.4
        - 计算并显示月度收益率
        - 使用每月的已实现收益和损失
        - 处理无数据月份，显示适当的指示器
        - 显示格式正确的百分比值
        """
        try:
            if year is None:
                year = datetime.now().year
            
            # 验证年份范围
            current_year = datetime.now().year
            if year < 2000 or year > current_year + 1:
                raise ValidationError(f"年份必须在2000到{current_year + 1}之间")
            
            # 获取指定年份的交易记录
            trades = TradeRecord.query.filter(
                and_(
                    extract('year', TradeRecord.trade_date) == year,
                    TradeRecord.is_corrected == False
                )
            ).all()
            
            # 按月份分组统计
            monthly_stats = {}
            for month in range(1, 13):
                monthly_stats[month] = {
                    'month': month,
                    'month_name': f"{year}-{month:02d}",
                    'buy_count': 0,
                    'sell_count': 0,
                    'total_trades': 0,
                    'buy_amount': 0,
                    'sell_amount': 0,
                    'profit_amount': 0,
                    'profit_rate': None,  # 月度收益率，None表示无数据
                    'success_count': 0,
                    'success_rate': 0,
                    'stocks': set(),
                    'has_data': False  # 标记是否有交易数据
                }
            
            # 统计每月交易数据
            for trade in trades:
                month = trade.trade_date.month
                monthly_stats[month]['stocks'].add(trade.stock_code)
                monthly_stats[month]['has_data'] = True
                
                if trade.trade_type == 'buy':
                    monthly_stats[month]['buy_count'] += 1
                    monthly_stats[month]['buy_amount'] += float(trade.price * trade.quantity)
                elif trade.trade_type == 'sell':
                    monthly_stats[month]['sell_count'] += 1
                    monthly_stats[month]['sell_amount'] += float(trade.price * trade.quantity)
                
                monthly_stats[month]['total_trades'] += 1
            
            # 计算每月的收益率和成功率
            for month, stats in monthly_stats.items():
                if stats['has_data']:
                    # 计算当月已完成交易的收益情况
                    month_profit, month_success_trades, month_cost = cls._calculate_monthly_realized_profit_and_success(
                        trades, month, year
                    )
                    stats['profit_amount'] = month_profit
                    
                    # 计算月度收益率：基于该月已完成交易的成本
                    if month_cost > 0:
                        stats['profit_rate'] = month_profit / month_cost
                    else:
                        stats['profit_rate'] = 0 if month_profit == 0 else None
                    
                    # 修正成功率计算：计算该月盈利股票数占该月交易股票数的比例
                    month_success_stocks = cls._calculate_monthly_success_stocks(trades, month, year)
                    stats['success_count'] = month_success_stocks
                    stats['success_rate'] = (month_success_stocks / len(stats['stocks']) * 100) if len(stats['stocks']) > 0 else 0
                else:
                    # 无数据月份保持默认值
                    stats['profit_rate'] = None
                
                stats['unique_stocks'] = len(stats['stocks'])
                stats['stocks'] = list(stats['stocks'])  # 转换为列表以便JSON序列化
            
            # 计算年度汇总
            valid_months = [stats for stats in monthly_stats.values() if stats['has_data']]
            year_summary = {
                'year': year,
                'total_buy_count': sum(stats['buy_count'] for stats in monthly_stats.values()),
                'total_sell_count': sum(stats['sell_count'] for stats in monthly_stats.values()),
                'total_trades': sum(stats['total_trades'] for stats in monthly_stats.values()),
                'total_buy_amount': sum(stats['buy_amount'] for stats in monthly_stats.values()),
                'total_sell_amount': sum(stats['sell_amount'] for stats in monthly_stats.values()),
                'total_profit': sum(stats['profit_amount'] for stats in monthly_stats.values()),
                'average_success_rate': sum(stats['success_rate'] for stats in valid_months) / len(valid_months) if valid_months else 0,
                'months_with_data': len(valid_months),
                'average_monthly_return': sum(stats['profit_rate'] for stats in valid_months if stats['profit_rate'] is not None) / len([s for s in valid_months if s['profit_rate'] is not None]) if any(s['profit_rate'] is not None for s in valid_months) else 0
            }
            
            return {
                'year_summary': year_summary,
                'monthly_data': list(monthly_stats.values())
            }
        except ValidationError as e:
            raise e
        except Exception as e:
            raise DatabaseError(f"获取月度统计失败: {str(e)}")
    
    @classmethod
    def export_statistics_to_excel(cls) -> bytes:
        """导出统计数据到Excel格式
        
        Requirements: 5.5
        - 支持导出Excel格式的统计报表
        """
        try:
            import pandas as pd
            from io import BytesIO
            
            # 创建Excel写入器
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # 1. 总体统计表
                overall_stats = cls.get_overall_statistics()
                overall_df = pd.DataFrame([overall_stats])
                overall_df.to_excel(writer, sheet_name='总体统计', index=False)
                
                # 2. 收益分布表
                profit_dist = cls.get_profit_distribution()
                profit_ranges_data = []
                for range_info in profit_dist['profit_ranges']:
                    profit_ranges_data.append({
                        '收益区间': range_info['range'],
                        '股票数量': range_info['count'],
                        '占比(%)': round(range_info['percentage'], 2)
                    })
                profit_df = pd.DataFrame(profit_ranges_data)
                profit_df.to_excel(writer, sheet_name='收益分布', index=False)
                
                # 3. 收益分布详细股票列表
                detailed_stocks = []
                for range_info in profit_dist['profit_ranges']:
                    for stock in range_info['stocks']:
                        detailed_stocks.append({
                            '收益区间': range_info['range'],
                            '股票代码': stock['stock_code'],
                            '股票名称': stock['stock_name'],
                            '收益率(%)': round(stock['profit_rate'] * 100, 2),
                            '收益金额': round(stock['profit_amount'], 2),
                            '状态': '持仓中' if stock['status'] == 'holding' else '已清仓'
                        })
                detailed_df = pd.DataFrame(detailed_stocks)
                detailed_df.to_excel(writer, sheet_name='收益详情', index=False)
                
                # 4. 月度统计表
                current_year = datetime.now().year
                monthly_stats = cls.get_monthly_statistics(current_year)
                monthly_data = []
                for month_data in monthly_stats['monthly_data']:
                    monthly_data.append({
                        '月份': month_data['month_name'],
                        '买入次数': month_data['buy_count'],
                        '卖出次数': month_data['sell_count'],
                        '总交易次数': month_data['total_trades'],
                        '买入金额': round(month_data['buy_amount'], 2),
                        '卖出金额': round(month_data['sell_amount'], 2),
                        '收益金额': round(month_data['profit_amount'], 2),
                        '涉及股票数': month_data['unique_stocks'],
                        '成功率(%)': round(month_data['success_rate'], 2)
                    })
                monthly_df = pd.DataFrame(monthly_data)
                monthly_df.to_excel(writer, sheet_name='月度统计', index=False)
                
                # 5. 持仓明细表
                trades = TradeRecord.query.filter_by(is_corrected=False).all()
                holdings = cls._calculate_current_holdings(trades)
                holdings_data = []
                for stock_code, holding in holdings.items():
                    holdings_data.append({
                        '股票代码': stock_code,
                        '股票名称': holding['stock_name'],
                        '持仓数量': holding['quantity'],
                        '平均成本': round(holding['avg_cost'], 2),
                        '当前价格': round(holding['current_price'], 2),
                        '持仓市值': round(holding['market_value'], 2),
                        '持仓成本': round(holding['total_cost'], 2),
                        '浮盈浮亏': round(holding['profit_amount'], 2),
                        '收益率(%)': round(holding['profit_rate'] * 100, 2)
                    })
                holdings_df = pd.DataFrame(holdings_data)
                holdings_df.to_excel(writer, sheet_name='当前持仓', index=False)
            
            output.seek(0)
            return output.getvalue()
        except ImportError:
            raise ValidationError("缺少pandas依赖，无法导出Excel文件")
        except Exception as e:
            raise DatabaseError(f"导出Excel失败: {str(e)}")
    
    @classmethod
    def _calculate_current_holdings(cls, trades: List[TradeRecord]) -> Dict[str, Dict[str, Any]]:
        """计算当前持仓情况（使用FIFO方法确保成本计算一致性）"""
        stock_trades = defaultdict(list)
        
        # 按股票分组交易记录
        for trade in trades:
            stock_trades[trade.stock_code].append(trade)
        
        holdings = {}
        
        for stock_code, stock_trade_list in stock_trades.items():
            # 按时间排序
            stock_trade_list.sort(key=lambda x: x.trade_date)
            
            # 使用FIFO方法计算剩余持仓和成本
            holding_info = cls._calculate_fifo_holdings(stock_trade_list)
            
            if holding_info['quantity'] > 0:
                # 获取当前价格
                latest_price = StockPrice.get_latest_price(stock_code)
                if latest_price:
                    current_price = float(latest_price.current_price)
                else:
                    current_price = holding_info['avg_cost']  # 如果没有价格数据，使用成本价
                
                market_value = current_price * holding_info['quantity']
                profit_amount = market_value - holding_info['total_cost']
                profit_rate = profit_amount / holding_info['total_cost'] if holding_info['total_cost'] > 0 else 0
                
                holdings[stock_code] = {
                    'stock_name': holding_info['stock_name'],
                    'quantity': holding_info['quantity'],
                    'total_cost': holding_info['total_cost'],
                    'avg_cost': holding_info['avg_cost'],
                    'current_price': current_price,
                    'market_value': market_value,
                    'profit_amount': profit_amount,
                    'profit_rate': profit_rate
                }
        
        return holdings
    
    @classmethod
    def _calculate_fifo_holdings(cls, stock_trades: List[TradeRecord]) -> Dict[str, Any]:
        """使用FIFO方法计算单只股票的剩余持仓"""
        buy_queue = []  # 买入队列
        stock_name = stock_trades[0].stock_name if stock_trades else ''
        
        for trade in stock_trades:
            if trade.trade_type == 'buy':
                buy_queue.append({
                    'quantity': trade.quantity,
                    'price': float(trade.price),
                    'remaining': trade.quantity
                })
            elif trade.trade_type == 'sell':
                sell_quantity = trade.quantity
                
                # 从买入队列中匹配卖出
                while sell_quantity > 0 and buy_queue:
                    buy_item = buy_queue[0]
                    
                    # 计算本次匹配的数量
                    match_quantity = min(sell_quantity, buy_item['remaining'])
                    
                    # 更新数量
                    buy_item['remaining'] -= match_quantity
                    sell_quantity -= match_quantity
                    
                    # 如果买入项目已完全匹配，从队列中移除
                    if buy_item['remaining'] <= 0:
                        buy_queue.pop(0)
        
        # 计算剩余持仓
        total_quantity = sum(item['remaining'] for item in buy_queue)
        total_cost = sum(item['remaining'] * item['price'] for item in buy_queue)
        avg_cost = total_cost / total_quantity if total_quantity > 0 else 0
        
        return {
            'stock_name': stock_name,
            'quantity': total_quantity,
            'total_cost': total_cost,
            'avg_cost': avg_cost
        }
    
    @classmethod
    def _calculate_closed_positions_profit(cls, trades: List[TradeRecord]) -> float:
        """计算已清仓股票的总收益"""
        stock_trades = defaultdict(list)
        
        # 按股票分组交易记录
        for trade in trades:
            stock_trades[trade.stock_code].append(trade)
        
        total_profit = 0
        
        for stock_code, stock_trade_list in stock_trades.items():
            # 按时间排序
            stock_trade_list.sort(key=lambda x: x.trade_date)
            
            # 计算该股票的收益
            position = 0  # 当前持仓
            total_cost = 0  # 总成本
            total_revenue = 0  # 总收入
            
            for trade in stock_trade_list:
                if trade.trade_type == 'buy':
                    position += trade.quantity
                    total_cost += float(trade.price * trade.quantity)
                elif trade.trade_type == 'sell':
                    position -= trade.quantity
                    total_revenue += float(trade.price * trade.quantity)
            
            # 如果已清仓（持仓为0），计算收益
            if position == 0:
                total_profit += (total_revenue - total_cost)
        
        return total_profit
    
    @classmethod
    def _calculate_floating_profit(cls, holdings: Dict[str, Dict[str, Any]]) -> float:
        """计算持仓浮盈浮亏"""
        return sum(holding['profit_amount'] for holding in holdings.values())
    
    @classmethod
    def _calculate_total_investment(cls, trades: List[TradeRecord]) -> float:
        """计算总投入资金"""
        total_buy_amount = sum(
            float(trade.price * trade.quantity) 
            for trade in trades 
            if trade.trade_type == 'buy'
        )
        return total_buy_amount
    
    @classmethod
    def _calculate_success_rate(cls, trades: List[TradeRecord]) -> float:
        """计算成功率（盈利的已清仓股票比例）"""
        stock_trades = defaultdict(list)
        
        # 按股票分组交易记录
        for trade in trades:
            stock_trades[trade.stock_code].append(trade)
        
        closed_stocks = 0
        profitable_stocks = 0
        
        for stock_code, stock_trade_list in stock_trades.items():
            # 按时间排序
            stock_trade_list.sort(key=lambda x: x.trade_date)
            
            # 计算该股票的持仓和收益
            position = 0
            total_cost = 0
            total_revenue = 0
            
            for trade in stock_trade_list:
                if trade.trade_type == 'buy':
                    position += trade.quantity
                    total_cost += float(trade.price * trade.quantity)
                elif trade.trade_type == 'sell':
                    position -= trade.quantity
                    total_revenue += float(trade.price * trade.quantity)
            
            # 如果已清仓
            if position == 0:
                closed_stocks += 1
                if total_revenue > total_cost:
                    profitable_stocks += 1
        
        return (profitable_stocks / closed_stocks * 100) if closed_stocks > 0 else 0
    
    @classmethod
    def _calculate_closed_positions_detail(cls, trades: List[TradeRecord]) -> List[Dict[str, Any]]:
        """计算已清仓股票的详细收益情况"""
        stock_trades = defaultdict(list)
        
        # 按股票分组交易记录
        for trade in trades:
            stock_trades[trade.stock_code].append(trade)
        
        closed_positions = []
        
        for stock_code, stock_trade_list in stock_trades.items():
            # 按时间排序
            stock_trade_list.sort(key=lambda x: x.trade_date)
            
            # 计算该股票的收益
            position = 0
            total_cost = 0
            total_revenue = 0
            stock_name = stock_trade_list[0].stock_name
            
            for trade in stock_trade_list:
                if trade.trade_type == 'buy':
                    position += trade.quantity
                    total_cost += float(trade.price * trade.quantity)
                elif trade.trade_type == 'sell':
                    position -= trade.quantity
                    total_revenue += float(trade.price * trade.quantity)
            
            # 如果已清仓
            if position == 0:
                profit_amount = total_revenue - total_cost
                profit_rate = profit_amount / total_cost if total_cost > 0 else 0
                
                closed_positions.append({
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'total_cost': total_cost,
                    'total_revenue': total_revenue,
                    'profit_amount': profit_amount,
                    'profit_rate': profit_rate
                })
        
        return closed_positions
    
    @classmethod
    def _calculate_realized_profit(cls, trades: List[TradeRecord]) -> float:
        """计算已实现收益（使用FIFO方法匹配所有买卖交易）
        
        Requirements: 1.1, 1.3
        - 汇总所有已完成的交易（买入-卖出配对）
        - 包括分批止盈的收益
        """
        stock_trades = defaultdict(list)
        
        # 按股票分组交易记录
        for trade in trades:
            stock_trades[trade.stock_code].append(trade)
        
        total_realized_profit = 0
        
        for stock_code, stock_trade_list in stock_trades.items():
            # 按时间排序
            stock_trade_list.sort(key=lambda x: x.trade_date)
            
            # 使用FIFO方法计算已实现收益
            realized_profit = cls._calculate_fifo_realized_profit(stock_trade_list)
            total_realized_profit += realized_profit
        
        return total_realized_profit
    
    @classmethod
    def _calculate_fifo_realized_profit(cls, stock_trades: List[TradeRecord]) -> float:
        """使用FIFO方法计算单只股票的已实现收益"""
        buy_queue = []  # 买入队列：[{'quantity': int, 'price': float, 'remaining': int}]
        realized_profit = 0
        
        for trade in stock_trades:
            if trade.trade_type == 'buy':
                buy_queue.append({
                    'quantity': trade.quantity,
                    'price': float(trade.price),
                    'remaining': trade.quantity
                })
            elif trade.trade_type == 'sell':
                sell_quantity = trade.quantity
                sell_price = float(trade.price)
                
                # 从买入队列中匹配卖出
                while sell_quantity > 0 and buy_queue:
                    buy_item = buy_queue[0]
                    
                    # 计算本次匹配的数量
                    match_quantity = min(sell_quantity, buy_item['remaining'])
                    
                    # 计算本次匹配的收益
                    cost = match_quantity * buy_item['price']
                    revenue = match_quantity * sell_price
                    profit = revenue - cost
                    realized_profit += profit
                    
                    # 更新数量
                    buy_item['remaining'] -= match_quantity
                    sell_quantity -= match_quantity
                    
                    # 如果买入项目已完全匹配，从队列中移除
                    if buy_item['remaining'] <= 0:
                        buy_queue.pop(0)
        
        return realized_profit
    
    @classmethod
    def _calculate_current_holdings_profit(cls, holdings: Dict[str, Dict[str, Any]]) -> float:
        """计算当前持仓收益（结合最新价格计算浮盈浮亏）
        
        Requirements: 1.2, 1.4
        - 使用当前市场价格减去所有持仓的成本基础
        """
        return sum(holding['profit_amount'] for holding in holdings.values())
    
    @classmethod
    def _calculate_monthly_realized_profit_and_success(cls, trades: List[TradeRecord], 
                                                     month: int, year: int) -> Tuple[float, int, float]:
        """计算指定月份的总收益、成功股票数和投入成本
        
        Requirements: 5.2
        - 按买入时间归属收益：该月买入的股票产生的收益都算作该月收益
        - 包括已实现收益和持仓浮盈浮亏
        """
        from calendar import monthrange
        
        # 计算该月的日期范围
        month_start = datetime(year, month, 1)
        last_day = monthrange(year, month)[1]
        month_end = datetime(year, month, last_day, 23, 59, 59)
        
        # 获取该月买入的交易产生的收益（包括已实现和未实现）
        month_profit = 0
        success_count = 0
        month_cost = 0
        
        # 按股票分组所有交易记录
        stock_trades = defaultdict(list)
        for trade in trades:
            stock_trades[trade.stock_code].append(trade)
        
        # 分析每只股票，计算该月买入产生的总收益
        for stock_code, stock_trade_list in stock_trades.items():
            # 按时间排序
            stock_trade_list.sort(key=lambda x: x.trade_date)
            
            # 计算该月买入产生的总收益（已实现 + 持仓浮盈浮亏）
            monthly_total_profits = cls._get_monthly_buy_total_profits(
                stock_trade_list, month_start, month_end
            )
            
            for buy_profit in monthly_total_profits:
                profit = buy_profit['total_profit']
                cost = buy_profit['cost']
                
                month_profit += profit
                month_cost += cost
                
                if profit > 0:
                    success_count += 1
        
        return month_profit, success_count, month_cost
    
    @classmethod
    def _calculate_monthly_success_stocks(cls, trades: List[TradeRecord], month: int, year: int) -> int:
        """计算指定月份成功（盈利）的股票数量
        
        Returns:
            int: 该月有交易且整体盈利的股票数量
        """
        from calendar import monthrange
        
        # 计算该月的日期范围
        month_start = datetime(year, month, 1)
        last_day = monthrange(year, month)[1]
        month_end = datetime(year, month, last_day, 23, 59, 59)
        
        # 获取该月有交易的股票
        monthly_stocks = set()
        for trade in trades:
            if month_start <= trade.trade_date <= month_end:
                monthly_stocks.add(trade.stock_code)
        
        # 按股票分组所有交易记录
        stock_trades = defaultdict(list)
        for trade in trades:
            stock_trades[trade.stock_code].append(trade)
        
        success_stocks = 0
        
        # 对每只该月有交易的股票，计算其总体收益情况
        for stock_code in monthly_stocks:
            if stock_code in stock_trades:
                stock_trade_list = stock_trades[stock_code]
                stock_trade_list.sort(key=lambda x: x.trade_date)
                
                # 计算该股票的总体收益（已实现 + 持仓浮盈浮亏）
                total_profit = cls._calculate_stock_total_profit(stock_trade_list)
                
                if total_profit > 0:
                    success_stocks += 1
        
        return success_stocks
    
    @classmethod
    def _calculate_stock_total_profit(cls, stock_trades: List[TradeRecord]) -> float:
        """计算单只股票的总体收益（已实现收益 + 持仓浮盈浮亏）"""
        from models.stock_price import StockPrice
        
        # 计算已实现收益
        realized_profit = cls._calculate_fifo_realized_profit(stock_trades)
        
        # 计算持仓浮盈浮亏
        holding_info = cls._calculate_fifo_holdings(stock_trades)
        floating_profit = 0
        
        if holding_info['quantity'] > 0:
            stock_code = stock_trades[0].stock_code
            latest_price = StockPrice.get_latest_price(stock_code)
            if latest_price:
                current_price = float(latest_price.current_price)
                market_value = current_price * holding_info['quantity']
                floating_profit = market_value - holding_info['total_cost']
            # 如果没有价格数据，浮盈浮亏为0（按成本价计算）
        
        return realized_profit + floating_profit
    
    @classmethod
    def _get_monthly_buy_total_profits(cls, stock_trades: List[TradeRecord], 
                                     month_start: datetime, month_end: datetime) -> List[Dict]:
        """获取指定月份买入的股票产生的总收益（已实现收益 + 持仓浮盈浮亏）"""
        from models.stock_price import StockPrice
        
        monthly_profits = []
        
        # 使用FIFO方法匹配买入和卖出
        buy_queue = []  # 买入队列
        stock_code = stock_trades[0].stock_code if stock_trades else None
        
        # 获取当前价格
        current_price = None
        if stock_code:
            latest_price = StockPrice.get_latest_price(stock_code)
            if latest_price:
                current_price = float(latest_price.current_price)
        
        for trade in stock_trades:
            if trade.trade_type == 'buy':
                buy_queue.append({
                    'trade': trade,
                    'remaining_quantity': trade.quantity,
                    'unit_cost': float(trade.price),
                    'is_monthly_buy': month_start <= trade.trade_date <= month_end  # 标记是否为该月买入
                })
            elif trade.trade_type == 'sell':
                sell_quantity = trade.quantity
                sell_price = float(trade.price)
                sell_date = trade.trade_date
                
                # 从买入队列中匹配
                while sell_quantity > 0 and buy_queue:
                    buy_item = buy_queue[0]
                    buy_trade = buy_item['trade']
                    
                    # 计算本次匹配的数量
                    match_quantity = min(sell_quantity, buy_item['remaining_quantity'])
                    
                    # 如果买入发生在指定月份内，记录该交易的已实现收益
                    if buy_item['is_monthly_buy']:
                        cost = match_quantity * buy_item['unit_cost']
                        revenue = match_quantity * sell_price
                        realized_profit = revenue - cost
                        
                        monthly_profits.append({
                            'type': 'realized',
                            'buy_date': buy_trade.trade_date,
                            'sell_date': sell_date,
                            'quantity': match_quantity,
                            'buy_price': buy_item['unit_cost'],
                            'sell_price': sell_price,
                            'cost': cost,
                            'revenue': revenue,
                            'total_profit': realized_profit
                        })
                    
                    # 更新数量
                    buy_item['remaining_quantity'] -= match_quantity
                    sell_quantity -= match_quantity
                    
                    # 如果买入项目已完全匹配，从队列中移除
                    if buy_item['remaining_quantity'] <= 0:
                        buy_queue.pop(0)
        
        # 处理剩余持仓（该月买入但未卖出的部分）
        if current_price is not None:
            for buy_item in buy_queue:
                if buy_item['is_monthly_buy'] and buy_item['remaining_quantity'] > 0:
                    cost = buy_item['remaining_quantity'] * buy_item['unit_cost']
                    market_value = buy_item['remaining_quantity'] * current_price
                    unrealized_profit = market_value - cost
                    
                    monthly_profits.append({
                        'type': 'unrealized',
                        'buy_date': buy_item['trade'].trade_date,
                        'quantity': buy_item['remaining_quantity'],
                        'buy_price': buy_item['unit_cost'],
                        'current_price': current_price,
                        'cost': cost,
                        'market_value': market_value,
                        'total_profit': unrealized_profit
                    })
        
        return monthly_profits
    
    @classmethod
    def _get_monthly_buy_based_profits(cls, stock_trades: List[TradeRecord], 
                                     month_start: datetime, month_end: datetime) -> List[Dict]:
        """获取指定月份买入的股票产生的已实现收益（保留向后兼容）"""
        buy_based_profits = []
        
        # 使用FIFO方法匹配买入和卖出
        buy_queue = []  # 买入队列
        
        for trade in stock_trades:
            if trade.trade_type == 'buy':
                buy_queue.append({
                    'trade': trade,
                    'remaining_quantity': trade.quantity,
                    'unit_cost': float(trade.price),
                    'is_monthly_buy': month_start <= trade.trade_date <= month_end  # 标记是否为该月买入
                })
            elif trade.trade_type == 'sell':
                sell_quantity = trade.quantity
                sell_price = float(trade.price)
                sell_date = trade.trade_date
                
                # 从买入队列中匹配
                while sell_quantity > 0 and buy_queue:
                    buy_item = buy_queue[0]
                    buy_trade = buy_item['trade']
                    
                    # 计算本次匹配的数量
                    match_quantity = min(sell_quantity, buy_item['remaining_quantity'])
                    
                    # 如果买入发生在指定月份内，记录该交易的收益
                    if buy_item['is_monthly_buy']:
                        cost = match_quantity * buy_item['unit_cost']
                        revenue = match_quantity * sell_price
                        profit = revenue - cost
                        
                        buy_based_profits.append({
                            'buy_date': buy_trade.trade_date,
                            'sell_date': sell_date,
                            'quantity': match_quantity,
                            'buy_price': buy_item['unit_cost'],
                            'sell_price': sell_price,
                            'cost': cost,
                            'revenue': revenue,
                            'profit': profit
                        })
                    
                    # 更新数量
                    buy_item['remaining_quantity'] -= match_quantity
                    sell_quantity -= match_quantity
                    
                    # 如果买入项目已完全匹配，从队列中移除
                    if buy_item['remaining_quantity'] <= 0:
                        buy_queue.pop(0)
        
        return buy_based_profits