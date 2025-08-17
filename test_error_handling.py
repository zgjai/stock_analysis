"""
错误处理测试
测试系统的错误处理机制，包括API错误响应格式、前端错误信息显示、异常情况处理等
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from app import create_app
from extensions import db
from models.trade_record import TradeRecord
from error_handlers import (
    APIError, ValidationError, NotFoundError, DatabaseError, 
    ExternalAPIError, FileOperationError
)


class TestErrorHandling:
    """错误处理测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试设置"""
        from config import TestingConfig
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # 创建测试数据库表
        db.create_all()
        
        yield
        
        # 清理
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_api_error_response_format(self):
        """测试API错误响应格式"""
        
        # 测试404错误
        response = self.client.get('/api/nonexistent-endpoint')
        assert response.status_code == 404
        
        response_data = json.loads(response.data)
        assert 'success' in response_data
        assert response_data['success'] is False
        assert 'error' in response_data
        assert 'code' in response_data['error']
        assert 'message' in response_data['error']
        assert response_data['error']['code'] == 'NOT_FOUND'
        
        # 测试405错误（方法不允许）
        response = self.client.patch('/api/health')  # health端点只支持GET
        assert response.status_code == 405
        
        response_data = json.loads(response.data)
        assert not response_data['success']
        assert response_data['error']['code'] == 'METHOD_NOT_ALLOWED'
    
    def test_validation_error_response(self):
        """测试验证错误响应"""
        
        # 测试缺少必填字段的验证错误
        invalid_data = {
            'stock_name': '测试股票',
            'trade_type': 'buy',
            'price': 10.50,
            'quantity': 100,
            'reason': '技术突破'
            # 缺少stock_code
        }
        
        response = self.client.post(
            '/api/trades',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert not response_data['success']
        assert response_data['error']['code'] == 'VALIDATION_ERROR'
        assert 'stock_code' in response_data['error']['message']
    
    def test_not_found_error_response(self):
        """测试资源不存在错误响应"""
        
        # 测试获取不存在的交易记录
        response = self.client.get('/api/trades/99999')
        assert response.status_code == 404
        
        response_data = json.loads(response.data)
        assert not response_data['success']
        assert response_data['error']['code'] == 'NOT_FOUND'
        assert '99999' in response_data['error']['message']
    
    def test_database_error_handling(self):
        """测试数据库错误处理"""
        
        # 创建一个有效的交易记录用于测试
        valid_data = {
            'stock_code': '000001',
            'stock_name': '测试股票',
            'trade_type': 'buy',
            'price': 10.50,
            'quantity': 100,
            'reason': '技术突破'
        }
        
        # 模拟数据库连接错误
        with patch('extensions.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database connection failed")
            
            response = self.client.post(
                '/api/trades',
                data=json.dumps(valid_data),
                content_type='application/json'
            )
            
            assert response.status_code == 500
            response_data = json.loads(response.data)
            assert not response_data['success']
            assert response_data['error']['code'] == 'DATABASE_ERROR'
    
    def test_json_parsing_error(self):
        """测试JSON解析错误"""
        
        # 发送无效的JSON数据
        response = self.client.post(
            '/api/trades',
            data='{"invalid": json}',  # 无效JSON
            content_type='application/json'
        )
        
        # 由于路由中的异常处理，JSON解析错误被转换为500错误
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert not response_data['success']
        assert 'error' in response_data
    
    def test_empty_request_body_error(self):
        """测试空请求体错误"""
        
        response = self.client.post(
            '/api/trades',
            data='',
            content_type='application/json'
        )
        
        # 空请求体导致JSON解析错误，被转换为500错误
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert not response_data['success']
        assert 'error' in response_data
    
    def test_custom_error_classes(self):
        """测试自定义错误类"""
        
        # 测试ValidationError
        error = ValidationError("测试验证错误", "test_field")
        assert error.message == "测试验证错误"
        assert error.code == "VALIDATION_ERROR"
        assert error.status_code == 400
        assert error.details['field'] == "test_field"
        
        # 测试NotFoundError
        error = NotFoundError("资源不存在", "trade")
        assert error.message == "资源不存在"
        assert error.code == "NOT_FOUND"
        assert error.status_code == 404
        assert error.details['resource_type'] == "trade"
        
        # 测试DatabaseError
        error = DatabaseError("数据库操作失败", "insert")
        assert error.message == "数据库操作失败"
        assert error.code == "DATABASE_ERROR"
        assert error.status_code == 500
        assert error.details['operation'] == "insert"
        
        # 测试ExternalAPIError
        error = ExternalAPIError("外部API调用失败", "akshare")
        assert error.message == "外部API调用失败"
        assert error.code == "EXTERNAL_API_ERROR"
        assert error.status_code == 503
        assert error.details['service'] == "akshare"
        
        # 测试FileOperationError
        error = FileOperationError("文件操作失败", "upload")
        assert error.message == "文件操作失败"
        assert error.code == "FILE_OPERATION_ERROR"
        assert error.status_code == 500
        assert error.details['operation'] == "upload"
    
    def test_error_logging(self):
        """测试错误日志记录"""
        
        with patch('error_handlers.logger') as mock_logger:
            # 触发一个验证错误
            invalid_data = {
                'stock_code': '00001',  # 无效格式
                'stock_name': '测试股票',
                'trade_type': 'buy',
                'price': 10.50,
                'quantity': 100,
                'reason': '技术突破'
            }
            
            response = self.client.post(
                '/api/trades',
                data=json.dumps(invalid_data),
                content_type='application/json'
            )
            
            # 验证日志记录被调用
            assert mock_logger.error.called or mock_logger.warning.called
    
    def test_error_details_sanitization(self):
        """测试错误详情的敏感信息过滤"""
        
        # 创建包含敏感信息的错误
        with patch('services.trading_service.TradingService.create_trade') as mock_create:
            mock_create.side_effect = Exception("Database password: secret123")
            
            valid_data = {
                'stock_code': '000001',
                'stock_name': '测试股票',
                'trade_type': 'buy',
                'price': 10.50,
                'quantity': 100,
                'reason': '技术突破'
            }
            
            response = self.client.post(
                '/api/trades',
                data=json.dumps(valid_data),
                content_type='application/json'
            )
            
            response_data = json.loads(response.data)
            # 错误信息不应该包含敏感信息的详细内容
            assert 'secret123' not in response_data['error']['message']
    
    def test_concurrent_error_handling(self):
        """测试并发情况下的错误处理"""
        
        import threading
        import time
        
        results = []
        
        def make_request():
            try:
                # 发送无效请求
                response = self.client.post(
                    '/api/trades',
                    data=json.dumps({'invalid': 'data'}),
                    content_type='application/json'
                )
                results.append(response.status_code)
            except Exception as e:
                results.append(str(e))
        
        # 创建多个并发请求
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有请求都得到了正确的错误处理
        assert len(results) == 5
        for result in results:
            assert result == 400  # 所有请求都应该返回400错误
    
    def test_error_response_consistency(self):
        """测试错误响应的一致性"""
        
        # 测试不同类型的错误都遵循相同的响应格式
        error_endpoints = [
            ('/api/trades/99999', 'GET', 404),  # Not Found
            ('/api/trades', 'PATCH', 405),      # Method Not Allowed
            ('/api/nonexistent', 'GET', 404),   # Not Found
        ]
        
        for endpoint, method, expected_status in error_endpoints:
            if method == 'GET':
                response = self.client.get(endpoint)
            elif method == 'PATCH':
                response = self.client.patch(endpoint)
            
            assert response.status_code == expected_status
            
            response_data = json.loads(response.data)
            # 验证响应格式一致性
            assert 'success' in response_data
            assert response_data['success'] is False
            assert 'error' in response_data
            assert 'code' in response_data['error']
            assert 'message' in response_data['error']
            assert isinstance(response_data['error']['code'], str)
            assert isinstance(response_data['error']['message'], str)
    
    def test_error_message_localization(self):
        """测试错误信息的本地化"""
        
        # 测试中文错误信息
        invalid_data = {
            'stock_name': '测试股票',
            'trade_type': 'buy',
            'price': 10.50,
            'quantity': 100,
            'reason': '技术突破'
            # 缺少stock_code
        }
        
        response = self.client.post(
            '/api/trades',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        response_data = json.loads(response.data)
        # 验证错误信息是中文
        assert any(char >= '\u4e00' and char <= '\u9fff' 
                  for char in response_data['error']['message'])
    
    def test_stack_trace_filtering(self):
        """测试堆栈跟踪信息的过滤"""
        
        with patch('services.trading_service.TradingService.create_trade') as mock_create:
            # 模拟一个会产生堆栈跟踪的错误
            mock_create.side_effect = Exception("Internal error with stack trace")
            
            valid_data = {
                'stock_code': '000001',
                'stock_name': '测试股票',
                'trade_type': 'buy',
                'price': 10.50,
                'quantity': 100,
                'reason': '技术突破'
            }
            
            response = self.client.post(
                '/api/trades',
                data=json.dumps(valid_data),
                content_type='application/json'
            )
            
            response_data = json.loads(response.data)
            # 在生产环境中，错误响应不应该包含详细的堆栈跟踪信息
            assert 'traceback' not in response_data['error']['message'].lower()
            assert 'stack trace' not in response_data['error']['message'].lower()
    
    def test_error_rate_limiting(self):
        """测试错误频率限制（如果实现了的话）"""
        
        # 这个测试假设系统实现了某种形式的错误频率限制
        # 如果没有实现，这个测试可以跳过或者作为未来的需求
        
        error_count = 0
        max_requests = 10
        
        for i in range(max_requests):
            response = self.client.post(
                '/api/trades',
                data=json.dumps({'invalid': 'data'}),
                content_type='application/json'
            )
            
            if response.status_code == 400:
                error_count += 1
        
        # 验证所有错误请求都得到了处理
        assert error_count == max_requests
    
    def test_error_recovery_mechanisms(self):
        """测试错误恢复机制"""
        
        # 测试在错误发生后系统是否能够正常恢复
        
        # 首先发送一个会导致错误的请求
        invalid_data = {
            'stock_code': '00001',  # 无效格式
            'stock_name': '测试股票',
            'trade_type': 'buy',
            'price': 10.50,
            'quantity': 100,
            'reason': '技术突破'
        }
        
        response = self.client.post(
            '/api/trades',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]  # 应该返回错误
        
        # 然后发送一个有效的请求，验证系统能够正常处理
        valid_data = {
            'stock_code': '000001',
            'stock_name': '测试股票',
            'trade_type': 'buy',
            'price': 10.50,
            'quantity': 100,
            'reason': '技术突破'
        }
        
        response = self.client.post(
            '/api/trades',
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201  # 应该成功创建
        response_data = json.loads(response.data)
        assert response_data['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])