"""
股票池集成测试
"""
import pytest
import json
from datetime import datetime, timedelta
from models.stock_pool import StockPool
from services.stock_pool_service import StockPoolService


class TestStockPoolIntegration:
    """股票池集成测试类"""
    
    def test_complete_stock_pool_workflow(self, client, db_session):
        """测试完整的股票池工作流程"""
        # 1. 添加股票到待观测池
        watch_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'target_price': 12.50,
            'add_reason': '技术面良好，突破关键阻力位'
        }
        
        response = client.post('/api/stock-pool',
                             data=json.dumps(watch_data),
                             content_type='application/json')
        assert response.status_code == 201
        watch_stock_data = response.get_json()['data']
        watch_stock_id = watch_stock_data['id']
        
        # 2. 验证股票在待观测池中
        response = client.get('/api/stock-pool/watch')
        assert response.status_code == 200
        watch_pool = response.get_json()['data']
        assert watch_pool['total'] == 1
        assert watch_pool['items'][0]['stock_code'] == '000001'
        
        # 3. 移动股票到待买入池
        move_data = {
            'new_pool_type': 'buy_ready',
            'reason': '价格回调到目标位置，准备买入'
        }
        
        response = client.post(f'/api/stock-pool/{watch_stock_id}/move',
                             data=json.dumps(move_data),
                             content_type='application/json')
        assert response.status_code == 200
        moved_stock_data = response.get_json()['data']
        buy_ready_stock_id = moved_stock_data['id']
        
        # 4. 验证股票在待买入池中
        response = client.get('/api/stock-pool/buy-ready')
        assert response.status_code == 200
        buy_ready_pool = response.get_json()['data']
        assert buy_ready_pool['total'] == 1
        assert buy_ready_pool['items'][0]['stock_code'] == '000001'
        assert buy_ready_pool['items'][0]['pool_type'] == 'buy_ready'
        
        # 5. 验证待观测池为空（原记录状态为moved）
        response = client.get('/api/stock-pool/watch')
        assert response.status_code == 200
        watch_pool = response.get_json()['data']
        assert watch_pool['total'] == 0
        
        # 6. 查看股票流转历史
        response = client.get('/api/stock-pool/history/000001')
        assert response.status_code == 200
        history_data = response.get_json()['data']
        assert len(history_data['history']) == 2
        # 最新记录应该是buy_ready池的活跃记录
        assert history_data['history'][0]['pool_type'] == 'buy_ready'
        assert history_data['history'][0]['status'] == 'active'
        # 旧记录应该是watch池的moved记录
        assert history_data['history'][1]['pool_type'] == 'watch'
        assert history_data['history'][1]['status'] == 'moved'
        
        # 7. 从池中移除股票
        remove_data = {
            'reason': '已完成买入，不再需要关注'
        }
        
        response = client.post(f'/api/stock-pool/{buy_ready_stock_id}/remove',
                             data=json.dumps(remove_data),
                             content_type='application/json')
        assert response.status_code == 200
        
        # 8. 验证待买入池为空
        response = client.get('/api/stock-pool/buy-ready')
        assert response.status_code == 200
        buy_ready_pool = response.get_json()['data']
        assert buy_ready_pool['total'] == 0
        
        # 9. 验证历史记录包含移除记录
        response = client.get('/api/stock-pool/history/000001')
        assert response.status_code == 200
        history_data = response.get_json()['data']
        assert len(history_data['history']) == 2
        # 最新记录应该是removed状态
        assert history_data['history'][0]['status'] == 'removed'
        assert '已完成买入' in history_data['history'][0]['add_reason']
    
    def test_batch_operations_workflow(self, client, db_session):
        """测试批量操作工作流程"""
        # 1. 创建多个股票在待观测池
        stocks_data = [
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'pool_type': 'watch',
                'add_reason': '技术面良好'
            },
            {
                'stock_code': '000002',
                'stock_name': '万科A',
                'pool_type': 'watch',
                'add_reason': '基本面改善'
            },
            {
                'stock_code': '000858',
                'stock_name': '五粮液',
                'pool_type': 'watch',
                'add_reason': '行业复苏'
            }
        ]
        
        stock_ids = []
        for stock_data in stocks_data:
            response = client.post('/api/stock-pool',
                                 data=json.dumps(stock_data),
                                 content_type='application/json')
            assert response.status_code == 201
            stock_ids.append(response.get_json()['data']['id'])
        
        # 2. 验证待观测池有3只股票
        response = client.get('/api/stock-pool/watch')
        assert response.status_code == 200
        watch_pool = response.get_json()['data']
        assert watch_pool['total'] == 3
        
        # 3. 批量移动前两只股票到待买入池
        batch_move_data = {
            'stock_ids': stock_ids[:2],
            'new_pool_type': 'buy_ready',
            'reason': '批量移动到买入池'
        }
        
        response = client.post('/api/stock-pool/batch/move',
                             data=json.dumps(batch_move_data),
                             content_type='application/json')
        assert response.status_code == 200
        move_result = response.get_json()['data']
        assert len(move_result['success']) == 2
        assert len(move_result['failed']) == 0
        
        # 4. 验证池状态
        # 待观测池应该只剩1只股票
        response = client.get('/api/stock-pool/watch')
        assert response.status_code == 200
        watch_pool = response.get_json()['data']
        assert watch_pool['total'] == 1
        
        # 待买入池应该有2只股票
        response = client.get('/api/stock-pool/buy-ready')
        assert response.status_code == 200
        buy_ready_pool = response.get_json()['data']
        assert buy_ready_pool['total'] == 2
        
        # 5. 批量移除待买入池的股票
        buy_ready_stock_ids = [item['id'] for item in buy_ready_pool['items']]
        batch_remove_data = {
            'stock_ids': buy_ready_stock_ids,
            'reason': '批量清理'
        }
        
        response = client.post('/api/stock-pool/batch/remove',
                             data=json.dumps(batch_remove_data),
                             content_type='application/json')
        assert response.status_code == 200
        remove_result = response.get_json()['data']
        assert len(remove_result['success']) == 2
        assert len(remove_result['failed']) == 0
        
        # 6. 验证待买入池为空
        response = client.get('/api/stock-pool/buy-ready')
        assert response.status_code == 200
        buy_ready_pool = response.get_json()['data']
        assert buy_ready_pool['total'] == 0
        
        # 7. 验证统计信息
        response = client.get('/api/stock-pool/stats')
        assert response.status_code == 200
        stats = response.get_json()['data']
        assert stats['totals']['active'] == 1  # 只剩待观测池的1只股票
        assert stats['totals']['moved'] == 2   # 2只股票被移动过
        assert stats['totals']['removed'] == 2 # 2只股票被移除
    
    def test_search_and_filter_workflow(self, client, db_session):
        """测试搜索和筛选工作流程"""
        # 1. 创建不同类型的测试数据
        test_stocks = [
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'pool_type': 'watch',
                'target_price': 12.50,
                'add_reason': '银行股技术面良好'
            },
            {
                'stock_code': '000002',
                'stock_name': '万科A',
                'pool_type': 'watch',
                'target_price': 25.00,
                'add_reason': '地产股基本面改善'
            },
            {
                'stock_code': '000858',
                'stock_name': '五粮液',
                'pool_type': 'buy_ready',
                'target_price': 180.00,
                'add_reason': '白酒行业复苏'
            }
        ]
        
        for stock_data in test_stocks:
            response = client.post('/api/stock-pool',
                                 data=json.dumps(stock_data),
                                 content_type='application/json')
            assert response.status_code == 201
        
        # 2. 按股票代码搜索
        response = client.get('/api/stock-pool?stock_code=000001')
        assert response.status_code == 200
        result = response.get_json()['data']
        assert result['total'] == 1
        assert result['items'][0]['stock_code'] == '000001'
        
        # 3. 按股票名称搜索
        response = client.get('/api/stock-pool?stock_name=平安')
        assert response.status_code == 200
        result = response.get_json()['data']
        assert result['total'] == 1
        assert result['items'][0]['stock_name'] == '平安银行'
        
        # 4. 按池类型筛选
        response = client.get('/api/stock-pool?pool_type=watch')
        assert response.status_code == 200
        result = response.get_json()['data']
        assert result['total'] == 2
        for item in result['items']:
            assert item['pool_type'] == 'watch'
        
        # 5. 按添加原因搜索
        response = client.get('/api/stock-pool?add_reason=技术面')
        assert response.status_code == 200
        result = response.get_json()['data']
        assert result['total'] == 1
        assert '技术面' in result['items'][0]['add_reason']
        
        # 6. 按目标价格范围筛选
        response = client.get('/api/stock-pool?min_target_price=20&max_target_price=200')
        assert response.status_code == 200
        result = response.get_json()['data']
        assert result['total'] == 2  # 万科A和五粮液
        for item in result['items']:
            assert 20 <= float(item['target_price']) <= 200
        
        # 7. 组合筛选条件
        response = client.get('/api/stock-pool?pool_type=watch&min_target_price=20')
        assert response.status_code == 200
        result = response.get_json()['data']
        assert result['total'] == 1
        assert result['items'][0]['stock_code'] == '000002'  # 万科A
        
        # 8. 测试分页
        response = client.get('/api/stock-pool?page=1&per_page=2')
        assert response.status_code == 200
        result = response.get_json()['data']
        assert result['total'] == 3
        assert len(result['items']) == 2
        assert result['current_page'] == 1
        assert result['has_next'] is True
        
        # 9. 测试排序
        response = client.get('/api/stock-pool?sort_by=target_price&sort_order=asc')
        assert response.status_code == 200
        result = response.get_json()['data']
        assert result['total'] == 3
        # 验证按目标价格升序排列
        prices = [float(item['target_price']) for item in result['items']]
        assert prices == sorted(prices)
    
    def test_error_handling_workflow(self, client, db_session):
        """测试错误处理工作流程"""
        # 1. 创建测试股票
        stock_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        response = client.post('/api/stock-pool',
                             data=json.dumps(stock_data),
                             content_type='application/json')
        assert response.status_code == 201
        stock_id = response.get_json()['data']['id']
        
        # 2. 尝试创建重复股票
        response = client.post('/api/stock-pool',
                             data=json.dumps(stock_data),
                             content_type='application/json')
        assert response.status_code == 400
        assert "已在" in response.get_json()['error']['message']
        
        # 3. 尝试移动到相同池
        move_data = {
            'new_pool_type': 'watch',
            'reason': '测试'
        }
        
        response = client.post(f'/api/stock-pool/{stock_id}/move',
                             data=json.dumps(move_data),
                             content_type='application/json')
        assert response.status_code == 400
        assert "已在" in response.get_json()['error']['message']
        
        # 4. 移动股票到买入池
        move_data = {
            'new_pool_type': 'buy_ready',
            'reason': '达到买入条件'
        }
        
        response = client.post(f'/api/stock-pool/{stock_id}/move',
                             data=json.dumps(move_data),
                             content_type='application/json')
        assert response.status_code == 200
        
        # 5. 尝试移动已移动的股票
        response = client.post(f'/api/stock-pool/{stock_id}/move',
                             data=json.dumps(move_data),
                             content_type='application/json')
        assert response.status_code == 400
        assert "只能移动活跃状态的股票" in response.get_json()['error']['message']
        
        # 6. 尝试操作不存在的股票
        response = client.get('/api/stock-pool/99999')
        assert response.status_code == 404
        
        response = client.post('/api/stock-pool/99999/move',
                             data=json.dumps(move_data),
                             content_type='application/json')
        assert response.status_code == 404
        
        # 7. 测试无效的请求数据
        invalid_data = {
            'stock_code': '000002',
            'stock_name': '万科A',
            'pool_type': 'invalid_pool'  # 无效的池类型
        }
        
        response = client.post('/api/stock-pool',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        assert response.status_code == 400
        
        # 8. 测试批量操作中的部分失败
        batch_data = {
            'stock_ids': [99999, 99998],  # 不存在的ID
            'new_pool_type': 'buy_ready',
            'reason': '测试'
        }
        
        response = client.post('/api/stock-pool/batch/move',
                             data=json.dumps(batch_data),
                             content_type='application/json')
        assert response.status_code == 200
        result = response.get_json()['data']
        assert len(result['success']) == 0
        assert len(result['failed']) == 2
    
    def test_concurrent_operations(self, client, db_session):
        """测试并发操作"""
        # 创建测试股票
        stock_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        response = client.post('/api/stock-pool',
                             data=json.dumps(stock_data),
                             content_type='application/json')
        assert response.status_code == 201
        stock_id = response.get_json()['data']['id']
        
        # 模拟并发移动操作（第二个应该失败）
        move_data = {
            'new_pool_type': 'buy_ready',
            'reason': '并发测试'
        }
        
        # 第一次移动应该成功
        response1 = client.post(f'/api/stock-pool/{stock_id}/move',
                               data=json.dumps(move_data),
                               content_type='application/json')
        assert response1.status_code == 200
        
        # 第二次移动应该失败（股票已经不是活跃状态）
        response2 = client.post(f'/api/stock-pool/{stock_id}/move',
                               data=json.dumps(move_data),
                               content_type='application/json')
        assert response2.status_code == 400
        assert "只能移动活跃状态的股票" in response2.get_json()['error']['message']