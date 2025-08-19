"""
分批止盈计算算法单元测试
"""
import pytest
from datetime import datetime
from decimal import Decimal
from services.profit_taking_service import ProfitTakingService
from models.profit_taking_target import ProfitTakingTarget
from models.trade_record import TradeRecord
from models.configuration import Configuration
from error_handlers import ValidationError


class TestProfitTakingCalculations:
    """分批止盈计算算法测试"""
    
    def test_calculate_expected_profit_single_target(self, app, db_session):
        """测试单个止盈目标的预期收益计算"""
        with app.app_context():
            buy_price = 10.00
            targets = [
                {
                    'target_price': 12.00,  # 20%涨幅
                    'sell_ratio': 0.50      # 卖出50%
                }
            ]
            
            result = ProfitTakingService.calculate_targets_expected_profit(buy_price, targets)
            
            # 预期收益率 = 20% * 50% = 10%
            assert result['total_expected_profit_ratio'] == pytest.approx(0.10, rel=1e-3)
            assert result['total_sell_ratio'] == 0.50
            assert len(result['targets_detail']) == 1
            
            target_detail = result['targets_detail'][0]
            assert target_detail['profit_ratio'] == pytest.approx(0.20, rel=1e-3)
            assert target_detail['sell_ratio'] == 0.50
            assert target_detail['expected_profit_ratio'] == pytest.approx(0.10, rel=1e-3)
    
    def test_calculate_expected_profit_multiple_targets(self, app, db_session):
        """测试多个止盈目标的预期收益计算"""
        with app.app_context():
            buy_price = 10.00
            targets = [
                {'target_price': 11.00, 'sell_ratio': 0.30},  # 10% * 30% = 3%
                {'target_price': 12.00, 'sell_ratio': 0.40},  # 20% * 40% = 8%
                {'target_price': 13.00, 'sell_ratio': 0.30}   # 30% * 30% = 9%
            ]
            
            result = ProfitTakingService.calculate_targets_expected_profit(buy_price, targets)
            
            # 总预期收益率 = 3% + 8% + 9% = 20%
            assert result['total_expected_profit_ratio'] == pytest.approx(0.20, rel=1e-3)
            assert result['total_sell_ratio'] == 1.00
            assert len(result['targets_detail']) == 3
            
            # 验证每个目标的详细计算
            details = result['targets_detail']
            
            # 第一个目标：11.00价格，10%涨幅，30%卖出
            assert details[0]['profit_ratio'] == pytest.approx(0.10, rel=1e-3)
            assert details[0]['expected_profit_ratio'] == pytest.approx(0.03, rel=1e-3)
            
            # 第二个目标：12.00价格，20%涨幅，40%卖出
            assert details[1]['profit_ratio'] == pytest.approx(0.20, rel=1e-3)
            assert details[1]['expected_profit_ratio'] == pytest.approx(0.08, rel=1e-3)
            
            # 第三个目标：13.00价格，30%涨幅，30%卖出
            assert details[2]['profit_ratio'] == pytest.approx(0.30, rel=1e-3)
            assert details[2]['expected_profit_ratio'] == pytest.approx(0.09, rel=1e-3)
    
    def test_calculate_expected_profit_with_profit_ratio(self, app, db_session):
        """测试使用止盈比例而非价格的预期收益计算"""
        with app.app_context():
            buy_price = 10.00
            targets = [
                {'profit_ratio': 0.15, 'sell_ratio': 0.40},  # 15% * 40% = 6%
                {'profit_ratio': 0.25, 'sell_ratio': 0.35},  # 25% * 35% = 8.75%
                {'profit_ratio': 0.35, 'sell_ratio': 0.25}   # 35% * 25% = 8.75%
            ]
            
            result = ProfitTakingService.calculate_targets_expected_profit(buy_price, targets)
            
            # 总预期收益率 = 6% + 8.75% + 8.75% = 23.5%
            assert result['total_expected_profit_ratio'] == pytest.approx(0.235, rel=1e-3)
            assert result['total_sell_ratio'] == 1.00
            
            # 验证每个目标的计算
            details = result['targets_detail']
            assert details[0]['profit_ratio'] == 0.15
            assert details[0]['expected_profit_ratio'] == pytest.approx(0.06, rel=1e-3)
            
            assert details[1]['profit_ratio'] == 0.25
            assert details[1]['expected_profit_ratio'] == pytest.approx(0.0875, rel=1e-3)
            
            assert details[2]['profit_ratio'] == 0.35
            assert details[2]['expected_profit_ratio'] == pytest.approx(0.0875, rel=1e-3)
    
    def test_calculate_expected_profit_mixed_price_and_ratio(self, app, db_session):
        """测试混合使用价格和比例的预期收益计算"""
        with app.app_context():
            buy_price = 10.00
            targets = [
                {'target_price': 11.00, 'sell_ratio': 0.30},    # 价格方式：10% * 30% = 3%
                {'profit_ratio': 0.25, 'sell_ratio': 0.40},     # 比例方式：25% * 40% = 10%
                {'target_price': 13.50, 'sell_ratio': 0.30}     # 价格方式：35% * 30% = 10.5%
            ]
            
            result = ProfitTakingService.calculate_targets_expected_profit(buy_price, targets)
            
            # 总预期收益率 = 3% + 10% + 10.5% = 23.5%
            assert result['total_expected_profit_ratio'] == pytest.approx(0.235, rel=1e-3)
            assert result['total_sell_ratio'] == 1.00
            
            details = result['targets_detail']
            
            # 第一个目标：从价格计算比例
            assert details[0]['target_price'] == 11.00
            assert details[0]['profit_ratio'] == pytest.approx(0.10, rel=1e-3)
            assert details[0]['expected_profit_ratio'] == pytest.approx(0.03, rel=1e-3)
            
            # 第二个目标：直接使用比例
            assert details[1]['target_price'] is None
            assert details[1]['profit_ratio'] == 0.25
            assert details[1]['expected_profit_ratio'] == pytest.approx(0.10, rel=1e-3)
            
            # 第三个目标：从价格计算比例
            assert details[2]['target_price'] == 13.50
            assert details[2]['profit_ratio'] == pytest.approx(0.35, rel=1e-3)
            assert details[2]['expected_profit_ratio'] == pytest.approx(0.105, rel=1e-3)
    
    def test_calculate_expected_profit_precision(self, app, db_session):
        """测试预期收益计算的精度"""
        with app.app_context():
            buy_price = 12.34
            targets = [
                {'target_price': 13.57, 'sell_ratio': 0.333},  # 复杂的小数计算
                {'profit_ratio': 0.1234, 'sell_ratio': 0.456}, # 高精度小数
                {'target_price': 15.678, 'sell_ratio': 0.211}  # 不规则小数
            ]
            
            result = ProfitTakingService.calculate_targets_expected_profit(buy_price, targets)
            
            # 验证计算结果的精度
            assert isinstance(result['total_expected_profit_ratio'], float)
            assert isinstance(result['total_sell_ratio'], float)
            
            # 验证总卖出比例
            expected_total_sell = 0.333 + 0.456 + 0.211
            assert result['total_sell_ratio'] == pytest.approx(expected_total_sell, rel=1e-3)
            
            # 验证每个目标的计算精度
            details = result['targets_detail']
            
            # 第一个目标：(13.57 - 12.34) / 12.34 * 0.333
            expected_profit_1 = (13.57 - 12.34) / 12.34
            expected_return_1 = expected_profit_1 * 0.333
            assert details[0]['profit_ratio'] == pytest.approx(expected_profit_1, rel=1e-3)
            assert details[0]['expected_profit_ratio'] == pytest.approx(expected_return_1, rel=1e-3)
            
            # 第二个目标：0.1234 * 0.456
            expected_return_2 = 0.1234 * 0.456
            assert details[1]['profit_ratio'] == 0.1234
            assert details[1]['expected_profit_ratio'] == pytest.approx(expected_return_2, rel=1e-3)
    
    def test_calculate_expected_profit_edge_cases(self, app, db_session):
        """测试预期收益计算的边界情况"""
        with app.app_context():
            buy_price = 10.00
            
            # 测试极小的卖出比例
            targets = [
                {'target_price': 11.00, 'sell_ratio': 0.001}  # 0.1%卖出
            ]
            
            result = ProfitTakingService.calculate_targets_expected_profit(buy_price, targets)
            
            # 预期收益率 = 10% * 0.1% = 0.01%
            assert result['total_expected_profit_ratio'] == pytest.approx(0.0001, rel=1e-3)
            assert result['total_sell_ratio'] == 0.001
            
            # 测试极大的止盈比例
            targets = [
                {'profit_ratio': 5.0, 'sell_ratio': 0.10}  # 500%涨幅，10%卖出
            ]
            
            result = ProfitTakingService.calculate_targets_expected_profit(buy_price, targets)
            
            # 预期收益率 = 500% * 10% = 50%
            assert result['total_expected_profit_ratio'] == pytest.approx(0.50, rel=1e-3)
            assert result['total_sell_ratio'] == 0.10
    
    def test_calculate_expected_profit_zero_values(self, app, db_session):
        """测试包含零值的预期收益计算"""
        with app.app_context():
            buy_price = 10.00
            targets = [
                {'target_price': 10.00, 'sell_ratio': 0.50},  # 0%涨幅（止盈价格等于买入价格）
                {'profit_ratio': 0.00, 'sell_ratio': 0.30},   # 0%止盈比例
                {'target_price': 12.00, 'sell_ratio': 0.20}   # 正常目标
            ]
            
            result = ProfitTakingService.calculate_targets_expected_profit(buy_price, targets)
            
            # 只有第三个目标有收益：20% * 20% = 4%
            assert result['total_expected_profit_ratio'] == pytest.approx(0.04, rel=1e-3)
            assert result['total_sell_ratio'] == 1.00
            
            details = result['targets_detail']
            
            # 第一个目标：0%涨幅
            assert details[0]['profit_ratio'] == 0.0
            assert details[0]['expected_profit_ratio'] == 0.0
            
            # 第二个目标：0%止盈比例
            assert details[1]['profit_ratio'] == 0.0
            assert details[1]['expected_profit_ratio'] == 0.0
            
            # 第三个目标：正常计算
            assert details[2]['profit_ratio'] == pytest.approx(0.20, rel=1e-3)
            assert details[2]['expected_profit_ratio'] == pytest.approx(0.04, rel=1e-3)
    
    def test_profit_target_model_calculation(self, app, db_session):
        """测试止盈目标模型内的计算逻辑"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建交易记录
            trade = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=10.00,
                quantity=1000,
                trade_date=datetime.now(),
                reason='少妇B1战法'
            )
            trade.save()
            
            # 测试模型内的自动计算
            target = ProfitTakingTarget(
                trade_record_id=trade.id,
                profit_ratio=0.25,  # 25%止盈比例
                sell_ratio=0.40,    # 40%卖出比例
                sequence_order=1
            )
            
            # 验证预期收益率被自动计算
            assert float(target.expected_profit_ratio) == pytest.approx(0.10, rel=1e-3)  # 25% * 40%
            
            # 测试更新止盈比例后重新计算
            target.profit_ratio = 0.30
            target._calculate_expected_profit()
            
            assert float(target.expected_profit_ratio) == pytest.approx(0.12, rel=1e-3)  # 30% * 40%
            
            # 测试更新卖出比例后重新计算
            target.sell_ratio = 0.50
            target._calculate_expected_profit()
            
            assert float(target.expected_profit_ratio) == pytest.approx(0.15, rel=1e-3)  # 30% * 50%
    
    def test_price_ratio_conversion_accuracy(self, app, db_session):
        """测试价格和比例转换的准确性"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            trade = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=10.00,
                quantity=1000,
                trade_date=datetime.now(),
                reason='少妇B1战法'
            )
            trade.save()
            
            # 测试从价格计算比例
            target = ProfitTakingTarget(
                trade_record_id=trade.id,
                target_price=12.50,  # 25%涨幅
                sell_ratio=0.40,
                sequence_order=1
            )
            
            target.update_profit_ratio_from_price(10.00)
            
            # 验证计算的止盈比例
            assert float(target.profit_ratio) == pytest.approx(0.25, rel=1e-3)
            assert float(target.expected_profit_ratio) == pytest.approx(0.10, rel=1e-3)
            
            # 测试从比例计算价格
            target2 = ProfitTakingTarget(
                trade_record_id=trade.id,
                profit_ratio=0.30,  # 30%止盈比例
                sell_ratio=0.50,
                sequence_order=2
            )
            
            target2.update_target_price_from_ratio(10.00)
            
            # 验证计算的止盈价格
            assert float(target2.target_price) == pytest.approx(13.00, rel=1e-3)  # 10.00 * 1.30
            assert float(target2.expected_profit_ratio) == pytest.approx(0.15, rel=1e-3)
    
    def test_complex_calculation_scenario(self, app, db_session):
        """测试复杂的计算场景"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建交易记录
            trade = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=8.88,  # 使用不规则的买入价格
                quantity=1000,
                trade_date=datetime.now(),
                reason='少妇B1战法'
            )
            trade.save()
            
            # 创建复杂的止盈目标组合
            targets_data = [
                {'target_price': 9.77, 'sell_ratio': 0.25},    # 约10%涨幅
                {'profit_ratio': 0.1518, 'sell_ratio': 0.33},  # 15.18%止盈比例
                {'target_price': 11.55, 'sell_ratio': 0.22},   # 约30%涨幅
                {'profit_ratio': 0.4444, 'sell_ratio': 0.20}   # 44.44%止盈比例
            ]
            
            # 使用服务计算预期收益
            result = ProfitTakingService.calculate_targets_expected_profit(8.88, targets_data)
            
            # 验证总卖出比例
            expected_total_sell = 0.25 + 0.33 + 0.22 + 0.20
            assert result['total_sell_ratio'] == pytest.approx(expected_total_sell, rel=1e-3)
            
            # 验证每个目标的计算
            details = result['targets_detail']
            
            # 第一个目标：从价格计算
            profit_ratio_1 = (9.77 - 8.88) / 8.88
            expected_return_1 = profit_ratio_1 * 0.25
            assert details[0]['profit_ratio'] == pytest.approx(profit_ratio_1, rel=1e-3)
            assert details[0]['expected_profit_ratio'] == pytest.approx(expected_return_1, rel=1e-3)
            
            # 第二个目标：直接使用比例
            expected_return_2 = 0.1518 * 0.33
            assert details[1]['profit_ratio'] == 0.1518
            assert details[1]['expected_profit_ratio'] == pytest.approx(expected_return_2, rel=1e-3)
            
            # 第三个目标：从价格计算
            profit_ratio_3 = (11.55 - 8.88) / 8.88
            expected_return_3 = profit_ratio_3 * 0.22
            assert details[2]['profit_ratio'] == pytest.approx(profit_ratio_3, rel=1e-3)
            assert details[2]['expected_profit_ratio'] == pytest.approx(expected_return_3, rel=1e-3)
            
            # 第四个目标：直接使用比例
            expected_return_4 = 0.4444 * 0.20
            assert details[3]['profit_ratio'] == 0.4444
            assert details[3]['expected_profit_ratio'] == pytest.approx(expected_return_4, rel=1e-3)
            
            # 验证总预期收益率
            expected_total_return = expected_return_1 + expected_return_2 + expected_return_3 + expected_return_4
            assert result['total_expected_profit_ratio'] == pytest.approx(expected_total_return, rel=1e-3)