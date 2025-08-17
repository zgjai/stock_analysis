"""
板块分析集成测试
"""
import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd
from models.sector_data import SectorData, SectorRanking
from services.sector_service import SectorAnalysisService


class TestSectorIntegration:
    """板块分析集成测试类"""
    
    @pytest.fixture
    def service(self):
        """获取服务类"""
        return SectorAnalysisService
    
    @pytest.fixture
    def mock_akshare_data(self):
        """模拟AKShare返回的完整数据"""
        return pd.DataFrame({
            '板块名称': [
                '电子信息', '新能源汽车', '医疗器械', '软件服务', '生物制药',
                '半导体', '光伏设备', '锂电池', '人工智能', '云计算'
            ],
            '板块代码': [
                'BK0727', 'BK0733', 'BK0726', 'BK0528', 'BK0456',
                'BK0512', 'BK0451', 'BK0732', 'BK0803', 'BK0739'
            ],
            '涨跌幅': [8.45, 6.23, 5.67, 4.89, 4.12, 3.78, 3.45, 2.98, 2.34, 1.87],
            '成交量': [
                2000000, 1800000, 1600000, 1400000, 1200000,
                1000000, 900000, 800000, 700000, 600000
            ],
            '总市值': [
                1000000000.0, 900000000.0, 800000000.0, 700000000.0, 600000000.0,
                500000000.0, 400000000.0, 350000000.0, 300000000.0, 250000000.0
            ]
        })
    
    def test_complete_sector_workflow(self, service, client, mock_akshare_data, db_session):
        """测试完整的板块分析工作流程"""
        
        # 1. 刷新板块数据
        with patch('akshare.stock_board_industry_name_em') as mock_ak:
            mock_ak.return_value = mock_akshare_data
            
            # API调用刷新数据
            response = client.post('/api/sectors/refresh')
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['count'] == 10
        
        # 2. 验证数据已正确保存
        today = date.today()
        sectors = SectorData.query.filter_by(record_date=today).all()
        assert len(sectors) == 10
        
        # 验证排名数据
        ranking = SectorRanking.query.filter_by(record_date=today).first()
        assert ranking is not None
        assert ranking.total_sectors == 10
        assert len(ranking.ranking_list) == 10
        
        # 3. 获取板块排名
        response = client.get('/api/sectors/ranking')
        assert response.status_code == 200
        
        ranking_data = response.get_json()
        assert len(ranking_data['data']) == 10
        assert ranking_data['data'][0]['sector_name'] == '电子信息'
        assert ranking_data['data'][0]['change_percent'] == 8.45
        
        # 4. 获取限制数量的排名
        response = client.get('/api/sectors/ranking?limit=5')
        assert response.status_code == 200
        
        limited_data = response.get_json()
        assert len(limited_data['data']) == 5
        
        # 5. 获取板块历史（目前只有一天数据）
        response = client.get('/api/sectors/history?sector_name=电子信息&days=7')
        assert response.status_code == 200
        
        history_data = response.get_json()
        assert len(history_data['data']) == 1
        assert history_data['data'][0]['sector_name'] == '电子信息'
        
        # 6. 获取分析汇总
        response = client.get('/api/sectors/summary')
        assert response.status_code == 200
        
        summary_data = response.get_json()
        summary = summary_data['data']
        assert summary['total_records'] == 10
        assert summary['unique_sectors'] == 10
        assert summary['data_days'] == 1
        assert summary['avg_change_percent'] > 0
        assert summary['max_change_percent'] == 8.45
        assert summary['min_change_percent'] == 1.87
        
        # 7. 获取可用日期
        response = client.get('/api/sectors/dates')
        assert response.status_code == 200
        
        dates_data = response.get_json()
        assert len(dates_data['data']) == 1
        assert dates_data['data'][0] == today.isoformat()
    
    def test_multi_day_top_performers_analysis(self, service, client, mock_akshare_data, db_session):
        """测试多天数据的TOPK板块分析"""
        
        # 创建多天的测试数据
        today = date.today()
        
        # 模拟3天的数据，每天板块排名有所变化
        test_data = [
            # 第1天 (今天)
            {
                'date': today,
                'sectors': [
                    ('电子信息', 8.45, 1), ('新能源汽车', 6.23, 2), ('医疗器械', 5.67, 3),
                    ('软件服务', 4.89, 4), ('生物制药', 4.12, 5), ('半导体', 3.78, 6)
                ]
            },
            # 第2天 (昨天)
            {
                'date': today - timedelta(days=1),
                'sectors': [
                    ('新能源汽车', 7.23, 1), ('电子信息', 6.45, 2), ('半导体', 5.67, 3),
                    ('医疗器械', 4.89, 4), ('软件服务', 4.12, 5), ('生物制药', 3.78, 6)
                ]
            },
            # 第3天 (前天)
            {
                'date': today - timedelta(days=2),
                'sectors': [
                    ('电子信息', 9.12, 1), ('半导体', 7.45, 2), ('新能源汽车', 6.78, 3),
                    ('生物制药', 5.23, 4), ('医疗器械', 4.56, 5), ('软件服务', 3.89, 6)
                ]
            }
        ]
        
        # 插入测试数据
        for day_data in test_data:
            for sector_name, change_percent, rank in day_data['sectors']:
                sector = SectorData(
                    sector_name=sector_name,
                    change_percent=change_percent,
                    record_date=day_data['date'],
                    rank_position=rank,
                    volume=1000000,
                    market_cap=500000000.0
                )
                db_session.add(sector)
        db_session.commit()
        
        # 测试TOPK板块统计
        response = client.get('/api/sectors/top-performers?days=3&top_k=3')
        assert response.status_code == 200
        
        top_data = response.get_json()
        performers = top_data['data']
        
        # 验证结果
        assert len(performers) >= 3
        
        # 电子信息应该排第一（3天都在前3，平均排名最好）
        electronics = next((p for p in performers if p['sector_name'] == '电子信息'), None)
        assert electronics is not None
        assert electronics['appearances'] == 3  # 3天都进入TOP3
        assert electronics['avg_rank'] <= 2.0  # 平均排名很好
        assert electronics['best_rank'] == 1   # 最好排名是第1
        
        # 新能源汽车也应该在列表中
        new_energy = next((p for p in performers if p['sector_name'] == '新能源汽车'), None)
        assert new_energy is not None
        assert new_energy['appearances'] == 3
        
        # 半导体也应该在列表中
        semiconductor = next((p for p in performers if p['sector_name'] == '半导体'), None)
        assert semiconductor is not None
        assert semiconductor['appearances'] >= 2  # 至少出现2次
    
    def test_sector_trend_analysis(self, service, client, db_session):
        """测试板块趋势分析"""
        
        # 创建趋势测试数据
        today = date.today()
        
        # 电子信息：上升趋势（排名从5上升到1）
        electronics_data = [
            (today, 1), (today - timedelta(days=1), 2),
            (today - timedelta(days=2), 3), (today - timedelta(days=3), 4),
            (today - timedelta(days=4), 5)
        ]
        
        # 新能源汽车：下降趋势（排名从1下降到5）
        new_energy_data = [
            (today, 5), (today - timedelta(days=1), 4),
            (today - timedelta(days=2), 3), (today - timedelta(days=3), 2),
            (today - timedelta(days=4), 1)
        ]
        
        # 医疗器械：稳定趋势（排名保持在3左右）
        medical_data = [
            (today, 3), (today - timedelta(days=1), 3),
            (today - timedelta(days=2), 3), (today - timedelta(days=3), 3),
            (today - timedelta(days=4), 3)
        ]
        
        # 插入数据
        for sector_name, data in [
            ('电子信息', electronics_data),
            ('新能源汽车', new_energy_data),
            ('医疗器械', medical_data)
        ]:
            for record_date, rank in data:
                sector = SectorData(
                    sector_name=sector_name,
                    change_percent=5.0,
                    record_date=record_date,
                    rank_position=rank
                )
                db_session.add(sector)
        db_session.commit()
        
        # 测试趋势计算
        electronics_trend = service._calculate_trend('电子信息', 5)
        new_energy_trend = service._calculate_trend('新能源汽车', 5)
        medical_trend = service._calculate_trend('医疗器械', 5)
        
        assert electronics_trend == 'up'      # 排名上升
        assert new_energy_trend == 'down'     # 排名下降
        assert medical_trend == 'stable'      # 排名稳定
        
        # 通过API验证趋势
        response = client.get('/api/sectors/top-performers?days=5&top_k=5')
        assert response.status_code == 200
        
        performers = response.get_json()['data']
        
        # 验证趋势字段
        for performer in performers:
            if performer['sector_name'] == '电子信息':
                assert performer['trend'] == 'up'
            elif performer['sector_name'] == '新能源汽车':
                assert performer['trend'] == 'down'
            elif performer['sector_name'] == '医疗器械':
                assert performer['trend'] == 'stable'
    
    def test_data_deduplication(self, service, client, mock_akshare_data, db_session):
        """测试数据去重功能"""
        
        with patch('akshare.stock_board_industry_name_em') as mock_ak:
            mock_ak.return_value = mock_akshare_data
            
            # 第一次刷新数据
            response1 = client.post('/api/sectors/refresh')
            assert response1.status_code == 200
            
            data1 = response1.get_json()
            assert data1['success'] is True
            assert data1['data']['count'] == 10
            
            # 第二次刷新数据（应该被去重）
            response2 = client.post('/api/sectors/refresh')
            assert response2.status_code == 200
            
            data2 = response2.get_json()
            assert data2['success'] is True
            assert data2['data']['count'] == 0  # 没有新增数据
            assert '今日数据已存在' in data2['message']
        
        # 验证数据库中只有一份数据
        today = date.today()
        sectors = SectorData.query.filter_by(record_date=today).all()
        assert len(sectors) == 10  # 没有重复数据
        
        rankings = SectorRanking.query.filter_by(record_date=today).all()
        assert len(rankings) == 1  # 只有一条排名记录
    
    def test_data_deletion_workflow(self, service, client, mock_akshare_data, db_session):
        """测试数据删除工作流程"""
        
        # 1. 先创建数据
        with patch('akshare.stock_board_industry_name_em') as mock_ak:
            mock_ak.return_value = mock_akshare_data
            
            response = client.post('/api/sectors/refresh')
            assert response.status_code == 200
        
        today = date.today()
        
        # 2. 验证数据存在
        sectors_before = SectorData.query.filter_by(record_date=today).count()
        rankings_before = SectorRanking.query.filter_by(record_date=today).count()
        
        assert sectors_before == 10
        assert rankings_before == 1
        
        # 3. 删除数据
        response = client.delete(f'/api/sectors/data/{today.isoformat()}')
        assert response.status_code == 200
        
        delete_data = response.get_json()
        assert delete_data['success'] is True
        assert delete_data['data']['deleted_sectors'] == 10
        assert delete_data['data']['deleted_rankings'] == 1
        
        # 4. 验证数据已删除
        sectors_after = SectorData.query.filter_by(record_date=today).count()
        rankings_after = SectorRanking.query.filter_by(record_date=today).count()
        
        assert sectors_after == 0
        assert rankings_after == 0
        
        # 5. 验证API返回空数据
        response = client.get('/api/sectors/ranking')
        assert response.status_code == 200
        
        ranking_data = response.get_json()
        assert len(ranking_data['data']) == 0
    
    def test_error_recovery_and_rollback(self, service, client, db_session):
        """测试错误恢复和回滚机制"""
        
        # 模拟部分数据有问题的情况
        problematic_data = pd.DataFrame({
            '板块名称': ['正常板块', '', '另一个正常板块'],  # 空名称会导致验证错误
            '板块代码': ['BK0001', 'BK0002', 'BK0003'],
            '涨跌幅': [5.23, 'invalid', 3.45],  # 无效的涨跌幅
            '成交量': [1000000, 800000, 600000],
            '总市值': [500000000.0, 400000000.0, 300000000.0]
        })
        
        with patch('akshare.stock_board_industry_name_em') as mock_ak:
            mock_ak.return_value = problematic_data
            
            with patch.object(SectorData, 'has_data_for_date', return_value=False):
                # 应该能够处理部分数据错误，保存有效数据
                result = service.refresh_sector_data()
                
                # 验证只保存了有效数据
                assert result['success'] is True
                assert result['count'] < 3  # 少于原始数据数量
        
        # 验证数据库状态一致
        today = date.today()
        sectors = SectorData.query.filter_by(record_date=today).all()
        
        # 所有保存的数据都应该是有效的
        for sector in sectors:
            assert sector.sector_name  # 名称不为空
            assert sector.change_percent is not None  # 涨跌幅不为空
    
    def test_concurrent_access_handling(self, service, client, mock_akshare_data, db_session):
        """测试并发访问处理"""
        
        # 模拟并发刷新数据的情况
        with patch('akshare.stock_board_industry_name_em') as mock_ak:
            mock_ak.return_value = mock_akshare_data
            
            # 第一个请求开始刷新
            with patch.object(SectorData, 'has_data_for_date', return_value=False):
                response1 = client.post('/api/sectors/refresh')
                assert response1.status_code == 200
            
            # 第二个请求应该检测到数据已存在
            response2 = client.post('/api/sectors/refresh')
            assert response2.status_code == 200
            
            data2 = response2.get_json()
            assert '今日数据已存在' in data2['message']
        
        # 验证最终数据一致性
        today = date.today()
        sectors = SectorData.query.filter_by(record_date=today).count()
        rankings = SectorRanking.query.filter_by(record_date=today).count()
        
        assert sectors == 10  # 没有重复数据
        assert rankings == 1   # 只有一条排名记录