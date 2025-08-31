"""
核心业务功能验证测试 - 交易记录基本功能测试
测试买入和卖出记录的创建和查询、验证交易记录的基本计算（止损止盈）、测试交易记录的更新和删除功能
需求: 1.3
"""
import pytest
import json
from datetime import datetime, date
from decimal import Decimal
from models.trade_record import TradeRecord, TradeCorrection
from models.configuration import Configuration
from services.trading_service import TradingService
from error_handlers import ValidationError, NotFoundError


class TestTradingRecordsBasicFunctionality:
    """交易记录基本功能测试"""
    
    def setup_trading_config(self):
        """设置交易配置"""
        Configuration.set_buy_reasons(['少妇B1战法', '少妇SB1战法', '少妇B2战法', '技术突破'])
        Configuration.set_sell_reasons(['部分止盈', '止损', '下等马/草泥马', '见顶信号', '技术破位'])
    
    # ========== 买入记录创建和查询测试 ==========
    
    def test_create_buy_record_basic(self, app, db_session):
        """测试创建基本买入记录"""
        with app.app_context():
            self.setup_trading_config()
            buy_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法',
                'notes': '基本买入测试'
            }
            
            trade = TradingService.create_trade(buy_data)
            
            # 验证基本字段
            assert trade.id is not None
            assert trade.stock_code == '000001'
            assert trade.stock_name == '平安银行'
            assert trade.trade_type == 'buy'
            assert float(trade.price) == 12.50
            assert trade.quantity == 1000
            assert trade.reason == '少妇B1战法'
            assert trade.notes == '基本买入测试'
            assert trade.trade_date is not None
            assert trade.is_corrected is False
    
    def test_create_buy_record_with_stop_loss_take_profit(self, app, db_session):
        """测试创建带止损止盈的买入记录"""
        with app.app_context():
            buy_data = {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'buy',
                'price': 15.80,
                'quantity': 500,
                'reason': '技术突破',
                'stop_loss_price': 14.20,
                'take_profit_ratio': 0.20,
                'sell_ratio': 0.50,
                'notes': '带止损止盈的买入'
            }
            
            trade = TradingService.create_trade(buy_data)
            
            # 验证止损止盈字段
            assert float(trade.stop_loss_price) == 14.20
            assert float(trade.take_profit_ratio) == 0.20
            assert float(trade.sell_ratio) == 0.50
            
            # 验证自动计算的风险收益比
            assert trade.expected_loss_ratio is not None
            assert trade.expected_profit_ratio is not None
            
            # 计算预期值
            expected_loss = (15.80 - 14.20) / 15.80  # 约0.1013
            expected_profit = 0.20 * 0.50  # 0.10
            
            assert abs(float(trade.expected_loss_ratio) - expected_loss) < 0.001
            assert abs(float(trade.expected_profit_ratio) - expected_profit) < 0.001
    
    def test_create_buy_record_validation_errors(self, app, db_session):
        """测试买入记录创建时的验证错误"""
        with app.app_context():
            # 测试缺少必填字段
            with pytest.raises(ValidationError):
                TradingService.create_trade({
                    'stock_code': '000001',
                    'trade_type': 'buy',
                    'price': 12.50
                    # 缺少 stock_name, quantity, reason
                })
            
            # 测试无效的交易原因
            with pytest.raises(ValidationError) as exc_info:
                TradingService.create_trade({
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': 12.50,
                    'quantity': 1000,
                    'reason': '无效原因'
                })
            assert "无效的buy原因" in str(exc_info.value)
            
            # 测试止损价格高于买入价格
            with pytest.raises(ValidationError) as exc_info:
                TradingService.create_trade({
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': 12.50,
                    'quantity': 1000,
                    'reason': '少妇B1战法',
                    'stop_loss_price': 13.00  # 高于买入价格
                })
            assert "止损价格必须小于买入价格" in str(exc_info.value)
    
    # ========== 卖出记录创建和查询测试 ==========
    
    def test_create_sell_record_basic(self, app, db_session):
        """测试创建基本卖出记录"""
        with app.app_context():
            sell_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'sell',
                'price': 13.80,
                'quantity': 500,
                'reason': '部分止盈',
                'notes': '基本卖出测试'
            }
            
            trade = TradingService.create_trade(sell_data)
            
            # 验证基本字段
            assert trade.id is not None
            assert trade.stock_code == '000001'
            assert trade.stock_name == '平安银行'
            assert trade.trade_type == 'sell'
            assert float(trade.price) == 13.80
            assert trade.quantity == 500
            assert trade.reason == '部分止盈'
            assert trade.notes == '基本卖出测试'
            
            # 卖出记录不应该有止损止盈字段
            assert trade.stop_loss_price is None
            assert trade.take_profit_ratio is None
            assert trade.sell_ratio is None
    
    def test_create_sell_record_validation_errors(self, app, db_session):
        """测试卖出记录创建时的验证错误"""
        with app.app_context():
            # 测试无效的卖出原因
            with pytest.raises(ValidationError) as exc_info:
                TradingService.create_trade({
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'sell',
                    'price': 13.80,
                    'quantity': 500,
                    'reason': '无效卖出原因'
                })
            assert "无效的sell原因" in str(exc_info.value)
    
    # ========== 交易记录查询测试 ==========
    
    def test_query_trades_by_stock_code(self, app, db_session):
        """测试按股票代码查询交易记录"""
        with app.app_context():
            # 创建多条不同股票的交易记录
            trades_data = [
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': 12.50,
                    'quantity': 1000,
                    'reason': '少妇B1战法'
                },
                {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'trade_type': 'buy',
                    'price': 15.80,
                    'quantity': 500,
                    'reason': '技术突破'
                },
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'sell',
                    'price': 13.20,
                    'quantity': 500,
                    'reason': '部分止盈'
                }
            ]
            
            for data in trades_data:
                TradingService.create_trade(data)
            
            # 查询特定股票的交易记录
            result = TradingService.get_trades(filters={'stock_code': '000001'})
            
            assert result['total'] == 2
            assert all(trade['stock_code'] == '000001' for trade in result['trades'])
    
    def test_query_trades_by_trade_type(self, app, db_session):
        """测试按交易类型查询交易记录"""
        with app.app_context():
            # 创建买入和卖出记录
            buy_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            sell_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'sell',
                'price': 13.50,
                'quantity': 500,
                'reason': '部分止盈'
            }
            
            TradingService.create_trade(buy_data)
            TradingService.create_trade(sell_data)
            
            # 查询买入记录
            buy_result = TradingService.get_trades(filters={'trade_type': 'buy'})
            assert buy_result['total'] == 1
            assert buy_result['trades'][0]['trade_type'] == 'buy'
            
            # 查询卖出记录
            sell_result = TradingService.get_trades(filters={'trade_type': 'sell'})
            assert sell_result['total'] == 1
            assert sell_result['trades'][0]['trade_type'] == 'sell'
    
    def test_query_trades_by_date_range(self, app, db_session):
        """测试按日期范围查询交易记录"""
        with app.app_context():
            # 创建不同日期的交易记录
            trades_data = [
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': 12.50,
                    'quantity': 1000,
                    'reason': '少妇B1战法',
                    'trade_date': datetime(2024, 1, 1, 9, 30)
                },
                {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'trade_type': 'buy',
                    'price': 15.80,
                    'quantity': 500,
                    'reason': '技术突破',
                    'trade_date': datetime(2024, 1, 15, 10, 0)
                },
                {
                    'stock_code': '000003',
                    'stock_name': '中国平安',
                    'trade_type': 'buy',
                    'price': 45.20,
                    'quantity': 200,
                    'reason': '少妇B2战法',
                    'trade_date': datetime(2024, 2, 1, 14, 30)
                }
            ]
            
            for data in trades_data:
                TradingService.create_trade(data)
            
            # 查询1月份的记录
            result = TradingService.get_trades(filters={
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            })
            
            assert result['total'] == 2
            for trade in result['trades']:
                trade_date = datetime.fromisoformat(trade['trade_date'].replace('Z', '+00:00'))
                assert trade_date.month == 1
    
    def test_query_trades_with_pagination(self, app, db_session):
        """测试交易记录分页查询"""
        with app.app_context():
            # 创建5条交易记录
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
            
            # 测试第一页
            result = TradingService.get_trades(page=1, per_page=2)
            assert result['total'] == 5
            assert len(result['trades']) == 2
            assert result['current_page'] == 1
            assert result['pages'] == 3
            assert result['has_next'] is True
            assert result['has_prev'] is False
            
            # 测试第二页
            result = TradingService.get_trades(page=2, per_page=2)
            assert len(result['trades']) == 2
            assert result['current_page'] == 2
            assert result['has_next'] is True
            assert result['has_prev'] is True
    
    def test_query_trades_with_sorting(self, app, db_session):
        """测试交易记录排序查询"""
        with app.app_context():
            # 创建不同价格的交易记录
            trades_data = [
                {'stock_code': '000001', 'stock_name': '股票1', 'trade_type': 'buy', 
                 'price': 15.80, 'quantity': 1000, 'reason': '少妇B1战法'},
                {'stock_code': '000002', 'stock_name': '股票2', 'trade_type': 'buy', 
                 'price': 10.20, 'quantity': 1000, 'reason': '少妇B1战法'},
                {'stock_code': '000003', 'stock_name': '股票3', 'trade_type': 'buy', 
                 'price': 12.50, 'quantity': 1000, 'reason': '少妇B1战法'}
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
    
    # ========== 止损止盈计算测试 ==========
    
    def test_risk_reward_calculation_basic(self, app):
        """测试基本的止损止盈计算"""
        with app.app_context():
            result = TradingService.calculate_risk_reward(
                buy_price=12.50,
                stop_loss_price=11.00,
                take_profit_ratio=0.20,
                sell_ratio=0.50
            )
            
            # 预期亏损比例 = (买入价 - 止损价) / 买入价
            expected_loss_ratio = (12.50 - 11.00) / 12.50  # 0.12
            # 预期收益比例 = 止盈比例 * 卖出比例
            expected_profit_ratio = 0.20 * 0.50  # 0.10
            # 风险收益比 = 预期收益 / 预期亏损
            risk_reward_ratio = expected_profit_ratio / expected_loss_ratio  # 0.833...
            
            assert abs(result['expected_loss_ratio'] - expected_loss_ratio) < 0.001
            assert abs(result['expected_profit_ratio'] - expected_profit_ratio) < 0.001
            assert abs(result['risk_reward_ratio'] - risk_reward_ratio) < 0.001
    
    def test_risk_reward_calculation_edge_cases(self, app):
        """测试止损止盈计算的边界情况"""
        with app.app_context():
            # 测试没有止损价格的情况
            result = TradingService.calculate_risk_reward(
                buy_price=12.50,
                take_profit_ratio=0.20,
                sell_ratio=0.50
            )
            assert result['expected_loss_ratio'] == 0.0
            assert result['expected_profit_ratio'] == 0.10
            assert result['risk_reward_ratio'] == float('inf')
            
            # 测试没有止盈设置的情况
            result = TradingService.calculate_risk_reward(
                buy_price=12.50,
                stop_loss_price=11.00
            )
            expected_loss_ratio = (12.50 - 11.00) / 12.50
            assert abs(result['expected_loss_ratio'] - expected_loss_ratio) < 0.001
            assert result['expected_profit_ratio'] == 0.0
            assert result['risk_reward_ratio'] == 0.0
    
    def test_risk_reward_calculation_invalid_stop_loss(self, app):
        """测试无效止损价格的计算"""
        with app.app_context():
            # 止损价格高于买入价格
            with pytest.raises(ValidationError) as exc_info:
                TradingService.calculate_risk_reward(
                    buy_price=12.50,
                    stop_loss_price=13.00
                )
            assert "止损价格必须小于买入价格" in str(exc_info.value)
    
    def test_buy_record_auto_calculation(self, app, db_session):
        """测试买入记录创建时自动计算止损止盈"""
        with app.app_context():
            buy_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 20.00,
                'quantity': 1000,
                'reason': '少妇B1战法',
                'stop_loss_price': 18.00,
                'take_profit_ratio': 0.25,
                'sell_ratio': 0.60
            }
            
            trade = TradingService.create_trade(buy_data)
            
            # 验证自动计算结果
            expected_loss = (20.00 - 18.00) / 20.00  # 0.10
            expected_profit = 0.25 * 0.60  # 0.15
            
            assert abs(float(trade.expected_loss_ratio) - expected_loss) < 0.001
            assert abs(float(trade.expected_profit_ratio) - expected_profit) < 0.001
    
    # ========== 交易记录更新测试 ==========
    
    def test_update_trade_basic_fields(self, app, db_session):
        """测试更新交易记录基本字段"""
        with app.app_context():
            # 创建交易记录
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法',
                'notes': '原始备注'
            }
            trade = TradingService.create_trade(trade_data)
            
            # 更新记录
            update_data = {
                'price': 13.00,
                'quantity': 1200,
                'reason': '少妇B2战法',
                'notes': '更新后的备注'
            }
            
            updated_trade = TradingService.update_trade(trade.id, update_data)
            
            # 验证更新结果
            assert float(updated_trade.price) == 13.00
            assert updated_trade.quantity == 1200
            assert updated_trade.reason == '少妇B2战法'
            assert updated_trade.notes == '更新后的备注'
            
            # 验证未更新的字段保持不变
            assert updated_trade.stock_code == '000001'
            assert updated_trade.stock_name == '平安银行'
            assert updated_trade.trade_type == 'buy'
    
    def test_update_buy_record_risk_reward_recalculation(self, app, db_session):
        """测试更新买入记录时重新计算止损止盈"""
        with app.app_context():
            # 创建带止损止盈的买入记录
            trade_data = {
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
            trade = TradingService.create_trade(trade_data)
            
            # 更新价格和止损价格
            update_data = {
                'price': 15.00,
                'stop_loss_price': 13.50,
                'take_profit_ratio': 0.30,
                'sell_ratio': 0.60
            }
            
            updated_trade = TradingService.update_trade(trade.id, update_data)
            
            # 验证重新计算的结果
            expected_loss = (15.00 - 13.50) / 15.00  # 0.10
            expected_profit = 0.30 * 0.60  # 0.18
            
            assert abs(float(updated_trade.expected_loss_ratio) - expected_loss) < 0.001
            assert abs(float(updated_trade.expected_profit_ratio) - expected_profit) < 0.001
    
    def test_update_trade_validation_errors(self, app, db_session):
        """测试更新交易记录时的验证错误"""
        with app.app_context():
            # 创建交易记录
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            trade = TradingService.create_trade(trade_data)
            
            # 测试更新为无效原因
            with pytest.raises(ValidationError) as exc_info:
                TradingService.update_trade(trade.id, {'reason': '无效原因'})
            assert "无效的buy原因" in str(exc_info.value)
    
    def test_update_nonexistent_trade(self, app, db_session):
        """测试更新不存在的交易记录"""
        with app.app_context():
            with pytest.raises(NotFoundError):
                TradingService.update_trade(99999, {'price': 10.00})
    
    # ========== 交易记录删除测试 ==========
    
    def test_delete_trade_success(self, app, db_session):
        """测试成功删除交易记录"""
        with app.app_context():
            # 创建交易记录
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            trade = TradingService.create_trade(trade_data)
            trade_id = trade.id
            
            # 删除记录
            result = TradingService.delete_trade(trade_id)
            assert result is True
            
            # 验证记录已被删除
            with pytest.raises(NotFoundError):
                TradingService.get_trade_by_id(trade_id)
    
    def test_delete_nonexistent_trade(self, app, db_session):
        """测试删除不存在的交易记录"""
        with app.app_context():
            with pytest.raises(NotFoundError):
                TradingService.delete_trade(99999)
    
    def test_delete_trade_with_corrections(self, app, db_session):
        """测试删除有订正记录的交易记录"""
        with app.app_context():
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
    
    # ========== 综合功能测试 ==========
    
    def test_complete_trading_workflow(self, app, db_session):
        """测试完整的交易工作流程"""
        with app.app_context():
            # 1. 创建买入记录
            buy_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法',
                'stop_loss_price': 11.00,
                'take_profit_ratio': 0.20,
                'sell_ratio': 0.50,
                'notes': '买入测试'
            }
            buy_trade = TradingService.create_trade(buy_data)
            
            # 2. 创建对应的卖出记录
            sell_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'sell',
                'price': 13.80,
                'quantity': 500,
                'reason': '部分止盈',
                'notes': '部分卖出'
            }
            sell_trade = TradingService.create_trade(sell_data)
            
            # 3. 查询该股票的所有交易记录
            result = TradingService.get_trades(filters={'stock_code': '000001'})
            assert result['total'] == 2
            
            # 4. 验证买入和卖出记录都存在
            trade_types = [trade['trade_type'] for trade in result['trades']]
            assert 'buy' in trade_types
            assert 'sell' in trade_types
            
            # 5. 更新买入记录的止损价格
            updated_buy = TradingService.update_trade(buy_trade.id, {
                'stop_loss_price': 11.50
            })
            
            # 验证止损止盈重新计算
            expected_loss = (12.50 - 11.50) / 12.50  # 0.08
            assert abs(float(updated_buy.expected_loss_ratio) - expected_loss) < 0.001
    
    def test_multiple_stocks_trading_records(self, app, db_session):
        """测试多只股票的交易记录管理"""
        with app.app_context():
            # 创建多只股票的交易记录
            stocks_data = [
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trades': [
                        {'trade_type': 'buy', 'price': 12.50, 'quantity': 1000, 'reason': '少妇B1战法'},
                        {'trade_type': 'sell', 'price': 13.20, 'quantity': 500, 'reason': '部分止盈'}
                    ]
                },
                {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'trades': [
                        {'trade_type': 'buy', 'price': 15.80, 'quantity': 500, 'reason': '技术突破'},
                        {'trade_type': 'buy', 'price': 14.90, 'quantity': 300, 'reason': '少妇B2战法'}
                    ]
                }
            ]
            
            # 创建所有交易记录
            for stock_data in stocks_data:
                for trade_info in stock_data['trades']:
                    trade_data = {
                        'stock_code': stock_data['stock_code'],
                        'stock_name': stock_data['stock_name'],
                        **trade_info
                    }
                    TradingService.create_trade(trade_data)
            
            # 验证每只股票的交易记录
            for stock_data in stocks_data:
                result = TradingService.get_trades(filters={'stock_code': stock_data['stock_code']})
                assert result['total'] == len(stock_data['trades'])
                
                # 验证所有记录都属于正确的股票
                for trade in result['trades']:
                    assert trade['stock_code'] == stock_data['stock_code']
                    assert trade['stock_name'] == stock_data['stock_name']
            
            # 验证总记录数
            all_trades = TradingService.get_trades()
            assert all_trades['total'] == 4  # 总共4条记录
    
    def test_trading_records_data_consistency(self, app, db_session):
        """测试交易记录数据一致性"""
        with app.app_context():
            # 创建交易记录
            trade_data = {
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
            trade = TradingService.create_trade(trade_data)
            
            # 通过不同方式获取记录，验证数据一致性
            trade_by_id = TradingService.get_trade_by_id(trade.id)
            trades_list = TradingService.get_trades(filters={'stock_code': '000001'})
            trade_from_list = trades_list['trades'][0]
            
            # 验证关键字段一致性
            assert trade_by_id.stock_code == trade_from_list['stock_code']
            assert float(trade_by_id.price) == trade_from_list['price']
            assert trade_by_id.quantity == trade_from_list['quantity']
            assert trade_by_id.reason == trade_from_list['reason']
            
            # 验证计算字段一致性
            if trade_by_id.expected_loss_ratio:
                assert abs(float(trade_by_id.expected_loss_ratio) - trade_from_list['expected_loss_ratio']) < 0.001
            if trade_by_id.expected_profit_ratio:
                assert abs(float(trade_by_id.expected_profit_ratio) - trade_from_list['expected_profit_ratio']) < 0.001


if __name__ == '__main__':
    pytest.main([__file__, '-v'])