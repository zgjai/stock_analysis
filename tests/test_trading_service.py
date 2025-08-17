"""
交易记录管理服务单元测试
"""
import pytest
from datetime import datetime, date
from decimal import Decimal
from services.trading_service import TradingService, TradingConfigService
from models.trade_record import TradeRecord, TradeCorrection
from models.configuration import Configuration
from error_handlers import ValidationError, NotFoundError, DatabaseError


class TestTradingService:
    """交易记录服务测试"""
    
    def test_create_buy_trade_success(self, app, db_session):
        """测试创建买入交易记录成功"""
        with app.app_context():
            # 设置买入原因配置
            Configuration.set_buy_reasons(['少妇B1战法', '少妇SB1战法'])
            
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法',
                'stop_loss_price': 11.00,
                'take_profit_ratio': 0.20,
                'sell_ratio': 0.50,
                'notes': '测试买入'
            }
            
            trade = TradingService.create_trade(trade_data)
            
            assert trade.id is not None
            assert trade.stock_code == '000001'
            assert trade.stock_name == '平安银行'
            assert trade.trade_type == 'buy'
            assert float(trade.price) == 12.50
            assert trade.quantity == 1000
            assert trade.reason == '少妇B1战法'
            assert float(trade.stop_loss_price) == 11.00
            assert float(trade.take_profit_ratio) == 0.20
            assert float(trade.sell_ratio) == 0.50
            assert trade.notes == '测试买入'
            
            # 验证自动计算的字段
            assert trade.expected_loss_ratio is not None
            assert trade.expected_profit_ratio is not None
            assert float(trade.expected_loss_ratio) == pytest.approx(0.12, rel=1e-2)  # (12.5-11)/12.5
            assert float(trade.expected_profit_ratio) == pytest.approx(0.10, rel=1e-2)  # 0.2*0.5
    
    def test_create_sell_trade_success(self, app, db_session):
        """测试创建卖出交易记录成功"""
        with app.app_context():
            # 设置卖出原因配置
            Configuration.set_sell_reasons(['部分止盈', '止损'])
            
            trade_data = {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'sell',
                'price': 15.80,
                'quantity': 500,
                'reason': '部分止盈',
                'notes': '测试卖出'
            }
            
            trade = TradingService.create_trade(trade_data)
            
            assert trade.id is not None
            assert trade.stock_code == '000002'
            assert trade.trade_type == 'sell'
            assert float(trade.price) == 15.80
            assert trade.reason == '部分止盈'
    
    def test_create_trade_invalid_reason(self, app, db_session):
        """测试创建交易记录时原因无效"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '无效原因'
            }
            
            with pytest.raises(ValidationError) as exc_info:
                TradingService.create_trade(trade_data)
            
            assert "无效的buy原因" in str(exc_info.value)
    
    def test_create_trade_missing_required_fields(self, app, db_session):
        """测试创建交易记录时缺少必填字段"""
        with app.app_context():
            trade_data = {
                'stock_code': '000001',
                'trade_type': 'buy',
                'price': 12.50
                # 缺少 stock_name, quantity, reason
            }
            
            with pytest.raises(ValidationError):
                TradingService.create_trade(trade_data)
    
    def test_update_trade_success(self, app, db_session):
        """测试更新交易记录成功"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法', '少妇B2战法'])
            
            # 先创建一个交易记录
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            trade = TradingService.create_trade(trade_data)
            
            # 更新交易记录
            update_data = {
                'price': 13.00,
                'quantity': 1200,
                'reason': '少妇B2战法',
                'notes': '更新后的备注'
            }
            
            updated_trade = TradingService.update_trade(trade.id, update_data)
            
            assert float(updated_trade.price) == 13.00
            assert updated_trade.quantity == 1200
            assert updated_trade.reason == '少妇B2战法'
            assert updated_trade.notes == '更新后的备注'
    
    def test_update_trade_not_found(self, app, db_session):
        """测试更新不存在的交易记录"""
        with app.app_context():
            with pytest.raises(NotFoundError):
                TradingService.update_trade(99999, {'price': 10.00})
    
    def test_get_trades_with_filters(self, app, db_session):
        """测试获取交易记录列表并应用筛选条件"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            Configuration.set_sell_reasons(['部分止盈'])
            
            # 创建测试数据
            trades_data = [
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': 12.50,
                    'quantity': 1000,
                    'reason': '少妇B1战法',
                    'trade_date': datetime(2024, 1, 1)
                },
                {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'trade_type': 'sell',
                    'price': 15.80,
                    'quantity': 500,
                    'reason': '部分止盈',
                    'trade_date': datetime(2024, 1, 2)
                },
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'sell',
                    'price': 13.20,
                    'quantity': 500,
                    'reason': '部分止盈',
                    'trade_date': datetime(2024, 1, 3)
                }
            ]
            
            for data in trades_data:
                TradingService.create_trade(data)
            
            # 测试按股票代码筛选
            result = TradingService.get_trades(filters={'stock_code': '000001'})
            assert result['total'] == 2
            assert all(trade['stock_code'] == '000001' for trade in result['trades'])
            
            # 测试按交易类型筛选
            result = TradingService.get_trades(filters={'trade_type': 'buy'})
            assert result['total'] == 1
            assert result['trades'][0]['trade_type'] == 'buy'
            
            # 测试按日期范围筛选
            result = TradingService.get_trades(filters={
                'start_date': '2024-01-02',
                'end_date': '2024-01-03'
            })
            assert result['total'] == 2
    
    def test_get_trades_with_pagination(self, app, db_session):
        """测试获取交易记录列表并分页"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建5条测试数据
            for i in range(5):
                trade_data = {
                    'stock_code': f'00000{i+1}',
                    'stock_name': f'股票{i+1}',
                    'trade_type': 'buy',
                    'price': 10.00 + i,
                    'quantity': 1000,
                    'reason': '少妇B1战法'
                }
                TradingService.create_trade(trade_data)
            
            # 测试分页
            result = TradingService.get_trades(page=1, per_page=2)
            
            assert result['total'] == 5
            assert len(result['trades']) == 2
            assert result['pages'] == 3
            assert result['current_page'] == 1
            assert result['has_next'] is True
            assert result['has_prev'] is False
    
    def test_get_trades_with_sorting(self, app, db_session):
        """测试获取交易记录列表并排序"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建测试数据
            trades_data = [
                {'stock_code': '000001', 'stock_name': '平安银行', 'trade_type': 'buy', 
                 'price': 12.50, 'quantity': 1000, 'reason': '少妇B1战法'},
                {'stock_code': '000002', 'stock_name': '万科A', 'trade_type': 'buy', 
                 'price': 15.80, 'quantity': 1000, 'reason': '少妇B1战法'},
                {'stock_code': '000003', 'stock_name': '中国平安', 'trade_type': 'buy', 
                 'price': 10.20, 'quantity': 1000, 'reason': '少妇B1战法'}
            ]
            
            for data in trades_data:
                TradingService.create_trade(data)
            
            # 测试按价格升序排序
            result = TradingService.get_trades(sort_by='price', sort_order='asc')
            prices = [trade['price'] for trade in result['trades']]
            assert prices == sorted(prices)
            
            # 测试按价格降序排序
            result = TradingService.get_trades(sort_by='price', sort_order='desc')
            prices = [trade['price'] for trade in result['trades']]
            assert prices == sorted(prices, reverse=True)
    
    def test_delete_trade_success(self, app, db_session):
        """测试删除交易记录成功"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            trade = TradingService.create_trade(trade_data)
            
            # 删除交易记录
            result = TradingService.delete_trade(trade.id)
            assert result is True
            
            # 验证记录已被删除
            with pytest.raises(NotFoundError):
                TradingService.get_trade_by_id(trade.id)
    
    def test_delete_trade_with_corrections(self, app, db_session):
        """测试删除有订正记录的交易记录"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建原始交易记录
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            original_trade = TradingService.create_trade(trade_data)
            
            # 订正交易记录
            corrected_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 13.00,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            TradingService.correct_trade_record(
                original_trade.id, 
                corrected_data, 
                '价格录入错误'
            )
            
            # 尝试删除原始记录应该失败
            with pytest.raises(ValidationError) as exc_info:
                TradingService.delete_trade(original_trade.id)
            
            assert "无法删除有订正记录关联的交易记录" in str(exc_info.value)
    
    def test_calculate_risk_reward(self, app):
        """测试计算止损止盈预期"""
        with app.app_context():
            # 测试正常计算
            result = TradingService.calculate_risk_reward(
                buy_price=12.50,
                stop_loss_price=11.00,
                take_profit_ratio=0.20,
                sell_ratio=0.50
            )
            
            expected_loss_ratio = (12.50 - 11.00) / 12.50  # 0.12
            expected_profit_ratio = 0.20 * 0.50  # 0.10
            risk_reward_ratio = expected_profit_ratio / expected_loss_ratio  # 0.833...
            
            assert result['expected_loss_ratio'] == pytest.approx(expected_loss_ratio, rel=1e-3)
            assert result['expected_profit_ratio'] == pytest.approx(expected_profit_ratio, rel=1e-3)
            assert result['risk_reward_ratio'] == pytest.approx(risk_reward_ratio, rel=1e-3)
    
    def test_calculate_risk_reward_invalid_stop_loss(self, app):
        """测试计算止损止盈预期时止损价格无效"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                TradingService.calculate_risk_reward(
                    buy_price=12.50,
                    stop_loss_price=13.00  # 止损价格高于买入价格
                )
            
            assert "止损价格必须小于买入价格" in str(exc_info.value)
    
    def test_correct_trade_record_success(self, app, db_session):
        """测试订正交易记录成功"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建原始交易记录
            original_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            original_trade = TradingService.create_trade(original_data)
            
            # 订正交易记录
            corrected_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 13.00,  # 修改价格
                'quantity': 1200,  # 修改数量
                'reason': '少妇B1战法'
            }
            
            corrected_trade = TradingService.correct_trade_record(
                original_trade.id,
                corrected_data,
                '价格和数量录入错误'
            )
            
            # 验证订正后的记录
            assert corrected_trade.id != original_trade.id
            assert float(corrected_trade.price) == 13.00
            assert corrected_trade.quantity == 1200
            assert corrected_trade.original_record_id == original_trade.id
            assert corrected_trade.correction_reason == '价格和数量录入错误'
            
            # 验证原始记录被标记为已订正
            original_trade = TradingService.get_trade_by_id(original_trade.id)
            assert original_trade.is_corrected is True
            
            # 验证订正历史记录
            corrections = TradeCorrection.query.filter_by(
                original_trade_id=original_trade.id
            ).all()
            assert len(corrections) == 1
            assert corrections[0].corrected_trade_id == corrected_trade.id
    
    def test_correct_trade_record_empty_reason(self, app, db_session):
        """测试订正交易记录时原因为空"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            trade = TradingService.create_trade(trade_data)
            
            with pytest.raises(ValidationError) as exc_info:
                TradingService.correct_trade_record(
                    trade.id,
                    {'price': 13.00},
                    ''  # 空原因
                )
            
            assert "订正原因不能为空" in str(exc_info.value)
    
    def test_get_correction_history(self, app, db_session):
        """测试获取订正历史"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建原始交易记录
            original_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            original_trade = TradingService.create_trade(original_data)
            
            # 第一次订正
            corrected_data1 = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 13.00,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            TradingService.correct_trade_record(
                original_trade.id,
                corrected_data1,
                '价格录入错误'
            )
            
            # 获取订正历史
            history = TradingService.get_correction_history(original_trade.id)
            
            assert len(history) == 1
            assert history[0]['correction_reason'] == '价格录入错误'
            assert 'corrected_fields' in history[0]
            assert isinstance(history[0]['corrected_fields'], dict)
    
    def test_correct_trade_record_not_found(self, app, db_session):
        """测试订正不存在的交易记录"""
        with app.app_context():
            with pytest.raises(NotFoundError):
                TradingService.correct_trade_record(
                    99999,  # 不存在的ID
                    {'price': 13.00},
                    '测试订正'
                )
    
    def test_correct_trade_record_multiple_fields(self, app, db_session):
        """测试订正交易记录多个字段"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法', '少妇B2战法'])
            
            # 创建原始交易记录
            original_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法',
                'notes': '原始备注'
            }
            original_trade = TradingService.create_trade(original_data)
            
            # 订正多个字段
            corrected_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 13.50,  # 修改价格
                'quantity': 1200,  # 修改数量
                'reason': '少妇B2战法',  # 修改原因
                'notes': '订正后备注'  # 修改备注
            }
            
            corrected_trade = TradingService.correct_trade_record(
                original_trade.id,
                corrected_data,
                '多个字段录入错误'
            )
            
            # 验证所有字段都被正确订正
            assert float(corrected_trade.price) == 13.50
            assert corrected_trade.quantity == 1200
            assert corrected_trade.reason == '少妇B2战法'
            assert corrected_trade.notes == '订正后备注'
            
            # 验证订正历史记录了所有变更字段
            history = TradingService.get_correction_history(original_trade.id)
            corrected_fields = history[0]['corrected_fields']
            
            assert 'price' in corrected_fields
            assert 'quantity' in corrected_fields
            assert 'reason' in corrected_fields
            assert 'notes' in corrected_fields
            
            # Check that the values are different and contain the expected numbers
            assert float(corrected_fields['price']['old_value']) == 12.50
            assert float(corrected_fields['price']['new_value']) == 13.50
            assert int(corrected_fields['quantity']['old_value']) == 1000
            assert int(corrected_fields['quantity']['new_value']) == 1200
    
    def test_correct_trade_record_with_risk_reward_recalculation(self, app, db_session):
        """测试订正买入记录时重新计算止损止盈"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建带止损止盈的买入记录
            original_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法',
                'stop_loss_price': 11.00,
                'take_profit_ratio': 0.20,
                'sell_ratio': 0.50
            }
            original_trade = TradingService.create_trade(original_data)
            
            # 订正价格，应该重新计算止损止盈比例
            corrected_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 10.00,  # 修改买入价格
                'quantity': 1000,
                'reason': '少妇B1战法',
                'stop_loss_price': 9.00,  # 修改止损价格
                'take_profit_ratio': 0.20,
                'sell_ratio': 0.50
            }
            
            corrected_trade = TradingService.correct_trade_record(
                original_trade.id,
                corrected_data,
                '价格录入错误'
            )
            
            # 验证止损止盈比例被重新计算
            expected_loss_ratio = (10.00 - 9.00) / 10.00  # 0.10
            expected_profit_ratio = 0.20 * 0.50  # 0.10
            
            assert corrected_trade.expected_loss_ratio is not None
            assert corrected_trade.expected_profit_ratio is not None
            assert float(corrected_trade.expected_loss_ratio) == pytest.approx(expected_loss_ratio, rel=1e-3)
            assert float(corrected_trade.expected_profit_ratio) == pytest.approx(expected_profit_ratio, rel=1e-3)
    
    def test_get_correction_history_empty(self, app, db_session):
        """测试获取没有订正历史的交易记录"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建交易记录但不订正
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            trade = TradingService.create_trade(trade_data)
            
            # 获取订正历史应该为空
            history = TradingService.get_correction_history(trade.id)
            assert len(history) == 0
    
    def test_correct_trade_record_invalid_corrected_data(self, app, db_session):
        """测试订正交易记录时提供无效的订正数据"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建原始交易记录
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            trade = TradingService.create_trade(trade_data)
            
            # 尝试用无效的股票代码订正
            with pytest.raises(DatabaseError):
                TradingService.correct_trade_record(
                    trade.id,
                    {
                        'stock_code': 'INVALID',  # 无效的股票代码
                        'stock_name': '平安银行',
                        'trade_type': 'buy',
                        'price': 13.00,
                        'quantity': 1000,
                        'reason': '少妇B1战法'
                    },
                    '测试无效数据'
                )


class TestTradingConfigService:
    """交易配置服务测试"""
    
    def test_get_buy_reasons(self, app, db_session):
        """测试获取买入原因"""
        with app.app_context():
            # 设置买入原因
            reasons = ['少妇B1战法', '少妇SB1战法', '少妇B2战法']
            Configuration.set_buy_reasons(reasons)
            
            result = TradingConfigService.get_buy_reasons()
            assert result == reasons
    
    def test_get_sell_reasons(self, app, db_session):
        """测试获取卖出原因"""
        with app.app_context():
            # 设置卖出原因
            reasons = ['部分止盈', '止损', '下等马/草泥马']
            Configuration.set_sell_reasons(reasons)
            
            result = TradingConfigService.get_sell_reasons()
            assert result == reasons
    
    def test_set_buy_reasons_success(self, app, db_session):
        """测试设置买入原因成功"""
        with app.app_context():
            reasons = ['新买入原因1', '新买入原因2']
            result = TradingConfigService.set_buy_reasons(reasons)
            
            assert result is True
            assert TradingConfigService.get_buy_reasons() == reasons
    
    def test_set_buy_reasons_invalid_format(self, app, db_session):
        """测试设置买入原因格式无效"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                TradingConfigService.set_buy_reasons("不是列表")
            
            assert "买入原因必须是列表格式" in str(exc_info.value)
    
    def test_set_buy_reasons_empty_list(self, app, db_session):
        """测试设置买入原因为空列表"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                TradingConfigService.set_buy_reasons([])
            
            assert "买入原因列表不能为空" in str(exc_info.value)
    
    def test_set_sell_reasons_success(self, app, db_session):
        """测试设置卖出原因成功"""
        with app.app_context():
            reasons = ['新卖出原因1', '新卖出原因2']
            result = TradingConfigService.set_sell_reasons(reasons)
            
            assert result is True
            assert TradingConfigService.get_sell_reasons() == reasons
    
    def test_get_all_config(self, app, db_session):
        """测试获取所有交易配置"""
        with app.app_context():
            buy_reasons = ['买入原因1', '买入原因2']
            sell_reasons = ['卖出原因1', '卖出原因2']
            
            Configuration.set_buy_reasons(buy_reasons)
            Configuration.set_sell_reasons(sell_reasons)
            
            config = TradingConfigService.get_all_config()
            
            assert config['buy_reasons'] == buy_reasons
            assert config['sell_reasons'] == sell_reasons