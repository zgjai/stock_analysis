"""
非交易日管理API路由
"""
from flask import request, jsonify
from datetime import date
from . import api_bp
from services.non_trading_day_service import NonTradingDayService
from error_handlers import create_success_response, create_error_response, ValidationError, DatabaseError


@api_bp.route('/non-trading-days', methods=['GET'])
def get_non_trading_days():
    """获取非交易日列表"""
    try:
        # 获取查询参数
        year = request.args.get('year', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if year:
            # 按年份查询
            holidays = NonTradingDayService.get_holidays_by_year(year)
            return create_success_response(
                data=holidays,
                message=f'成功获取{year}年节假日列表'
            )
        elif start_date and end_date:
            # 按日期范围查询
            non_trading_days = NonTradingDayService.get_non_trading_days_in_range(start_date, end_date)
            return create_success_response(
                data=non_trading_days,
                message=f'成功获取{start_date}到{end_date}的非交易日列表'
            )
        else:
            # 获取所有记录
            all_holidays = NonTradingDayService.get_all()
            holidays_data = [holiday.to_dict() for holiday in all_holidays]
            return create_success_response(
                data=holidays_data,
                message='成功获取所有非交易日列表'
            )
            
    except Exception as e:
        return create_error_response(
            message=f'获取非交易日列表失败: {str(e)}',
            status_code=500
        )


@api_bp.route('/non-trading-days', methods=['POST'])
def add_non_trading_day():
    """添加非交易日"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('date') or not data.get('name'):
            return create_error_response(
                message='缺少必填字段: date, name',
                status_code=400
            )
        
        holiday = NonTradingDayService.add_holiday(
            holiday_date=data['date'],
            name=data['name'],
            description=data.get('description')
        )
        
        return create_success_response(
            data=holiday,
            message='成功添加非交易日',
            status_code=201
        )
        
    except ValidationError as e:
        return create_error_response(
            message=str(e),
            status_code=400
        )
    except DatabaseError as e:
        return create_error_response(
            message=str(e),
            status_code=500
        )
    except Exception as e:
        return create_error_response(
            message=f'添加非交易日失败: {str(e)}',
            status_code=500
        )


@api_bp.route('/non-trading-days/<int:holiday_id>', methods=['PUT'])
def update_non_trading_day(holiday_id):
    """更新非交易日"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response(
                message='请提供更新数据',
                status_code=400
            )
        
        # 过滤允许更新的字段
        allowed_fields = ['name', 'description']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return create_error_response(
                message='没有有效的更新字段',
                status_code=400
            )
        
        holiday = NonTradingDayService.update(holiday_id, update_data)
        
        return create_success_response(
            data=holiday.to_dict(),
            message='成功更新非交易日'
        )
        
    except ValidationError as e:
        return create_error_response(
            message=str(e),
            status_code=400
        )
    except DatabaseError as e:
        return create_error_response(
            message=str(e),
            status_code=500
        )
    except Exception as e:
        return create_error_response(
            message=f'更新非交易日失败: {str(e)}',
            status_code=500
        )


@api_bp.route('/non-trading-days/<int:holiday_id>', methods=['DELETE'])
def delete_non_trading_day(holiday_id):
    """删除非交易日"""
    try:
        NonTradingDayService.delete(holiday_id)
        
        return create_success_response(
            message='成功删除非交易日'
        )
        
    except ValidationError as e:
        return create_error_response(
            message=str(e),
            status_code=400
        )
    except DatabaseError as e:
        return create_error_response(
            message=str(e),
            status_code=500
        )
    except Exception as e:
        return create_error_response(
            message=f'删除非交易日失败: {str(e)}',
            status_code=500
        )


@api_bp.route('/non-trading-days/by-date/<date_str>', methods=['DELETE'])
def delete_non_trading_day_by_date(date_str):
    """根据日期删除非交易日"""
    try:
        success = NonTradingDayService.remove_holiday(date_str)
        
        if success:
            return create_success_response(
                message=f'成功删除日期 {date_str} 的非交易日配置'
            )
        else:
            return create_error_response(
                message=f'删除日期 {date_str} 的非交易日配置失败',
                status_code=500
            )
        
    except ValidationError as e:
        return create_error_response(
            message=str(e),
            status_code=400
        )
    except DatabaseError as e:
        return create_error_response(
            message=str(e),
            status_code=500
        )
    except Exception as e:
        return create_error_response(
            message=f'删除非交易日失败: {str(e)}',
            status_code=500
        )


@api_bp.route('/non-trading-days/bulk', methods=['POST'])
def bulk_add_non_trading_days():
    """批量添加非交易日"""
    try:
        data = request.get_json()
        
        if not data or not isinstance(data.get('holidays'), list):
            return create_error_response(
                message='请提供有效的节假日列表',
                status_code=400
            )
        
        holidays = NonTradingDayService.bulk_add_holidays(data['holidays'])
        
        return create_success_response(
            data=holidays,
            message=f'成功批量添加 {len(holidays)} 个非交易日',
            status_code=201
        )
        
    except Exception as e:
        return create_error_response(
            message=f'批量添加非交易日失败: {str(e)}',
            status_code=500
        )


@api_bp.route('/trading-days/check/<date_str>', methods=['GET'])
def check_trading_day(date_str):
    """检查指定日期是否为交易日"""
    try:
        is_trading = NonTradingDayService.is_trading_day(date_str)
        
        return create_success_response(
            data={
                'date': date_str,
                'is_trading_day': is_trading,
                'day_type': '交易日' if is_trading else '非交易日'
            },
            message=f'{date_str} 是{"交易日" if is_trading else "非交易日"}'
        )
        
    except Exception as e:
        return create_error_response(
            message=f'检查交易日失败: {str(e)}',
            status_code=500
        )


@api_bp.route('/trading-days/calculate', methods=['GET'])
def calculate_trading_days():
    """计算两个日期之间的交易日数量"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return create_error_response(
                message='请提供开始日期和结束日期',
                status_code=400
            )
        
        trading_days = NonTradingDayService.calculate_trading_days(start_date, end_date)
        
        return create_success_response(
            data={
                'start_date': start_date,
                'end_date': end_date,
                'trading_days': trading_days
            },
            message=f'从 {start_date} 到 {end_date} 共有 {trading_days} 个交易日'
        )
        
    except Exception as e:
        return create_error_response(
            message=f'计算交易日数量失败: {str(e)}',
            status_code=500
        )


@api_bp.route('/trading-days/holding-days', methods=['GET'])
def calculate_holding_days():
    """计算持仓天数"""
    try:
        buy_date = request.args.get('buy_date')
        sell_date = request.args.get('sell_date')  # 可选，默认为今天
        
        if not buy_date:
            return create_error_response(
                message='请提供买入日期',
                status_code=400
            )
        
        holding_days = NonTradingDayService.calculate_holding_days(buy_date, sell_date)
        
        result_data = {
            'buy_date': buy_date,
            'holding_days': holding_days
        }
        
        if sell_date:
            result_data['sell_date'] = sell_date
            message = f'从 {buy_date} 到 {sell_date} 持仓 {holding_days} 个交易日'
        else:
            result_data['sell_date'] = date.today().isoformat()
            message = f'从 {buy_date} 到今天持仓 {holding_days} 个交易日'
        
        return create_success_response(
            data=result_data,
            message=message
        )
        
    except Exception as e:
        return create_error_response(
            message=f'计算持仓天数失败: {str(e)}',
            status_code=500
        )


@api_bp.route('/trading-calendar/<int:year>', methods=['GET'])
def get_trading_calendar(year):
    """获取指定年份的交易日历"""
    try:
        calendar_data = NonTradingDayService.get_trading_calendar(year)
        
        return create_success_response(
            data=calendar_data,
            message=f'成功获取{year}年交易日历'
        )
        
    except Exception as e:
        return create_error_response(
            message=f'获取交易日历失败: {str(e)}',
            status_code=500
        )


@api_bp.route('/trading-days/next/<date_str>', methods=['GET'])
def get_next_trading_day(date_str):
    """获取指定日期之后的下一个交易日"""
    try:
        next_day = NonTradingDayService.get_next_trading_day(date_str)
        
        if next_day:
            return create_success_response(
                data={
                    'current_date': date_str,
                    'next_trading_day': next_day
                },
                message=f'{date_str} 之后的下一个交易日是 {next_day}'
            )
        else:
            return create_error_response(
                message=f'无法找到 {date_str} 之后的交易日',
                status_code=404
            )
        
    except Exception as e:
        return create_error_response(
            message=f'获取下一个交易日失败: {str(e)}',
            status_code=500
        )


@api_bp.route('/trading-days/previous/<date_str>', methods=['GET'])
def get_previous_trading_day(date_str):
    """获取指定日期之前的上一个交易日"""
    try:
        prev_day = NonTradingDayService.get_previous_trading_day(date_str)
        
        if prev_day:
            return create_success_response(
                data={
                    'current_date': date_str,
                    'previous_trading_day': prev_day
                },
                message=f'{date_str} 之前的上一个交易日是 {prev_day}'
            )
        else:
            return create_error_response(
                message=f'无法找到 {date_str} 之前的交易日',
                status_code=404
            )
        
    except Exception as e:
        return create_error_response(
            message=f'获取上一个交易日失败: {str(e)}',
            status_code=500
        )