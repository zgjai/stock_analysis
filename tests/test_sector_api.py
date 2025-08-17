"""
板块分析API测试
"""
import pytest
import json
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd
from models.sector_data import SectorData, SectorRanking


class TestSectorAPI:
    """板块分析API测试类"""
    
    @pytest.fixture
    def sample_sector_data(self, db_session):
        """创建测试用的板块数据"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        sectors = [
            SectorData(
                sector_name='电子信息',
                sector_code='BK0727',
                change_percent=5.23,
                record_date=today,
                rank_position=1,
                volume=1000000,
                market_cap=500000000.0
            ),
            SectorData(
                sector_name='新能源汽车',
                sector_code='BK0733',
                change_percent=3.45,
                record_date=today,
                rank_position=2,
                volume=800000,
                market_cap=400000000.0
            ),
            SectorData(
                sector_name='医疗器械',
                sector_code='BK0726',
                change_percent=2.10,
                record_date=today,
                rank_position=3,
                volume=600000,
                market_cap=300000000.0
            ),
            # 昨天的数据
            SectorData(
                sector_name='电子信息',
                change_percent=4.56,
                record_date=yesterday,
                rank_position=1
            ),
            SectorData(
                sector_name='医疗器械',
                change_percent=3.21,
                record_date=yesterday,
                rank_position=2
            )
        ]
        
        for sector in sectors:
            db_session.add(sector)
        db_session.commit()
        
        return sectors
    
    @pytest.fixture
    def mock_akshare_data(self):
        """模拟AKShare返回的数据"""
        return pd.DataFrame({
            '板块名称': ['电子信息', '新能源汽车', '医疗器械'],
            '板块代码': ['BK0727', 'BK0733', 'BK0726'],
            '涨跌幅': [5.23, 3.45, 2.10],
            '成交量': [1000000, 800000, 600000],
            '总市值': [500000000.0, 400000000.0, 300000000.0]
        })
    
    def test_refresh_sector_data_success(self, client, mock_akshare_data, db_session):
        """测试成功刷新板块数据"""
        with patch('akshare.stock_board_industry_name_em') as mock_ak:
            mock_ak.return_value = mock_akshare_data
            
            # 确保今日没有数据
            with patch.object(SectorData, 'has_data_for_date', return_value=False):
                response = client.post('/api/sectors/refresh')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['count'] == 3
            assert '成功获取并保存3条板块数据' in data['message']
    
    def test_refresh_sector_data_already_exists(self, client, db_session):
        """测试数据已存在时的处理"""
        with patch.object(SectorData, 'has_data_for_date', return_value=True):
            response = client.post('/api/sectors/refresh')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['count'] == 0
        assert '今日数据已存在' in data['message']
    
    def test_refresh_sector_data_akshare_error(self, client, db_session):
        """测试AKShare API错误"""
        with patch('akshare.stock_board_industry_name_em') as mock_ak:
            mock_ak.side_effect = Exception("API调用失败")
            
            with patch.object(SectorData, 'has_data_for_date', return_value=False):
                response = client.post('/api/sectors/refresh')
            
            assert response.status_code == 503
            data = response.get_json()
            assert data['success'] is False
            assert data['error']['code'] == 'EXTERNAL_API_ERROR'
    
    def test_get_sector_ranking_default(self, client, sample_sector_data):
        """测试获取默认板块排名"""
        response = client.get('/api/sectors/ranking')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 3
        assert data['data'][0]['sector_name'] == '电子信息'
        assert data['data'][0]['rank_position'] == 1
        assert data['meta']['count'] == 3
    
    def test_get_sector_ranking_with_date(self, client, sample_sector_data):
        """测试获取指定日期的板块排名"""
        today = date.today()
        response = client.get(f'/api/sectors/ranking?date={today.isoformat()}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 3
        assert data['meta']['date'] == today.isoformat()
    
    def test_get_sector_ranking_with_limit(self, client, sample_sector_data):
        """测试限制返回数量"""
        response = client.get('/api/sectors/ranking?limit=2')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2
        assert data['meta']['limit'] == 2
    
    def test_get_sector_ranking_invalid_date(self, client):
        """测试无效日期格式"""
        response = client.get('/api/sectors/ranking?date=invalid-date')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_get_sector_ranking_invalid_limit(self, client):
        """测试无效限制数量"""
        response = client.get('/api/sectors/ranking?limit=-1')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_get_sector_history_success(self, client, sample_sector_data):
        """测试获取板块历史表现"""
        response = client.get('/api/sectors/history?sector_name=电子信息&days=7')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2  # 今天和昨天的数据
        assert data['meta']['sector_name'] == '电子信息'
        assert data['meta']['days'] == 7
    
    def test_get_sector_history_missing_name(self, client):
        """测试缺少板块名称"""
        response = client.get('/api/sectors/history?days=7')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert '板块名称不能为空' in data['error']['message']
    
    def test_get_sector_history_invalid_days(self, client):
        """测试无效天数"""
        response = client.get('/api/sectors/history?sector_name=电子信息&days=0')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_get_top_performers_default(self, client, sample_sector_data):
        """测试获取默认TOPK板块"""
        response = client.get('/api/sectors/top-performers')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 2  # 至少有电子信息和医疗器械
        assert data['meta']['days'] == 30
        assert data['meta']['top_k'] == 10
        
        # 检查数据结构
        if data['data']:
            performer = data['data'][0]
            assert 'sector_name' in performer
            assert 'appearances' in performer
            assert 'avg_rank' in performer
            assert 'best_rank' in performer
            assert 'trend' in performer
            assert 'frequency_rate' in performer
    
    def test_get_top_performers_custom_params(self, client, sample_sector_data):
        """测试自定义参数的TOPK板块"""
        response = client.get('/api/sectors/top-performers?days=7&top_k=5')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['meta']['days'] == 7
        assert data['meta']['top_k'] == 5
    
    def test_get_top_performers_invalid_params(self, client):
        """测试无效参数"""
        response = client.get('/api/sectors/top-performers?days=0&top_k=10')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_get_analysis_summary_default(self, client, sample_sector_data):
        """测试获取默认分析汇总"""
        response = client.get('/api/sectors/summary')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        summary = data['data']
        assert summary['period_days'] == 30
        assert summary['total_records'] == 5  # 3个今天的 + 2个昨天的
        assert summary['unique_sectors'] == 3
        assert summary['data_days'] == 2  # 今天和昨天
        assert 'avg_change_percent' in summary
        assert 'max_change_percent' in summary
        assert 'min_change_percent' in summary
        assert 'data_completeness' in summary
    
    def test_get_analysis_summary_custom_days(self, client, sample_sector_data):
        """测试自定义天数的分析汇总"""
        response = client.get('/api/sectors/summary?days=7')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['period_days'] == 7
    
    def test_get_analysis_summary_invalid_days(self, client):
        """测试无效天数"""
        response = client.get('/api/sectors/summary?days=-1')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_get_available_dates_default(self, client, sample_sector_data):
        """测试获取默认可用日期"""
        response = client.get('/api/sectors/dates')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2  # 今天和昨天
        assert data['meta']['count'] == 2
        assert data['meta']['limit'] == 30
        
        # 检查日期格式和排序（最新的在前）
        dates = data['data']
        today = date.today()
        yesterday = today - timedelta(days=1)
        assert dates[0] == today.isoformat()
        assert dates[1] == yesterday.isoformat()
    
    def test_get_available_dates_custom_limit(self, client, sample_sector_data):
        """测试自定义限制的可用日期"""
        response = client.get('/api/sectors/dates?limit=1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['meta']['limit'] == 1
    
    def test_get_available_dates_invalid_limit(self, client):
        """测试无效限制数量"""
        response = client.get('/api/sectors/dates?limit=0')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_delete_sector_data_success(self, client, sample_sector_data, db_session):
        """测试成功删除板块数据"""
        today = date.today()
        
        # 添加排名数据
        ranking = SectorRanking(
            record_date=today,
            total_sectors=3
        )
        ranking.ranking_list = [{'rank': 1, 'sector_name': '电子信息'}]
        db_session.add(ranking)
        db_session.commit()
        
        response = client.delete(f'/api/sectors/data/{today.isoformat()}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['deleted_sectors'] == 3
        assert data['data']['deleted_rankings'] == 1
        
        # 验证数据已删除
        remaining_sectors = SectorData.query.filter_by(record_date=today).count()
        remaining_rankings = SectorRanking.query.filter_by(record_date=today).count()
        
        assert remaining_sectors == 0
        assert remaining_rankings == 0
    
    def test_delete_sector_data_invalid_date(self, client):
        """测试删除无效日期的数据"""
        response = client.delete('/api/sectors/data/invalid-date')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_delete_sector_data_nonexistent(self, client):
        """测试删除不存在的数据"""
        future_date = date.today() + timedelta(days=30)
        response = client.delete(f'/api/sectors/data/{future_date.isoformat()}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['deleted_sectors'] == 0
        assert data['data']['deleted_rankings'] == 0
    
    def test_api_error_handlers(self, client):
        """测试API错误处理"""
        # 测试404
        response = client.get('/api/sectors/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'NOT_FOUND'
        
        # 测试405
        response = client.patch('/api/sectors/refresh')
        assert response.status_code == 405
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'METHOD_NOT_ALLOWED'