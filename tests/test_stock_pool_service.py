"""
股票池服务测试
"""
import pytest
from datetime import datetime, date
from services.stock_pool_service import StockPoolService
from models.stock_pool import StockPool
from error_handlers import ValidationError, NotFoundError, DatabaseError


class TestStockPoolService:
    """股票池服务测试类"""
    
    def test_create_stock_pool_entry_success(self, db_session):
        """测试成功创建股票池条目"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'target_price': 12.50,
            'add_reason': '技术面良好'
        }
        
        stock_pool = StockPoolService.create_stock_pool_entry(data)
        
        assert stock_pool.id is not None
        assert stock_pool.stock_code == '000001'
        assert stock_pool.stock_name == '平安银行'
        assert stock_pool.pool_type == 'watch'
        assert float(stock_pool.target_price) == 12.50
        assert stock_pool.add_reason == '技术面良好'
        assert stock_pool.status == 'active'
    
    def test_create_stock_pool_entry_duplicate(self, db_session):
        """测试创建重复股票池条目"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        # 创建第一个条目
        StockPoolService.create_stock_pool_entry(data)
        
        # 尝试创建重复条目
        with pytest.raises(ValidationError) as exc_info:
            StockPoolService.create_stock_pool_entry(data)
        
        assert "已在" in str(exc_info.value)
    
    def test_get_by_pool_type(self, db_session):
        """测试根据池类型获取股票"""
        # 创建测试数据
        watch_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        buy_ready_data = {
            'stock_code': '000002',
            'stock_name': '万科A',
            'pool_type': 'buy_ready',
            'add_reason': '达到买入条件'
        }
        
        StockPoolService.create_stock_pool_entry(watch_data)
        StockPoolService.create_stock_pool_entry(buy_ready_data)
        
        # 测试获取待观测池
        watch_result = StockPoolService.get_by_pool_type('watch')
        assert watch_result['total'] == 1
        assert watch_result['items'][0]['stock_code'] == '000001'
        
        # 测试获取待买入池
        buy_ready_result = StockPoolService.get_by_pool_type('buy_ready')
        assert buy_ready_result['total'] == 1
        assert buy_ready_result['items'][0]['stock_code'] == '000002'
    
    def test_get_watch_pool(self, db_session):
        """测试获取待观测池"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        StockPoolService.create_stock_pool_entry(data)
        
        result = StockPoolService.get_watch_pool()
        assert result['total'] == 1
        assert result['items'][0]['pool_type'] == 'watch'
    
    def test_get_buy_ready_pool(self, db_session):
        """测试获取待买入池"""
        data = {
            'stock_code': '000002',
            'stock_name': '万科A',
            'pool_type': 'buy_ready',
            'add_reason': '达到买入条件'
        }
        
        StockPoolService.create_stock_pool_entry(data)
        
        result = StockPoolService.get_buy_ready_pool()
        assert result['total'] == 1
        assert result['items'][0]['pool_type'] == 'buy_ready'
    
    def test_get_stock_history(self, db_session):
        """测试获取股票流转历史"""
        # 创建初始记录
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        stock_pool = StockPoolService.create_stock_pool_entry(data)
        
        # 移动到另一个池
        StockPoolService.move_stock_to_pool(stock_pool.id, 'buy_ready', '达到买入条件')
        
        # 获取历史记录
        history = StockPoolService.get_stock_history('000001')
        
        assert len(history) == 2
        # 最新记录应该是buy_ready池的
        assert history[0]['pool_type'] == 'buy_ready'
        assert history[0]['status'] == 'active'
        # 旧记录应该是moved状态
        assert history[1]['pool_type'] == 'watch'
        assert history[1]['status'] == 'moved'
    
    def test_move_stock_to_pool_success(self, db_session):
        """测试成功移动股票到另一个池"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        stock_pool = StockPoolService.create_stock_pool_entry(data)
        
        # 移动到买入池
        new_stock = StockPoolService.move_stock_to_pool(stock_pool.id, 'buy_ready', '达到买入条件')
        
        # 验证新记录
        assert new_stock.pool_type == 'buy_ready'
        assert new_stock.status == 'active'
        assert new_stock.add_reason == '达到买入条件'
        
        # 验证原记录状态
        db_session.refresh(stock_pool)
        assert stock_pool.status == 'moved'
    
    def test_move_stock_to_same_pool(self, db_session):
        """测试移动股票到相同池"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        stock_pool = StockPoolService.create_stock_pool_entry(data)
        
        # 尝试移动到相同池
        with pytest.raises(ValidationError) as exc_info:
            StockPoolService.move_stock_to_pool(stock_pool.id, 'watch', '测试')
        
        assert "已在" in str(exc_info.value)
    
    def test_move_inactive_stock(self, db_session):
        """测试移动非活跃状态的股票"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        stock_pool = StockPoolService.create_stock_pool_entry(data)
        
        # 先移除股票
        StockPoolService.remove_stock_from_pool(stock_pool.id, '测试移除')
        
        # 尝试移动已移除的股票
        with pytest.raises(ValidationError) as exc_info:
            StockPoolService.move_stock_to_pool(stock_pool.id, 'buy_ready', '测试')
        
        assert "只能移动活跃状态的股票" in str(exc_info.value)
    
    def test_remove_stock_from_pool_success(self, db_session):
        """测试成功从池中移除股票"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        stock_pool = StockPoolService.create_stock_pool_entry(data)
        
        # 移除股票
        removed_stock = StockPoolService.remove_stock_from_pool(stock_pool.id, '不再关注')
        
        assert removed_stock.status == 'removed'
        assert '不再关注' in removed_stock.add_reason
    
    def test_remove_inactive_stock(self, db_session):
        """测试移除非活跃状态的股票"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        stock_pool = StockPoolService.create_stock_pool_entry(data)
        
        # 先移除股票
        StockPoolService.remove_stock_from_pool(stock_pool.id, '第一次移除')
        
        # 尝试再次移除
        with pytest.raises(ValidationError) as exc_info:
            StockPoolService.remove_stock_from_pool(stock_pool.id, '第二次移除')
        
        assert "只能移除活跃状态的股票" in str(exc_info.value)
    
    def test_batch_move_stocks_success(self, db_session):
        """测试批量移动股票成功"""
        # 创建多个股票
        stocks = []
        for i in range(3):
            data = {
                'stock_code': f'00000{i+1}',
                'stock_name': f'股票{i+1}',
                'pool_type': 'watch',
                'add_reason': '技术面良好'
            }
            stock = StockPoolService.create_stock_pool_entry(data)
            stocks.append(stock)
        
        stock_ids = [stock.id for stock in stocks]
        
        # 批量移动
        results = StockPoolService.batch_move_stocks(stock_ids, 'buy_ready', '批量移动测试')
        
        assert len(results['success']) == 3
        assert len(results['failed']) == 0
        
        # 验证移动结果
        for success in results['success']:
            assert success['stock_id'] in stock_ids
    
    def test_batch_move_stocks_partial_failure(self, db_session):
        """测试批量移动股票部分失败"""
        # 创建股票
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        stock = StockPoolService.create_stock_pool_entry(data)
        
        # 包含不存在的ID
        stock_ids = [stock.id, 99999]
        
        # 批量移动
        results = StockPoolService.batch_move_stocks(stock_ids, 'buy_ready', '批量移动测试')
        
        assert len(results['success']) == 1
        assert len(results['failed']) == 1
        assert results['failed'][0]['stock_id'] == 99999
    
    def test_batch_remove_stocks_success(self, db_session):
        """测试批量移除股票成功"""
        # 创建多个股票
        stocks = []
        for i in range(3):
            data = {
                'stock_code': f'00000{i+1}',
                'stock_name': f'股票{i+1}',
                'pool_type': 'watch',
                'add_reason': '技术面良好'
            }
            stock = StockPoolService.create_stock_pool_entry(data)
            stocks.append(stock)
        
        stock_ids = [stock.id for stock in stocks]
        
        # 批量移除
        results = StockPoolService.batch_remove_stocks(stock_ids, '批量移除测试')
        
        assert len(results['success']) == 3
        assert len(results['failed']) == 0
        
        # 验证移除结果
        for success in results['success']:
            assert success['stock_id'] in stock_ids
    
    def test_search_stocks_by_code(self, db_session):
        """测试按股票代码搜索"""
        # 创建测试数据
        data1 = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        data2 = {
            'stock_code': '000002',
            'stock_name': '万科A',
            'pool_type': 'watch',
            'add_reason': '基本面良好'
        }
        
        StockPoolService.create_stock_pool_entry(data1)
        StockPoolService.create_stock_pool_entry(data2)
        
        # 搜索特定股票代码
        filters = {'stock_code': '000001'}
        result = StockPoolService.search_stocks(filters)
        
        assert result['total'] == 1
        assert result['items'][0]['stock_code'] == '000001'
    
    def test_search_stocks_by_name(self, db_session):
        """测试按股票名称搜索"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        StockPoolService.create_stock_pool_entry(data)
        
        # 搜索股票名称
        filters = {'stock_name': '平安'}
        result = StockPoolService.search_stocks(filters)
        
        assert result['total'] == 1
        assert result['items'][0]['stock_name'] == '平安银行'
    
    def test_search_stocks_by_pool_type(self, db_session):
        """测试按池类型搜索"""
        data1 = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        data2 = {
            'stock_code': '000002',
            'stock_name': '万科A',
            'pool_type': 'buy_ready',
            'add_reason': '达到买入条件'
        }
        
        StockPoolService.create_stock_pool_entry(data1)
        StockPoolService.create_stock_pool_entry(data2)
        
        # 搜索待观测池
        filters = {'pool_type': 'watch'}
        result = StockPoolService.search_stocks(filters)
        
        assert result['total'] == 1
        assert result['items'][0]['pool_type'] == 'watch'
    
    def test_search_stocks_with_pagination(self, db_session):
        """测试分页搜索"""
        # 创建多个股票
        for i in range(5):
            data = {
                'stock_code': f'00000{i+1}',
                'stock_name': f'股票{i+1}',
                'pool_type': 'watch',
                'add_reason': '技术面良好'
            }
            StockPoolService.create_stock_pool_entry(data)
        
        # 分页搜索
        result = StockPoolService.search_stocks({}, page=1, per_page=3)
        
        assert result['total'] == 5
        assert len(result['items']) == 3
        assert result['pages'] == 2
        assert result['current_page'] == 1
        assert result['has_next'] is True
        assert result['has_prev'] is False
    
    def test_get_pool_statistics(self, db_session):
        """测试获取股票池统计"""
        # 创建测试数据
        watch_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        buy_ready_data = {
            'stock_code': '000002',
            'stock_name': '万科A',
            'pool_type': 'buy_ready',
            'add_reason': '达到买入条件'
        }
        
        stock1 = StockPoolService.create_stock_pool_entry(watch_data)
        stock2 = StockPoolService.create_stock_pool_entry(buy_ready_data)
        
        # 移动一个股票
        StockPoolService.move_stock_to_pool(stock1.id, 'buy_ready', '移动测试')
        
        # 移除一个股票
        StockPoolService.remove_stock_from_pool(stock2.id, '移除测试')
        
        # 获取统计
        stats = StockPoolService.get_pool_statistics()
        
        assert stats['pool_stats']['watch']['moved'] == 1
        assert stats['pool_stats']['buy_ready']['active'] == 1
        assert stats['pool_stats']['buy_ready']['removed'] == 1
        assert stats['totals']['active'] == 1
        assert stats['totals']['moved'] == 1
        assert stats['totals']['removed'] == 1
    
    def test_get_active_by_stock_code(self, db_session):
        """测试获取股票的活跃记录"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        stock_pool = StockPoolService.create_stock_pool_entry(data)
        
        # 获取活跃记录
        active_record = StockPoolService.get_active_by_stock_code('000001')
        assert active_record is not None
        assert active_record.id == stock_pool.id
        
        # 移除股票后应该找不到活跃记录
        StockPoolService.remove_stock_from_pool(stock_pool.id, '测试移除')
        active_record = StockPoolService.get_active_by_stock_code('000001')
        assert active_record is None
    
    def test_get_active_by_stock_code_with_pool_type(self, db_session):
        """测试按池类型获取股票的活跃记录"""
        data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'pool_type': 'watch',
            'add_reason': '技术面良好'
        }
        
        StockPoolService.create_stock_pool_entry(data)
        
        # 按池类型查找
        watch_record = StockPoolService.get_active_by_stock_code('000001', 'watch')
        assert watch_record is not None
        assert watch_record.pool_type == 'watch'
        
        buy_ready_record = StockPoolService.get_active_by_stock_code('000001', 'buy_ready')
        assert buy_ready_record is None