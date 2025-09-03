"""
历史交易记录API集成测试
"""
import pytest
import json
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Flask
from extensions import db
from models.historical_trade import HistoricalTrade
from models.trade_record import TradeRecord
from services.historical_trade_service import HistoricalTradeService


class TestHistoricalTradeAPI:
    """历史交易记录API测试类"""
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    @pytest.fixture
    def sample_trade_records(self, app):
        """创建示例交易记录"""
        with app.app_context():
            # 清理现有数据
            TradeRecord.query.delete()
            db.session.commit()
            
            # 创建买入记录
            buy_record1 = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=Decimal('10.00'),
                quantity=1000,
                trade_date=datetime(2024, 1, 1),
                reason='技术分析'
            )
            
            buy_record2 = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=Decimal('9.50'),
                quantity=500,
                trade_date=datetime(2024, 1, 5),
                reason='补仓'
            )
            
            # 创建卖出记录
            sell_record = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='sell',
                price=Decimal('11.00'),
                quantity=1500,
                trade_date=datetime(2024, 1, 15),
                reason='止盈'
            )
            
            db.session.add_all([buy_record1, buy_record2, sell_record])
            db.session.commit()
            
            # 刷新对象以确保它们绑定到会话
            db.session.refresh(buy_record1)
            db.session.refresh(buy_record2)
            db.session.refresh(sell_record)
            
            return {
                'buy_records': [buy_record1, buy_record2],
                'sell_records': [sell_record]
            }
    
    @pytest.fixture
    def sample_historical_trade(self, app, sample_trade_records):
        """创建示例历史交易记录"""
        with app.app_context():
            # 清理现有历史交易数据
            HistoricalTrade.query.delete()
            db.session.commit()
            
            buy_records = sample_trade_records['buy_records']
            sell_records = sample_trade_records['sell_records']
            
            historical_trade = HistoricalTrade(
                stock_code='000001',
                stock_name='平安银行',
                buy_date=datetime(2024, 1, 1),
                sell_date=datetime(2024, 1, 15),
                holding_days=14,
                total_investment=Decimal('14750.00'),  # 10*1000 + 9.5*500
                total_return=Decimal('1750.00'),       # 11*1500 - 14750
                return_rate=Decimal('0.1186'),         # 1750/14750
                buy_records_ids=json.dumps([buy_records[0].id, buy_records[1].id]),
                sell_records_ids=json.dumps([sell_records[0].id]),
                is_completed=True,
                completion_date=datetime(2024, 1, 15)
            )
            
            db.session.add(historical_trade)
            db.session.commit()
            db.session.refresh(historical_trade)
            
            return historical_trade
    
    def test_get_historical_trades_empty(self, client, app):
        """测试获取空的历史交易记录列表"""
        with app.app_context():
            response = client.get('/api/historical-trades')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['message'] == '获取历史交易记录成功'
            assert data['data']['total'] == 0
            assert data['data']['trades'] == []
    
    def test_get_historical_trades_with_data(self, client, app, sample_historical_trade):
        """测试获取历史交易记录列表（有数据）"""
        with app.app_context():
            response = client.get('/api/historical-trades')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['data']['total'] == 1
            assert len(data['data']['trades']) == 1
            
            trade = data['data']['trades'][0]
            assert trade['stock_code'] == '000001'
            assert trade['stock_name'] == '平安银行'
            assert trade['holding_days'] == 14
            assert float(trade['total_investment']) == 14750.00
            assert float(trade['total_return']) == 1750.00
    
    def test_get_historical_trades_with_pagination(self, client, app):
        """测试分页获取历史交易记录"""
        with app.app_context():
            # 清理现有数据
            HistoricalTrade.query.delete()
            db.session.commit()
            
            # 创建多条历史交易记录
            for i in range(25):
                trade = HistoricalTrade(
                    stock_code=f'00000{i % 5 + 1}',
                    stock_name=f'测试股票{i}',
                    buy_date=datetime(2024, 1, 1) + timedelta(days=i),
                    sell_date=datetime(2024, 1, 1) + timedelta(days=i+10),
                    holding_days=10,
                    total_investment=Decimal('10000.00'),
                    total_return=Decimal('1000.00'),
                    return_rate=Decimal('0.10'),
                    is_completed=True,
                    completion_date=datetime(2024, 1, 1) + timedelta(days=i+10)
                )
                db.session.add(trade)
            
            db.session.commit()
            
            # 测试第一页
            response = client.get('/api/historical-trades?page=1&per_page=10')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['data']['total'] == 25
            assert data['data']['current_page'] == 1
            assert data['data']['per_page'] == 10
            assert len(data['data']['trades']) == 10
            assert data['data']['has_next'] is True
            assert data['data']['has_prev'] is False
            
            # 测试第二页
            response = client.get('/api/historical-trades?page=2&per_page=10')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['data']['current_page'] == 2
            assert len(data['data']['trades']) == 10
            assert data['data']['has_next'] is True
            assert data['data']['has_prev'] is True
    
    def test_get_historical_trades_with_filters(self, client, app):
        """测试筛选获取历史交易记录"""
        with app.app_context():
            # 清理现有数据
            HistoricalTrade.query.delete()
            db.session.commit()
            
            # 创建不同的历史交易记录
            trade1 = HistoricalTrade(
                stock_code='000001',
                stock_name='平安银行',
                buy_date=datetime(2024, 1, 1),
                sell_date=datetime(2024, 1, 15),
                holding_days=14,
                total_investment=Decimal('10000.00'),
                total_return=Decimal('1000.00'),
                return_rate=Decimal('0.10'),
                is_completed=True,
                completion_date=datetime(2024, 1, 15)
            )
            
            trade2 = HistoricalTrade(
                stock_code='000002',
                stock_name='万科A',
                buy_date=datetime(2024, 2, 1),
                sell_date=datetime(2024, 2, 20),
                holding_days=19,
                total_investment=Decimal('20000.00'),
                total_return=Decimal('-1000.00'),
                return_rate=Decimal('-0.05'),
                is_completed=True,
                completion_date=datetime(2024, 2, 20)
            )
            
            db.session.add_all([trade1, trade2])
            db.session.commit()
            
            # 测试股票代码筛选
            response = client.get('/api/historical-trades?stock_code=000001')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['data']['total'] == 1
            assert data['data']['trades'][0]['stock_code'] == '000001'
            
            # 测试盈利状态筛选
            response = client.get('/api/historical-trades?is_profitable=true')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['data']['total'] == 1
            assert data['data']['trades'][0]['stock_code'] == '000001'
            
            # 测试日期范围筛选
            response = client.get('/api/historical-trades?start_date=2024-02-01&end_date=2024-02-28')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['data']['total'] == 1
            assert data['data']['trades'][0]['stock_code'] == '000002'
    
    def test_get_historical_trades_with_sorting(self, client, app):
        """测试排序获取历史交易记录"""
        with app.app_context():
            # 清理现有数据
            HistoricalTrade.query.delete()
            db.session.commit()
            
            # 创建不同收益率的交易记录
            trade1 = HistoricalTrade(
                stock_code='000001',
                stock_name='股票1',
                buy_date=datetime(2024, 1, 1),
                sell_date=datetime(2024, 1, 15),
                holding_days=14,
                total_investment=Decimal('10000.00'),
                total_return=Decimal('500.00'),
                return_rate=Decimal('0.05'),
                is_completed=True,
                completion_date=datetime(2024, 1, 15)
            )
            
            trade2 = HistoricalTrade(
                stock_code='000002',
                stock_name='股票2',
                buy_date=datetime(2024, 1, 1),
                sell_date=datetime(2024, 1, 15),
                holding_days=14,
                total_investment=Decimal('10000.00'),
                total_return=Decimal('1500.00'),
                return_rate=Decimal('0.15'),
                is_completed=True,
                completion_date=datetime(2024, 1, 15)
            )
            
            db.session.add_all([trade1, trade2])
            db.session.commit()
            
            # 测试按收益率降序排序
            response = client.get('/api/historical-trades?sort_by=return_rate&sort_order=desc')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['data']['total'] == 2
            assert data['data']['trades'][0]['stock_code'] == '000002'  # 收益率更高的在前
            assert data['data']['trades'][1]['stock_code'] == '000001'
            
            # 测试按收益率升序排序
            response = client.get('/api/historical-trades?sort_by=return_rate&sort_order=asc')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['data']['trades'][0]['stock_code'] == '000001'  # 收益率更低的在前
            assert data['data']['trades'][1]['stock_code'] == '000002'
    
    def test_get_historical_trade_detail(self, client, app, sample_historical_trade):
        """测试获取单个历史交易记录详情"""
        with app.app_context():
            trade_id = sample_historical_trade.id
            
            response = client.get(f'/api/historical-trades/{trade_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['message'] == '获取历史交易记录详情成功'
            
            trade_data = data['data']
            assert trade_data['id'] == trade_id
            assert trade_data['stock_code'] == '000001'
            assert trade_data['stock_name'] == '平安银行'
            assert 'buy_records' in trade_data
            assert 'sell_records' in trade_data
            assert 'reviews' in trade_data
            assert len(trade_data['buy_records']) == 2
            assert len(trade_data['sell_records']) == 1
    
    def test_get_historical_trade_detail_not_found(self, client, app):
        """测试获取不存在的历史交易记录详情"""
        with app.app_context():
            response = client.get('/api/historical-trades/99999')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            
            assert data['success'] is False
            assert 'error' in data or 'message' in data
    
    def test_sync_historical_trades(self, client, app, sample_trade_records):
        """测试同步历史交易记录"""
        with app.app_context():
            # 确保没有现有的历史交易记录
            HistoricalTrade.query.delete()
            db.session.commit()
            
            response = client.post('/api/historical-trades/sync', 
                                 json={},
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert '同步成功' in data['message']
            assert data['data']['created_count'] >= 0
            assert 'total_checked' in data['data']
    
    def test_generate_historical_trades(self, client, app, sample_trade_records):
        """测试生成历史交易记录"""
        with app.app_context():
            # 确保没有现有的历史交易记录
            HistoricalTrade.query.delete()
            db.session.commit()
            
            response = client.post('/api/historical-trades/generate',
                                 json={},
                                 content_type='application/json')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert '生成成功' in data['message']
            assert data['data']['created_count'] >= 0
            assert 'total_identified' in data['data']
    
    def test_generate_historical_trades_force_regenerate(self, client, app, sample_historical_trade):
        """测试强制重新生成历史交易记录"""
        with app.app_context():
            # 记录现有记录数
            initial_count = HistoricalTrade.query.count()
            assert initial_count > 0
            
            response = client.post('/api/historical-trades/generate', 
                                 json={'force_regenerate': True})
            
            assert response.status_code == 201
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert '生成成功' in data['message']
    
    def test_get_historical_trade_statistics(self, client, app, sample_historical_trade):
        """测试获取历史交易统计信息"""
        with app.app_context():
            response = client.get('/api/historical-trades/statistics')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['message'] == '获取历史交易统计信息成功'
            
            stats = data['data']
            assert 'total_trades' in stats
            assert 'profitable_trades' in stats
            assert 'loss_trades' in stats
            assert 'win_rate' in stats
            assert 'total_investment' in stats
            assert 'total_return' in stats
            assert 'overall_return_rate' in stats
            assert stats['total_trades'] >= 1
    
    def test_identify_completed_trades(self, client, app, sample_trade_records):
        """测试识别已完成的交易"""
        with app.app_context():
            response = client.post('/api/historical-trades/identify')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['message'] == '识别已完成交易成功'
            assert 'completed_trades' in data['data']
            assert 'total_count' in data['data']
            assert data['data']['total_count'] >= 0
    
    def test_calculate_trade_metrics(self, client, app, sample_trade_records):
        """测试计算交易指标"""
        with app.app_context():
            buy_records = sample_trade_records['buy_records']
            sell_records = sample_trade_records['sell_records']
            
            # 获取记录ID，确保在会话中
            buy_ids = []
            sell_ids = []
            
            for record in buy_records:
                db.session.refresh(record)
                buy_ids.append(record.id)
            
            for record in sell_records:
                db.session.refresh(record)
                sell_ids.append(record.id)
            
            request_data = {
                'buy_records_ids': buy_ids,
                'sell_records_ids': sell_ids
            }
            
            response = client.post('/api/historical-trades/calculate-metrics', 
                                 json=request_data)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['message'] == '计算交易指标成功'
            
            metrics = data['data']
            assert 'buy_date' in metrics
            assert 'sell_date' in metrics
            assert 'holding_days' in metrics
            assert 'total_investment' in metrics
            assert 'total_return' in metrics
            assert 'return_rate' in metrics
            assert 'is_profitable' in metrics
    
    def test_validate_historical_trade_data(self, client, app):
        """测试验证历史交易数据"""
        with app.app_context():
            valid_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'buy_date': '2024-01-01T00:00:00',
                'sell_date': '2024-01-15T00:00:00',
                'holding_days': 14,
                'total_investment': 10000.00,
                'total_return': 1000.00,
                'return_rate': 0.10,
                'is_completed': True,
                'completion_date': '2024-01-15T00:00:00'
            }
            
            response = client.post('/api/historical-trades/validate', 
                                 json=valid_data)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['message'] == '历史交易数据验证通过'
            assert data['data']['is_valid'] is True
            assert 'validated_data' in data['data']
    
    def test_validate_historical_trade_data_invalid(self, client, app):
        """测试验证无效的历史交易数据"""
        with app.app_context():
            invalid_data = {
                'stock_code': '',  # 空股票代码
                'stock_name': '平安银行',
                'buy_date': '2024-01-15T00:00:00',  # 买入日期晚于卖出日期
                'sell_date': '2024-01-01T00:00:00',
                'total_investment': -1000.00,  # 负投资金额
                'total_return': 1000.00,
                'return_rate': 0.10
            }
            
            response = client.post('/api/historical-trades/validate', 
                                 json=invalid_data)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['message'] == '历史交易数据验证失败'
            assert data['data']['is_valid'] is False
            assert 'validation_errors' in data['data']
    
    def test_api_parameter_validation(self, client, app):
        """测试API参数验证"""
        with app.app_context():
            # 测试无效的页码
            response = client.get('/api/historical-trades?page=0')
            assert response.status_code == 400
            
            # 测试无效的每页数量
            response = client.get('/api/historical-trades?per_page=101')
            assert response.status_code == 400
            
            # 测试无效的排序字段
            response = client.get('/api/historical-trades?sort_by=invalid_field')
            assert response.status_code == 400
            
            # 测试无效的排序方向
            response = client.get('/api/historical-trades?sort_order=invalid')
            assert response.status_code == 400
            
            # 测试无效的收益率格式
            response = client.get('/api/historical-trades?min_return_rate=invalid')
            assert response.status_code == 400
            
            # 测试无效的持仓天数格式
            response = client.get('/api/historical-trades?min_holding_days=invalid')
            assert response.status_code == 400
    
    def test_api_error_handling(self, client, app):
        """测试API错误处理"""
        with app.app_context():
            # 测试获取不存在的记录
            response = client.get('/api/historical-trades/99999')
            assert response.status_code == 404
            
            # 测试计算指标时缺少参数
            response = client.post('/api/historical-trades/calculate-metrics', json={})
            assert response.status_code == 400
            
            # 测试计算指标时使用不存在的记录ID
            response = client.post('/api/historical-trades/calculate-metrics', 
                                 json={
                                     'buy_records_ids': [99999],
                                     'sell_records_ids': [99998]
                                 })
            assert response.status_code == 404
            
            # 测试验证数据时缺少必填字段
            response = client.post('/api/historical-trades/validate', 
                                 json={'stock_code': '000001'})
            assert response.status_code == 200  # 验证失败但返回200
            data = json.loads(response.data)
            assert data['data']['is_valid'] is False
    
    def test_api_response_format(self, client, app, sample_historical_trade):
        """测试API响应格式"""
        with app.app_context():
            response = client.get('/api/historical-trades')
            
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            
            data = json.loads(response.data)
            
            # 验证标准响应格式
            assert 'success' in data
            assert 'message' in data
            assert 'data' in data
            assert isinstance(data['success'], bool)
            assert isinstance(data['message'], str)
            assert isinstance(data['data'], dict)
    
    def test_api_logging(self, client, app, caplog):
        """测试API日志记录"""
        with app.app_context():
            response = client.get('/api/historical-trades')
            
            # 验证日志记录
            assert '获取历史交易记录列表请求开始' in caplog.text
            assert '获取历史交易记录列表请求完成' in caplog.text