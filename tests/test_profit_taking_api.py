"""
分批止盈API接口单元测试
"""
import pytest
from datetime import datetime
import json
from models.trade_record import TradeRecord
from models.configuration import Configuration
from services.profit_taking_service import ProfitTakingService


class TestProfitTakingAPI:
    """分批止盈API接口测试"""
    
    def test_get_profit_targets_success(self, client, app, db_session):
        """测试获取止盈目标API成功"""
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
            
            # 创建止盈目标
            targets_data = [
                {'target_price': 11.00, 'sell_ratio': 0.30},
                {'target_price': 12.00, 'sell_ratio': 0.40}
            ]
            ProfitTakingService.create_profit_targets(trade.id, targets_data)
            
            # 调用API获取止盈目标
            response = client.get(f'/api/trades/{trade.id}/profit-targets')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['message'] == '获取止盈目标成功'
            
            # 验证返回的数据结构
            summary = data['data']
            assert summary['trade_id'] == trade.id
            assert summary['use_batch_profit_taking'] is True
            assert summary['targets_count'] == 2
            assert len(summary['targets']) == 2
            assert summary['total_sell_ratio'] == 0.70
            assert summary['total_expected_profit_ratio'] > 0
    
    def test_get_profit_targets_trade_not_found(self, client, app, db_session):
        """测试获取不存在交易记录的止盈目标"""
        with app.app_context():
            response = client.get('/api/trades/99999/profit-targets')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'NOT_FOUND'
            assert '交易记录 99999 不存在' in data['error']['message']
    
    def test_get_profit_targets_no_targets(self, client, app, db_session):
        """测试获取没有止盈目标的交易记录"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建买入交易记录但不设置止盈目标
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
            
            response = client.get(f'/api/trades/{trade.id}/profit-targets')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            summary = data['data']
            assert summary['targets_count'] == 0
            assert len(summary['targets']) == 0
            assert summary['use_batch_profit_taking'] is False
    
    def test_set_profit_targets_success(self, client, app, db_session):
        """测试设置止盈目标API成功"""
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
            request_data = {
                'profit_targets': [
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
            }
            
            # 调用API设置止盈目标
            response = client.put(f'/api/trades/{trade.id}/profit-targets',
                                data=json.dumps(request_data),
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['message'] == '设置止盈目标成功'
            
            # 验证返回的汇总信息
            summary = data['data']
            assert summary['trade_id'] == trade.id
            assert summary['use_batch_profit_taking'] is True
            assert summary['targets_count'] == 3
            assert len(summary['targets']) == 3
            assert summary['total_sell_ratio'] == 1.00
    
    def test_set_profit_targets_empty_request(self, client, app, db_session):
        """测试设置止盈目标API空请求"""
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
            
            # 发送空的止盈目标列表
            response = client.put(f'/api/trades/{trade.id}/profit-targets',
                                data=json.dumps({'profit_targets': []}),
                                content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert '止盈目标列表不能为空' in data['error']['message']
    
    def test_set_profit_targets_empty_targets_list(self, client, app, db_session):
        """测试设置止盈目标API空目标列表"""
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
            
            request_data = {'profit_targets': []}
            
            response = client.put(f'/api/trades/{trade.id}/profit-targets',
                                data=json.dumps(request_data),
                                content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert '止盈目标列表不能为空' in data['error']['message']
    
    def test_set_profit_targets_invalid_data_format(self, client, app, db_session):
        """测试设置止盈目标API无效数据格式"""
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
            
            # 止盈目标不是字典格式
            request_data = {
                'profit_targets': ['invalid_format']
            }
            
            response = client.put(f'/api/trades/{trade.id}/profit-targets',
                                data=json.dumps(request_data),
                                content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert '第1个止盈目标数据格式无效' in data['error']['message']
    
    def test_set_profit_targets_validation_error(self, client, app, db_session):
        """测试设置止盈目标API验证错误"""
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
            request_data = {
                'profit_targets': [
                    {'target_price': 11.00, 'sell_ratio': 0.60},
                    {'target_price': 12.00, 'sell_ratio': 0.50}  # 总计110%
                ]
            }
            
            response = client.put(f'/api/trades/{trade.id}/profit-targets',
                                data=json.dumps(request_data),
                                content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            error = data['error']
            assert hasattr(error, 'message') or 'message' in error
            # Check that it's a validation error about total ratio
            assert 'validation' in str(error).lower() or 'total' in str(error).lower()
    
    def test_set_profit_targets_trade_not_found(self, client, app, db_session):
        """测试为不存在的交易记录设置止盈目标"""
        with app.app_context():
            request_data = {
                'profit_targets': [
                    {'target_price': 11.00, 'sell_ratio': 0.50}
                ]
            }
            
            response = client.put('/api/trades/99999/profit-targets',
                                data=json.dumps(request_data),
                                content_type='application/json')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'NOT_FOUND'
    
    def test_validate_profit_targets_success(self, client, app, db_session):
        """测试验证止盈目标API成功"""
        with app.app_context():
            request_data = {
                'buy_price': 10.00,
                'profit_targets': [
                    {
                        'target_price': 11.00,
                        'profit_ratio': 0.10,
                        'sell_ratio': 0.30
                    },
                    {
                        'target_price': 12.00,
                        'profit_ratio': 0.20,
                        'sell_ratio': 0.40
                    }
                ]
            }
            
            response = client.post('/api/trades/validate-profit-targets',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['message'] == '止盈目标验证通过'
            
            # 验证返回的计算结果
            result = data['data']['validation_result']
            assert 'total_expected_profit_ratio' in result
            assert 'total_sell_ratio' in result
            assert 'targets_detail' in result
            assert result['total_sell_ratio'] == 0.70
            assert len(result['targets_detail']) == 2
    
    def test_validate_profit_targets_empty_request(self, client, app, db_session):
        """测试验证止盈目标API空请求"""
        with app.app_context():
            response = client.post('/api/trades/validate-profit-targets',
                                 data=json.dumps({}),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['is_valid'] is False
            assert 'validation_errors' in data['data']
    
    def test_validate_profit_targets_missing_buy_price(self, client, app, db_session):
        """测试验证止盈目标API缺少买入价格"""
        with app.app_context():
            request_data = {
                'profit_targets': [
                    {'target_price': 11.00, 'sell_ratio': 0.50}
                ]
            }
            
            response = client.post('/api/trades/validate-profit-targets',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['is_valid'] is False
            assert 'validation_errors' in data['data']
    
    def test_validate_profit_targets_invalid_buy_price(self, client, app, db_session):
        """测试验证止盈目标API无效买入价格"""
        with app.app_context():
            # 测试买入价格为0
            request_data = {
                'buy_price': 0,
                'profit_targets': [
                    {'target_price': 11.00, 'sell_ratio': 0.50}
                ]
            }
            
            response = client.post('/api/trades/validate-profit-targets',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['is_valid'] is False
            
            # 测试买入价格格式无效
            request_data = {
                'buy_price': 'invalid',
                'profit_targets': [
                    {'target_price': 11.00, 'sell_ratio': 0.50}
                ]
            }
            
            response = client.post('/api/trades/validate-profit-targets',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['is_valid'] is False
    
    def test_validate_profit_targets_empty_targets_list(self, client, app, db_session):
        """测试验证止盈目标API空目标列表"""
        with app.app_context():
            request_data = {
                'buy_price': 10.00,
                'profit_targets': []
            }
            
            response = client.post('/api/trades/validate-profit-targets',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['is_valid'] is False
    
    def test_validate_profit_targets_invalid_target_format(self, client, app, db_session):
        """测试验证止盈目标API无效目标格式"""
        with app.app_context():
            request_data = {
                'buy_price': 10.00,
                'profit_targets': ['invalid_format']
            }
            
            response = client.post('/api/trades/validate-profit-targets',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['is_valid'] is False
    
    def test_validate_profit_targets_validation_error(self, client, app, db_session):
        """测试验证止盈目标API验证错误"""
        with app.app_context():
            request_data = {
                'buy_price': 10.00,
                'profit_targets': [
                    {'target_price': 8.00, 'sell_ratio': 0.50}  # 止盈价格低于买入价格
                ]
            }
            
            response = client.post('/api/trades/validate-profit-targets',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['is_valid'] is False
            assert 'validation_errors' in data['data']
    
    def test_set_profit_targets_update_existing(self, client, app, db_session):
        """测试更新现有止盈目标"""
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
            
            # 先设置初始止盈目标
            initial_data = {
                'profit_targets': [
                    {'target_price': 11.00, 'sell_ratio': 0.50}
                ]
            }
            
            response = client.put(f'/api/trades/{trade.id}/profit-targets',
                                data=json.dumps(initial_data),
                                content_type='application/json')
            assert response.status_code == 200
            
            # 更新止盈目标
            updated_data = {
                'profit_targets': [
                    {'target_price': 11.50, 'sell_ratio': 0.30},
                    {'target_price': 12.50, 'sell_ratio': 0.40}
                ]
            }
            
            response = client.put(f'/api/trades/{trade.id}/profit-targets',
                                data=json.dumps(updated_data),
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            # 验证更新后的目标
            summary = data['data']
            assert summary['targets_count'] == 2
            assert summary['total_sell_ratio'] == 0.70
            
            # 验证具体的目标价格
            targets = summary['targets']
            assert targets[0]['target_price'] == 11.50
            assert targets[1]['target_price'] == 12.50
    
    def test_profit_targets_api_integration(self, client, app, db_session):
        """测试止盈目标API集成流程"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 1. 创建买入交易记录
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
            
            # 2. 验证止盈目标数据
            validate_data = {
                'buy_price': 10.00,
                'profit_targets': [
                    {'target_price': 11.00, 'sell_ratio': 0.30},
                    {'target_price': 12.00, 'sell_ratio': 0.40},
                    {'target_price': 13.00, 'sell_ratio': 0.30}
                ]
            }
            
            response = client.post('/api/trades/validate-profit-targets',
                                 data=json.dumps(validate_data),
                                 content_type='application/json')
            assert response.status_code == 200
            
            # 3. 设置止盈目标
            set_data = {
                'profit_targets': validate_data['profit_targets']
            }
            
            response = client.put(f'/api/trades/{trade.id}/profit-targets',
                                data=json.dumps(set_data),
                                content_type='application/json')
            assert response.status_code == 200
            
            # 4. 获取止盈目标
            response = client.get(f'/api/trades/{trade.id}/profit-targets')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            summary = data['data']
            
            # 验证完整的数据流
            assert summary['trade_id'] == trade.id
            assert summary['use_batch_profit_taking'] is True
            assert summary['targets_count'] == 3
            assert summary['total_sell_ratio'] == 1.00
            assert len(summary['targets']) == 3
            
            # 验证目标顺序
            targets = summary['targets']
            assert targets[0]['sequence_order'] == 1
            assert targets[1]['sequence_order'] == 2
            assert targets[2]['sequence_order'] == 3
            
            # 验证目标价格
            assert targets[0]['target_price'] == 11.00
            assert targets[1]['target_price'] == 12.00
            assert targets[2]['target_price'] == 13.00