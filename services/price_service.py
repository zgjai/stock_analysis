"""
股票价格服务
集成AKShare库实现股票实时价格获取功能
"""
import akshare as ak
import pandas as pd
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Union
import logging

from models.stock_price import StockPrice
from services.base_service import BaseService
from error_handlers import ValidationError, ExternalAPIError
from utils.validators import validate_stock_code
from extensions import db


logger = logging.getLogger(__name__)


class PriceService(BaseService):
    """股票价格服务类"""
    
    model = StockPrice
    
    # 类级别的缓存变量（用于全市场数据）
    _market_data_cache = None
    _cache_timestamp = None
    _cache_duration = timedelta(minutes=1)  # 1分钟缓存
    
    def __init__(self):
        self.db = db
    
    def refresh_stock_price(self, stock_code: str, force_refresh: bool = False) -> Dict:
        """
        刷新单个股票价格
        
        Args:
            stock_code: 股票代码
            force_refresh: 是否强制刷新（忽略缓存）
            
        Returns:
            Dict: 包含价格信息的字典
        """
        try:
            # 验证股票代码
            validate_stock_code(stock_code)
            
            today = date.today()
            
            # 检查是否需要刷新
            if not force_refresh:
                existing_price = StockPrice.get_price_by_date(stock_code, today)
                if existing_price:
                    logger.info(f"股票 {stock_code} 今日价格已存在，无需刷新")
                    return {
                        'success': True,
                        'message': '价格数据已是最新',
                        'data': existing_price.to_dict(),
                        'from_cache': True
                    }
            
            # 从AKShare获取实时价格
            price_data = self._fetch_stock_price_from_akshare(stock_code)
            
            if not price_data:
                raise ExternalAPIError(f"无法获取股票 {stock_code} 的价格数据")
            
            # 保存到数据库
            stock_price = StockPrice.update_or_create(
                stock_code=stock_code,
                stock_name=price_data['stock_name'],
                current_price=price_data['current_price'],
                change_percent=price_data['change_percent'],
                record_date=today
            )
            
            logger.info(f"成功刷新股票 {stock_code} 价格: {price_data['current_price']}")
            
            return {
                'success': True,
                'message': '价格刷新成功',
                'data': stock_price.to_dict(),
                'from_cache': False
            }
            
        except ValidationError as e:
            logger.error(f"股票代码验证失败: {e}")
            raise e
        except ExternalAPIError as e:
            logger.error(f"外部API调用失败: {e}")
            raise e
        except Exception as e:
            logger.error(f"刷新股票价格时发生未知错误: {e}")
            raise ExternalAPIError(f"刷新股票价格失败: {str(e)}")
    
    def refresh_multiple_stocks(self, stock_codes: List[str], force_refresh: bool = False) -> Dict:
        """
        批量刷新多个股票价格（优化版本）
        一次获取市场数据，批量处理多只股票
        
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
                'api_time': 0,
                'processing_time': 0
            }
        }
        
        start_time = datetime.now()
        
        try:
            # 获取市场数据（一次性获取所有股票数据）
            logger.info(f"开始批量刷新 {len(stock_codes)} 只股票价格...")
            market_data = self._get_market_data_cached(force_refresh)
            api_time = datetime.now()
            
            if market_data is None:
                raise ExternalAPIError("无法获取市场数据")
            
            # 批量处理股票数据
            for stock_code in stock_codes:
                try:
                    # 验证股票代码
                    validate_stock_code(stock_code)
                    
                    # 从市场数据中查找股票
                    stock_data = market_data[market_data['代码'] == stock_code]
                    
                    if not stock_data.empty:
                        row = stock_data.iloc[0]
                        
                        # 提取价格信息
                        price_data = {
                            'stock_name': row['名称'],
                            'current_price': float(row['最新价']),
                            'change_percent': float(row['涨跌幅'])
                        }
                        
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
                        
                    else:
                        error_msg = f"未找到股票 {stock_code} 的数据"
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
            
            # 记录性能数据
            total_time = (end_time - start_time).total_seconds()
            api_time_seconds = (api_time - start_time).total_seconds()
            processing_time = (end_time - api_time).total_seconds()
            
            results['performance'] = {
                'total_time': total_time,
                'api_time': api_time_seconds,
                'processing_time': processing_time,
                'stocks_per_second': len(stock_codes) / total_time if total_time > 0 else 0,
                'method': 'batch_market_data'
            }
            
            logger.info(f"批量刷新完成: {results['success_count']}/{len(stock_codes)} 成功, "
                       f"总耗时 {total_time:.2f}s (API: {api_time_seconds:.2f}s, 处理: {processing_time:.2f}s)")
            
        except Exception as e:
            logger.error(f"批量刷新失败: {e}")
            results['errors'].append({
                'stock_code': 'ALL',
                'error': str(e)
            })
            results['failed_count'] = len(stock_codes)
        
        return results
    
    def get_stock_price(self, stock_code: str, target_date: Optional[date] = None) -> Optional[Dict]:
        """
        获取股票价格（优先从缓存获取）
        
        Args:
            stock_code: 股票代码
            target_date: 目标日期，默认为今天
            
        Returns:
            Dict: 价格信息字典，如果不存在返回None
        """
        try:
            validate_stock_code(stock_code)
            
            if target_date is None:
                target_date = date.today()
            
            stock_price = StockPrice.get_price_by_date(stock_code, target_date)
            
            if stock_price:
                return stock_price.to_dict()
            
            return None
            
        except ValidationError as e:
            logger.error(f"获取股票价格时验证失败: {e}")
            raise e
        except Exception as e:
            logger.error(f"获取股票价格时发生错误: {e}")
            raise ExternalAPIError(f"获取股票价格失败: {str(e)}")
    
    def get_latest_price(self, stock_code: str) -> Optional[Dict]:
        """
        获取股票最新价格
        
        Args:
            stock_code: 股票代码
            
        Returns:
            Dict: 最新价格信息字典
        """
        try:
            validate_stock_code(stock_code)
            
            stock_price = StockPrice.get_latest_price(stock_code)
            
            if stock_price:
                return stock_price.to_dict()
            
            return None
            
        except ValidationError as e:
            logger.error(f"获取最新价格时验证失败: {e}")
            raise e
        except Exception as e:
            logger.error(f"获取最新价格时发生错误: {e}")
            raise ExternalAPIError(f"获取最新价格失败: {str(e)}")
    
    def get_price_history(self, stock_code: str, days: int = 30) -> List[Dict]:
        """
        获取股票价格历史
        
        Args:
            stock_code: 股票代码
            days: 获取天数
            
        Returns:
            List[Dict]: 价格历史列表
        """
        try:
            validate_stock_code(stock_code)
            
            if days <= 0:
                raise ValidationError("天数必须大于0", "days")
            
            price_history = StockPrice.get_price_history(stock_code, days)
            
            return [price.to_dict() for price in price_history]
            
        except ValidationError as e:
            logger.error(f"获取价格历史时验证失败: {e}")
            raise e
        except Exception as e:
            logger.error(f"获取价格历史时发生错误: {e}")
            raise ExternalAPIError(f"获取价格历史失败: {str(e)}")
    
    def cleanup_old_prices(self, days_to_keep: int = 90) -> Dict:
        """
        清理旧的价格数据
        
        Args:
            days_to_keep: 保留天数
            
        Returns:
            Dict: 清理结果
        """
        try:
            cutoff_date = date.today() - timedelta(days=days_to_keep)
            
            # 删除指定日期之前的数据
            deleted_count = StockPrice.query.filter(
                StockPrice.record_date < cutoff_date
            ).delete()
            
            self.db.session.commit()
            
            logger.info(f"清理了 {deleted_count} 条旧价格数据")
            
            return {
                'success': True,
                'message': f'成功清理 {deleted_count} 条旧数据',
                'deleted_count': deleted_count
            }
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"清理旧价格数据时发生错误: {e}")
            raise ExternalAPIError(f"清理数据失败: {str(e)}")
    

    
    def _get_market_data_cached(self, force_refresh: bool = False):
        """
        获取市场数据（带缓存）
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            DataFrame: 市场数据
        """
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
                # 更新类级别缓存
                PriceService._market_data_cache = market_data
                PriceService._cache_timestamp = now
                logger.info(f"市场数据获取成功，包含 {len(market_data)} 只股票")
                return market_data
            else:
                logger.warning("市场数据为空")
                return None
                
        except Exception as e:
            logger.error(f"获取市场数据失败: {e}")
            return None
    
    def _fetch_stock_price_from_akshare(self, stock_code: str) -> Optional[Dict]:
        """
        从AKShare获取股票价格数据（使用全市场数据）
        
        Args:
            stock_code: 股票代码
            
        Returns:
            Dict: 价格数据字典
        """
        try:
            # 使用缓存的市场数据
            market_data = self._get_market_data_cached()
            
            if market_data is None or market_data.empty:
                logger.warning("无法获取市场数据")
                return None
            
            # 查找指定股票
            stock_data = market_data[market_data['代码'] == stock_code]
            
            if stock_data.empty:
                logger.warning(f"未找到股票 {stock_code} 的数据")
                return None
            
            # 获取第一行数据
            row = stock_data.iloc[0]
            
            # 提取价格信息
            price_data = {
                'stock_name': row['名称'],
                'current_price': float(row['最新价']),
                'change_percent': float(row['涨跌幅'])
            }
            
            logger.debug(f"从AKShare获取到股票 {stock_code} 数据: {price_data}")
            
            return price_data
            
        except Exception as e:
            logger.error(f"从AKShare获取股票 {stock_code} 数据失败: {e}")
            return None
    
    def get_cache_status(self, stock_codes: List[str]) -> Dict:
        """
        获取股票价格缓存状态
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            Dict: 缓存状态信息
        """
        today = date.today()
        cache_status = {
            'total_stocks': len(stock_codes),
            'cached_today': 0,
            'need_refresh': 0,
            'details': []
        }
        
        for stock_code in stock_codes:
            try:
                validate_stock_code(stock_code)
                
                latest_price = StockPrice.get_price_by_date(stock_code, today)
                
                if latest_price:
                    cache_status['cached_today'] += 1
                    status = 'cached'
                else:
                    cache_status['need_refresh'] += 1
                    status = 'need_refresh'
                
                cache_status['details'].append({
                    'stock_code': stock_code,
                    'status': status,
                    'last_update': latest_price.record_date.isoformat() if latest_price else None
                })
                
            except ValidationError:
                cache_status['details'].append({
                    'stock_code': stock_code,
                    'status': 'invalid',
                    'last_update': None
                })
        
        return cache_status
    
    def get_market_cache_info(self) -> Dict:
        """
        获取市场数据缓存信息
        
        Returns:
            Dict: 缓存状态信息
        """
        now = datetime.now()
        
        return {
            'has_cache': self._market_data_cache is not None,
            'cache_timestamp': self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            'cache_age_seconds': (now - self._cache_timestamp).total_seconds() if self._cache_timestamp else None,
            'cache_valid': (
                self._cache_timestamp and 
                now - self._cache_timestamp < self._cache_duration
            ) if self._cache_timestamp else False,
            'cached_stocks_count': len(self._market_data_cache) if self._market_data_cache is not None else 0,
            'cache_duration_minutes': self._cache_duration.total_seconds() / 60,
            'method': 'batch_market_data',
            'api_function': 'ak.stock_zh_a_spot_em',
            'description': '使用全市场数据批量处理，带1分钟缓存优化'
        }