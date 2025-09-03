#!/usr/bin/env python3
"""
测试复盘组件集成功能
"""
import sys
import os
import requests
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_review_api_endpoints():
    """测试复盘API端点"""
    base_url = "http://localhost:5000/api"
    
    print("=== 测试复盘API端点 ===")
    
    # 测试获取历史交易列表
    print("\n1. 测试获取历史交易列表...")
    try:
        response = requests.get(f"{base_url}/historical-trades")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data', {}).get('trades'):
                trades = data['data']['trades']
                print(f"获取到 {len(trades)} 条历史交易记录")
                
                if trades:
                    # 使用第一条记录测试复盘功能
                    test_trade = trades[0]
                    trade_id = test_trade['id']
                    print(f"使用交易ID {trade_id} 进行复盘测试")
                    
                    # 测试获取复盘记录
                    print(f"\n2. 测试获取复盘记录 (交易ID: {trade_id})...")
                    review_response = requests.get(f"{base_url}/trade-reviews/by-trade/{trade_id}")
                    print(f"状态码: {review_response.status_code}")
                    
                    if review_response.status_code == 200:
                        review_data = review_response.json()
                        if review_data.get('success') and review_data.get('data'):
                            print("已存在复盘记录")
                            print(f"复盘标题: {review_data['data'].get('review_title', '无标题')}")
                        else:
                            print("该交易暂无复盘记录")
                            
                            # 测试创建复盘记录
                            print(f"\n3. 测试创建复盘记录...")
                            create_data = {
                                "historical_trade_id": trade_id,
                                "review_title": f"测试复盘 - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                "review_content": "这是一个测试复盘记录，用于验证复盘功能是否正常工作。",
                                "review_type": "general",
                                "strategy_score": 4,
                                "timing_score": 3,
                                "risk_control_score": 4,
                                "overall_score": 4,
                                "key_learnings": "测试学习点：复盘功能正常工作",
                                "improvement_areas": "测试改进点：继续完善功能"
                            }
                            
                            create_response = requests.post(
                                f"{base_url}/trade-reviews",
                                json=create_data,
                                headers={'Content-Type': 'application/json'}
                            )
                            print(f"创建复盘状态码: {create_response.status_code}")
                            
                            if create_response.status_code == 201:
                                create_result = create_response.json()
                                if create_result.get('success'):
                                    review_id = create_result['data']['id']
                                    print(f"复盘记录创建成功，ID: {review_id}")
                                    
                                    # 测试更新复盘记录
                                    print(f"\n4. 测试更新复盘记录...")
                                    update_data = {
                                        "review_title": f"更新的测试复盘 - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                        "review_content": "这是更新后的复盘内容。",
                                        "overall_score": 5
                                    }
                                    
                                    update_response = requests.put(
                                        f"{base_url}/trade-reviews/{review_id}",
                                        json=update_data,
                                        headers={'Content-Type': 'application/json'}
                                    )
                                    print(f"更新复盘状态码: {update_response.status_code}")
                                    
                                    if update_response.status_code == 200:
                                        print("复盘记录更新成功")
                                    else:
                                        print(f"更新失败: {update_response.text}")
                                    
                                    # 测试获取单个复盘记录
                                    print(f"\n5. 测试获取单个复盘记录...")
                                    get_response = requests.get(f"{base_url}/trade-reviews/{review_id}")
                                    print(f"获取复盘状态码: {get_response.status_code}")
                                    
                                    if get_response.status_code == 200:
                                        get_result = get_response.json()
                                        if get_result.get('success'):
                                            print("复盘记录获取成功")
                                            print(f"标题: {get_result['data'].get('review_title')}")
                                            print(f"评分: {get_result['data'].get('overall_score')}")
                                        else:
                                            print(f"获取失败: {get_result.get('message')}")
                                    else:
                                        print(f"获取失败: {get_response.text}")
                                else:
                                    print(f"创建失败: {create_result.get('message')}")
                            else:
                                print(f"创建失败: {create_response.text}")
                    else:
                        print(f"获取复盘记录失败: {review_response.text}")
                else:
                    print("没有历史交易记录可用于测试")
            else:
                print("没有获取到历史交易记录")
        else:
            print(f"获取历史交易失败: {response.text}")
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

def test_frontend_files():
    """测试前端文件是否存在"""
    print("\n=== 测试前端文件 ===")
    
    files_to_check = [
        'static/js/review-editor.js',
        'static/js/image-uploader.js',
        'static/js/review-viewer.js',
        'templates/historical_trades.html'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✓ {file_path} 存在")
            
            # 检查文件大小
            size = os.path.getsize(file_path)
            print(f"  文件大小: {size} 字节")
            
            # 检查关键内容
            if file_path.endswith('.js'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'class ' in content:
                        class_names = []
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip().startswith('class '):
                                class_name = line.strip().split()[1].split('(')[0].split('{')[0]
                                class_names.append(class_name)
                        if class_names:
                            print(f"  包含类: {', '.join(class_names)}")
        else:
            print(f"✗ {file_path} 不存在")

def main():
    """主函数"""
    print("复盘组件集成测试")
    print("=" * 50)
    
    # 测试前端文件
    test_frontend_files()
    
    # 测试API端点
    try:
        test_review_api_endpoints()
    except requests.exceptions.ConnectionError:
        print("\n注意: 无法连接到服务器，请确保应用正在运行 (python app.py)")
    except Exception as e:
        print(f"\nAPI测试出现错误: {str(e)}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()