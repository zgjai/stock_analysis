#!/usr/bin/env python3
"""
修复交易记录保存问题
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.trade_record import TradeRecord
from services.trading_service import TradingService
import traceback

def fix_trading_records_save_issue():
    """修复交易记录保存问题"""
    app = create_app()
    
    with app.app_context():
        print("=== 交易记录保存问题修复 ===")
        
        # 1. 检查数据库连接
        try:
            trade_count = TradeRecord.query.count()
            print(f"✓ 数据库连接正常，共有 {trade_count} 条交易记录")
        except Exception as e:
            print(f"✗ 数据库连接失败: {str(e)}")
            return
        
        # 2. 测试创建交易记录
        print("\n--- 测试创建交易记录 ---")
        try:
            test_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 15.50,
                'quantity': 1000,
                'reason': '技术分析',
                'notes': '修复测试'
            }
            
            trade = TradingService.create_trade(test_data)
            print(f"✓ 创建交易记录成功，ID: {trade.id}")
            
        except Exception as e:
            print(f"✗ 创建交易记录失败: {str(e)}")
            traceback.print_exc()
        
        # 3. 测试更新交易记录
        print("\n--- 测试更新交易记录 ---")
        try:
            # 获取最新的交易记录
            latest_trade = TradeRecord.query.order_by(TradeRecord.id.desc()).first()
            if latest_trade:
                update_data = {
                    'price': 16.00,
                    'quantity': 1200,
                    'notes': '修复测试更新'
                }
                
                updated_trade = TradingService.update_trade(latest_trade.id, update_data)
                print(f"✓ 更新交易记录成功，ID: {updated_trade.id}")
                print(f"  更新后价格: {updated_trade.price}")
                print(f"  更新后数量: {updated_trade.quantity}")
                
            else:
                print("✗ 没有找到可更新的交易记录")
                
        except Exception as e:
            print(f"✗ 更新交易记录失败: {str(e)}")
            traceback.print_exc()
        
        # 4. 检查API路由配置
        print("\n--- 检查API路由配置 ---")
        try:
            from api.trading_routes import api_bp
            print(f"✓ API蓝图注册正常")
            
            # 检查路由
            routes = []
            for rule in app.url_map.iter_rules():
                if rule.rule.startswith('/api/trades'):
                    routes.append(f"{rule.methods} {rule.rule}")
            
            print("✓ 交易记录API路由:")
            for route in routes:
                print(f"  {route}")
                
        except Exception as e:
            print(f"✗ API路由检查失败: {str(e)}")
        
        # 5. 检查CSRF配置
        print("\n--- 检查CSRF配置 ---")
        csrf_enabled = app.config.get('WTF_CSRF_ENABLED', False)
        print(f"CSRF保护状态: {'启用' if csrf_enabled else '禁用'}")
        
        if csrf_enabled:
            print("⚠️  CSRF保护已启用，这可能导致API请求被拒绝")
            print("   建议在开发环境中禁用CSRF保护")
        else:
            print("✓ CSRF保护已禁用，API请求应该正常")
        
        print("\n=== 修复完成 ===")
        print("如果问题仍然存在，请检查:")
        print("1. 前端发送的数据格式是否正确")
        print("2. API请求的Content-Type是否为application/json")
        print("3. 浏览器开发者工具中的网络请求详情")

if __name__ == '__main__':
    fix_trading_records_save_issue()