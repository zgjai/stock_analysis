"""
错误处理中间件和API响应格式
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    """自定义API错误类"""
    def __init__(self, message, code='GENERIC_ERROR', status_code=400, details=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

class ValidationError(APIError):
    """数据验证错误"""
    def __init__(self, message, field=None, details=None):
        super().__init__(message, 'VALIDATION_ERROR', 400, details)
        if field:
            self.details['field'] = field

class NotFoundError(APIError):
    """资源不存在错误"""
    def __init__(self, message, resource_type=None):
        super().__init__(message, 'NOT_FOUND', 404)
        if resource_type:
            self.details['resource_type'] = resource_type

class DatabaseError(APIError):
    """数据库操作错误"""
    def __init__(self, message, operation=None):
        super().__init__(message, 'DATABASE_ERROR', 500)
        if operation:
            self.details['operation'] = operation

class ExternalAPIError(APIError):
    """外部API调用错误"""
    def __init__(self, message, service=None):
        super().__init__(message, 'EXTERNAL_API_ERROR', 503)
        if service:
            self.details['service'] = service

class FileOperationError(APIError):
    """文件操作错误"""
    def __init__(self, message, operation=None):
        super().__init__(message, 'FILE_OPERATION_ERROR', 500)
        if operation:
            self.details['operation'] = operation

def create_error_response(error_code, message, status_code=400, details=None):
    """创建标准错误响应"""
    return jsonify({
        'success': False,
        'error': {
            'code': error_code,
            'message': message,
            'details': details or {}
        }
    }), status_code

def create_success_response(data=None, message=None, warning=None):
    """创建标准成功响应"""
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    if warning:
        response['warning'] = warning
    return jsonify(response)

def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """处理自定义API错误"""
        logger.error(f"API Error: {error.message}, Code: {error.code}")
        return create_error_response(
            error.code, 
            error.message, 
            error.status_code, 
            error.details
        )
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """处理数据验证错误"""
        logger.warning(f"Validation Error: {error.message}")
        return create_error_response(
            error.code,
            error.message,
            error.status_code,
            error.details
        )
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        """处理资源不存在错误"""
        logger.warning(f"Not Found Error: {error.message}")
        return create_error_response(
            error.code,
            error.message,
            error.status_code,
            error.details
        )
    
    @app.errorhandler(DatabaseError)
    def handle_database_error(error):
        """处理数据库错误"""
        logger.error(f"Database Error: {error.message}")
        return create_error_response(
            error.code,
            error.message,
            error.status_code,
            error.details
        )
    
    @app.errorhandler(ExternalAPIError)
    def handle_external_api_error(error):
        """处理外部API错误"""
        logger.error(f"External API Error: {error.message}")
        return create_error_response(
            error.code,
            error.message,
            error.status_code,
            error.details
        )
    
    @app.errorhandler(FileOperationError)
    def handle_file_operation_error(error):
        """处理文件操作错误"""
        logger.error(f"File Operation Error: {error.message}")
        return create_error_response(
            error.code,
            error.message,
            error.status_code,
            error.details
        )
    
    @app.errorhandler(404)
    def handle_404(error):
        """处理404错误"""
        return create_error_response(
            'NOT_FOUND',
            '请求的资源不存在',
            404
        )
    
    @app.errorhandler(405)
    def handle_405(error):
        """处理方法不允许错误"""
        return create_error_response(
            'METHOD_NOT_ALLOWED',
            '请求方法不被允许',
            405
        )
    
    @app.errorhandler(500)
    def handle_500(error):
        """处理内部服务器错误"""
        logger.error(f"Internal Server Error: {str(error)}")
        return create_error_response(
            'INTERNAL_SERVER_ERROR',
            '服务器内部错误',
            500
        )
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """处理未预期的错误"""
        logger.error(f"Unexpected Error: {str(error)}", exc_info=True)
        return create_error_response(
            'UNEXPECTED_ERROR',
            '发生了未预期的错误',
            500
        )