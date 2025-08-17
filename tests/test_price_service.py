"""
股票价格服务测试
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
import pandas as pd

from services.price_service import PriceService
from models.stock_price import StockPrice
from error_handlers import ValidationError, ExternalAPIError


class TestPriceService:
    """价格服务测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.price_service = PriceService()
        self.test_stock_code = '000001'
        self.test_stock_name = '平安银行'
        self.test_price = 12.50
        self.test_change_percent = 2.5
        self.today = date.today()
    
    def test_init(self):
        """测试服务初始化"""
        assert self.price_service.model == StockPrice
        assert hasattr(self.price_service, 'db')
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_refresh_stock_price_success(self, mock_akshare, db_session):
        """测试成功刷新股票价格"""
        # 模拟AKShare返回数据
        mock_df = pd.DataFrame({
            '代码': [self.test_stock_code],
            '名称': [self.test_stock_name],
            '最新价': [self.test_price],
            '涨跌幅': [self.test_change_percent]
        })
        mock_akshare.return_value = mock_df
        
        # 执行刷新
        result = self.price_service.refresh_stock_price(self.test_stock_code)
        
        # 验证结果
        assert result['success'] is True
        assert result['message'] == '价格刷新成功'
        assert result['from_cache'] is False
        assert result['data']['stock_code'] == self.test_stock_code
        assert result['data']['current_price'] == self.test_price
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_refresh_stock_price_with_cache(self, mock_akshare, db_session):
        """测试有缓存时的价格刷新"""
        # 创建今日价格记录
        existing_price = StockPrice(
            stock_code=self.test_stock_code,
            stock_name=self.test_stock_name,
            current_price=self.test_price,
            change_percent=self.test_change_percent,
            record_date=self.today
        )
        existing_price.save()
        
        # 执行刷新（不强制）
        result = self.price_service.refresh_stock_price(self.test_stock_code, force_refresh=False)
        
        # 验证结果
        assert result['success'] is True
        assert result['message'] == '价格数据已是最新'
        assert result['from_cache'] is True
        
        # 验证没有调用AKShare
        mock_akshare.assert_not_called()
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_refresh_stock_price_force_refresh(self, mock_akshare):
        """测试强制刷新股票价格"""
        # 创建今日价格记录
        existing_price = StockPrice(
            stock_code=self.test_stock_code,
            stock_name=self.test_stock_name,
            current_price=10.0,
            change_percent=0.0,
            record_date=self.today
        )
        existing_price.save()
        
        # 模拟AKShare返回新数据
        mock_df = pd.DataFrame({
            '代码': [self.test_stock_code],
            '名称': [self.test_stock_name],
            '最新价': [self.test_price],
            '涨跌幅': [self.test_change_percent]
        })
        mock_akshare.return_value = mock_df
        
        # 执行强制刷新
        result = self.price_service.refresh_stock_price(self.test_stock_code, force_refresh=True)
        
        # 验证结果
        assert result['success'] is True
        assert result['from_cache'] is False
        assert result['data']['current_price'] == self.test_price
        
        # 验证调用了AKShare
        mock_akshare.assert_called_once()
    
    def test_refresh_stock_price_invalid_code(self):
        """测试无效股票代码"""
        with pytest.raises(ValidationError) as exc_info:
            self.price_service.refresh_stock_price('INVALID')
        
        assert '股票代码格式不正确' in str(exc_info.value)
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_refresh_stock_price_akshare_empty(self, mock_akshare):
        """测试AKShare返回空数据"""
        mock_akshare.return_value = pd.DataFrame()
        
        with pytest.raises(ExternalAPIError) as exc_info:
            self.price_service.refresh_stock_price(self.test_stock_code)
        
        assert '无法获取股票' in str(exc_info.value)
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_refresh_stock_price_stock_not_found(self, mock_akshare):
        """测试股票未找到"""
        # 模拟AKShare返回其他股票数据
        mock_df = pd.DataFrame({
            '代码': ['000002'],
            '名称': ['万科A'],
            '最新价': [20.0],
            '涨跌幅': [1.0]
        })
        mock_akshare.return_value = mock_df
        
        with pytest.raises(ExternalAPIError) as exc_info:
            self.price_service.refresh_stock_price(self.test_stock_code)
        
        assert '无法获取股票' in str(exc_info.value)
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_refresh_multiple_stocks_success(self, mock_akshare):
        """测试批量刷新股票价格成功"""
        stock_codes = ['000001', '000002']
        
        # 模拟AKShare返回数据
        mock_df = pd.DataFrame({
            '代码': stock_codes,
            '名称': ['平安银行', '万科A'],
            '最新价': [12.5, 20.0],
            '涨跌幅': [2.5, 1.0]
        })
        mock_akshare.return_value = mock_df
        
        # 执行批量刷新
        results = self.price_service.refresh_multiple_stocks(stock_codes)
        
        # 验证结果
        assert results['success_count'] == 2
        assert results['failed_count'] == 0
        assert len(results['results']) == 2
        assert len(results['errors']) == 0
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_refresh_multiple_stocks_partial_failure(self, mock_akshare):
        """测试批量刷新部分失败"""
        stock_codes = ['000001', 'INVALID']
        
        # 模拟AKShare返回数据
        mock_df = pd.DataFrame({
            '代码': ['000001'],
            '名称': ['平安银行'],
            '最新价': [12.5],
            '涨跌幅': [2.5]
        })
        mock_akshare.return_value = mock_df
        
        # 执行批量刷新
        results = self.price_service.refresh_multiple_stocks(stock_codes)
        
        # 验证结果
        assert results['success_count'] == 1
        assert results['failed_count'] == 1
        assert len(results['results']) == 1
        assert len(results['errors']) == 1
        assert results['errors'][0]['stock_code'] == 'INVALID'
    
    def test_get_stock_price_success(self, db_session):
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
        
        # 获取价格
        result = self.price_service.get_stock_price(self.test_stock_code, self.today)
        
        # 验证结果
        assert result is not None
        assert result['stock_code'] == self.test_stock_code
        assert result['current_price'] == self.test_price
    
    def test_get_stock_price_not_found(self):
        """测试获取不存在的股票价格"""
        result = self.price_service.get_stock_price(self.test_stock_code, self.today)
        assert result is None
    
    def test_get_stock_price_invalid_code(self):
        """测试获取价格时股票代码无效"""
        with pytest.raises(ValidationError):
            self.price_service.get_stock_price('INVALID')
    
    def test_get_latest_price_success(self):
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
        
        # 获取最新价格
        result = self.price_service.get_latest_price(self.test_stock_code)
        
        # 验证结果
        assert result is not None
        assert result['current_price'] == self.test_price
        assert result['record_date'] == self.today.isoformat()
    
    def test_get_latest_price_not_found(self):
        """测试获取不存在股票的最新价格"""
        result = self.price_service.get_latest_price(self.test_stock_code)
        assert result is None
    
    def test_get_price_history_success(self):
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
        
        # 获取价格历史
        history = self.price_service.get_price_history(self.test_stock_code, 3)
        
        # 验证结果
        assert len(history) == 3
        # 应该按日期倒序排列
        assert history[0]['record_date'] == self.today.isoformat()
    
    def test_get_price_history_invalid_days(self):
        """测试获取价格历史时天数无效"""
        with pytest.raises(ValidationError) as exc_info:
            self.price_service.get_price_history(self.test_stock_code, 0)
        
        assert '天数必须大于0' in str(exc_info.value)
    
    def test_cleanup_old_prices_success(self):
        """测试清理旧价格数据成功"""
        # 创建新旧价格记录
        old_date = self.today - timedelta(days=100)
        recent_date = self.today - timedelta(days=10)
        
        old_price = StockPrice(
            stock_code=self.test_stock_code,
            stock_name=self.test_stock_name,
            current_price=10.0,
            change_percent=0.0,
            record_date=old_date
        )
        old_price.save()
        
        recent_price = StockPrice(
            stock_code=self.test_stock_code,
            stock_name=self.test_stock_name,
            current_price=self.test_price,
            change_percent=self.test_change_percent,
            record_date=recent_date
        )
        recent_price.save()
        
        # 清理90天前的数据
        result = self.price_service.cleanup_old_prices(90)
        
        # 验证结果
        assert result['success'] is True
        assert result['deleted_count'] == 1
        
        # 验证旧数据被删除，新数据保留
        assert StockPrice.get_price_by_date(self.test_stock_code, old_date) is None
        assert StockPrice.get_price_by_date(self.test_stock_code, recent_date) is not None
    
    def test_get_cache_status_success(self):
        """测试获取缓存状态成功"""
        stock_codes = ['000001', '000002', 'INVALID']
        
        # 创建一个今日价格记录
        price_record = StockPrice(
            stock_code='000001',
            stock_name='平安银行',
            current_price=self.test_price,
            change_percent=self.test_change_percent,
            record_date=self.today
        )
        price_record.save()
        
        # 获取缓存状态
        status = self.price_service.get_cache_status(stock_codes)
        
        # 验证结果
        assert status['total_stocks'] == 3
        assert status['cached_today'] == 1
        assert status['need_refresh'] == 1
        assert len(status['details']) == 3
        
        # 验证详细状态
        details = {detail['stock_code']: detail for detail in status['details']}
        assert details['000001']['status'] == 'cached'
        assert details['000002']['status'] == 'need_refresh'
        assert details['INVALID']['status'] == 'invalid'
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_fetch_stock_price_from_akshare_success(self, mock_akshare):
        """测试从AKShare获取价格数据成功"""
        # 模拟AKShare返回数据
        mock_df = pd.DataFrame({
            '代码': [self.test_stock_code],
            '名称': [self.test_stock_name],
            '最新价': [self.test_price],
            '涨跌幅': [self.test_change_percent]
        })
        mock_akshare.return_value = mock_df
        
        # 调用私有方法
        result = self.price_service._fetch_stock_price_from_akshare(self.test_stock_code)
        
        # 验证结果
        assert result is not None
        assert result['stock_name'] == self.test_stock_name
        assert result['current_price'] == self.test_price
        assert result['change_percent'] == self.test_change_percent
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_fetch_stock_price_from_akshare_empty_data(self, mock_akshare):
        """测试AKShare返回空数据"""
        mock_akshare.return_value = pd.DataFrame()
        
        result = self.price_service._fetch_stock_price_from_akshare(self.test_stock_code)
        assert result is None
    
    @patch('services.price_service.ak.stock_zh_a_spot_em')
    def test_fetch_stock_price_from_akshare_exception(self, mock_akshare):
        """测试AKShare调用异常"""
        mock_akshare.side_effect = Exception("API调用失败")
        
        result = self.price_service._fetch_stock_price_from_akshare(self.test_stock_code)
        assert result is None