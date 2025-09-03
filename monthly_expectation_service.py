"""
月度期望收益服务
"""
import json
from datetime import datetime, date
from typing import Dict, List, Any
from services.base_service import BaseService
from error_handlers import ValidationError, DatabaseError


class MonthlyExpectationService(BaseService):
    """月度期望收益服务"""
    
    @classmethod
    def get_monthly_expectations(cls) -> List[Dict[str, Any]]:
        """获取月度期望收益数据
        
        Returns:
            月度期望收益数据列表
        """
        try:
            # 读取预计算的期望收益数据
            with open('expected_monthly_returns.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
        except FileNotFoundError:
            raise DatabaseError("期望收益数据文件不存在，请先运行计算脚本")
        except json.JSONDecodeError:
            raise DatabaseError("期望收益数据文件格式错误")
        except Exception as e:
            raise DatabaseError(f"读取期望收益数据失败: {str(e)}")
    
    @classmethod
    def get_monthly_comparison(cls, year: int = None, month: int = None) -> Dict[str, Any]:
        """获取指定月份的期望与实际收益对比
        
        Args:
            year: 年份，默认为当前年份
            month: 月份，默认为当前月份
            
        Returns:
            对比数据字典
        """
        try:
            if year is None:
                year = datetime.now().year
            if month is None:
                month = datetime.now().month
            
            # 获取期望数据
            expectations = cls.get_monthly_expectations()
            
            # 查找指定月份的期望数据
            target_month = f"{year}年{month:02d}月"
            expected_data = None
            
            for item in expectations:
                if item['month'] == target_month:
                    expected_data = item
                    break
            
            if not expected_data:
                raise ValidationError(f"未找到{target_month}的期望数据")
            
            # 获取实际收益数据（这里需要从交易记录中计算）
            actual_data = cls._calculate_actual_monthly_return(year, month)
            
            # 计算对比结果
            comparison = cls._calculate_monthly_comparison(expected_data, actual_data)
            
            return {
                'year': year,
                'month': month,
                'month_str': target_month,
                'expected': expected_data,
                'actual': actual_data,
                'comparison': comparison
            }
            
        except ValidationError as e:
            raise e
        except Exception as e:
            raise DatabaseError(f"获取月度对比数据失败: {str(e)}")
    
    @classmethod
    def _calculate_actual_monthly_return(cls, year: int, month: int) -> Dict[str, Any]:
        """计算指定月份的实际收益
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            实际收益数据字典
        """
        try:
            from models.trade_record import TradeRecord
            from services.analytics_service import AnalyticsService
            from sqlalchemy import and_, extract
            from datetime import datetime, date
            
            # 获取指定月份的交易记录
            trades = TradeRecord.query.filter(
                and_(
                    TradeRecord.is_corrected == False,
                    extract('year', TradeRecord.trade_date) == year,
                    extract('month', TradeRecord.trade_date) == month
                )
            ).all()
            
            if not trades:
                return {
                    'total_trades': 0,
                    'buy_amount': 0.0,
                    'sell_amount': 0.0,
                    'realized_profit': 0.0,
                    'unrealized_profit': 0.0,
                    'total_profit': 0.0,
                    'return_rate': 0.0,
                    'start_capital': 0.0,
                    'end_capital': 0.0
                }
            
            # 使用AnalyticsService的月度收益计算方法，确保与其他模块一致
            all_trades = TradeRecord.query.all()
            monthly_profit, monthly_success, monthly_cost = AnalyticsService._calculate_monthly_realized_profit_and_success(
                all_trades, month, year
            )
            
            # 计算当月的买入和卖出金额
            buy_amount = sum(float(t.price) * t.quantity for t in trades if t.trade_type == 'buy')
            sell_amount = sum(float(t.price) * t.quantity for t in trades if t.trade_type == 'sell')
            
            # 计算当月现金流差额
            monthly_cash_flow = sell_amount - buy_amount
            
            # 计算收益率（基于当月投入成本）
            return_rate = monthly_profit / monthly_cost if monthly_cost > 0 else 0.0
            
            # 估算月初资本
            start_capital = cls._estimate_month_start_capital(year, month)
            end_capital = start_capital + monthly_profit
            
            return {
                'total_trades': len(trades),
                'buy_amount': buy_amount,
                'sell_amount': sell_amount,
                'realized_profit': monthly_profit,  # 使用AnalyticsService的月度收益
                'unrealized_profit': 0.0,  # 月度收益中不区分已实现和未实现
                'total_profit': monthly_profit,  # 当月总收益
                'return_rate': return_rate,
                'start_capital': start_capital,
                'end_capital': end_capital,
                'monthly_cash_flow': monthly_cash_flow,  # 当月现金流差额
                'monthly_cost': monthly_cost,  # 当月投入成本
                'monthly_success': monthly_success  # 当月成功股票数
            }
            
        except Exception as e:
            raise DatabaseError(f"计算实际月度收益失败: {str(e)}")
    
    @classmethod
    def _estimate_month_start_capital(cls, year: int, month: int) -> float:
        """估算月初资本
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            估算的月初资本
        """
        # 简化处理：如果是2025年8月，返回320万；否则根据期望数据估算
        if year == 2025 and month == 8:
            return 3200000.0
        
        try:
            expectations = cls.get_monthly_expectations()
            target_month = f"{year}年{month:02d}月"
            
            for item in expectations:
                if item['month'] == target_month:
                    return item['start_capital']
            
            # 如果找不到，返回320万作为默认值
            return 3200000.0
            
        except:
            return 3200000.0
    
    @classmethod
    def _calculate_monthly_comparison(cls, expected: Dict[str, Any], actual: Dict[str, Any]) -> Dict[str, Any]:
        """计算月度对比结果
        
        Args:
            expected: 期望数据
            actual: 实际数据
            
        Returns:
            对比结果字典
        """
        try:
            # 收益金额差异（使用总收益，与期望对比模块保持一致）
            amount_diff = actual['total_profit'] - expected['expected_amount']
            amount_diff_pct = (amount_diff / expected['expected_amount'] * 100) if expected['expected_amount'] != 0 else 0
            
            # 收益率差异
            rate_diff = actual['return_rate'] - (expected['expected_rate'] / 100)
            rate_diff_pct = (rate_diff / (expected['expected_rate'] / 100) * 100) if expected['expected_rate'] != 0 else 0
            
            # 判断表现状态
            def get_performance_status(diff_pct):
                if abs(diff_pct) <= 10:
                    return {'status': 'neutral', 'message': '接近期望', 'color': 'warning'}
                elif diff_pct > 10:
                    return {'status': 'positive', 'message': '超出期望', 'color': 'success'}
                else:
                    return {'status': 'negative', 'message': '低于期望', 'color': 'danger'}
            
            amount_status = get_performance_status(amount_diff_pct)
            rate_status = get_performance_status(rate_diff_pct)
            
            return {
                'amount_diff': amount_diff,
                'amount_diff_pct': amount_diff_pct,
                'rate_diff': rate_diff,
                'rate_diff_pct': rate_diff_pct,
                'amount_status': amount_status,
                'rate_status': rate_status
            }
            
        except Exception as e:
            raise DatabaseError(f"计算月度对比结果失败: {str(e)}")