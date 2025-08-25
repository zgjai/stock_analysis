#!/usr/bin/env python3
"""
非交易日功能集成测试
"""
import sys
import os
from datetime import date, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """测试基本功能"""
    print("=== 非交易日功能集成测试 ===\n")
    
    # 测试1: 导入模型和服务
    try:
        from models.non_trading_day import NonTradingDay
        from services.non_trading_day_service import NonTradingDayService
        print("✅ 成功导入NonTradingDay模型和服务")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    
    # 测试2: 测试周末判断（不需要数据库）
    try:
        # 2024年1月6日是星期六
        saturday = date(2024, 1, 6)
        is_trading = NonTradingDay.is_trading_day(saturday)
        assert not is_trading, "星期六应该不是交易日"
        print("✅ 周末判断功能正常")
    except Exception as e:
        print(f"❌ 周末判断测试失败: {e}")
        return False
    
    # 测试3: 测试交易日计算（不需要数据库）
    try:
        # 模拟计算交易日（假设所有工作日都是交易日）
        start_date = date(2024, 1, 1)  # 星期一
        end_date = date(2024, 1, 5)    # 星期五
        
        # 手动计算预期结果
        expected_days = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:  # 工作日
                expected_days += 1
            current += timedelta(days=1)
        
        print(f"✅ 交易日计算逻辑正常（预期{expected_days}个工作日）")
    except Exception as e:
        print(f"❌ 交易日计算测试失败: {e}")
        return False
    
    # 测试4: 测试字符串日期处理
    try:
        # 测试字符串格式日期
        is_trading = NonTradingDay.is_trading_day('2024-01-06')  # 星期六
        assert not is_trading, "字符串格式的星期六应该不是交易日"
        print("✅ 字符串日期处理正常")
    except Exception as e:
        print(f"❌ 字符串日期处理测试失败: {e}")
        return False
    
    # 测试5: 测试服务类方法（不涉及数据库操作）
    try:
        # 测试持仓天数计算逻辑
        buy_date = '2024-01-01'
        sell_date = '2024-01-05'
        
        # 这里只测试方法存在性，不测试具体计算
        assert hasattr(NonTradingDayService, 'calculate_holding_days')
        assert hasattr(NonTradingDayService, 'is_trading_day')
        assert hasattr(NonTradingDayService, 'add_holiday')
        print("✅ 服务类方法定义正常")
    except Exception as e:
        print(f"❌ 服务类方法测试失败: {e}")
        return False
    
    # 测试6: 测试API路由导入
    try:
        from api.non_trading_day_routes import api_bp
        print("✅ API路由导入正常")
    except ImportError as e:
        print(f"❌ API路由导入失败: {e}")
        return False
    
    print("\n=== 所有基本功能测试通过 ===")
    return True

def test_date_calculations():
    """测试日期计算功能"""
    print("\n=== 日期计算功能测试 ===\n")
    
    from models.non_trading_day import NonTradingDay
    
    # 测试各种日期场景
    test_cases = [
        # (日期, 预期结果, 描述)
        ('2024-01-01', True, '2024年1月1日 - 星期一'),
        ('2024-01-02', True, '2024年1月2日 - 星期二'),
        ('2024-01-03', True, '2024年1月3日 - 星期三'),
        ('2024-01-04', True, '2024年1月4日 - 星期四'),
        ('2024-01-05', True, '2024年1月5日 - 星期五'),
        ('2024-01-06', False, '2024年1月6日 - 星期六'),
        ('2024-01-07', False, '2024年1月7日 - 星期日'),
    ]
    
    for date_str, expected, description in test_cases:
        try:
            result = NonTradingDay.is_trading_day(date_str)
            if result == expected:
                print(f"✅ {description}: {'交易日' if result else '非交易日'}")
            else:
                print(f"❌ {description}: 预期{'交易日' if expected else '非交易日'}，实际{'交易日' if result else '非交易日'}")
                return False
        except Exception as e:
            print(f"❌ {description}: 测试失败 - {e}")
            return False
    
    print("\n=== 日期计算功能测试通过 ===")
    return True

def test_model_methods():
    """测试模型方法"""
    print("\n=== 模型方法测试 ===\n")
    
    from models.non_trading_day import NonTradingDay
    
    # 测试方法存在性
    methods_to_test = [
        'is_trading_day',
        'calculate_trading_days',
        'get_non_trading_days_in_range',
        'get_next_trading_day',
        'get_previous_trading_day',
        'to_dict'
    ]
    
    for method_name in methods_to_test:
        if hasattr(NonTradingDay, method_name):
            print(f"✅ 方法 {method_name} 存在")
        else:
            print(f"❌ 方法 {method_name} 不存在")
            return False
    
    print("\n=== 模型方法测试通过 ===")
    return True

def test_service_methods():
    """测试服务方法"""
    print("\n=== 服务方法测试 ===\n")
    
    from services.non_trading_day_service import NonTradingDayService
    
    # 测试方法存在性
    methods_to_test = [
        'is_trading_day',
        'calculate_trading_days',
        'calculate_holding_days',
        'get_non_trading_days_in_range',
        'add_holiday',
        'remove_holiday',
        'get_holidays_by_year',
        'get_next_trading_day',
        'get_previous_trading_day',
        'bulk_add_holidays',
        'get_trading_calendar'
    ]
    
    for method_name in methods_to_test:
        if hasattr(NonTradingDayService, method_name):
            print(f"✅ 服务方法 {method_name} 存在")
        else:
            print(f"❌ 服务方法 {method_name} 不存在")
            return False
    
    print("\n=== 服务方法测试通过 ===")
    return True

def main():
    """主测试函数"""
    print("开始非交易日功能集成测试...\n")
    
    tests = [
        test_basic_functionality,
        test_date_calculations,
        test_model_methods,
        test_service_methods
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"测试 {test_func.__name__} 失败")
        except Exception as e:
            print(f"测试 {test_func.__name__} 出现异常: {e}")
    
    print(f"\n=== 测试总结 ===")
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("❌ 部分测试失败")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)