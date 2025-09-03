"""
期望值计算核心逻辑集成测试
"""
import pytest
from services.expectation_comparison_service import ExpectationComparisonService


class TestExpectationCalculationIntegration:
    """期望值计算集成测试类"""
    
    def test_expectation_calculation_integration(self):
        """测试期望值计算的完整集成 - Requirements: 2.2, 2.4, 7.1, 7.2"""
        # 使用默认320万本金
        base_capital = ExpectationComparisonService.DEFAULT_BASE_CAPITAL
        
        # 计算期望指标
        expectation = ExpectationComparisonService.calculate_expectation_metrics(base_capital)
        
        # 验证期望指标的合理性
        assert expectation['return_rate'] > -0.1  # 期望收益率应该在合理范围内
        assert expectation['return_rate'] < 0.3
        assert expectation['holding_days'] > 0    # 期望持仓天数应该为正数
        assert expectation['holding_days'] < 50   # 不应该超过50天
        assert 0 <= expectation['success_rate'] <= 1  # 胜率应该在0-1之间
        assert expectation['return_amount'] == base_capital * expectation['return_rate']
        
        # 验证具体的期望值（基于给定的概率模型）
        # 手动计算验证
        expected_return_rate = (
            0.10 * 0.20 +    # 10%概率盈利20%
            0.10 * 0.15 +    # 10%概率盈利15%
            0.15 * 0.10 +    # 15%概率盈利10%
            0.15 * 0.05 +    # 15%概率盈利5%
            0.10 * 0.02 +    # 10%概率盈利2%
            0.20 * (-0.03) + # 20%概率亏损3%
            0.15 * (-0.05) + # 15%概率亏损5%
            0.05 * (-0.10)   # 5%概率亏损10%
        )
        
        expected_holding_days = (
            0.10 * 30 +      # 10%概率最大持仓30天
            0.10 * 20 +      # 10%概率最大持仓20天
            0.15 * 15 +      # 15%概率最大持仓15天
            0.15 * 10 +      # 15%概率最大持仓10天
            0.10 * 5 +       # 10%概率最大持仓5天
            0.20 * 5 +       # 20%概率最大持仓5天
            0.15 * 5 +       # 15%概率最大持仓5天
            0.05 * 5         # 5%概率最大持仓5天
        )
        
        expected_success_rate = 0.10 + 0.10 + 0.15 + 0.15 + 0.10  # 盈利概率之和
        
        # 验证计算结果
        assert abs(expectation['return_rate'] - expected_return_rate) < 0.001
        assert abs(expectation['holding_days'] - expected_holding_days) < 0.001
        assert abs(expectation['success_rate'] - expected_success_rate) < 0.001
        
        # 验证期望收益金额
        expected_return_amount = base_capital * expected_return_rate
        assert abs(expectation['return_amount'] - expected_return_amount) < 0.01
        
        print(f"期望收益率: {expectation['return_rate']:.4f} ({expectation['return_rate']*100:.2f}%)")
        print(f"期望收益金额: {expectation['return_amount']:,.2f}元")
        print(f"期望持仓天数: {expectation['holding_days']:.2f}天")
        print(f"期望胜率: {expectation['success_rate']:.2f} ({expectation['success_rate']*100:.1f}%)")
    
    def test_probability_model_consistency(self):
        """测试概率模型的一致性 - Requirements: 2.2"""
        model = ExpectationComparisonService.PROBABILITY_MODEL
        
        # 验证概率总和为1
        total_probability = sum(scenario['probability'] for scenario in model)
        assert abs(total_probability - 1.0) < 0.001, f"概率总和应该为1，实际为{total_probability}"
        
        # 验证模型包含8个场景
        assert len(model) == 8, f"应该包含8个概率场景，实际为{len(model)}"
        
        # 验证每个场景的数据完整性
        for i, scenario in enumerate(model):
            assert 'probability' in scenario, f"场景{i}缺少probability字段"
            assert 'return_rate' in scenario, f"场景{i}缺少return_rate字段"
            assert 'max_holding_days' in scenario, f"场景{i}缺少max_holding_days字段"
            
            assert 0 <= scenario['probability'] <= 1, f"场景{i}的概率应该在0-1之间"
            assert scenario['max_holding_days'] > 0, f"场景{i}的最大持仓天数应该大于0"
        
        # 验证盈利和亏损场景的分布
        profit_scenarios = [s for s in model if s['return_rate'] > 0]
        loss_scenarios = [s for s in model if s['return_rate'] < 0]
        neutral_scenarios = [s for s in model if s['return_rate'] == 0]
        
        assert len(profit_scenarios) > 0, "应该包含盈利场景"
        assert len(loss_scenarios) > 0, "应该包含亏损场景"
        
        print(f"盈利场景数量: {len(profit_scenarios)}")
        print(f"亏损场景数量: {len(loss_scenarios)}")
        print(f"中性场景数量: {len(neutral_scenarios)}")
    
    def test_base_capital_scaling(self):
        """测试基准本金缩放的正确性 - Requirements: 7.1, 7.2"""
        # 测试不同本金下的期望计算
        test_capitals = [1000000, 3200000, 5000000, 10000000]
        
        base_expectation = ExpectationComparisonService.calculate_expectation_metrics(3200000)
        
        for capital in test_capitals:
            expectation = ExpectationComparisonService.calculate_expectation_metrics(capital)
            
            # 收益率、持仓天数、胜率应该不变
            assert expectation['return_rate'] == base_expectation['return_rate']
            assert expectation['holding_days'] == base_expectation['holding_days']
            assert expectation['success_rate'] == base_expectation['success_rate']
            
            # 收益金额应该按比例缩放
            expected_amount = capital * base_expectation['return_rate']
            assert abs(expectation['return_amount'] - expected_amount) < 0.01
            
            # 验证缩放比例
            scale_factor = capital / 3200000
            expected_scaled_amount = base_expectation['return_amount'] * scale_factor
            assert abs(expectation['return_amount'] - expected_scaled_amount) < 0.01
    
    def test_expectation_vs_actual_comparison_logic(self):
        """测试期望与实际对比逻辑的完整性 - Requirements: 5.1, 5.2, 5.3"""
        # 创建模拟的期望和实际数据
        expectation = {
            'return_rate': 0.0175,    # 1.75%期望收益率
            'return_amount': 56000,   # 56000元期望收益
            'holding_days': 11.5,     # 11.5天期望持仓
            'success_rate': 0.6       # 60%期望胜率
        }
        
        # 测试不同的实际表现情况
        test_cases = [
            {
                'name': '超出期望',
                'actual': {
                    'return_rate': 0.025,     # 2.5%实际收益率
                    'return_amount': 80000,   # 80000元实际收益
                    'holding_days': 9.0,      # 9天实际持仓
                    'success_rate': 0.7       # 70%实际胜率
                },
                'expected_status': 'positive'
            },
            {
                'name': '低于期望',
                'actual': {
                    'return_rate': 0.01,      # 1%实际收益率
                    'return_amount': 32000,   # 32000元实际收益
                    'holding_days': 15.0,     # 15天实际持仓
                    'success_rate': 0.4       # 40%实际胜率
                },
                'expected_status': 'negative'
            },
            {
                'name': '接近期望',
                'actual': {
                    'return_rate': 0.018,     # 1.8%实际收益率
                    'return_amount': 57600,   # 57600元实际收益
                    'holding_days': 11.0,     # 11天实际持仓
                    'success_rate': 0.62      # 62%实际胜率
                },
                'expected_status': 'neutral'
            }
        ]
        
        for case in test_cases:
            comparison = ExpectationComparisonService.calculate_comparison_results(
                expectation, case['actual']
            )
            
            # 验证差异计算
            assert 'return_rate_diff' in comparison
            assert 'return_amount_diff' in comparison
            assert 'holding_days_diff' in comparison
            assert 'success_rate_diff' in comparison
            
            # 验证百分比差异计算
            assert 'return_rate_pct_diff' in comparison
            assert 'holding_days_pct_diff' in comparison
            assert 'success_rate_pct_diff' in comparison
            
            # 验证状态判断
            assert 'return_rate_status' in comparison
            assert 'holding_days_status' in comparison
            assert 'success_rate_status' in comparison
            
            print(f"\n{case['name']}:")
            print(f"  收益率差异: {comparison['return_rate_pct_diff']:.2f}%")
            print(f"  持仓天数差异: {comparison['holding_days_pct_diff']:.2f}%")
            print(f"  胜率差异: {comparison['success_rate_pct_diff']:.2f}%")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])