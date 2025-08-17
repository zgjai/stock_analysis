"""
交易记录订正功能集成测试
"""
import pytest
import json
from datetime import datetime
from models.configuration import Configuration
from models.trade_record import TradeRecord, TradeCorrection
from services.trading_service import TradingService


class TestCorrectionIntegration:
    """交易记录订正功能集成测试"""
    
    def test_complete_correction_workflow(self, client, app, db_session):
        """测试完整的订正工作流程"""
        with app.app_context():
            # 1. 设置配置
            Configuration.set_buy_reasons(['少妇B1战法', '少妇B2战法'])
            
            # 2. 创建原始交易记录
            original_trade_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'reason': '少妇B1战法',
                'stop_loss_price': 11.00,
                'take_profit_ratio': 0.20,
                'sell_ratio': 0.50,
                'notes': '原始交易记录'
            }
            
            response = client.post('/api/trades', 
                                 data=json.dumps(original_trade_data),
                                 content_type='application/json')
            
            assert response.status_code == 201
            original_trade = json.loads(response.data)['data']
            original_trade_id = original_trade['id']
            
            # 验证原始记录创建成功
            assert original_trade['stock_code'] == '000001'
            assert original_trade['price'] == 12.50
            assert original_trade['is_corrected'] is False
            
            # 3. 订正交易记录
            correction_data = {
                'reason': '价格和数量录入错误，需要订正',
                'corrected_data': {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'trade_type': 'buy',
                    'price': 13.80,  # 修改价格
                    'quantity': 1200,  # 修改数量
                    'reason': '少妇B2战法',  # 修改原因
                    'stop_loss_price': 12.00,  # 修改止损价格
                    'take_profit_ratio': 0.25,  # 修改止盈比例
                    'sell_ratio': 0.60,  # 修改卖出比例
                    'notes': '订正后的交易记录'  # 修改备注
                }
            }
            
            response = client.post(f'/api/trades/{original_trade_id}/correct', 
                                 data=json.dumps(correction_data),
                                 content_type='application/json')
            
            assert response.status_code == 201
            corrected_trade = json.loads(response.data)['data']
            corrected_trade_id = corrected_trade['id']
            
            # 验证订正记录创建成功
            assert corrected_trade['id'] != original_trade_id
            assert corrected_trade['stock_code'] == '000001'
            assert corrected_trade['price'] == 13.80
            assert corrected_trade['quantity'] == 1200
            assert corrected_trade['reason'] == '少妇B2战法'
            assert corrected_trade['original_record_id'] == original_trade_id
            assert corrected_trade['correction_reason'] == '价格和数量录入错误，需要订正'
            assert corrected_trade['is_corrected'] is False
            
            # 验证止损止盈重新计算
            expected_loss_ratio = (13.80 - 12.00) / 13.80
            expected_profit_ratio = 0.25 * 0.60
            assert abs(corrected_trade['expected_loss_ratio'] - expected_loss_ratio) < 0.001
            assert abs(corrected_trade['expected_profit_ratio'] - expected_profit_ratio) < 0.001
            
            # 4. 验证原始记录被标记为已订正
            response = client.get(f'/api/trades/{original_trade_id}')
            assert response.status_code == 200
            updated_original = json.loads(response.data)['data']
            assert updated_original['is_corrected'] is True
            
            # 5. 获取订正历史
            response = client.get(f'/api/trades/{original_trade_id}/history')
            assert response.status_code == 200
            history = json.loads(response.data)['data']
            
            assert len(history) == 1
            correction_record = history[0]
            assert correction_record['original_trade_id'] == original_trade_id
            assert correction_record['corrected_trade_id'] == corrected_trade_id
            assert correction_record['correction_reason'] == '价格和数量录入错误，需要订正'
            
            # 验证变更字段记录
            corrected_fields = correction_record['corrected_fields']
            assert 'price' in corrected_fields
            assert 'quantity' in corrected_fields
            assert 'reason' in corrected_fields
            assert 'notes' in corrected_fields
            
            # 6. 验证数据库中的记录
            # 应该有2条交易记录：1条原始（已标记订正）+ 1条订正后
            all_trades = TradeRecord.query.all()
            assert len(all_trades) == 2
            
            # 应该有1条订正历史记录
            corrections = TradeCorrection.query.all()
            assert len(corrections) == 1
            
            # 7. 测试筛选功能
            # 获取已订正的记录
            response = client.get('/api/trades?is_corrected=true')
            assert response.status_code == 200
            corrected_trades = json.loads(response.data)['data']['trades']
            assert len(corrected_trades) == 1
            assert corrected_trades[0]['id'] == original_trade_id
            
            # 获取未订正的记录
            response = client.get('/api/trades?is_corrected=false')
            assert response.status_code == 200
            uncorrected_trades = json.loads(response.data)['data']['trades']
            assert len(uncorrected_trades) == 1
            assert uncorrected_trades[0]['id'] == corrected_trade_id
            
            # 8. 测试删除保护
            # 尝试删除有订正记录的原始交易应该失败
            response = client.delete(f'/api/trades/{original_trade_id}')
            assert response.status_code == 400
            error_data = json.loads(response.data)
            assert '无法删除有订正记录关联的交易记录' in error_data['error']['message']
            
            # 尝试删除订正后的交易也应该失败
            response = client.delete(f'/api/trades/{corrected_trade_id}')
            assert response.status_code == 400
    
    def test_multiple_corrections_workflow(self, client, app, db_session):
        """测试多次订正的工作流程"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法', '少妇B2战法', '少妇SB1战法'])
            
            # 1. 创建原始交易记录
            original_trade_data = {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'buy',
                'price': 20.00,
                'quantity': 500,
                'reason': '少妇B1战法'
            }
            
            response = client.post('/api/trades', 
                                 data=json.dumps(original_trade_data),
                                 content_type='application/json')
            
            original_trade_id = json.loads(response.data)['data']['id']
            
            # 2. 第一次订正
            first_correction = {
                'reason': '第一次订正：价格错误',
                'corrected_data': {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'trade_type': 'buy',
                    'price': 21.00,  # 修改价格
                    'quantity': 500,
                    'reason': '少妇B1战法'
                }
            }
            
            response = client.post(f'/api/trades/{original_trade_id}/correct', 
                                 data=json.dumps(first_correction),
                                 content_type='application/json')
            
            first_corrected_id = json.loads(response.data)['data']['id']
            
            # 3. 第二次订正（订正第一次订正的记录）
            second_correction = {
                'reason': '第二次订正：原因错误',
                'corrected_data': {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'trade_type': 'buy',
                    'price': 21.00,
                    'quantity': 500,
                    'reason': '少妇B2战法'  # 修改原因
                }
            }
            
            response = client.post(f'/api/trades/{first_corrected_id}/correct', 
                                 data=json.dumps(second_correction),
                                 content_type='application/json')
            
            second_corrected_id = json.loads(response.data)['data']['id']
            
            # 4. 验证订正链
            # 原始记录 -> 第一次订正 -> 第二次订正
            
            # 获取原始记录的订正历史
            response = client.get(f'/api/trades/{original_trade_id}/history')
            original_history = json.loads(response.data)['data']
            assert len(original_history) == 1
            assert original_history[0]['corrected_trade_id'] == first_corrected_id
            
            # 获取第一次订正记录的订正历史
            # 注意：这会返回所有与该记录相关的订正（作为原始记录和作为订正记录）
            response = client.get(f'/api/trades/{first_corrected_id}/history')
            first_history = json.loads(response.data)['data']
            assert len(first_history) == 2  # 包含：原始->第一次 和 第一次->第二次
            
            # 找到第一次订正记录作为原始记录的订正（即第二次订正）
            second_correction_record = None
            for record in first_history:
                if record['original_trade_id'] == first_corrected_id:
                    second_correction_record = record
                    break
            
            assert second_correction_record is not None
            assert second_correction_record['corrected_trade_id'] == second_corrected_id
            
            # 获取第二次订正记录的订正历史
            # 注意：这会返回该记录作为corrected_trade_id的记录
            response = client.get(f'/api/trades/{second_corrected_id}/history')
            second_history = json.loads(response.data)['data']
            assert len(second_history) == 1  # 包含：第一次->第二次的订正记录
            assert second_history[0]['corrected_trade_id'] == second_corrected_id
            assert second_history[0]['original_trade_id'] == first_corrected_id
            
            # 5. 验证数据库状态
            # 应该有3条交易记录
            all_trades = TradeRecord.query.all()
            assert len(all_trades) == 3
            
            # 应该有2条订正历史记录
            corrections = TradeCorrection.query.all()
            assert len(corrections) == 2
            
            # 验证订正状态
            original = TradeRecord.query.get(original_trade_id)
            first_corrected = TradeRecord.query.get(first_corrected_id)
            second_corrected = TradeRecord.query.get(second_corrected_id)
            
            assert original.is_corrected is True
            assert first_corrected.is_corrected is True
            assert second_corrected.is_corrected is False  # 最新的记录未被订正
    
    def test_correction_permission_control(self, client, app, db_session):
        """测试订正权限控制"""
        with app.app_context():
            Configuration.set_buy_reasons(['少妇B1战法'])
            
            # 创建交易记录
            trade_data = {
                'stock_code': '000003',
                'stock_name': '中国平安',
                'trade_type': 'buy',
                'price': 50.00,
                'quantity': 100,
                'reason': '少妇B1战法'
            }
            
            response = client.post('/api/trades', 
                                 data=json.dumps(trade_data),
                                 content_type='application/json')
            
            trade_id = json.loads(response.data)['data']['id']
            
            # 测试各种无效的订正请求
            
            # 1. 缺少订正原因
            invalid_correction1 = {
                'corrected_data': {
                    'stock_code': '000003',
                    'stock_name': '中国平安',
                    'trade_type': 'buy',
                    'price': 51.00,
                    'quantity': 100,
                    'reason': '少妇B1战法'
                }
            }
            
            response = client.post(f'/api/trades/{trade_id}/correct', 
                                 data=json.dumps(invalid_correction1),
                                 content_type='application/json')
            
            assert response.status_code == 400
            assert '订正原因不能为空' in json.loads(response.data)['error']['message']
            
            # 2. 缺少订正数据
            invalid_correction2 = {
                'reason': '测试订正'
            }
            
            response = client.post(f'/api/trades/{trade_id}/correct', 
                                 data=json.dumps(invalid_correction2),
                                 content_type='application/json')
            
            assert response.status_code == 400
            assert '订正数据不能为空' in json.loads(response.data)['error']['message']
            
            # 3. 空的订正原因
            invalid_correction3 = {
                'reason': '',
                'corrected_data': {
                    'stock_code': '000003',
                    'stock_name': '中国平安',
                    'trade_type': 'buy',
                    'price': 51.00,
                    'quantity': 100,
                    'reason': '少妇B1战法'
                }
            }
            
            response = client.post(f'/api/trades/{trade_id}/correct', 
                                 data=json.dumps(invalid_correction3),
                                 content_type='application/json')
            
            assert response.status_code == 400
            assert '订正原因不能为空' in json.loads(response.data)['error']['message']
            
            # 4. 订正不存在的交易记录
            valid_correction = {
                'reason': '测试订正',
                'corrected_data': {
                    'stock_code': '000003',
                    'stock_name': '中国平安',
                    'trade_type': 'buy',
                    'price': 51.00,
                    'quantity': 100,
                    'reason': '少妇B1战法'
                }
            }
            
            response = client.post('/api/trades/99999/correct', 
                                 data=json.dumps(valid_correction),
                                 content_type='application/json')
            
            assert response.status_code == 404
            assert json.loads(response.data)['error']['code'] == 'NOT_FOUND'