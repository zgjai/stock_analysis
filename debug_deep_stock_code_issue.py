#!/usr/bin/env python3
"""
深度调试股票代码传递问题
"""
import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_request_data_flow():
    """测试请求数据流"""
    print("=== 测试请求数据流 ===")
    
    # 模拟前端发送的数据
    frontend_data = {
        'stock_code': '000001',
        'stock_name': '平安银行',
        'trade_type': 'buy',
        'price': '10.50',
        'quantity': '1000',
        'trade_date': '2025-08-19T13:25:00',
        'reason': '少妇B1战法',
        'notes': '测试交易记录'
    }
    
    print("1. 前端发送的数据:")
    print(json.dumps(frontend_data, indent=2, ensure_ascii=False))
    
    # 检查每个字段的值和类型
    print("\n2. 字段详细检查:")
    for key, value in frontend_data.items():
        print(f"   {key}: '{value}' (类型: {type(value).__name__}, 长度: {len(str(value)) if value else 'N/A'})")
    
    # 检查stock_code字段
    stock_code = frontend_data.get('stock_code')
    print(f"\n3. stock_code 详细分析:")
    print(f"   值: '{stock_code}'")
    print(f"   类型: {type(stock_code)}")
    print(f"   是否为空: {not stock_code}")
    print(f"   是否为None: {stock_code is None}")
    print(f"   是否为空字符串: {stock_code == ''}")
    print(f"   长度: {len(stock_code) if stock_code else 'N/A'}")
    print(f"   布尔值: {bool(stock_code)}")
    
    return frontend_data

def test_api_route_validation():
    """测试API路由验证逻辑"""
    print("\n=== 测试API路由验证逻辑 ===")
    
    try:
        from api.trading_routes import create_trade
        from flask import Flask, request
        import json
        
        app = Flask(__name__)
        
        # 模拟请求数据
        test_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 10.50,
            'quantity': 1000,
            'trade_date': datetime.now().isoformat(),
            'reason': '少妇B1战法',
            'notes': '测试交易记录'
        }
        
        print("测试数据:", json.dumps(test_data, indent=2, ensure_ascii=False, default=str))
        
        # 检查必填字段验证逻辑
        required_fields = ['stock_code', 'stock_name', 'trade_type', 'price', 'quantity', 'reason']
        print("\n必填字段检查:")
        for field in required_fields:
            value = test_data.get(field)
            is_missing = field not in test_data or test_data[field] is None
            print(f"   {field}: {value} - {'缺失' if is_missing else '存在'}")
        
        return test_data
        
    except Exception as e:
        print(f"API路由测试失败: {str(e)}")
        return None

def test_validators_directly():
    """直接测试验证器函数"""
    print("\n=== 直接测试验证器函数 ===")
    
    try:
        from utils.validators import validate_stock_code
        
        test_codes = ['000001', '', None, '00001', '0000001', 'abc123']
        
        for code in test_codes:
            try:
                result = validate_stock_code(code)
                print(f"   '{code}' -> 验证通过")
            except Exception as e:
                print(f"   '{code}' -> 验证失败: {str(e)}")
                
    except Exception as e:
        print(f"验证器测试失败: {str(e)}")

def test_trading_service():
    """测试TradingService"""
    print("\n=== 测试TradingService ===")
    
    try:
        from services.trading_service import TradingService
        from datetime import datetime
        
        test_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 10.50,
            'quantity': 1000,
            'trade_date': datetime.now(),
            'reason': '少妇B1战法',
            'notes': '测试交易记录'
        }
        
        print("TradingService 测试数据:")
        print(json.dumps({k: str(v) for k, v in test_data.items()}, indent=2, ensure_ascii=False))
        
        # 检查每个字段
        print("\n字段检查:")
        for key, value in test_data.items():
            print(f"   {key}: {value} ({type(value).__name__})")
        
        # 尝试创建交易记录
        print("\n尝试创建交易记录...")
        trade = TradingService.create_trade(test_data)
        print(f"✓ 交易记录创建成功: ID={trade.id}")
        
        # 清理测试数据
        TradingService.delete_trade(trade.id)
        print("✓ 测试数据已清理")
        
        return True
        
    except Exception as e:
        print(f"✗ TradingService 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model_validation():
    """测试模型验证"""
    print("\n=== 测试模型验证 ===")
    
    try:
        from models.trade_record import TradeRecord
        from datetime import datetime
        
        test_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 10.50,
            'quantity': 1000,
            'trade_date': datetime.now(),
            'reason': '少妇B1战法',
            'notes': '测试交易记录'
        }
        
        print("模型验证测试数据:")
        print(json.dumps({k: str(v) for k, v in test_data.items()}, indent=2, ensure_ascii=False))
        
        # 尝试创建模型实例
        print("\n尝试创建模型实例...")
        trade = TradeRecord(**test_data)
        print(f"✓ 模型实例创建成功: {trade}")
        
        return True
        
    except Exception as e:
        print(f"✗ 模型验证测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始深度调试股票代码传递问题...")
    print("=" * 60)
    
    # 1. 测试请求数据流
    frontend_data = test_request_data_flow()
    
    # 2. 测试验证器函数
    test_validators_directly()
    
    # 3. 测试API路由
    api_data = test_api_route_validation()
    
    # 4. 测试模型验证
    model_ok = test_model_validation()
    
    # 5. 测试TradingService
    service_ok = test_trading_service()
    
    print("\n" + "=" * 60)
    print("调试总结:")
    print(f"- 前端数据: {'✓' if frontend_data else '✗'}")
    print(f"- 模型验证: {'✓' if model_ok else '✗'}")
    print(f"- 服务层: {'✓' if service_ok else '✗'}")
    
    if not service_ok:
        print("\n🔍 问题可能在服务层或数据库连接")
        print("建议检查:")
        print("1. 数据库连接是否正常")
        print("2. 必填字段验证逻辑")
        print("3. 数据类型转换")
    else:
        print("\n🎉 所有测试通过，问题可能已解决")

if __name__ == '__main__':
    main()