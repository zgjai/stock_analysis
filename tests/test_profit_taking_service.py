"""
分批止盈服务单元测试
"""
import pytest
from datetime import datetime
from decimal import Decimal
from services.profit_taking_service import ProfitTakingService
from models.profit_taking_target import ProfitTakingTarget
from models.trade_record import TradeRecord
from models.configuration import Configuration
from error_handlers import ValidationError, NotFoundError, DatabaseError


class TestProfitTakingService:
    """分批止盈服务测试"""
    
    def test_create_profit_targets_success(self, app, db_session):
        """测试创建止盈目标成功"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建买入交易记录
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
            
            # 准备止盈目标数据
            targets_data = [
                {
                    'target_price': 11.00,
                    'profit_ratio': 0.10,
                    'sell_ratio': 0.30
                },
                {
                    'target_price': 12.00,
                    'profit_ratio': 0.20,
                    'sell_ratio': 0.40
                },
                {
                    'target_price': 13.00,
                    'profit_ratio': 0.30,
                    'sell_ratio': 0.30
                }
            ]
            
            # 创建止盈目标
            created_targets = ProfitTakingService.create_profit_targets(trade.id, targets_data)
            
            assert len(created_targets) == 3
            
            # 验证第一个目标
            target1 = created_targets[0]
            assert target1.trade_record_id == trade.id
            assert float(target1.target_price) == 11.00
            assert float(target1.profit_ratio) == pytest.approx(0.10, rel=1e-3)
            assert float(target1.sell_ratio) == 0.30
            assert target1.sequence_order == 1
            
            # 验证第二个目标
            target2 = created_targets[1]
            assert float(target2.target_price) == 12.00
            assert target2.sequence_order == 2
            
            # 验证第三个目标
            target3 = created_targets[2]
            assert float(target3.target_price) == 13.00
            assert target3.sequence_order == 3
            
            # 验证交易记录的分批止盈标志被设置
            updated_trade = TradeRecord.get_by_id(trade.id)
            assert updated_trade.use_batch_profit_taking is True
    
    def test_create_profit_targets_trade_not_found(self, app, db_session):
        """测试创建止盈目标时交易记录不存在"""
        with app.app_context():
            targets_data = [
                {'target_price': 11.00, 'sell_ratio': 0.50}
            ]
            
            with pytest.raises(NotFoundError) as exc_info:
                ProfitTakingService.create_profit_targets(99999, targets_data)
            
            assert "交易记录 99999 不存在" in str(exc_info.value)
    
    def test_create_profit_targets_not_buy_trade(self, app, db_session):
        """测试为非买入交易记录创建止盈目标"""
        with app.app_context():
            Configuration.set_sell_reasons(['部分止盈'])
            
            # 创建卖出交易记录
            trade = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='sell',
                price=12.00,
                quantity=500,
                trade_date=datetime.now(),
                reason='部分止盈'
            )
            trade.save()
            
            targets_data = [
                {'target_price': 13.00, 'sell_ratio': 0.50}
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.create_profit_targets(trade.id, targets_data)
            
            assert "只有买入记录才能设置止盈目标" in str(exc_info.value)
    
    def test_create_profit_targets_invalid_total_ratio(self, app, db_session):
        """测试创建止盈目标时总卖出比例超过100%"""
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
            
            # 总卖出比例超过100%
            targets_data = [
                {'target_price': 11.00, 'sell_ratio': 0.60},
                {'target_price': 12.00, 'sell_ratio': 0.50}  # 总计110%
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.create_profit_targets(trade.id, targets_data)
            
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'total_sell_ratio' in str(error.details)
    
    def test_create_profit_targets_invalid_target_price(self, app, db_session):
        """测试创建止盈目标时止盈价格无效"""
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
            
            # 止盈价格低于买入价格
            targets_data = [
                {'target_price': 8.00, 'sell_ratio': 0.50}  # 低于买入价格10.00
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.create_profit_targets(trade.id, targets_data)
            
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'target_price' in str(error.details)
    
    def test_update_profit_targets_success(self, app, db_session):
        """测试更新止盈目标成功"""
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
            
            # 先创建初始止盈目标
            initial_targets = [
                {'target_price': 11.00, 'sell_ratio': 0.50}
            ]
            ProfitTakingService.create_profit_targets(trade.id, initial_targets)
            
            # 更新止盈目标
            updated_targets_data = [
                {'target_price': 11.50, 'sell_ratio': 0.30},
                {'target_price': 12.50, 'sell_ratio': 0.40},
                {'target_price': 13.50, 'sell_ratio': 0.30}
            ]
            
            updated_targets = ProfitTakingService.update_profit_targets(trade.id, updated_targets_data)
            
            assert len(updated_targets) == 3
            assert float(updated_targets[0].target_price) == 11.50
            assert float(updated_targets[1].target_price) == 12.50
            assert float(updated_targets[2].target_price) == 13.50
    
    def test_get_profit_targets_success(self, app, db_session):
        """测试获取止盈目标成功"""
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
            
            # 创建止盈目标
            targets_data = [
                {'target_price': 11.00, 'sell_ratio': 0.30},
                {'target_price': 12.00, 'sell_ratio': 0.40}
            ]
            ProfitTakingService.create_profit_targets(trade.id, targets_data)
            
            # 获取止盈目标
            targets = ProfitTakingService.get_profit_targets(trade.id)
            
            assert len(targets) == 2
            assert float(targets[0].target_price) == 11.00
            assert float(targets[1].target_price) == 12.00
    
    def test_get_profit_targets_trade_not_found(self, app, db_session):
        """测试获取不存在交易记录的止盈目标"""
        with app.app_context():
            with pytest.raises(NotFoundError) as exc_info:
                ProfitTakingService.get_profit_targets(99999)
            
            assert "交易记录 99999 不存在" in str(exc_info.value)
    
    def test_delete_profit_targets_success(self, app, db_session):
        """测试删除止盈目标成功"""
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
            
            # 创建止盈目标
            targets_data = [
                {'target_price': 11.00, 'sell_ratio': 0.50}
            ]
            ProfitTakingService.create_profit_targets(trade.id, targets_data)
            
            # 验证目标已创建
            targets = ProfitTakingService.get_profit_targets(trade.id)
            assert len(targets) == 1
            
            # 删除止盈目标
            result = ProfitTakingService.delete_profit_targets(trade.id)
            assert result is True
            
            # 验证目标已删除
            targets = ProfitTakingService.get_profit_targets(trade.id)
            assert len(targets) == 0
            
            # 验证交易记录的分批止盈标志被清除
            updated_trade = TradeRecord.get_by_id(trade.id)
            assert updated_trade.use_batch_profit_taking is False
    
    def test_validate_targets_total_ratio_success(self, app, db_session):
        """测试验证止盈目标总比例成功"""
        with app.app_context():
            targets = [
                {'sell_ratio': 0.30, 'target_price': 11.00},
                {'sell_ratio': 0.40, 'target_price': 12.00},
                {'sell_ratio': 0.30, 'target_price': 13.00}
            ]
            
            result = ProfitTakingService.validate_targets_total_ratio(targets)
            assert result is True
    
    def test_validate_targets_total_ratio_empty_targets(self, app, db_session):
        """测试验证空的止盈目标列表"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.validate_targets_total_ratio([])
            
            assert "至少需要设置一个止盈目标" in str(exc_info.value)
    
    def test_validate_targets_total_ratio_exceed_100_percent(self, app, db_session):
        """测试验证止盈目标总比例超过100%"""
        with app.app_context():
            targets = [
                {'sell_ratio': 0.60, 'target_price': 11.00},
                {'sell_ratio': 0.50, 'target_price': 12.00}  # 总计110%
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.validate_targets_total_ratio(targets)
            
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'total_sell_ratio' in str(error.details)
    
    def test_validate_targets_total_ratio_invalid_sell_ratio(self, app, db_session):
        """测试验证无效的卖出比例"""
        with app.app_context():
            # 测试卖出比例为0
            targets = [
                {'sell_ratio': 0, 'target_price': 11.00}
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.validate_targets_total_ratio(targets)
            
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'sell_ratio' in str(error.details)
            
            # 测试卖出比例超过100%
            targets = [
                {'sell_ratio': 1.5, 'target_price': 11.00}
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.validate_targets_total_ratio(targets)
            
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'sell_ratio' in str(error.details)
    
    def test_validate_targets_total_ratio_missing_sell_ratio(self, app, db_session):
        """测试验证缺少卖出比例"""
        with app.app_context():
            targets = [
                {'target_price': 11.00}  # 缺少 sell_ratio
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.validate_targets_total_ratio(targets)
            
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'sell_ratio' in str(error.details)
    
    def test_validate_targets_against_buy_price_success(self, app, db_session):
        """测试验证止盈目标相对于买入价格成功"""
        with app.app_context():
            buy_price = 10.00
            targets = [
                {'target_price': 11.00, 'profit_ratio': 0.10, 'sell_ratio': 0.30},
                {'target_price': 12.00, 'profit_ratio': 0.20, 'sell_ratio': 0.40}
            ]
            
            result = ProfitTakingService.validate_targets_against_buy_price(buy_price, targets)
            assert result is True
    
    def test_validate_targets_against_buy_price_invalid_buy_price(self, app, db_session):
        """测试验证无效的买入价格"""
        with app.app_context():
            targets = [
                {'target_price': 11.00, 'sell_ratio': 0.50}
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.validate_targets_against_buy_price(0, targets)
            
            assert "买入价格必须大于0" in str(exc_info.value)
    
    def test_validate_targets_against_buy_price_target_price_too_low(self, app, db_session):
        """测试验证止盈价格低于买入价格"""
        with app.app_context():
            buy_price = 10.00
            targets = [
                {'target_price': 8.00, 'sell_ratio': 0.50}  # 低于买入价格
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.validate_targets_against_buy_price(buy_price, targets)
            
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'target_price' in str(error.details)
    
    def test_validate_targets_against_buy_price_target_price_too_high(self, app, db_session):
        """测试验证止盈价格过高"""
        with app.app_context():
            buy_price = 10.00
            targets = [
                {'target_price': 150.00, 'sell_ratio': 0.50}  # 超过买入价格的10倍
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.validate_targets_against_buy_price(buy_price, targets)
            
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'target_price' in str(error.details)
    
    def test_validate_targets_against_buy_price_inconsistent_price_ratio(self, app, db_session):
        """测试验证止盈价格和比例不一致"""
        with app.app_context():
            buy_price = 10.00
            targets = [
                {
                    'target_price': 12.00,  # 20%涨幅
                    'profit_ratio': 0.50,   # 但设置为50%
                    'sell_ratio': 0.50
                }
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.validate_targets_against_buy_price(buy_price, targets)
            
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'consistency' in str(error.details)
    
    def test_calculate_targets_expected_profit_success(self, app, db_session):
        """测试计算止盈目标预期收益成功"""
        with app.app_context():
            buy_price = 10.00
            targets = [
                {'target_price': 11.00, 'sell_ratio': 0.30},  # 10% * 30% = 3%
                {'target_price': 12.00, 'sell_ratio': 0.40},  # 20% * 40% = 8%
                {'profit_ratio': 0.30, 'sell_ratio': 0.30}    # 30% * 30% = 9%
            ]
            
            result = ProfitTakingService.calculate_targets_expected_profit(buy_price, targets)
            
            assert result['total_expected_profit_ratio'] == pytest.approx(0.20, rel=1e-3)  # 3% + 8% + 9%
            assert result['total_sell_ratio'] == 1.00  # 30% + 40% + 30%
            assert len(result['targets_detail']) == 3
            
            # 验证第一个目标详情
            target1 = result['targets_detail'][0]
            assert target1['sequence_order'] == 1
            assert target1['target_price'] == 11.00
            assert target1['profit_ratio'] == pytest.approx(0.10, rel=1e-3)
            assert target1['sell_ratio'] == 0.30
            assert target1['expected_profit_ratio'] == pytest.approx(0.03, rel=1e-3)
    
    def test_calculate_targets_expected_profit_empty_targets(self, app, db_session):
        """测试计算空止盈目标列表的预期收益"""
        with app.app_context():
            buy_price = 10.00
            targets = []
            
            result = ProfitTakingService.calculate_targets_expected_profit(buy_price, targets)
            
            assert result['total_expected_profit_ratio'] == 0.0
            assert result['total_sell_ratio'] == 0.0
            assert len(result['targets_detail']) == 0
    
    def test_calculate_targets_expected_profit_invalid_buy_price(self, app, db_session):
        """测试计算预期收益时买入价格无效"""
        with app.app_context():
            targets = [
                {'target_price': 11.00, 'sell_ratio': 0.50}
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.calculate_targets_expected_profit(0, targets)
            
            assert "买入价格必须大于0" in str(exc_info.value)
    
    def test_calculate_targets_expected_profit_invalid_data_format(self, app, db_session):
        """测试计算预期收益时数据格式无效"""
        with app.app_context():
            buy_price = 10.00
            targets = [
                {'target_price': 'invalid', 'sell_ratio': 0.50}  # 无效的价格格式
            ]
            
            # This should raise a ValidationError due to invalid decimal conversion
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.calculate_targets_expected_profit(buy_price, targets)
            
            error = exc_info.value
            assert "价格格式无效" in str(error) or "第1个止盈目标" in str(error)
    
    def test_get_targets_summary_success(self, app, db_session):
        """测试获取止盈目标汇总信息成功"""
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
            
            # 创建止盈目标
            targets_data = [
                {'target_price': 11.00, 'sell_ratio': 0.30},
                {'target_price': 12.00, 'sell_ratio': 0.40}
            ]
            ProfitTakingService.create_profit_targets(trade.id, targets_data)
            
            # 获取汇总信息
            summary = ProfitTakingService.get_targets_summary(trade.id)
            
            assert summary['trade_id'] == trade.id
            assert summary['use_batch_profit_taking'] is True
            assert summary['targets_count'] == 2
            assert summary['total_sell_ratio'] == 0.70
            assert summary['total_expected_profit_ratio'] > 0
            assert len(summary['targets']) == 2
    
    def test_get_targets_summary_no_targets(self, app, db_session):
        """测试获取没有止盈目标的交易记录汇总信息"""
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
            
            # 获取汇总信息（没有创建止盈目标）
            summary = ProfitTakingService.get_targets_summary(trade.id)
            
            assert summary['trade_id'] == trade.id
            assert summary['use_batch_profit_taking'] is False
            assert summary['targets_count'] == 0
            assert summary['total_sell_ratio'] == 0.0
            assert summary['total_expected_profit_ratio'] == 0.0
            assert len(summary['targets']) == 0
    
    def test_get_targets_summary_trade_not_found(self, app, db_session):
        """测试获取不存在交易记录的汇总信息"""
        with app.app_context():
            with pytest.raises(NotFoundError) as exc_info:
                ProfitTakingService.get_targets_summary(99999)
            
            assert "交易记录 99999 不存在" in str(exc_info.value)
    
    def test_create_profit_targets_replaces_existing(self, app, db_session):
        """测试创建止盈目标会替换现有目标"""
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
            
            # 创建初始止盈目标
            initial_targets = [
                {'target_price': 11.00, 'sell_ratio': 0.50}
            ]
            ProfitTakingService.create_profit_targets(trade.id, initial_targets)
            
            # 验证初始目标已创建
            targets = ProfitTakingService.get_profit_targets(trade.id)
            assert len(targets) == 1
            assert float(targets[0].target_price) == 11.00
            
            # 创建新的止盈目标（应该替换现有的）
            new_targets = [
                {'target_price': 12.00, 'sell_ratio': 0.30},
                {'target_price': 13.00, 'sell_ratio': 0.40}
            ]
            ProfitTakingService.create_profit_targets(trade.id, new_targets)
            
            # 验证新目标已替换旧目标
            targets = ProfitTakingService.get_profit_targets(trade.id)
            assert len(targets) == 2
            assert float(targets[0].target_price) == 12.00
            assert float(targets[1].target_price) == 13.00
    
    def test_validate_targets_with_detailed_errors(self, app, db_session):
        """测试验证止盈目标时返回详细错误信息"""
        with app.app_context():
            targets = [
                {
                    'sell_ratio': 0,  # 无效：卖出比例为0
                    'target_price': -5.00,  # 无效：价格为负数
                    'profit_ratio': -0.10,  # 无效：止盈比例为负数
                    'sequence_order': 0  # 无效：序列顺序为0
                },
                {
                    'sell_ratio': 1.5,  # 无效：卖出比例超过100%
                    'profit_ratio': 15.0  # 无效：止盈比例超过1000%
                }
            ]
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingService.validate_targets_total_ratio(targets)
            
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'targets[0]' in error.details
            assert 'targets[1]' in error.details
            
            # 验证第一个目标的错误详情
            target0_errors = error.details['targets[0]']
            assert 'sell_ratio' in target0_errors
            assert 'target_price' in target0_errors
            assert 'profit_ratio' in target0_errors
            assert 'sequence_order' in target0_errors
            
            # 验证第二个目标的错误详情
            target1_errors = error.details['targets[1]']
            assert 'sell_ratio' in target1_errors
            assert 'profit_ratio' in target1_errors