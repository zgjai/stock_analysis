"""
复盘功能增强集成测试
测试持仓天数编辑、复盘保存功能和浮盈计算的完整集成
"""
import pytest
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from models.trade_record import TradeRecord
from models.review_record import ReviewRecord
from models.stock_price import StockPrice
from services.review_service import ReviewService
from services.trading_service import TradingService
from extensions import db


class TestHoldingDaysEditingIntegration:
    """持仓天数编辑集成测试"""
    
    def test_holding_days_crud_complete_workflow(self, client, db_session):
        """测试持仓天数CRUD完整工作流程"""
        stock_code = '000001'
        
        # 1. 创建初始持仓天数记录
        create_data = {'holding_days': 5}
        response = client.post(f'/api/holdings/{stock_code}/days',
                             json=create_data)
        
        assert response.status_code == 201
        data = response.json
        assert data['success'] is True
        assert data['data']['holding_days'] == 5
        created_id = data['data']['id']
        
        # 2. 读取持仓天数
        response = client.get(f'/api/holdings/{stock_code}/days')
        assert response.status_code == 200
        data = response.json
        assert data['data']['holding_days'] == 5
        
        # 3. 更新持仓天数
        update_data = {'holding_days': 10}
        response = client.put(f'/api/holdings/{stock_code}/days',
                            json=update_data)
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert data['data']['holding_days'] == 10
        
        # 4. 验证更新后的数据
        response = client.get(f'/api/holdings/{stock_code}/days')
        assert response.status_code == 200
        data = response.json
        assert data['data']['holding_days'] == 10
        
        # 5. 删除持仓天数记录
        response = client.delete(f'/api/holdings/{stock_code}/days')
        assert response.status_code == 200
        
        # 6. 验证删除后无法获取
        response = client.get(f'/api/holdings/{stock_code}/days')
        assert response.status_code == 200
        data = response.json
        assert data['data']['holding_days'] is None
    
    def test_holding_days_validation_integration(self, client, db_session):
        """测试持仓天数验证集成"""
        stock_code = '000001'
        
        # 测试无效输入类型
        invalid_inputs = [
            {'holding_days': 'invalid'},  # 字符串
            {'holding_days': -5},         # 负数
            {'holding_days': 0},          # 零
            {'holding_days': 3.14},       # 小数
            {'holding_days': None},       # None
            {}                            # 空数据
        ]
        
        for invalid_data in invalid_inputs:
            response = client.post(f'/api/holdings/{stock_code}/days',
                                 json=invalid_data)
            assert response.status_code == 400
            data = response.json
            assert data['success'] is False
            assert '持仓天数' in data['error']['message']
    
    def test_holding_days_with_review_integration(self, client, db_session):
        """测试持仓天数与复盘记录的集成"""
        stock_code = '000001'
        
        # 1. 创建交易记录
        trade_data = {
            'stock_code': stock_code,
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试买入'
        }
        
        response = client.post('/api/trades', json=trade_data)
        assert response.status_code == 201
        
        # 2. 创建复盘记录（包含持仓天数）
        review_data = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 0,
            'trend_score': 1,
            'j_score': 1,
            'analysis': '测试复盘',
            'decision': 'hold',
            'reason': '继续持有',
            'holding_days': 7
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        review_id = response.json['data']['id']
        
        # 3. 通过持仓天数API更新
        update_data = {'holding_days': 12}
        response = client.put(f'/api/holdings/{stock_code}/days',
                            json=update_data)
        assert response.status_code == 200
        
        # 4. 验证复盘记录中的持仓天数也被更新
        response = client.get(f'/api/reviews/{review_id}')
        assert response.status_code == 200
        data = response.json
        assert data['data']['holding_days'] == 12
        
        # 5. 获取持仓信息，验证持仓天数正确
        response = client.get(f'/api/holdings/{stock_code}')
        assert response.status_code == 200
        data = response.json
        assert data['data']['holding_days'] == 12
    
    def test_holding_days_concurrent_updates(self, client, db_session):
        """测试持仓天数并发更新"""
        stock_code = '000001'
        
        # 创建初始记录
        create_data = {'holding_days': 5}
        response = client.post(f'/api/holdings/{stock_code}/days',
                             json=create_data)
        assert response.status_code == 201
        
        # 模拟并发更新
        update_requests = [
            {'holding_days': 10},
            {'holding_days': 15},
            {'holding_days': 20}
        ]
        
        responses = []
        for update_data in update_requests:
            response = client.put(f'/api/holdings/{stock_code}/days',
                                json=update_data)
            responses.append(response)
        
        # 验证所有请求都成功
        for response in responses:
            assert response.status_code == 200
            assert response.json['success'] is True
        
        # 验证最终状态
        response = client.get(f'/api/holdings/{stock_code}/days')
        assert response.status_code == 200
        final_days = response.json['data']['holding_days']
        assert final_days in [10, 15, 20]  # 应该是其中一个值


class TestReviewSaveIntegration:
    """复盘保存功能集成测试"""
    
    def test_review_save_complete_workflow(self, client, db_session):
        """测试复盘保存完整工作流程"""
        stock_code = '000001'
        
        # 1. 创建完整的复盘记录
        review_data = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),
            'holding_days': 8,
            'current_price': 13.50,
            'floating_profit_ratio': 0.08,
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 0,
            'trend_score': 1,
            'j_score': 1,
            'analysis': '技术面良好，继续持有',
            'decision': 'hold',
            'reason': '符合持有条件'
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        data = response.json
        assert data['success'] is True
        
        review_id = data['data']['id']
        saved_review = data['data']
        
        # 验证保存的数据
        assert saved_review['stock_code'] == stock_code
        assert saved_review['holding_days'] == 8
        assert float(saved_review['current_price']) == 13.50
        assert float(saved_review['floating_profit_ratio']) == 0.08
        assert saved_review['total_score'] == 4
        assert saved_review['analysis'] == '技术面良好，继续持有'
        
        # 2. 更新复盘记录
        update_data = {
            'current_price': 14.00,
            'floating_profit_ratio': 0.12,
            'analysis': '价格继续上涨，表现优异',
            'decision': 'sell_partial'
        }
        
        response = client.put(f'/api/reviews/{review_id}', json=update_data)
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        
        updated_review = data['data']
        assert float(updated_review['current_price']) == 14.00
        assert float(updated_review['floating_profit_ratio']) == 0.12
        assert updated_review['analysis'] == '价格继续上涨，表现优异'
        assert updated_review['decision'] == 'sell_partial'
        
        # 3. 验证数据持久化
        response = client.get(f'/api/reviews/{review_id}')
        assert response.status_code == 200
        data = response.json
        persisted_review = data['data']
        
        assert float(persisted_review['current_price']) == 14.00
        assert float(persisted_review['floating_profit_ratio']) == 0.12
        assert persisted_review['analysis'] == '价格继续上涨，表现优异'
    
    def test_review_save_validation_integration(self, client, db_session):
        """测试复盘保存数据验证集成"""
        # 测试必填字段验证
        incomplete_data = {
            'review_date': date.today().isoformat(),
            'price_up_score': 1
            # 缺少 stock_code
        }
        
        response = client.post('/api/reviews', json=incomplete_data)
        assert response.status_code == 400
        data = response.json
        assert data['success'] is False
        assert 'stock_code' in data['error']['message']
        
        # 测试数据类型验证
        invalid_data = {
            'stock_code': '000001',
            'review_date': date.today().isoformat(),
            'current_price': 'invalid_price',  # 无效价格
            'floating_profit_ratio': 'invalid_ratio',  # 无效比例
            'price_up_score': 2  # 无效评分
        }
        
        response = client.post('/api/reviews', json=invalid_data)
        assert response.status_code == 400
        data = response.json
        assert data['success'] is False
    
    def test_review_save_with_floating_profit(self, client, db_session):
        """测试包含浮盈数据的复盘保存"""
        stock_code = '000001'
        
        # 1. 创建交易记录（设置成本价）
        trade_data = {
            'stock_code': stock_code,
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试买入'
        }
        
        response = client.post('/api/trades', json=trade_data)
        assert response.status_code == 201
        
        # 2. 创建包含浮盈计算的复盘记录
        current_price = 13.75
        expected_ratio = (current_price - 12.50) / 12.50  # 0.1
        
        review_data = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),
            'holding_days': 5,
            'current_price': current_price,
            'floating_profit_ratio': expected_ratio,
            'price_up_score': 1,
            'bbi_score': 1,
            'analysis': '浮盈10%，表现良好'
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        data = response.json
        
        saved_review = data['data']
        assert abs(float(saved_review['floating_profit_ratio']) - expected_ratio) < 0.001
        assert float(saved_review['current_price']) == current_price
        
        # 3. 验证浮盈数据的持久化
        review_id = saved_review['id']
        response = client.get(f'/api/reviews/{review_id}')
        assert response.status_code == 200
        
        persisted_review = response.json['data']
        assert abs(float(persisted_review['floating_profit_ratio']) - expected_ratio) < 0.001
    
    def test_review_save_error_handling(self, client, db_session):
        """测试复盘保存错误处理"""
        # 1. 测试数据库约束错误
        review_data = {
            'stock_code': '000001',
            'review_date': date.today().isoformat(),
            'price_up_score': 1
        }
        
        # 创建第一条记录
        response1 = client.post('/api/reviews', json=review_data)
        assert response1.status_code == 201
        
        # 尝试创建重复记录（相同股票代码和日期）
        response2 = client.post('/api/reviews', json=review_data)
        assert response2.status_code == 400
        data = response2.json
        assert data['success'] is False
        assert '已存在' in data['error']['message']
        
        # 2. 测试更新不存在的记录
        update_data = {'analysis': '测试更新'}
        response = client.put('/api/reviews/99999', json=update_data)
        assert response.status_code == 404
        data = response.json
        assert data['success'] is False
    
    def test_review_save_data_consistency(self, client, db_session):
        """测试复盘保存数据一致性"""
        stock_code = '000001'
        
        # 1. 创建复盘记录
        review_data = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),
            'holding_days': 10,
            'current_price': 15.00,
            'floating_profit_ratio': 0.20,
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 1,
            'trend_score': 1,
            'j_score': 1
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        review_id = response.json['data']['id']
        
        # 2. 验证总分计算一致性
        response = client.get(f'/api/reviews/{review_id}')
        assert response.status_code == 200
        data = response.json['data']
        
        expected_score = sum([
            data['price_up_score'],
            data['bbi_score'],
            data['volume_score'],
            data['trend_score'],
            data['j_score']
        ])
        assert data['total_score'] == expected_score
        
        # 3. 更新评分并验证总分重新计算
        update_data = {
            'volume_score': 0,
            'j_score': 0
        }
        
        response = client.put(f'/api/reviews/{review_id}', json=update_data)
        assert response.status_code == 200
        updated_data = response.json['data']
        
        new_expected_score = sum([
            updated_data['price_up_score'],
            updated_data['bbi_score'],
            updated_data['volume_score'],
            updated_data['trend_score'],
            updated_data['j_score']
        ])
        assert updated_data['total_score'] == new_expected_score
        assert updated_data['total_score'] == 3  # 1+1+0+1+0


class TestFloatingProfitCalculationIntegration:
    """浮盈计算集成测试"""
    
    def test_floating_profit_calculation_accuracy(self, client, db_session):
        """测试浮盈计算准确性"""
        stock_code = '000001'
        buy_price = 10.00
        
        # 1. 创建交易记录
        trade_data = {
            'stock_code': stock_code,
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': buy_price,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试买入'
        }
        
        response = client.post('/api/trades', json=trade_data)
        assert response.status_code == 201
        
        # 2. 测试不同价格的浮盈计算
        test_cases = [
            {'current_price': 11.00, 'expected_ratio': 0.10},    # 上涨10%
            {'current_price': 9.00, 'expected_ratio': -0.10},    # 下跌10%
            {'current_price': 12.50, 'expected_ratio': 0.25},    # 上涨25%
            {'current_price': 7.50, 'expected_ratio': -0.25},    # 下跌25%
            {'current_price': 10.00, 'expected_ratio': 0.00},    # 无变化
            {'current_price': 10.01, 'expected_ratio': 0.001},   # 微涨
            {'current_price': 9.99, 'expected_ratio': -0.001}    # 微跌
        ]
        
        for case in test_cases:
            calc_data = {
                'stock_code': stock_code,
                'current_price': case['current_price']
            }
            
            response = client.post('/api/reviews/calculate-floating-profit',
                                 json=calc_data)
            assert response.status_code == 200
            data = response.json
            
            assert data['success'] is True
            calculated_ratio = float(data['data']['floating_profit_ratio'])
            expected_ratio = case['expected_ratio']
            
            # 允许小的浮点数误差
            assert abs(calculated_ratio - expected_ratio) < 0.0001, \
                f"Price: {case['current_price']}, Expected: {expected_ratio}, Got: {calculated_ratio}"
            
            # 验证其他计算字段
            assert float(data['data']['buy_price']) == buy_price
            assert float(data['data']['current_price']) == case['current_price']
            
            expected_amount = (case['current_price'] - buy_price) * 1000  # 1000股
            assert abs(float(data['data']['floating_profit_amount']) - expected_amount) < 0.01
    
    def test_floating_profit_calculation_edge_cases(self, client, db_session):
        """测试浮盈计算边界情况"""
        stock_code = '000001'
        
        # 1. 测试无交易记录的情况
        calc_data = {
            'stock_code': 'NONEXISTENT',
            'current_price': 12.00
        }
        
        response = client.post('/api/reviews/calculate-floating-profit',
                             json=calc_data)
        assert response.status_code == 404
        data = response.json
        assert data['success'] is False
        assert '未找到' in data['error']['message']
        
        # 2. 创建交易记录
        trade_data = {
            'stock_code': stock_code,
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 10.00,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试买入'
        }
        
        response = client.post('/api/trades', json=trade_data)
        assert response.status_code == 201
        
        # 3. 测试无效的当前价格
        invalid_prices = [
            {'current_price': 0},        # 零价格
            {'current_price': -5.00},    # 负价格
            {'current_price': 'invalid'} # 非数字
        ]
        
        for invalid_data in invalid_prices:
            calc_data = {
                'stock_code': stock_code,
                **invalid_data
            }
            
            response = client.post('/api/reviews/calculate-floating-profit',
                                 json=calc_data)
            assert response.status_code == 400
            data = response.json
            assert data['success'] is False
        
        # 4. 测试极大和极小的价格
        extreme_cases = [
            {'current_price': 0.01},     # 极小价格
            {'current_price': 999999.99} # 极大价格
        ]
        
        for case in extreme_cases:
            calc_data = {
                'stock_code': stock_code,
                'current_price': case['current_price']
            }
            
            response = client.post('/api/reviews/calculate-floating-profit',
                                 json=calc_data)
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            assert 'floating_profit_ratio' in data['data']
    
    def test_floating_profit_with_multiple_trades(self, client, db_session):
        """测试多笔交易的浮盈计算"""
        stock_code = '000001'
        
        # 1. 创建多笔买入交易
        trades_data = [
            {
                'stock_code': stock_code,
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 10.00,
                'quantity': 1000,
                'trade_date': (datetime.now() - timedelta(days=5)).isoformat(),
                'reason': '第一次买入'
            },
            {
                'stock_code': stock_code,
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.00,
                'quantity': 500,
                'trade_date': (datetime.now() - timedelta(days=3)).isoformat(),
                'reason': '第二次买入'
            }
        ]
        
        for trade_data in trades_data:
            response = client.post('/api/trades', json=trade_data)
            assert response.status_code == 201
        
        # 2. 计算浮盈（应该使用加权平均成本价）
        current_price = 11.00
        calc_data = {
            'stock_code': stock_code,
            'current_price': current_price
        }
        
        response = client.post('/api/reviews/calculate-floating-profit',
                             json=calc_data)
        assert response.status_code == 200
        data = response.json
        
        # 验证使用了加权平均成本价
        # 加权平均成本 = (10.00*1000 + 12.00*500) / (1000+500) = 16000/1500 = 10.67
        expected_avg_price = (10.00 * 1000 + 12.00 * 500) / (1000 + 500)
        expected_ratio = (current_price - expected_avg_price) / expected_avg_price
        
        calculated_ratio = float(data['data']['floating_profit_ratio'])
        assert abs(calculated_ratio - expected_ratio) < 0.001
    
    def test_floating_profit_with_sell_trades(self, client, db_session):
        """测试包含卖出交易的浮盈计算"""
        stock_code = '000001'
        
        # 1. 创建买入交易
        buy_data = {
            'stock_code': stock_code,
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 10.00,
            'quantity': 1000,
            'trade_date': (datetime.now() - timedelta(days=5)).isoformat(),
            'reason': '买入'
        }
        
        response = client.post('/api/trades', json=buy_data)
        assert response.status_code == 201
        
        # 2. 创建部分卖出交易
        sell_data = {
            'stock_code': stock_code,
            'stock_name': '平安银行',
            'trade_type': 'sell',
            'price': 12.00,
            'quantity': 300,
            'trade_date': (datetime.now() - timedelta(days=2)).isoformat(),
            'reason': '部分止盈'
        }
        
        response = client.post('/api/trades', json=sell_data)
        assert response.status_code == 201
        
        # 3. 计算剩余持仓的浮盈
        current_price = 11.00
        calc_data = {
            'stock_code': stock_code,
            'current_price': current_price
        }
        
        response = client.post('/api/reviews/calculate-floating-profit',
                             json=calc_data)
        assert response.status_code == 200
        data = response.json
        
        # 验证计算基于剩余持仓（700股）
        remaining_quantity = 1000 - 300
        expected_amount = (current_price - 10.00) * remaining_quantity
        calculated_amount = float(data['data']['floating_profit_amount'])
        
        assert abs(calculated_amount - expected_amount) < 0.01
    
    def test_floating_profit_precision_handling(self, client, db_session):
        """测试浮盈计算精度处理"""
        stock_code = '000001'
        
        # 创建交易记录
        trade_data = {
            'stock_code': stock_code,
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 3.333,  # 使用有精度要求的价格
            'quantity': 333,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试精度'
        }
        
        response = client.post('/api/trades', json=trade_data)
        assert response.status_code == 201
        
        # 测试精度计算
        current_price = 3.337  # 微小差异
        calc_data = {
            'stock_code': stock_code,
            'current_price': current_price
        }
        
        response = client.post('/api/reviews/calculate-floating-profit',
                             json=calc_data)
        assert response.status_code == 200
        data = response.json
        
        # 验证精度保持
        calculated_ratio = float(data['data']['floating_profit_ratio'])
        expected_ratio = (3.337 - 3.333) / 3.333
        
        assert abs(calculated_ratio - expected_ratio) < 0.000001
        
        # 验证格式化显示
        formatted_ratio = data['data']['formatted_ratio']
        assert '%' in formatted_ratio
        assert '+' in formatted_ratio or '-' in formatted_ratio


class TestErrorHandlingAndBoundaryConditions:
    """错误处理和边界情况测试"""
    
    def test_api_error_handling_consistency(self, client, db_session):
        """测试API错误处理一致性"""
        # 1. 测试无效的股票代码格式
        invalid_stock_codes = ['', '   ', '12345678', 'INVALID']
        
        for invalid_code in invalid_stock_codes:
            # 测试持仓天数API
            response = client.get(f'/api/holdings/{invalid_code}/days')
            assert response.status_code in [400, 404]
            
            # 测试浮盈计算API
            calc_data = {
                'stock_code': invalid_code,
                'current_price': 12.00
            }
            response = client.post('/api/reviews/calculate-floating-profit',
                                 json=calc_data)
            assert response.status_code in [400, 404]
        
        # 2. 测试无效的JSON数据
        invalid_json_cases = [
            '',           # 空字符串
            'invalid',    # 非JSON
            '{"invalid"}' # 无效JSON格式
        ]
        
        for invalid_json in invalid_json_cases:
            response = client.post('/api/reviews',
                                 data=invalid_json,
                                 content_type='application/json')
            assert response.status_code == 400
    
    def test_database_constraint_handling(self, client, db_session):
        """测试数据库约束处理"""
        stock_code = '000001'
        review_date = date.today().isoformat()
        
        # 1. 创建复盘记录
        review_data = {
            'stock_code': stock_code,
            'review_date': review_date,
            'price_up_score': 1
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        
        # 2. 尝试创建重复记录
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 400
        data = response.json
        assert data['success'] is False
        assert '已存在' in data['error']['message']
        
        # 3. 测试外键约束（如果适用）
        # 这里可以添加更多数据库约束测试
    
    def test_concurrent_operations_handling(self, client, db_session):
        """测试并发操作处理"""
        stock_code = '000001'
        
        # 1. 并发创建持仓天数记录
        create_data = {'holding_days': 5}
        
        responses = []
        for _ in range(3):
            response = client.post(f'/api/holdings/{stock_code}/days',
                                 json=create_data)
            responses.append(response)
        
        # 验证只有一个成功，其他返回错误
        success_count = sum(1 for r in responses if r.status_code == 201)
        error_count = sum(1 for r in responses if r.status_code == 400)
        
        assert success_count == 1
        assert error_count == 2
        
        # 2. 并发更新操作
        update_requests = [
            {'holding_days': 10},
            {'holding_days': 15},
            {'holding_days': 20}
        ]
        
        update_responses = []
        for update_data in update_requests:
            response = client.put(f'/api/holdings/{stock_code}/days',
                                json=update_data)
            update_responses.append(response)
        
        # 验证所有更新都成功
        for response in update_responses:
            assert response.status_code == 200
    
    def test_data_validation_boundary_values(self, client, db_session):
        """测试数据验证边界值"""
        stock_code = '000001'
        
        # 1. 测试持仓天数边界值
        boundary_cases = [
            {'holding_days': 1, 'should_succeed': True},      # 最小有效值
            {'holding_days': 0, 'should_succeed': False},     # 边界无效值
            {'holding_days': -1, 'should_succeed': False},    # 负数
            {'holding_days': 9999, 'should_succeed': True},   # 大数值
            {'holding_days': 10000, 'should_succeed': True}   # 更大数值
        ]
        
        for case in boundary_cases:
            response = client.post(f'/api/holdings/{stock_code}/days',
                                 json={'holding_days': case['holding_days']})
            
            if case['should_succeed']:
                assert response.status_code == 201
                # 清理数据
                client.delete(f'/api/holdings/{stock_code}/days')
            else:
                assert response.status_code == 400
        
        # 2. 测试价格边界值
        price_boundary_cases = [
            {'current_price': 0.01, 'should_succeed': True},     # 最小有效价格
            {'current_price': 0, 'should_succeed': False},       # 零价格
            {'current_price': -0.01, 'should_succeed': False},   # 负价格
            {'current_price': 999999.99, 'should_succeed': True} # 极大价格
        ]
        
        # 先创建交易记录用于浮盈计算
        trade_data = {
            'stock_code': stock_code,
            'stock_name': '测试股票',
            'trade_type': 'buy',
            'price': 10.00,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试'
        }
        client.post('/api/trades', json=trade_data)
        
        for case in price_boundary_cases:
            calc_data = {
                'stock_code': stock_code,
                'current_price': case['current_price']
            }
            
            response = client.post('/api/reviews/calculate-floating-profit',
                                 json=calc_data)
            
            if case['should_succeed']:
                assert response.status_code == 200
            else:
                assert response.status_code == 400


class TestDataConsistencyAndIntegrity:
    """数据一致性和完整性测试"""
    
    def test_cross_module_data_consistency(self, client, db_session):
        """测试跨模块数据一致性"""
        stock_code = '000001'
        
        # 1. 创建交易记录
        trade_data = {
            'stock_code': stock_code,
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试买入'
        }
        
        response = client.post('/api/trades', json=trade_data)
        assert response.status_code == 201
        
        # 2. 创建复盘记录
        review_data = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),
            'holding_days': 8,
            'current_price': 13.75,
            'floating_profit_ratio': 0.10,
            'price_up_score': 1,
            'bbi_score': 1
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        review_id = response.json['data']['id']
        
        # 3. 通过持仓天数API更新
        update_data = {'holding_days': 12}
        response = client.put(f'/api/holdings/{stock_code}/days',
                            json=update_data)
        assert response.status_code == 200
        
        # 4. 验证各模块数据一致性
        # 检查复盘记录
        response = client.get(f'/api/reviews/{review_id}')
        assert response.status_code == 200
        review = response.json['data']
        assert review['holding_days'] == 12
        
        # 检查持仓信息
        response = client.get(f'/api/holdings/{stock_code}')
        assert response.status_code == 200
        holding = response.json['data']
        assert holding['holding_days'] == 12
        
        # 检查持仓天数API
        response = client.get(f'/api/holdings/{stock_code}/days')
        assert response.status_code == 200
        days_info = response.json['data']
        assert days_info['holding_days'] == 12
    
    def test_transaction_rollback_integrity(self, client, db_session):
        """测试事务回滚完整性"""
        stock_code = '000001'
        
        # 1. 创建初始数据
        review_data = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),
            'holding_days': 5,
            'price_up_score': 1
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        review_id = response.json['data']['id']
        
        # 2. 尝试无效更新（应该触发回滚）
        invalid_update = {
            'holding_days': 'invalid_value',  # 无效数据
            'price_up_score': 2  # 无效评分
        }
        
        response = client.put(f'/api/reviews/{review_id}',
                            json=invalid_update)
        assert response.status_code == 400
        
        # 3. 验证原始数据未被破坏
        response = client.get(f'/api/reviews/{review_id}')
        assert response.status_code == 200
        data = response.json['data']
        
        assert data['holding_days'] == 5  # 原始值未变
        assert data['price_up_score'] == 1  # 原始值未变
    
    def test_data_integrity_after_operations(self, client, db_session):
        """测试操作后数据完整性"""
        stock_code = '000001'
        
        # 1. 执行一系列操作
        operations = [
            # 创建交易记录
            lambda: client.post('/api/trades', json={
                'stock_code': stock_code,
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 10.00,
                'quantity': 1000,
                'trade_date': datetime.now().isoformat(),
                'reason': '测试'
            }),
            
            # 创建复盘记录
            lambda: client.post('/api/reviews', json={
                'stock_code': stock_code,
                'review_date': date.today().isoformat(),
                'holding_days': 5,
                'current_price': 11.00,
                'floating_profit_ratio': 0.10,
                'price_up_score': 1
            }),
            
            # 更新持仓天数
            lambda: client.put(f'/api/holdings/{stock_code}/days',
                             json={'holding_days': 10}),
            
            # 计算浮盈
            lambda: client.post('/api/reviews/calculate-floating-profit',
                              json={
                                  'stock_code': stock_code,
                                  'current_price': 12.00
                              })
        ]
        
        # 执行所有操作
        results = []
        for operation in operations:
            result = operation()
            results.append(result)
            assert result.status_code in [200, 201]
        
        # 2. 验证最终数据完整性
        # 检查持仓信息
        response = client.get(f'/api/holdings/{stock_code}')
        assert response.status_code == 200
        holding = response.json['data']
        
        assert holding['stock_code'] == stock_code
        assert holding['current_quantity'] == 1000
        assert holding['holding_days'] == 10
        
        # 检查复盘记录
        response = client.get(f'/api/reviews/stock/{stock_code}/latest')
        assert response.status_code == 200
        review = response.json['data']
        
        assert review['stock_code'] == stock_code
        assert review['holding_days'] == 10
        assert 'current_price' in review
        assert 'floating_profit_ratio' in review
    
    def test_referential_integrity(self, client, db_session):
        """测试引用完整性"""
        stock_code = '000001'
        
        # 1. 创建相关数据
        trade_data = {
            'stock_code': stock_code,
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 10.00,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试'
        }
        
        response = client.post('/api/trades', json=trade_data)
        assert response.status_code == 201
        trade_id = response.json['data']['id']
        
        review_data = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),
            'holding_days': 5,
            'price_up_score': 1
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        review_id = response.json['data']['id']
        
        # 2. 验证引用关系
        # 通过股票代码查询应该能找到相关记录
        response = client.get(f'/api/holdings/{stock_code}')
        assert response.status_code == 200
        
        response = client.get(f'/api/reviews/stock/{stock_code}')
        assert response.status_code == 200
        reviews = response.json['data']
        assert len(reviews) == 1
        assert reviews[0]['id'] == review_id
        
        # 3. 测试删除操作的引用完整性
        # 删除复盘记录
        response = client.delete(f'/api/reviews/{review_id}')
        assert response.status_code == 200
        
        # 验证持仓信息仍然存在（基于交易记录）
        response = client.get(f'/api/holdings/{stock_code}')
        assert response.status_code == 200
        
        # 但复盘相关信息应该被清理
        response = client.get(f'/api/reviews/stock/{stock_code}')
        assert response.status_code == 200
        reviews = response.json['data']
        assert len(reviews) == 0