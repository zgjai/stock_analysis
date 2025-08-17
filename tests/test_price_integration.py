"""
股票价格服务集成测试
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
import pandas as pd

from models.stock_price import StockPrice
from services.price_service import PriceService


class TestPriceIntegration:
    """价格服务集成测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.price_service = PriceService()
        self.test_stock_codes = ['000001', '000002', '600000']
        self.today = date.today()
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_complete_price_workflow(self, mock_akshare, client):
        """测试完整的价格服务工作流程"""
        # 模拟AKShare返回数据
        mock_df = pd.DataFrame({
            '代码': self.test_stock_codes,
            '名称': ['平安银行', '万科A', '浦发银行'],
            '最新价': [12.5, 20.0, 8.5],
            '涨跌幅': [2.5, 1.0, -1.5]
        })
        mock_akshare.return_value = mock_df
        
        # 1. 批量刷新股票价格
        response = client.post('/api/prices/refresh', 
                             json={'stock_codes': self.test_stock_codes})
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['success_count'] == 3
        
        # 2. 验证数据库中的记录
        for stock_code in self.test_stock_codes:
            price_record = StockPrice.get_price_by_date(stock_code, self.today)
            assert price_record is not None
            assert price_record.stock_code == stock_code
        
        # 3. 获取单个股票价格
        response = client.get(f'/api/prices/{self.test_stock_codes[0]}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['stock_code'] == self.test_stock_codes[0]
        assert data['data']['current_price'] == 12.5
        
        # 4. 获取最新价格
        response = client.get(f'/api/prices/{self.test_stock_codes[0]}/latest')
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['current_price'] == 12.5
        
        # 5. 批量获取价格
        response = client.post('/api/prices/batch', 
                             json={'stock_codes': self.test_stock_codes})
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 3
        for result in data['data']:
            assert result['success'] is True
        
        # 6. 检查缓存状态
        response = client.post('/api/prices/cache/status', 
                             json={'stock_codes': self.test_stock_codes})
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['cached_today'] == 3
        assert data['data']['need_refresh'] == 0
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_cache_mechanism(self, mock_akshare, client):
        """测试缓存机制"""
        stock_code = self.test_stock_codes[0]
        
        # 模拟AKShare返回数据
        mock_df = pd.DataFrame({
            '代码': [stock_code],
            '名称': ['平安银行'],
            '最新价': [12.5],
            '涨跌幅': [2.5]
        })
        mock_akshare.return_value = mock_df
        
        # 1. 首次刷新，应该调用AKShare
        response = client.post('/api/prices/refresh', 
                             json={'stock_codes': [stock_code]})
        assert response.status_code == 200
        data = response.get_json()
        assert data['from_cache'] is False
        mock_akshare.assert_called_once()
        
        # 2. 再次刷新（不强制），应该使用缓存
        mock_akshare.reset_mock()
        response = client.post('/api/prices/refresh', 
                             json={'stock_codes': [stock_code]})
        assert response.status_code == 200
        data = response.get_json()
        assert data['from_cache'] is True
        mock_akshare.assert_not_called()
        
        # 3. 强制刷新，应该调用AKShare
        mock_akshare.reset_mock()
        response = client.post('/api/prices/refresh', 
                             json={
                                 'stock_codes': [stock_code],
                                 'force_refresh': True
                             })
        assert response.status_code == 200
        data = response.get_json()
        assert data['from_cache'] is False
        mock_akshare.assert_called_once()
    
    def test_price_history_and_cleanup(self, client):
        """测试价格历史和清理功能"""
        stock_code = self.test_stock_codes[0]
        
        # 创建多天的价格记录
        for i in range(10):
            price_date = self.today - timedelta(days=i)
            price_record = StockPrice(
                stock_code=stock_code,
                stock_name='平安银行',
                current_price=10.0 + i * 0.1,
                change_percent=i * 0.1,
                record_date=price_date
            )
            price_record.save()
        
        # 1. 获取价格历史
        response = client.get(f'/api/prices/{stock_code}/history?days=5')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 5
        
        # 验证按日期倒序排列
        dates = [item['record_date'] for item in data['data']]
        assert dates == sorted(dates, reverse=True)
        
        # 2. 清理旧数据
        response = client.post('/api/prices/cache/cleanup', 
                             json={'days_to_keep': 7})
        assert response.status_code == 200
        data = response.get_json()
        assert data['deleted_count'] == 3  # 删除8、9、10天前的数据
        
        # 3. 验证清理结果
        response = client.get(f'/api/prices/{stock_code}/history?days=10')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 7  # 只剩7天的数据
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_error_handling_and_recovery(self, mock_akshare, client):
        """测试错误处理和恢复"""
        stock_codes = ['000001', 'INVALID', '000002']
        
        # 模拟AKShare返回部分数据（缺少INVALID股票）
        mock_df = pd.DataFrame({
            '代码': ['000001', '000002'],
            '名称': ['平安银行', '万科A'],
            '最新价': [12.5, 20.0],
            '涨跌幅': [2.5, 1.0]
        })
        mock_akshare.return_value = mock_df
        
        # 1. 批量刷新，部分成功
        response = client.post('/api/prices/refresh', 
                             json={'stock_codes': stock_codes})
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['success_count'] == 2
        assert data['data']['failed_count'] == 1
        
        # 2. 验证成功的记录被保存
        assert StockPrice.get_price_by_date('000001', self.today) is not None
        assert StockPrice.get_price_by_date('000002', self.today) is not None
        
        # 3. 验证失败的记录没有被保存
        assert StockPrice.get_price_by_date('INVALID', self.today) is None
        
        # 4. 批量获取价格，部分成功
        response = client.post('/api/prices/batch', 
                             json={'stock_codes': stock_codes})
        assert response.status_code == 200
        data = response.get_json()
        
        results = {result['stock_code']: result for result in data['data']}
        assert results['000001']['success'] is True
        assert results['000002']['success'] is True
        assert results['INVALID']['success'] is False
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_akshare_api_failure(self, mock_akshare, client):
        """测试AKShare API调用失败"""
        stock_code = self.test_stock_codes[0]
        
        # 模拟AKShare API异常
        mock_akshare.side_effect = Exception("网络连接失败")
        
        # 尝试刷新价格
        response = client.post('/api/prices/refresh', 
                             json={'stock_codes': [stock_code]})
        
        # 应该返回外部API错误
        assert response.status_code == 503
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'EXTERNAL_API_ERROR'
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_data_consistency(self, mock_akshare, client):
        """测试数据一致性"""
        stock_code = self.test_stock_codes[0]
        
        # 模拟AKShare返回数据
        mock_df = pd.DataFrame({
            '代码': [stock_code],
            '名称': ['平安银行'],
            '最新价': [12.5],
            '涨跌幅': [2.5]
        })
        mock_akshare.return_value = mock_df
        
        # 1. 刷新价格
        response = client.post('/api/prices/refresh', 
                             json={'stock_codes': [stock_code]})
        assert response.status_code == 200
        
        # 2. 通过不同API获取价格，应该返回相同数据
        # 获取特定日期价格
        response1 = client.get(f'/api/prices/{stock_code}?date={self.today.isoformat()}')
        assert response1.status_code == 200
        data1 = response1.get_json()
        
        # 获取最新价格
        response2 = client.get(f'/api/prices/{stock_code}/latest')
        assert response2.status_code == 200
        data2 = response2.get_json()
        
        # 批量获取价格
        response3 = client.post('/api/prices/batch', 
                              json={'stock_codes': [stock_code]})
        assert response3.status_code == 200
        data3 = response3.get_json()
        
        # 验证数据一致性
        assert data1['data']['current_price'] == data2['data']['current_price']
        assert data2['data']['current_price'] == data3['data'][0]['data']['current_price']
        assert data1['data']['change_percent'] == data2['data']['change_percent']
        assert data2['data']['change_percent'] == data3['data'][0]['data']['change_percent']
    
    def test_date_deduplication(self, client):
        """测试日期去重功能"""
        stock_code = self.test_stock_codes[0]
        
        # 手动创建今日价格记录
        original_price = StockPrice(
            stock_code=stock_code,
            stock_name='平安银行',
            current_price=10.0,
            change_percent=0.0,
            record_date=self.today
        )
        original_price.save()
        original_id = original_price.id
        
        # 使用update_or_create更新同一天的记录
        updated_price = StockPrice.update_or_create(
            stock_code=stock_code,
            stock_name='平安银行',
            current_price=12.5,
            change_percent=2.5,
            record_date=self.today
        )
        
        # 验证记录被更新而不是创建新记录
        assert updated_price.id == original_id
        assert updated_price.current_price == 12.5
        assert updated_price.change_percent == 2.5
        
        # 验证数据库中只有一条记录
        all_prices = StockPrice.query.filter_by(
            stock_code=stock_code, 
            record_date=self.today
        ).all()
        assert len(all_prices) == 1
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_concurrent_refresh_safety(self, mock_akshare, client):
        """测试并发刷新的安全性"""
        stock_code = self.test_stock_codes[0]
        
        # 模拟AKShare返回数据
        mock_df = pd.DataFrame({
            '代码': [stock_code],
            '名称': ['平安银行'],
            '最新价': [12.5],
            '涨跌幅': [2.5]
        })
        mock_akshare.return_value = mock_df
        
        # 模拟并发请求（虽然在测试中是顺序执行）
        responses = []
        for i in range(3):
            response = client.post('/api/prices/refresh', 
                                 json={'stock_codes': [stock_code]})
            responses.append(response)
        
        # 验证所有请求都成功
        for response in responses:
            assert response.status_code == 200
        
        # 验证数据库中只有一条今日记录
        all_prices = StockPrice.query.filter_by(
            stock_code=stock_code, 
            record_date=self.today
        ).all()
        assert len(all_prices) == 1