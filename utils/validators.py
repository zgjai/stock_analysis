"""
数据验证工具函数
"""
import re
from error_handlers import ValidationError

def validate_stock_code(stock_code):
    """验证股票代码格式"""
    if not stock_code:
        raise ValidationError("股票代码不能为空", "stock_code")
    
    # A股股票代码格式：6位数字
    if not re.match(r'^\d{6}$', stock_code):
        raise ValidationError("股票代码格式不正确，应为6位数字", "stock_code")
    
    return True

def validate_price(price):
    """验证价格格式"""
    if price is None:
        raise ValidationError("价格不能为空", "price")
    
    try:
        price_float = float(price)
        if price_float <= 0:
            raise ValidationError("价格必须大于0", "price")
        if price_float > 9999.99:
            raise ValidationError("价格不能超过9999.99", "price")
        return price_float
    except (ValueError, TypeError):
        raise ValidationError("价格格式不正确", "price")

def validate_quantity(quantity, stock_code=None):
    """验证数量格式"""
    if quantity is None:
        raise ValidationError("数量不能为空", "quantity")
    
    try:
        quantity_int = int(quantity)
        if quantity_int <= 0:
            raise ValidationError("数量必须大于0", "quantity")
        if quantity_int > 999999:
            raise ValidationError("数量不能超过999999", "quantity")
        
        # 如果提供了股票代码，使用股票特定的验证规则
        if stock_code:
            from utils.stock_utils import validate_stock_quantity
            is_valid, error_message = validate_stock_quantity(stock_code, quantity_int)
            if not is_valid:
                raise ValidationError(error_message, "quantity")
        else:
            # 默认验证规则：必须是100的倍数
            if quantity_int % 100 != 0:
                raise ValidationError("数量必须是100的倍数", "quantity")
        
        return quantity_int
    except (ValueError, TypeError):
        raise ValidationError("数量格式不正确", "quantity")

def validate_trade_type(trade_type):
    """验证交易类型"""
    if not trade_type:
        raise ValidationError("交易类型不能为空", "trade_type")
    
    if trade_type not in ['buy', 'sell']:
        raise ValidationError("交易类型必须是buy或sell", "trade_type")
    
    return trade_type

def validate_ratio(ratio, field_name):
    """验证比例值（0-1之间）"""
    if ratio is None:
        return None
    
    try:
        ratio_float = float(ratio)
        if ratio_float < 0 or ratio_float > 1:
            raise ValidationError(f"{field_name}必须在0-1之间", field_name)
        return ratio_float
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name}格式不正确", field_name)

def validate_date(date_str):
    """验证日期格式"""
    if not date_str:
        raise ValidationError("日期不能为空", "date")
    
    try:
        from datetime import datetime
        # 支持 YYYY-MM-DD 格式
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        return parsed_date
    except ValueError:
        raise ValidationError("日期格式不正确，应为YYYY-MM-DD", "date")

def validate_positive_integer(value, field_name):
    """验证正整数"""
    if value is None:
        raise ValidationError(f"{field_name}不能为空", field_name)
    
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValidationError(f"{field_name}必须大于0", field_name)
        return int_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name}必须是正整数", field_name)