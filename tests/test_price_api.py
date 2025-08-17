"""
股票价格API测试
"""
import pytest
import json
from unittest.mock import patch
from datetime import date, timedelta

from models.stock_price import StockPrice


class TestPriceAPI:
    """价格API测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_stock_code = '000001'
        self.test_stock_name = '平安银行'
        self.test_price = 12.50
        self.test_change_percent = 2.5
        self.today = date.today()
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_refresh_prices_single_stock_success(self, mock_akshare, client):
        """测试刷新单个股票价格成功"""
        import pandas as pd
        
        # 模拟AKShare返回数据
        mock_df = pd.DataFrame({
            '代码': [self.test_stock_code],
            '名称': [self.test_stock_name],
            '最新价': [self.test_price],
            '涨跌幅': [self.test_change_percent]
        })
        mock_akshare.return_value = mock_df
        
        # 发送请求
        response = client.post('/api/prices/refresh', 
                             json={'stock_codes': [self.test_stock_code]})
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == '价格刷新成功'
        assert data['from_cache'] is False
        assert data['data']['stock_code'] == self.test_stock_code
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_refresh_prices_multiple_stocks_success(self, mock_akshare, client):
        """测试批量刷新股票价格成功"""
        import pandas as pd
        
        stock_codes = ['000001', '000002']
        
        # 模拟AKShare返回数据
        mock_df = pd.DataFrame({
            '代码': stock_codes,
            '名称': ['平安银行', '万科A'],
            '最新价': [12.5, 20.0],
            '涨跌幅': [2.5, 1.0]
        })
        mock_akshare.return_value = mock_df
        
        # 发送请求
        response = client.post('/api/prices/refresh', 
                             json={'stock_codes': stock_codes})
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert '批量刷新完成' in data['message']
        assert data['data']['success_count'] == 2
        assert data['data']['failed_count'] == 0
    
    def test_refresh_prices_no_stock_codes(self, client):
        """测试刷新价格时未提供股票代码"""
        response = client.post('/api/prices/refresh', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert '请提供股票代码列表' in data['error']['message']
    
    def test_refresh_prices_invalid_stock_code(self, client):
        """测试刷新价格时股票代码无效"""
        response = client.post('/api/prices/refresh', 
                             json={'stock_codes': ['INVALID']})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_get_stock_price_success(self, client, db_session):
        """测试获取股票价格成功"""
        # 创建价格记录
        price_record = StockPrice(
            stock_code=self.test_stock_code,
            stock_name=self.test_stock_name,
            current_price=self.test_price,
            change_percent=self.test_change_percent,
            record_date=self.today
        )
        price_record.save()
        
        # 发送请求
        response = client.get(f'/api/prices/{self.test_stock_code}')
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['stock_code'] == self.test_stock_code
        assert data['data']['current_price'] == self.test_price
    
    def test_get_stock_price_with_date(self, client):
        """测试获取指定日期的股票价格"""
        target_date = self.today - timedelta(days=1)
        
        # 创建价格记录
        price_record = StockPrice(
            stock_code=self.test_stock_code,
            stock_name=self.test_stock_name,
            current_price=self.test_price,
            change_percent=self.test_change_percent,
            record_date=target_date
        )
        price_record.save()
        
        # 发送请求
        response = client.get(f'/api/prices/{self.test_stock_code}?date={target_date.isoformat()}')
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['record_date'] == target_date.isoformat()
    
    def test_get_stock_price_invalid_date_format(self, client):
        """测试获取股票价格时日期格式无效"""
        response = client.get(f'/api/prices/{self.test_stock_code}?date=invalid-date')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert '日期格式不正确' in data['error']['message']
    
    def test_get_stock_price_not_found(self, client):
        """测试获取不存在的股票价格"""
        response = client.get(f'/api/prices/{self.test_stock_code}')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'NOT_FOUND'
    
    def test_get_stock_price_invalid_code(self, client):
        """测试获取价格时股票代码无效"""
        response = client.get('/api/prices/INVALID')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_get_latest_price_success(self, client, db_session):
        """测试获取最新价格成功"""
        # 创建多个价格记录
        yesterday = self.today - timedelta(days=1)
        
        old_price = StockPrice(
            stock_code=self.test_stock_code,
            stock_name=self.test_stock_name,
            current_price=10.0,
            change_percent=0.0,
            record_date=yesterday
        )
        old_price.save()
        
        new_price = StockPrice(
            stock_code=self.test_stock_code,
            stock_name=self.test_stock_name,
            current_price=self.test_price,
            change_percent=self.test_change_percent,
            record_date=self.today
        )
        new_price.save()
        
        # 发送请求
        response = client.get(f'/api/prices/{self.test_stock_code}/latest')
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['current_price'] == self.test_price
        assert data['data']['record_date'] == self.today.isoformat()
    
    def test_get_latest_price_not_found(self, client):
        """测试获取不存在股票的最新价格"""
        response = client.get(f'/api/prices/{self.test_stock_code}/latest')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'NOT_FOUND'
    
    def test_get_price_history_success(self, client, db_session):
        """测试获取价格历史成功"""
        # 创建多个价格记录
        for i in range(5):
            price_date = self.today - timedelta(days=i)
            price_record = StockPrice(
                stock_code=self.test_stock_code,
                stock_name=self.test_stock_name,
                current_price=10.0 + i,
                change_percent=i,
                record_date=price_date
            )
            price_record.save()
        
        # 发送请求
        response = client.get(f'/api/prices/{self.test_stock_code}/history?days=3')
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 3
        # 应该按日期倒序排列
        assert data['data'][0]['record_date'] == self.today.isoformat()
    
    def test_get_price_history_invalid_days(self, client):
        """测试获取价格历史时天数无效"""
        response = client.get(f'/api/prices/{self.test_stock_code}/history?days=0')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert '天数必须大于0' in data['error']['message']
    
    def test_get_cache_status_success(self, client, db_session):
        """测试获取缓存状态成功"""
        stock_codes = ['000001', '000002']
        
        # 创建一个今日价格记录
        price_record = StockPrice(
            stock_code='000001',
            stock_name='平安银行',
            current_price=self.test_price,
            change_percent=self.test_change_percent,
            record_date=self.today
        )
        price_record.save()
        
        # 发送请求
        response = client.post('/api/prices/cache/status', 
                             json={'stock_codes': stock_codes})
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['total_stocks'] == 2
        assert data['data']['cached_today'] == 1
        assert data['data']['need_refresh'] == 1
    
    def test_get_cache_status_no_stock_codes(self, client):
        """测试获取缓存状态时未提供股票代码"""
        response = client.post('/api/prices/cache/status', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert '请提供股票代码列表' in data['error']['message']
    
    def test_cleanup_cache_success(self, client):
        """测试清理缓存成功"""
        # 创建旧价格记录
        old_date = self.today - timedelta(days=100)
        old_price = StockPrice(
            stock_code=self.test_stock_code,
            stock_name=self.test_stock_name,
            current_price=10.0,
            change_percent=0.0,
            record_date=old_date
        )
        old_price.save()
        
        # 发送请求
        response = client.post('/api/prices/cache/cleanup', 
                             json={'days_to_keep': 90})
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['deleted_count'] == 1
    
    def test_cleanup_cache_invalid_days(self, client):
        """测试清理缓存时天数无效"""
        response = client.post('/api/prices/cache/cleanup', 
                             json={'days_to_keep': 0})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert '保留天数必须大于0' in data['error']['message']
    
    def test_get_batch_prices_success(self, client, db_session):
        """测试批量获取股票价格成功"""
        stock_codes = ['000001', '000002']
        
        # 创建价格记录
        for i, code in enumerate(stock_codes):
            price_record = StockPrice(
                stock_code=code,
                stock_name=f'股票{i+1}',
                current_price=10.0 + i,
                change_percent=i,
                record_date=self.today
            )
            price_record.save()
        
        # 发送请求
        response = client.post('/api/prices/batch', 
                             json={'stock_codes': stock_codes})
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2
        
        # 验证每个结果
        for result in data['data']:
            assert result['success'] is True
            assert result['data'] is not None
    
    def test_get_batch_prices_with_date(self, client):
        """测试批量获取指定日期的股票价格"""
        target_date = self.today - timedelta(days=1)
        stock_codes = ['000001']
        
        # 创建价格记录
        price_record = StockPrice(
            stock_code=stock_codes[0],
            stock_name='平安银行',
            current_price=self.test_price,
            change_percent=self.test_change_percent,
            record_date=target_date
        )
        price_record.save()
        
        # 发送请求
        response = client.post('/api/prices/batch', 
                             json={
                                 'stock_codes': stock_codes,
                                 'date': target_date.isoformat()
                             })
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data'][0]['data']['record_date'] == target_date.isoformat()
    
    def test_get_batch_prices_no_stock_codes(self, client):
        """测试批量获取价格时未提供股票代码"""
        response = client.post('/api/prices/batch', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert '请提供股票代码列表' in data['error']['message']
    
    def test_get_batch_prices_invalid_date_format(self, client):
        """测试批量获取价格时日期格式无效"""
        response = client.post('/api/prices/batch', 
                             json={
                                 'stock_codes': ['000001'],
                                 'date': 'invalid-date'
                             })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert '日期格式不正确' in data['error']['message']
    
    def test_get_batch_prices_partial_success(self, client):
        """测试批量获取价格部分成功"""
        stock_codes = ['000001', 'NOTFOUND']
        
        # 只创建一个价格记录
        price_record = StockPrice(
            stock_code='000001',
            stock_name='平安银行',
            current_price=self.test_price,
            change_percent=self.test_change_percent,
            record_date=self.today
        )
        price_record.save()
        
        # 发送请求
        response = client.post('/api/prices/batch', 
                             json={'stock_codes': stock_codes})
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2
        
        # 验证结果
        results = {result['stock_code']: result for result in data['data']}
        assert results['000001']['success'] is True
        assert results['NOTFOUND']['success'] is False