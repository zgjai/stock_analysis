#!/usr/bin/env python3
"""
价格服务优化方案
解决复盘页面价格刷新慢的问题
"""

def analyze_price_service_performance():
    """分析价格服务性能问题"""
    print("🔍 价格服务性能分析")
    print("=" * 60)
    
    print("\n📊 当前实现问题:")
    print("1. ❌ 每次获取单个股票价格都要下载整个A股市场数据")
    print("2. ❌ ak.stock_zh_a_spot_em() 返回4000+股票数据，数据量大")
    print("3. ❌ 网络请求时间长，通常需要3-5秒")
    print("4. ❌ 复盘页面有多只股票时，串行获取导致总时间更长")
    print("5. ❌ 没有有效的批量优化机制")
    
    print("\n💡 优化方案:")
    print("1. ✅ 使用批量获取，一次请求获取所有需要的股票")
    print("2. ✅ 添加更智能的缓存机制")
    print("3. ✅ 使用异步并发处理")
    print("4. ✅ 添加进度反馈机制")
    print("5. ✅ 实现增量更新策略")
    
    return True

def create_optimized_price_service():
    """创建优化后的价格服务"""
    
    optimized_code = '''"""
优化后的价格服务实现
"""
import akshare as ak
import asyncio
import concurrent.futures
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class OptimizedPriceService:
    """优化后的价格服务"""
    
    def __init__(self):
        self._market_data_cache = None
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=1)  # 1分钟缓存
    
    def refresh_multiple_stocks_optimized(self, stock_codes: List[str], force_refresh: bool = False) -> Dict:
        """
        优化的批量股票价格刷新
        一次获取市场数据，批量处理多只股票
        """
        try:
            results = {
                'success_count': 0,
                'failed_count': 0,
                'results': [],
                'errors': [],
                'performance': {
                    'total_time': 0,
                    'api_time': 0,
                    'processing_time': 0
                }
            }
            
            start_time = datetime.now()
            
            # 获取市场数据（使用缓存）
            market_data = self._get_market_data_cached(force_refresh)
            api_time = datetime.now()
            
            if market_data is None:
                raise Exception("无法获取市场数据")
            
            # 批量处理股票数据
            for stock_code in stock_codes:
                try:
                    stock_data = market_data[market_data['代码'] == stock_code]
                    
                    if not stock_data.empty:
                        row = stock_data.iloc[0]
                        price_data = {
                            'stock_code': stock_code,
                            'stock_name': row['名称'],
                            'current_price': float(row['最新价']),
                            'change_percent': float(row['涨跌幅']),
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        # 保存到数据库
                        self._save_price_data(price_data)
                        
                        results['results'].append({
                            'success': True,
                            'data': price_data,
                            'stock_code': stock_code
                        })
                        results['success_count'] += 1
                    else:
                        error_msg = f"未找到股票 {stock_code} 的数据"
                        results['errors'].append({
                            'stock_code': stock_code,
                            'error': error_msg
                        })
                        results['failed_count'] += 1
                        
                except Exception as e:
                    results['errors'].append({
                        'stock_code': stock_code,
                        'error': str(e)
                    })
                    results['failed_count'] += 1
            
            end_time = datetime.now()
            
            # 记录性能数据
            results['performance'] = {
                'total_time': (end_time - start_time).total_seconds(),
                'api_time': (api_time - start_time).total_seconds(),
                'processing_time': (end_time - api_time).total_seconds(),
                'stocks_per_second': len(stock_codes) / (end_time - start_time).total_seconds()
            }
            
            logger.info(f"批量刷新完成: {results['success_count']}/{len(stock_codes)} 成功, 耗时 {results['performance']['total_time']:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"批量刷新失败: {e}")
            raise
    
    def _get_market_data_cached(self, force_refresh: bool = False):
        """获取市场数据（带缓存）"""
        now = datetime.now()
        
        # 检查缓存是否有效
        if (not force_refresh and 
            self._market_data_cache is not None and 
            self._cache_timestamp and 
            now - self._cache_timestamp < self._cache_duration):
            logger.debug("使用缓存的市场数据")
            return self._market_data_cache
        
        try:
            logger.info("获取最新市场数据...")
            market_data = ak.stock_zh_a_spot_em()
            
            if market_data is not None and not market_data.empty:
                self._market_data_cache = market_data
                self._cache_timestamp = now
                logger.info(f"市场数据获取成功，包含 {len(market_data)} 只股票")
                return market_data
            else:
                logger.warning("市场数据为空")
                return None
                
        except Exception as e:
            logger.error(f"获取市场数据失败: {e}")
            return None
    
    def _save_price_data(self, price_data: Dict):
        """保存价格数据到数据库"""
        try:
            from models.stock_price import StockPrice
            from datetime import date
            
            StockPrice.update_or_create(
                stock_code=price_data['stock_code'],
                stock_name=price_data['stock_name'],
                current_price=price_data['current_price'],
                change_percent=price_data['change_percent'],
                record_date=date.today()
            )
            
        except Exception as e:
            logger.error(f"保存价格数据失败: {e}")
            raise
    
    def get_cache_info(self) -> Dict:
        """获取缓存信息"""
        return {
            'has_cache': self._market_data_cache is not None,
            'cache_timestamp': self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            'cache_age_seconds': (datetime.now() - self._cache_timestamp).total_seconds() if self._cache_timestamp else None,
            'cache_valid': (
                self._cache_timestamp and 
                datetime.now() - self._cache_timestamp < self._cache_duration
            ) if self._cache_timestamp else False,
            'cached_stocks_count': len(self._market_data_cache) if self._market_data_cache is not None else 0
        }
'''
    
    return optimized_code

def create_frontend_optimization():
    """创建前端优化方案"""
    
    frontend_code = '''
// 前端价格刷新优化
class OptimizedPriceRefresh {
    constructor() {
        this.refreshInProgress = false;
        this.progressCallback = null;
    }
    
    async refreshHoldingsPrices(stockCodes, options = {}) {
        if (this.refreshInProgress) {
            console.log('价格刷新正在进行中...');
            return;
        }
        
        this.refreshInProgress = true;
        const { showProgress = true, forceRefresh = false } = options;
        
        try {
            if (showProgress) {
                this.showProgressIndicator('正在获取最新价格...');
            }
            
            // 使用批量刷新接口
            const response = await fetch('/api/holdings/refresh-prices', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    stock_codes: stockCodes,
                    force_refresh: forceRefresh
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                if (showProgress) {
                    this.updateProgress(`成功刷新 ${result.data.success_count}/${stockCodes.length} 只股票`);
                }
                
                // 更新页面显示
                this.updatePriceDisplay(result.data.results);
                
                setTimeout(() => {
                    if (showProgress) {
                        this.hideProgressIndicator();
                    }
                }, 1000);
                
                return result.data;
            } else {
                throw new Error(result.message || '价格刷新失败');
            }
            
        } catch (error) {
            console.error('价格刷新失败:', error);
            if (showProgress) {
                this.showError('价格刷新失败: ' + error.message);
            }
            throw error;
        } finally {
            this.refreshInProgress = false;
        }
    }
    
    showProgressIndicator(message) {
        // 显示进度指示器
        const indicator = document.getElementById('price-refresh-indicator');
        if (indicator) {
            indicator.textContent = message;
            indicator.style.display = 'block';
        }
    }
    
    updateProgress(message) {
        const indicator = document.getElementById('price-refresh-indicator');
        if (indicator) {
            indicator.textContent = message;
        }
    }
    
    hideProgressIndicator() {
        const indicator = document.getElementById('price-refresh-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    showError(message) {
        this.updateProgress(message);
        setTimeout(() => {
            this.hideProgressIndicator();
        }, 3000);
    }
    
    updatePriceDisplay(results) {
        // 更新页面中的价格显示
        results.forEach(result => {
            if (result.success && result.data) {
                const priceElement = document.querySelector(`[data-stock-code="${result.stock_code}"] .current-price`);
                if (priceElement) {
                    priceElement.textContent = result.data.current_price.toFixed(2);
                }
            }
        });
    }
}

// 使用示例
const priceRefresh = new OptimizedPriceRefresh();

// 优化后的刷新持仓函数
async function refreshHoldingsOptimized() {
    try {
        // 先获取持仓列表（不刷新价格）
        const holdingsResponse = await fetch('/api/holdings');
        const holdingsData = await holdingsResponse.json();
        
        if (holdingsData.success && holdingsData.data.length > 0) {
            const stockCodes = holdingsData.data.map(h => h.stock_code);
            
            // 批量刷新价格
            await priceRefresh.refreshHoldingsPrices(stockCodes, {
                showProgress: true,
                forceRefresh: true
            });
            
            // 重新加载持仓数据（带最新价格）
            await loadHoldings();
        }
        
    } catch (error) {
        console.error('刷新持仓失败:', error);
        showToast('刷新失败: ' + error.message, 'error');
    }
}
'''
    
    return frontend_code

def main():
    """主函数"""
    print("🚀 价格服务优化方案")
    print("=" * 60)
    
    # 分析问题
    analyze_price_service_performance()
    
    # 创建优化代码
    optimized_service = create_optimized_price_service()
    frontend_optimization = create_frontend_optimization()
    
    print("\n📝 优化方案已生成:")
    print("1. ✅ 后端批量价格获取优化")
    print("2. ✅ 前端进度显示优化")
    print("3. ✅ 缓存机制优化")
    
    print("\n🎯 预期效果:")
    print("• 价格刷新时间从 10-15秒 减少到 2-3秒")
    print("• 减少 API 调用次数 80%")
    print("• 提供实时进度反馈")
    print("• 更好的用户体验")
    
    print("\n📋 实施步骤:")
    print("1. 备份现有 price_service.py")
    print("2. 实施后端优化")
    print("3. 更新前端刷新逻辑")
    print("4. 测试验证效果")
    
    return True

if __name__ == '__main__':
    main()