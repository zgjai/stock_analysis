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
from services.base_service import BaseService
from error_handlers import ValidationError, DatabaseError


class AnalyticsService(BaseService):
    """统计分析服务"""
    
    @classmethod
    def get_overall_statistics(cls) -> Dict[str, Any]:
        """获取总体收益统计概览
        
        Requirements: 5.1, 5.2
        - 显示总体收益概览
        - 显示已清仓收益、持仓浮盈浮亏、总收益率
        """
        try:
            # 获取所有交易记录
            trades = TradeRecord.query.filter_by(is_corrected=False).all()
            
            # 计算持仓情况
            holdings = cls._calculate_current_holdings(trades)
            
            # 计算已清仓收益
            closed_profit = cls._calculate_closed_positions_profit(trades)
            
            # 计算持仓浮盈浮亏
            floating_profit = cls._calculate_floating_profit(holdings)
            
            # 计算总投入资金
            total_investment = cls._calculate_total_investment(trades)
            
            # 计算总收益率
            total_profit = closed_profit + floating_profit
            total_return_rate = (total_profit / total_investment * 100) if total_investment > 0 else 0
            
            # 统计交易次数
            buy_count = len([t for t in trades if t.trade_type == 'buy'])
            sell_count = len([t for t in trades if t.trade_type == 'sell'])
            
            # 计算成功率（盈利的已清仓股票比例）
            success_rate = cls._calculate_success_rate(trades)
            
            return {
                'total_investment': float(total_investment),
                'closed_profit': float(closed_profit),
                'floating_profit': float(floating_profit),
                'total_profit': float(total_profit),
                'total_return_rate': float(total_return_rate),
                'current_holdings_count': len(holdings),
                'total_buy_count': buy_count,
                'total_sell_count': sell_count,
                'success_rate': float(success_rate),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            raise DatabaseError(f"获取总体统计失败: {str(e)}")
    
    @classmethod
    def get_profit_distribution(cls) -> Dict[str, Any]:
        """获取收益分布区间分析
        
        Requirements: 5.3
        - 按盈亏区间显示股票分布情况
        """
        try:
            # 获取所有交易记录
            trades = TradeRecord.query.filter_by(is_corrected=False).all()
            
            # 计算持仓情况
            holdings = cls._calculate_current_holdings(trades)
            
            # 计算已清仓股票的收益情况
            closed_positions = cls._calculate_closed_positions_detail(trades)
            
            # 定义收益区间
            profit_ranges = [
                {'range': '< -20%', 'min': float('-inf'), 'max': -0.2, 'count': 0, 'stocks': []},
                {'range': '-20% ~ -10%', 'min': -0.2, 'max': -0.1, 'count': 0, 'stocks': []},
                {'range': '-10% ~ -5%', 'min': -0.1, 'max': -0.05, 'count': 0, 'stocks': []},
                {'range': '-5% ~ 0%', 'min': -0.05, 'max': 0, 'count': 0, 'stocks': []},
                {'range': '0% ~ 5%', 'min': 0, 'max': 0.05, 'count': 0, 'stocks': []},
                {'range': '5% ~ 10%', 'min': 0.05, 'max': 0.1, 'count': 0, 'stocks': []},
                {'range': '10% ~ 20%', 'min': 0.1, 'max': 0.2, 'count': 0, 'stocks': []},
                {'range': '20% ~ 50%', 'min': 0.2, 'max': 0.5, 'count': 0, 'stocks': []},
                {'range': '> 50%', 'min': 0.5, 'max': float('inf'), 'count': 0, 'stocks': []}
            ]
            
            # 统计持仓股票分布
            for stock_code, holding in holdings.items():
                profit_rate = holding['profit_rate']
                for range_info in profit_ranges:
                    if range_info['min'] <= profit_rate < range_info['max']:
                        range_info['count'] += 1
                        range_info['stocks'].append({
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
                for range_info in profit_ranges:
                    if range_info['min'] <= profit_rate < range_info['max']:
                        range_info['count'] += 1
                        range_info['stocks'].append({
                            'stock_code': position['stock_code'],
                            'stock_name': position['stock_name'],
                            'profit_rate': profit_rate,
                            'profit_amount': position['profit_amount'],
                            'status': 'closed'
                        })
                        break
            
            # 计算总股票数
            total_stocks = sum(range_info['count'] for range_info in profit_ranges)
            
            # 计算百分比
            for range_info in profit_ranges:
                range_info['percentage'] = (range_info['count'] / total_stocks * 100) if total_stocks > 0 else 0
            
            return {
                'profit_ranges': profit_ranges,
                'total_stocks': total_stocks,
                'holding_stocks': len(holdings),
                'closed_stocks': len(closed_positions)
            }
        except Exception as e:
            raise DatabaseError(f"获取收益分布失败: {str(e)}")
    
    @classmethod
    def get_monthly_statistics(cls, year: int = None) -> Dict[str, Any]:
        """获取月度交易统计和成功率
        
        Requirements: 5.4
        - 显示每月交易次数、收益情况和成功率
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
                    'success_count': 0,
                    'success_rate': 0,
                    'stocks': set()
                }
            
            # 统计每月交易数据
            for trade in trades:
                month = trade.trade_date.month
                monthly_stats[month]['stocks'].add(trade.stock_code)
                
                if trade.trade_type == 'buy':
                    monthly_stats[month]['buy_count'] += 1
                    monthly_stats[month]['buy_amount'] += float(trade.price * trade.quantity)
                elif trade.trade_type == 'sell':
                    monthly_stats[month]['sell_count'] += 1
                    monthly_stats[month]['sell_amount'] += float(trade.price * trade.quantity)
                
                monthly_stats[month]['total_trades'] += 1
            
            # 计算每月的收益和成功率
            for month, stats in monthly_stats.items():
                # 计算当月涉及的股票的收益情况
                month_profit, month_success = cls._calculate_monthly_profit_and_success(
                    trades, month, year
                )
                stats['profit_amount'] = month_profit
                stats['success_count'] = month_success
                stats['success_rate'] = (month_success / len(stats['stocks']) * 100) if len(stats['stocks']) > 0 else 0
                stats['unique_stocks'] = len(stats['stocks'])
                stats['stocks'] = list(stats['stocks'])  # 转换为列表以便JSON序列化
            
            # 计算年度汇总
            year_summary = {
                'year': year,
                'total_buy_count': sum(stats['buy_count'] for stats in monthly_stats.values()),
                'total_sell_count': sum(stats['sell_count'] for stats in monthly_stats.values()),
                'total_trades': sum(stats['total_trades'] for stats in monthly_stats.values()),
                'total_buy_amount': sum(stats['buy_amount'] for stats in monthly_stats.values()),
                'total_sell_amount': sum(stats['sell_amount'] for stats in monthly_stats.values()),
                'total_profit': sum(stats['profit_amount'] for stats in monthly_stats.values()),
                'average_success_rate': sum(stats['success_rate'] for stats in monthly_stats.values()) / 12
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
        """计算当前持仓情况"""
        holdings = defaultdict(lambda: {
            'stock_name': '',
            'quantity': 0,
            'total_cost': 0,
            'avg_cost': 0,
            'current_price': 0,
            'market_value': 0,
            'profit_amount': 0,
            'profit_rate': 0
        })
        
        # 计算每只股票的持仓
        for trade in trades:
            stock_code = trade.stock_code
            holdings[stock_code]['stock_name'] = trade.stock_name
            
            if trade.trade_type == 'buy':
                holdings[stock_code]['quantity'] += trade.quantity
                holdings[stock_code]['total_cost'] += float(trade.price * trade.quantity)
            elif trade.trade_type == 'sell':
                holdings[stock_code]['quantity'] -= trade.quantity
                # 按比例减少成本
                if holdings[stock_code]['quantity'] > 0:
                    cost_ratio = trade.quantity / (holdings[stock_code]['quantity'] + trade.quantity)
                    holdings[stock_code]['total_cost'] *= (1 - cost_ratio)
        
        # 移除已清仓的股票
        holdings = {k: v for k, v in holdings.items() if v['quantity'] > 0}
        
        # 计算平均成本和当前市值
        for stock_code, holding in holdings.items():
            if holding['quantity'] > 0:
                holding['avg_cost'] = holding['total_cost'] / holding['quantity']
                
                # 获取当前价格
                latest_price = StockPrice.get_latest_price(stock_code)
                if latest_price:
                    holding['current_price'] = float(latest_price.current_price)
                else:
                    holding['current_price'] = holding['avg_cost']  # 如果没有价格数据，使用成本价
                
                holding['market_value'] = holding['current_price'] * holding['quantity']
                holding['profit_amount'] = holding['market_value'] - holding['total_cost']
                holding['profit_rate'] = holding['profit_amount'] / holding['total_cost'] if holding['total_cost'] > 0 else 0
        
        return dict(holdings)
    
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
    def _calculate_monthly_profit_and_success(cls, trades: List[TradeRecord], 
                                            month: int, year: int) -> Tuple[float, int]:
        """计算指定月份的收益和成功股票数"""
        # 获取该月涉及的股票
        month_stocks = set()
        for trade in trades:
            if trade.trade_date.month == month and trade.trade_date.year == year:
                month_stocks.add(trade.stock_code)
        
        # 计算每只股票到该月底的收益情况
        month_profit = 0
        success_count = 0
        
        # 计算该月的最后一天
        from calendar import monthrange
        last_day = monthrange(year, month)[1]
        month_end = datetime(year, month, last_day)
        
        for stock_code in month_stocks:
            stock_trades = [t for t in trades if t.stock_code == stock_code 
                          and t.trade_date <= month_end]
            
            # 计算该股票的收益
            position = 0
            total_cost = 0
            total_revenue = 0
            
            for trade in stock_trades:
                if trade.trade_type == 'buy':
                    position += trade.quantity
                    total_cost += float(trade.price * trade.quantity)
                elif trade.trade_type == 'sell':
                    position -= trade.quantity
                    total_revenue += float(trade.price * trade.quantity)
            
            # 如果已清仓，计算实际收益
            if position == 0:
                profit = total_revenue - total_cost
                month_profit += profit
                if profit > 0:
                    success_count += 1
        
        return month_profit, success_count