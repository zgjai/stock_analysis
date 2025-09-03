"""
输入验证和清理工具
"""
import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from error_handlers import ValidationError

logger = logging.getLogger(__name__)


class InputValidator:
    """输入验证器"""
    
    # 正则表达式模式
    PATTERNS = {
        'stock_code': r'^[0-9]{6}$',
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^1[3-9]\d{9}$',
        'date': r'^\d{4}-\d{2}-\d{2}$',
        'datetime': r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
        'decimal': r'^-?\d+(\.\d+)?$',
        'integer': r'^-?\d+$',
        'positive_integer': r'^[1-9]\d*$',
        'non_negative_integer': r'^(0|[1-9]\d*)$',
    }
    
    @classmethod
    def validate_stock_code(cls, stock_code: Any) -> str:
        """
        验证股票代码
        
        Args:
            stock_code: 股票代码
            
        Returns:
            str: 验证后的股票代码
            
        Raises:
            ValidationError: 验证失败
        """
        if not stock_code:
            raise ValidationError("股票代码不能为空", "stock_code")
        
        # 转换为字符串并清理
        code_str = str(stock_code).strip()
        
        # 格式验证
        if not re.match(cls.PATTERNS['stock_code'], code_str):
            raise ValidationError("股票代码必须是6位数字", "stock_code")
        
        return code_str
    
    @classmethod
    def validate_stock_name(cls, stock_name: Any) -> str:
        """
        验证股票名称
        
        Args:
            stock_name: 股票名称
            
        Returns:
            str: 验证后的股票名称
        """
        if not stock_name:
            raise ValidationError("股票名称不能为空", "stock_name")
        
        # 转换为字符串并清理
        name_str = str(stock_name).strip()
        
        # 长度验证
        if len(name_str) > 50:
            raise ValidationError("股票名称不能超过50个字符", "stock_name")
        
        # 清理特殊字符
        name_str = cls._sanitize_string(name_str)
        
        return name_str
    
    @classmethod
    def validate_price(cls, price: Any, field_name: str = "price") -> Decimal:
        """
        验证价格
        
        Args:
            price: 价格值
            field_name: 字段名称
            
        Returns:
            Decimal: 验证后的价格
        """
        if price is None:
            raise ValidationError(f"{field_name}不能为空", field_name)
        
        try:
            # 转换为Decimal
            if isinstance(price, str):
                price = price.strip()
                if not price:
                    raise ValidationError(f"{field_name}不能为空", field_name)
            
            decimal_price = Decimal(str(price))
            
            # 范围验证
            if decimal_price <= 0:
                raise ValidationError(f"{field_name}必须大于0", field_name)
            
            if decimal_price > Decimal('9999999.99'):
                raise ValidationError(f"{field_name}不能超过9999999.99", field_name)
            
            # 精度验证（最多2位小数）
            if decimal_price.as_tuple().exponent < -2:
                raise ValidationError(f"{field_name}最多保留2位小数", field_name)
            
            return decimal_price
            
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(f"{field_name}格式不正确", field_name)
    
    @classmethod
    def validate_quantity(cls, quantity: Any, field_name: str = "quantity") -> int:
        """
        验证数量
        
        Args:
            quantity: 数量值
            field_name: 字段名称
            
        Returns:
            int: 验证后的数量
        """
        if quantity is None:
            raise ValidationError(f"{field_name}不能为空", field_name)
        
        try:
            # 转换为整数
            if isinstance(quantity, str):
                quantity = quantity.strip()
                if not quantity:
                    raise ValidationError(f"{field_name}不能为空", field_name)
            
            int_quantity = int(quantity)
            
            # 范围验证
            if int_quantity <= 0:
                raise ValidationError(f"{field_name}必须大于0", field_name)
            
            if int_quantity > 999999999:
                raise ValidationError(f"{field_name}不能超过999999999", field_name)
            
            return int_quantity
            
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}必须是整数", field_name)
    
    @classmethod
    def validate_date(cls, date_value: Any, field_name: str = "date") -> datetime:
        """
        验证日期
        
        Args:
            date_value: 日期值
            field_name: 字段名称
            
        Returns:
            datetime: 验证后的日期
        """
        if date_value is None:
            raise ValidationError(f"{field_name}不能为空", field_name)
        
        # 如果已经是datetime对象
        if isinstance(date_value, datetime):
            return date_value
        
        # 如果是date对象
        if isinstance(date_value, date):
            return datetime.combine(date_value, datetime.min.time())
        
        # 字符串格式处理
        if isinstance(date_value, str):
            date_str = date_value.strip()
            if not date_str:
                raise ValidationError(f"{field_name}不能为空", field_name)
            
            # 尝试多种日期格式
            date_formats = [
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%fZ',
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            raise ValidationError(f"{field_name}日期格式不正确", field_name)
        
        raise ValidationError(f"{field_name}类型不正确", field_name)
    
    @classmethod
    def validate_percentage(cls, percentage: Any, field_name: str = "percentage") -> Decimal:
        """
        验证百分比
        
        Args:
            percentage: 百分比值
            field_name: 字段名称
            
        Returns:
            Decimal: 验证后的百分比（小数形式）
        """
        if percentage is None:
            return None
        
        try:
            # 转换为Decimal
            if isinstance(percentage, str):
                percentage = percentage.strip()
                if not percentage:
                    return None
                
                # 处理百分号
                if percentage.endswith('%'):
                    percentage = percentage[:-1]
                    decimal_percentage = Decimal(percentage) / 100
                else:
                    decimal_percentage = Decimal(percentage)
            else:
                decimal_percentage = Decimal(str(percentage))
            
            # 范围验证（-100% 到 1000%）
            if decimal_percentage < Decimal('-1.0') or decimal_percentage > Decimal('10.0'):
                raise ValidationError(f"{field_name}必须在-100%到1000%之间", field_name)
            
            return decimal_percentage
            
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(f"{field_name}格式不正确", field_name)
    
    @classmethod
    def validate_score(cls, score: Any, field_name: str = "score") -> Optional[int]:
        """
        验证评分
        
        Args:
            score: 评分值
            field_name: 字段名称
            
        Returns:
            Optional[int]: 验证后的评分
        """
        if score is None or score == '':
            return None
        
        try:
            # 转换为整数
            if isinstance(score, str):
                score = score.strip()
                if not score:
                    return None
            
            int_score = int(score)
            
            # 范围验证（1-5分）
            if int_score < 1 or int_score > 5:
                raise ValidationError(f"{field_name}必须在1-5之间", field_name)
            
            return int_score
            
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}必须是1-5之间的整数", field_name)
    
    @classmethod
    def validate_text(cls, text: Any, field_name: str = "text", 
                     max_length: int = None, required: bool = False) -> Optional[str]:
        """
        验证文本
        
        Args:
            text: 文本值
            field_name: 字段名称
            max_length: 最大长度
            required: 是否必填
            
        Returns:
            Optional[str]: 验证后的文本
        """
        if text is None or text == '':
            if required:
                raise ValidationError(f"{field_name}不能为空", field_name)
            return None
        
        # 转换为字符串并清理
        text_str = str(text).strip()
        
        if not text_str and required:
            raise ValidationError(f"{field_name}不能为空", field_name)
        
        if not text_str:
            return None
        
        # 长度验证
        if max_length and len(text_str) > max_length:
            raise ValidationError(f"{field_name}不能超过{max_length}个字符", field_name)
        
        # 清理文本
        text_str = cls._sanitize_string(text_str)
        
        return text_str
    
    @classmethod
    def validate_review_type(cls, review_type: Any) -> str:
        """
        验证复盘类型
        
        Args:
            review_type: 复盘类型
            
        Returns:
            str: 验证后的复盘类型
        """
        if not review_type:
            return 'general'  # 默认类型
        
        valid_types = ['general', 'success', 'failure', 'lesson']
        type_str = str(review_type).strip().lower()
        
        if type_str not in valid_types:
            raise ValidationError(f"复盘类型必须是{', '.join(valid_types)}之一", "review_type")
        
        return type_str
    
    @classmethod
    def validate_pagination_params(cls, page: Any, per_page: Any) -> tuple:
        """
        验证分页参数
        
        Args:
            page: 页码
            per_page: 每页数量
            
        Returns:
            tuple: (页码, 每页数量)
        """
        # 验证页码
        if page is not None:
            try:
                page_int = int(page)
                if page_int < 1:
                    raise ValidationError("页码必须大于0", "page")
                if page_int > 10000:
                    raise ValidationError("页码不能超过10000", "page")
            except (ValueError, TypeError):
                raise ValidationError("页码必须是整数", "page")
        else:
            page_int = None
        
        # 验证每页数量
        if per_page is not None:
            try:
                per_page_int = int(per_page)
                if per_page_int < 1:
                    raise ValidationError("每页数量必须大于0", "per_page")
                if per_page_int > 100:
                    raise ValidationError("每页数量不能超过100", "per_page")
            except (ValueError, TypeError):
                raise ValidationError("每页数量必须是整数", "per_page")
        else:
            per_page_int = 20  # 默认每页20条
        
        return page_int, per_page_int
    
    @classmethod
    def validate_sort_params(cls, sort_by: Any, sort_order: Any, 
                           allowed_fields: List[str]) -> tuple:
        """
        验证排序参数
        
        Args:
            sort_by: 排序字段
            sort_order: 排序方向
            allowed_fields: 允许的排序字段
            
        Returns:
            tuple: (排序字段, 排序方向)
        """
        # 验证排序字段
        if sort_by is not None:
            sort_by_str = str(sort_by).strip()
            if sort_by_str not in allowed_fields:
                raise ValidationError(f"排序字段必须是{', '.join(allowed_fields)}之一", "sort_by")
        else:
            sort_by_str = allowed_fields[0] if allowed_fields else 'id'
        
        # 验证排序方向
        if sort_order is not None:
            sort_order_str = str(sort_order).strip().lower()
            if sort_order_str not in ['asc', 'desc']:
                raise ValidationError("排序方向必须是asc或desc", "sort_order")
        else:
            sort_order_str = 'desc'
        
        return sort_by_str, sort_order_str
    
    @classmethod
    def _sanitize_string(cls, input_str: str) -> str:
        """
        清理字符串
        
        Args:
            input_str: 输入字符串
            
        Returns:
            str: 清理后的字符串
        """
        if not input_str:
            return ""
        
        # HTML转义
        sanitized = html.escape(input_str)
        
        # 移除控制字符
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        # 规范化空白字符
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized.strip()


class DataSanitizer:
    """数据清理器"""
    
    @staticmethod
    def sanitize_historical_trade_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理历史交易数据
        
        Args:
            data: 原始数据
            
        Returns:
            Dict: 清理后的数据
        """
        sanitized = {}
        
        # 股票代码
        if 'stock_code' in data:
            sanitized['stock_code'] = InputValidator.validate_stock_code(data['stock_code'])
        
        # 股票名称
        if 'stock_name' in data:
            sanitized['stock_name'] = InputValidator.validate_stock_name(data['stock_name'])
        
        # 日期字段
        for date_field in ['buy_date', 'sell_date', 'completion_date']:
            if date_field in data:
                sanitized[date_field] = InputValidator.validate_date(data[date_field], date_field)
        
        # 数值字段
        for price_field in ['total_investment', 'total_return']:
            if price_field in data:
                sanitized[price_field] = InputValidator.validate_price(data[price_field], price_field)
        
        # 收益率
        if 'return_rate' in data:
            sanitized['return_rate'] = InputValidator.validate_percentage(data['return_rate'], 'return_rate')
        
        # 持仓天数
        if 'holding_days' in data:
            sanitized['holding_days'] = InputValidator.validate_quantity(data['holding_days'], 'holding_days')
        
        # 布尔字段
        if 'is_completed' in data:
            sanitized['is_completed'] = bool(data['is_completed'])
        
        # 记录ID列表
        for id_field in ['buy_records_ids', 'sell_records_ids']:
            if id_field in data:
                sanitized[id_field] = data[id_field]  # 保持原样，由模型处理
        
        return sanitized
    
    @staticmethod
    def sanitize_review_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理复盘数据
        
        Args:
            data: 原始数据
            
        Returns:
            Dict: 清理后的数据
        """
        sanitized = {}
        
        # 历史交易ID
        if 'historical_trade_id' in data:
            sanitized['historical_trade_id'] = InputValidator.validate_quantity(
                data['historical_trade_id'], 'historical_trade_id'
            )
        
        # 文本字段
        text_fields = {
            'review_title': 200,
            'review_content': None,
            'key_learnings': None,
            'improvement_areas': None
        }
        
        for field, max_length in text_fields.items():
            if field in data:
                sanitized[field] = InputValidator.validate_text(
                    data[field], field, max_length=max_length
                )
        
        # 复盘类型
        if 'review_type' in data:
            sanitized['review_type'] = InputValidator.validate_review_type(data['review_type'])
        
        # 评分字段
        score_fields = ['strategy_score', 'timing_score', 'risk_control_score', 'overall_score']
        for field in score_fields:
            if field in data:
                sanitized[field] = InputValidator.validate_score(data[field], field)
        
        return sanitized
    
    @staticmethod
    def sanitize_filter_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理筛选参数
        
        Args:
            params: 原始参数
            
        Returns:
            Dict: 清理后的参数
        """
        sanitized = {}
        
        # 股票代码
        if 'stock_code' in params and params['stock_code']:
            try:
                sanitized['stock_code'] = InputValidator.validate_stock_code(params['stock_code'])
            except ValidationError:
                pass  # 忽略无效的股票代码
        
        # 股票名称
        if 'stock_name' in params and params['stock_name']:
            sanitized['stock_name'] = InputValidator.validate_text(
                params['stock_name'], 'stock_name', max_length=50
            )
        
        # 日期范围
        for date_field in ['start_date', 'end_date']:
            if date_field in params and params[date_field]:
                try:
                    sanitized[date_field] = InputValidator.validate_date(params[date_field], date_field)
                except ValidationError:
                    pass  # 忽略无效的日期
        
        # 数值范围
        numeric_fields = [
            'min_return_rate', 'max_return_rate',
            'min_holding_days', 'max_holding_days',
            'min_overall_score', 'max_overall_score'
        ]
        
        for field in numeric_fields:
            if field in params and params[field] is not None:
                try:
                    if 'return_rate' in field:
                        sanitized[field] = InputValidator.validate_percentage(params[field], field)
                    elif 'score' in field:
                        sanitized[field] = InputValidator.validate_score(params[field], field)
                    else:
                        sanitized[field] = InputValidator.validate_quantity(params[field], field)
                except ValidationError:
                    pass  # 忽略无效的数值
        
        # 布尔字段
        if 'is_profitable' in params and params['is_profitable'] is not None:
            profitable_str = str(params['is_profitable']).lower()
            if profitable_str in ['true', '1', 'yes']:
                sanitized['is_profitable'] = True
            elif profitable_str in ['false', '0', 'no']:
                sanitized['is_profitable'] = False
        
        # 复盘类型
        if 'review_type' in params and params['review_type']:
            try:
                sanitized['review_type'] = InputValidator.validate_review_type(params['review_type'])
            except ValidationError:
                pass  # 忽略无效的复盘类型
        
        return sanitized


def validate_request_data(validation_rules: Dict[str, Dict[str, Any]]):
    """
    请求数据验证装饰器
    
    Args:
        validation_rules: 验证规则字典
    """
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            
            try:
                # 获取请求数据
                if request.is_json:
                    data = request.get_json() or {}
                else:
                    data = request.form.to_dict()
                    data.update(request.args.to_dict())
                
                # 验证数据
                validated_data = {}
                
                for field, rules in validation_rules.items():
                    value = data.get(field)
                    
                    # 检查必填字段
                    if rules.get('required', False) and (value is None or value == ''):
                        raise ValidationError(f"{field}是必填字段", field)
                    
                    # 如果值为空且不是必填，跳过验证
                    if value is None or value == '':
                        continue
                    
                    # 根据类型验证
                    field_type = rules.get('type', 'string')
                    
                    if field_type == 'stock_code':
                        validated_data[field] = InputValidator.validate_stock_code(value)
                    elif field_type == 'price':
                        validated_data[field] = InputValidator.validate_price(value, field)
                    elif field_type == 'quantity':
                        validated_data[field] = InputValidator.validate_quantity(value, field)
                    elif field_type == 'date':
                        validated_data[field] = InputValidator.validate_date(value, field)
                    elif field_type == 'percentage':
                        validated_data[field] = InputValidator.validate_percentage(value, field)
                    elif field_type == 'score':
                        validated_data[field] = InputValidator.validate_score(value, field)
                    elif field_type == 'text':
                        max_length = rules.get('max_length')
                        validated_data[field] = InputValidator.validate_text(
                            value, field, max_length=max_length, required=rules.get('required', False)
                        )
                    else:
                        validated_data[field] = value
                
                # 将验证后的数据添加到请求上下文
                from flask import g
                g.validated_data = validated_data
                
                return func(*args, **kwargs)
                
            except ValidationError as e:
                logger.warning(f"请求数据验证失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': str(e),
                    'error_code': 'VALIDATION_ERROR',
                    'field': getattr(e, 'field', None)
                }), 400
            except Exception as e:
                logger.error(f"请求数据验证异常: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': '数据验证失败',
                    'error_code': 'VALIDATION_EXCEPTION'
                }), 500
        
        return wrapper
    return decorator