"""
股票池API测试
"""
import pytest
import json
from datetime import datetime
from models.stock_pool import StockPool


class TestStockPoolAPI:
    """股票池API测试类"""
    
    def test_create_stock_pool_entry_success(self, client, db_session):
        """测试成功创建股票池条目"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'target_price': 12.50,
            'add_reason': '技术面良好'
        }
        
        response = client.post('/api/stock-pool', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 201
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['stock_code'] == '000001'
        assert result['data']['pool_type'] == 'watch'
        assert result['data']['status'] == 'active'
    
    def test_create_stock_pool_entry_missing_fields(self, client, db_session):
        """测试创建股票池条目缺少必填字段"""
        data = {
            'stock_code': '000001',
            # 缺少stock_name和pool_type
        }
        
        response = client.post('/api/stock-pool',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert result['success'] is False
    
    def test_create_stock_pool_entry_duplicate(self, client, db_session):
        """测试创建重复股票池条目"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        # 创建第一个条目
        response1 = client.post('/api/stock-pool',
                               data=json.dumps(data),
                               content_type='application/json')
        assert response1.status_code == 201
        
        # 尝试创建重复条目
        response2 = client.post('/api/stock-pool',
                               data=json.dumps(data),
                               content_type='application/json')
        assert response2.status_code == 400
        result = response2.get_json()
        assert result['success'] is False
        assert "已在" in result['error']['message']
    
    def test_get_stock_pool_list(self, client, db_session):
        """测试获取股票池列表"""
        # 创建测试数据
        stock1 = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock2 = StockPool(
            stock_code='000002',
            stock_name='万科A',
            pool_type='buy_ready',
            add_reason='达到买入条件'
        )
        stock1.save()
        stock2.save()
        
        response = client.get('/api/stock-pool')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['total'] == 2
        assert len(result['data']['items']) == 2
    
    def test_get_stock_pool_list_with_filters(self, client, db_session):
        """测试带筛选条件获取股票池列表"""
        # 创建测试数据
        stock1 = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock2 = StockPool(
            stock_code='000002',
            stock_name='万科A',
            pool_type='buy_ready',
            add_reason='达到买入条件'
        )
        stock1.save()
        stock2.save()
        
        # 按池类型筛选
        response = client.get('/api/stock-pool?pool_type=watch')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['total'] == 1
        assert result['data']['items'][0]['pool_type'] == 'watch'
    
    def test_get_stock_pool_list_with_pagination(self, client, db_session):
        """测试分页获取股票池列表"""
        # 创建多个测试数据
        for i in range(5):
            stock = StockPool(
                stock_code=f'00000{i+1}',
                stock_name=f'股票{i+1}',
                pool_type='watch',
                add_reason='技术面良好'
            )
            stock.save()
        
        response = client.get('/api/stock-pool?page=1&per_page=3')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['total'] == 5
        assert len(result['data']['items']) == 3
        assert result['data']['current_page'] == 1
        assert result['data']['has_next'] is True
    
    def test_get_stock_pool_entry(self, client, db_session):
        """测试获取单个股票池条目"""
        stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock.save()
        
        response = client.get(f'/api/stock-pool/{stock.id}')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['stock_code'] == '000001'
    
    def test_get_stock_pool_entry_not_found(self, client, db_session):
        """测试获取不存在的股票池条目"""
        response = client.get('/api/stock-pool/99999')
        
        assert response.status_code == 404
        result = response.get_json()
        assert result['success'] is False
    
    def test_update_stock_pool_entry(self, client, db_session):
        """测试更新股票池条目"""
        stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock.save()
        
        update_data = {
            'target_price': 15.00,
            'add_reason': '更新后的原因'
        }
        
        response = client.put(f'/api/stock-pool/{stock.id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert float(result['data']['target_price']) == 15.00
        assert result['data']['add_reason'] == '更新后的原因'
    
    def test_delete_stock_pool_entry(self, client, db_session):
        """测试删除股票池条目"""
        stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock.save()
        
        response = client.delete(f'/api/stock-pool/{stock.id}')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        
        # 验证记录已删除
        deleted_stock = StockPool.query.get(stock.id)
        assert deleted_stock is None
    
    def test_get_watch_pool(self, client, db_session):
        """测试获取待观测池"""
        # 创建测试数据
        watch_stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        buy_ready_stock = StockPool(
            stock_code='000002',
            stock_name='万科A',
            pool_type='buy_ready',
            add_reason='达到买入条件'
        )
        watch_stock.save()
        buy_ready_stock.save()
        
        response = client.get('/api/stock-pool/watch')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['total'] == 1
        assert result['data']['items'][0]['pool_type'] == 'watch'
    
    def test_get_buy_ready_pool(self, client, db_session):
        """测试获取待买入池"""
        # 创建测试数据
        watch_stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        buy_ready_stock = StockPool(
            stock_code='000002',
            stock_name='万科A',
            pool_type='buy_ready',
            add_reason='达到买入条件'
        )
        watch_stock.save()
        buy_ready_stock.save()
        
        response = client.get('/api/stock-pool/buy-ready')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['total'] == 1
        assert result['data']['items'][0]['pool_type'] == 'buy_ready'
    
    def test_move_stock_to_pool_success(self, client, db_session):
        """测试成功移动股票到另一个池"""
        stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock.save()
        
        move_data = {
            'new_pool_type': 'buy_ready',
            'reason': '达到买入条件'
        }
        
        response = client.post(f'/api/stock-pool/{stock.id}/move',
                             data=json.dumps(move_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['pool_type'] == 'buy_ready'
        assert result['data']['status'] == 'active'
        
        # 验证原记录状态
        db_session.refresh(stock)
        assert stock.status == 'moved'
    
    def test_move_stock_to_pool_missing_data(self, client, db_session):
        """测试移动股票缺少必要数据"""
        stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock.save()
        
        move_data = {}  # 缺少new_pool_type
        
        response = client.post(f'/api/stock-pool/{stock.id}/move',
                             data=json.dumps(move_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert result['success'] is False
    
    def test_move_stock_to_invalid_pool(self, client, db_session):
        """测试移动股票到无效池类型"""
        stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock.save()
        
        move_data = {
            'new_pool_type': 'invalid_pool',
            'reason': '测试'
        }
        
        response = client.post(f'/api/stock-pool/{stock.id}/move',
                             data=json.dumps(move_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert result['success'] is False
    
    def test_remove_stock_from_pool_success(self, client, db_session):
        """测试成功从池中移除股票"""
        stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock.save()
        
        remove_data = {
            'reason': '不再关注'
        }
        
        response = client.post(f'/api/stock-pool/{stock.id}/remove',
                             data=json.dumps(remove_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['status'] == 'removed'
    
    def test_remove_stock_from_pool_without_reason(self, client, db_session):
        """测试移除股票不提供原因"""
        stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock.save()
        
        response = client.post(f'/api/stock-pool/{stock.id}/remove',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['status'] == 'removed'
    
    def test_batch_move_stocks_success(self, client, db_session):
        """测试批量移动股票成功"""
        # 创建多个股票
        stocks = []
        for i in range(3):
            stock = StockPool(
                stock_code=f'00000{i+1}',
                stock_name=f'股票{i+1}',
                pool_type='watch',
                add_reason='技术面良好'
            )
            stock.save()
            stocks.append(stock)
        
        batch_data = {
            'stock_ids': [stock.id for stock in stocks],
            'new_pool_type': 'buy_ready',
            'reason': '批量移动测试'
        }
        
        response = client.post('/api/stock-pool/batch/move',
                             data=json.dumps(batch_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert len(result['data']['success']) == 3
        assert len(result['data']['failed']) == 0
    
    def test_batch_move_stocks_partial_failure(self, client, db_session):
        """测试批量移动股票部分失败"""
        stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock.save()
        
        batch_data = {
            'stock_ids': [stock.id, 99999],  # 包含不存在的ID
            'new_pool_type': 'buy_ready',
            'reason': '批量移动测试'
        }
        
        response = client.post('/api/stock-pool/batch/move',
                             data=json.dumps(batch_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert len(result['data']['success']) == 1
        assert len(result['data']['failed']) == 1
    
    def test_batch_remove_stocks_success(self, client, db_session):
        """测试批量移除股票成功"""
        # 创建多个股票
        stocks = []
        for i in range(3):
            stock = StockPool(
                stock_code=f'00000{i+1}',
                stock_name=f'股票{i+1}',
                pool_type='watch',
                add_reason='技术面良好'
            )
            stock.save()
            stocks.append(stock)
        
        batch_data = {
            'stock_ids': [stock.id for stock in stocks],
            'reason': '批量移除测试'
        }
        
        response = client.post('/api/stock-pool/batch/remove',
                             data=json.dumps(batch_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert len(result['data']['success']) == 3
        assert len(result['data']['failed']) == 0
    
    def test_get_stock_history(self, client, db_session):
        """测试获取股票流转历史"""
        # 创建初始记录
        stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        stock.save()
        
        # 移动到另一个池
        move_data = {
            'new_pool_type': 'buy_ready',
            'reason': '达到买入条件'
        }
        client.post(f'/api/stock-pool/{stock.id}/move',
                   data=json.dumps(move_data),
                   content_type='application/json')
        
        # 获取历史记录
        response = client.get('/api/stock-pool/history/000001')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['stock_code'] == '000001'
        assert len(result['data']['history']) == 2
        # 最新记录应该是buy_ready池的
        assert result['data']['history'][0]['pool_type'] == 'buy_ready'
        assert result['data']['history'][0]['status'] == 'active'
    
    def test_get_stock_pool_stats(self, client, db_session):
        """测试获取股票池统计"""
        # 创建测试数据
        watch_stock = StockPool(
            stock_code='000001',
            stock_name='平安银行',
            pool_type='watch',
            add_reason='技术面良好'
        )
        buy_ready_stock = StockPool(
            stock_code='000002',
            stock_name='万科A',
            pool_type='buy_ready',
            add_reason='达到买入条件'
        )
        watch_stock.save()
        buy_ready_stock.save()
        
        response = client.get('/api/stock-pool/stats')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'pool_stats' in result['data']
        assert 'totals' in result['data']
        assert result['data']['totals']['active'] == 2