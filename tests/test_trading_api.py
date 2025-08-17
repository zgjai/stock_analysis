"""
交易记录管理API集成测试
"""
import pytest
import json
from datetime import datetime
from models.configuration import Configuration
from models.trade_record import TradeRecord


class TestTradingAPI:
    """交易记录API集成测试"""
    
    def test_create_trade_success(self, client, app, db_session):
        """测试创建交易记录API成功"""
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
            
            response = client.post('/api/trades', 
                                 data=json.dumps(trade_data),
                                 content_type='application/json')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['message'] == '交易记录创建成功'
            assert data['data']['stock_code'] == '000001'
            assert data['data']['trade_type'] == 'buy'
            assert data['data']['price'] == 12.50
    
    def test_create_trade_missing_data(self, client, app, db_session):
        """测试创建交易记录API缺少数据"""
        with app.app_context():
            response = client.post('/api/trades', 
                                 data=json.dumps({}),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'VALIDATION_ERROR' in data['error']['code']
    
    def test_create_trade_invalid_reason(self, client, app, db_session):
        """测试创建交易记录API无效原因"""
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
            
            response = client.post('/api/trades', 
                                 data=json.dumps(trade_data),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert '无效的buy原因' in data['error']['message']
    
    def test_get_trades_list(self, client, app, db_session):
        """测试获取交易记录列表API"""
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
                    'reason': '少妇B1战法'
                },
                {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'trade_type': 'sell',
                    'price': 15.80,
                    'quantity': 500,
                    'reason': '部分止盈'
                }
            ]
            
            for trade_data in trades_data:
                client.post('/api/trades', 
                          data=json.dumps(trade_data),
                          content_type='application/json')
            
            # 获取交易记录列表
            response = client.get('/api/trades')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['total'] == 2
            assert len(data['data']['trades']) == 2
    
    def test_get_trades_with_filters(self, client, app, db_session):
        """测试获取交易记录列表API带筛选条件"""
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
                    'reason': '少妇B1战法'
                },
                {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'trade_type': 'sell',
                    'price': 15.80,
                    'quantity': 500,
                    'reason': '部分止盈'
                }
            ]
            
            for trade_data in trades_data:
                client.post('/api/trades', 
                          data=json.dumps(trade_data),
                          content_type='application/json')
            
            # 按股票代码筛选
            response = client.get('/api/trades?stock_code=000001')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['total'] == 1
            assert data['data']['trades'][0]['stock_code'] == '000001'
            
            # 按交易类型筛选
            response = client.get('/api/trades?trade_type=buy')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['total'] == 1
            assert data['data']['trades'][0]['trade_type'] == 'buy'
    
    def test_get_trades_with_pagination(self, client, app, db_session):
        """测试获取交易记录列表API分页"""
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
                client.post('/api/trades', 
                          data=json.dumps(trade_data),
                          content_type='application/json')
            
            # 测试分页
            response = client.get('/api/trades?page=1&per_page=2')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['total'] == 5
            assert len(data['data']['trades']) == 2
            assert data['data']['pages'] == 3
            assert data['data']['current_page'] == 1
    
    def test_get_trade_by_id(self, client, app, db_session):
        """测试根据ID获取交易记录API"""
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
            
            # 创建交易记录
            response = client.post('/api/trades', 
                                 data=json.dumps(trade_data),
                                 content_type='application/json')
            
            created_trade = json.loads(response.data)['data']
            trade_id = created_trade['id']
            
            # 获取交易记录详情
            response = client.get(f'/api/trades/{trade_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['id'] == trade_id
            assert data['data']['stock_code'] == '000001'
    
    def test_get_trade_not_found(self, client, app, db_session):
        """测试获取不存在的交易记录API"""
        with app.app_context():
            response = client.get('/api/trades/99999')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'NOT_FOUND'
    
    def test_update_trade_success(self, client, app, db_session):
        """测试更新交易记录API成功"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法', '少妇B2战法'])
            
            # 创建交易记录
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            
            response = client.post('/api/trades', 
                                 data=json.dumps(trade_data),
                                 content_type='application/json')
            
            created_trade = json.loads(response.data)['data']
            trade_id = created_trade['id']
            
            # 更新交易记录
            update_data = {
                'price': 13.00,
                'quantity': 1200,
                'reason': '少妇B2战法'
            }
            
            response = client.put(f'/api/trades/{trade_id}', 
                                data=json.dumps(update_data),
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['price'] == 13.00
            assert data['data']['quantity'] == 1200
            assert data['data']['reason'] == '少妇B2战法'
    
    def test_delete_trade_success(self, client, app, db_session):
        """测试删除交易记录API成功"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建交易记录
            trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            
            response = client.post('/api/trades', 
                                 data=json.dumps(trade_data),
                                 content_type='application/json')
            
            created_trade = json.loads(response.data)['data']
            trade_id = created_trade['id']
            
            # 删除交易记录
            response = client.delete(f'/api/trades/{trade_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['message'] == '交易记录删除成功'
            
            # 验证记录已被删除
            response = client.get(f'/api/trades/{trade_id}')
            assert response.status_code == 404
    
    def test_calculate_risk_reward_api(self, client, app, db_session):
        """测试计算止损止盈预期API"""
        with app.app_context():
            calculation_data = {
                'buy_price': 12.50,
                'stop_loss_price': 11.00,
                'take_profit_ratio': 0.20,
                'sell_ratio': 0.50
            }
            
            response = client.post('/api/trades/calculate-risk-reward', 
                                 data=json.dumps(calculation_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'expected_loss_ratio' in data['data']
            assert 'expected_profit_ratio' in data['data']
            assert 'risk_reward_ratio' in data['data']
    
    def test_correct_trade_record_api(self, client, app, db_session):
        """测试订正交易记录API"""
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
            
            response = client.post('/api/trades', 
                                 data=json.dumps(trade_data),
                                 content_type='application/json')
            
            original_trade = json.loads(response.data)['data']
            trade_id = original_trade['id']
            
            # 订正交易记录
            correction_data = {
                'reason': '价格录入错误',
                'corrected_data': {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': 13.00,
                    'quantity': 1000,
                    'reason': '少妇B1战法'
                }
            }
            
            response = client.post(f'/api/trades/{trade_id}/correct', 
                                 data=json.dumps(correction_data),
                                 content_type='application/json')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['price'] == 13.00
            assert data['data']['original_record_id'] == trade_id
            assert data['data']['correction_reason'] == '价格录入错误'
    
    def test_get_correction_history_api(self, client, app, db_session):
        """测试获取订正历史API"""
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
            
            response = client.post('/api/trades', 
                                 data=json.dumps(trade_data),
                                 content_type='application/json')
            
            original_trade = json.loads(response.data)['data']
            trade_id = original_trade['id']
            
            # 订正交易记录
            correction_data = {
                'reason': '价格录入错误',
                'corrected_data': {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': 13.00,
                    'quantity': 1000,
                    'reason': '少妇B1战法'
                }
            }
            
            client.post(f'/api/trades/{trade_id}/correct', 
                       data=json.dumps(correction_data),
                       content_type='application/json')
            
            # 获取订正历史
            response = client.get(f'/api/trades/{trade_id}/history')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['data']) == 1
            assert data['data'][0]['correction_reason'] == '价格录入错误'
    
    def test_correct_trade_record_api_missing_reason(self, client, app, db_session):
        """测试订正交易记录API缺少原因"""
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
            
            response = client.post('/api/trades', 
                                 data=json.dumps(trade_data),
                                 content_type='application/json')
            
            original_trade = json.loads(response.data)['data']
            trade_id = original_trade['id']
            
            # 尝试订正但不提供原因
            correction_data = {
                'corrected_data': {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': 13.00,
                    'quantity': 1000,
                    'reason': '少妇B1战法'
                }
            }
            
            response = client.post(f'/api/trades/{trade_id}/correct', 
                                 data=json.dumps(correction_data),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert '订正原因不能为空' in data['error']['message']
    
    def test_correct_trade_record_api_missing_corrected_data(self, client, app, db_session):
        """测试订正交易记录API缺少订正数据"""
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
            
            response = client.post('/api/trades', 
                                 data=json.dumps(trade_data),
                                 content_type='application/json')
            
            original_trade = json.loads(response.data)['data']
            trade_id = original_trade['id']
            
            # 尝试订正但不提供订正数据
            correction_data = {
                'reason': '测试订正'
            }
            
            response = client.post(f'/api/trades/{trade_id}/correct', 
                                 data=json.dumps(correction_data),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert '订正数据不能为空' in data['error']['message']
    
    def test_correct_trade_record_api_not_found(self, client, app, db_session):
        """测试订正不存在的交易记录API"""
        with app.app_context():
            correction_data = {
                'reason': '测试订正',
                'corrected_data': {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': 13.00,
                    'quantity': 1000,
                    'reason': '少妇B1战法'
                }
            }
            
            response = client.post('/api/trades/99999/correct', 
                                 data=json.dumps(correction_data),
                                 content_type='application/json')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'NOT_FOUND'
    
    def test_get_correction_history_api_not_found(self, client, app, db_session):
        """测试获取不存在交易记录的订正历史API"""
        with app.app_context():
            response = client.get('/api/trades/99999/history')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['data']) == 0  # 空历史记录
    
    def test_get_trades_list_with_corrected_filter(self, client, app, db_session):
        """测试获取交易记录列表按订正状态筛选"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建两条交易记录
            trade_data1 = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            
            trade_data2 = {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'buy',
                'price': 15.80,
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            
            response1 = client.post('/api/trades', 
                                  data=json.dumps(trade_data1),
                                  content_type='application/json')
            
            response2 = client.post('/api/trades', 
                                  data=json.dumps(trade_data2),
                                  content_type='application/json')
            
            trade1_id = json.loads(response1.data)['data']['id']
            
            # 订正第一条记录
            correction_data = {
                'reason': '价格录入错误',
                'corrected_data': {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': 13.00,
                    'quantity': 1000,
                    'reason': '少妇B1战法'
                }
            }
            
            client.post(f'/api/trades/{trade1_id}/correct', 
                       data=json.dumps(correction_data),
                       content_type='application/json')
            
            # 筛选已订正的记录
            response = client.get('/api/trades?is_corrected=true')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['total'] == 1
            assert data['data']['trades'][0]['is_corrected'] is True
            
            # 筛选未订正的记录
            response = client.get('/api/trades?is_corrected=false')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            # 应该有2条记录：1条原始未订正记录 + 1条订正后的记录
            assert data['data']['total'] == 2
    
    def test_get_trade_config_api(self, client, app, db_session):
        """测试获取交易配置API"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法', '少妇SB1战法'])
            Configuration.set_sell_reasons(['部分止盈', '止损'])
            
            response = client.get('/api/trades/config')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'buy_reasons' in data['data']
            assert 'sell_reasons' in data['data']
            assert data['data']['buy_reasons'] == ['少妇B1战法', '少妇SB1战法']
            assert data['data']['sell_reasons'] == ['部分止盈', '止损']
    
    def test_get_buy_reasons_api(self, client, app, db_session):
        """测试获取买入原因API"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法', '少妇SB1战法'])
            
            response = client.get('/api/trades/config/buy-reasons')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['buy_reasons'] == ['少妇B1战法', '少妇SB1战法']
    
    def test_set_buy_reasons_api(self, client, app, db_session):
        """测试设置买入原因API"""
        with app.app_context():
            new_reasons = ['新买入原因1', '新买入原因2']
            
            response = client.put('/api/trades/config/buy-reasons', 
                                data=json.dumps({'buy_reasons': new_reasons}),
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['buy_reasons'] == new_reasons
            
            # 验证配置已更新
            response = client.get('/api/trades/config/buy-reasons')
            data = json.loads(response.data)
            assert data['data']['buy_reasons'] == new_reasons
    
    def test_get_sell_reasons_api(self, client, app, db_session):
        """测试获取卖出原因API"""
        with app.app_context():
            Configuration.set_sell_reasons(['部分止盈', '止损'])
            
            response = client.get('/api/trades/config/sell-reasons')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['sell_reasons'] == ['部分止盈', '止损']
    
    def test_set_sell_reasons_api(self, client, app, db_session):
        """测试设置卖出原因API"""
        with app.app_context():
            new_reasons = ['新卖出原因1', '新卖出原因2']
            
            response = client.put('/api/trades/config/sell-reasons', 
                                data=json.dumps({'sell_reasons': new_reasons}),
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['sell_reasons'] == new_reasons
    
    def test_get_trade_stats_api(self, client, app, db_session):
        """测试获取交易统计API"""
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
                    'reason': '少妇B1战法'
                },
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'sell',
                    'price': 13.50,
                    'quantity': 500,
                    'reason': '部分止盈'
                },
                {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'trade_type': 'buy',
                    'price': 15.80,
                    'quantity': 1000,
                    'reason': '少妇B1战法'
                }
            ]
            
            for trade_data in trades_data:
                client.post('/api/trades', 
                          data=json.dumps(trade_data),
                          content_type='application/json')
            
            # 获取交易统计
            response = client.get('/api/trades/stats')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['total_trades'] == 3
            assert data['data']['buy_count'] == 2
            assert data['data']['sell_count'] == 1
            assert len(data['data']['stock_stats']) == 2  # 两只股票