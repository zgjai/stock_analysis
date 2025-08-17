"""
案例管理API路由
"""
import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.exceptions import RequestEntityTooLarge
from services.case_service import CaseService
from error_handlers import ValidationError, FileOperationError, NotFoundError, create_success_response, create_error_response
from datetime import datetime

case_bp = Blueprint('case', __name__, url_prefix='/api/cases')
case_service = CaseService()


@case_bp.route('', methods=['GET'])
def get_cases():
    """获取案例列表"""
    try:
        # 获取查询参数
        keyword = request.args.get('keyword')
        stock_code = request.args.get('stock_code')
        tags = request.args.getlist('tags')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # 处理日期参数
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 搜索案例
        result = case_service.search_cases(
            keyword=keyword,
            stock_code=stock_code,
            tags=tags,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )
        
        return create_success_response(result)
        
    except ValueError as e:
        return create_error_response("INVALID_PARAMETER", "参数格式错误", 400, str(e))
    except Exception as e:
        return create_error_response("QUERY_ERROR", "获取案例列表失败", 500, str(e))


@case_bp.route('', methods=['POST'])
def upload_case():
    """上传案例"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return create_error_response("MISSING_FILE", "请选择要上传的文件", 400)
        
        file = request.files['file']
        if file.filename == '':
            return create_error_response("EMPTY_FILE", "请选择要上传的文件", 400)
        
        # 获取其他参数
        stock_code = request.form.get('stock_code')
        title = request.form.get('title')
        tags_str = request.form.get('tags', '[]')
        notes = request.form.get('notes')
        
        # 解析标签
        import json
        try:
            tags = json.loads(tags_str) if tags_str else []
        except json.JSONDecodeError:
            tags = []
        
        # 上传案例
        result = case_service.upload_image(
            file=file,
            stock_code=stock_code,
            title=title,
            tags=tags,
            notes=notes
        )
        
        return create_success_response(result, "案例上传成功")
        
    except RequestEntityTooLarge:
        return create_error_response("FILE_TOO_LARGE", "文件大小超过限制", 400)
    except ValidationError as e:
        return create_error_response("VALIDATION_ERROR", e.message, 400, getattr(e, "field", None))
    except FileOperationError as e:
        return create_error_response("FILE_OPERATION_ERROR", e.message, 500)
    except Exception as e:
        return create_error_response("UPLOAD_ERROR", "案例上传失败", 400, str(e))


@case_bp.route('/<int:case_id>', methods=['GET'])
def get_case(case_id):
    """获取单个案例详情"""
    try:
        case = case_service.get_by_id(case_id)
        return create_success_response(case.to_dict())
        
    except NotFoundError as e:
        return create_error_response("NOT_FOUND", "案例不存在", 404)
    except Exception as e:
        return create_error_response("QUERY_ERROR", "获取案例详情失败", 400, str(e))


@case_bp.route('/<int:case_id>', methods=['PUT'])
def update_case(case_id):
    """更新案例信息"""
    try:
        data = request.get_json()
        if not data:
            return create_error_response("MISSING_DATA", "请提供更新数据", 400)
        
        result = case_service.update_case(case_id, **data)
        return create_success_response(result, "案例更新成功")
        
    except NotFoundError as e:
        return create_error_response("NOT_FOUND", "案例不存在", 404)
    except ValidationError as e:
        return create_error_response("VALIDATION_ERROR", e.message, 400, getattr(e, "field", None))
    except Exception as e:
        return create_error_response("UPDATE_ERROR", "案例更新失败", 400, str(e))


@case_bp.route('/<int:case_id>', methods=['DELETE'])
def delete_case(case_id):
    """删除案例"""
    try:
        case_service.delete_case(case_id)
        return create_success_response(None, "案例删除成功")
        
    except NotFoundError as e:
        return create_error_response("NOT_FOUND", "案例不存在", 404)
    except ValidationError as e:
        return create_error_response("VALIDATION_ERROR", e.message, 400, getattr(e, "field", None))
    except Exception as e:
        return create_error_response("DELETE_ERROR", "案例删除失败", 400, str(e))


@case_bp.route('/<int:case_id>/image', methods=['GET'])
def get_case_image(case_id):
    """获取案例图片"""
    try:
        case = case_service.get_by_id(case_id)
        
        if not case.image_path or not os.path.exists(case.image_path):
            return create_error_response("FILE_NOT_FOUND", "图片文件不存在", 400)
        
        # Convert to absolute path if it's relative
        image_path = case.image_path
        if not os.path.isabs(image_path):
            image_path = os.path.abspath(image_path)
        
        return send_file(image_path)
        
    except NotFoundError as e:
        return create_error_response("NOT_FOUND", "案例不存在", 404)
    except ValidationError as e:
        return create_error_response("VALIDATION_ERROR", e.message, 400, getattr(e, "field", None))
    except Exception as e:
        return create_error_response("FILE_ERROR", "获取图片失败", 400, str(e))


@case_bp.route('/by-stock/<stock_code>', methods=['GET'])
def get_cases_by_stock(stock_code):
    """根据股票代码获取案例"""
    try:
        cases = case_service.get_cases_by_stock_code(stock_code)
        return create_success_response(cases)
        
    except Exception as e:
        return create_error_response("QUERY_ERROR", "获取案例失败", 400, str(e))


@case_bp.route('/by-tag/<tag>', methods=['GET'])
def get_cases_by_tag(tag):
    """根据标签获取案例"""
    try:
        cases = case_service.get_cases_by_tag(tag)
        return create_success_response(cases)
        
    except Exception as e:
        return create_error_response("QUERY_ERROR", "获取案例失败", 400, str(e))


@case_bp.route('/tags', methods=['GET'])
def get_all_tags():
    """获取所有标签"""
    try:
        tags = case_service.get_all_tags()
        return create_success_response(tags)
        
    except Exception as e:
        return create_error_response("QUERY_ERROR", "获取标签失败", 400, str(e))


@case_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取案例统计信息"""
    try:
        stats = case_service.get_statistics()
        return create_success_response(stats)
        
    except Exception as e:
        return create_error_response("QUERY_ERROR", "获取统计信息失败", 400, str(e))


@case_bp.route('/search', methods=['POST'])
def search_cases():
    """高级搜索案例"""
    try:
        data = request.get_json()
        if not data:
            data = {}
        
        result = case_service.search_cases(
            keyword=data.get('keyword'),
            stock_code=data.get('stock_code'),
            tags=data.get('tags'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d') if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d') if data.get('end_date') else None,
            page=data.get('page', 1),
            per_page=data.get('per_page', 20)
        )
        
        return create_success_response(result)
        
    except ValueError as e:
        return create_error_response("INVALID_DATE_FORMAT", "日期格式错误", 400, str(e))
    except Exception as e:
        return create_error_response("SEARCH_ERROR", "搜索失败", 400, str(e))


# 错误处理
@case_bp.errorhandler(413)
def too_large(e):
    return create_error_response("FILE_TOO_LARGE", "文件大小超过限制", 400)


@case_bp.errorhandler(400)
def bad_request(e):
    return create_error_response("BAD_REQUEST", "请求参数错误", 400)