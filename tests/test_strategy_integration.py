"""
交易策略系统集成测试
"""
import pytest
import json
from datetime import date, datetime, timedelta
from models.trading_strategy import TradingStrategy
from models.trade_record import TradeRecord
from models.stock_price import StockPrice
from models.review_record import ReviewRecord
from services.strategy_service import StrategyService, StrategyEvaluator, HoldingAlertService
from services.review_service import HoldingService


class TestStrategyIntegration:
    """交易策略系统集成测试"""
    
    def test_complete_strategy_workflow(self, app):
        """测试完整的策略工作流程"""
        with app.app_context():
            # 1. 创建交易策略
            strategy_data = {
                'strategy_name': '集成测试策略',
                'description': '用于集成测试的策略',
                'is_active': True,
                'rules': {
                    "rules": [
                        {"day_range": [1, 3], "loss_threshold": -0.05, "action": "sell_all", "condition": "loss_exceed"},
                        {"day_range": [4, 7], "profit_threshold": 0.10, "action": "sell_partial", "sell_ratio": 0.5, "condition": "profit_exceed"},
                        {"day_range": [8, 15], "profit_threshold": 0.05, "action": "sell_all", "condition": "profit_below"}
                    ]
                }
            }
            
            strategy = StrategyService.create_strategy(strategy_data)
            assert strategy is not None
            assert strategy.is_active == True
            
            # 2. 创建交易记录（买入）
            buy_date = datetime.now() - timedelta(days=5)
            buy_record = TradeRecord(
                stock_code='000001',
                stock_name='集成测试股票',
                trade_type='buy',
                price=10.0,
                quantity=1000,
                trade_date=buy_date,
                reason='测试买入'
            )
            buy_record.save()
            
            # 3. 创建股票价格记录（当前价格）
            price_record = StockPrice(
                stock_code='000001',
                stock_name='集成测试股票',
                current_price=11.5,  # 15%盈利
                change_percent=15.0,
                record_date=date.today()
            )
            price_record.save()
            
            # 4. 创建复盘记录（设置持仓天数）
            review_record = ReviewRecord(
                stock_code='000001',
                review_date=date.today(),
                holding_days=5,  # 持仓5天
                price_up_score=1,
                bbi_score=1,
                volume_score=1,
                trend_score=1,
                j_score=1,
                analysis='测试复盘',
                decision='hold',
                reason='继续观察'
            )
            review_record.save()
            
            # 5. 获取当前持仓
            holdings = HoldingService.get_current_holdings()
            assert len(holdings) == 1
            assert holdings[0]['stock_code'] == '000001'
            assert holdings[0]['holding_days'] == 5
            
            # 6. 评估策略提醒
            alerts = StrategyEvaluator.evaluate_all_holdings()
            
            # 应该有提醒，因为持仓5天，盈利15%，符合4-7天盈利超过10%的部分止盈条件
            assert len(alerts) > 0
            
            # 找到相关提醒
            relevant_alert = None
            for alert in alerts:
                if alert['stock_code'] == '000001' and alert['alert_type'] == 'sell_partial':
                    relevant_alert = alert
                    break
            
            assert relevant_alert is not None
            assert relevant_alert['holding_days'] == 5
            assert relevant_alert['profit_loss_ratio'] == 0.15  # 15%盈利
            assert relevant_alert['sell_ratio'] == 0.5  # 50%卖出
            assert relevant_alert['suggested_sell_quantity'] == 500  # 建议卖出500股
            
            # 7. 测试提醒汇总
            summary = HoldingAlertService.get_alerts_summary()
            assert summary['total_alerts'] > 0
            assert summary['sell_partial_alerts'] > 0
            assert '000001' in summary['alerts_by_stock']
            
            # 清理数据
            buy_record.delete()
            price_record.delete()
            review_record.delete()
            strategy.delete()
    
    def test_loss_alert_scenario(self, app):
        """测试止损提醒场景"""
        with app.app_context():
            # 创建止损策略
            strategy = TradingStrategy(
                strategy_name='止损测试策略',
                is_active=True,
                description='测试止损场景'
            )
            strategy.rules_list = {
                "rules": [
                    {"day_range": [1, 10], "loss_threshold": -0.08, "action": "sell_all", "condition": "loss_exceed"}
                ]
            }
            strategy.save()
            
            # 创建买入记录
            buy_record = TradeRecord(
                stock_code='000002',
                stock_name='止损测试股票',
                trade_type='buy',
                price=20.0,
                quantity=500,
                trade_date=datetime.now() - timedelta(days=3),
                reason='测试买入'
            )
            buy_record.save()
            
            # 创建价格记录（亏损10%）
            price_record = StockPrice(
                stock_code='000002',
                stock_name='止损测试股票',
                current_price=18.0,  # 10%亏损
                change_percent=-10.0,
                record_date=date.today()
            )
            price_record.save()
            
            # 创建复盘记录
            review_record = ReviewRecord(
                stock_code='000002',
                review_date=date.today(),
                holding_days=3,
                price_up_score=0,
                bbi_score=0,
                volume_score=0,
                trend_score=0,
                j_score=0,
                analysis='股价下跌',
                decision='hold',
                reason='观察中'
            )
            review_record.save()
            
            # 评估策略
            alerts = StrategyEvaluator.evaluate_single_holding('000002')
            
            # 应该触发止损提醒
            assert len(alerts) > 0
            alert = alerts[0]
            assert alert['alert_type'] == 'sell_all'
            assert alert['profit_loss_ratio'] == -0.10  # 10%亏损
            assert '止损' in alert['alert_message']
            
            # 测试紧急提醒
            urgent_alerts = HoldingAlertService.get_urgent_alerts()
            assert len(urgent_alerts) > 0
            
            # 清理数据
            buy_record.delete()
            price_record.delete()
            review_record.delete()
            strategy.delete()
    
    def test_multiple_strategies_evaluation(self, app):
        """测试多策略评估"""
        with app.app_context():
            # 创建两个不同的策略
            strategy1 = TradingStrategy(
                strategy_name='保守策略',
                is_active=True,
                description='保守的止损止盈策略'
            )
            strategy1.rules_list = {
                "rules": [
                    {"day_range": [1, 5], "loss_threshold": -0.03, "action": "sell_all", "condition": "loss_exceed"},
                    {"day_range": [1, 5], "profit_threshold": 0.05, "action": "sell_partial", "sell_ratio": 0.3, "condition": "profit_exceed"}
                ]
            }
            strategy1.save()
            
            strategy2 = TradingStrategy(
                strategy_name='激进策略',
                is_active=True,
                description='激进的止损止盈策略'
            )
            strategy2.rules_list = {
                "rules": [
                    {"day_range": [1, 5], "loss_threshold": -0.10, "action": "sell_all", "condition": "loss_exceed"},
                    {"day_range": [1, 5], "profit_threshold": 0.15, "action": "sell_partial", "sell_ratio": 0.5, "condition": "profit_exceed"}
                ]
            }
            strategy2.save()
            
            # 创建持仓数据
            buy_record = TradeRecord(
                stock_code='000003',
                stock_name='多策略测试股票',
                trade_type='buy',
                price=15.0,
                quantity=800,
                trade_date=datetime.now() - timedelta(days=3),
                reason='测试买入'
            )
            buy_record.save()
            
            # 创建价格记录（盈利8%）
            price_record = StockPrice(
                stock_code='000003',
                stock_name='多策略测试股票',
                current_price=16.2,  # 8%盈利
                change_percent=8.0,
                record_date=date.today()
            )
            price_record.save()
            
            # 创建复盘记录
            review_record = ReviewRecord(
                stock_code='000003',
                review_date=date.today(),
                holding_days=3,
                price_up_score=1,
                bbi_score=1,
                volume_score=1,
                trend_score=1,
                j_score=1,
                analysis='股价上涨',
                decision='hold',
                reason='继续持有'
            )
            review_record.save()
            
            # 评估策略
            alerts = StrategyEvaluator.evaluate_single_holding('000003')
            
            # 应该有来自保守策略的提醒（8%盈利超过5%阈值）
            # 但不应该有来自激进策略的提醒（8%盈利未达到15%阈值）
            conservative_alerts = [a for a in alerts if a['strategy_name'] == '保守策略']
            aggressive_alerts = [a for a in alerts if a['strategy_name'] == '激进策略']
            
            assert len(conservative_alerts) > 0
            assert len(aggressive_alerts) == 0
            
            conservative_alert = conservative_alerts[0]
            assert conservative_alert['alert_type'] == 'sell_partial'
            assert conservative_alert['sell_ratio'] == 0.3
            
            # 清理数据
            buy_record.delete()
            price_record.delete()
            review_record.delete()
            strategy1.delete()
            strategy2.delete()


class TestStrategyAPIIntegration:
    """策略API集成测试"""
    
    def test_complete_api_workflow(self, client, app):
        """测试完整的API工作流程"""
        with app.app_context():
            # 1. 创建策略
            strategy_data = {
                'strategy_name': 'API集成测试策略',
                'description': '通过API测试完整流程',
                'rules': {
                    "rules": [
                        {"day_range": [1, 5], "loss_threshold": -0.05, "action": "sell_all", "condition": "loss_exceed"},
                        {"day_range": [6, 10], "profit_threshold": 0.10, "action": "sell_partial", "sell_ratio": 0.4, "condition": "profit_exceed"}
                    ]
                }
            }
            
            response = client.post('/api/strategies',
                                 data=json.dumps(strategy_data),
                                 content_type='application/json')
            
            assert response.status_code == 201
            strategy_id = response.get_json()['data']['id']
            
            # 2. 验证策略创建成功
            response = client.get(f'/api/strategies/{strategy_id}')
            assert response.status_code == 200
            
            # 3. 创建测试数据
            buy_record = TradeRecord(
                stock_code='000004',
                stock_name='API集成测试股票',
                trade_type='buy',
                price=25.0,
                quantity=400,
                trade_date=datetime.now() - timedelta(days=8),
                reason='API测试买入'
            )
            buy_record.save()
            
            price_record = StockPrice(
                stock_code='000004',
                stock_name='API集成测试股票',
                current_price=28.0,  # 12%盈利
                change_percent=12.0,
                record_date=date.today()
            )
            price_record.save()
            
            review_record = ReviewRecord(
                stock_code='000004',
                review_date=date.today(),
                holding_days=8,
                price_up_score=1,
                bbi_score=1,
                volume_score=1,
                trend_score=1,
                j_score=1,
                analysis='API测试复盘',
                decision='hold',
                reason='API测试'
            )
            review_record.save()
            
            # 4. 通过API获取持仓提醒
            response = client.get('/api/holdings/alerts')
            assert response.status_code == 200
            alerts = response.get_json()['data']
            
            # 应该有提醒（持仓8天，盈利12%，符合6-10天盈利超过10%的条件）
            relevant_alerts = [a for a in alerts if a['stock_code'] == '000004' and a['strategy_name'] == 'API集成测试策略']
            assert len(relevant_alerts) > 0
            
            alert = relevant_alerts[0]
            assert alert['alert_type'] == 'sell_partial'
            assert alert['sell_ratio'] == 0.4
            
            # 5. 获取提醒汇总
            response = client.get('/api/holdings/alerts/summary')
            assert response.status_code == 200
            summary = response.get_json()['data']
            assert summary['total_alerts'] > 0
            
            # 6. 测试策略规则
            test_data = {
                'rule': {
                    "day_range": [6, 10],
                    "profit_threshold": 0.10,
                    "action": "sell_partial",
                    "sell_ratio": 0.4,
                    "condition": "profit_exceed"
                },
                'holding_days': 8,
                'profit_loss_ratio': 0.12
            }
            
            response = client.post('/api/strategies/test-rule',
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            result = response.get_json()['data']
            assert result['rule_applies'] == True
            assert result['rule_triggered'] == True
            
            # 7. 删除策略
            response = client.delete(f'/api/strategies/{strategy_id}')
            assert response.status_code == 200
            
            # 清理数据
            buy_record.delete()
            price_record.delete()
            review_record.delete()
    
    def test_default_strategy_management(self, client):
        """测试默认策略管理"""
        # 重置默认策略
        response = client.post('/api/strategies/default/reset')
        assert response.status_code == 200
        
        default_strategy = response.get_json()['data']
        assert default_strategy['strategy_name'] == '默认持仓策略'
        assert default_strategy['is_active'] == True
        assert 'rules_list' in default_strategy
        
        # 获取默认策略
        response = client.get('/api/strategies/default')
        assert response.status_code == 200
        
        # 获取激活的策略（应该包含默认策略）
        response = client.get('/api/strategies/active')
        assert response.status_code == 200
        
        active_strategies = response.get_json()['data']
        default_found = any(s['strategy_name'] == '默认持仓策略' for s in active_strategies)
        assert default_found == True