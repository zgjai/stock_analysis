"""
API集成测试 - 覆盖所有业务场景
测试所有API端点的集成功能，包括边界条件和异常情况
"""
import pytest
from datetime import datetime, date, timedelta
from extensions import db
import json


class TestComprehensiveAPIIntegration:
    """全面的API集成测试"""
    
    def test_trading_api_comprehensive(self, client, db_session):
        """交易API全面测试"""
        
        # 1. 测试创建买入记录
        buy_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '少妇B1战法',
            'notes': '测试买入',
            'stop_loss_price': 11.25,
            'take_profit_ratio': 0.15,
            'sell_ratio': 0.5
        }
        
        response = client.post('/api/trades', json=buy_data)
        assert response.status_code == 201
        buy_id = response.json['data']['id']
        
        # 验证计算字段
        trade = response.json['data']
        assert trade['expected_loss_ratio'] == 0.1
        assert abs(trade['expected_profit_ratio'] - 0.075) < 0.001
        
        # 2. 测试创建卖出记录
        sell_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'sell',
            'price': 14.00,
            'quantity': 500,
            'trade_date': datetime.now().isoformat(),
            'reason': '部分止盈',
            'notes': '测试卖出'
        }
        
        response = client.post('/api/trades', json=sell_data)
        assert response.status_code == 201
        sell_id = response.json['data']['id']
        
        # 3. 测试获取交易记录列表
        response = client.get('/api/trades')
        assert response.status_code == 200
        trades = response.json['data']
        assert len(trades) == 2
        
        # 4. 测试按股票代码筛选
        response = client.get('/api/trades?stock_code=000001')
        assert response.status_code == 200
        trades = response.json['data']
        assert len(trades) == 2
        assert all(t['stock_code'] == '000001' for t in trades)
        
        # 5. 测试按交易类型筛选
        response = client.get('/api/trades?trade_type=buy')
        assert response.status_code == 200
        trades = response.json['data']
        assert len(trades) == 1
        assert trades[0]['trade_type'] == 'buy'
        
        # 6. 测试日期范围筛选
        start_date = (datetime.now() - timedelta(days=1)).date().isoformat()
        end_date = (datetime.now() + timedelta(days=1)).date().isoformat()
        response = client.get(f'/api/trades?start_date={start_date}&end_date={end_date}')
        assert response.status_code == 200
        trades = response.json['data']
        assert len(trades) == 2
        
        # 7. 测试更新交易记录
        update_data = {
            'notes': '更新后的备注',
            'reason': '更新后的原因'
        }
        
        response = client.put(f'/api/trades/{buy_id}', json=update_data)
        assert response.status_code == 200
        assert response.json['data']['notes'] == '更新后的备注'
        
        # 8. 测试删除交易记录
        response = client.delete(f'/api/trades/{sell_id}')
        assert response.status_code == 200
        
        # 验证删除
        response = client.get(f'/api/trades/{sell_id}')
        assert response.status_code == 404
        
        # 9. 测试订正功能
        correction_data = {
            'price': 12.80,
            'quantity': 1200,
            'correction_reason': '价格记录错误'
        }
        
        response = client.post(f'/api/trades/{buy_id}/correct', json=correction_data)
        assert response.status_code == 201
        corrected_id = response.json['data']['id']
        
        # 验证原记录被标记
        response = client.get(f'/api/trades/{buy_id}')
        assert response.status_code == 200
        assert response.json['data']['is_corrected'] == True
        
        # 10. 测试获取订正历史
        response = client.get(f'/api/trades/{buy_id}/history')
        assert response.status_code == 200
        history = response.json['data']
        assert len(history) == 1
        
    def test_trading_api_validation_errors(self, client, db_session):
        """测试交易API验证错误"""
        
        # 1. 测试缺少必填字段
        invalid_data = {
            'stock_code': '000001',
            # 缺少stock_name
            'trade_type': 'buy',
            'price': 12.50
        }
        
        response = client.post('/api/trades', json=invalid_data)
        assert response.status_code == 400
        assert 'error' in response.json
        
        # 2. 测试无效的交易类型
        invalid_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'invalid_type',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试'
        }
        
        response = client.post('/api/trades', json=invalid_data)
        assert response.status_code == 400
        
        # 3. 测试负数价格
        invalid_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': -12.50,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试'
        }
        
        response = client.post('/api/trades', json=invalid_data)
        assert response.status_code == 400
        
        # 4. 测试无效的股票代码格式
        invalid_data = {
            'stock_code': 'INVALID',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '测试'
        }
        
        response = client.post('/api/trades', json=invalid_data)
        assert response.status_code == 400
        
    def test_review_api_comprehensive(self, client, db_session):
        """复盘API全面测试"""
        
        # 1. 创建复盘记录
        review_data = {
            'stock_code': '000001',
            'review_date': date.today().isoformat(),
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 0,
            'trend_score': 1,
            'j_score': 1,
            'analysis': '整体表现良好',
            'decision': 'hold',
            'reason': '继续观察',
            'holding_days': 5
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        review_id = response.json['data']['id']
        assert response.json['data']['total_score'] == 4
        
        # 2. 测试重复日期创建（应该失败）
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 400
        
        # 3. 测试获取复盘记录
        response = client.get('/api/reviews')
        assert response.status_code == 200
        reviews = response.json['data']
        assert len(reviews) == 1
        
        # 4. 测试按股票代码筛选
        response = client.get('/api/reviews?stock_code=000001')
        assert response.status_code == 200
        reviews = response.json['data']
        assert len(reviews) == 1
        
        # 5. 测试按日期范围筛选
        start_date = (date.today() - timedelta(days=1)).isoformat()
        end_date = (date.today() + timedelta(days=1)).isoformat()
        response = client.get(f'/api/reviews?start_date={start_date}&end_date={end_date}')
        assert response.status_code == 200
        reviews = response.json['data']
        assert len(reviews) == 1
        
        # 6. 测试更新复盘记录
        update_data = {
            'analysis': '更新后的分析',
            'decision': 'sell_partial',
            'holding_days': 6
        }
        
        response = client.put(f'/api/reviews/{review_id}', json=update_data)
        assert response.status_code == 200
        assert response.json['data']['analysis'] == '更新后的分析'
        assert response.json['data']['decision'] == 'sell_partial'
        
        # 7. 测试删除复盘记录
        response = client.delete(f'/api/reviews/{review_id}')
        assert response.status_code == 200
        
    def test_holdings_api_comprehensive(self, client, db_session):
        """持仓API全面测试"""
        
        # 1. 创建买入记录
        buy_trades = [
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 10.00,
                'quantity': 1000,
                'trade_date': (datetime.now() - timedelta(days=5)).isoformat(),
                'reason': '测试买入1'
            },
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.00,
                'quantity': 500,
                'trade_date': (datetime.now() - timedelta(days=3)).isoformat(),
                'reason': '测试买入2'
            },
            {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'buy',
                'price': 15.00,
                'quantity': 800,
                'trade_date': (datetime.now() - timedelta(days=2)).isoformat(),
                'reason': '测试买入3'
            }
        ]
        
        for trade_data in buy_trades:
            response = client.post('/api/trades', json=trade_data)
            assert response.status_code == 201
        
        # 2. 创建部分卖出记录
        sell_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'sell',
            'price': 13.00,
            'quantity': 300,
            'trade_date': (datetime.now() - timedelta(days=1)).isoformat(),
            'reason': '部分止盈'
        }
        
        response = client.post('/api/trades', json=sell_data)
        assert response.status_code == 201
        
        # 3. 获取持仓列表
        response = client.get('/api/holdings')
        assert response.status_code == 200
        holdings = response.json['data']
        
        # 验证持仓计算
        assert len(holdings) == 2  # 两只股票
        
        # 验证000001的持仓
        holding_001 = next(h for h in holdings if h['stock_code'] == '000001')
        assert holding_001['quantity'] == 1200  # 1000+500-300
        assert abs(holding_001['avg_cost'] - 10.67) < 0.01  # (10*1000+12*500)/1500
        
        # 验证000002的持仓
        holding_002 = next(h for h in holdings if h['stock_code'] == '000002')
        assert holding_002['quantity'] == 800
        assert holding_002['avg_cost'] == 15.00
        
        # 4. 添加当前价格
        prices = [
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'current_price': 14.00,
                'change_percent': 12.0,
                'record_date': date.today().isoformat()
            },
            {
                'stock_code': '000002',
                'stock_name': '万科A',
                'current_price': 16.50,
                'change_percent': 10.0,
                'record_date': date.today().isoformat()
            }
        ]
        
        for price_data in prices:
            response = client.post('/api/prices', json=price_data)
            assert response.status_code == 201
        
        # 5. 重新获取持仓（包含盈亏信息）
        response = client.get('/api/holdings')
        assert response.status_code == 200
        holdings = response.json['data']
        
        # 验证盈亏计算
        holding_001 = next(h for h in holdings if h['stock_code'] == '000001')
        assert holding_001['current_price'] == 14.00
        assert holding_001['unrealized_profit'] > 0
        
        holding_002 = next(h for h in holdings if h['stock_code'] == '000002')
        assert holding_002['current_price'] == 16.50
        assert holding_002['unrealized_profit'] > 0
        
    def test_stock_pool_api_comprehensive(self, client, db_session):
        """股票池API全面测试"""
        
        # 1. 添加股票到观察池
        watch_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'target_price': 12.00,
            'add_reason': '技术形态良好',
            'status': 'active'
        }
        
        response = client.post('/api/stock-pool', json=watch_data)
        assert response.status_code == 201
        watch_id = response.json['data']['id']
        
        # 2. 添加股票到待买入池
        buy_ready_data = {
            'stock_code': '000002',
            'stock_name': '万科A',
            'pool_type': 'buy_ready',
            'target_price': 15.50,
            'add_reason': '突破关键阻力',
            'status': 'active'
        }
        
        response = client.post('/api/stock-pool', json=buy_ready_data)
        assert response.status_code == 201
        buy_ready_id = response.json['data']['id']
        
        # 3. 获取股票池列表
        response = client.get('/api/stock-pool')
        assert response.status_code == 200
        pools = response.json['data']
        assert len(pools) == 2
        
        # 4. 按池类型筛选
        response = client.get('/api/stock-pool?pool_type=watch')
        assert response.status_code == 200
        pools = response.json['data']
        assert len(pools) == 1
        assert pools[0]['pool_type'] == 'watch'
        
        # 5. 按状态筛选
        response = client.get('/api/stock-pool?status=active')
        assert response.status_code == 200
        pools = response.json['data']
        assert len(pools) == 2
        
        # 6. 更新股票池状态（从观察池移至待买入池）
        update_data = {
            'pool_type': 'buy_ready',
            'target_price': 12.50,
            'add_reason': '突破确认'
        }
        
        response = client.put(f'/api/stock-pool/{watch_id}', json=update_data)
        assert response.status_code == 200
        assert response.json['data']['pool_type'] == 'buy_ready'
        
        # 7. 移除股票（标记为已移除）
        response = client.delete(f'/api/stock-pool/{buy_ready_id}')
        assert response.status_code == 200
        
        # 验证状态更新
        response = client.get(f'/api/stock-pool/{buy_ready_id}')
        assert response.status_code == 200
        assert response.json['data']['status'] == 'removed'
        
    def test_case_study_api_comprehensive(self, client, db_session):
        """案例研究API全面测试"""
        
        # 1. 创建案例
        case_data = {
            'stock_code': '000001',
            'title': '平安银行突破案例',
            'image_path': '/uploads/case_001.png',
            'tags': ['突破', '银行股', 'B1战法'],
            'notes': '经典的B1战法突破案例'
        }
        
        response = client.post('/api/cases', json=case_data)
        assert response.status_code == 201
        case_id = response.json['data']['id']
        
        # 2. 创建更多案例用于测试搜索
        more_cases = [
            {
                'stock_code': '000002',
                'title': '万科A回调案例',
                'image_path': '/uploads/case_002.png',
                'tags': ['回调', '地产股'],
                'notes': '回调买入案例'
            },
            {
                'stock_code': '000003',
                'title': '招商银行突破案例',
                'image_path': '/uploads/case_003.png',
                'tags': ['突破', '银行股', 'B2战法'],
                'notes': 'B2战法突破案例'
            }
        ]
        
        for case in more_cases:
            response = client.post('/api/cases', json=case)
            assert response.status_code == 201
        
        # 3. 获取所有案例
        response = client.get('/api/cases')
        assert response.status_code == 200
        cases = response.json['data']
        assert len(cases) == 3
        
        # 4. 按标题搜索
        response = client.get('/api/cases?search=突破')
        assert response.status_code == 200
        cases = response.json['data']
        assert len(cases) == 2
        assert all('突破' in case['title'] for case in cases)
        
        # 5. 按标签筛选
        response = client.get('/api/cases?tags=银行股')
        assert response.status_code == 200
        cases = response.json['data']
        assert len(cases) == 2
        assert all('银行股' in case['tags'] for case in cases)
        
        # 6. 按股票代码筛选
        response = client.get('/api/cases?stock_code=000001')
        assert response.status_code == 200
        cases = response.json['data']
        assert len(cases) == 1
        assert cases[0]['stock_code'] == '000001'
        
        # 7. 更新案例
        update_data = {
            'notes': '更新后的案例说明',
            'tags': ['突破', '银行股', 'B1战法', '成功案例']
        }
        
        response = client.put(f'/api/cases/{case_id}', json=update_data)
        assert response.status_code == 200
        assert '成功案例' in response.json['data']['tags']
        
        # 8. 删除案例
        response = client.delete(f'/api/cases/{case_id}')
        assert response.status_code == 200
        
        # 验证删除
        response = client.get(f'/api/cases/{case_id}')
        assert response.status_code == 404
        
    def test_analytics_api_comprehensive(self, client, db_session):
        """统计分析API全面测试"""
        
        # 1. 创建测试数据
        self._create_analytics_test_data(client)
        
        # 2. 测试总体统计
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        overview = response.json['data']
        
        # 验证统计字段
        required_fields = [
            'total_trades', 'realized_profit', 'unrealized_profit',
            'total_profit', 'success_rate', 'total_investment'
        ]
        for field in required_fields:
            assert field in overview
        
        # 3. 测试收益分布
        response = client.get('/api/analytics/profit-distribution')
        assert response.status_code == 200
        distribution = response.json['data']
        assert len(distribution) > 0
        
        # 验证分布数据结构
        for item in distribution:
            assert 'range' in item
            assert 'count' in item
            assert 'percentage' in item
        
        # 4. 测试月度统计
        response = client.get('/api/analytics/monthly')
        assert response.status_code == 200
        monthly = response.json['data']
        assert len(monthly) > 0
        
        # 验证月度数据结构
        for item in monthly:
            assert 'month' in item
            assert 'trade_count' in item
            assert 'profit' in item
            assert 'success_rate' in item
        
        # 5. 测试按年份筛选月度统计
        current_year = date.today().year
        response = client.get(f'/api/analytics/monthly?year={current_year}')
        assert response.status_code == 200
        monthly = response.json['data']
        assert all(item['month'].startswith(str(current_year)) for item in monthly)
        
        # 6. 测试导出功能
        response = client.get('/api/analytics/export')
        assert response.status_code == 200
        export_data = response.json['data']
        
        # 验证导出数据包含所有必要信息
        assert 'overview' in export_data
        assert 'monthly_stats' in export_data
        assert 'profit_distribution' in export_data
        assert 'trade_summary' in export_data
        
    def test_price_service_api_comprehensive(self, client, db_session):
        """价格服务API全面测试"""
        
        # 1. 添加价格数据
        price_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'current_price': 12.50,
            'change_percent': 2.40,
            'record_date': date.today().isoformat()
        }
        
        response = client.post('/api/prices', json=price_data)
        assert response.status_code == 201
        
        # 2. 测试重复日期添加（应该更新而不是创建新记录）
        updated_price_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'current_price': 12.80,
            'change_percent': 2.80,
            'record_date': date.today().isoformat()
        }
        
        response = client.post('/api/prices', json=updated_price_data)
        assert response.status_code == 201
        
        # 3. 获取特定股票价格
        response = client.get('/api/prices/000001')
        assert response.status_code == 200
        price = response.json['data']
        assert price['current_price'] == 12.80  # 应该是更新后的价格
        
        # 4. 获取价格历史
        response = client.get('/api/prices/000001/history')
        assert response.status_code == 200
        history = response.json['data']
        assert len(history) >= 1
        
        # 5. 批量获取价格
        response = client.get('/api/prices?stock_codes=000001,000002')
        assert response.status_code == 200
        prices = response.json['data']
        assert len(prices) >= 1
        
        # 6. 测试手动刷新价格（模拟）
        response = client.post('/api/prices/refresh', json={'stock_codes': ['000001']})
        assert response.status_code == 200
        
    def test_sector_analysis_api_comprehensive(self, client, db_session):
        """板块分析API全面测试"""
        
        # 1. 添加板块数据
        sectors_data = [
            {
                'sector_name': '银行',
                'sector_code': 'BK0475',
                'change_percent': 2.15,
                'record_date': date.today().isoformat(),
                'rank_position': 1,
                'volume': 1500000000,
                'market_cap': 850000000000.0
            },
            {
                'sector_name': '地产',
                'sector_code': 'BK0451',
                'change_percent': 1.85,
                'record_date': date.today().isoformat(),
                'rank_position': 2,
                'volume': 1200000000,
                'market_cap': 650000000000.0
            },
            {
                'sector_name': '科技',
                'sector_code': 'BK0737',
                'change_percent': 1.45,
                'record_date': date.today().isoformat(),
                'rank_position': 3,
                'volume': 2000000000,
                'market_cap': 1200000000000.0
            }
        ]
        
        for sector_data in sectors_data:
            response = client.post('/api/sectors', json=sector_data)
            assert response.status_code == 201
        
        # 2. 获取当日板块排名
        response = client.get('/api/sectors/ranking')
        assert response.status_code == 200
        ranking = response.json['data']
        assert len(ranking) == 3
        assert ranking[0]['sector_name'] == '银行'  # 排名第一
        
        # 3. 按日期获取排名
        today = date.today().isoformat()
        response = client.get(f'/api/sectors/ranking?date={today}')
        assert response.status_code == 200
        ranking = response.json['data']
        assert len(ranking) == 3
        
        # 4. 获取历史表现
        start_date = (date.today() - timedelta(days=7)).isoformat()
        end_date = date.today().isoformat()
        response = client.get(f'/api/sectors/history?start_date={start_date}&end_date={end_date}')
        assert response.status_code == 200
        history = response.json['data']
        assert len(history) >= 3
        
        # 5. 添加历史数据用于TOPK测试
        for days_ago in range(1, 6):
            test_date = date.today() - timedelta(days=days_ago)
            for i, sector in enumerate(['银行', '地产', '科技', '医药', '消费']):
                sector_data = {
                    'sector_name': sector,
                    'sector_code': f'BK{1000+i}',
                    'change_percent': (5-i) * 0.5 + days_ago * 0.1,
                    'record_date': test_date.isoformat(),
                    'rank_position': i + 1,
                    'volume': 1000000000 * (i + 1),
                    'market_cap': 500000000000.0 * (i + 1)
                }
                
                response = client.post('/api/sectors', json=sector_data)
                # 可能会有重复数据，忽略409错误
                assert response.status_code in [201, 409]
        
        # 6. 获取TOPK统计
        response = client.get('/api/sectors/top-performers?days=5&top_k=3')
        assert response.status_code == 200
        top_performers = response.json['data']
        assert len(top_performers) > 0
        
        # 验证TOPK数据结构
        for performer in top_performers:
            assert 'sector_name' in performer
            assert 'appearances' in performer
            assert 'avg_rank' in performer
            assert 'best_rank' in performer
        
        # 7. 测试手动刷新板块数据
        response = client.post('/api/sectors/refresh')
        assert response.status_code == 200
        
    def test_strategy_api_comprehensive(self, client, db_session):
        """策略API全面测试"""
        
        # 1. 创建策略
        strategy_data = {
            'strategy_name': '测试策略',
            'is_active': True,
            'rules': {
                'rules': [
                    {
                        'day_range': [1, 5],
                        'loss_threshold': -0.05,
                        'action': 'sell_all',
                        'condition': 'loss_exceed'
                    },
                    {
                        'day_range': [6, 10],
                        'profit_threshold': 0.10,
                        'action': 'sell_partial',
                        'sell_ratio': 0.5,
                        'condition': 'profit_exceed'
                    }
                ]
            },
            'description': '测试用策略'
        }
        
        response = client.post('/api/strategies', json=strategy_data)
        assert response.status_code == 201
        strategy_id = response.json['data']['id']
        
        # 2. 获取策略列表
        response = client.get('/api/strategies')
        assert response.status_code == 200
        strategies = response.json['data']
        assert len(strategies) >= 1
        
        # 3. 获取单个策略
        response = client.get(f'/api/strategies/{strategy_id}')
        assert response.status_code == 200
        strategy = response.json['data']
        assert strategy['strategy_name'] == '测试策略'
        
        # 4. 更新策略
        update_data = {
            'is_active': False,
            'description': '更新后的策略描述'
        }
        
        response = client.put(f'/api/strategies/{strategy_id}', json=update_data)
        assert response.status_code == 200
        assert response.json['data']['is_active'] == False
        
        # 5. 创建持仓数据用于策略评估测试
        self._create_holdings_for_strategy_test(client)
        
        # 6. 评估策略
        response = client.post('/api/strategies/evaluate')
        assert response.status_code == 200
        
        # 7. 获取持仓提醒
        response = client.get('/api/holdings/alerts')
        assert response.status_code == 200
        alerts = response.json['data']
        # 由于策略已停用，应该没有提醒或提醒数量较少
        
        # 8. 重新启用策略
        response = client.put(f'/api/strategies/{strategy_id}', json={'is_active': True})
        assert response.status_code == 200
        
        # 9. 再次评估策略
        response = client.post('/api/strategies/evaluate')
        assert response.status_code == 200
        
        # 10. 删除策略
        response = client.delete(f'/api/strategies/{strategy_id}')
        assert response.status_code == 200
        
        # 验证删除
        response = client.get(f'/api/strategies/{strategy_id}')
        assert response.status_code == 404
        
    def _create_analytics_test_data(self, client):
        """创建统计分析测试数据"""
        trades_data = [
            # 盈利交易对
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 10.00,
                'quantity': 1000,
                'trade_date': (datetime.now() - timedelta(days=10)).isoformat(),
                'reason': '测试买入'
            },
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'sell',
                'price': 12.00,
                'quantity': 1000,
                'trade_date': (datetime.now() - timedelta(days=5)).isoformat(),
                'reason': '测试卖出'
            },
            # 亏损交易对
            {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'buy',
                'price': 15.00,
                'quantity': 500,
                'trade_date': (datetime.now() - timedelta(days=8)).isoformat(),
                'reason': '测试买入'
            },
            {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'sell',
                'price': 14.00,
                'quantity': 500,
                'trade_date': (datetime.now() - timedelta(days=3)).isoformat(),
                'reason': '测试卖出'
            },
            # 持仓中
            {
                'stock_code': '000003',
                'stock_name': '招商银行',
                'trade_type': 'buy',
                'price': 20.00,
                'quantity': 800,
                'trade_date': (datetime.now() - timedelta(days=2)).isoformat(),
                'reason': '测试买入'
            }
        ]
        
        for trade_data in trades_data:
            response = client.post('/api/trades', json=trade_data)
            assert response.status_code == 201
        
        # 添加当前价格
        price_data = {
            'stock_code': '000003',
            'stock_name': '招商银行',
            'current_price': 22.00,
            'change_percent': 10.0,
            'record_date': date.today().isoformat()
        }
        
        response = client.post('/api/prices', json=price_data)
        assert response.status_code == 201
        
    def _create_holdings_for_strategy_test(self, client):
        """创建持仓数据用于策略测试"""
        # 创建买入记录
        buy_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 10.00,
            'quantity': 1000,
            'trade_date': (datetime.now() - timedelta(days=7)).isoformat(),
            'reason': '策略测试买入'
        }
        
        response = client.post('/api/trades', json=buy_data)
        assert response.status_code == 201
        
        # 创建复盘记录（设置持仓天数）
        review_data = {
            'stock_code': '000001',
            'review_date': date.today().isoformat(),
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 1,
            'trend_score': 1,
            'j_score': 1,
            'analysis': '策略测试复盘',
            'decision': 'hold',
            'reason': '继续持有',
            'holding_days': 7
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        
        # 添加当前价格
        price_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'current_price': 11.50,  # 上涨15%
            'change_percent': 15.0,
            'record_date': date.today().isoformat()
        }
        
        response = client.post('/api/prices', json=price_data)
        assert response.status_code == 201