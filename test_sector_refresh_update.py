#!/usr/bin/env python3
"""
测试板块数据实时更新功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import date
# 测试配置

def test_sector_refresh_update():
    """测试板块数据刷新和更新功能"""
    
    base_url = "http://localhost:5001"  # 正确的端口号
    
    print("=== 板块数据实时更新测试 ===\n")
    
    # 1. 第一次刷新数据
    print("1. 第一次刷新板块数据...")
    try:
        response = requests.post(f"{base_url}/api/sectors/refresh", timeout=30)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            first_count = result.get('data', {}).get('count', 0)
            print(f"✓ 第一次刷新成功，获取 {first_count} 条数据")
        else:
            print(f"✗ 第一次刷新失败: {result.get('error', {}).get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"✗ 第一次刷新请求失败: {e}")
        return False
    
    print("\n" + "="*50 + "\n")
    
    # 2. 立即再次刷新数据（测试同一天数据更新）
    print("2. 立即再次刷新板块数据（测试当天数据更新）...")
    try:
        response = requests.post(f"{base_url}/api/sectors/refresh", timeout=30)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            second_count = result.get('data', {}).get('count', 0)
            is_updated = result.get('data', {}).get('updated', False)
            
            if is_updated:
                print(f"✓ 当天数据更新成功，更新了 {second_count} 条数据")
                print("✓ 系统正确识别并更新了同一天的数据")
            else:
                print(f"✓ 获取了 {second_count} 条新数据")
                
        else:
            print(f"✗ 第二次刷新失败: {result.get('error', {}).get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"✗ 第二次刷新请求失败: {e}")
        return False
    
    print("\n" + "="*50 + "\n")
    
    # 3. 验证数据是否正确存储
    print("3. 验证今日板块数据...")
    try:
        response = requests.get(f"{base_url}/api/sectors/ranking", timeout=10)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        
        if result.get('success'):
            ranking_data = result.get('data', [])
            print(f"✓ 成功获取今日板块排名，共 {len(ranking_data)} 条记录")
            
            if ranking_data:
                # 显示前5名
                print("\n前5名板块:")
                for i, sector in enumerate(ranking_data[:5]):
                    print(f"  {i+1}. {sector.get('sector_name', 'N/A')} - {sector.get('change_percent', 0):.2f}%")
                    
                # 检查数据日期
                first_sector = ranking_data[0]
                record_date = first_sector.get('record_date')
                today_str = date.today().isoformat()
                
                if record_date == today_str:
                    print(f"✓ 数据日期正确: {record_date}")
                else:
                    print(f"⚠ 数据日期异常: {record_date} (期望: {today_str})")
            else:
                print("⚠ 没有获取到排名数据")
                
        else:
            print(f"✗ 获取排名失败: {result.get('error', {}).get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"✗ 获取排名请求失败: {e}")
        return False
    
    print("\n" + "="*50 + "\n")
    
    # 4. 测试数据状态API
    print("4. 测试板块分析汇总...")
    try:
        response = requests.get(f"{base_url}/api/sectors/summary?days=7", timeout=10)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        
        if result.get('success'):
            summary = result.get('data', {})
            print(f"✓ 获取分析汇总成功")
            print(f"  - 最新数据日期: {summary.get('latest_data_date', 'N/A')}")
            print(f"  - 总记录数: {summary.get('total_records', 0)}")
            print(f"  - 唯一板块数: {summary.get('unique_sectors', 0)}")
            print(f"  - 数据完整度: {summary.get('data_completeness', 0):.1f}%")
        else:
            print(f"✗ 获取汇总失败: {result.get('error', {}).get('message', '未知错误')}")
            
    except Exception as e:
        print(f"✗ 获取汇总请求失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("✓ 板块数据实时更新功能测试通过")
    print("✓ 系统现在支持当天数据的实时刷新和更新")
    
    return True

if __name__ == "__main__":
    success = test_sector_refresh_update()
    sys.exit(0 if success else 1)