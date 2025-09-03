"""
期望对比功能数据传输对象（DTO）
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ExpectationMetrics:
    """期望指标数据传输对象
    
    Requirements: 2.2, 2.3, 2.4
    """
    return_rate: float          # 期望收益率
    return_amount: float        # 期望收益金额（基于320万）
    holding_days: float         # 期望持仓天数
    success_rate: float         # 期望胜率
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class ActualMetrics:
    """实际指标数据传输对象
    
    Requirements: 3.1, 3.2, 3.3, 3.4
    """
    return_rate: float          # 实际收益率
    return_amount: float        # 实际收益金额（已实现收益）
    holding_days: float         # 实际平均持仓天数
    success_rate: float         # 实际胜率
    total_trades: int           # 总交易数
    completed_trades: int       # 已完成交易数
    total_invested: float       # 总投入资金
    realized_profit: float      # 已实现收益
    unrealized_profit: float    # 未实现收益
    total_profit: float         # 总收益（已实现+未实现）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class DifferenceStatus:
    """差异状态数据传输对象
    
    Requirements: 5.4, 5.5
    """
    status: str                 # 状态：positive, negative, neutral
    message: str                # 提示信息：超出期望, 低于期望, 接近期望
    color: str                  # 颜色标识：success, danger, warning
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class ComparisonResults:
    """对比结果数据传输对象
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    """
    return_rate_diff: float     # 收益率差异
    return_amount_diff: float   # 收益金额差异
    holding_days_diff: float    # 持仓天数差异
    success_rate_diff: float    # 胜率差异
    return_rate_pct_diff: float # 收益率百分比差异
    holding_days_pct_diff: float # 持仓天数百分比差异
    success_rate_pct_diff: float # 胜率百分比差异
    return_rate_status: DifferenceStatus    # 收益率状态
    holding_days_status: DifferenceStatus   # 持仓天数状态
    success_rate_status: DifferenceStatus   # 胜率状态
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        # 转换嵌套的DifferenceStatus对象
        data['return_rate_status'] = self.return_rate_status.to_dict()
        data['holding_days_status'] = self.holding_days_status.to_dict()
        data['success_rate_status'] = self.success_rate_status.to_dict()
        return data


@dataclass
class TimeRangeInfo:
    """时间范围信息数据传输对象
    
    Requirements: 6.1, 6.2, 7.3
    """
    range: str                  # 时间范围代码：30d, 90d, 1y, all
    range_name: str             # 时间范围名称：最近30天, 最近90天, 最近1年, 全部时间
    start_date: str             # 开始日期（ISO格式）
    end_date: str               # 结束日期（ISO格式）
    total_trades: int           # 该时间范围内的总交易数
    base_capital_start_date: str # 320万本金起始日期（ISO格式）
    base_capital_start_note: str # 本金起始日期说明
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class ExpectationComparisonData:
    """期望对比完整数据传输对象
    
    Requirements: 2.1, 6.1, 6.2, 6.3
    """
    expectation: ExpectationMetrics     # 期望指标
    actual: ActualMetrics               # 实际指标
    comparison: ComparisonResults       # 对比结果
    time_range: TimeRangeInfo          # 时间范围信息
    base_capital: float                 # 基准本金
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'expectation': self.expectation.to_dict(),
            'actual': self.actual.to_dict(),
            'comparison': self.comparison.to_dict(),
            'time_range': self.time_range.to_dict(),
            'base_capital': self.base_capital
        }
    
    @classmethod
    def from_service_data(cls, service_data: Dict[str, Any]) -> 'ExpectationComparisonData':
        """从服务层数据创建DTO对象
        
        Args:
            service_data: 服务层返回的数据字典
            
        Returns:
            ExpectationComparisonData对象
        """
        # 创建期望指标对象
        expectation = ExpectationMetrics(**service_data['expectation'])
        
        # 创建实际指标对象
        actual = ActualMetrics(**service_data['actual'])
        
        # 创建差异状态对象
        comparison_data = service_data['comparison']
        return_rate_status = DifferenceStatus(**comparison_data['return_rate_status'])
        holding_days_status = DifferenceStatus(**comparison_data['holding_days_status'])
        success_rate_status = DifferenceStatus(**comparison_data['success_rate_status'])
        
        # 创建对比结果对象
        comparison = ComparisonResults(
            return_rate_diff=comparison_data['return_rate_diff'],
            return_amount_diff=comparison_data['return_amount_diff'],
            holding_days_diff=comparison_data['holding_days_diff'],
            success_rate_diff=comparison_data['success_rate_diff'],
            return_rate_pct_diff=comparison_data['return_rate_pct_diff'],
            holding_days_pct_diff=comparison_data['holding_days_pct_diff'],
            success_rate_pct_diff=comparison_data['success_rate_pct_diff'],
            return_rate_status=return_rate_status,
            holding_days_status=holding_days_status,
            success_rate_status=success_rate_status
        )
        
        # 创建时间范围信息对象
        time_range = TimeRangeInfo(**service_data['time_range'])
        
        return cls(
            expectation=expectation,
            actual=actual,
            comparison=comparison,
            time_range=time_range,
            base_capital=service_data['base_capital']
        )


@dataclass
class ExpectationComparisonResponse:
    """期望对比API响应数据传输对象"""
    success: bool
    data: Optional[ExpectationComparisonData]
    message: str
    error_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            'success': self.success,
            'message': self.message
        }
        
        if self.data:
            result['data'] = self.data.to_dict()
        
        if self.error_code:
            result['error_code'] = self.error_code
            
        return result