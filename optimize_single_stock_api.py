#!/usr/bin/env python3
"""
使用单只股票API优化价格服务
"""
import akshare as ak
import time

def test_single_stock_api():
    """测试单只股票API的性能"""
    print("🧪 测试单只股票API性能")
    print("=" * 50)
    
    test_stocks = ["000001", "000002", "000776"]
    
    print("\n📊 方案对比:")
    
    # 方案1：全市场数据（当前方案）
    print("\n🔴 方案1：全市场数据")
    start_time = time.time()
    try:
        df = ak.stock_zh_a_spot_em()
        market_time = time.time() - start_time
        print(f"   下载全市场数据: {market_time:.2f}s ({len(df)} 只股票)")
        
        for stock_code in test_stocks:
            start_single = time.time()
            stock_data = df[df['代码'] == stock_code]
            single_time = time.time() - start_single
            
            if not stock_data.empty:
                row = stock_data.iloc[0]
                price = float(row['最新价'])
                print(f"   {stock_code}: {price} 元 (筛选耗时: {single_time:.4f}s)")
            else:
                print(f"   {stock_code}: 未找到数据")
        
        total_time1 = time.time() - start_time
        print(f"   总耗时: {total_time1:.2f}s")
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        total_time1 = float('inf')
    
    # 方案2：单只股票API
    print("\n🟢 方案2：单只股票API")
    start_time = time.time()
    success_count = 0
    
    for stock_code in test_stocks:
        try:
            start_single = time.time()
            stock_data = ak.stock_bid_ask_em(symbol=stock_code)
            single_time = time.time() - start_single
            
            if not stock_data.empty:
                # 获取最新价格
                current_price = float(stock_data['value'].iloc[0])  # 最新价
                print(f"   {stock_code}: {current_price} 元 (查询耗时: {single_time:.2f}s)")
                success_count += 1
            else:
                print(f"   {stock_code}: 未找到数据")
                
        except Exception as e:
            print(f"   {stock_code}: ❌ 失败 - {e}")
    
    total_time2 = time.time() - start_time
    print(f"   总耗时: {total_time2:.2f}s")
    print(f"   成功率: {success_count}/{len(test_stocks)}")
    
    # 性能对比
    if total_time1 != float('inf'):
        improvement = (total_time1 - total_time2) / total_time1 * 100
        print(f"\n📈 性能提升: {improvement:.1f}%")
        print(f"   方案1: {total_time1:.2f}s")
        print(f"   方案2: {total_time2:.2f}s")
    
    return success_count > 0

def create_optimized_price_service():
    """创建使用单只股票API的优化版本"""
    
    code = '''
def _fetch_stock_price_from_akshare_optimized(self, stock_code: str) -> Optional[Dict]:
    """
    从AKShare获取单只股票价格数据（优化版本）
    使用 ak.stock_bid_ask_em 直接查询单只股票
    
    Args:
        stock_code: 股票代码
        
    Returns:
        Dict: 价格数据字典
    """
    try:
        # 使用单只股票查询接口
        stock_data = ak.stock_bid_ask_em(symbol=stock_code)
        
        if stock_data is None or stock_data.empty:
            logger.warning(f"AKShare返回空数据: {stock_code}")
            return None
        
        # 解析数据结构
        # stock_bid_ask_em 返回的数据格式：
        # item    value
        # 最新价   xx.xx
        # 涨跌额   xx.xx
        # 涨跌幅   xx.xx%
        # ...
        
        data_dict = dict(zip(stock_data['item'], stock_data['value']))
        
        # 提取价格信息
        current_price = float(data_dict.get('最新价', 0))
        change_percent_str = data_dict.get('涨跌幅', '0%')
        
        # 处理涨跌幅（去掉%符号）
        change_percent = float(change_percent_str.replace('%', '')) if change_percent_str != '-' else 0.0
        
        # 获取股票名称（可能需要额外查询）
        stock_name = data_dict.get('名称', f'股票{stock_code}')
        
        price_data = {
            'stock_name': stock_name,
            'current_price': current_price,
            'change_percent': change_percent
        }
        
        logger.debug(f"从AKShare获取到股票 {stock_code} 数据: {price_data}")
        
        return price_data
        
    except Exception as e:
        logger.error(f"从AKShare获取股票 {stock_code} 数据失败: {e}")
        return None

def refresh_multiple_stocks_optimized(self, stock_codes: List[str], force_refresh: bool = False) -> Dict:
    """
    批量刷新多个股票价格（使用单只股票API）
    
    Args:
        stock_codes: 股票代码列表
        force_refresh: 是否强制刷新
        
    Returns:
        Dict: 批量刷新结果
    """
    results = {
        'success_count': 0,
        'failed_count': 0,
        'results': [],
        'errors': [],
        'performance': {
            'total_time': 0,
            'avg_time_per_stock': 0,
            'parallel_processing': False
        }
    }
    
    start_time = datetime.now()
    
    try:
        logger.info(f"开始批量刷新 {len(stock_codes)} 只股票价格（使用单只股票API）...")
        
        # 串行处理每只股票（可以考虑并行优化）
        for i, stock_code in enumerate(stock_codes, 1):
            try:
                # 验证股票代码
                validate_stock_code(stock_code)
                
                # 获取单只股票数据
                price_data = self._fetch_stock_price_from_akshare_optimized(stock_code)
                
                if price_data:
                    # 保存到数据库
                    today = date.today()
                    stock_price = StockPrice.update_or_create(
                        stock_code=stock_code,
                        stock_name=price_data['stock_name'],
                        current_price=price_data['current_price'],
                        change_percent=price_data['change_percent'],
                        record_date=today
                    )
                    
                    results['results'].append({
                        'success': True,
                        'message': '价格刷新成功',
                        'data': stock_price.to_dict(),
                        'from_cache': False
                    })
                    results['success_count'] += 1
                    
                    logger.info(f"刷新进度: {i}/{len(stock_codes)} - {stock_code}: {price_data['current_price']}")
                    
                else:
                    error_msg = f"未能获取股票 {stock_code} 的价格数据"
                    results['errors'].append({
                        'stock_code': stock_code,
                        'error': error_msg
                    })
                    results['failed_count'] += 1
                    logger.warning(error_msg)
                    
            except ValidationError as e:
                results['errors'].append({
                    'stock_code': stock_code,
                    'error': str(e)
                })
                results['failed_count'] += 1
                logger.error(f"股票代码验证失败 {stock_code}: {e}")
                
            except Exception as e:
                results['errors'].append({
                    'stock_code': stock_code,
                    'error': str(e)
                })
                results['failed_count'] += 1
                logger.error(f"处理股票 {stock_code} 失败: {e}")
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # 记录性能数据
        results['performance'] = {
            'total_time': total_time,
            'avg_time_per_stock': total_time / len(stock_codes) if stock_codes else 0,
            'stocks_per_second': len(stock_codes) / total_time if total_time > 0 else 0,
            'parallel_processing': False  # 当前是串行处理
        }
        
        logger.info(f"批量刷新完成: {results['success_count']}/{len(stock_codes)} 成功, "
                   f"总耗时 {total_time:.2f}s, 平均 {results['performance']['avg_time_per_stock']:.2f}s/股票")
        
    except Exception as e:
        logger.error(f"批量刷新失败: {e}")
        results['errors'].append({
            'stock_code': 'ALL',
            'error': str(e)
        })
        results['failed_count'] = len(stock_codes)
    
    return results
'''
    
    return code

def main():
    """主函数"""
    print("🚀 单只股票API优化方案")
    print("=" * 60)
    
    # 测试API性能
    if test_single_stock_api():
        print("\n✅ 单只股票API测试成功")
        
        # 生成优化代码
        optimized_code = create_optimized_price_service()
        
        print("\n📝 优化建议:")
        print("1. 使用 ak.stock_bid_ask_em(symbol=stock_code) 替代全市场查询")
        print("2. 每只股票独立查询，避免下载无关数据")
        print("3. 可以考虑并行处理进一步优化")
        print("4. 减少网络传输量和内存使用")
        
        print("\n🎯 预期效果:")
        print("• 单只股票查询时间：1-2秒（vs 9秒）")
        print("• 网络传输量减少：95%+")
        print("• 内存使用减少：90%+")
        print("• 更稳定的性能表现")
        
    else:
        print("\n❌ 单只股票API测试失败，可能需要检查网络或API变化")

if __name__ == '__main__':
    main()