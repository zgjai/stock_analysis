"""
期望对比服务单元测试
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from services.expectation_comparison_service import ExpectationComparisonService
from models.trade_record import TradeRecord
from error_handlers import ValidationError, DatabaseError


class TestExpectationComparisonService:
    """期望对比服务测试类"""
    
    def test_probability_model_definition(self):
        """测试概率模型定义 - Requirements: 2.2"""
        model = ExpectationComparisonService.PROBABILITY_MODEL
        
        # 验证模型包含8个场景
        assert len(model) == 8
        
        # 验证概率总和为1
        total_probability = sum(scenario['probability'] for scenario in model)
        assert abs(total_probability - 1.0) < 0.001
        
        # 验证每个场景包含必要字段
        for scenario in model:
            assert 'probability' in scenario
            assert 'return_rate' in scenario
            assert 'max_holding_days' in scenario
            assert 0 <= scenario['probability'] <= 1
            assert scenario['max_holding_days'] > 0
    
    def test_calculate_expectation_metrics_basic(self):
        """测试基础期望指标计算 - Requirements: 2.2, 2.4"""
        base_capital = 3200000
        result = ExpectationComparisonService.calculate_expectation_metrics(base_capital)
        
        # 验证返回结果包含所有必要字段
        expected_keys = ['return_rate', 'return_amount', 'holding_days', 'success_rate']
        for key in expected_keys:
            assert key in result
            assert isinstance(result[key], (int, float))
        
        # 验证期望收益率计算
        model = ExpectationComparisonService.PROBABILITY_MODEL
        expected_return_rate = sum(p['probability'] * p['return_rate'] for p in model)
        assert abs(result['return_rate'] - expected_return_rate) < 0.001
        
        # 验证期望持仓天数计算
        expected_holding_days = sum(p['probability'] * p['max_holding_days'] for p in model)
        assert abs(result['holding_days'] - expected_holding_days) < 0.001
        
        # 验证期望胜率计算
        expected_success_rate = sum(p['probability'] for p in model if p['return_rate'] > 0)
        assert abs(result['success_rate'] - expected_success_rate) < 0.001
        
        # 验证期望收益金额计算 - Requirements: 7.1, 7.2
        expected_return_amount = base_capital * expected_return_rate
        assert abs(result['return_amount'] - expected_return_amount) < 0.01
    
    def test_calculate_expectation_metrics_different_capital(self):
        """测试不同本金下的期望指标计算 - Requirements: 7.1, 7.2"""
        test_capitals = [1000000, 5000000, 10000000]
        
        for capital in test_capitals:
            result = ExpectationComparisonService.calculate_expectation_metrics(capital)
            
            # 收益率和其他指标应该不变
            base_result = ExpectationComparisonService.calculate_expectation_metrics(3200000)
            assert result['return_rate'] == base_result['return_rate']
            assert result['holding_days'] == base_result['holding_days']
            assert result['success_rate'] == base_result['success_rate']
            
            # 收益金额应该按比例变化
            expected_amount = capital * result['return_rate']
            assert abs(result['return_amount'] - expected_amount) < 0.01
    
    def test_calculate_expectation_metrics_manual_calculation(self):
        """测试期望指标的手动计算验证 - Requirements: 2.2, 2.4"""
        base_capital = 3200000
        result = ExpectationComparisonService.calculate_expectation_metrics(base_capital)
        
        # 手动计算期望收益率
        model = ExpectationComparisonService.PROBABILITY_MODEL
        manual_return_rate = (
            0.10 * 0.20 +  # 10%概率盈利20%
            0.10 * 0.15 +  # 10%概率盈利15%
            0.15 * 0.10 +  # 15%概率盈利10%
            0.15 * 0.05 +  # 15%概率盈利5%
            0.10 * 0.02 +  # 10%概率盈利2%
            0.20 * (-0.03) +  # 20%概率亏损3%
            0.15 * (-0.05) +  # 15%概率亏损5%
            0.05 * (-0.10)    # 5%概率亏损10%
        )
        assert abs(result['return_rate'] - manual_return_rate) < 0.001
        
        # 手动计算期望持仓天数
        manual_holding_days = (
            0.10 * 30 +  # 10%概率最大持仓30天
            0.10 * 20 +  # 10%概率最大持仓20天
            0.15 * 15 +  # 15%概率最大持仓15天
            0.15 * 10 +  # 15%概率最大持仓10天
            0.10 * 5 +   # 10%概率最大持仓5天
            0.20 * 5 +   # 20%概率最大持仓5天
            0.15 * 5 +   # 15%概率最大持仓5天
            0.05 * 5     # 5%概率最大持仓5天
        )
        assert abs(result['holding_days'] - manual_holding_days) < 0.001
        
        # 手动计算期望胜率（盈利概率之和）
        manual_success_rate = 0.10 + 0.10 + 0.15 + 0.15 + 0.10  # 前5个场景为盈利
        assert abs(result['success_rate'] - manual_success_rate) < 0.001
    
    def test_calculate_actual_metrics_empty_trades(self):
        """测试空交易列表的实际指标计算 - Requirements: 3.1, 3.2, 3.3"""
        base_capital = 3200000
        result = ExpectationComparisonService.calculate_actual_metrics([], base_capital)
        
        # 验证空交易时的默认值
        assert result['return_rate'] == 0.0
        assert result['return_amount'] == 0.0
        assert result['holding_days'] == 0.0
        assert result['success_rate'] == 0.0
        assert result['total_trades'] == 0
        assert result['completed_trades'] == 0
    
    def test_calculate_actual_metrics_with_mock_trades(self):
        """测试使用模拟交易数据的实际指标计算 - Requirements: 3.1, 3.2, 3.3, 3.4"""
        base_capital = 3200000
        
        # 创建模拟交易数据
        mock_trades = self._create_mock_completed_trades()
        
        with patch.object(ExpectationComparisonService, '_calculate_completed_trades_metrics') as mock_calc:
            # 模拟已完成交易的计算结果
            mock_calc.return_value = {
                'weighted_return_rate': 0.05,  # 5%收益率
                'avg_holding_days': 12.0,      # 平均12天
                'success_rate': 0.7,           # 70%胜率
                'completed_count': 10          # 10笔完成交易
            }
            
            result = ExpectationComparisonService.calculate_actual_metrics(mock_trades, base_capital)
            
            # 验证计算结果
            assert result['return_rate'] == 0.05
            assert result['return_amount'] == base_capital * 0.05
            assert result['holding_days'] == 12.0
            assert result['success_rate'] == 0.7
            assert result['total_trades'] == len(mock_trades)
            assert result['completed_trades'] == 10
    
    def test_calculate_comparison_results_basic(self):
        """测试基础对比结果计算 - Requirements: 5.1, 5.2, 5.3"""
        expectation = {
            'return_rate': 0.02,      # 2%期望收益率
            'return_amount': 64000,   # 64000元期望收益
            'holding_days': 11.5,     # 11.5天期望持仓
            'success_rate': 0.6       # 60%期望胜率
        }
        
        actual = {
            'return_rate': 0.03,      # 3%实际收益率
            'return_amount': 96000,   # 96000元实际收益
            'holding_days': 10.0,     # 10天实际持仓
            'success_rate': 0.7       # 70%实际胜率
        }
        
        result = ExpectationComparisonService.calculate_comparison_results(expectation, actual)
        
        # 验证差异计算
        assert abs(result['return_rate_diff'] - 0.01) < 0.001
        assert abs(result['return_amount_diff'] - 32000) < 0.01
        assert abs(result['holding_days_diff'] - (-1.5)) < 0.001
        assert abs(result['success_rate_diff'] - 0.1) < 0.001
        
        # 验证百分比差异计算
        assert abs(result['return_rate_pct_diff'] - 50.0) < 0.1  # (0.01/0.02)*100
        assert abs(result['holding_days_pct_diff'] - (-13.04)) < 0.1  # (-1.5/11.5)*100
        assert abs(result['success_rate_pct_diff'] - 16.67) < 0.1  # (0.1/0.6)*100
    
    def test_calculate_comparison_results_status_generation(self):
        """测试对比结果状态生成 - Requirements: 5.4, 5.5"""
        expectation = {
            'return_rate': 0.02,
            'return_amount': 64000,
            'holding_days': 10.0,
            'success_rate': 0.6
        }
        
        # 测试超出期望的情况
        actual_positive = {
            'return_rate': 0.025,     # 25%超出期望
            'return_amount': 80000,
            'holding_days': 8.0,      # 持仓天数更短（更好）
            'success_rate': 0.7       # 17%超出期望
        }
        
        result = ExpectationComparisonService.calculate_comparison_results(expectation, actual_positive)
        
        # 验证状态判断
        assert result['return_rate_status']['status'] == 'positive'
        assert result['return_rate_status']['message'] == '超出期望'
        assert result['holding_days_status']['status'] == 'positive'  # 持仓天数短是好事
        assert result['success_rate_status']['status'] == 'positive'
    
    def test_get_difference_status_ranges(self):
        """测试差异状态判断的边界值 - Requirements: 5.4, 5.5"""
        # 测试接近期望（±5%范围内）
        status = ExpectationComparisonService._get_difference_status(3.0)
        assert status['status'] == 'neutral'
        assert status['message'] == '接近期望'
        assert status['color'] == 'warning'
        
        status = ExpectationComparisonService._get_difference_status(-4.0)
        assert status['status'] == 'neutral'
        
        # 测试超出期望（>5%）
        status = ExpectationComparisonService._get_difference_status(10.0)
        assert status['status'] == 'positive'
        assert status['message'] == '超出期望'
        assert status['color'] == 'success'
        
        # 测试低于期望（<-5%）
        status = ExpectationComparisonService._get_difference_status(-10.0)
        assert status['status'] == 'negative'
        assert status['message'] == '低于期望'
        assert status['color'] == 'danger'
        
        # 测试反向判断（如持仓天数）
        status = ExpectationComparisonService._get_difference_status(-10.0, reverse=True)
        assert status['status'] == 'positive'  # 持仓天数减少是好事
        
        status = ExpectationComparisonService._get_difference_status(10.0, reverse=True)
        assert status['status'] == 'negative'  # 持仓天数增加是坏事
    
    def test_validate_parameters_valid_inputs(self):
        """测试参数验证 - 有效输入"""
        # 测试有效的时间范围
        valid_ranges = ['30d', '90d', '1y', 'all']
        for time_range in valid_ranges:
            try:
                ExpectationComparisonService._validate_parameters(time_range, 3200000)
            except ValidationError:
                pytest.fail(f"Valid time range {time_range} should not raise ValidationError")
        
        # 测试有效的本金
        valid_capitals = [1, 1000000, 3200000, 10000000]
        for capital in valid_capitals:
            try:
                ExpectationComparisonService._validate_parameters('all', capital)
            except ValidationError:
                pytest.fail(f"Valid capital {capital} should not raise ValidationError")
    
    def test_validate_parameters_invalid_inputs(self):
        """测试参数验证 - 无效输入"""
        # 测试无效的时间范围
        invalid_ranges = ['1d', '7d', '6m', 'invalid']
        for time_range in invalid_ranges:
            with pytest.raises(ValidationError, match="时间范围必须是以下之一"):
                ExpectationComparisonService._validate_parameters(time_range, 3200000)
        
        # 测试无效的本金
        invalid_capitals = [0, -1000, -3200000]
        for capital in invalid_capitals:
            with pytest.raises(ValidationError, match="基准本金必须大于0"):
                ExpectationComparisonService._validate_parameters('all', capital)
    
    def test_calculate_stock_completed_trades_fifo(self):
        """测试FIFO方法计算单只股票完成交易"""
        # 创建测试交易记录
        base_date = datetime(2024, 1, 1)
        trades = [
            self._create_mock_trade('buy', 100, 10.0, base_date),
            self._create_mock_trade('buy', 200, 12.0, base_date + timedelta(days=1)),
            self._create_mock_trade('sell', 150, 15.0, base_date + timedelta(days=5)),
            self._create_mock_trade('sell', 100, 14.0, base_date + timedelta(days=10))
        ]
        
        completed = ExpectationComparisonService._calculate_stock_completed_trades(trades)
        
        # 验证完成交易数量
        assert len(completed) == 3
        
        # FIFO逻辑：
        # 第一次卖出150股@15元：先从第一次买入100股@10元中取100股，再从第二次买入200股@12元中取50股
        # 第二次卖出100股@14元：从第二次买入剩余的150股@12元中取100股
        
        # 验证第一笔完成交易（100股@10元卖@15元）
        first_trade = completed[0]
        assert first_trade['quantity'] == 100
        assert first_trade['buy_price'] == 10.0
        assert first_trade['sell_price'] == 15.0
        assert first_trade['profit'] == 100 * (15.0 - 10.0)
        assert first_trade['holding_days'] == 5
        
        # 验证第二笔完成交易（50股@12元卖@15元）
        second_trade = completed[1]
        assert second_trade['quantity'] == 50
        assert second_trade['buy_price'] == 12.0
        assert second_trade['sell_price'] == 15.0
        assert second_trade['profit'] == 50 * (15.0 - 12.0)
        assert second_trade['holding_days'] == 4  # 从1月2日到1月6日是4天
        
        # 验证第三笔完成交易（100股@12元卖@14元）
        third_trade = completed[2]
        assert third_trade['quantity'] == 100
        assert third_trade['buy_price'] == 12.0
        assert third_trade['sell_price'] == 14.0
        assert third_trade['profit'] == 100 * (14.0 - 12.0)
        assert third_trade['holding_days'] == 9  # 从1月2日到1月11日是9天
    
    def test_default_base_capital_constant(self):
        """测试默认基准本金常量 - Requirements: 7.1, 7.2"""
        assert ExpectationComparisonService.DEFAULT_BASE_CAPITAL == 3200000
    
    def test_expectation_metrics_error_handling(self):
        """测试期望指标计算的错误处理"""
        # 测试异常情况下的错误处理 - 空模型会导致sum()返回0，不会抛出异常
        # 改为测试无效的模型数据
        invalid_model = [{'invalid': 'data'}]
        with patch.object(ExpectationComparisonService, 'PROBABILITY_MODEL', invalid_model):
            with pytest.raises(DatabaseError, match="计算期望指标失败"):
                ExpectationComparisonService.calculate_expectation_metrics(3200000)
    
    def test_actual_metrics_error_handling(self):
        """测试实际指标计算的错误处理"""
        # 创建会导致错误的模拟交易 - 模拟_calculate_completed_trades_metrics抛出异常
        mock_trades = [Mock(spec=TradeRecord)]
        
        with patch.object(ExpectationComparisonService, '_calculate_completed_trades_metrics') as mock_calc:
            mock_calc.side_effect = Exception("Test error")
            with pytest.raises(DatabaseError, match="计算实际指标失败"):
                ExpectationComparisonService.calculate_actual_metrics(mock_trades, 3200000)
    
    def test_comparison_results_error_handling(self):
        """测试对比结果计算的错误处理"""
        # 测试除零错误的处理
        expectation = {'return_rate': 0, 'return_amount': 0, 'holding_days': 0, 'success_rate': 0}
        actual = {'return_rate': 0.05, 'return_amount': 160000, 'holding_days': 10, 'success_rate': 0.7}
        
        result = ExpectationComparisonService.calculate_comparison_results(expectation, actual)
        
        # 验证除零情况下的处理
        assert result['return_rate_pct_diff'] == 0  # 期望值为0时，百分比差异为0
        assert result['holding_days_pct_diff'] == 0
        assert result['success_rate_pct_diff'] == 0
    
    # 辅助方法
    def _create_mock_completed_trades(self):
        """创建模拟的已完成交易数据"""
        trades = []
        base_date = datetime(2024, 1, 1)
        
        for i in range(20):  # 创建20笔交易
            # 买入交易
            buy_trade = Mock(spec=TradeRecord)
            buy_trade.stock_code = f'00000{i % 5}'  # 5只不同股票
            buy_trade.trade_type = 'buy'
            buy_trade.quantity = 100
            buy_trade.price = Decimal('10.00')
            buy_trade.trade_date = base_date + timedelta(days=i)
            buy_trade.is_corrected = False
            trades.append(buy_trade)
            
            # 对应的卖出交易（部分）
            if i < 10:  # 只有前10笔有对应的卖出
                sell_trade = Mock(spec=TradeRecord)
                sell_trade.stock_code = f'00000{i % 5}'
                sell_trade.trade_type = 'sell'
                sell_trade.quantity = 100
                sell_trade.price = Decimal('11.00')  # 10%收益
                sell_trade.trade_date = base_date + timedelta(days=i + 5)
                sell_trade.is_corrected = False
                trades.append(sell_trade)
        
        return trades
    
    def _create_mock_trade(self, trade_type, quantity, price, trade_date):
        """创建单个模拟交易记录"""
        trade = Mock(spec=TradeRecord)
        trade.trade_type = trade_type
        trade.quantity = quantity
        trade.price = Decimal(str(price))
        trade.trade_date = trade_date
        trade.is_corrected = False
        return trade


if __name__ == '__main__':
    pytest.main([__file__, '-v'])