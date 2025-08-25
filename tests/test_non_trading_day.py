"""
非交易日功能单元测试
"""
import unittest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.non_trading_day import NonTradingDay
from services.non_trading_day_service import NonTradingDayService
from error_handlers import ValidationError, DatabaseError


class TestNonTradingDayModel(unittest.TestCase):
    """非交易日模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_date = date(2024, 1, 1)  # 2024年1月1日，星期一
        self.weekend_date = date(2024, 1, 6)  # 2024年1月6日，星期六
        self.sunday_date = date(2024, 1, 7)  # 2024年1月7日，星期日
    
    @patch('models.non_trading_day.NonTradingDay.query')
    def test_is_trading_day_weekday(self, mock_query):
        """测试工作日是否为交易日"""
        # 模拟数据库查询返回None（没有找到非交易日记录）
        mock_query.filter_by.return_value.first.return_value = None
        
        # 测试工作日（星期一）
        result = NonTradingDay.is_trading_day(self.test_date)
        self.assertTrue(result)
    
    def test_is_trading_day_weekend(self):
        """测试周末是否为交易日"""
        # 测试星期六
        result = NonTradingDay.is_trading_day(self.weekend_date)
        self.assertFalse(result)
        
        # 测试星期日
        result = NonTradingDay.is_trading_day(self.sunday_date)
        self.assertFalse(result)
    
    @patch('models.non_trading_day.NonTradingDay.query')
    def test_is_trading_day_holiday(self, mock_query):
        """测试节假日是否为交易日"""
        # 模拟数据库查询返回节假日记录
        mock_holiday = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_holiday
        
        result = NonTradingDay.is_trading_day(self.test_date)
        self.assertFalse(result)
    
    def test_is_trading_day_string_date(self):
        """测试字符串日期格式"""
        result = NonTradingDay.is_trading_day('2024-01-06')  # 星期六
        self.assertFalse(result)
    
    @patch('models.non_trading_day.NonTradingDay.is_trading_day')
    def test_calculate_trading_days(self, mock_is_trading_day):
        """测试计算交易日数量"""
        # 模拟is_trading_day方法
        # 假设2024-01-01到2024-01-05中，1,2,3,4,5都是交易日
        mock_is_trading_day.side_effect = lambda d: d.weekday() < 5
        
        start_date = date(2024, 1, 1)  # 星期一
        end_date = date(2024, 1, 5)    # 星期五
        
        result = NonTradingDay.calculate_trading_days(start_date, end_date)
        self.assertEqual(result, 5)  # 5个工作日
    
    def test_calculate_trading_days_invalid_range(self):
        """测试无效日期范围"""
        start_date = date(2024, 1, 5)
        end_date = date(2024, 1, 1)
        
        result = NonTradingDay.calculate_trading_days(start_date, end_date)
        self.assertEqual(result, 0)
    
    def test_calculate_trading_days_string_dates(self):
        """测试字符串日期格式的交易日计算"""
        with patch.object(NonTradingDay, 'is_trading_day', return_value=True):
            result = NonTradingDay.calculate_trading_days('2024-01-01', '2024-01-01')
            self.assertEqual(result, 1)
    
    @patch('models.non_trading_day.NonTradingDay.query')
    def test_get_non_trading_days_in_range(self, mock_query):
        """测试获取日期范围内的非交易日"""
        # 模拟查询结果
        mock_holidays = [MagicMock(), MagicMock()]
        mock_query.filter.return_value.order_by.return_value.all.return_value = mock_holidays
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        result = NonTradingDay.get_non_trading_days_in_range(start_date, end_date)
        self.assertEqual(len(result), 2)
    
    @patch('models.non_trading_day.NonTradingDay.is_trading_day')
    def test_get_next_trading_day(self, mock_is_trading_day):
        """测试获取下一个交易日"""
        # 模拟1月1日不是交易日，1月2日是交易日
        mock_is_trading_day.side_effect = lambda d: d.day == 2
        
        check_date = date(2024, 1, 1)
        result = NonTradingDay.get_next_trading_day(check_date)
        
        expected_date = date(2024, 1, 2)
        self.assertEqual(result, expected_date)
    
    @patch('models.non_trading_day.NonTradingDay.is_trading_day')
    def test_get_previous_trading_day(self, mock_is_trading_day):
        """测试获取上一个交易日"""
        # 模拟1月2日不是交易日，1月1日是交易日
        mock_is_trading_day.side_effect = lambda d: d.day == 1
        
        check_date = date(2024, 1, 2)
        result = NonTradingDay.get_previous_trading_day(check_date)
        
        expected_date = date(2024, 1, 1)
        self.assertEqual(result, expected_date)
    
    def test_to_dict(self):
        """测试转换为字典"""
        # 创建一个模拟的NonTradingDay实例
        holiday = NonTradingDay()
        holiday.id = 1
        holiday.date = date(2024, 1, 1)
        holiday.name = '元旦'
        holiday.type = 'holiday'
        holiday.description = '新年第一天'
        
        # 模拟父类的to_dict方法
        with patch.object(NonTradingDay.__bases__[0], 'to_dict') as mock_super_to_dict:
            mock_super_to_dict.return_value = {
                'id': 1,
                'name': '元旦',
                'type': 'holiday',
                'description': '新年第一天',
                'date': date(2024, 1, 1)
            }
            
            result = holiday.to_dict()
            
            # 验证日期被转换为ISO格式字符串
            self.assertEqual(result['date'], '2024-01-01')


class TestNonTradingDayService(unittest.TestCase):
    """非交易日服务测试"""
    
    def setUp(self):
        """测试前准备"""
        self.service = NonTradingDayService
        self.test_date = date(2024, 1, 1)
    
    @patch('services.non_trading_day_service.NonTradingDay.is_trading_day')
    def test_is_trading_day(self, mock_is_trading_day):
        """测试判断交易日"""
        mock_is_trading_day.return_value = True
        
        result = self.service.is_trading_day(self.test_date)
        self.assertTrue(result)
        mock_is_trading_day.assert_called_once_with(self.test_date)
    
    @patch('services.non_trading_day_service.NonTradingDay.is_trading_day')
    def test_is_trading_day_exception(self, mock_is_trading_day):
        """测试判断交易日异常处理"""
        mock_is_trading_day.side_effect = Exception('Database error')
        
        with self.assertRaises(DatabaseError):
            self.service.is_trading_day(self.test_date)
    
    @patch('services.non_trading_day_service.NonTradingDay.calculate_trading_days')
    def test_calculate_trading_days(self, mock_calculate):
        """测试计算交易日数量"""
        mock_calculate.return_value = 5
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 5)
        
        result = self.service.calculate_trading_days(start_date, end_date)
        self.assertEqual(result, 5)
        mock_calculate.assert_called_once_with(start_date, end_date)
    
    def test_calculate_holding_days_with_sell_date(self):
        """测试计算持仓天数（有卖出日期）"""
        with patch.object(self.service.model, 'calculate_trading_days', return_value=10):
            buy_date = '2024-01-01'
            sell_date = '2024-01-15'
            
            result = self.service.calculate_holding_days(buy_date, sell_date)
            self.assertEqual(result, 10)
    
    @patch('services.non_trading_day_service.date')
    def test_calculate_holding_days_without_sell_date(self, mock_date):
        """测试计算持仓天数（无卖出日期，使用今天）"""
        mock_date.today.return_value = date(2024, 1, 15)
        
        with patch.object(self.service.model, 'calculate_trading_days', return_value=10):
            buy_date = '2024-01-01'
            
            result = self.service.calculate_holding_days(buy_date)
            self.assertEqual(result, 10)
    
    @patch('services.non_trading_day_service.NonTradingDay.get_non_trading_days_in_range')
    def test_get_non_trading_days_in_range(self, mock_get_range):
        """测试获取日期范围内的非交易日"""
        mock_holidays = [MagicMock()]
        mock_holidays[0].to_dict.return_value = {'date': '2024-01-01', 'name': '元旦'}
        mock_get_range.return_value = mock_holidays
        
        start_date = '2024-01-01'
        end_date = '2024-01-31'
        
        result = self.service.get_non_trading_days_in_range(start_date, end_date)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], '元旦')
    
    @patch('services.non_trading_day_service.NonTradingDay.query')
    def test_add_holiday_success(self, mock_query):
        """测试成功添加节假日"""
        # 模拟不存在相同日期的记录
        mock_query.filter_by.return_value.first.return_value = None
        
        with patch.object(self.service, 'create') as mock_create:
            mock_holiday = MagicMock()
            mock_holiday.to_dict.return_value = {'date': '2024-01-01', 'name': '元旦'}
            mock_create.return_value = mock_holiday
            
            result = self.service.add_holiday('2024-01-01', '元旦', '新年第一天')
            
            self.assertEqual(result['name'], '元旦')
            mock_create.assert_called_once()
    
    @patch('services.non_trading_day_service.NonTradingDay.query')
    def test_add_holiday_duplicate(self, mock_query):
        """测试添加重复节假日"""
        # 模拟存在相同日期的记录
        mock_query.filter_by.return_value.first.return_value = MagicMock()
        
        with self.assertRaises(ValidationError):
            self.service.add_holiday('2024-01-01', '元旦')
    
    @patch('services.non_trading_day_service.NonTradingDay.query')
    def test_remove_holiday_success(self, mock_query):
        """测试成功移除节假日"""
        mock_holiday = MagicMock()
        mock_holiday.delete.return_value = True
        mock_query.filter_by.return_value.first.return_value = mock_holiday
        
        result = self.service.remove_holiday('2024-01-01')
        self.assertTrue(result)
    
    @patch('services.non_trading_day_service.NonTradingDay.query')
    def test_remove_holiday_not_found(self, mock_query):
        """测试移除不存在的节假日"""
        mock_query.filter_by.return_value.first.return_value = None
        
        with self.assertRaises(ValidationError):
            self.service.remove_holiday('2024-01-01')
    
    @patch('services.non_trading_day_service.NonTradingDay.query')
    def test_get_holidays_by_year(self, mock_query):
        """测试按年份获取节假日"""
        mock_holidays = [MagicMock(), MagicMock()]
        for i, holiday in enumerate(mock_holidays):
            holiday.to_dict.return_value = {'date': f'2024-01-0{i+1}', 'name': f'节假日{i+1}'}
        
        mock_query.filter.return_value.order_by.return_value.all.return_value = mock_holidays
        
        result = self.service.get_holidays_by_year(2024)
        self.assertEqual(len(result), 2)
    
    @patch('services.non_trading_day_service.NonTradingDay.get_next_trading_day')
    def test_get_next_trading_day(self, mock_get_next):
        """测试获取下一个交易日"""
        mock_get_next.return_value = date(2024, 1, 2)
        
        result = self.service.get_next_trading_day('2024-01-01')
        self.assertEqual(result, '2024-01-02')
    
    @patch('services.non_trading_day_service.NonTradingDay.get_next_trading_day')
    def test_get_next_trading_day_none(self, mock_get_next):
        """测试获取下一个交易日返回None"""
        mock_get_next.return_value = None
        
        result = self.service.get_next_trading_day('2024-01-01')
        self.assertIsNone(result)
    
    def test_bulk_add_holidays_success(self):
        """测试批量添加节假日成功"""
        holidays_data = [
            {'date': '2024-01-01', 'name': '元旦'},
            {'date': '2024-02-10', 'name': '春节'}
        ]
        
        with patch.object(self.service, 'add_holiday') as mock_add:
            mock_add.side_effect = [
                {'date': '2024-01-01', 'name': '元旦'},
                {'date': '2024-02-10', 'name': '春节'}
            ]
            
            result = self.service.bulk_add_holidays(holidays_data)
            self.assertEqual(len(result), 2)
            self.assertEqual(mock_add.call_count, 2)
    
    def test_bulk_add_holidays_with_duplicates(self):
        """测试批量添加节假日（包含重复）"""
        holidays_data = [
            {'date': '2024-01-01', 'name': '元旦'},
            {'date': '2024-01-02', 'name': '重复日期'}
        ]
        
        with patch.object(self.service, 'add_holiday') as mock_add:
            # 第一个成功，第二个抛出ValidationError
            mock_add.side_effect = [
                {'date': '2024-01-01', 'name': '元旦'},
                ValidationError('重复日期')
            ]
            
            result = self.service.bulk_add_holidays(holidays_data)
            self.assertEqual(len(result), 1)  # 只有一个成功添加
    
    @patch('services.non_trading_day_service.NonTradingDay.calculate_trading_days')
    @patch('services.non_trading_day_service.NonTradingDayService.get_non_trading_days_in_range')
    def test_get_trading_calendar(self, mock_get_range, mock_calculate):
        """测试获取交易日历"""
        mock_calculate.return_value = 250
        mock_get_range.return_value = [{'date': '2024-01-01', 'name': '元旦'}]
        
        # 模拟每月交易日计算
        with patch.object(self.service, 'calculate_trading_days') as mock_monthly_calc:
            mock_monthly_calc.return_value = 20
            
            result = self.service.get_trading_calendar(2024)
            
            self.assertEqual(result['year'], 2024)
            self.assertEqual(result['total_trading_days'], 250)
            self.assertEqual(len(result['non_trading_days']), 1)
            self.assertEqual(len(result['monthly_trading_days']), 12)


if __name__ == '__main__':
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加模型测试
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNonTradingDayModel))
    
    # 添加服务测试
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNonTradingDayService))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果
    print(f"\n测试结果:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # 返回退出码
    exit_code = 0 if result.wasSuccessful() else 1
    print(f"\n测试{'通过' if exit_code == 0 else '失败'}")
    exit(exit_code)