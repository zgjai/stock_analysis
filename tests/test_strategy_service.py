"""
交易策略服务测试
"""
import pytest
from datetime import date, datetime, timedelta
from services.strategy_service import StrategyService, StrategyEvaluator, HoldingAlertService
from models.trading_strategy import TradingStrategy
from models.trade_record import TradeRecord
from models.stock_price import StockPrice
from error_handlers import ValidationError, NotFoundError


class TestStrategyService:
    """交易策略服务测试"""
    
    def test_create_strategy_success(self, app):
        """测试创建策略成功"""
        with app.app_context():
            strategy_data = {
                'strategy_name': '测试策略',
                'description': '这是一个测试策略',
                'rules': {
                    "rules": [
                        {"day_range": [1, 5], "loss_threshold": -0.05, "action": "sell_all", "condition": "loss_exceed"}
                    ]
                }
            }
            
            strategy = StrategyService.create_strategy(strategy_data)
            
            assert strategy is not None
            assert strategy.strategy_name == '测试策略'
            assert strategy.is_active == True
            assert strategy.rules_list == strategy_data['rules']
    
    def test_create_strategy_validation_error(self, app):
        """测试创建策略验证错误"""
        with app.app_context():
            # 缺少必填字段
            with pytest.raises(ValidationError):
                StrategyService.create_strategy({})
            
            # 策略规则格式错误
            with pytest.raises(ValidationError):
                StrategyService.create_strategy({
                    'strategy_name': '测试策略',
                    'rules': 'invalid json'
                })
    
    def test_update_strategy_success(self, app, sample_strategy):
        """测试更新策略成功"""
        with app.app_context():
            update_data = {
                'description': '更新后的描述',
                'is_active': False
            }
            
            updated_strategy = StrategyService.update_strategy(sample_strategy.id, update_data)
            
            assert updated_strategy.description == '更新后的描述'
            assert updated_strategy.is_active == False
    
    def test_get_strategies_with_filters(self, app, sample_strategy):
        """测试获取策略列表（带筛选）"""
        with app.app_context():
            # 测试激活状态筛选
            result = StrategyService.get_strategies(filters={'is_active': True})
            assert len(result['strategies']) >= 1
            
            # 测试策略名称筛选
            result = StrategyService.get_strategies(filters={'strategy_name': '测试'})
            assert len(result['strategies']) >= 1
    
    def test_activate_deactivate_strategy(self, app, sample_strategy):
        """测试激活/停用策略"""
        with app.app_context():
            # 停用策略
            deactivated = StrategyService.deactivate_strategy(sample_strategy.id)
            assert deactivated.is_active == False
            
            # 激活策略
            activated = StrategyService.activate_strategy(sample_strategy.id)
            assert activated.is_active == True
    
    def test_validate_strategy_rules(self, app):
        """测试策略规则验证"""
        with app.app_context():
            # 有效规则
            valid_rules = {
                "rules": [
                    {"day_range": [1, 5], "loss_threshold": -0.05, "action": "sell_all", "condition": "loss_exceed"},
                    {"day_range": [6, 10], "profit_threshold": 0.10, "action": "sell_partial", "sell_ratio": 0.5, "condition": "profit_exceed"}
                ]
            }
            
            # 不应该抛出异常
            StrategyService._validate_strategy_rules(valid_rules)
            
            # 无效规则 - 缺少必填字段
            with pytest.raises(ValidationError):
                invalid_rules = {
                    "rules": [
                        {"day_range": [1, 5], "action": "sell_all"}  # 缺少condition
                    ]
                }
                StrategyService._validate_strategy_rules(invalid_rules)
            
            # 无效规则 - day_range格式错误
            with pytest.raises(ValidationError):
                invalid_rules = {
                    "rules": [
                        {"day_range": [1], "action": "sell_all", "condition": "loss_exceed"}  # day_range只有一个元素
                    ]
                }
                StrategyService._validate_strategy_rules(invalid_rules)
            
            # 无效规则 - action值错误
            with pytest.raises(ValidationError):
                invalid_rules = {
                    "rules": [
                        {"day_range": [1, 5], "action": "invalid_action", "condition": "loss_exceed"}
                    ]
                }
                StrategyService._validate_strategy_rules(invalid_rules)
            
            # 无效规则 - 部分卖出缺少sell_ratio
            with pytest.raises(ValidationError):
                invalid_rules = {
                    "rules": [
                        {"day_range": [1, 5], "action": "sell_partial", "condition": "profit_exceed"}  # 缺少sell_ratio
                    ]
                }
                StrategyService._validate_strategy_rules(invalid_rules)


class TestStrategyEvaluator:
    """策略评估引擎测试"""
    
    def test_rule_applies_to_holding_days(self, app):
        """测试规则是否适用于持仓天数"""
        with app.app_context():
            rule = {"day_range": [5, 10], "action": "sell_all", "condition": "loss_exceed"}
            
            assert StrategyEvaluator._rule_applies_to_holding_days(rule, 5) == True
            assert StrategyEvaluator._rule_applies_to_holding_days(rule, 7) == True
            assert StrategyEvaluator._rule_applies_to_holding_days(rule, 10) == True
            assert StrategyEvaluator._rule_applies_to_holding_days(rule, 4) == False
            assert StrategyEvaluator._rule_applies_to_holding_days(rule, 11) == False
    
    def test_rule_triggered_loss_exceed(self, app):
        """测试亏损超过阈值规则触发"""
        with app.app_context():
            rule = {"loss_threshold": -0.05, "condition": "loss_exceed"}
            
            # 亏损6%，应该触发
            assert StrategyEvaluator._rule_triggered(rule, -0.06, 5) == True
            
            # 亏损4%，不应该触发
            assert StrategyEvaluator._rule_triggered(rule, -0.04, 5) == False
            
            # 盈利，不应该触发
            assert StrategyEvaluator._rule_triggered(rule, 0.05, 5) == False
    
    def test_rule_triggered_profit_below(self, app):
        """测试盈利低于阈值规则触发"""
        with app.app_context():
            rule = {"profit_threshold": 0.10, "condition": "profit_below"}
            
            # 盈利8%，低于10%，应该触发
            assert StrategyEvaluator._rule_triggered(rule, 0.08, 5) == True
            
            # 盈利12%，高于10%，不应该触发
            assert StrategyEvaluator._rule_triggered(rule, 0.12, 5) == False
            
            # 亏损，应该触发
            assert StrategyEvaluator._rule_triggered(rule, -0.05, 5) == True
    
    def test_rule_triggered_profit_exceed(self, app):
        """测试盈利超过阈值规则触发"""
        with app.app_context():
            rule = {"profit_threshold": 0.10, "condition": "profit_exceed"}
            
            # 盈利12%，超过10%，应该触发
            assert StrategyEvaluator._rule_triggered(rule, 0.12, 5) == True
            
            # 盈利8%，低于10%，不应该触发
            assert StrategyEvaluator._rule_triggered(rule, 0.08, 5) == False
            
            # 亏损，不应该触发
            assert StrategyEvaluator._rule_triggered(rule, -0.05, 5) == False
    
    def test_rule_triggered_profit_below_or_drawdown(self, app):
        """测试盈利低于阈值或回撤超过阈值规则触发"""
        with app.app_context():
            rule = {
                "profit_threshold": 0.15,
                "drawdown_threshold": 0.10,
                "condition": "profit_below_or_drawdown"
            }
            
            # 盈利12%，低于15%，应该触发
            assert StrategyEvaluator._rule_triggered(rule, 0.12, 5) == True
            
            # 盈利18%，高于15%，不应该触发
            assert StrategyEvaluator._rule_triggered(rule, 0.18, 5) == False
            
            # 亏损12%，超过10%回撤阈值，应该触发
            assert StrategyEvaluator._rule_triggered(rule, -0.12, 5) == True
    
    def test_create_holding_alert(self, app):
        """测试创建持仓提醒"""
        with app.app_context():
            rule = {
                "day_range": [5, 10],
                "loss_threshold": -0.05,
                "action": "sell_all",
                "condition": "loss_exceed"
            }
            
            strategy = TradingStrategy(
                strategy_name='测试策略',
                is_active=True
            )
            
            alert = StrategyEvaluator._create_holding_alert(
                stock_code='000001',
                stock_name='测试股票',
                holding_days=7,
                buy_price=10.0,
                current_price=9.0,
                current_quantity=1000,
                profit_loss_ratio=-0.10,
                rule=rule,
                strategy=strategy
            )
            
            assert alert['stock_code'] == '000001'
            assert alert['stock_name'] == '测试股票'
            assert alert['holding_days'] == 7
            assert alert['buy_price'] == 10.0
            assert alert['current_price'] == 9.0
            assert alert['current_quantity'] == 1000
            assert alert['profit_loss_ratio'] == -0.10
            assert alert['profit_loss_amount'] == -1000.0  # (9.0 - 10.0) * 1000
            assert alert['alert_type'] == 'sell_all'
            assert alert['sell_ratio'] == 1.0
            assert alert['suggested_sell_quantity'] == 1000
            assert alert['strategy_name'] == '测试策略'
            assert '持仓7天' in alert['alert_message']
            assert '亏损10.0%' in alert['alert_message']
    
    def test_generate_alert_message(self, app):
        """测试生成提醒消息"""
        with app.app_context():
            # 止损消息
            rule = {"action": "sell_all", "condition": "loss_exceed"}
            message = StrategyEvaluator._generate_alert_message('000001', 5, -0.08, rule)
            assert '持仓5天' in message
            assert '亏损8.0%' in message
            assert '全部清仓止损' in message
            
            # 止盈消息
            rule = {"action": "sell_partial", "sell_ratio": 0.3, "condition": "profit_exceed"}
            message = StrategyEvaluator._generate_alert_message('000001', 10, 0.15, rule)
            assert '持仓10天' in message
            assert '盈利15.0%' in message
            assert '部分止盈30.0%' in message
    
    def test_format_rule_description(self, app):
        """测试格式化规则描述"""
        with app.app_context():
            # 止损规则
            rule = {
                "day_range": [1, 5],
                "loss_threshold": -0.05,
                "action": "sell_all",
                "condition": "loss_exceed"
            }
            desc = StrategyEvaluator._format_rule_description(rule)
            assert '1-5天' in desc
            assert '亏损超过5.0%' in desc
            assert '全部清仓' in desc
            
            # 部分止盈规则
            rule = {
                "day_range": [10, 15],
                "profit_threshold": 0.20,
                "action": "sell_partial",
                "sell_ratio": 0.3,
                "condition": "profit_exceed"
            }
            desc = StrategyEvaluator._format_rule_description(rule)
            assert '10-15天' in desc
            assert '盈利超过20.0%' in desc
            assert '部分止盈30.0%' in desc


class TestHoldingAlertService:
    """持仓提醒服务测试"""
    
    def test_get_alerts_summary(self, app):
        """测试获取提醒汇总信息"""
        with app.app_context():
            # 由于没有实际持仓数据，这里主要测试方法不会出错
            summary = HoldingAlertService.get_alerts_summary()
            
            assert 'total_alerts' in summary
            assert 'urgent_alerts' in summary
            assert 'profit_alerts' in summary
            assert 'sell_all_alerts' in summary
            assert 'sell_partial_alerts' in summary
            assert 'hold_alerts' in summary
            assert 'alerts_by_stock' in summary
            
            # 没有持仓时，所有计数应该为0
            assert summary['total_alerts'] == 0
            assert summary['urgent_alerts'] == 0
            assert summary['profit_alerts'] == 0


@pytest.fixture
def sample_strategy(app):
    """创建示例策略"""
    with app.app_context():
        strategy_data = {
            'strategy_name': '测试策略',
            'description': '这是一个测试策略',
            'is_active': True,
            'rules': {
                "rules": [
                    {"day_range": [1, 5], "loss_threshold": -0.05, "action": "sell_all", "condition": "loss_exceed"},
                    {"day_range": [6, 10], "profit_threshold": 0.10, "action": "sell_partial", "sell_ratio": 0.5, "condition": "profit_exceed"}
                ]
            }
        }
        
        strategy = TradingStrategy(**strategy_data)
        strategy.rules_list = strategy_data['rules']
        strategy.save()
        
        yield strategy
        
        # 清理
        try:
            strategy.delete()
        except:
            pass


@pytest.fixture
def sample_holding_data(app):
    """创建示例持仓数据"""
    with app.app_context():
        # 创建买入记录
        buy_record = TradeRecord(
            stock_code='000001',
            stock_name='测试股票',
            trade_type='buy',
            price=10.0,
            quantity=1000,
            trade_date=datetime.now() - timedelta(days=7),
            reason='测试买入'
        )
        buy_record.save()
        
        # 创建股票价格记录
        price_record = StockPrice(
            stock_code='000001',
            stock_name='测试股票',
            current_price=9.5,
            change_percent=-5.0,
            record_date=date.today()
        )
        price_record.save()
        
        yield {
            'buy_record': buy_record,
            'price_record': price_record
        }
        
        # 清理
        try:
            buy_record.delete()
            price_record.delete()
        except:
            pass