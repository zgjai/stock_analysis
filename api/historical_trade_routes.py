"""
历史交易记录API路由
"""
from flask import request, jsonify, current_app
from datetime import datetime
from . import api_bp
from extensions import db
from services.historical_trade_service import HistoricalTradeService
from error_handlers import create_success_response, ValidationError, NotFoundError, DatabaseError


@api_bp.route('/historical-trades', methods=['GET'])
def get_historical_trades():
    """
    获取历史交易记录列表，支持分页和筛选
    
    Query Parameters:
    - page: 页码 (可选)
    - per_page: 每页数量 (可选，默认20)
    - stock_code: 股票代码筛选 (可选)
    - stock_name: 股票名称筛选 (可选)
    - start_date: 开始日期筛选 (可选，格式: YYYY-MM-DD)
    - end_date: 结束日期筛选 (可选，格式: YYYY-MM-DD)
    - min_return_rate: 最小收益率筛选 (可选)
    - max_return_rate: 最大收益率筛选 (可选)
    - min_holding_days: 最小持仓天数筛选 (可选)
    - max_holding_days: 最大持仓天数筛选 (可选)
    - is_profitable: 是否盈利筛选 (可选，true/false)
    - sort_by: 排序字段 (可选，默认completion_date)
    - sort_order: 排序方向 (可选，asc/desc，默认desc)
    
    Requirements: 1.1, 1.4
    """
    try:
        current_app.logger.info("=== 获取历史交易记录列表请求开始 ===")
        
        # 获取筛选参数
        filters = {}
        
        # 基本筛选参数
        if request.args.get('stock_code'):
            filters['stock_code'] = request.args.get('stock_code').strip()
            current_app.logger.info(f"股票代码筛选: {filters['stock_code']}")
        
        if request.args.get('stock_name'):
            filters['stock_name'] = request.args.get('stock_name').strip()
            current_app.logger.info(f"股票名称筛选: {filters['stock_name']}")
        
        # 日期范围筛选
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
            current_app.logger.info(f"开始日期筛选: {filters['start_date']}")
        
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
            current_app.logger.info(f"结束日期筛选: {filters['end_date']}")
        
        # 收益率范围筛选
        if request.args.get('min_return_rate') is not None:
            try:
                filters['min_return_rate'] = float(request.args.get('min_return_rate'))
                current_app.logger.info(f"最小收益率筛选: {filters['min_return_rate']}")
            except (ValueError, TypeError):
                raise ValidationError("最小收益率格式不正确", "min_return_rate")
        
        if request.args.get('max_return_rate') is not None:
            try:
                filters['max_return_rate'] = float(request.args.get('max_return_rate'))
                current_app.logger.info(f"最大收益率筛选: {filters['max_return_rate']}")
            except (ValueError, TypeError):
                raise ValidationError("最大收益率格式不正确", "max_return_rate")
        
        # 持仓天数范围筛选
        if request.args.get('min_holding_days') is not None:
            try:
                filters['min_holding_days'] = int(request.args.get('min_holding_days'))
                current_app.logger.info(f"最小持仓天数筛选: {filters['min_holding_days']}")
            except (ValueError, TypeError):
                raise ValidationError("最小持仓天数格式不正确", "min_holding_days")
        
        if request.args.get('max_holding_days') is not None:
            try:
                filters['max_holding_days'] = int(request.args.get('max_holding_days'))
                current_app.logger.info(f"最大持仓天数筛选: {filters['max_holding_days']}")
            except (ValueError, TypeError):
                raise ValidationError("最大持仓天数格式不正确", "max_holding_days")
        
        # 盈利状态筛选
        if request.args.get('is_profitable') is not None:
            profitable_str = request.args.get('is_profitable').lower()
            if profitable_str in ['true', '1', 'yes']:
                filters['is_profitable'] = True
            elif profitable_str in ['false', '0', 'no']:
                filters['is_profitable'] = False
            else:
                raise ValidationError("盈利状态参数格式不正确，应为true或false", "is_profitable")
            current_app.logger.info(f"盈利状态筛选: {filters['is_profitable']}")
        
        # 分页参数
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int, default=20)
        
        # 验证分页参数
        if page is not None and page < 1:
            raise ValidationError("页码必须大于0", "page")
        
        if per_page < 1 or per_page > 100:
            raise ValidationError("每页数量必须在1-100之间", "per_page")
        
        current_app.logger.info(f"分页参数: page={page}, per_page={per_page}")
        
        # 排序参数
        sort_by = request.args.get('sort_by', 'completion_date')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 验证排序参数
        valid_sort_fields = [
            'completion_date', 'buy_date', 'sell_date', 'stock_code', 
            'total_investment', 'total_return', 'return_rate', 'holding_days'
        ]
        if sort_by not in valid_sort_fields:
            raise ValidationError(f"排序字段无效，支持的字段: {', '.join(valid_sort_fields)}", "sort_by")
        
        if sort_order.lower() not in ['asc', 'desc']:
            raise ValidationError("排序方向必须是asc或desc", "sort_order")
        
        current_app.logger.info(f"排序参数: sort_by={sort_by}, sort_order={sort_order}")
        
        # 获取历史交易记录
        result = HistoricalTradeService.get_historical_trades(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        current_app.logger.info(f"获取到 {result.get('total', 0)} 条历史交易记录")
        current_app.logger.info("=== 获取历史交易记录列表请求完成 ===")
        
        return create_success_response(
            data=result,
            message='获取历史交易记录成功'
        )
    
    except ValidationError as e:
        current_app.logger.error(f"参数验证失败: {str(e)}")
        raise e
    except Exception as e:
        current_app.logger.error(f"获取历史交易记录失败: {str(e)}")
        raise DatabaseError(f"获取历史交易记录失败: {str(e)}")


@api_bp.route('/historical-trades/<int:trade_id>', methods=['GET'])
def get_historical_trade(trade_id):
    """
    获取单个历史交易记录详情
    
    Path Parameters:
    - trade_id: 历史交易记录ID
    
    Requirements: 1.1
    """
    try:
        current_app.logger.info(f"=== 获取历史交易记录详情请求开始，ID: {trade_id} ===")
        
        # 验证ID参数
        if trade_id <= 0:
            raise ValidationError("交易记录ID必须大于0", "trade_id")
        
        # 获取历史交易记录
        historical_trade = HistoricalTradeService.get_by_id(trade_id)
        
        if not historical_trade:
            raise NotFoundError(f"未找到ID为{trade_id}的历史交易记录")
        
        # 转换为字典格式，包含详细信息
        trade_data = historical_trade.to_dict()
        
        # 添加关联的交易记录信息
        from models.trade_record import TradeRecord
        
        # 获取买入记录详情
        buy_records_ids = historical_trade.buy_records_list
        if buy_records_ids:
            buy_records = TradeRecord.query.filter(TradeRecord.id.in_(buy_records_ids)).all()
            trade_data['buy_records'] = [record.to_dict() for record in buy_records]
        else:
            trade_data['buy_records'] = []
        
        # 获取卖出记录详情
        sell_records_ids = historical_trade.sell_records_list
        if sell_records_ids:
            sell_records = TradeRecord.query.filter(TradeRecord.id.in_(sell_records_ids)).all()
            trade_data['sell_records'] = [record.to_dict() for record in sell_records]
        else:
            trade_data['sell_records'] = []
        
        # 获取复盘记录（如果存在）
        from models.trade_review import TradeReview
        reviews = TradeReview.query.filter_by(historical_trade_id=trade_id).all()
        trade_data['reviews'] = [review.to_dict() for review in reviews]
        
        current_app.logger.info(f"成功获取历史交易记录详情，包含 {len(trade_data['buy_records'])} 条买入记录，{len(trade_data['sell_records'])} 条卖出记录，{len(trade_data['reviews'])} 条复盘记录")
        current_app.logger.info("=== 获取历史交易记录详情请求完成 ===")
        
        return create_success_response(
            data=trade_data,
            message='获取历史交易记录详情成功'
        )
    
    except (ValidationError, NotFoundError) as e:
        current_app.logger.error(f"获取历史交易记录详情失败: {str(e)}")
        raise e
    except Exception as e:
        current_app.logger.error(f"获取历史交易记录详情失败: {str(e)}")
        raise DatabaseError(f"获取历史交易记录详情失败: {str(e)}")


@api_bp.route('/historical-trades/sync', methods=['POST'])
def sync_historical_trades():
    """
    同步生成历史交易记录
    
    Request Body (JSON):
    - force_regenerate: 是否强制重新生成 (可选，默认false)
    
    Requirements: 3.4, 3.5
    """
    try:
        current_app.logger.info("=== 同步历史交易记录请求开始 ===")
        
        # 获取请求参数
        data = request.get_json(silent=True) or {}
        force_regenerate = data.get('force_regenerate', False)
        
        current_app.logger.info(f"强制重新生成: {force_regenerate}")
        
        # 验证参数类型
        if not isinstance(force_regenerate, bool):
            raise ValidationError("force_regenerate参数必须是布尔值", "force_regenerate")
        
        # 执行同步操作
        if force_regenerate:
            # 强制重新生成所有历史交易记录
            result = HistoricalTradeService.generate_historical_records(force_regenerate=True)
            operation_type = "重新生成"
        else:
            # 增量同步
            result = HistoricalTradeService.sync_historical_records()
            operation_type = "增量同步"
        
        current_app.logger.info(f"{operation_type}历史交易记录完成: {result}")
        current_app.logger.info("=== 同步历史交易记录请求完成 ===")
        
        return create_success_response(
            data=result,
            message=f'历史交易记录{operation_type}成功'
        )
    
    except ValidationError as e:
        current_app.logger.error(f"参数验证失败: {str(e)}")
        raise e
    except Exception as e:
        current_app.logger.error(f"同步历史交易记录失败: {str(e)}")
        raise DatabaseError(f"同步历史交易记录失败: {str(e)}")


@api_bp.route('/historical-trades/generate', methods=['POST'])
def generate_historical_trades():
    """
    生成历史交易记录（初始化）
    
    Request Body (JSON):
    - force_regenerate: 是否强制重新生成 (可选，默认false)
    
    Requirements: 3.4
    """
    try:
        current_app.logger.info("=== 生成历史交易记录请求开始 ===")
        
        # 获取请求参数
        data = request.get_json(silent=True) or {}
        force_regenerate = data.get('force_regenerate', False)
        
        current_app.logger.info(f"强制重新生成: {force_regenerate}")
        
        # 验证参数类型
        if not isinstance(force_regenerate, bool):
            raise ValidationError("force_regenerate参数必须是布尔值", "force_regenerate")
        
        # 执行生成操作
        result = HistoricalTradeService.generate_historical_records(force_regenerate=force_regenerate)
        
        current_app.logger.info(f"生成历史交易记录完成: {result}")
        current_app.logger.info("=== 生成历史交易记录请求完成 ===")
        
        return create_success_response(
            data=result,
            message='历史交易记录生成成功'
        ), 201
    
    except ValidationError as e:
        current_app.logger.error(f"参数验证失败: {str(e)}")
        raise e
    except Exception as e:
        current_app.logger.error(f"生成历史交易记录失败: {str(e)}")
        raise DatabaseError(f"生成历史交易记录失败: {str(e)}")


@api_bp.route('/historical-trades/statistics', methods=['GET'])
def get_historical_trade_statistics():
    """
    获取历史交易统计信息
    
    Requirements: 1.4
    """
    try:
        current_app.logger.info("=== 获取历史交易统计信息请求开始 ===")
        
        # 获取统计信息
        statistics = HistoricalTradeService.get_trade_statistics()
        
        current_app.logger.info(f"获取统计信息完成: {statistics}")
        current_app.logger.info("=== 获取历史交易统计信息请求完成 ===")
        
        return create_success_response(
            data=statistics,
            message='获取历史交易统计信息成功'
        )
    
    except Exception as e:
        current_app.logger.error(f"获取历史交易统计信息失败: {str(e)}")
        raise DatabaseError(f"获取历史交易统计信息失败: {str(e)}")


@api_bp.route('/historical-trades/identify', methods=['POST'])
def identify_completed_trades():
    """
    识别已完成的交易（不保存到数据库）
    
    Requirements: 1.2, 1.3
    """
    try:
        current_app.logger.info("=== 识别已完成交易请求开始 ===")
        
        # 识别已完成的交易
        completed_trades = HistoricalTradeService.identify_completed_trades()
        
        current_app.logger.info(f"识别到 {len(completed_trades)} 个已完成的交易")
        current_app.logger.info("=== 识别已完成交易请求完成 ===")
        
        return create_success_response(
            data={
                'completed_trades': completed_trades,
                'total_count': len(completed_trades)
            },
            message='识别已完成交易成功'
        )
    
    except Exception as e:
        current_app.logger.error(f"识别已完成交易失败: {str(e)}")
        raise DatabaseError(f"识别已完成交易失败: {str(e)}")


@api_bp.route('/historical-trades/calculate-metrics', methods=['POST'])
def calculate_trade_metrics():
    """
    计算交易指标
    
    Request Body (JSON):
    - buy_records_ids: 买入记录ID列表
    - sell_records_ids: 卖出记录ID列表
    
    Requirements: 1.3
    """
    try:
        current_app.logger.info("=== 计算交易指标请求开始 ===")
        
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        buy_records_ids = data.get('buy_records_ids', [])
        sell_records_ids = data.get('sell_records_ids', [])
        
        # 验证参数
        if not buy_records_ids:
            raise ValidationError("买入记录ID列表不能为空", "buy_records_ids")
        
        if not sell_records_ids:
            raise ValidationError("卖出记录ID列表不能为空", "sell_records_ids")
        
        # 验证ID列表格式
        if not isinstance(buy_records_ids, list) or not all(isinstance(id, int) for id in buy_records_ids):
            raise ValidationError("买入记录ID列表格式不正确", "buy_records_ids")
        
        if not isinstance(sell_records_ids, list) or not all(isinstance(id, int) for id in sell_records_ids):
            raise ValidationError("卖出记录ID列表格式不正确", "sell_records_ids")
        
        current_app.logger.info(f"买入记录IDs: {buy_records_ids}")
        current_app.logger.info(f"卖出记录IDs: {sell_records_ids}")
        
        # 获取交易记录
        from models.trade_record import TradeRecord
        
        buy_records = TradeRecord.query.filter(TradeRecord.id.in_(buy_records_ids)).all()
        sell_records = TradeRecord.query.filter(TradeRecord.id.in_(sell_records_ids)).all()
        
        # 验证记录是否存在
        if len(buy_records) != len(buy_records_ids):
            missing_ids = set(buy_records_ids) - set(record.id for record in buy_records)
            raise NotFoundError(f"未找到买入记录ID: {list(missing_ids)}")
        
        if len(sell_records) != len(sell_records_ids):
            missing_ids = set(sell_records_ids) - set(record.id for record in sell_records)
            raise NotFoundError(f"未找到卖出记录ID: {list(missing_ids)}")
        
        # 计算交易指标
        metrics = HistoricalTradeService.calculate_trade_metrics(buy_records, sell_records)
        
        current_app.logger.info(f"计算交易指标完成: {metrics}")
        current_app.logger.info("=== 计算交易指标请求完成 ===")
        
        return create_success_response(
            data=metrics,
            message='计算交易指标成功'
        )
    
    except (ValidationError, NotFoundError) as e:
        current_app.logger.error(f"计算交易指标失败: {str(e)}")
        raise e
    except Exception as e:
        current_app.logger.error(f"计算交易指标失败: {str(e)}")
        raise DatabaseError(f"计算交易指标失败: {str(e)}")


@api_bp.route('/historical-trades/validate', methods=['POST'])
def validate_historical_trade_data():
    """
    验证历史交易数据（不保存到数据库）
    
    Request Body (JSON): 历史交易数据
    
    Requirements: 5.3
    """
    try:
        current_app.logger.info("=== 验证历史交易数据请求开始 ===")
        
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        current_app.logger.info(f"验证数据: {data}")
        
        # 验证必填字段
        required_fields = [
            'stock_code', 'stock_name', 'buy_date', 'sell_date',
            'total_investment', 'total_return', 'return_rate'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"缺少必填字段: {field}", field)
        
        # 创建临时对象进行验证（不保存到数据库）
        from models.historical_trade import HistoricalTrade
        
        # 处理日期字段
        for date_field in ['buy_date', 'sell_date', 'completion_date']:
            if date_field in data and isinstance(data[date_field], str):
                try:
                    data[date_field] = datetime.fromisoformat(data[date_field].replace('Z', '+00:00'))
                except ValueError:
                    raise ValidationError(f"{date_field}日期格式不正确", date_field)
        
        # 验证数据（通过模型的验证逻辑）
        temp_trade = HistoricalTrade(**data)
        
        # 如果验证通过，返回处理后的数据
        validated_data = temp_trade.to_dict()
        
        current_app.logger.info("历史交易数据验证通过")
        current_app.logger.info("=== 验证历史交易数据请求完成 ===")
        
        return create_success_response(
            data={
                'is_valid': True,
                'validated_data': validated_data
            },
            message='历史交易数据验证通过'
        )
    
    except ValidationError as e:
        current_app.logger.error(f"数据验证失败: {str(e)}")
        return create_success_response(
            data={
                'is_valid': False,
                'validation_errors': {e.field if hasattr(e, 'field') else 'general': e.message}
            },
            message='历史交易数据验证失败'
        )
    except Exception as e:
        current_app.logger.error(f"验证历史交易数据失败: {str(e)}")
        raise DatabaseError(f"验证历史交易数据失败: {str(e)}")