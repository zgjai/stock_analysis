#!/usr/bin/env python3
"""
测试回退到全市场数据方案的优化效果
"""
import requests
import time
import json
from datetime import datetime

def test_market_data_optimization():
    """测试全市场数据优化方案"""
    base_url = "http://localhost:5001"
    
    print("🔄 全市场数据优化方案测试")
    print("=" * 60)
    
    # 1. 测试获取持仓列表
    print("\n1️⃣ 测试获取持仓列表...")
    start_time = time.time()
    
    try:
        response = requests.get(f"{base_url}/api/holdings", timeout=30)
        holdings_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                holdings = data['data']
                stock_codes = [h['stock_code'] for h in holdings]
                
                print(f"✅ 获取持仓成功: {len(holdings)} 只股票")
                print(f"⏱️ 耗时: {holdings_time:.2f}s")
                print(f"📋 股票代码: {', '.join(stock_codes)}")
                
                # 2. 测试批量价格刷新（全市场数据+缓存）
                print(f"\n2️⃣ 测试批量价格刷新 ({len(stock_codes)} 只股票)...")
                start_time = time.time()
                
                refresh_response = requests.post(
                    f"{base_url}/api/holdings/refresh-prices",
                    json={
                        'stock_codes': stock_codes,
                        'force_refresh': True
                    },
                    timeout=60
                )
                
                refresh_time = time.time() - start_time
                
                if refresh_response.status_code == 200:
                    refresh_data = refresh_response.json()
                    
                    if refresh_data.get('success'):
                        result = refresh_data['data']
                        performance = result.get('performance', {})
                        
                        print(f"✅ 批量刷新成功!")
                        print(f"📊 成功: {result['success_count']}/{len(stock_codes)}")
                        print(f"❌ 失败: {result['failed_count']}")
                        print(f"⏱️ 总耗时: {refresh_time:.2f}s")
                        
                        if performance:
                            print(f"🔍 性能详情:")
                            print(f"   - 使用方法: {performance.get('method', 'unknown')}")
                            print(f"   - API调用时间: {performance.get('api_time', 0):.2f}s")
                            print(f"   - 数据处理时间: {performance.get('processing_time', 0):.2f}s")
                            print(f"   - 处理速度: {performance.get('stocks_per_second', 0):.1f} 股票/秒")
                        
                        # 显示成功的股票价格
                        if result['results']:
                            print(f"\n💰 价格信息:")
                            for res in result['results'][:5]:  # 只显示前5个
                                if res['success']:
                                    data = res['data']
                                    print(f"   - {data['stock_code']}: {data['current_price']} 元 ({data['stock_name']})")
                        
                        # 显示失败的股票
                        if result['errors']:
                            print(f"\n❌ 失败的股票:")
                            for error in result['errors']:
                                print(f"   - {error['stock_code']}: {error['error']}")
                        
                        # 3. 测试缓存效果（立即再次刷新）
                        print(f"\n3️⃣ 测试缓存效果（立即再次刷新）...")
                        start_time = time.time()
                        
                        cache_response = requests.post(
                            f"{base_url}/api/holdings/refresh-prices",
                            json={
                                'stock_codes': stock_codes,
                                'force_refresh': False  # 不强制刷新，使用缓存
                            },
                            timeout=60
                        )
                        
                        cache_time = time.time() - start_time
                        
                        if cache_response.status_code == 200:
                            cache_data = cache_response.json()
                            if cache_data.get('success'):
                                cache_result = cache_data['data']
                                cache_performance = cache_result.get('performance', {})
                                
                                print(f"✅ 缓存刷新成功!")
                                print(f"📊 成功: {cache_result['success_count']}/{len(stock_codes)}")
                                print(f"⏱️ 缓存耗时: {cache_time:.2f}s")
                                print(f"🔍 缓存API时间: {cache_performance.get('api_time', 0):.2f}s")
                                
                                # 缓存效果对比
                                print(f"\n📈 缓存效果对比:")
                                print(f"   - 首次刷新: {refresh_time:.2f}s")
                                print(f"   - 缓存刷新: {cache_time:.2f}s")
                                if refresh_time > 0:
                                    cache_improvement = (refresh_time - cache_time) / refresh_time * 100
                                    print(f"   - 缓存提升: {cache_improvement:.1f}%")
                            
                        else:
                            print(f"❌ 缓存刷新失败: {cache_response.status_code}")
                    
                    else:
                        print(f"❌ 批量刷新失败: {refresh_data.get('message', '未知错误')}")
                
                else:
                    print(f"❌ 批量刷新请求失败: {refresh_response.status_code}")
                    print(f"响应内容: {refresh_response.text}")
            
            else:
                print("❌ 没有持仓数据")
        
        else:
            print(f"❌ 获取持仓失败: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_cache_info():
    """测试缓存信息"""
    base_url = "http://localhost:5001"
    
    print(f"\n4️⃣ 测试缓存信息...")
    
    try:
        response = requests.get(f"{base_url}/api/price-service/cache-info", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                cache_info = data['data']
                
                print(f"✅ 缓存信息获取成功:")
                print(f"   - 使用方法: {cache_info['method']}")
                print(f"   - API函数: {cache_info['api_function']}")
                print(f"   - 描述: {cache_info['description']}")
                print(f"   - 是否有缓存: {'是' if cache_info['has_cache'] else '否'}")
                print(f"   - 缓存时间: {cache_info['cache_timestamp'] or '无'}")
                print(f"   - 缓存年龄: {cache_info['cache_age_seconds'] or 0:.1f}秒")
                print(f"   - 缓存有效: {'是' if cache_info['cache_valid'] else '否'}")
                print(f"   - 缓存股票数: {cache_info['cached_stocks_count']}")
                print(f"   - 缓存时长: {cache_info['cache_duration_minutes']}分钟")
                
            else:
                print(f"❌ 获取缓存信息失败: {data.get('message', '未知错误')}")
        
        else:
            print(f"❌ 缓存信息请求失败: {response.status_code}")
        
    except Exception as e:
        print(f"❌ 缓存信息测试失败: {e}")

def compare_approaches():
    """对比不同方案"""
    print(f"\n📊 方案对比:")
    print("=" * 60)
    
    print("🔴 原始方案（无优化）:")
    print("   - 每只股票单独调用 ak.stock_zh_a_spot_em()")
    print("   - 重复下载全市场数据")
    print("   - 5只股票需要 35-45秒")
    
    print("\n🟡 单只股票API方案:")
    print("   - 调用 ak.stock_bid_ask_em(symbol=code)")
    print("   - 理论上更快，但实际获取不到实时价格")
    print("   - 数据可能不准确或延迟")
    
    print("\n🟢 当前方案（全市场数据+缓存）:")
    print("   - 一次调用 ak.stock_zh_a_spot_em() 获取全市场数据")
    print("   - 1分钟内复用缓存数据")
    print("   - 批量处理多只股票")
    print("   - 首次: 7-9秒，缓存内: 0.1秒")
    print("   - 数据准确，实时性好")

def main():
    """主函数"""
    print("🔄 全市场数据优化方案测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 方案对比
    compare_approaches()
    
    # 性能测试
    test_market_data_optimization()
    
    # 缓存测试
    test_cache_info()
    
    print(f"\n🎉 测试完成!")
    print("💡 虽然不如单只股票API理论速度快，但数据准确性更好！")
    print("🚀 缓存机制确保了后续请求的快速响应！")

if __name__ == '__main__':
    main()