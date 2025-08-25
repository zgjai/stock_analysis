"""
交易记录管理API路由
"""
from flask import request, jsonify, current_app
from datetime import datetime
from . import api_bp
from extensions import db
from services.trading_service import TradingService, TradingConfigService
from services.profit_taking_service import ProfitTakingService
from utils.batch_profit_compatibility import BatchProfitCompatibilityHandler
from error_handlers import create_success_response, ValidationError, NotFoundError


@api_bp.route('/trades', methods=['GET'])
def get_trades():
    """获取交易记录列表"""
    try:
        # 获取查询参数
        filters = {}
        
        # 基本筛选参数
        if request.args.get('stock_code'):
            filters['stock_code'] = request.args.get('stock_code')
        
        if request.args.get('stock_name'):
            filters['stock_name'] = request.args.get('stock_name')
        
        if request.args.get('trade_type'):
            filters['trade_type'] = request.args.get('trade_type')
        
        if request.args.get('reason'):
            filters['reason'] = request.args.get('reason')
        
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        
        if request.args.get('min_price'):
            filters['min_price'] = request.args.get('min_price')
        
        if request.args.get('max_price'):
            filters['max_price'] = request.args.get('max_price')
        
        if request.args.get('is_corrected') is not None:
            filters['is_corrected'] = request.args.get('is_corrected').lower() == 'true'
        
        # 分页参数
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int, default=20)
        
        # 排序参数
        sort_by = request.args.get('sort_by', 'trade_date')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 获取交易记录
        result = TradingService.get_trades(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return create_success_response(
            data=result,
            message='获取交易记录成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades', methods=['POST'])
def create_trade():
    """创建交易记录"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        # 必填字段验证 - 更宽松的验证逻辑
        required_fields = ['stock_code', 'stock_name', 'trade_type', 'price', 'quantity', 'reason']
        for field in required_fields:
            # 检查字段是否存在
            if field not in data:
                raise ValidationError(f"缺少必填字段: {field}")
            
            # 获取字段值
            value = data[field]
            
            # 处理None值
            if value is None:
                raise ValidationError(f"{field}不能为空")
            
            # 处理字符串值
            if isinstance(value, str):
                value = value.strip()
                if value == '':
                    raise ValidationError(f"{field}不能为空")
                # 更新处理后的值
                data[field] = value
            
            # 处理数值字段
            elif field in ['price', 'quantity']:
                try:
                    if field == 'price':
                        data[field] = float(value)
                    elif field == 'quantity':
                        data[field] = int(value)
                except (ValueError, TypeError):
                    raise ValidationError(f"{field}格式不正确")
        
        # 设置交易日期（如果未提供）
        if 'trade_date' not in data or not data['trade_date']:
            data['trade_date'] = datetime.now()
        elif isinstance(data['trade_date'], str):
            try:
                data['trade_date'] = datetime.fromisoformat(data['trade_date'].replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("交易日期格式不正确")
        
        # 创建交易记录
        trade = TradingService.create_trade(data)
        
        # 如果使用分批止盈，返回包含止盈目标的详细信息
        if trade.use_batch_profit_taking:
            trade_data = TradingService.get_trade_with_profit_targets(trade.id)
        else:
            trade_data = trade.to_dict()
        
        return create_success_response(
            data=trade_data,
            message='交易记录创建成功'
        ), 201
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>', methods=['GET'])
def get_trade(trade_id):
    """获取单个交易记录详情"""
    try:
        # 获取交易记录及其止盈目标详情
        trade_data = TradingService.get_trade_with_profit_targets(trade_id)
        
        return create_success_response(
            data=trade_data,
            message='获取交易记录成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>', methods=['PUT'])
def update_trade(trade_id):
    """更新交易记录"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        # 改进的字段验证逻辑
        def validate_numeric_field(field_name, field_type='float'):
            """验证数值字段"""
            if field_name not in data:
                return  # 字段不存在，跳过验证（更新时允许部分字段）
            
            value = data[field_name]
            
            # 处理None值
            if value is None:
                raise ValidationError(f"{field_name}不能为空")
            
            # 处理空字符串
            if isinstance(value, str):
                value = value.strip()
                if value == '':
                    raise ValidationError(f"{field_name}不能为空")
                
                # 尝试转换为数字
                try:
                    if field_type == 'int':
                        value = int(value)
                    else:
                        value = float(value)
                    data[field_name] = value  # 更新原数据
                except (ValueError, TypeError):
                    raise ValidationError(f"{field_name}格式无效，必须是数字")
            
            # 验证数值范围
            if isinstance(value, (int, float)):
                if value <= 0:
                    raise ValidationError(f"{field_name}必须大于0")
                
                # 数量字段的特殊验证
                if field_name == 'quantity' and int(value) % 100 != 0:
                    raise ValidationError("数量必须是100的倍数")
        
        # 验证价格和数量字段
        validate_numeric_field('price', 'float')
        validate_numeric_field('quantity', 'int')
        
        # 处理交易日期
        if 'trade_date' in data and data['trade_date'] is not None:
            if isinstance(data['trade_date'], str):
                try:
                    # 处理多种日期格式
                    trade_date_str = data['trade_date'].strip()
                    if trade_date_str:
                        # 处理datetime-local格式 (YYYY-MM-DDTHH:MM)
                        if 'T' in trade_date_str and len(trade_date_str) == 16:
                            data['trade_date'] = datetime.fromisoformat(trade_date_str)
                        # 处理ISO格式
                        elif 'T' in trade_date_str:
                            data['trade_date'] = datetime.fromisoformat(trade_date_str.replace('Z', '+00:00'))
                        else:
                            # 尝试其他格式
                            data['trade_date'] = datetime.fromisoformat(trade_date_str)
                    else:
                        raise ValidationError("交易日期不能为空")
                except ValueError:
                    raise ValidationError(f"交易日期格式不正确: {data['trade_date']}")
        
        # 更新交易记录（支持分批止盈）
        trade = TradingService.update_trade(trade_id, data)
        
        # 如果使用分批止盈，返回包含止盈目标的详细信息
        if trade.use_batch_profit_taking:
            trade_data = TradingService.get_trade_with_profit_targets(trade.id)
        else:
            trade_data = trade.to_dict()
        
        return create_success_response(
            data=trade_data,
            message='交易记录更新成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    """删除交易记录"""
    try:
        TradingService.delete_trade(trade_id)
        
        return create_success_response(
            message='交易记录删除成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/calculate-risk-reward', methods=['POST'])
def calculate_risk_reward():
    """计算止损止盈预期"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        buy_price = data.get('buy_price')
        if not buy_price:
            raise ValidationError("买入价格不能为空")
        
        stop_loss_price = data.get('stop_loss_price')
        take_profit_ratio = data.get('take_profit_ratio')
        sell_ratio = data.get('sell_ratio')
        profit_targets = data.get('profit_targets')
        
        result = TradingService.calculate_risk_reward(
            buy_price=float(buy_price),
            stop_loss_price=float(stop_loss_price) if stop_loss_price else None,
            take_profit_ratio=float(take_profit_ratio) if take_profit_ratio else None,
            sell_ratio=float(sell_ratio) if sell_ratio else None,
            profit_targets=profit_targets
        )
        
        return create_success_response(
            data=result,
            message='计算止损止盈预期成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>/correct', methods=['POST'])
def correct_trade(trade_id):
    """订正交易记录"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        reason = data.get('reason')
        if not reason:
            raise ValidationError("订正原因不能为空")
        
        corrected_data = data.get('corrected_data', {})
        if not corrected_data:
            raise ValidationError("订正数据不能为空")
        
        # 处理交易日期
        if 'trade_date' in corrected_data and isinstance(corrected_data['trade_date'], str):
            try:
                corrected_data['trade_date'] = datetime.fromisoformat(corrected_data['trade_date'].replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("交易日期格式不正确")
        
        # 订正交易记录
        corrected_trade = TradingService.correct_trade_record(
            original_trade_id=trade_id,
            corrected_data=corrected_data,
            reason=reason
        )
        
        return create_success_response(
            data=corrected_trade.to_dict(),
            message='交易记录订正成功'
        ), 201
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>/history', methods=['GET'])
def get_correction_history(trade_id):
    """获取交易记录订正历史"""
    try:
        history = TradingService.get_correction_history(trade_id)
        
        return create_success_response(
            data=history,
            message='获取订正历史成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/config', methods=['GET'])
def get_trade_config():
    """获取交易配置"""
    try:
        config = TradingConfigService.get_all_config()
        
        return create_success_response(
            data=config,
            message='获取交易配置成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/config/buy-reasons', methods=['GET'])
def get_buy_reasons():
    """获取买入原因选项"""
    try:
        reasons = TradingConfigService.get_buy_reasons()
        
        return create_success_response(
            data={'buy_reasons': reasons},
            message='获取买入原因成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/config/buy-reasons', methods=['PUT'])
def set_buy_reasons():
    """设置买入原因选项"""
    try:
        data = request.get_json()
        
        if not data or 'buy_reasons' not in data:
            raise ValidationError("买入原因列表不能为空")
        
        reasons = data['buy_reasons']
        TradingConfigService.set_buy_reasons(reasons)
        
        return create_success_response(
            data={'buy_reasons': reasons},
            message='设置买入原因成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/config/sell-reasons', methods=['GET'])
def get_sell_reasons():
    """获取卖出原因选项"""
    try:
        reasons = TradingConfigService.get_sell_reasons()
        
        return create_success_response(
            data={'sell_reasons': reasons},
            message='获取卖出原因成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/config/sell-reasons', methods=['PUT'])
def set_sell_reasons():
    """设置卖出原因选项"""
    try:
        data = request.get_json()
        
        if not data or 'sell_reasons' not in data:
            raise ValidationError("卖出原因列表不能为空")
        
        reasons = data['sell_reasons']
        TradingConfigService.set_sell_reasons(reasons)
        
        return create_success_response(
            data={'sell_reasons': reasons},
            message='设置卖出原因成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>/profit-targets', methods=['GET'])
def get_profit_targets(trade_id):
    """获取交易记录的止盈目标"""
    try:
        # 获取止盈目标汇总信息
        summary = ProfitTakingService.get_targets_summary(trade_id)
        
        return create_success_response(
            data=summary,
            message='获取止盈目标成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>/profit-targets', methods=['PUT'])
def set_profit_targets(trade_id):
    """设置/更新交易记录的止盈目标"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空", "request_body")
        
        profit_targets = data.get('profit_targets', [])
        
        if not profit_targets:
            raise ValidationError("止盈目标列表不能为空", "profit_targets")
        
        # 验证止盈目标数据格式
        for i, target in enumerate(profit_targets):
            if not isinstance(target, dict):
                raise ValidationError(f"第{i+1}个止盈目标数据格式无效", f"profit_targets[{i}]")
        
        # 更新止盈目标
        updated_targets = TradingService.update_trade_profit_targets(trade_id, profit_targets)
        
        # 获取更新后的汇总信息
        summary = ProfitTakingService.get_targets_summary(trade_id)
        
        return create_success_response(
            data=summary,
            message='设置止盈目标成功'
        )
    
    except ValidationError as e:
        # 如果是详细的验证错误，保持原有的错误结构
        raise e
    except Exception as e:
        raise e


@api_bp.route('/trades/validate-profit-targets', methods=['POST'])
def validate_profit_targets():
    """验证止盈目标数据（不保存）"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空", "request_body")
        
        buy_price = data.get('buy_price')
        if not buy_price:
            raise ValidationError("买入价格不能为空", "buy_price")
        
        # 验证买入价格格式
        try:
            buy_price_float = float(buy_price)
            if buy_price_float <= 0:
                raise ValidationError("买入价格必须大于0", "buy_price")
        except (ValueError, TypeError):
            raise ValidationError("买入价格格式无效", "buy_price")
        
        profit_targets = data.get('profit_targets', [])
        if not profit_targets:
            raise ValidationError("止盈目标列表不能为空", "profit_targets")
        
        # 验证止盈目标数据格式
        for i, target in enumerate(profit_targets):
            if not isinstance(target, dict):
                raise ValidationError(f"第{i+1}个止盈目标数据格式无效", f"profit_targets[{i}]")
        
        # 执行完整验证
        ProfitTakingService.validate_targets_total_ratio(profit_targets)
        ProfitTakingService.validate_targets_against_buy_price(buy_price_float, profit_targets)
        
        # 计算预期收益信息
        result = ProfitTakingService.calculate_targets_expected_profit(
            buy_price=buy_price_float,
            targets=profit_targets
        )
        
        return create_success_response(
            data={
                'is_valid': True,
                'validation_result': result
            },
            message='止盈目标验证通过'
        )
    
    except ValidationError as e:
        # 返回验证失败的详细信息
        return create_success_response(
            data={
                'is_valid': False,
                'validation_errors': e.details if hasattr(e, 'details') else {'general': e.message}
            },
            message='止盈目标验证失败'
        )
    except Exception as e:
        raise e


@api_bp.route('/trades/calculate-batch-profit', methods=['POST'])
def calculate_batch_profit():
    """计算分批止盈预期收益"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空", "request_body")
        
        buy_price = data.get('buy_price')
        if not buy_price:
            raise ValidationError("买入价格不能为空", "buy_price")
        
        # 验证买入价格格式
        try:
            buy_price_float = float(buy_price)
            if buy_price_float <= 0:
                raise ValidationError("买入价格必须大于0", "buy_price")
        except (ValueError, TypeError):
            raise ValidationError("买入价格格式无效", "buy_price")
        
        profit_targets = data.get('profit_targets', [])
        if not profit_targets:
            raise ValidationError("止盈目标列表不能为空", "profit_targets")
        
        # 验证止盈目标数据格式
        for i, target in enumerate(profit_targets):
            if not isinstance(target, dict):
                raise ValidationError(f"第{i+1}个止盈目标数据格式无效", f"profit_targets[{i}]")
        
        # 先进行基本验证
        ProfitTakingService.validate_targets_total_ratio(profit_targets)
        ProfitTakingService.validate_targets_against_buy_price(buy_price_float, profit_targets)
        
        # 计算分批止盈预期收益
        result = ProfitTakingService.calculate_targets_expected_profit(
            buy_price=buy_price_float,
            targets=profit_targets
        )
        
        return create_success_response(
            data=result,
            message='计算分批止盈预期收益成功'
        )
    
    except ValidationError as e:
        # 如果是详细的验证错误，保持原有的错误结构
        raise e
    except Exception as e:
        raise e


@api_bp.route('/trades/stats', methods=['GET'])
def get_trade_stats():
    """获取交易统计信息"""
    try:
        # 获取基本统计信息
        from models.trade_record import TradeRecord
        from sqlalchemy import func
        
        # 总交易记录数
        total_trades = TradeRecord.query.count()
        
        # 买入和卖出记录数
        buy_count = TradeRecord.query.filter_by(trade_type='buy').count()
        sell_count = TradeRecord.query.filter_by(trade_type='sell').count()
        
        # 被订正的记录数
        corrected_count = TradeRecord.query.filter_by(is_corrected=True).count()
        
        # 按股票代码分组统计
        from sqlalchemy import case
        stock_stats = db.session.query(
            TradeRecord.stock_code,
            TradeRecord.stock_name,
            func.count(TradeRecord.id).label('trade_count'),
            func.sum(case((TradeRecord.trade_type == 'buy', 1), else_=0)).label('buy_count'),
            func.sum(case((TradeRecord.trade_type == 'sell', 1), else_=0)).label('sell_count')
        ).group_by(TradeRecord.stock_code, TradeRecord.stock_name).all()
        
        stock_stats_list = []
        for stat in stock_stats:
            stock_stats_list.append({
                'stock_code': stat.stock_code,
                'stock_name': stat.stock_name,
                'trade_count': stat.trade_count,
                'buy_count': stat.buy_count,
                'sell_count': stat.sell_count
            })
        
        stats = {
            'total_trades': total_trades,
            'buy_count': buy_count,
            'sell_count': sell_count,
            'corrected_count': corrected_count,
            'stock_stats': stock_stats_list
        }
        
        return create_success_response(
            data=stats,
            message='获取交易统计成功'
        )
    
    except Exception as e:
        raise e

@api_bp.route('/trades/compatibility-status', methods=['GET'])
def get_compatibility_status():
    """获取分批止盈功能兼容性状态"""
    try:
        status = BatchProfitCompatibilityHandler.get_compatibility_status()
        
        return create_success_response(
            data=status,
            message='获取兼容性状态成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/ensure-compatibility', methods=['POST'])
def ensure_compatibility():
    """确保数据兼容性"""
    try:
        result = BatchProfitCompatibilityHandler.ensure_compatibility()
        
        return create_success_response(
            data=result,
            message='兼容性处理完成'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/current-holdings', methods=['GET'])
def get_current_holdings_for_trading():
    """获取当前持仓列表，用于卖出操作的股票选择
    
    Requirements: 3.2
    - 为卖出操作提供股票选择
    """
    try:
        from services.analytics_service import AnalyticsService
        from models.trade_record import TradeRecord
        
        # 获取所有未订正的交易记录
        trades = TradeRecord.query.filter_by(is_corrected=False).all()
        
        # 计算当前持仓
        holdings = AnalyticsService._calculate_current_holdings(trades)
        
        # 转换为适合前端使用的格式
        holdings_list = []
        for stock_code, holding in holdings.items():
            holdings_list.append({
                'stock_code': stock_code,
                'stock_name': holding['stock_name'],
                'quantity': holding['quantity'],
                'avg_cost': round(holding['avg_cost'], 2),
                'current_price': round(holding['current_price'], 2),
                'market_value': round(holding['market_value'], 2),
                'profit_amount': round(holding['profit_amount'], 2),
                'profit_rate': round(holding['profit_rate'] * 100, 2)
            })
        
        # 按股票代码排序
        holdings_list.sort(key=lambda x: x['stock_code'])
        
        return create_success_response(
            data={
                'holdings': holdings_list,
                'total_count': len(holdings_list)
            },
            message='获取当前持仓成功'
        )
    
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>/migrate-to-batch', methods=['POST'])
def migrate_to_batch_profit(trade_id):
    """将单一止盈迁移为分批止盈"""
    try:
        result = BatchProfitCompatibilityHandler.migrate_single_to_batch_profit(trade_id)
        
        if result['success']:
            return create_success_response(
                data=result,
                message=result['message']
            )
        else:
            raise ValidationError(result['message'], 'migration')
    
    except ValidationError as e:
        raise e
    except Exception as e:
        raise e


@api_bp.route('/trades/<int:trade_id>/migrate-to-single', methods=['POST'])
def migrate_to_single_profit(trade_id):
    """将分批止盈迁移为单一止盈"""
    try:
        result = BatchProfitCompatibilityHandler.migrate_batch_to_single_profit(trade_id)
        
        if result['success']:
            return create_success_response(
                data=result,
                message=result['message']
            )
        else:
            raise ValidationError(result['message'], 'migration')
    
    except ValidationError as e:
        raise e
    except Exception as e:
        raise e