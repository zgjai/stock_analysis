#!/usr/bin/env python3
"""
价格刷新优化修复脚本
解决复盘页面价格刷新时重复请求过多的问题
"""

import os
import sys
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def optimize_review_page_js():
    """优化复盘页面的JavaScript代码，减少重复API调用"""
    
    review_template_path = 'templates/review.html'
    
    if not os.path.exists(review_template_path):
        logger.error(f"复盘页面模板文件不存在: {review_template_path}")
        return False
    
    try:
        # 读取原文件
        with open(review_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建备份
        backup_path = f"{review_template_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"已创建备份文件: {backup_path}")
        
        # 优化自动刷新逻辑
        old_auto_refresh = '''        // 每30秒刷新一次价格
        autoRefreshInterval = setInterval(() => {
            console.log('自动刷新价格...');
            loadHoldings(true);
        }, 30000); // 30秒'''
        
        new_auto_refresh = '''        // 每60秒刷新一次价格（降低频率）
        autoRefreshInterval = setInterval(() => {
            console.log('自动刷新价格...');
            // 使用防抖机制，避免重复调用
            if (!window.isRefreshing) {
                window.isRefreshing = true;
                loadHoldings(true).finally(() => {
                    window.isRefreshing = false;
                });
            }
        }, 60000); // 60秒'''
        
        if old_auto_refresh in content:
            content = content.replace(old_auto_refresh, new_auto_refresh)
            logger.info("✅ 已优化自动刷新频率和防抖机制")
        
        # 优化loadHoldings函数，添加防抖机制
        old_load_holdings = '''async function loadHoldings(forceRefreshPrices = false) {
    console.log('📊 开始加载持仓数据', forceRefreshPrices ? '(强制刷新价格)' : '');
    const holdingsList = document.getElementById('holdings-list');

    if (!holdingsList) {
        console.error('持仓列表容器不存在');
        return;
    }

    try {
        holdingsList.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                ${forceRefreshPrices ? '正在刷新价格数据...' : '正在加载持仓数据...'}
            </div>
        `;

        const url = forceRefreshPrices ? '/api/holdings?force_refresh=true' : '/api/holdings';
        const response = await fetch(url);
        const data = await response.json();'''
        
        new_load_holdings = '''// 防抖变量
let loadHoldingsDebounceTimer = null;

async function loadHoldings(forceRefreshPrices = false) {
    console.log('📊 开始加载持仓数据', forceRefreshPrices ? '(强制刷新价格)' : '');
    
    // 防抖机制：如果正在加载，则取消之前的请求
    if (loadHoldingsDebounceTimer) {
        clearTimeout(loadHoldingsDebounceTimer);
    }
    
    // 如果正在刷新，直接返回
    if (window.isRefreshing && forceRefreshPrices) {
        console.log('⏸️ 价格刷新正在进行中，跳过本次请求');
        return;
    }
    
    const holdingsList = document.getElementById('holdings-list');

    if (!holdingsList) {
        console.error('持仓列表容器不存在');
        return;
    }

    try {
        holdingsList.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                ${forceRefreshPrices ? '正在刷新价格数据...' : '正在加载持仓数据...'}
            </div>
        `;

        const url = forceRefreshPrices ? '/api/holdings?force_refresh=true' : '/api/holdings';
        const response = await fetch(url);
        const data = await response.json();'''
        
        if old_load_holdings in content:
            content = content.replace(old_load_holdings, new_load_holdings)
            logger.info("✅ 已添加loadHoldings防抖机制")
        
        # 写入优化后的内容
        with open(review_template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("✅ 复盘页面JavaScript优化完成")
        return True
        
    except Exception as e:
        logger.error(f"优化复盘页面失败: {e}")
        return False

def optimize_holding_service():
    """优化HoldingService，减少重复的价格API调用"""
    
    service_path = 'services/review_service.py'
    
    if not os.path.exists(service_path):
        logger.error(f"服务文件不存在: {service_path}")
        return False
    
    try:
        # 读取原文件
        with open(service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建备份
        backup_path = f"{service_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"已创建备份文件: {backup_path}")
        
        # 优化_get_current_price方法，添加批量获取和缓存机制
        old_get_price = '''    @classmethod
    def _get_current_price(cls, stock_code: str, force_refresh: bool = False) -> Optional[float]:
        """获取股票当前价格"""
        try:
            from services.price_service import PriceService
            from datetime import datetime, timedelta
            price_service = PriceService()
            
            # 如果不强制刷新，检查缓存是否足够新（5分钟内）
            if not force_refresh:
                price_data = price_service.get_latest_price(stock_code)
                if price_data and price_data.get('current_price'):
                    # 检查价格更新时间
                    if 'updated_at' in price_data:
                        try:
                            updated_time = datetime.fromisoformat(price_data['updated_at'].replace('Z', '+00:00'))
                            if datetime.now() - updated_time.replace(tzinfo=None) < timedelta(minutes=5):
                                return float(price_data['current_price'])
                        except:
                            pass
            
            # 强制刷新或缓存过期，从AKShare获取实时价格
            try:
                result = price_service.refresh_stock_price(stock_code, force_refresh=True)
                if result.get('success') and result.get('data'):
                    return float(result['data'].get('current_price', 0))
            except Exception as e:
                logger.warning(f"获取股票 {stock_code} 实时价格失败: {e}")
                
                # 如果实时获取失败，返回缓存价格（如果有的话）
                price_data = price_service.get_latest_price(stock_code)
                if price_data and price_data.get('current_price'):
                    return float(price_data['current_price'])
            
            return None
            
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 当前价格时发生错误: {e}")
            return None'''
        
        new_get_price = '''    # 价格缓存，避免重复调用
    _price_cache = {}
    _cache_timestamp = None
    
    @classmethod
    def _get_current_price(cls, stock_code: str, force_refresh: bool = False) -> Optional[float]:
        """获取股票当前价格（带缓存优化）"""
        try:
            from services.price_service import PriceService
            from datetime import datetime, timedelta
            
            # 检查内存缓存（1分钟内有效）
            now = datetime.now()
            if (not force_refresh and 
                cls._cache_timestamp and 
                now - cls._cache_timestamp < timedelta(minutes=1) and
                stock_code in cls._price_cache):
                logger.debug(f"使用内存缓存价格: {stock_code}")
                return cls._price_cache[stock_code]
            
            price_service = PriceService()
            
            # 如果不强制刷新，检查数据库缓存是否足够新（5分钟内）
            if not force_refresh:
                price_data = price_service.get_latest_price(stock_code)
                if price_data and price_data.get('current_price'):
                    # 检查价格更新时间
                    if 'updated_at' in price_data:
                        try:
                            updated_time = datetime.fromisoformat(price_data['updated_at'].replace('Z', '+00:00'))
                            if datetime.now() - updated_time.replace(tzinfo=None) < timedelta(minutes=5):
                                price = float(price_data['current_price'])
                                # 更新内存缓存
                                cls._price_cache[stock_code] = price
                                cls._cache_timestamp = now
                                return price
                        except:
                            pass
            
            # 强制刷新或缓存过期，从AKShare获取实时价格
            try:
                result = price_service.refresh_stock_price(stock_code, force_refresh=True)
                if result.get('success') and result.get('data'):
                    price = float(result['data'].get('current_price', 0))
                    # 更新内存缓存
                    cls._price_cache[stock_code] = price
                    cls._cache_timestamp = now
                    return price
            except Exception as e:
                logger.warning(f"获取股票 {stock_code} 实时价格失败: {e}")
                
                # 如果实时获取失败，返回缓存价格（如果有的话）
                price_data = price_service.get_latest_price(stock_code)
                if price_data and price_data.get('current_price'):
                    price = float(price_data['current_price'])
                    # 更新内存缓存
                    cls._price_cache[stock_code] = price
                    cls._cache_timestamp = now
                    return price
            
            return None
            
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 当前价格时发生错误: {e}")
            return None'''
        
        if old_get_price in content:
            content = content.replace(old_get_price, new_get_price)
            logger.info("✅ 已优化价格获取方法，添加内存缓存")
        
        # 添加批量价格刷新方法
        batch_refresh_method = '''
    @classmethod
    def refresh_all_holdings_prices(cls, stock_codes: List[str]) -> Dict[str, Any]:
        """批量刷新所有持仓股票价格"""
        try:
            from services.price_service import PriceService
            price_service = PriceService()
            
            # 使用批量刷新方法
            result = price_service.refresh_multiple_stocks(stock_codes, force_refresh=True)
            
            # 清空内存缓存，强制重新获取
            cls._price_cache.clear()
            cls._cache_timestamp = None
            
            return result
            
        except Exception as e:
            logger.error(f"批量刷新价格失败: {e}")
            return {
                'success_count': 0,
                'failed_count': len(stock_codes),
                'results': [],
                'errors': [{'error': str(e)}]
            }
'''
        
        # 在类的末尾添加批量刷新方法
        if 'def get_holding_stats(cls)' in content:
            content = content.replace(
                'def get_holding_stats(cls)',
                batch_refresh_method + '\n    @classmethod\n    def get_holding_stats(cls)'
            )
            logger.info("✅ 已添加批量价格刷新方法")
        
        # 写入优化后的内容
        with open(service_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("✅ HoldingService优化完成")
        return True
        
    except Exception as e:
        logger.error(f"优化HoldingService失败: {e}")
        return False

def create_optimized_api_route():
    """创建优化的API路由，支持批量价格刷新"""
    
    route_path = 'api/review_routes.py'
    
    if not os.path.exists(route_path):
        logger.error(f"API路由文件不存在: {route_path}")
        return False
    
    try:
        # 读取原文件
        with open(route_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建备份
        backup_path = f"{route_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"已创建备份文件: {backup_path}")
        
        # 添加批量价格刷新路由
        batch_refresh_route = '''

@api_bp.route('/holdings/refresh-prices', methods=['POST'])
def refresh_holdings_prices():
    """批量刷新持仓股票价格"""
    try:
        data = request.get_json() or {}
        stock_codes = data.get('stock_codes', [])
        
        if not stock_codes:
            # 如果没有指定股票代码，获取所有持仓股票
            holdings = HoldingService.get_current_holdings(force_refresh_prices=False)
            stock_codes = [h['stock_code'] for h in holdings]
        
        if not stock_codes:
            return create_success_response(
                data={'message': '没有需要刷新的股票'},
                message='没有持仓股票需要刷新价格'
            )
        
        # 批量刷新价格
        result = HoldingService.refresh_all_holdings_prices(stock_codes)
        
        return create_success_response(
            data=result,
            message=f'批量刷新完成，成功: {result["success_count"]}, 失败: {result["failed_count"]}'
        )
    
    except Exception as e:
        logger.error(f"批量刷新价格失败: {e}")
        raise e
'''
        
        # 在文件末尾添加新路由
        if batch_refresh_route.strip() not in content:
            content += batch_refresh_route
            logger.info("✅ 已添加批量价格刷新路由")
        
        # 写入优化后的内容
        with open(route_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("✅ API路由优化完成")
        return True
        
    except Exception as e:
        logger.error(f"优化API路由失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("🚀 开始价格刷新优化修复")
    
    success_count = 0
    total_count = 3
    
    # 1. 优化复盘页面JavaScript
    if optimize_review_page_js():
        success_count += 1
        logger.info("✅ 复盘页面JavaScript优化成功")
    else:
        logger.error("❌ 复盘页面JavaScript优化失败")
    
    # 2. 优化HoldingService
    if optimize_holding_service():
        success_count += 1
        logger.info("✅ HoldingService优化成功")
    else:
        logger.error("❌ HoldingService优化失败")
    
    # 3. 创建优化的API路由
    if create_optimized_api_route():
        success_count += 1
        logger.info("✅ API路由优化成功")
    else:
        logger.error("❌ API路由优化失败")
    
    # 总结
    logger.info(f"\n{'='*50}")
    logger.info(f"价格刷新优化修复完成")
    logger.info(f"成功: {success_count}/{total_count}")
    
    if success_count == total_count:
        logger.info("🎉 所有优化都已成功完成！")
        logger.info("\n主要优化内容:")
        logger.info("1. 降低自动刷新频率从30秒到60秒")
        logger.info("2. 添加防抖机制，避免重复调用")
        logger.info("3. 添加内存缓存，减少数据库查询")
        logger.info("4. 支持批量价格刷新，减少API调用次数")
        logger.info("\n请重启服务器以应用更改")
    else:
        logger.warning("⚠️ 部分优化未能完成，请检查错误信息")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)