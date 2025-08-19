#!/usr/bin/env python3
"""
测试分批止盈API功能
"""
import requests
import json
from datetime import datetime

# 服务器配置
BASE_URL = 'http://localhost:5001'
API_BASE = f'{BASE_URL}/api'

def test_api_connection():
    """测试API连接"""
    print("测试API连接...")
    try:
        response = requests.get(f'{API_BASE}/health', timeout=5)
        print(f"健康检查: {response.status_code}")
        if response.status_code == 200:
            print("✅ API连接正常")
            return True
        else:
            print(f"❌ API连接异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def test_create_batch_profit_trade():
    """测试创建分批止盈交易记录"""
    print("\n测试创建分批止盈交易记录...")
    
    trade_data = {
        "stock_code": "000001",
        "stock_name": "平安银行",
        "trade_type": "buy",
        "quantity": 1000,
        "price": 20.00,
        "reason": "技术分析",
        "use_batch_profit_taking": True,
        "profit_targets": [
            {
                "target_price": 22.00,
                "sell_ratio": 0.30,
                "sequence_order": 1
            },
            {
                "target_price": 24.00,
                "sell_ratio": 0.40,
                "sequence_order": 2
            },
            {
                "target_price": 26.00,
                "sell_ratio": 0.30,
                "sequence_order": 3
            }
        ]
    }
    
    try:
        response = requests.post(
            f'{API_BASE}/trades',
            json=trade_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ 创建分批止盈交易记录成功")
            print(f"交易记录ID: {data['data']['id']}")
            
            # 检查是否包含止盈目标
            if 'profit_targets' in data['data']:
                targets = data['data']['profit_targets']
                print(f"止盈目标数量: {len(targets)}")
                for i, target in enumerate(targets):
                    print(f"  目标{i+1}: 价格={target['target_price']}, 比例={target['sell_ratio']}%")
            
            return data['data']['id']
        else:
            print(f"❌ 创建失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误信息: {error_data}")
            except:
                print(f"响应内容: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_get_trade_with_targets(trade_id):
    """测试获取包含止盈目标的交易记录"""
    print(f"\n测试获取交易记录 {trade_id}...")
    
    try:
        response = requests.get(f'{API_BASE}/trades/{trade_id}', timeout=5)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取交易记录成功")
            
            trade = data['data']
            print(f"股票: {trade['stock_name']} ({trade['stock_code']})")
            print(f"类型: {trade['trade_type']}")
            print(f"价格: {trade['price']}")
            print(f"数量: {trade['quantity']}")
            print(f"使用分批止盈: {trade.get('use_batch_profit_taking', False)}")
            
            if 'profit_targets' in trade:
                targets = trade['profit_targets']
                print(f"止盈目标数量: {len(targets)}")
                for target in targets:
                    print(f"  目标价格: {target['target_price']}, 卖出比例: {target['sell_ratio']}%")
            
            return True
        else:
            print(f"❌ 获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_calculate_batch_profit():
    """测试计算分批止盈预期收益"""
    print("\n测试计算分批止盈预期收益...")
    
    calculation_data = {
        "buy_price": 20.00,
        "quantity": 1000,
        "profit_targets": [
            {
                "target_price": 22.00,
                "sell_ratio": 0.30
            },
            {
                "target_price": 24.00,
                "sell_ratio": 0.40
            },
            {
                "target_price": 26.00,
                "sell_ratio": 0.30
            }
        ]
    }
    
    try:
        response = requests.post(
            f'{API_BASE}/trades/calculate-batch-profit',
            json=calculation_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 计算分批止盈预期收益成功")
            
            result = data['data']
            print(f"总预期收益率: {result['total_expected_profit_ratio']:.2%}")
            print(f"总卖出比例: {result['total_sell_ratio']:.2%}")
            print(f"目标详情数量: {len(result['targets_detail'])}")
            
            return True
        else:
            print(f"❌ 计算失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_validate_profit_targets():
    """测试验证止盈目标"""
    print("\n测试验证止盈目标...")
    
    # 测试有效的目标
    valid_targets = {
        "buy_price": 20.00,
        "profit_targets": [
            {
                "target_price": 22.00,
                "sell_ratio": 0.50
            },
            {
                "target_price": 24.00,
                "sell_ratio": 0.50
            }
        ]
    }
    
    try:
        response = requests.post(
            f'{API_BASE}/trades/validate-profit-targets',
            json=valid_targets,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"有效目标验证 - 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 验证结果: {data['data']['is_valid']}")
        
        # 测试无效的目标（比例超过100%）
        invalid_targets = {
            "buy_price": 20.00,
            "profit_targets": [
                {
                    "target_price": 22.00,
                    "sell_ratio": 0.60
                },
                {
                    "target_price": 24.00,
                    "sell_ratio": 0.60
                }
            ]
        }
        
        response = requests.post(
            f'{API_BASE}/trades/validate-profit-targets',
            json=invalid_targets,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"无效目标验证 - 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"验证结果: {data['data']['is_valid']}")
            if not data['data']['is_valid']:
                print(f"错误信息: {data['data']['validation_errors']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始分批止盈API功能测试")
    print("=" * 50)
    
    # 测试API连接
    if not test_api_connection():
        print("API连接失败，终止测试")
        return
    
    # 测试创建分批止盈交易记录
    trade_id = test_create_batch_profit_trade()
    
    if trade_id:
        # 测试获取交易记录
        test_get_trade_with_targets(trade_id)
    
    # 测试计算分批止盈预期收益
    test_calculate_batch_profit()
    
    # 测试验证止盈目标
    test_validate_profit_targets()
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == '__main__':
    main()