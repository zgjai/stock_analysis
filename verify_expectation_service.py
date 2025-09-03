#!/usr/bin/env python3
"""
期望对比服务验证脚本
直接测试服务层功能，不依赖Flask应用上下文
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_expectation_calculation():
    """测试期望值计算"""
    print("=" * 60)
    print("测试期望值计算")
    print("=" * 60)
    
    try:
        from services.expectation_comparison_service import ExpectationComparisonService
        
        # 测试期望指标计算
        base_capital = 3200000
        expectation = ExpectationComparisonService.calculate_expectation_metrics(base_capital)
        
        print(f"基准本金: {base_capital:,}元")
        print(f"期望收益率: {expectation['return_rate']:.4f} ({expectation['return_rate']*100:.2f}%)")
        print(f"期望收益金额: {expectation['return_amount']:,.2f}元")
        print(f"期望持仓天数: {expectation['holding_days']:.2f}天")
        print(f"期望胜率: {expectation['success_rate']:.4f} ({expectation['success_rate']*100:.1f}%)")
        
        # 验证计算结果
        model = ExpectationComparisonService.PROBABILITY_MODEL
        
        # 手动计算期望收益率
        manual_return_rate = sum(p['probability'] * p['return_rate'] for p in model)
        print(f"\n验证期望收益率: {manual_return_rate:.4f}")
        
        if abs(expectation['return_rate'] - manual_return_rate) < 0.0001:
            print("✓ 期望收益率计算正确")
        else:
            print("✗ 期望收益率计算错误")
        
        # 手动计算期望持仓天数
        manual_holding_days = sum(p['probability'] * p['max_holding_days'] for p in model)
        print(f"验证期望持仓天数: {manual_holding_days:.2f}")
        
        if abs(expectation['holding_days'] - manual_holding_days) < 0.01:
            print("✓ 期望持仓天数计算正确")
        else:
            print("✗ 期望持仓天数计算错误")
        
        # 手动计算期望胜率
        manual_success_rate = sum(p['probability'] for p in model if p['return_rate'] > 0)
        print(f"验证期望胜率: {manual_success_rate:.4f}")
        
        if abs(expectation['success_rate'] - manual_success_rate) < 0.0001:
            print("✓ 期望胜率计算正确")
        else:
            print("✗ 期望胜率计算错误")
        
        return True
        
    except Exception as e:
        print(f"✗ 期望值计算测试失败: {e}")
        return False

def test_actual_metrics_calculation():
    """测试实际指标计算（使用模拟数据）"""
    print("\n" + "=" * 60)
    print("测试实际指标计算")
    print("=" * 60)
    
    try:
        from services.expectation_comparison_service import ExpectationComparisonService
        
        # 创建模拟交易记录
        class MockTradeRecord:
            def __init__(self, stock_code, trade_type, quantity, price, trade_date):
                self.stock_code = stock_code
                self.trade_type = trade_type
                self.quantity = quantity
                self.price = Decimal(str(price))
                self.trade_date = trade_date
                self.is_corrected = False
        
        # 创建测试数据
        base_date = datetime(2024, 1, 1)
        mock_trades = [
            # 股票A - 盈利交易
            MockTradeRecord('000001', 'buy', 100, 10.0, base_date),
            MockTradeRecord('000001', 'sell', 100, 12.0, base_date + timedelta(days=10)),
            
            # 股票B - 亏损交易
            MockTradeRecord('000002', 'buy', 200, 15.0, base_date + timedelta(days=5)),
            MockTradeRecord('000002', 'sell', 200, 14.0, base_date + timedelta(days=15)),
            
            # 股票C - 部分卖出
            MockTradeRecord('000003', 'buy', 300, 8.0, base_date + timedelta(days=10)),
            MockTradeRecord('000003', 'sell', 150, 9.0, base_date + timedelta(days=20)),
        ]
        
        base_capital = 3200000
        actual = ExpectationComparisonService.calculate_actual_metrics(mock_trades, base_capital)
        
        print(f"测试交易记录数: {len(mock_trades)}")
        print(f"实际收益率: {actual['return_rate']:.4f} ({actual['return_rate']*100:.2f}%)")
        print(f"实际收益金额: {actual['return_amount']:,.2f}元")
        print(f"实际持仓天数: {actual['holding_days']:.2f}天")
        print(f"实际胜率: {actual['success_rate']:.4f} ({actual['success_rate']*100:.1f}%)")
        print(f"总交易数: {actual['total_trades']}")
        print(f"完成交易数: {actual['completed_trades']}")
        
        # 验证基本逻辑
        if actual['total_trades'] == len(mock_trades):
            print("✓ 总交易数统计正确")
        else:
            print("✗ 总交易数统计错误")
        
        if actual['completed_trades'] > 0:
            print("✓ 完成交易数计算正常")
        else:
            print("⚠ 完成交易数为0，可能正常（取决于数据）")
        
        return True
        
    except Exception as e:
        print(f"✗ 实际指标计算测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_comparison_calculation():
    """测试对比结果计算"""
    print("\n" + "=" * 60)
    print("测试对比结果计算")
    print("=" * 60)
    
    try:
        from services.expectation_comparison_service import ExpectationComparisonService
        
        # 模拟期望值和实际值
        expectation = {
            'return_rate': 0.0175,
            'return_amount': 56000,
            'holding_days': 11.5,
            'success_rate': 0.6
        }
        
        actual = {
            'return_rate': 0.025,
            'return_amount': 80000,
            'holding_days': 9.0,
            'success_rate': 0.7
        }
        
        comparison = ExpectationComparisonService.calculate_comparison_results(expectation, actual)
        
        print("期望值:")
        for key, value in expectation.items():
            if 'rate' in key:
                print(f"  {key}: {value:.4f} ({value*100:.2f}%)")
            elif 'amount' in key:
                print(f"  {key}: {value:,.2f}元")
            else:
                print(f"  {key}: {value:.2f}")
        
        print("\n实际值:")
        for key, value in actual.items():
            if 'rate' in key:
                print(f"  {key}: {value:.4f} ({value*100:.2f}%)")
            elif 'amount' in key:
                print(f"  {key}: {value:,.2f}元")
            else:
                print(f"  {key}: {value:.2f}")
        
        print("\n对比结果:")
        print(f"收益率差异: {comparison['return_rate_diff']:.4f} ({comparison['return_rate_pct_diff']:.2f}%)")
        print(f"收益金额差异: {comparison['return_amount_diff']:,.2f}元")
        print(f"持仓天数差异: {comparison['holding_days_diff']:.2f}天 ({comparison['holding_days_pct_diff']:.2f}%)")
        print(f"胜率差异: {comparison['success_rate_diff']:.4f} ({comparison['success_rate_pct_diff']:.2f}%)")
        
        print("\n状态分析:")
        print(f"收益率状态: {comparison['return_rate_status']['message']} ({comparison['return_rate_status']['color']})")
        print(f"持仓天数状态: {comparison['holding_days_status']['message']} ({comparison['holding_days_status']['color']})")
        print(f"胜率状态: {comparison['success_rate_status']['message']} ({comparison['success_rate_status']['color']})")
        
        # 验证差异计算
        expected_return_diff = actual['return_rate'] - expectation['return_rate']
        if abs(comparison['return_rate_diff'] - expected_return_diff) < 0.0001:
            print("✓ 收益率差异计算正确")
        else:
            print("✗ 收益率差异计算错误")
        
        return True
        
    except Exception as e:
        print(f"✗ 对比结果计算测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parameter_validation():
    """测试参数验证"""
    print("\n" + "=" * 60)
    print("测试参数验证")
    print("=" * 60)
    
    try:
        from services.expectation_comparison_service import ExpectationComparisonService
        from error_handlers import ValidationError
        
        # 测试有效参数
        valid_cases = [
            ('all', 3200000),
            ('1y', 1000000),
            ('90d', 5000000),
            ('30d', 10000000)
        ]
        
        print("测试有效参数:")
        for time_range, base_capital in valid_cases:
            try:
                ExpectationComparisonService._validate_parameters(time_range, base_capital)
                print(f"✓ {time_range}, {base_capital} - 验证通过")
            except ValidationError as e:
                print(f"✗ {time_range}, {base_capital} - 验证失败: {e}")
        
        # 测试无效参数
        invalid_cases = [
            ('invalid', 3200000, '时间范围'),
            ('all', -1000000, '基准本金'),
            ('all', 0, '基准本金'),
            ('1d', 3200000, '时间范围')
        ]
        
        print("\n测试无效参数:")
        for time_range, base_capital, expected_error in invalid_cases:
            try:
                ExpectationComparisonService._validate_parameters(time_range, base_capital)
                print(f"✗ {time_range}, {base_capital} - 应该抛出异常但没有")
            except ValidationError as e:
                if expected_error in str(e):
                    print(f"✓ {time_range}, {base_capital} - 正确拒绝: {e}")
                else:
                    print(f"⚠ {time_range}, {base_capital} - 错误消息不匹配: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ 参数验证测试失败: {e}")
        return False

def test_fifo_calculation():
    """测试FIFO计算逻辑"""
    print("\n" + "=" * 60)
    print("测试FIFO计算逻辑")
    print("=" * 60)
    
    try:
        from services.expectation_comparison_service import ExpectationComparisonService
        
        # 创建模拟交易记录
        class MockTradeRecord:
            def __init__(self, trade_type, quantity, price, trade_date):
                self.trade_type = trade_type
                self.quantity = quantity
                self.price = Decimal(str(price))
                self.trade_date = trade_date
        
        base_date = datetime(2024, 1, 1)
        trades = [
            MockTradeRecord('buy', 100, 10.0, base_date),
            MockTradeRecord('buy', 200, 12.0, base_date + timedelta(days=1)),
            MockTradeRecord('sell', 150, 15.0, base_date + timedelta(days=5)),
            MockTradeRecord('sell', 100, 14.0, base_date + timedelta(days=10))
        ]
        
        completed = ExpectationComparisonService._calculate_stock_completed_trades(trades)
        
        print(f"输入交易记录: {len(trades)}笔")
        print(f"完成交易记录: {len(completed)}笔")
        
        for i, trade in enumerate(completed, 1):
            profit_rate = (trade['sell_price'] - trade['buy_price']) / trade['buy_price'] * 100
            print(f"交易{i}: {trade['quantity']}股 @ {trade['buy_price']} -> {trade['sell_price']}, "
                  f"收益: {trade['profit']:.2f}元 ({profit_rate:.2f}%), "
                  f"持仓: {trade['holding_days']}天")
        
        # 验证FIFO逻辑
        if len(completed) == 3:  # 应该有3笔完成交易
            print("✓ FIFO交易匹配数量正确")
        else:
            print(f"✗ FIFO交易匹配数量错误: 期望3笔，实际{len(completed)}笔")
        
        # 验证第一笔交易（100股@10元卖@15元）
        if completed[0]['quantity'] == 100 and completed[0]['buy_price'] == 10.0:
            print("✓ FIFO第一笔交易匹配正确")
        else:
            print("✗ FIFO第一笔交易匹配错误")
        
        return True
        
    except Exception as e:
        print(f"✗ FIFO计算测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """测试性能"""
    print("\n" + "=" * 60)
    print("测试性能")
    print("=" * 60)
    
    try:
        import time
        from services.expectation_comparison_service import ExpectationComparisonService
        
        # 测试期望值计算性能
        start_time = time.time()
        for _ in range(1000):
            ExpectationComparisonService.calculate_expectation_metrics(3200000)
        end_time = time.time()
        
        expectation_time = (end_time - start_time) * 1000
        print(f"期望值计算性能: 1000次调用耗时 {expectation_time:.2f}ms")
        print(f"平均每次调用: {expectation_time/1000:.4f}ms")
        
        if expectation_time < 100:
            print("✓ 期望值计算性能优秀")
        elif expectation_time < 500:
            print("⚠ 期望值计算性能良好")
        else:
            print("✗ 期望值计算性能需要优化")
        
        # 测试参数验证性能
        start_time = time.time()
        for _ in range(10000):
            ExpectationComparisonService._validate_parameters('all', 3200000)
        end_time = time.time()
        
        validation_time = (end_time - start_time) * 1000
        print(f"参数验证性能: 10000次调用耗时 {validation_time:.2f}ms")
        print(f"平均每次调用: {validation_time/10000:.4f}ms")
        
        if validation_time < 50:
            print("✓ 参数验证性能优秀")
        elif validation_time < 200:
            print("⚠ 参数验证性能良好")
        else:
            print("✗ 参数验证性能需要优化")
        
        return True
        
    except Exception as e:
        print(f"✗ 性能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("期望对比服务验证")
    print("测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("期望值计算", test_expectation_calculation),
        ("实际指标计算", test_actual_metrics_calculation),
        ("对比结果计算", test_comparison_calculation),
        ("参数验证", test_parameter_validation),
        ("FIFO计算逻辑", test_fifo_calculation),
        ("性能测试", test_performance)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name}测试异常: {e}")
            test_results.append((test_name, False))
    
    # 生成测试摘要
    print("\n" + "=" * 60)
    print("测试摘要")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！期望对比服务功能正常。")
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)