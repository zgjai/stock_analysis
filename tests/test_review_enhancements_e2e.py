"""
复盘功能增强端到端测试
模拟完整的用户交互流程，测试从前端到后端的完整功能
"""
import pytest
import json
import time
from datetime import datetime, date, timedelta
from decimal import Decimal
from models.trade_record import TradeRecord
from models.review_record import ReviewRecord
from services.review_service import ReviewService
from services.trading_service import TradingService


class TestReviewEnhancementsE2E:
    """复盘功能增强端到端测试"""
    
    def test_complete_review_workflow_e2e(self, client, db_session):
        """测试完整的复盘工作流程端到端"""
        stock_code = '000001'
        stock_name = '平安银行'
        
        # === 第一阶段：交易准备 ===
        
        # 1. 用户买入股票
        buy_trade_data = {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': (datetime.now() - timedelta(days=5)).isoformat(),
            'reason': '少妇B1战法',
            'notes': '技术形态良好，突破买入',
            'stop_loss_price': 11.25,
            'take_profit_ratio': 0.15,
            'sell_ratio': 0.5
        }
        
        response = client.post('/api/trades', json=buy_trade_data)
        assert response.status_code == 201
        trade_data = response.json['data']
        
        # 验证交易记录创建成功
        assert trade_data['stock_code'] == stock_code
        assert float(trade_data['price']) == 12.50
        assert trade_data['quantity'] == 1000
        
        # === 第二阶段：初始复盘 ===
        
        # 2. 用户进行第一次复盘（持仓第3天）
        initial_review_data = {
            'stock_code': stock_code,
            'review_date': (date.today() - timedelta(days=2)).isoformat(),
            'holding_days': 3,
            'current_price': 13.00,  # 上涨4%
            'floating_profit_ratio': 0.04,
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 0,
            'trend_score': 1,
            'j_score': 0,
            'analysis': '价格稳步上涨，技术指标良好',
            'decision': 'hold',
            'reason': '符合持有条件，继续观察'
        }
        
        response = client.post('/api/reviews', json=initial_review_data)
        assert response.status_code == 201
        initial_review = response.json['data']
        
        # 验证复盘记录创建成功
        assert initial_review['stock_code'] == stock_code
        assert initial_review['holding_days'] == 3
        assert float(initial_review['current_price']) == 13.00
        assert initial_review['total_score'] == 3
        assert initial_review['decision'] == 'hold'
        
        initial_review_id = initial_review['id']
        
        # === 第三阶段：持仓天数编辑 ===
        
        # 3. 用户发现持仓天数记录错误，需要修正为5天
        corrected_days = 5
        update_days_data = {'holding_days': corrected_days}
        
        response = client.put(f'/api/holdings/{stock_code}/days',
                            json=update_days_data)
        assert response.status_code == 200
        days_update_result = response.json
        
        # 验证持仓天数更新成功
        assert days_update_result['success'] is True
        assert days_update_result['data']['holding_days'] == corrected_days
        
        # 4. 验证复盘记录中的持仓天数也被同步更新
        response = client.get(f'/api/reviews/{initial_review_id}')
        assert response.status_code == 200
        updated_review = response.json['data']
        assert updated_review['holding_days'] == corrected_days
        
        # === 第四阶段：浮盈计算和更新 ===
        
        # 5. 股价继续上涨，用户输入新的当前价格进行浮盈计算
        new_current_price = 14.25
        calc_data = {
            'stock_code': stock_code,
            'current_price': new_current_price
        }
        
        response = client.post('/api/reviews/calculate-floating-profit',
                             json=calc_data)
        assert response.status_code == 200
        calc_result = response.json['data']
        
        # 验证浮盈计算结果
        expected_ratio = (new_current_price - 12.50) / 12.50  # 14%
        assert abs(float(calc_result['floating_profit_ratio']) - expected_ratio) < 0.001
        assert float(calc_result['buy_price']) == 12.50
        assert float(calc_result['current_price']) == new_current_price
        
        expected_amount = (new_current_price - 12.50) * 1000
        assert abs(float(calc_result['floating_profit_amount']) - expected_amount) < 0.01
        
        # 验证格式化显示
        formatted_ratio = calc_result['formatted_ratio']
        assert '+' in formatted_ratio  # 正收益
        assert '%' in formatted_ratio
        
        # === 第五阶段：复盘数据保存 ===
        
        # 6. 用户更新复盘记录，保存新的价格和分析
        updated_review_data = {
            'current_price': new_current_price,
            'floating_profit_ratio': expected_ratio,
            'volume_score': 1,  # 成交量指标改善
            'analysis': '价格突破前高，成交量放大，表现优异',
            'decision': 'sell_partial',  # 决策改为部分卖出
            'reason': '达到部分止盈条件'
        }
        
        response = client.put(f'/api/reviews/{initial_review_id}',
                            json=updated_review_data)
        assert response.status_code == 200
        final_review = response.json['data']
        
        # 验证复盘数据保存成功
        assert float(final_review['current_price']) == new_current_price
        assert abs(float(final_review['floating_profit_ratio']) - expected_ratio) < 0.001
        assert final_review['volume_score'] == 1
        assert final_review['total_score'] == 4  # 1+1+1+1+0
        assert final_review['decision'] == 'sell_partial'
        assert '表现优异' in final_review['analysis']
        
        # === 第六阶段：数据一致性验证 ===
        
        # 7. 验证所有相关API返回的数据一致性
        
        # 检查持仓信息
        response = client.get(f'/api/holdings/{stock_code}')
        assert response.status_code == 200
        holding_info = response.json['data']
        
        assert holding_info['stock_code'] == stock_code
        assert holding_info['stock_name'] == stock_name
        assert holding_info['current_quantity'] == 1000
        assert holding_info['holding_days'] == corrected_days
        assert holding_info['latest_review'] is not None
        
        # 检查持仓天数API
        response = client.get(f'/api/holdings/{stock_code}/days')
        assert response.status_code == 200
        days_info = response.json['data']
        assert days_info['holding_days'] == corrected_days
        
        # 检查股票的所有复盘记录
        response = client.get(f'/api/reviews/stock/{stock_code}')
        assert response.status_code == 200
        all_reviews = response.json['data']
        assert len(all_reviews) == 1
        assert all_reviews[0]['id'] == initial_review_id
        
        # 检查最新复盘记录
        response = client.get(f'/api/reviews/stock/{stock_code}/latest')
        assert response.status_code == 200
        latest_review = response.json['data']
        assert latest_review['id'] == initial_review_id
        assert latest_review['decision'] == 'sell_partial'
        
        # === 第七阶段：后续操作验证 ===
        
        # 8. 用户根据复盘决策执行部分卖出
        sell_trade_data = {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'trade_type': 'sell',
            'price': 14.25,
            'quantity': 500,  # 卖出50%
            'trade_date': datetime.now().isoformat(),
            'reason': '部分止盈',
            'notes': '根据复盘决策执行卖出'
        }
        
        response = client.post('/api/trades', json=sell_trade_data)
        assert response.status_code == 201
        sell_trade = response.json['data']
        
        # 验证卖出交易记录
        assert sell_trade['trade_type'] == 'sell'
        assert sell_trade['quantity'] == 500
        assert float(sell_trade['price']) == 14.25
        
        # 9. 验证持仓数量更新
        response = client.get(f'/api/holdings/{stock_code}')
        assert response.status_code == 200
        updated_holding = response.json['data']
        assert updated_holding['current_quantity'] == 500  # 剩余50%
        
        # 10. 进行卖出后的复盘
        post_sell_review_data = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),
            'holding_days': 6,  # 持仓天数增加
            'current_price': 14.50,  # 价格继续上涨
            'floating_profit_ratio': (14.50 - 12.50) / 12.50,  # 基于剩余持仓
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 1,
            'trend_score': 1,
            'j_score': 1,
            'analysis': '卖出后价格继续上涨，剩余持仓表现良好',
            'decision': 'hold',
            'reason': '继续持有剩余仓位'
        }
        
        response = client.post('/api/reviews', json=post_sell_review_data)
        assert response.status_code == 201
        post_sell_review = response.json['data']
        
        # 验证新复盘记录
        assert post_sell_review['holding_days'] == 6
        assert post_sell_review['total_score'] == 5  # 满分
        assert post_sell_review['decision'] == 'hold'
        
        # === 最终验证 ===
        
        # 11. 获取完整的交易和复盘历史
        response = client.get(f'/api/trades?stock_code={stock_code}')
        assert response.status_code == 200
        all_trades = response.json['data']['trades']
        assert len(all_trades) == 2  # 一买一卖
        
        response = client.get(f'/api/reviews/stock/{stock_code}')
        assert response.status_code == 200
        all_reviews = response.json['data']
        assert len(all_reviews) == 2  # 两次复盘
        
        # 验证数据完整性和一致性
        buy_trade = next(t for t in all_trades if t['trade_type'] == 'buy')
        sell_trade = next(t for t in all_trades if t['trade_type'] == 'sell')
        
        assert buy_trade['quantity'] == 1000
        assert sell_trade['quantity'] == 500
        
        # 验证复盘记录的时间顺序
        reviews_by_date = sorted(all_reviews, key=lambda x: x['review_date'])
        assert len(reviews_by_date) == 2
        assert reviews_by_date[0]['holding_days'] == 5  # 修正后的天数
        assert reviews_by_date[1]['holding_days'] == 6
    
    def test_error_recovery_workflow_e2e(self, client, db_session):
        """测试错误恢复工作流程端到端"""
        stock_code = '000002'
        
        # === 场景：用户操作中遇到各种错误并恢复 ===
        
        # 1. 用户尝试为不存在的股票创建复盘记录
        invalid_review_data = {
            'stock_code': 'NONEXISTENT',
            'review_date': date.today().isoformat(),
            'price_up_score': 1
        }
        
        response = client.post('/api/reviews', json=invalid_review_data)
        # 这应该成功，因为复盘记录不依赖交易记录存在
        assert response.status_code == 201
        
        # 2. 用户尝试计算不存在交易记录的浮盈
        calc_data = {
            'stock_code': 'NONEXISTENT',
            'current_price': 12.00
        }
        
        response = client.post('/api/reviews/calculate-floating-profit',
                             json=calc_data)
        assert response.status_code == 404
        error_data = response.json
        assert error_data['success'] is False
        assert '未找到' in error_data['error']['message']
        
        # 3. 用户创建正确的交易记录
        trade_data = {
            'stock_code': stock_code,
            'stock_name': '万科A',
            'trade_type': 'buy',
            'price': 8.00,
            'quantity': 2000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试买入'
        }
        
        response = client.post('/api/trades', json=trade_data)
        assert response.status_code == 201
        
        # 4. 用户尝试输入无效的持仓天数
        invalid_days_data = {'holding_days': -5}
        
        response = client.post(f'/api/holdings/{stock_code}/days',
                             json=invalid_days_data)
        assert response.status_code == 400
        error_data = response.json
        assert error_data['success'] is False
        assert '正整数' in error_data['error']['message']
        
        # 5. 用户输入正确的持仓天数
        valid_days_data = {'holding_days': 3}
        
        response = client.post(f'/api/holdings/{stock_code}/days',
                             json=valid_days_data)
        assert response.status_code == 201
        
        # 6. 用户尝试输入无效的当前价格进行浮盈计算
        invalid_calc_data = {
            'stock_code': stock_code,
            'current_price': -5.00  # 负价格
        }
        
        response = client.post('/api/reviews/calculate-floating-profit',
                             json=invalid_calc_data)
        assert response.status_code == 400
        
        # 7. 用户输入正确的价格进行浮盈计算
        valid_calc_data = {
            'stock_code': stock_code,
            'current_price': 8.80
        }
        
        response = client.post('/api/reviews/calculate-floating-profit',
                             json=valid_calc_data)
        assert response.status_code == 200
        calc_result = response.json['data']
        
        expected_ratio = (8.80 - 8.00) / 8.00  # 10%
        assert abs(float(calc_result['floating_profit_ratio']) - expected_ratio) < 0.001
        
        # 8. 用户创建复盘记录时输入无效评分
        invalid_review_data = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),
            'holding_days': 3,
            'current_price': 8.80,
            'floating_profit_ratio': expected_ratio,
            'price_up_score': 2,  # 无效评分
            'bbi_score': 1
        }
        
        response = client.post('/api/reviews', json=invalid_review_data)
        assert response.status_code == 400
        
        # 9. 用户输入正确的复盘数据
        valid_review_data = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),
            'holding_days': 3,
            'current_price': 8.80,
            'floating_profit_ratio': expected_ratio,
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 0,
            'trend_score': 1,
            'j_score': 0,
            'analysis': '恢复后的正确复盘',
            'decision': 'hold'
        }
        
        response = client.post('/api/reviews', json=valid_review_data)
        assert response.status_code == 201
        review_data = response.json['data']
        
        # 验证最终数据正确性
        assert review_data['stock_code'] == stock_code
        assert review_data['holding_days'] == 3
        assert float(review_data['current_price']) == 8.80
        assert review_data['total_score'] == 3
        assert review_data['analysis'] == '恢复后的正确复盘'
        
        # 10. 验证所有数据的一致性
        response = client.get(f'/api/holdings/{stock_code}')
        assert response.status_code == 200
        holding = response.json['data']
        
        assert holding['holding_days'] == 3
        assert holding['latest_review'] is not None
        assert holding['latest_review']['decision'] == 'hold'
    
    def test_concurrent_user_operations_e2e(self, client, db_session):
        """测试并发用户操作端到端"""
        stock_code = '000003'
        
        # === 场景：模拟多个用户同时操作同一股票 ===
        
        # 1. 创建基础交易记录
        trade_data = {
            'stock_code': stock_code,
            'stock_name': '招商银行',
            'trade_type': 'buy',
            'price': 20.00,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试买入'
        }
        
        response = client.post('/api/trades', json=trade_data)
        assert response.status_code == 201
        
        # 2. 模拟用户A创建持仓天数记录
        user_a_days_data = {'holding_days': 5}
        
        response_a = client.post(f'/api/holdings/{stock_code}/days',
                               json=user_a_days_data)
        assert response_a.status_code == 201
        
        # 3. 模拟用户B尝试创建相同的持仓天数记录（应该失败）
        user_b_days_data = {'holding_days': 7}
        
        response_b = client.post(f'/api/holdings/{stock_code}/days',
                               json=user_b_days_data)
        assert response_b.status_code == 400  # 已存在
        
        # 4. 模拟用户A和用户B同时进行浮盈计算
        calc_data_a = {
            'stock_code': stock_code,
            'current_price': 21.00
        }
        
        calc_data_b = {
            'stock_code': stock_code,
            'current_price': 22.00
        }
        
        response_a = client.post('/api/reviews/calculate-floating-profit',
                               json=calc_data_a)
        response_b = client.post('/api/reviews/calculate-floating-profit',
                               json=calc_data_b)
        
        # 两个计算都应该成功
        assert response_a.status_code == 200
        assert response_b.status_code == 200
        
        calc_result_a = response_a.json['data']
        calc_result_b = response_b.json['data']
        
        # 验证计算结果不同
        assert float(calc_result_a['current_price']) == 21.00
        assert float(calc_result_b['current_price']) == 22.00
        assert calc_result_a['floating_profit_ratio'] != calc_result_b['floating_profit_ratio']
        
        # 5. 模拟用户A创建复盘记录
        review_data_a = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),
            'holding_days': 5,
            'current_price': 21.00,
            'floating_profit_ratio': float(calc_result_a['floating_profit_ratio']),
            'price_up_score': 1,
            'bbi_score': 1,
            'analysis': '用户A的复盘',
            'decision': 'hold'
        }
        
        response_a = client.post('/api/reviews', json=review_data_a)
        assert response_a.status_code == 201
        review_a_id = response_a.json['data']['id']
        
        # 6. 模拟用户B尝试创建相同日期的复盘记录（应该失败）
        review_data_b = {
            'stock_code': stock_code,
            'review_date': date.today().isoformat(),  # 相同日期
            'holding_days': 7,
            'current_price': 22.00,
            'price_up_score': 1,
            'analysis': '用户B的复盘',
            'decision': 'sell_partial'
        }
        
        response_b = client.post('/api/reviews', json=review_data_b)
        assert response_b.status_code == 400  # 重复记录
        
        # 7. 模拟用户A和用户B同时更新持仓天数
        update_data_a = {'holding_days': 8}
        update_data_b = {'holding_days': 10}
        
        response_a = client.put(f'/api/holdings/{stock_code}/days',
                              json=update_data_a)
        response_b = client.put(f'/api/holdings/{stock_code}/days',
                              json=update_data_b)
        
        # 两个更新都应该成功（后者覆盖前者）
        assert response_a.status_code == 200
        assert response_b.status_code == 200
        
        # 8. 验证最终状态
        response = client.get(f'/api/holdings/{stock_code}/days')
        assert response.status_code == 200
        final_days = response.json['data']['holding_days']
        assert final_days in [8, 10]  # 应该是其中一个值
        
        # 9. 验证复盘记录中的持仓天数也被更新
        response = client.get(f'/api/reviews/{review_a_id}')
        assert response.status_code == 200
        updated_review = response.json['data']
        assert updated_review['holding_days'] == final_days
        
        # 10. 验证数据一致性
        response = client.get(f'/api/holdings/{stock_code}')
        assert response.status_code == 200
        holding = response.json['data']
        assert holding['holding_days'] == final_days
    
    def test_performance_under_load_e2e(self, client, db_session):
        """测试负载下的性能端到端"""
        # === 场景：测试系统在大量数据下的性能 ===
        
        # 1. 创建多只股票的交易记录
        stock_codes = [f'00000{i}' for i in range(1, 11)]  # 10只股票
        
        for i, stock_code in enumerate(stock_codes):
            trade_data = {
                'stock_code': stock_code,
                'stock_name': f'测试股票{i+1}',
                'trade_type': 'buy',
                'price': 10.00 + i,
                'quantity': 1000,
                'trade_date': (datetime.now() - timedelta(days=i)).isoformat(),
                'reason': f'测试买入{i+1}'
            }
            
            response = client.post('/api/trades', json=trade_data)
            assert response.status_code == 201
        
        # 2. 为每只股票创建持仓天数记录
        start_time = time.time()
        
        for i, stock_code in enumerate(stock_codes):
            days_data = {'holding_days': i + 1}
            response = client.post(f'/api/holdings/{stock_code}/days',
                                 json=days_data)
            assert response.status_code == 201
        
        days_creation_time = time.time() - start_time
        assert days_creation_time < 5.0  # 应该在5秒内完成
        
        # 3. 批量进行浮盈计算
        start_time = time.time()
        
        calc_results = []
        for i, stock_code in enumerate(stock_codes):
            calc_data = {
                'stock_code': stock_code,
                'current_price': 12.00 + i * 0.5
            }
            
            response = client.post('/api/reviews/calculate-floating-profit',
                                 json=calc_data)
            assert response.status_code == 200
            calc_results.append(response.json['data'])
        
        calc_time = time.time() - start_time
        assert calc_time < 3.0  # 应该在3秒内完成
        
        # 4. 批量创建复盘记录
        start_time = time.time()
        
        review_ids = []
        for i, (stock_code, calc_result) in enumerate(zip(stock_codes, calc_results)):
            review_data = {
                'stock_code': stock_code,
                'review_date': (date.today() - timedelta(days=i)).isoformat(),
                'holding_days': i + 1,
                'current_price': float(calc_result['current_price']),
                'floating_profit_ratio': float(calc_result['floating_profit_ratio']),
                'price_up_score': 1,
                'bbi_score': i % 2,  # 交替0和1
                'volume_score': (i + 1) % 2,
                'trend_score': 1,
                'j_score': i % 2,
                'analysis': f'股票{i+1}的复盘分析',
                'decision': 'hold' if i % 2 == 0 else 'sell_partial'
            }
            
            response = client.post('/api/reviews', json=review_data)
            assert response.status_code == 201
            review_ids.append(response.json['data']['id'])
        
        review_creation_time = time.time() - start_time
        assert review_creation_time < 5.0  # 应该在5秒内完成
        
        # 5. 批量查询持仓信息
        start_time = time.time()
        
        for stock_code in stock_codes:
            response = client.get(f'/api/holdings/{stock_code}')
            assert response.status_code == 200
            holding = response.json['data']
            assert holding['stock_code'] == stock_code
        
        query_time = time.time() - start_time
        assert query_time < 2.0  # 应该在2秒内完成
        
        # 6. 批量更新持仓天数
        start_time = time.time()
        
        for i, stock_code in enumerate(stock_codes):
            update_data = {'holding_days': (i + 1) * 2}  # 翻倍
            response = client.put(f'/api/holdings/{stock_code}/days',
                                json=update_data)
            assert response.status_code == 200
        
        update_time = time.time() - start_time
        assert update_time < 3.0  # 应该在3秒内完成
        
        # 7. 验证批量操作的数据一致性
        for i, stock_code in enumerate(stock_codes):
            # 检查持仓天数
            response = client.get(f'/api/holdings/{stock_code}/days')
            assert response.status_code == 200
            days_info = response.json['data']
            assert days_info['holding_days'] == (i + 1) * 2
            
            # 检查复盘记录
            response = client.get(f'/api/reviews/{review_ids[i]}')
            assert response.status_code == 200
            review = response.json['data']
            assert review['holding_days'] == (i + 1) * 2  # 应该被同步更新
        
        # 8. 测试批量查询性能
        start_time = time.time()
        
        # 获取所有持仓
        response = client.get('/api/holdings')
        assert response.status_code == 200
        all_holdings = response.json['data']
        assert len(all_holdings) == len(stock_codes)
        
        # 获取所有复盘记录
        response = client.get('/api/reviews')
        assert response.status_code == 200
        all_reviews = response.json['data']['reviews']
        assert len(all_reviews) == len(stock_codes)
        
        batch_query_time = time.time() - start_time
        assert batch_query_time < 2.0  # 应该在2秒内完成
        
        # 9. 验证数据完整性
        for i, stock_code in enumerate(stock_codes):
            holding = next(h for h in all_holdings if h['stock_code'] == stock_code)
            review = next(r for r in all_reviews if r['stock_code'] == stock_code)
            
            assert holding['holding_days'] == (i + 1) * 2
            assert review['holding_days'] == (i + 1) * 2
            assert holding['latest_review']['id'] == review['id']