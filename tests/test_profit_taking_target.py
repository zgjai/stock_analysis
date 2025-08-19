"""
分批止盈目标模型单元测试
"""
import pytest
from datetime import datetime
from decimal import Decimal
from models.profit_taking_target import ProfitTakingTarget
from models.trade_record import TradeRecord
from models.configuration import Configuration
from error_handlers import ValidationError


class TestProfitTakingTarget:
    """分批止盈目标模型测试"""
    
    def test_create_valid_profit_target(self, app, db_session):
        """测试创建有效的止盈目标"""
        with app.app_context():
            # 先创建一个交易记录
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
            target = ProfitTakingTarget(
                trade_record_id=trade.id,
                target_price=12.00,
                profit_ratio=0.20,
                sell_ratio=0.50,
                sequence_order=1
            )
            target.save()
            
            assert target.id is not None
            assert target.trade_record_id == trade.id
            assert float(target.target_price) == 12.00
            assert float(target.profit_ratio) == 0.20
            assert float(target.sell_ratio) == 0.50
            assert float(target.expected_profit_ratio) == 0.10  # 0.20 * 0.50
            assert target.sequence_order == 1
    
    def test_create_profit_target_invalid_sell_ratio(self, app, db_session):
        """测试创建止盈目标时卖出比例无效"""
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
            
            # 测试卖出比例为0
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingTarget(
                    trade_record_id=trade.id,
                    sell_ratio=0,
                    sequence_order=1
                )
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'sell_ratio' in str(error.details)
            
            # 测试卖出比例超过100%
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingTarget(
                    trade_record_id=trade.id,
                    sell_ratio=1.5,
                    sequence_order=1
                )
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'sell_ratio' in str(error.details)
    
    def test_create_profit_target_invalid_profit_ratio(self, app, db_session):
        """测试创建止盈目标时止盈比例无效"""
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
            
            # 测试止盈比例为负数
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingTarget(
                    trade_record_id=trade.id,
                    profit_ratio=-0.10,
                    sell_ratio=0.50,
                    sequence_order=1
                )
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'profit_ratio' in str(error.details)
            
            # 测试止盈比例超过1000%
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingTarget(
                    trade_record_id=trade.id,
                    profit_ratio=15.0,  # 1500%
                    sell_ratio=0.50,
                    sequence_order=1
                )
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'profit_ratio' in str(error.details)
    
    def test_create_profit_target_invalid_target_price(self, app, db_session):
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
            
            # 测试止盈价格为负数
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingTarget(
                    trade_record_id=trade.id,
                    target_price=-5.00,
                    sell_ratio=0.50,
                    sequence_order=1
                )
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'target_price' in str(error.details)
    
    def test_create_profit_target_invalid_sequence_order(self, app, db_session):
        """测试创建止盈目标时序列顺序无效"""
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
            
            # 测试序列顺序为0
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingTarget(
                    trade_record_id=trade.id,
                    sell_ratio=0.50,
                    sequence_order=0
                )
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'sequence_order' in str(error.details)
            
            # 测试序列顺序为负数
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingTarget(
                    trade_record_id=trade.id,
                    sell_ratio=0.50,
                    sequence_order=-1
                )
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'sequence_order' in str(error.details)
    
    def test_create_profit_target_missing_sell_ratio(self, app, db_session):
        """测试创建止盈目标时缺少卖出比例"""
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
            
            with pytest.raises(ValidationError) as exc_info:
                ProfitTakingTarget(
                    trade_record_id=trade.id,
                    target_price=12.00,
                    sequence_order=1
                    # 缺少 sell_ratio
                )
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'sell_ratio' in str(error.details)
    
    def test_validate_against_buy_price_success(self, app, db_session):
        """测试相对于买入价格的验证成功"""
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
            
            target = ProfitTakingTarget(
                trade_record_id=trade.id,
                target_price=12.00,
                profit_ratio=0.20,
                sell_ratio=0.50,
                sequence_order=1
            )
            
            # 验证应该成功
            result = target.validate_against_buy_price(10.00)
            assert result is True
    
    def test_validate_against_buy_price_invalid_target_price(self, app, db_session):
        """测试相对于买入价格的验证失败 - 止盈价格无效"""
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
            
            target = ProfitTakingTarget(
                trade_record_id=trade.id,
                target_price=8.00,  # 止盈价格低于买入价格
                sell_ratio=0.50,
                sequence_order=1
            )
            
            with pytest.raises(ValidationError) as exc_info:
                target.validate_against_buy_price(10.00)
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'target_price' in str(error.details)
    
    def test_validate_against_buy_price_too_high_target_price(self, app, db_session):
        """测试相对于买入价格的验证失败 - 止盈价格过高"""
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
            
            target = ProfitTakingTarget(
                trade_record_id=trade.id,
                target_price=150.00,  # 止盈价格超过买入价格的10倍
                sell_ratio=0.50,
                sequence_order=1
            )
            
            with pytest.raises(ValidationError) as exc_info:
                target.validate_against_buy_price(10.00)
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'target_price' in str(error.details)
    
    def test_validate_against_buy_price_inconsistent_price_ratio(self, app, db_session):
        """测试相对于买入价格的验证失败 - 价格和比例不一致"""
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
            
            target = ProfitTakingTarget(
                trade_record_id=trade.id,
                target_price=12.00,  # 20%涨幅
                profit_ratio=0.50,   # 但设置为50%
                sell_ratio=0.50,
                sequence_order=1
            )
            
            with pytest.raises(ValidationError) as exc_info:
                target.validate_against_buy_price(10.00)
            error = exc_info.value
            assert hasattr(error, 'details')
            assert 'consistency' in str(error.details)
    
    def test_update_profit_ratio_from_price(self, app, db_session):
        """测试根据价格更新止盈比例"""
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
            
            target = ProfitTakingTarget(
                trade_record_id=trade.id,
                target_price=12.00,
                sell_ratio=0.50,
                sequence_order=1
            )
            
            target.update_profit_ratio_from_price(10.00)
            
            # 止盈比例应该被自动计算为 (12.00 - 10.00) / 10.00 = 0.20
            assert float(target.profit_ratio) == pytest.approx(0.20, rel=1e-3)
            assert float(target.expected_profit_ratio) == pytest.approx(0.10, rel=1e-3)  # 0.20 * 0.50
    
    def test_update_target_price_from_ratio(self, app, db_session):
        """测试根据比例更新止盈价格"""
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
            
            target = ProfitTakingTarget(
                trade_record_id=trade.id,
                profit_ratio=0.20,
                sell_ratio=0.50,
                sequence_order=1
            )
            
            target.update_target_price_from_ratio(10.00)
            
            # 止盈价格应该被自动计算为 10.00 * (1 + 0.20) = 12.00
            assert float(target.target_price) == pytest.approx(12.00, rel=1e-3)
            assert float(target.expected_profit_ratio) == pytest.approx(0.10, rel=1e-3)  # 0.20 * 0.50
    
    def test_get_by_trade_record(self, app, db_session):
        """测试根据交易记录ID获取止盈目标"""
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
            
            # 创建多个止盈目标
            targets_data = [
                {'target_price': 11.00, 'sell_ratio': 0.30, 'sequence_order': 1},
                {'target_price': 12.00, 'sell_ratio': 0.40, 'sequence_order': 2},
                {'target_price': 13.00, 'sell_ratio': 0.30, 'sequence_order': 3}
            ]
            
            for data in targets_data:
                target = ProfitTakingTarget(
                    trade_record_id=trade.id,
                    **data
                )
                target.save()
            
            # 获取所有止盈目标
            targets = ProfitTakingTarget.get_by_trade_record(trade.id)
            
            assert len(targets) == 3
            # 验证按序列顺序排序
            assert targets[0].sequence_order == 1
            assert targets[1].sequence_order == 2
            assert targets[2].sequence_order == 3
            assert float(targets[0].target_price) == 11.00
            assert float(targets[1].target_price) == 12.00
            assert float(targets[2].target_price) == 13.00
    
    def test_delete_by_trade_record(self, app, db_session):
        """测试删除指定交易记录的所有止盈目标"""
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
            target1 = ProfitTakingTarget(
                trade_record_id=trade.id,
                target_price=11.00,
                sell_ratio=0.50,
                sequence_order=1
            )
            target1.save()
            
            target2 = ProfitTakingTarget(
                trade_record_id=trade.id,
                target_price=12.00,
                sell_ratio=0.50,
                sequence_order=2
            )
            target2.save()
            
            # 验证目标已创建
            targets = ProfitTakingTarget.get_by_trade_record(trade.id)
            assert len(targets) == 2
            
            # 删除所有目标
            result = ProfitTakingTarget.delete_by_trade_record(trade.id)
            assert result is True
            
            # 验证目标已删除
            targets = ProfitTakingTarget.get_by_trade_record(trade.id)
            assert len(targets) == 0
    
    def test_to_dict(self, app, db_session):
        """测试转换为字典"""
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
            
            target = ProfitTakingTarget(
                trade_record_id=trade.id,
                target_price=12.00,
                profit_ratio=0.20,
                sell_ratio=0.50,
                sequence_order=1
            )
            target.save()
            
            target_dict = target.to_dict()
            
            assert target_dict['trade_record_id'] == trade.id
            assert isinstance(target_dict['target_price'], float)
            assert isinstance(target_dict['profit_ratio'], float)
            assert isinstance(target_dict['sell_ratio'], float)
            assert isinstance(target_dict['expected_profit_ratio'], float)
            assert target_dict['sequence_order'] == 1
            
            # 验证数值正确性
            assert target_dict['target_price'] == 12.00
            assert target_dict['profit_ratio'] == pytest.approx(0.20, rel=1e-3)
            assert target_dict['sell_ratio'] == 0.50
            assert target_dict['expected_profit_ratio'] == pytest.approx(0.10, rel=1e-3)
    
    def test_auto_calculate_profit_ratio_from_price(self, app, db_session):
        """测试根据止盈价格自动计算止盈比例"""
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
            
            # 只提供止盈价格，不提供止盈比例
            target = ProfitTakingTarget(
                trade_record_id=trade.id,
                target_price=12.00,
                sell_ratio=0.50,
                sequence_order=1
            )
            
            # 验证相对于买入价格时，应该自动计算止盈比例
            target.validate_against_buy_price(10.00)
            
            # 止盈比例应该被自动计算
            assert target.profit_ratio is not None
            assert float(target.profit_ratio) == pytest.approx(0.20, rel=1e-3)
            assert float(target.expected_profit_ratio) == pytest.approx(0.10, rel=1e-3)
    
    def test_expected_profit_calculation(self, app, db_session):
        """测试预期收益率计算"""
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
            
            # 测试不同的止盈比例和卖出比例组合
            test_cases = [
                {'profit_ratio': 0.10, 'sell_ratio': 0.50, 'expected': 0.05},
                {'profit_ratio': 0.20, 'sell_ratio': 0.30, 'expected': 0.06},
                {'profit_ratio': 0.15, 'sell_ratio': 1.00, 'expected': 0.15},
                {'profit_ratio': 0.25, 'sell_ratio': 0.40, 'expected': 0.10}
            ]
            
            for i, case in enumerate(test_cases):
                target = ProfitTakingTarget(
                    trade_record_id=trade.id,
                    profit_ratio=case['profit_ratio'],
                    sell_ratio=case['sell_ratio'],
                    sequence_order=i + 1
                )
                
                assert float(target.expected_profit_ratio) == pytest.approx(case['expected'], rel=1e-3)