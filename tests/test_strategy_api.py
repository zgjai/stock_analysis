"""
交易策略API测试
"""
import pytest
import json
from datetime import date, datetime, timedelta
from models.trading_strategy import TradingStrategy
from models.trade_record import TradeRecord
from models.stock_price import StockPrice


class TestStrategyAPI:
    """交易策略API测试"""
    
    def test_get_strategies(self, client, sample_strategy):
        """测试获取策略列表"""
        response = client.get('/api/strategies')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'strategies' in data['data']
        assert len(data['data']['strategies']) >= 1
    
    def test_get_strategies_with_filters(self, client, sample_strategy):
        """测试带筛选条件获取策略列表"""
        # 测试激活状态筛选
        response = client.get('/api/strategies?is_active=true')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        
        # 测试策略名称筛选
        response = client.get('/api/strategies?strategy_name=测试')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
    
    def test_create_strategy_success(self, client):
        """测试创建策略成功"""
        strategy_data = {
            'strategy_name': 'API测试策略',
            'description': '通过API创建的测试策略',
            'rules': {
                "rules": [
                    {"day_range": [1, 5], "loss_threshold": -0.05, "action": "sell_all", "condition": "loss_exceed"}
                ]
            }
        }
        
        response = client.post('/api/strategies', 
                             data=json.dumps(strategy_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['strategy_name'] == 'API测试策略'
        assert data['data']['is_active'] == True
    
    def test_create_strategy_validation_error(self, client):
        """测试创建策略验证错误"""
        # 缺少必填字段
        response = client.post('/api/strategies',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
        
        # 策略规则格式错误
        invalid_data = {
            'strategy_name': '无效策略',
            'rules': 'invalid json'
        }
        
        response = client.post('/api/strategies',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
    
    def test_get_strategy_detail(self, client, sample_strategy):
        """测试获取策略详情"""
        response = client.get(f'/api/strategies/{sample_strategy.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['id'] == sample_strategy.id
        assert data['data']['strategy_name'] == sample_strategy.strategy_name
    
    def test_get_strategy_not_found(self, client):
        """测试获取不存在的策略"""
        response = client.get('/api/strategies/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] == False
    
    def test_update_strategy_success(self, client, sample_strategy):
        """测试更新策略成功"""
        update_data = {
            'description': '更新后的描述',
            'is_active': False
        }
        
        response = client.put(f'/api/strategies/{sample_strategy.id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['description'] == '更新后的描述'
        assert data['data']['is_active'] == False
    
    def test_delete_strategy_success(self, client, sample_strategy):
        """测试删除策略成功"""
        response = client.delete(f'/api/strategies/{sample_strategy.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
    
    def test_activate_strategy(self, client, sample_strategy):
        """测试激活策略"""
        # 先停用策略
        sample_strategy.is_active = False
        sample_strategy.save()
        
        response = client.post(f'/api/strategies/{sample_strategy.id}/activate')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['is_active'] == True
    
    def test_deactivate_strategy(self, client, sample_strategy):
        """测试停用策略"""
        response = client.post(f'/api/strategies/{sample_strategy.id}/deactivate')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['is_active'] == False
    
    def test_get_active_strategies(self, client, sample_strategy):
        """测试获取激活的策略"""
        response = client.get('/api/strategies/active')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert isinstance(data['data'], list)
    
    def test_validate_strategy_rules(self, client):
        """测试验证策略规则"""
        # 有效规则
        valid_rules = {
            'rules': {
                "rules": [
                    {"day_range": [1, 5], "loss_threshold": -0.05, "action": "sell_all", "condition": "loss_exceed"}
                ]
            }
        }
        
        response = client.post('/api/strategies/validate-rules',
                             data=json.dumps(valid_rules),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        
        # 无效规则
        invalid_rules = {
            'rules': {
                "rules": [
                    {"day_range": [1], "action": "sell_all"}  # 缺少必填字段
                ]
            }
        }
        
        response = client.post('/api/strategies/validate-rules',
                             data=json.dumps(invalid_rules),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False


class TestHoldingAlertsAPI:
    """持仓提醒API测试"""
    
    def test_get_holding_alerts(self, client):
        """测试获取持仓提醒"""
        response = client.get('/api/holdings/alerts')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert isinstance(data['data'], list)
    
    def test_get_holding_alerts_by_type(self, client):
        """测试按类型获取持仓提醒"""
        # 测试获取紧急提醒
        response = client.get('/api/holdings/alerts?type=urgent')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        
        # 测试获取止盈提醒
        response = client.get('/api/holdings/alerts?type=profit')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        
        # 测试获取全部清仓提醒
        response = client.get('/api/holdings/alerts?type=sell_all')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
    
    def test_get_holding_alerts_by_stock(self, client):
        """测试获取特定股票的持仓提醒"""
        response = client.get('/api/holdings/alerts?stock_code=000001')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert isinstance(data['data'], list)
    
    def test_get_alerts_summary(self, client):
        """测试获取提醒汇总"""
        response = client.get('/api/holdings/alerts/summary')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        
        summary = data['data']
        assert 'total_alerts' in summary
        assert 'urgent_alerts' in summary
        assert 'profit_alerts' in summary
        assert 'sell_all_alerts' in summary
        assert 'sell_partial_alerts' in summary
        assert 'hold_alerts' in summary
        assert 'alerts_by_stock' in summary
    
    def test_evaluate_holdings(self, client):
        """测试手动触发持仓策略评估"""
        # 评估所有持仓
        response = client.post('/api/holdings/alerts/evaluate')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert isinstance(data['data'], list)
        
        # 评估特定股票
        eval_data = {'stock_code': '000001'}
        response = client.post('/api/holdings/alerts/evaluate',
                             data=json.dumps(eval_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert isinstance(data['data'], list)
    
    def test_test_strategy_rule(self, client):
        """测试策略规则测试"""
        test_data = {
            'rule': {
                "day_range": [5, 10],
                "loss_threshold": -0.05,
                "action": "sell_all",
                "condition": "loss_exceed"
            },
            'holding_days': 7,
            'profit_loss_ratio': -0.08
        }
        
        response = client.post('/api/strategies/test-rule',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        
        result = data['data']
        assert 'rule_applies' in result
        assert 'rule_triggered' in result
        assert 'rule_description' in result
        assert 'test_parameters' in result
        
        # 规则应该适用且触发
        assert result['rule_applies'] == True
        assert result['rule_triggered'] == True
        assert 'alert_message' in result
    
    def test_get_default_strategy(self, client):
        """测试获取默认策略"""
        response = client.get('/api/strategies/default')
        
        # 如果默认策略存在
        if response.status_code == 200:
            data = response.get_json()
            assert data['success'] == True
            assert data['data']['strategy_name'] == '默认持仓策略'
        else:
            # 如果默认策略不存在
            assert response.status_code == 404
    
    def test_reset_default_strategy(self, client):
        """测试重置默认策略"""
        response = client.post('/api/strategies/default/reset')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['strategy_name'] == '默认持仓策略'
        assert data['data']['is_active'] == True
        assert 'rules_list' in data['data']


@pytest.fixture
def sample_strategy(app):
    """创建示例策略"""
    with app.app_context():
        strategy_data = {
            'strategy_name': 'API测试策略',
            'description': '用于API测试的策略',
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
            stock_name='API测试股票',
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
            stock_name='API测试股票',
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