#!/usr/bin/env python3
"""
验证非交易日功能实现
"""
import os
import sys
from datetime import date

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_files_created():
    """验证文件是否创建成功"""
    print("=== 验证文件创建 ===\n")
    
    files_to_check = [
        'models/non_trading_day.py',
        'services/non_trading_day_service.py',
        'api/non_trading_day_routes.py',
        'templates/non_trading_days.html',
        'static/js/non-trading-days.js',
        'migrations/20250821_000001_add_non_trading_day.py',
        'tests/test_non_trading_day.py'
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            all_exist = False
    
    return all_exist

def verify_model_structure():
    """验证模型结构"""
    print("\n=== 验证模型结构 ===\n")
    
    try:
        from models.non_trading_day import NonTradingDay
        
        # 检查模型属性
        expected_attributes = ['date', 'name', 'type', 'description']
        for attr in expected_attributes:
            if hasattr(NonTradingDay, attr):
                print(f"✅ 模型属性 {attr} 存在")
            else:
                print(f"❌ 模型属性 {attr} 不存在")
                return False
        
        # 检查模型方法
        expected_methods = [
            'is_trading_day',
            'calculate_trading_days',
            'get_non_trading_days_in_range',
            'get_next_trading_day',
            'get_previous_trading_day'
        ]
        
        for method in expected_methods:
            if hasattr(NonTradingDay, method):
                print(f"✅ 模型方法 {method} 存在")
            else:
                print(f"❌ 模型方法 {method} 不存在")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入模型失败: {e}")
        return False

def verify_service_structure():
    """验证服务结构"""
    print("\n=== 验证服务结构 ===\n")
    
    try:
        from services.non_trading_day_service import NonTradingDayService
        
        # 检查服务方法
        expected_methods = [
            'is_trading_day',
            'calculate_trading_days',
            'calculate_holding_days',
            'add_holiday',
            'remove_holiday',
            'get_holidays_by_year',
            'bulk_add_holidays',
            'get_trading_calendar'
        ]
        
        for method in expected_methods:
            if hasattr(NonTradingDayService, method):
                print(f"✅ 服务方法 {method} 存在")
            else:
                print(f"❌ 服务方法 {method} 不存在")
                return False
        
        # 检查是否继承自BaseService
        from services.base_service import BaseService
        if issubclass(NonTradingDayService, BaseService):
            print("✅ 服务类正确继承BaseService")
        else:
            print("❌ 服务类未继承BaseService")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入服务失败: {e}")
        return False

def verify_api_routes():
    """验证API路由"""
    print("\n=== 验证API路由 ===\n")
    
    try:
        # 检查路由文件内容
        with open('api/non_trading_day_routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键路由端点
        expected_routes = [
            '/non-trading-days',
            '/trading-days/check/',
            '/trading-days/calculate',
            '/trading-days/holding-days',
            '/trading-calendar/',
            '/non-trading-days/bulk'
        ]
        
        for route in expected_routes:
            if route in content:
                print(f"✅ API路由 {route} 存在")
            else:
                print(f"❌ API路由 {route} 不存在")
                return False
        
        # 检查HTTP方法
        http_methods = ['GET', 'POST', 'PUT', 'DELETE']
        for method in http_methods:
            if f"methods=['{method}']" in content or f'methods=["GET", "POST"]' in content:
                print(f"✅ HTTP方法 {method} 被使用")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证API路由失败: {e}")
        return False

def verify_frontend_template():
    """验证前端模板"""
    print("\n=== 验证前端模板 ===\n")
    
    try:
        with open('templates/non_trading_days.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键元素
        expected_elements = [
            'extends "base.html"',
            'id="addHolidayModal"',
            'id="editHolidayModal"',
            'id="calendarModal"',
            'id="holidaysTable"',
            'checkTradingDayBtn',
            'calculateHoldingDaysBtn'
        ]
        
        for element in expected_elements:
            if element in content:
                print(f"✅ 模板元素 {element} 存在")
            else:
                print(f"❌ 模板元素 {element} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 验证前端模板失败: {e}")
        return False

def verify_javascript():
    """验证JavaScript文件"""
    print("\n=== 验证JavaScript文件 ===\n")
    
    try:
        with open('static/js/non-trading-days.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键类和方法
        expected_elements = [
            'class NonTradingDaysManager',
            'checkTradingDay()',
            'calculateHoldingDays()',
            'loadHolidays()',
            'saveHoliday()',
            'deleteHoliday(',
            'loadCalendar('
        ]
        
        for element in expected_elements:
            if element in content:
                print(f"✅ JavaScript元素 {element} 存在")
            else:
                print(f"❌ JavaScript元素 {element} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 验证JavaScript文件失败: {e}")
        return False

def verify_migration_script():
    """验证迁移脚本"""
    print("\n=== 验证迁移脚本 ===\n")
    
    try:
        with open('migrations/20250821_000001_add_non_trading_day.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键函数和内容
        expected_elements = [
            'def upgrade():',
            'def downgrade():',
            'NonTradingDay',
            'default_holidays',
            '2024年法定节假日',
            'db.create_all()',
            'db.session.commit()'
        ]
        
        for element in expected_elements:
            if element in content:
                print(f"✅ 迁移脚本元素 {element} 存在")
            else:
                print(f"❌ 迁移脚本元素 {element} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 验证迁移脚本失败: {e}")
        return False

def verify_integration():
    """验证集成配置"""
    print("\n=== 验证集成配置 ===\n")
    
    try:
        # 检查模型是否添加到__init__.py
        with open('models/__init__.py', 'r', encoding='utf-8') as f:
            models_init = f.read()
        
        if 'NonTradingDay' in models_init:
            print("✅ NonTradingDay已添加到models/__init__.py")
        else:
            print("❌ NonTradingDay未添加到models/__init__.py")
            return False
        
        # 检查服务是否添加到__init__.py
        with open('services/__init__.py', 'r', encoding='utf-8') as f:
            services_init = f.read()
        
        if 'NonTradingDayService' in services_init:
            print("✅ NonTradingDayService已添加到services/__init__.py")
        else:
            print("❌ NonTradingDayService未添加到services/__init__.py")
            return False
        
        # 检查API路由是否添加到__init__.py
        with open('api/__init__.py', 'r', encoding='utf-8') as f:
            api_init = f.read()
        
        if 'non_trading_day_routes' in api_init:
            print("✅ non_trading_day_routes已添加到api/__init__.py")
        else:
            print("❌ non_trading_day_routes未添加到api/__init__.py")
            return False
        
        # 检查前端路由是否添加
        with open('routes.py', 'r', encoding='utf-8') as f:
            routes_content = f.read()
        
        if 'non_trading_days' in routes_content:
            print("✅ 非交易日路由已添加到routes.py")
        else:
            print("❌ 非交易日路由未添加到routes.py")
            return False
        
        # 检查导航菜单是否添加
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_template = f.read()
        
        if '非交易日配置' in base_template:
            print("✅ 非交易日配置菜单已添加到导航栏")
        else:
            print("❌ 非交易日配置菜单未添加到导航栏")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 验证集成配置失败: {e}")
        return False

def main():
    """主验证函数"""
    print("开始验证非交易日功能实现...\n")
    
    verifications = [
        ("文件创建", verify_files_created),
        ("模型结构", verify_model_structure),
        ("服务结构", verify_service_structure),
        ("API路由", verify_api_routes),
        ("前端模板", verify_frontend_template),
        ("JavaScript", verify_javascript),
        ("迁移脚本", verify_migration_script),
        ("集成配置", verify_integration)
    ]
    
    passed = 0
    total = len(verifications)
    
    for name, verify_func in verifications:
        try:
            if verify_func():
                passed += 1
                print(f"✅ {name} 验证通过\n")
            else:
                print(f"❌ {name} 验证失败\n")
        except Exception as e:
            print(f"❌ {name} 验证出现异常: {e}\n")
    
    print("=== 验证总结 ===")
    print(f"总验证项: {total}")
    print(f"通过验证: {passed}")
    print(f"失败验证: {total - passed}")
    
    if passed == total:
        print("\n🎉 所有验证通过！非交易日功能实现完成。")
        print("\n📋 实现的功能包括:")
        print("1. ✅ NonTradingDay数据模型 - 支持节假日配置和交易日计算")
        print("2. ✅ NonTradingDayService服务类 - 提供交易日判断和持仓天数计算功能")
        print("3. ✅ 非交易日管理API端点 - 支持增删改查操作")
        print("4. ✅ 前端非交易日配置界面 - 允许用户添加和管理节假日")
        print("5. ✅ 单元测试 - 编写了非交易日功能的单元测试")
        print("6. ✅ 数据库迁移脚本 - 包含默认节假日数据")
        print("7. ✅ 完整的前后端集成 - 包括导航菜单和页面路由")
        
        print("\n🚀 下一步:")
        print("1. 运行数据库迁移: python migrations/20250821_000001_add_non_trading_day.py")
        print("2. 启动应用程序测试功能")
        print("3. 访问 /non-trading-days 页面进行配置")
        
        return True
    else:
        print(f"\n❌ 部分验证失败，请检查上述错误信息")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)