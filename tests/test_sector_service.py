"""
板块分析服务测试
"""
import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd
from services.sector_service import SectorAnalysisService
from models.sector_data import SectorData, SectorRanking
from error_handlers import ValidationError, ExternalAPIError


class TestSectorAnalysisService:
    """板块分析服务测试类"""
    
    @pytest.fixture
    def service(self):
        """获取服务类"""
        return SectorAnalysisService
    
    @pytest.fixture
    def sample_sector_data(self):
        """创建测试用的板块数据"""
        today = date.today()
        return [
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
            )
        ]
    
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
    
    def test_refresh_sector_data_success(self, service, mock_akshare_data, db_session):
        """测试成功刷新板块数据"""
        with patch('akshare.stock_board_industry_name_em') as mock_ak:
            mock_ak.return_value = mock_akshare_data
            
            # 确保今日没有数据
            with patch.object(SectorData, 'has_data_for_date', return_value=False):
                result = service.refresh_sector_data()
            
            assert result['success'] is True
            assert result['count'] == 3
            assert '成功获取并保存3条板块数据' in result['message']
    
    def test_refresh_sector_data_already_exists(self, service, db_session):
        """测试数据已存在时的处理"""
        with patch.object(SectorData, 'has_data_for_date', return_value=True):
            result = service.refresh_sector_data()
        
        assert result['success'] is True
        assert result['count'] == 0
        assert '今日数据已存在' in result['message']
    
    def test_refresh_sector_data_akshare_error(self, service, db_session):
        """测试AKShare API错误"""
        with patch('akshare.stock_board_industry_name_em') as mock_ak:
            mock_ak.side_effect = Exception("API调用失败")
            
            with patch.object(SectorData, 'has_data_for_date', return_value=False):
                with pytest.raises(ExternalAPIError):
                    service.refresh_sector_data()
    
    def test_refresh_sector_data_empty_dataframe(self, service, db_session):
        """测试空数据框的处理"""
        empty_df = pd.DataFrame()
        
        with patch('akshare.stock_board_industry_name_em') as mock_ak:
            mock_ak.return_value = empty_df
            
            with patch.object(SectorData, 'has_data_for_date', return_value=False):
                result = service.refresh_sector_data()
            
            assert result['success'] is False
            assert result['count'] == 0
            assert '未获取到板块数据' in result['message']
    
    def test_get_sector_ranking_with_date(self, service, sample_sector_data, db_session):
        """测试获取指定日期的板块排名"""
        # 添加测试数据
        for sector in sample_sector_data:
            db_session.add(sector)
        db_session.commit()
        
        today = date.today()
        ranking = service.get_sector_ranking(today, limit=2)
        
        assert len(ranking) == 2
        assert ranking[0]['sector_name'] == '电子信息'
        assert ranking[0]['rank_position'] == 1
        assert ranking[1]['sector_name'] == '新能源汽车'
        assert ranking[1]['rank_position'] == 2
    
    def test_get_sector_ranking_latest(self, service, sample_sector_data, db_session):
        """测试获取最新排名"""
        # 添加测试数据
        for sector in sample_sector_data:
            db_session.add(sector)
        db_session.commit()
        
        ranking = service.get_sector_ranking()
        
        assert len(ranking) == 3
        assert ranking[0]['sector_name'] == '电子信息'
        assert ranking[0]['change_percent'] == 5.23
    
    def test_get_sector_history_success(self, service, db_session):
        """测试获取板块历史表现"""
        # 创建历史数据
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        sectors = [
            SectorData(
                sector_name='电子信息',
                change_percent=5.23,
                record_date=today,
                rank_position=1
            ),
            SectorData(
                sector_name='电子信息',
                change_percent=3.45,
                record_date=yesterday,
                rank_position=2
            )
        ]
        
        for sector in sectors:
            db_session.add(sector)
        db_session.commit()
        
        history = service.get_sector_history('电子信息', days=7)
        
        assert len(history) == 2
        assert history[0]['record_date'] == today.isoformat()  # 最新的在前
        assert history[1]['record_date'] == yesterday.isoformat()
    
    def test_get_sector_history_empty_name(self, service):
        """测试空板块名称"""
        with pytest.raises(ValidationError) as exc_info:
            service.get_sector_history('', days=7)
        
        assert '板块名称不能为空' in str(exc_info.value)
    
    def test_get_sector_history_invalid_days(self, service):
        """测试无效天数"""
        with pytest.raises(ValidationError) as exc_info:
            service.get_sector_history('电子信息', days=0)
        
        assert '查询天数必须大于0' in str(exc_info.value)
    
    def test_get_top_performers_success(self, service, db_session):
        """测试获取TOPK板块统计"""
        # 创建测试数据
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        sectors = [
            # 今天的数据
            SectorData(sector_name='电子信息', change_percent=5.23, record_date=today, rank_position=1),
            SectorData(sector_name='新能源汽车', change_percent=3.45, record_date=today, rank_position=2),
            SectorData(sector_name='医疗器械', change_percent=2.10, record_date=today, rank_position=3),
            # 昨天的数据
            SectorData(sector_name='电子信息', change_percent=4.56, record_date=yesterday, rank_position=1),
            SectorData(sector_name='医疗器械', change_percent=3.21, record_date=yesterday, rank_position=2),
            SectorData(sector_name='新能源汽车', change_percent=1.87, record_date=yesterday, rank_position=5),
        ]
        
        for sector in sectors:
            db_session.add(sector)
        db_session.commit()
        
        top_performers = service.get_top_performers(days=7, top_k=3)
        
        assert len(top_performers) >= 2  # 至少有电子信息和医疗器械
        
        # 检查电子信息板块（应该排第一，因为出现次数最多且平均排名最好）
        electronics = next((p for p in top_performers if p['sector_name'] == '电子信息'), None)
        assert electronics is not None
        assert electronics['appearances'] == 2
        assert electronics['best_rank'] == 1
        assert electronics['avg_rank'] == 1.0
    
    def test_get_top_performers_invalid_params(self, service):
        """测试无效参数"""
        with pytest.raises(ValidationError) as exc_info:
            service.get_top_performers(days=0, top_k=10)
        assert '查询天数必须大于0' in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            service.get_top_performers(days=30, top_k=0)
        assert 'TOPK值必须大于0' in str(exc_info.value)
    
    def test_calculate_trend_up(self, service, db_session):
        """测试上升趋势计算"""
        # 创建排名上升的数据（排名数字变小表示上升）
        today = date.today()
        sectors = []
        
        for i in range(5):
            sector_date = today - timedelta(days=i)
            rank = 6 + i  # 排名逐渐上升（从过去的10到现在的6）
            sectors.append(SectorData(
                sector_name='测试板块',
                change_percent=2.0,
                record_date=sector_date,
                rank_position=rank
            ))
        
        for sector in sectors:
            db_session.add(sector)
        db_session.commit()
        
        trend = service._calculate_trend('测试板块', 5)
        assert trend == 'up'
    
    def test_calculate_trend_down(self, service, db_session):
        """测试下降趋势计算"""
        # 创建排名下降的数据（排名数字变大表示下降）
        today = date.today()
        sectors = []
        
        for i in range(5):
            sector_date = today - timedelta(days=i)
            rank = 5 - i  # 排名逐渐下降（今天是1，4天前是5，这是上升趋势）
            sectors.append(SectorData(
                sector_name='测试板块',
                change_percent=2.0,
                record_date=sector_date,
                rank_position=rank
            ))
        
        for sector in sectors:
            db_session.add(sector)
        db_session.commit()
        
        trend = service._calculate_trend('测试板块', 5)
        assert trend == 'down'
    
    def test_calculate_trend_stable(self, service, db_session):
        """测试稳定趋势计算"""
        # 创建排名稳定的数据
        today = date.today()
        sectors = []
        
        for i in range(5):
            sector_date = today - timedelta(days=i)
            sectors.append(SectorData(
                sector_name='测试板块',
                change_percent=2.0,
                record_date=sector_date,
                rank_position=5  # 排名保持稳定
            ))
        
        for sector in sectors:
            db_session.add(sector)
        db_session.commit()
        
        trend = service._calculate_trend('测试板块', 5)
        assert trend == 'stable'
    
    def test_get_sector_analysis_summary(self, service, sample_sector_data, db_session):
        """测试获取板块分析汇总"""
        # 添加测试数据
        for sector in sample_sector_data:
            db_session.add(sector)
        db_session.commit()
        
        summary = service.get_sector_analysis_summary(days=30)
        
        assert summary['period_days'] == 30
        assert summary['total_records'] == 3
        assert summary['unique_sectors'] == 3
        assert summary['data_days'] == 1
        assert summary['avg_change_percent'] > 0
        assert summary['max_change_percent'] == 5.23
        assert summary['min_change_percent'] == 2.10
    
    def test_get_available_dates(self, service, sample_sector_data, db_session):
        """测试获取可用日期列表"""
        # 添加测试数据
        for sector in sample_sector_data:
            db_session.add(sector)
        db_session.commit()
        
        dates = service.get_available_dates(limit=10)
        
        assert len(dates) == 1
        assert dates[0] == date.today().isoformat()
    
    def test_delete_sector_data(self, service, sample_sector_data, db_session):
        """测试删除板块数据"""
        # 添加测试数据
        today = date.today()
        for sector in sample_sector_data:
            db_session.add(sector)
        
        # 添加排名数据
        ranking = SectorRanking(
            record_date=today,
            total_sectors=3
        )
        ranking.ranking_list = [{'rank': 1, 'sector_name': '电子信息'}]
        db_session.add(ranking)
        db_session.commit()
        
        # 删除数据
        result = service.delete_sector_data(today)
        
        assert result['success'] is True
        assert result['deleted_sectors'] == 3
        assert result['deleted_rankings'] == 1
        
        # 验证数据已删除
        remaining_sectors = SectorData.query.filter_by(record_date=today).count()
        remaining_rankings = SectorRanking.query.filter_by(record_date=today).count()
        
        assert remaining_sectors == 0
        assert remaining_rankings == 0