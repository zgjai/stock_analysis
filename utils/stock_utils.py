"""
股票工具函数
"""

def is_star_market_stock(stock_code: str) -> bool:
    """
    判断是否为科创板股票（68开头）
    
    Args:
        stock_code: 股票代码
        
    Returns:
        bool: 如果是科创板股票返回True，否则返回False
    """
    if not stock_code or not isinstance(stock_code, str):
        return False
    
    # 科创板股票代码以68开头
    return stock_code.strip().startswith('68')


def get_stock_quantity_rule(stock_code: str) -> dict:
    """
    获取股票数量验证规则
    
    Args:
        stock_code: 股票代码
        
    Returns:
        dict: 包含验证规则的字典
    """
    is_star_market = is_star_market_stock(stock_code)
    
    if is_star_market:
        return {
            'min_quantity': 1,
            'multiple_required': False,
            'multiple_value': None,
            'hint': '科创板股票可购买任意数量',
            'error_message': '数量必须大于0'
        }
    else:
        return {
            'min_quantity': 100,
            'multiple_required': True,
            'multiple_value': 100,
            'hint': '股票数量必须是100的倍数',
            'error_message': '数量必须是100的倍数且大于0'
        }


def validate_stock_quantity(stock_code: str, quantity) -> tuple[bool, str]:
    """
    验证股票数量是否符合规则
    
    Args:
        stock_code: 股票代码
        quantity: 股票数量（可以是字符串或整数）
        
    Returns:
        tuple: (是否有效, 错误消息)
    """
    if quantity is None:
        return False, "数量不能为空"
    
    # 确保quantity是整数类型
    try:
        quantity_int = int(quantity)
    except (ValueError, TypeError):
        return False, "数量必须是整数"
    
    if quantity_int <= 0:
        return False, "数量必须大于0"
    
    rule = get_stock_quantity_rule(stock_code)
    
    if rule['multiple_required']:
        if quantity_int % rule['multiple_value'] != 0:
            return False, rule['error_message']
    
    if quantity_int < rule['min_quantity']:
        return False, rule['error_message']
    
    return True, ""