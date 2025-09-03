#!/usr/bin/env python3
"""
测试收益分布配置API端点
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from app import create_app
from extensions import db
from models.profit_distribution_config import ProfitDistributionConfig


def test_api_endpoints():
    """测试API端点"""
    app = create_app()
    
    with app.test_client() as client:
        print("=== 测试收益分布配置API ===")
        
        # 1. 测试获取配置列表
        print("\n1. 测试获取配置列表...")
        response = client.get('/api/profit-distribution/configs')
        assert response.status_code == 200
        data = response.get_json()
        print(f"获取到 {len(data['data'])} 个配置")
        
        # 2. 测试创建新配置
        print("\n2. 测试创建新配置...")
        new_config = {
            'range_name': '测试区间',
            'min_profit_rate': 1.0,   # 100% (不与现有区间重叠)
            'max_profit_rate': 2.0,   # 200%
            'sort_order': 10,
            'is_active': True
        }
        response = client.post('/api/profit-distribution/configs', 
                             json=new_config,
                             content_type='application/json')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_json()}")
        assert response.status_code == 200
        created_config = response.get_json()
        print(f"创建配置成功: {created_config['data']['range_name']}")
        config_id = created_config['data']['id']
        
        # 3. 测试更新配置
        print("\n3. 测试更新配置...")
        update_data = {
            'range_name': '更新后的测试区间',
            'is_active': False
        }
        response = client.put(f'/api/profit-distribution/configs/{config_id}',
                            json=update_data,
                            content_type='application/json')
        assert response.status_code == 200
        print("配置更新成功")
        
        # 4. 测试获取分析结果
        print("\n4. 测试获取分析结果...")
        response = client.get('/api/profit-distribution/analysis?use_trade_pairs=true')
        assert response.status_code == 200
        analysis_data = response.get_json()
        print(f"分析结果: {analysis_data['data']['total_trades']} 笔交易")
        
        # 5. 测试获取交易配对分析
        print("\n5. 测试获取交易配对分析...")
        response = client.get('/api/profit-distribution/trade-pairs')
        assert response.status_code == 200
        pairs_data = response.get_json()
        print(f"交易配对: {pairs_data['data']['total_completed_trades']} 笔完成交易")
        
        # 6. 测试批量更新排序
        print("\n6. 测试批量更新排序...")
        batch_update = {
            'configs': [
                {'id': config_id, 'sort_order': 5}
            ]
        }
        response = client.post('/api/profit-distribution/configs/batch-update',
                             json=batch_update,
                             content_type='application/json')
        assert response.status_code == 200
        print("批量更新成功")
        
        # 7. 测试删除配置
        print("\n7. 测试删除配置...")
        response = client.delete(f'/api/profit-distribution/configs/{config_id}')
        assert response.status_code == 200
        print("配置删除成功")
        
        # 8. 测试重置默认配置
        print("\n8. 测试重置默认配置...")
        response = client.post('/api/profit-distribution/configs/reset-default')
        assert response.status_code == 200
        print("重置默认配置成功")
        
        print("\n=== API测试完成 ===")


if __name__ == '__main__':
    test_api_endpoints()