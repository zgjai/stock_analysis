"""
API请求限制和防护工具
"""
import time
import logging
from typing import Dict, Any, Optional, Tuple
from functools import wraps
from collections import defaultdict, deque
from flask import request, jsonify, current_app, g
from error_handlers import ValidationError

logger = logging.getLogger(__name__)


class RateLimiter:
    """请求频率限制器"""
    
    def __init__(self):
        # 存储每个IP的请求记录
        self.requests = defaultdict(deque)
        # 存储每个IP的请求计数
        self.request_counts = defaultdict(int)
        # 存储被封禁的IP
        self.blocked_ips = {}
        
        # 默认限制配置
        self.default_limits = {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'burst_limit': 10,  # 突发请求限制
            'block_duration': 300,  # 封禁时长（秒）
        }
    
    def is_allowed(self, identifier: str, endpoint: str = None) -> Tuple[bool, Dict[str, Any]]:
        """
        检查请求是否被允许
        
        Args:
            identifier: 请求标识符（通常是IP地址）
            endpoint: API端点
            
        Returns:
            Tuple[bool, Dict]: (是否允许, 限制信息)
        """
        try:
            current_time = time.time()
            
            # 检查是否被封禁
            if identifier in self.blocked_ips:
                block_time = self.blocked_ips[identifier]
                if current_time - block_time < self.default_limits['block_duration']:
                    return False, {
                        'blocked': True,
                        'block_remaining': self.default_limits['block_duration'] - (current_time - block_time),
                        'reason': 'IP被临时封禁'
                    }
                else:
                    # 解除封禁
                    del self.blocked_ips[identifier]
            
            # 获取端点特定的限制配置
            limits = self._get_endpoint_limits(endpoint)
            
            # 清理过期的请求记录
            self._cleanup_old_requests(identifier, current_time)
            
            # 检查分钟级限制
            minute_requests = self._count_requests_in_window(identifier, current_time, 60)
            if minute_requests >= limits['requests_per_minute']:
                self._handle_rate_limit_exceeded(identifier, 'minute')
                return False, {
                    'rate_limited': True,
                    'limit_type': 'minute',
                    'limit': limits['requests_per_minute'],
                    'current': minute_requests,
                    'reset_time': 60
                }
            
            # 检查小时级限制
            hour_requests = self._count_requests_in_window(identifier, current_time, 3600)
            if hour_requests >= limits['requests_per_hour']:
                self._handle_rate_limit_exceeded(identifier, 'hour')
                return False, {
                    'rate_limited': True,
                    'limit_type': 'hour',
                    'limit': limits['requests_per_hour'],
                    'current': hour_requests,
                    'reset_time': 3600
                }
            
            # 检查突发请求限制
            burst_requests = self._count_requests_in_window(identifier, current_time, 10)
            if burst_requests >= limits['burst_limit']:
                return False, {
                    'rate_limited': True,
                    'limit_type': 'burst',
                    'limit': limits['burst_limit'],
                    'current': burst_requests,
                    'reset_time': 10
                }
            
            # 记录请求
            self.requests[identifier].append(current_time)
            self.request_counts[identifier] += 1
            
            return True, {
                'allowed': True,
                'minute_requests': minute_requests + 1,
                'hour_requests': hour_requests + 1,
                'limits': limits
            }
            
        except Exception as e:
            logger.error(f"请求频率检查失败: {str(e)}")
            # 出错时允许请求通过
            return True, {'error': str(e)}
    
    def _get_endpoint_limits(self, endpoint: str) -> Dict[str, int]:
        """获取端点特定的限制配置"""
        # 不同端点的特殊限制
        endpoint_limits = {
            '/api/historical-trades/sync': {
                'requests_per_minute': 5,
                'requests_per_hour': 20,
                'burst_limit': 2,
                'block_duration': 600,
            },
            '/api/trade-reviews/*/images': {
                'requests_per_minute': 20,
                'requests_per_hour': 100,
                'burst_limit': 5,
                'block_duration': 300,
            },
        }
        
        # 检查是否有匹配的端点配置
        for pattern, limits in endpoint_limits.items():
            if endpoint and pattern in endpoint:
                return {**self.default_limits, **limits}
        
        return self.default_limits
    
    def _cleanup_old_requests(self, identifier: str, current_time: float) -> None:
        """清理过期的请求记录"""
        if identifier in self.requests:
            # 保留最近1小时的请求记录
            cutoff_time = current_time - 3600
            while self.requests[identifier] and self.requests[identifier][0] < cutoff_time:
                self.requests[identifier].popleft()
    
    def _count_requests_in_window(self, identifier: str, current_time: float, window_seconds: int) -> int:
        """统计时间窗口内的请求数量"""
        if identifier not in self.requests:
            return 0
        
        cutoff_time = current_time - window_seconds
        count = 0
        
        for request_time in reversed(self.requests[identifier]):
            if request_time >= cutoff_time:
                count += 1
            else:
                break
        
        return count
    
    def _handle_rate_limit_exceeded(self, identifier: str, limit_type: str) -> None:
        """处理请求频率超限"""
        logger.warning(f"请求频率超限: {identifier}, 类型: {limit_type}")
        
        # 如果是严重超限，临时封禁IP
        if limit_type in ['hour', 'minute']:
            recent_violations = self._count_recent_violations(identifier)
            if recent_violations >= 3:
                self.blocked_ips[identifier] = time.time()
                logger.warning(f"IP被临时封禁: {identifier}")
    
    def _count_recent_violations(self, identifier: str) -> int:
        """统计最近的违规次数"""
        # 简化实现，实际可以更复杂
        return self.request_counts.get(identifier, 0) // 100
    
    def get_stats(self) -> Dict[str, Any]:
        """获取限制器统计信息"""
        return {
            'active_ips': len(self.requests),
            'blocked_ips': len(self.blocked_ips),
            'total_requests': sum(self.request_counts.values()),
            'blocked_ips_list': list(self.blocked_ips.keys())
        }
    
    def reset_ip(self, identifier: str) -> bool:
        """重置IP的请求记录"""
        try:
            if identifier in self.requests:
                del self.requests[identifier]
            if identifier in self.request_counts:
                del self.request_counts[identifier]
            if identifier in self.blocked_ips:
                del self.blocked_ips[identifier]
            
            logger.info(f"IP请求记录已重置: {identifier}")
            return True
        except Exception as e:
            logger.error(f"重置IP请求记录失败: {identifier}, 错误: {str(e)}")
            return False


class SecurityProtector:
    """安全防护器"""
    
    def __init__(self):
        self.suspicious_patterns = [
            # SQL注入模式
            r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b|\bDROP\b)',
            # XSS模式
            r'(<script|javascript:|onload=|onerror=)',
            # 路径遍历模式
            r'(\.\./|\.\.\\|%2e%2e%2f)',
            # 命令注入模式
            r'(;|\||&|\$\(|\`)',
        ]
        
        self.blocked_user_agents = [
            'sqlmap',
            'nikto',
            'nmap',
            'masscan',
            'nessus',
        ]
    
    def check_request_security(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        检查请求安全性
        
        Args:
            request_data: 请求数据
            
        Returns:
            Tuple[bool, str]: (是否安全, 威胁描述)
        """
        try:
            # 检查User-Agent
            user_agent = request.headers.get('User-Agent', '').lower()
            for blocked_agent in self.blocked_user_agents:
                if blocked_agent in user_agent:
                    return False, f"可疑的User-Agent: {blocked_agent}"
            
            # 检查请求参数
            for key, value in request_data.items():
                if isinstance(value, str):
                    threat = self._check_string_for_threats(value)
                    if threat:
                        return False, f"参数 {key} 包含可疑内容: {threat}"
            
            # 检查请求头
            for header_name, header_value in request.headers:
                if isinstance(header_value, str):
                    threat = self._check_string_for_threats(header_value)
                    if threat:
                        return False, f"请求头 {header_name} 包含可疑内容: {threat}"
            
            return True, "请求安全"
            
        except Exception as e:
            logger.error(f"安全检查失败: {str(e)}")
            return True, "安全检查异常，允许通过"
    
    def _check_string_for_threats(self, input_string: str) -> Optional[str]:
        """检查字符串是否包含威胁"""
        import re
        
        input_lower = input_string.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return f"匹配可疑模式: {pattern}"
        
        return None


# 全局实例
rate_limiter = RateLimiter()
security_protector = SecurityProtector()


def rate_limit(requests_per_minute: int = None, requests_per_hour: int = None):
    """
    请求频率限制装饰器
    
    Args:
        requests_per_minute: 每分钟请求限制
        requests_per_hour: 每小时请求限制
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取客户端IP
            client_ip = get_client_ip()
            
            # 获取端点信息
            endpoint = request.endpoint
            
            # 检查请求频率
            allowed, limit_info = rate_limiter.is_allowed(client_ip, endpoint)
            
            if not allowed:
                logger.warning(f"请求被限制: IP={client_ip}, 端点={endpoint}, 原因={limit_info}")
                
                response_data = {
                    'success': False,
                    'message': '请求过于频繁，请稍后再试',
                    'error_code': 'RATE_LIMITED',
                    'limit_info': limit_info
                }
                
                return jsonify(response_data), 429
            
            # 在响应头中添加限制信息
            response = func(*args, **kwargs)
            
            if hasattr(response, 'headers'):
                limits = limit_info.get('limits', {})
                response.headers['X-RateLimit-Limit-Minute'] = str(limits.get('requests_per_minute', 60))
                response.headers['X-RateLimit-Limit-Hour'] = str(limits.get('requests_per_hour', 1000))
                response.headers['X-RateLimit-Remaining-Minute'] = str(max(0, limits.get('requests_per_minute', 60) - limit_info.get('minute_requests', 0)))
                response.headers['X-RateLimit-Remaining-Hour'] = str(max(0, limits.get('requests_per_hour', 1000) - limit_info.get('hour_requests', 0)))
            
            return response
        
        return wrapper
    return decorator


def security_check():
    """安全检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 收集请求数据
                request_data = {}
                
                # 获取查询参数
                request_data.update(request.args.to_dict())
                
                # 获取表单数据
                if request.form:
                    request_data.update(request.form.to_dict())
                
                # 获取JSON数据
                if request.is_json:
                    json_data = request.get_json(silent=True)
                    if json_data:
                        request_data.update(json_data)
                
                # 执行安全检查
                is_safe, threat_description = security_protector.check_request_security(request_data)
                
                if not is_safe:
                    client_ip = get_client_ip()
                    logger.warning(f"安全威胁检测: IP={client_ip}, 威胁={threat_description}")
                    
                    response_data = {
                        'success': False,
                        'message': '请求包含不安全内容',
                        'error_code': 'SECURITY_THREAT'
                    }
                    
                    return jsonify(response_data), 400
                
                return func(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"安全检查异常: {str(e)}")
                # 异常时允许请求通过
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def get_client_ip() -> str:
    """获取客户端IP地址"""
    # 检查代理头
    if request.headers.get('X-Forwarded-For'):
        # 获取第一个IP（客户端真实IP）
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    elif request.headers.get('CF-Connecting-IP'):  # Cloudflare
        return request.headers.get('CF-Connecting-IP')
    else:
        return request.remote_addr or 'unknown'


def log_request_info():
    """记录请求信息"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            client_ip = get_client_ip()
            user_agent = request.headers.get('User-Agent', 'Unknown')
            
            logger.info(f"API请求开始: {request.method} {request.path} - IP: {client_ip}")
            
            try:
                response = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                status_code = getattr(response, 'status_code', 200)
                logger.info(f"API请求完成: {request.method} {request.path} - IP: {client_ip} - 状态: {status_code} - 耗时: {execution_time:.2f}s")
                
                return response
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"API请求失败: {request.method} {request.path} - IP: {client_ip} - 错误: {str(e)} - 耗时: {execution_time:.2f}s")
                raise
        
        return wrapper
    return decorator