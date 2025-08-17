"""
端到端测试 - 完整用户流程测试
测试完整的用户业务流程，从交易记录创建到复盘分析的全流程
"""
import pytest
from datetime import datetime, date, timedelta
from models.trade_record import TradeRecord
from models.review_record import ReviewRecord
from models.stock_pool import StockPool
from models.case_study import CaseStudy
from models.stock_price import StockPrice
from models.sector_data import SectorData
from models.trading_strategy import TradingStrategy
from extensions import db
import json


class TestCompleteUserWorkflows:
    """完整用户工作流程测试"""
    
    def test_complete_trading_workflow(self, client, db_session):
        """测试完整的交易工作流程：从股票池 -> 买入 -> 复盘 -> 卖出"""
        
        # 1. 添加股票到观察池
        stock_pool_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'target_price': 12.00,
            'add_reason': '技术形态良好',
            'status': 'active'
        }
        
        response = client.post('/api/stock-pool', json=stock_pool_data)
        assert response.status_code == 201
        pool_id = response.json['data']['id']
        
        # 2. 将股票移至待买入池
        update_data = {
            'pool_type': 'buy_ready',
            'target_price': 12.50,
            'add_reason': '突破关键阻力位'
        }
        
        response = client.put(f'/api/stock-pool/{pool_id}', json=update_data)
        assert response.status_code == 200
        assert response.json['data']['pool_type'] == 'buy_ready'
        
        # 3. 执行买入操作
        buy_trade_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '少妇B1战法',
            'notes': '突破买入',
            'stop_loss_price': 11.25,
            'take_profit_ratio': 0.15,
            'sell_ratio': 0.5
        }
        
        response = client.post('/api/trades', json=buy_trade_data)
        assert response.status_code == 201
        buy_trade_id = response.json['data']['id']
        
        # 验证止损止盈计算
        trade_data = response.json['data']
        assert trade_data['expected_loss_ratio'] == 0.1  # (12.5-11.25)/12.5
        assert abs(trade_data['expected_profit_ratio'] - 0.075) < 0.001  # 15% * 50%
        
        # 4. 从股票池移除（已买入）
        response = client.delete(f'/api/stock-pool/{pool_id}')
        assert response.status_code == 200
        
        # 5. 进行每日复盘
        review_data = {
            'stock_code': '000001',
            'review_date': date.today().isoformat(),
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 0,
            'trend_score': 1,
            'j_score': 1,
            'analysis': '整体表现良好，继续持有',
            'decision': 'hold',
            'reason': '技术指标良好',
            'holding_days': 3
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        assert response.json['data']['total_score'] == 4
        
        # 6. 获取持仓列表，验证持仓状态
        response = client.get('/api/holdings')
        assert response.status_code == 200
        holdings = response.json['data']
        assert len(holdings) == 1
        assert holdings[0]['stock_code'] == '000001'
        assert holdings[0]['quantity'] == 1000
        
        # 7. 模拟价格上涨，触发策略提醒
        # 先创建策略
        strategy_data = {
            'strategy_name': '测试策略',
            'is_active': True,
            'rules': {
                'rules': [
                    {
                        'day_range': [1, 5],
                        'profit_threshold': 0.10,
                        'action': 'sell_partial',
                        'sell_ratio': 0.3,
                        'condition': 'profit_exceed'
                    }
                ]
            },
            'description': '测试策略'
        }
        
        response = client.post('/api/strategies', json=strategy_data)
        assert response.status_code == 201
        
        # 更新股票价格（模拟上涨15%）
        price_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'current_price': 14.38,  # 上涨15%
            'change_percent': 15.04,
            'record_date': date.today().isoformat()
        }
        
        response = client.post('/api/prices', json=price_data)
        assert response.status_code == 201
        
        # 8. 获取持仓提醒
        response = client.get('/api/holdings/alerts')
        assert response.status_code == 200
        alerts = response.json['data']
        assert len(alerts) > 0
        alert = alerts[0]
        assert alert['stock_code'] == '000001'
        assert alert['alert_type'] == 'sell_partial'
        assert alert['sell_ratio'] == 0.3
        
        # 9. 执行部分卖出
        sell_trade_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'sell',
            'price': 14.38,
            'quantity': 300,  # 卖出30%
            'trade_date': datetime.now().isoformat(),
            'reason': '部分止盈',
            'notes': '策略提醒卖出'
        }
        
        response = client.post('/api/trades', json=sell_trade_data)
        assert response.status_code == 201
        
        # 10. 验证持仓更新
        response = client.get('/api/holdings')
        assert response.status_code == 200
        holdings = response.json['data']
        assert holdings[0]['quantity'] == 700  # 剩余70%
        
        # 11. 获取交易统计
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        analytics = response.json['data']
        assert analytics['total_trades'] == 2
        assert analytics['realized_profit'] > 0  # 有实现收益
        
    def test_case_study_workflow(self, client, db_session):
        """测试案例研究工作流程"""
        
        # 1. 上传案例截图
        case_data = {
            'stock_code': '000002',
            'title': '万科A突破案例',
            'image_path': '/uploads/test_case.png',
            'tags': ['突破', '地产股'],
            'notes': '经典突破形态'
        }
        
        response = client.post('/api/cases', json=case_data)
        assert response.status_code == 201
        case_id = response.json['data']['id']
        
        # 2. 搜索案例
        response = client.get('/api/cases?search=突破')
        assert response.status_code == 200
        cases = response.json['data']
        assert len(cases) == 1
        assert cases[0]['title'] == '万科A突破案例'
        
        # 3. 按标签筛选
        response = client.get('/api/cases?tags=地产股')
        assert response.status_code == 200
        cases = response.json['data']
        assert len(cases) == 1
        
        # 4. 更新案例信息
        update_data = {
            'notes': '经典突破形态，后续涨幅达到20%',
            'tags': ['突破', '地产股', '成功案例']
        }
        
        response = client.put(f'/api/cases/{case_id}', json=update_data)
        assert response.status_code == 200
        assert '成功案例' in response.json['data']['tags']
        
    def test_sector_analysis_workflow(self, client, db_session):
        """测试板块分析工作流程"""
        
        # 1. 模拟添加多天板块数据
        base_date = date.today() - timedelta(days=5)
        sectors = ['银行', '地产', '科技', '医药', '消费']
        
        for day_offset in range(5):
            current_date = base_date + timedelta(days=day_offset)
            for i, sector in enumerate(sectors):
                sector_data = {
                    'sector_name': sector,
                    'sector_code': f'BK{1000+i}',
                    'change_percent': (i + day_offset) * 0.5 + 1.0,
                    'record_date': current_date.isoformat(),
                    'rank_position': i + 1,
                    'volume': 1000000000 * (i + 1),
                    'market_cap': 500000000000.0 * (i + 1)
                }
                
                response = client.post('/api/sectors', json=sector_data)
                assert response.status_code == 201
        
        # 2. 获取最新板块排名
        response = client.get('/api/sectors/ranking')
        assert response.status_code == 200
        ranking = response.json['data']
        assert len(ranking) > 0
        
        # 3. 获取历史表现
        start_date = (base_date).isoformat()
        end_date = date.today().isoformat()
        response = client.get(f'/api/sectors/history?start_date={start_date}&end_date={end_date}')
        assert response.status_code == 200
        history = response.json['data']
        assert len(history) > 0
        
        # 4. 获取TOPK统计
        response = client.get('/api/sectors/top-performers?days=5&top_k=3')
        assert response.status_code == 200
        top_performers = response.json['data']
        assert len(top_performers) > 0
        
        # 验证统计数据
        for performer in top_performers:
            assert 'sector_name' in performer
            assert 'appearances' in performer
            assert 'avg_rank' in performer
            assert performer['appearances'] > 0
            
    def test_correction_workflow(self, client, db_session):
        """测试交易记录订正工作流程"""
        
        # 1. 创建原始交易记录
        original_trade_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '少妇B1战法',
            'notes': '原始记录'
        }
        
        response = client.post('/api/trades', json=original_trade_data)
        assert response.status_code == 201
        original_trade_id = response.json['data']['id']
        
        # 2. 订正交易记录
        correction_data = {
            'price': 12.80,  # 订正价格
            'quantity': 1200,  # 订正数量
            'notes': '订正后记录',
            'correction_reason': '发现价格记录错误'
        }
        
        response = client.post(f'/api/trades/{original_trade_id}/correct', json=correction_data)
        assert response.status_code == 201
        corrected_trade_id = response.json['data']['id']
        
        # 3. 验证原始记录被标记为已订正
        response = client.get(f'/api/trades/{original_trade_id}')
        assert response.status_code == 200
        original_trade = response.json['data']
        assert original_trade['is_corrected'] == True
        
        # 4. 验证订正记录
        response = client.get(f'/api/trades/{corrected_trade_id}')
        assert response.status_code == 200
        corrected_trade = response.json['data']
        assert corrected_trade['price'] == 12.80
        assert corrected_trade['quantity'] == 1200
        assert corrected_trade['original_record_id'] == original_trade_id
        
        # 5. 获取订正历史
        response = client.get(f'/api/trades/{original_trade_id}/history')
        assert response.status_code == 200
        history = response.json['data']
        assert len(history) == 1
        assert history[0]['correction_reason'] == '发现价格记录错误'
        
    def test_analytics_comprehensive_workflow(self, client, db_session):
        """测试统计分析综合工作流程"""
        
        # 1. 创建多笔交易记录（包含买入和卖出）
        trades_data = [
            # 第一笔：盈利交易
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 10.00,
                'quantity': 1000,
                'trade_date': (datetime.now() - timedelta(days=10)).isoformat(),
                'reason': '少妇B1战法'
            },
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'sell',
                'price': 12.00,
                'quantity': 1000,
                'trade_date': (datetime.now() - timedelta(days=5)).isoformat(),
                'reason': '部分止盈'
            },
            # 第二笔：亏损交易
            {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'buy',
                'price': 15.00,
                'quantity': 500,
                'trade_date': (datetime.now() - timedelta(days=8)).isoformat(),
                'reason': '少妇B2战法'
            },
            {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'sell',
                'price': 14.00,
                'quantity': 500,
                'trade_date': (datetime.now() - timedelta(days=3)).isoformat(),
                'reason': '止损'
            },
            # 第三笔：持仓中
            {
                'stock_code': '000003',
                'stock_name': '招商银行',
                'trade_type': 'buy',
                'price': 20.00,
                'quantity': 800,
                'trade_date': (datetime.now() - timedelta(days=2)).isoformat(),
                'reason': '单针二十战法'
            }
        ]
        
        for trade_data in trades_data:
            response = client.post('/api/trades', json=trade_data)
            assert response.status_code == 201
        
        # 2. 添加当前价格数据
        price_data = [
            {
                'stock_code': '000003',
                'stock_name': '招商银行',
                'current_price': 22.00,  # 浮盈10%
                'change_percent': 10.0,
                'record_date': date.today().isoformat()
            }
        ]
        
        for price in price_data:
            response = client.post('/api/prices', json=price)
            assert response.status_code == 201
        
        # 3. 获取总体统计
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        overview = response.json['data']
        
        # 验证统计数据
        assert overview['total_trades'] == 5
        assert overview['realized_profit'] == 1500.0  # (12-10)*1000 + (14-15)*500
        assert overview['unrealized_profit'] == 1600.0  # (22-20)*800
        assert overview['total_profit'] == 3100.0
        assert overview['success_rate'] == 0.5  # 1盈利/2完成交易
        
        # 4. 获取收益分布
        response = client.get('/api/analytics/profit-distribution')
        assert response.status_code == 200
        distribution = response.json['data']
        
        # 验证分布数据
        assert len(distribution) > 0
        total_stocks = sum(d['count'] for d in distribution)
        assert total_stocks == 3  # 总共3只股票
        
        # 5. 获取月度统计
        response = client.get('/api/analytics/monthly')
        assert response.status_code == 200
        monthly = response.json['data']
        
        # 验证月度数据
        current_month_data = next((m for m in monthly if m['month'] == date.today().strftime('%Y-%m')), None)
        assert current_month_data is not None
        assert current_month_data['trade_count'] == 5
        
    def test_strategy_evaluation_workflow(self, client, db_session):
        """测试策略评估工作流程"""
        
        # 1. 创建交易策略
        strategy_data = {
            'strategy_name': '综合测试策略',
            'is_active': True,
            'rules': {
                'rules': [
                    {
                        'day_range': [1, 3],
                        'loss_threshold': -0.05,
                        'action': 'sell_all',
                        'condition': 'loss_exceed'
                    },
                    {
                        'day_range': [4, 7],
                        'profit_threshold': 0.10,
                        'action': 'sell_partial',
                        'sell_ratio': 0.5,
                        'condition': 'profit_exceed'
                    },
                    {
                        'day_range': [8, 15],
                        'profit_threshold': 0.15,
                        'drawdown_threshold': 0.10,
                        'action': 'sell_all',
                        'condition': 'profit_below_or_drawdown'
                    }
                ]
            },
            'description': '多阶段动态策略'
        }
        
        response = client.post('/api/strategies', json=strategy_data)
        assert response.status_code == 201
        strategy_id = response.json['data']['id']
        
        # 2. 创建持仓记录
        buy_trade_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 10.00,
            'quantity': 1000,
            'trade_date': (datetime.now() - timedelta(days=5)).isoformat(),
            'reason': '测试买入'
        }
        
        response = client.post('/api/trades', json=buy_trade_data)
        assert response.status_code == 201
        
        # 3. 创建复盘记录（设置持仓天数）
        review_data = {
            'stock_code': '000001',
            'review_date': date.today().isoformat(),
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 1,
            'trend_score': 1,
            'j_score': 1,
            'analysis': '测试复盘',
            'decision': 'hold',
            'reason': '继续持有',
            'holding_days': 5
        }
        
        response = client.post('/api/reviews', json=review_data)
        assert response.status_code == 201
        
        # 4. 更新股票价格（触发策略）
        price_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'current_price': 11.20,  # 上涨12%
            'change_percent': 12.0,
            'record_date': date.today().isoformat()
        }
        
        response = client.post('/api/prices', json=price_data)
        assert response.status_code == 201
        
        # 5. 评估策略提醒
        response = client.post('/api/strategies/evaluate')
        assert response.status_code == 200
        
        # 6. 获取持仓提醒
        response = client.get('/api/holdings/alerts')
        assert response.status_code == 200
        alerts = response.json['data']
        
        # 验证策略提醒
        alert = next((a for a in alerts if a['stock_code'] == '000001'), None)
        assert alert is not None
        assert alert['alert_type'] == 'sell_partial'  # 5天持仓，12%收益，应触发部分卖出
        assert alert['sell_ratio'] == 0.5
        
        # 7. 测试策略更新
        update_data = {
            'is_active': False
        }
        
        response = client.put(f'/api/strategies/{strategy_id}', json=update_data)
        assert response.status_code == 200
        
        # 8. 验证策略停用后无提醒
        response = client.get('/api/holdings/alerts')
        assert response.status_code == 200
        alerts = response.json['data']
        
        # 应该没有来自已停用策略的提醒
        active_alerts = [a for a in alerts if a.get('strategy_active', True)]
        assert len(active_alerts) == 0 or all(not a.get('strategy_active', True) for a in alerts)