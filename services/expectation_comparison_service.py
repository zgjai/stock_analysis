"""
期望对比分析服务
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from collections import defaultdict
from sqlalchemy import and_, extract
from extensions import db
from models.trade_record import TradeRecord
from services.base_service import BaseService
from error_handlers import ValidationError, DatabaseError


class ExpectationComparisonService(BaseService):
    """期望对比分析服务"""
    
    # 概率模型定义 (Requirements: 2.2, 2.3)
    PROBABILITY_MODEL = [
        {'probability': 0.10, 'return_rate': 0.20, 'max_holding_days': 30},
        {'probability': 0.10, 'return_rate': 0.15, 'max_holding_days': 20},
        {'probability': 0.15, 'return_rate': 0.10, 'max_holding_days': 15},
        {'probability': 0.15, 'return_rate': 0.05, 'max_holding_days': 10},
        {'probability': 0.10, 'return_rate': 0.02, 'max_holding_days': 5},
        {'probability': 0.20, 'return_rate': -0.03, 'max_holding_days': 5},
        {'probability': 0.15, 'return_rate': -0.05, 'max_holding_days': 5},
        {'probability': 0.05, 'return_rate': -0.10, 'max_holding_days': 5}
    ]
    
    # 默认基准本金 (Requirements: 7.1, 7.2)
    DEFAULT_BASE_CAPITAL = 3200000  # 320万
    
    # 320万本金起始日期 (Requirements: 7.3)
    BASE_CAPITAL_START_DATE = datetime(2025, 8, 1)  # 2025年8月1号开始
    
    @classmethod
    def get_expectation_comparison(cls, time_range: str = 'all', base_capital: float = None) -> Dict[str, Any]:
        """获取期望对比数据
        
        Args:
            time_range: 时间范围 ('30d', '90d', '1y', 'all')
            base_capital: 基准本金，默认320万
            
        Returns:
            期望对比数据字典
            
        Requirements: 2.1, 6.1, 6.2, 6.3
        """
        try:
            if base_capital is None:
                base_capital = cls.DEFAULT_BASE_CAPITAL
            
            # 验证参数
            cls._validate_parameters(time_range, base_capital)
            
            # 计算期望指标
            expectation_metrics = cls.calculate_expectation_metrics(base_capital)
            
            # 获取实际交易数据
            trades = cls._get_trades_by_time_range(time_range)
            
            # 计算实际指标
            actual_metrics = cls.calculate_actual_metrics(trades, base_capital)
            
            # 计算对比结果
            comparison_results = cls.calculate_comparison_results(expectation_metrics, actual_metrics)
            
            # 获取时间范围信息
            time_range_info = cls._get_time_range_info(time_range, trades)
            
            return {
                'expectation': expectation_metrics,
                'actual': actual_metrics,
                'comparison': comparison_results,
                'time_range': time_range_info,
                'base_capital': base_capital
            }
        except ValidationError as e:
            raise e
        except Exception as e:
            raise DatabaseError(f"获取期望对比数据失败: {str(e)}")
    
    @classmethod
    def calculate_expectation_metrics(cls, base_capital: float) -> Dict[str, float]:
        """计算期望指标
        
        Args:
            base_capital: 基准本金
            
        Returns:
            期望指标字典
            
        Requirements: 2.2, 2.3, 2.4
        """
        try:
            # 期望收益率 = Σ(概率 × 收益率)
            expected_return_rate = sum(
                p['probability'] * p['return_rate'] 
                for p in cls.PROBABILITY_MODEL
            )
            
            # 期望持仓天数 = Σ(概率 × 最大持仓天数)
            expected_holding_days = sum(
                p['probability'] * p['max_holding_days'] 
                for p in cls.PROBABILITY_MODEL
            )
            
            # 期望胜率 = 盈利概率之和
            expected_success_rate = sum(
                p['probability'] 
                for p in cls.PROBABILITY_MODEL 
                if p['return_rate'] > 0
            )
            
            # 期望收益金额（基于基准本金）
            expected_return_amount = base_capital * expected_return_rate
            
            return {
                'return_rate': expected_return_rate,
                'return_amount': expected_return_amount,
                'holding_days': expected_holding_days,
                'success_rate': expected_success_rate
            }
        except Exception as e:
            raise DatabaseError(f"计算期望指标失败: {str(e)}")
    
    @classmethod
    def calculate_actual_metrics(cls, trades: List[TradeRecord], base_capital: float) -> Dict[str, float]:
        """计算实际指标
        
        Args:
            trades: 交易记录列表
            base_capital: 基准本金
            
        Returns:
            实际指标字典
            
        Requirements: 3.1, 3.2, 3.3, 3.4
        """
        try:
            if not trades:
                return {
                    'return_rate': 0.0,
                    'return_amount': 0.0,
                    'holding_days': 0.0,
                    'success_rate': 0.0,
                    'total_trades': 0,
                    'completed_trades': 0,
                    'total_invested': 0.0,
                    'realized_profit': 0.0
                }
            
            # 计算实际投入资金
            total_buy_amount = sum(float(t.price) * t.quantity for t in trades if t.trade_type == 'buy')
            
            # 计算已完成交易的实际指标
            completed_trades_data = cls._calculate_completed_trades_metrics(trades)
            
            # 计算已实现收益
            actual_realized_profit = completed_trades_data.get('total_realized_profit', 0.0)
            
            # 计算当前持仓的未实现收益
            unrealized_profit = cls._calculate_unrealized_profit(trades)
            
            # 总收益 = 已实现收益 + 未实现收益
            total_profit = actual_realized_profit + unrealized_profit
            
            # 基于实际投入资金的总收益率
            actual_return_rate = total_profit / total_buy_amount if total_buy_amount > 0 else 0.0
            
            # 实际收益金额包含已实现和未实现收益
            actual_return_amount = total_profit
            
            # 计算实际平均持仓天数
            actual_holding_days = completed_trades_data['avg_holding_days']
            
            # 计算实际胜率
            actual_success_rate = completed_trades_data['success_rate']
            
            return {
                'return_rate': actual_return_rate,
                'return_amount': actual_return_amount,
                'holding_days': actual_holding_days,
                'success_rate': actual_success_rate,
                'total_trades': len(trades),
                'completed_trades': completed_trades_data['completed_count'],
                'total_invested': total_buy_amount,
                'realized_profit': actual_realized_profit,
                'unrealized_profit': unrealized_profit,
                'total_profit': total_profit
            }
        except Exception as e:
            raise DatabaseError(f"计算实际指标失败: {str(e)}")
    
    @classmethod
    def calculate_comparison_results(cls, expectation: Dict[str, float], actual: Dict[str, float]) -> Dict[str, Any]:
        """计算对比结果
        
        Args:
            expectation: 期望指标
            actual: 实际指标
            
        Returns:
            对比结果字典
            
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
        """
        try:
            # 计算差异值
            return_rate_diff = actual['return_rate'] - expectation['return_rate']
            return_amount_diff = actual['return_amount'] - expectation['return_amount']
            holding_days_diff = actual['holding_days'] - expectation['holding_days']
            success_rate_diff = actual['success_rate'] - expectation['success_rate']
            
            # 计算百分比差异
            return_rate_pct_diff = (return_rate_diff / expectation['return_rate'] * 100) if expectation['return_rate'] != 0 else 0
            holding_days_pct_diff = (holding_days_diff / expectation['holding_days'] * 100) if expectation['holding_days'] != 0 else 0
            success_rate_pct_diff = (success_rate_diff / expectation['success_rate'] * 100) if expectation['success_rate'] != 0 else 0
            
            # 生成差异状态和提示
            return_rate_status = cls._get_difference_status(return_rate_pct_diff)
            holding_days_status = cls._get_difference_status(holding_days_pct_diff, reverse=True)  # 持仓天数越短越好
            success_rate_status = cls._get_difference_status(success_rate_pct_diff)
            
            return {
                'return_rate_diff': return_rate_diff,
                'return_amount_diff': return_amount_diff,
                'holding_days_diff': holding_days_diff,
                'success_rate_diff': success_rate_diff,
                'return_rate_pct_diff': return_rate_pct_diff,
                'holding_days_pct_diff': holding_days_pct_diff,
                'success_rate_pct_diff': success_rate_pct_diff,
                'return_rate_status': return_rate_status,
                'holding_days_status': holding_days_status,
                'success_rate_status': success_rate_status
            }
        except Exception as e:
            raise DatabaseError(f"计算对比结果失败: {str(e)}")
    
    @classmethod
    def _validate_parameters(cls, time_range: str, base_capital: float) -> None:
        """验证参数
        
        Args:
            time_range: 时间范围
            base_capital: 基准本金
            
        Raises:
            ValidationError: 参数验证失败
        """
        valid_time_ranges = ['30d', '90d', '1y', 'all']
        if time_range not in valid_time_ranges:
            raise ValidationError(f"时间范围必须是以下之一: {', '.join(valid_time_ranges)}")
        
        if base_capital <= 0:
            raise ValidationError("基准本金必须大于0")
    
    @classmethod
    def _get_trades_by_time_range(cls, time_range: str) -> List[TradeRecord]:
        """根据时间范围获取交易记录
        
        Args:
            time_range: 时间范围
            
        Returns:
            交易记录列表
            
        Requirements: 6.1, 6.2, 7.3
        """
        try:
            # 基础查询：未订正的交易记录，且在320万本金起始日期之后
            query = TradeRecord.query.filter(
                and_(
                    TradeRecord.is_corrected == False,
                    TradeRecord.trade_date >= cls.BASE_CAPITAL_START_DATE
                )
            )
            
            if time_range != 'all':
                # 计算时间范围的开始日期
                now = datetime.now()
                if time_range == '30d':
                    start_date = now - timedelta(days=30)
                elif time_range == '90d':
                    start_date = now - timedelta(days=90)
                elif time_range == '1y':
                    start_date = now - timedelta(days=365)
                
                # 确保开始日期不早于320万本金起始日期
                start_date = max(start_date, cls.BASE_CAPITAL_START_DATE)
                query = query.filter(TradeRecord.trade_date >= start_date)
            
            return query.all()
        except Exception as e:
            raise DatabaseError(f"获取交易记录失败: {str(e)}")
    
    @classmethod
    def _calculate_completed_trades_metrics(cls, trades: List[TradeRecord]) -> Dict[str, float]:
        """计算已完成交易的指标
        
        Args:
            trades: 交易记录列表
            
        Returns:
            已完成交易指标字典
            
        Requirements: 3.1, 3.2, 3.3, 3.5
        """
        try:
            # 按股票分组交易记录
            stock_trades = defaultdict(list)
            for trade in trades:
                stock_trades[trade.stock_code].append(trade)
            
            completed_trades = []
            total_cost = 0
            total_profit = 0
            total_holding_days = 0
            successful_trades = 0
            
            for stock_code, stock_trade_list in stock_trades.items():
                # 按时间排序
                stock_trade_list.sort(key=lambda x: x.trade_date)
                
                # 计算该股票的完成交易
                stock_completed = cls._calculate_stock_completed_trades(stock_trade_list)
                
                for completed_trade in stock_completed:
                    completed_trades.append(completed_trade)
                    total_cost += completed_trade['cost']
                    total_profit += completed_trade['profit']
                    total_holding_days += completed_trade['holding_days']
                    
                    if completed_trade['profit'] > 0:
                        successful_trades += 1
            
            if not completed_trades:
                return {
                    'weighted_return_rate': 0.0,
                    'avg_holding_days': 0.0,
                    'success_rate': 0.0,
                    'completed_count': 0
                }
            
            # 计算加权平均收益率
            weighted_return_rate = total_profit / total_cost if total_cost > 0 else 0
            
            # 计算平均持仓天数
            avg_holding_days = total_holding_days / len(completed_trades)
            
            # 计算胜率
            success_rate = successful_trades / len(completed_trades)
            
            return {
                'weighted_return_rate': weighted_return_rate,
                'avg_holding_days': avg_holding_days,
                'success_rate': success_rate,
                'completed_count': len(completed_trades),
                'total_realized_profit': total_profit
            }
        except Exception as e:
            raise DatabaseError(f"计算已完成交易指标失败: {str(e)}")
    
    @classmethod
    def _calculate_stock_completed_trades(cls, stock_trades: List[TradeRecord]) -> List[Dict[str, Any]]:
        """计算单只股票的完成交易（使用FIFO方法）
        
        Args:
            stock_trades: 单只股票的交易记录列表
            
        Returns:
            完成交易列表
        """
        buy_queue = []  # 买入队列
        completed_trades = []
        
        for trade in stock_trades:
            if trade.trade_type == 'buy':
                buy_queue.append({
                    'quantity': trade.quantity,
                    'price': float(trade.price),
                    'date': trade.trade_date,
                    'remaining': trade.quantity
                })
            elif trade.trade_type == 'sell':
                sell_quantity = trade.quantity
                sell_price = float(trade.price)
                sell_date = trade.trade_date
                
                # 从买入队列中匹配卖出
                while sell_quantity > 0 and buy_queue:
                    buy_item = buy_queue[0]
                    
                    # 计算本次匹配的数量
                    match_quantity = min(sell_quantity, buy_item['remaining'])
                    
                    # 计算本次匹配的成本和收益
                    cost = match_quantity * buy_item['price']
                    revenue = match_quantity * sell_price
                    profit = revenue - cost
                    
                    # 计算持仓天数
                    holding_days = (sell_date - buy_item['date']).days
                    
                    # 记录完成交易
                    completed_trades.append({
                        'quantity': match_quantity,
                        'buy_price': buy_item['price'],
                        'sell_price': sell_price,
                        'cost': cost,
                        'revenue': revenue,
                        'profit': profit,
                        'holding_days': holding_days,
                        'buy_date': buy_item['date'],
                        'sell_date': sell_date
                    })
                    
                    # 更新数量
                    buy_item['remaining'] -= match_quantity
                    sell_quantity -= match_quantity
                    
                    # 如果买入项目已完全匹配，从队列中移除
                    if buy_item['remaining'] <= 0:
                        buy_queue.pop(0)
        
        return completed_trades
    
    @classmethod
    def _calculate_unrealized_profit(cls, trades: List[TradeRecord]) -> float:
        """计算当前持仓的未实现收益
        
        Args:
            trades: 交易记录列表
            
        Returns:
            未实现收益金额
        """
        try:
            from models.stock_price import StockPrice
            from collections import defaultdict
            
            # 计算当前持仓
            holdings = defaultdict(lambda: {'quantity': 0, 'total_cost': 0})
            
            for trade in trades:
                if trade.trade_type == 'buy':
                    holdings[trade.stock_code]['quantity'] += trade.quantity
                    holdings[trade.stock_code]['total_cost'] += float(trade.price) * trade.quantity
                elif trade.trade_type == 'sell':
                    # 按FIFO计算卖出成本
                    if holdings[trade.stock_code]['quantity'] > 0:
                        avg_cost = holdings[trade.stock_code]['total_cost'] / holdings[trade.stock_code]['quantity']
                        cost_reduction = avg_cost * trade.quantity
                        holdings[trade.stock_code]['total_cost'] -= cost_reduction
                        holdings[trade.stock_code]['quantity'] -= trade.quantity
            
            # 计算未实现收益
            total_unrealized_profit = 0.0
            
            for stock_code, holding in holdings.items():
                if holding['quantity'] > 0:
                    # 获取最新价格
                    stock_price = StockPrice.get_latest_price(stock_code)
                    if stock_price and stock_price.current_price:
                        current_price = float(stock_price.current_price)
                        market_value = current_price * holding['quantity']
                        unrealized_profit = market_value - holding['total_cost']
                        total_unrealized_profit += unrealized_profit
            
            return total_unrealized_profit
            
        except Exception as e:
            # 如果无法获取价格数据，返回0
            return 0.0
    
    @classmethod
    def _get_difference_status(cls, pct_diff: float, reverse: bool = False) -> Dict[str, str]:
        """获取差异状态
        
        Args:
            pct_diff: 百分比差异
            reverse: 是否反向判断（如持仓天数，越短越好）
            
        Returns:
            状态字典，包含status和message
            
        Requirements: 5.4, 5.5
        """
        abs_diff = abs(pct_diff)
        
        if abs_diff <= 5:  # ±5%范围内
            return {
                'status': 'neutral',
                'message': '接近期望',
                'color': 'warning'
            }
        elif (pct_diff > 5 and not reverse) or (pct_diff < -5 and reverse):
            return {
                'status': 'positive',
                'message': '超出期望',
                'color': 'success'
            }
        else:
            return {
                'status': 'negative',
                'message': '低于期望',
                'color': 'danger'
            }
    
    @classmethod
    def _get_time_range_info(cls, time_range: str, trades: List[TradeRecord]) -> Dict[str, Any]:
        """获取时间范围信息
        
        Args:
            time_range: 时间范围
            trades: 交易记录列表
            
        Returns:
            时间范围信息字典
        """
        try:
            now = datetime.now()
            
            if time_range == 'all':
                # 对于全部时间，起始日期不能早于320万本金起始日期
                start_date = cls.BASE_CAPITAL_START_DATE
                if trades:
                    actual_start = min(trade.trade_date for trade in trades)
                    start_date = max(start_date, actual_start)
                end_date = max(trade.trade_date for trade in trades) if trades else now
                range_name = f'全部时间（自{cls.BASE_CAPITAL_START_DATE.strftime("%Y年%m月%d日")}）'
            else:
                if time_range == '30d':
                    start_date = now - timedelta(days=30)
                    range_name = '最近30天'
                elif time_range == '90d':
                    start_date = now - timedelta(days=90)
                    range_name = '最近90天'
                elif time_range == '1y':
                    start_date = now - timedelta(days=365)
                    range_name = '最近1年'
                
                # 确保开始日期不早于320万本金起始日期
                start_date = max(start_date, cls.BASE_CAPITAL_START_DATE)
                end_date = now
            
            return {
                'range': time_range,
                'range_name': range_name,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_trades': len(trades),
                'base_capital_start_date': cls.BASE_CAPITAL_START_DATE.isoformat(),
                'base_capital_start_note': f'320万本金计算起始日期：{cls.BASE_CAPITAL_START_DATE.strftime("%Y年%m月%d日")}'
            }
        except Exception as e:
            return {
                'range': time_range,
                'range_name': '未知',
                'start_date': now.isoformat(),
                'end_date': now.isoformat(),
                'total_trades': 0,
                'base_capital_start_date': cls.BASE_CAPITAL_START_DATE.isoformat(),
                'base_capital_start_note': f'320万本金计算起始日期：{cls.BASE_CAPITAL_START_DATE.strftime("%Y年%m月%d日")}'
            }