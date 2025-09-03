"""
历史交易服务单元测试
"""
import pytest
import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from services.historical_trade_service import HistoricalTradeService
from models.trade_record import TradeRecord
from models.historical_trade import HistoricalTrade
from error_handlers import ValidationError, DatabaseError, NotFoundError


class TestHistoricalTradeService:
    """历史交易服务测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.service = HistoricalTradeService
        
        # 创建模拟的交易记录
        self.mock_buy_record1 = Mock(spec=TradeRecord)
        self.mock_buy_record1.id = 1
        self.mock_buy_record1.stock_code = "000001"
        self.mock_buy_record1.stock_name = "平安银行"
        self.mock_buy_record1.trade_type = "buy"
        self.mock_buy_record1.price = Decimal("10.00")
        self.mock_buy_record1.quantity = 1000
        self.mock_buy_record1.trade_date = datetime(2024, 1, 1)
        self.mock_buy_record1.is_corrected = False
        
        self.mock_buy_record2 = Mock(spec=TradeRecord)
        self.mock_buy_record2.id = 2
        self.mock_buy_record2.stock_code = "000001"
        self.mock_buy_record2.stock_name = "平安银行"
        self.mock_buy_record2.trade_type = "buy"
        self.mock_buy_record2.price = Decimal("9.50")
        self.mock_buy_record2.quantity = 500
        self.mock_buy_record2.trade_date = datetime(2024, 1, 5)
        self.mock_buy_record2.is_corrected = False
        
        self.mock_sell_record = Mock(spec=TradeRecord)
        self.mock_sell_record.id = 3
        self.mock_sell_record.stock_code = "000001"
        self.mock_sell_record.stock_name = "平安银行"
        self.mock_sell_record.trade_type = "sell"
        self.mock_sell_record.price = Decimal("11.00")
        self.mock_sell_record.quantity = 1500
        self.mock_sell_record.trade_date = datetime(2024, 1, 15)
        self.mock_sell_record.is_corrected = False
    
    @patch('services.historical_trade_service.TradeRecord')
    @patch('flask.current_app')
    def test_identify_completed_trades_success(self, mock_app, mock_trade_record):
        """测试成功识别已完成交易"""
        # 准备测试数据
        mock_app.logger = Mock()
        
        # 模拟查询结果
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [
            self.mock_buy_record1,
            self.mock_buy_record2,
            self.mock_sell_record
        ]
        mock_trade_record.query = mock_query
        
        # 执行测试
        result = self.service.identify_completed_trades()
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 1  # 应该识别出一个完整交易
        
        completed_trade = result[0]
        assert completed_trade['stock_code'] == "000001"
        assert completed_trade['stock_name'] == "平安银行"
        assert completed_trade['buy_date'] == datetime(2024, 1, 1)
        assert completed_trade['sell_date'] == datetime(2024, 1, 15)
        assert completed_trade['holding_days'] == 14
        assert completed_trade['is_completed'] is True
    
    @patch('services.historical_trade_service.TradeRecord')
    @patch('flask.current_app')
    def test_identify_completed_trades_no_trades(self, mock_app, mock_trade_record):
        """测试没有交易记录的情况"""
        # 准备测试数据
        mock_app.logger = Mock()
        
        # 模拟空查询结果
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        mock_trade_record.query = mock_query
        
        # 执行测试
        result = self.service.identify_completed_trades()
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 0
    
    @patch('flask.current_app')
    def test_analyze_stock_trades_complete_cycle(self, mock_app):
        """测试分析股票交易记录 - 完整周期"""
        mock_app.logger = Mock()
        
        trades = [self.mock_buy_record1, self.mock_buy_record2, self.mock_sell_record]
        
        # 执行测试
        result = self.service._analyze_stock_trades("000001", trades)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 1
        
        completed_trade = result[0]
        assert completed_trade['stock_code'] == "000001"
        assert completed_trade['holding_days'] == 14
    
    @patch('flask.current_app')
    def test_analyze_stock_trades_incomplete_cycle(self, mock_app):
        """测试分析股票交易记录 - 不完整周期"""
        mock_app.logger = Mock()
        
        # 只有买入记录，没有卖出
        trades = [self.mock_buy_record1, self.mock_buy_record2]
        
        # 执行测试
        result = self.service._analyze_stock_trades("000001", trades)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 0  # 没有完整交易
    
    @patch('flask.current_app')
    def test_create_completed_trade_data(self, mock_app):
        """测试创建完整交易数据"""
        mock_app.logger = Mock()
        
        buy_records = [self.mock_buy_record1, self.mock_buy_record2]
        sell_records = [self.mock_sell_record]
        
        # 执行测试
        result = self.service._create_completed_trade_data("000001", buy_records, sell_records)
        
        # 验证结果
        assert result['stock_code'] == "000001"
        assert result['stock_name'] == "平安银行"
        assert result['buy_date'] == datetime(2024, 1, 1)
        assert result['sell_date'] == datetime(2024, 1, 15)
        assert result['holding_days'] == 14
        
        # 验证财务计算
        expected_investment = 10.00 * 1000 + 9.50 * 500  # 14750
        expected_revenue = 11.00 * 1500  # 16500
        expected_return = expected_revenue - expected_investment  # 1750
        expected_return_rate = expected_return / expected_investment  # 约0.119
        
        assert float(result['total_investment']) == expected_investment
        assert float(result['total_return']) == expected_return
        assert abs(float(result['return_rate']) - expected_return_rate) < 0.001
        
        # 验证记录ID
        buy_ids = json.loads(result['buy_records_ids'])
        sell_ids = json.loads(result['sell_records_ids'])
        assert buy_ids == [1, 2]
        assert sell_ids == [3]
    
    @patch('flask.current_app')
    def test_calculate_trade_metrics(self, mock_app):
        """测试计算交易指标"""
        mock_app.logger = Mock()
        
        buy_records = [self.mock_buy_record1, self.mock_buy_record2]
        sell_records = [self.mock_sell_record]
        
        # 执行测试
        result = self.service.calculate_trade_metrics(buy_records, sell_records)
        
        # 验证基本指标
        assert result['buy_date'] == datetime(2024, 1, 1)
        assert result['sell_date'] == datetime(2024, 1, 15)
        assert result['holding_days'] == 14
        assert result['total_buy_quantity'] == 1500
        assert result['total_sell_quantity'] == 1500
        
        # 验证财务指标
        assert result['total_investment'] == 14750.0
        assert result['total_revenue'] == 16500.0
        assert result['total_return'] == 1750.0
        assert result['is_profitable'] is True
        
        # 验证计算指标
        assert abs(result['return_rate'] - 0.11864406779661017) < 0.001
        assert result['avg_buy_price'] == 14750.0 / 1500
        assert result['avg_sell_price'] == 11.0
        assert result['daily_return_rate'] > 0
        assert result['annualized_return_rate'] > 0
    
    def test_calculate_trade_metrics_empty_records(self):
        """测试计算交易指标 - 空记录"""
        with pytest.raises(ValidationError) as exc_info:
            self.service.calculate_trade_metrics([], [])
        
        assert "买入记录和卖出记录都不能为空" in str(exc_info.value)
    
    @patch('services.historical_trade_service.HistoricalTrade')
    @patch('services.historical_trade_service.db')
    @patch('flask.current_app')
    def test_generate_historical_records_success(self, mock_app, mock_db, mock_historical_trade):
        """测试成功生成历史交易记录"""
        mock_app.logger = Mock()
        
        # 模拟identify_completed_trades返回结果
        completed_trades = [{
            'stock_code': '000001',
            'stock_name': '平安银行',
            'buy_date': datetime(2024, 1, 1),
            'sell_date': datetime(2024, 1, 15),
            'holding_days': 14,
            'total_investment': Decimal('14750.00'),
            'total_return': Decimal('1750.00'),
            'return_rate': Decimal('0.1186'),
            'buy_records_ids': '[1, 2]',
            'sell_records_ids': '[3]',
            'is_completed': True,
            'completion_date': datetime(2024, 1, 15)
        }]
        
        with patch.object(self.service, 'identify_completed_trades', return_value=completed_trades):
            with patch.object(self.service, '_find_existing_record', return_value=None):
                with patch.object(self.service, 'create') as mock_create:
                    mock_create.return_value = Mock(id=1)
                    
                    # 执行测试
                    result = self.service.generate_historical_records()
                    
                    # 验证结果
                    assert result['total_identified'] == 1
                    assert result['created_count'] == 1
                    assert result['skipped_count'] == 0
                    assert result['error_count'] == 0
                    assert result['success'] is True
    
    @patch('services.historical_trade_service.HistoricalTrade')
    @patch('services.historical_trade_service.db')
    @patch('flask.current_app')
    def test_generate_historical_records_force_regenerate(self, mock_app, mock_db, mock_historical_trade):
        """测试强制重新生成历史交易记录"""
        mock_app.logger = Mock()
        
        # 模拟删除操作
        mock_query = Mock()
        mock_query.delete.return_value = 5  # 删除了5条记录
        mock_historical_trade.query = mock_query
        
        completed_trades = []  # 空的完整交易列表
        
        with patch.object(self.service, 'identify_completed_trades', return_value=completed_trades):
            # 执行测试
            result = self.service.generate_historical_records(force_regenerate=True)
            
            # 验证结果
            assert result['total_identified'] == 0
            assert result['created_count'] == 0
            assert result['success'] is True
            
            # 验证删除操作被调用
            mock_query.delete.assert_called_once()
            mock_db.session.commit.assert_called()
    
    @patch('services.historical_trade_service.HistoricalTrade')
    @patch('flask.current_app')
    def test_sync_historical_records_success(self, mock_app, mock_historical_trade):
        """测试成功同步历史交易记录"""
        mock_app.logger = Mock()
        
        # 模拟最后同步记录
        mock_last_record = Mock()
        mock_last_record.created_at = datetime(2024, 1, 1)
        
        mock_query = Mock()
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = mock_last_record
        mock_historical_trade.query = mock_query
        
        # 模拟新的完整交易
        completed_trades = [{
            'stock_code': '000002',
            'stock_name': '万科A',
            'buy_date': datetime(2024, 1, 10),
            'sell_date': datetime(2024, 1, 20),
            'holding_days': 10,
            'total_investment': Decimal('10000.00'),
            'total_return': Decimal('500.00'),
            'return_rate': Decimal('0.05'),
            'buy_records_ids': '[4]',
            'sell_records_ids': '[5]',
            'is_completed': True,
            'completion_date': datetime(2024, 1, 20)
        }]
        
        with patch.object(self.service, 'identify_completed_trades', return_value=completed_trades):
            with patch.object(self.service, '_find_existing_record', return_value=None):
                with patch.object(self.service, 'create') as mock_create:
                    mock_create.return_value = Mock(id=2)
                    
                    # 执行测试
                    result = self.service.sync_historical_records()
                    
                    # 验证结果
                    assert result['total_checked'] == 1
                    assert result['created_count'] == 1
                    assert result['updated_count'] == 0
                    assert result['error_count'] == 0
                    assert result['success'] is True
    
    @patch('services.historical_trade_service.HistoricalTrade')
    def test_get_historical_trades_with_pagination(self, mock_historical_trade):
        """测试获取历史交易记录列表 - 分页"""
        # 模拟分页结果
        mock_pagination = Mock()
        mock_pagination.items = [Mock(to_dict=Mock(return_value={'id': 1}))]
        mock_pagination.total = 10
        mock_pagination.pages = 2
        mock_pagination.page = 1
        mock_pagination.per_page = 5
        mock_pagination.has_next = True
        mock_pagination.has_prev = False
        
        mock_query = Mock()
        mock_query.paginate.return_value = mock_pagination
        mock_historical_trade.query = mock_query
        
        with patch.object(self.service, '_apply_filters', return_value=mock_query):
            with patch.object(self.service, '_apply_sorting', return_value=mock_query):
                # 执行测试
                result = self.service.get_historical_trades(page=1, per_page=5)
                
                # 验证结果
                assert 'trades' in result
                assert 'total' in result
                assert 'pages' in result
                assert result['total'] == 10
                assert result['pages'] == 2
                assert result['current_page'] == 1
    
    @patch('services.historical_trade_service.HistoricalTrade')
    def test_get_historical_trades_without_pagination(self, mock_historical_trade):
        """测试获取历史交易记录列表 - 不分页"""
        # 模拟查询结果
        mock_trades = [Mock(to_dict=Mock(return_value={'id': i})) for i in range(3)]
        
        mock_query = Mock()
        mock_query.all.return_value = mock_trades
        mock_historical_trade.query = mock_query
        
        with patch.object(self.service, '_apply_filters', return_value=mock_query):
            with patch.object(self.service, '_apply_sorting', return_value=mock_query):
                # 执行测试
                result = self.service.get_historical_trades()
                
                # 验证结果
                assert 'trades' in result
                assert 'total' in result
                assert result['total'] == 3
                assert len(result['trades']) == 3
    
    @patch('services.historical_trade_service.db')
    @patch('services.historical_trade_service.func')
    @patch('services.historical_trade_service.HistoricalTrade')
    @patch('flask.current_app')
    def test_get_trade_statistics(self, mock_app, mock_historical_trade, mock_func, mock_db):
        """测试获取交易统计信息"""
        mock_app.logger = Mock()
        
        # 模拟查询结果
        mock_query = Mock()
        mock_query.count.return_value = 10
        mock_query.filter.return_value = mock_query
        mock_historical_trade.query = mock_query
        
        # 模拟profitable_trades查询
        profitable_query = Mock()
        profitable_query.count.return_value = 7
        mock_query.filter.return_value = profitable_query
        
        # 模拟loss_trades查询
        loss_query = Mock()
        loss_query.count.return_value = 3
        
        # 设置filter方法的返回值
        def filter_side_effect(condition):
            # 根据条件返回不同的查询对象
            if "total_return > 0" in str(condition):
                return profitable_query
            elif "total_return < 0" in str(condition):
                return loss_query
            return mock_query
        
        mock_query.filter.side_effect = filter_side_effect
        
        # 模拟聚合查询
        mock_session = Mock()
        mock_session.query.return_value.scalar.return_value = 100000  # 总投资
        mock_db.session = mock_session
        
        # 执行测试
        result = self.service.get_trade_statistics()
        
        # 验证结果
        assert 'total_trades' in result
        assert 'profitable_trades' in result
        assert 'loss_trades' in result
        assert 'win_rate' in result
        assert 'total_investment' in result
        assert 'total_return' in result
        assert isinstance(result['total_trades'], int)
        assert isinstance(result['win_rate'], (int, float))
    
    def test_find_existing_record(self):
        """测试查找现有记录"""
        trade_data = {
            'stock_code': '000001',
            'buy_date': datetime(2024, 1, 1),
            'sell_date': datetime(2024, 1, 15)
        }
        
        with patch.object(self.service.model, 'query') as mock_query:
            mock_filter = Mock()
            mock_query.filter.return_value = mock_filter
            mock_filter.first.return_value = Mock(id=1)
            
            # 执行测试
            result = self.service._find_existing_record(trade_data)
            
            # 验证结果
            assert result is not None
            assert result.id == 1
    
    def test_needs_update_true(self):
        """测试需要更新的情况"""
        existing_record = Mock()
        existing_record.total_investment = Decimal('10000')
        existing_record.total_return = Decimal('1000')
        existing_record.return_rate = Decimal('0.1')
        existing_record.holding_days = 10
        
        new_data = {
            'total_investment': Decimal('10000'),
            'total_return': Decimal('1500'),  # 不同的值
            'return_rate': Decimal('0.15'),   # 不同的值
            'holding_days': 10
        }
        
        # 执行测试
        result = self.service._needs_update(existing_record, new_data)
        
        # 验证结果
        assert result is True
    
    def test_needs_update_false(self):
        """测试不需要更新的情况"""
        existing_record = Mock()
        existing_record.total_investment = Decimal('10000')
        existing_record.total_return = Decimal('1000')
        existing_record.return_rate = Decimal('0.1')
        existing_record.holding_days = 10
        
        new_data = {
            'total_investment': Decimal('10000'),
            'total_return': Decimal('1000'),
            'return_rate': Decimal('0.1'),
            'holding_days': 10
        }
        
        # 执行测试
        result = self.service._needs_update(existing_record, new_data)
        
        # 验证结果
        assert result is False
    
    def test_apply_filters(self):
        """测试应用筛选条件"""
        mock_query = Mock()
        
        filters = {
            'stock_code': '000001',
            'stock_name': '平安',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'min_return_rate': 0.05,
            'max_return_rate': 0.20,
            'min_holding_days': 5,
            'max_holding_days': 30,
            'is_profitable': True
        }
        
        # 执行测试
        result = self.service._apply_filters(mock_query, filters)
        
        # 验证filter方法被调用
        assert mock_query.filter.call_count > 0
    
    def test_apply_sorting_desc(self):
        """测试应用排序 - 降序"""
        mock_query = Mock()
        
        with patch('services.historical_trade_service.desc') as mock_desc:
            # 执行测试
            result = self.service._apply_sorting(mock_query, 'completion_date', 'desc')
            
            # 验证排序被应用
            mock_query.order_by.assert_called_once()
            mock_desc.assert_called_once()
    
    def test_apply_sorting_asc(self):
        """测试应用排序 - 升序"""
        mock_query = Mock()
        
        with patch('services.historical_trade_service.asc') as mock_asc:
            # 执行测试
            result = self.service._apply_sorting(mock_query, 'completion_date', 'asc')
            
            # 验证排序被应用
            mock_query.order_by.assert_called_once()
            mock_asc.assert_called_once()
    
    def test_parse_date_string(self):
        """测试解析日期字符串"""
        # 测试不同格式的日期字符串
        date_formats = [
            ('2024-01-01', datetime(2024, 1, 1)),
            ('2024/01/01', datetime(2024, 1, 1)),
            ('2024-01-01 10:30:00', datetime(2024, 1, 1, 10, 30, 0))
        ]
        
        for date_str, expected in date_formats:
            result = self.service._parse_date(date_str)
            assert result == expected
    
    def test_parse_date_datetime_object(self):
        """测试解析datetime对象"""
        dt = datetime(2024, 1, 1, 10, 30, 0)
        result = self.service._parse_date(dt)
        assert result == dt
    
    def test_parse_date_invalid_format(self):
        """测试解析无效日期格式"""
        with pytest.raises(ValidationError) as exc_info:
            self.service._parse_date("invalid-date")
        
        assert "日期格式错误" in str(exc_info.value)
    
    def test_parse_date_invalid_type(self):
        """测试解析无效日期类型"""
        with pytest.raises(ValidationError) as exc_info:
            self.service._parse_date(123)
        
        assert "日期格式错误" in str(exc_info.value)


class TestHistoricalTradeServiceIntegration:
    """历史交易服务集成测试类"""
    
    @patch('services.historical_trade_service.TradeRecord')
    @patch('services.historical_trade_service.HistoricalTrade')
    @patch('services.historical_trade_service.db')
    @patch('flask.current_app')
    def test_full_workflow_generate_and_sync(self, mock_app, mock_db, mock_historical_trade, mock_trade_record):
        """测试完整工作流程：生成和同步"""
        mock_app.logger = Mock()
        service = HistoricalTradeService
        
        # 模拟交易记录查询
        mock_trades = [
            Mock(id=1, stock_code="000001", stock_name="平安银行", trade_type="buy", 
                 price=Decimal("10.00"), quantity=1000, trade_date=datetime(2024, 1, 1), is_corrected=False),
            Mock(id=2, stock_code="000001", stock_name="平安银行", trade_type="sell", 
                 price=Decimal("11.00"), quantity=1000, trade_date=datetime(2024, 1, 15), is_corrected=False)
        ]
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_trades
        mock_trade_record.query = mock_query
        
        # 模拟历史交易记录查询（空结果）
        mock_hist_query = Mock()
        mock_hist_query.filter.return_value = mock_hist_query
        mock_hist_query.first.return_value = None
        mock_historical_trade.query = mock_hist_query
        
        # 模拟创建操作
        with patch.object(service, 'create') as mock_create:
            mock_create.return_value = Mock(id=1)
            
            # 执行生成操作
            result = service.generate_historical_records()
            
            # 验证生成结果
            assert result['success'] is True
            assert result['created_count'] == 1
            
            # 验证create被调用
            mock_create.assert_called_once()
            
            # 获取create调用的参数
            create_args = mock_create.call_args[0][0]
            assert create_args['stock_code'] == "000001"
            assert create_args['holding_days'] == 14
            assert create_args['is_completed'] is True
    
    @patch('flask.current_app')
    def test_edge_case_partial_sell(self, mock_app):
        """测试边界情况：部分卖出"""
        mock_app.logger = Mock()
        service = HistoricalTradeService
        
        # 创建部分卖出的交易记录
        trades = [
            Mock(id=1, stock_code="000001", stock_name="平安银行", trade_type="buy", 
                 price=Decimal("10.00"), quantity=1000, trade_date=datetime(2024, 1, 1), is_corrected=False),
            Mock(id=2, stock_code="000001", stock_name="平安银行", trade_type="sell", 
                 price=Decimal("11.00"), quantity=500, trade_date=datetime(2024, 1, 15), is_corrected=False),
            # 还有500股未卖出
        ]
        
        # 执行分析
        result = service._analyze_stock_trades("000001", trades)
        
        # 验证结果：应该没有完整交易
        assert len(result) == 0
    
    @patch('flask.current_app')
    def test_edge_case_multiple_complete_cycles(self, mock_app):
        """测试边界情况：多个完整交易周期"""
        mock_app.logger = Mock()
        service = HistoricalTradeService
        
        # 创建多个完整交易周期
        trades = [
            # 第一个周期
            Mock(id=1, stock_code="000001", stock_name="平安银行", trade_type="buy", 
                 price=Decimal("10.00"), quantity=1000, trade_date=datetime(2024, 1, 1), is_corrected=False),
            Mock(id=2, stock_code="000001", stock_name="平安银行", trade_type="sell", 
                 price=Decimal("11.00"), quantity=1000, trade_date=datetime(2024, 1, 15), is_corrected=False),
            # 第二个周期
            Mock(id=3, stock_code="000001", stock_name="平安银行", trade_type="buy", 
                 price=Decimal("9.00"), quantity=2000, trade_date=datetime(2024, 2, 1), is_corrected=False),
            Mock(id=4, stock_code="000001", stock_name="平安银行", trade_type="sell", 
                 price=Decimal("10.50"), quantity=2000, trade_date=datetime(2024, 2, 20), is_corrected=False),
        ]
        
        # 执行分析
        result = service._analyze_stock_trades("000001", trades)
        
        # 验证结果：应该有两个完整交易
        assert len(result) == 2
        
        # 验证第一个交易
        first_trade = result[0]
        assert first_trade['buy_date'] == datetime(2024, 1, 1)
        assert first_trade['sell_date'] == datetime(2024, 1, 15)
        
        # 验证第二个交易
        second_trade = result[1]
        assert second_trade['buy_date'] == datetime(2024, 2, 1)
        assert second_trade['sell_date'] == datetime(2024, 2, 20)