#!/usr/bin/env python3
"""
测试修复后的API调用
"""
import requests
import json

def test_api_call():
    """测试API调用"""
    
    # 测试数据
    test_data = {
        "stock_code": "000776",
        "stock_name": "广发证券",
        "trade_type": "buy",
        "trade_date": "2025-08-04T16:20",
        "price": "19.453",
        "quantity": "31100",
        "reason": "单针二十战法",
        "use_batch_profit_taking": "on",
        "stop_loss_price": "19",
        "profit_ratio_1": "10",
        "target_price_1": "21.40",
        "sell_ratio_1": "20",
        "profit_ratio_2": "20",
        "target_price_2": "23.34",
        "sell_ratio_2": "40",
        "profit_ratio_3": "30",
        "target_price_3": "25.29",
        "sell_ratio_3": "40",
        "notes": ""
    }
    
    print("=== 测试修复后的API调用 ===")
    print(f"发送数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        # 发送POST请求
        response = requests.post(
            'http://localhost:5001/api/trades',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            data = result.get('data', {})
            print(f"\n✅ 创建成功!")
            print(f"交易记录ID: {data.get('id')}")
            print(f"股票代码: {data.get('stock_code')}")
            print(f"使用分批止盈: {data.get('use_batch_profit_taking')}")
            print(f"总预期收益率: {data.get('total_expected_profit_ratio', 0):.4f}")
            print(f"总卖出比例: {data.get('total_sell_ratio', 0):.2f}")
            
            # 检查止盈目标
            profit_targets = data.get('profit_targets', [])
            if profit_targets:
                print(f"止盈目标数量: {len(profit_targets)}")
                for i, target in enumerate(profit_targets):
                    print(f"  目标 {i+1}: 价格={target.get('target_price')}, 止盈比例={target.get('profit_ratio'):.1%}, 卖出比例={target.get('sell_ratio'):.1%}, 预期收益={target.get('expected_profit_ratio'):.1%}")
        else:
            print(f"\n❌ 创建失败!")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"\n❌ 请求失败: {str(e)}")

if __name__ == "__main__":
    test_api_call()