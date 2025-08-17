"""
统计分析API路由
"""
from flask import request, jsonify, send_file
from datetime import datetime
from . import api_bp
from services.analytics_service import AnalyticsService
from error_handlers import create_success_response, create_error_response, ValidationError, DatabaseError
import io


@api_bp.route('/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """获取总体统计概览
    
    Requirements: 5.1, 5.2
    - 显示总体收益概览
    - 显示已清仓收益、持仓浮盈浮亏、总收益率
    """
    try:
        overview = AnalyticsService.get_overall_statistics()
        return create_success_response(
            data=overview,
            message='获取总体统计成功'
        )
    except DatabaseError as e:
        return create_error_response('DATABASE_ERROR', str(e), 500)
    except Exception as e:
        return create_error_response('INTERNAL_ERROR', f'获取总体统计失败: {str(e)}', 500)


@api_bp.route('/analytics/profit-distribution', methods=['GET'])
def get_profit_distribution():
    """获取收益分布区间分析
    
    Requirements: 5.3
    - 按盈亏区间显示股票分布情况
    """
    try:
        distribution = AnalyticsService.get_profit_distribution()
        return create_success_response(
            data=distribution,
            message='获取收益分布成功'
        )
    except DatabaseError as e:
        return create_error_response('DATABASE_ERROR', str(e), 500)
    except Exception as e:
        return create_error_response('INTERNAL_ERROR', f'获取收益分布失败: {str(e)}', 500)


@api_bp.route('/analytics/monthly', methods=['GET'])
def get_monthly_statistics():
    """获取月度交易统计和成功率
    
    Requirements: 5.4
    - 显示每月交易次数、收益情况和成功率
    
    Query Parameters:
    - year: 年份，默认为当前年份
    """
    try:
        year = request.args.get('year', type=int)
        if year is None:
            year = datetime.now().year
        
        # 验证年份范围
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 1:
            raise ValidationError(f"年份必须在2000到{current_year + 1}之间")
        
        monthly_stats = AnalyticsService.get_monthly_statistics(year)
        return create_success_response(
            data=monthly_stats,
            message=f'获取{year}年月度统计成功'
        )
    except ValidationError as e:
        return create_error_response('VALIDATION_ERROR', str(e), 400)
    except DatabaseError as e:
        return create_error_response('DATABASE_ERROR', str(e), 500)
    except Exception as e:
        return create_error_response('INTERNAL_ERROR', f'获取月度统计失败: {str(e)}', 500)


@api_bp.route('/analytics/export', methods=['GET'])
def export_statistics():
    """导出统计数据到Excel格式
    
    Requirements: 5.5
    - 支持导出Excel格式的统计报表
    
    Query Parameters:
    - format: 导出格式，目前支持 'excel'
    """
    try:
        export_format = request.args.get('format', 'excel').lower()
        
        if export_format != 'excel':
            return create_error_response('VALIDATION_ERROR', "目前只支持Excel格式导出", 400)
        
        # 生成Excel文件
        excel_data = AnalyticsService.export_statistics_to_excel()
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'股票交易统计报表_{timestamp}.xlsx'
        
        # 创建文件对象
        excel_file = io.BytesIO(excel_data)
        excel_file.seek(0)
        
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except ValidationError as e:
        return create_error_response('VALIDATION_ERROR', str(e), 400)
    except DatabaseError as e:
        return create_error_response('DATABASE_ERROR', str(e), 500)
    except Exception as e:
        return create_error_response('INTERNAL_ERROR', f'导出统计数据失败: {str(e)}', 500)


@api_bp.route('/analytics/holdings', methods=['GET'])
def get_analytics_holdings():
    """获取当前持仓详情
    
    补充功能：提供当前持仓的详细信息
    """
    try:
        from models.trade_record import TradeRecord
        
        # 获取所有未订正的交易记录
        trades = TradeRecord.query.filter_by(is_corrected=False).all()
        
        # 计算持仓情况
        holdings = AnalyticsService._calculate_current_holdings(trades)
        
        # 转换为列表格式
        holdings_list = []
        for stock_code, holding in holdings.items():
            holding_info = holding.copy()
            holding_info['stock_code'] = stock_code
            holdings_list.append(holding_info)
        
        # 按收益率排序
        holdings_list.sort(key=lambda x: x['profit_rate'], reverse=True)
        
        return create_success_response(
            data={
                'holdings': holdings_list,
                'total_count': len(holdings_list),
                'total_market_value': sum(h['market_value'] for h in holdings_list),
                'total_cost': sum(h['total_cost'] for h in holdings_list),
                'total_profit': sum(h['profit_amount'] for h in holdings_list)
            },
            message='获取当前持仓成功'
        )
    except DatabaseError as e:
        return create_error_response('DATABASE_ERROR', str(e), 500)
    except Exception as e:
        return create_error_response('INTERNAL_ERROR', f'获取当前持仓失败: {str(e)}', 500)


@api_bp.route('/analytics/performance', methods=['GET'])
def get_performance_metrics():
    """获取投资表现指标
    
    补充功能：提供更详细的投资表现分析
    """
    try:
        from models.trade_record import TradeRecord
        from datetime import timedelta
        
        # 获取所有未订正的交易记录
        trades = TradeRecord.query.filter_by(is_corrected=False).all()
        
        if not trades:
            return create_success_response(
                data={
                    'total_trades': 0,
                    'trading_days': 0,
                    'avg_trades_per_day': 0,
                    'most_traded_stock': None,
                    'best_performing_stock': None,
                    'worst_performing_stock': None
                },
                message='暂无交易数据'
            )
        
        # 计算交易天数
        trade_dates = set(trade.trade_date.date() for trade in trades)
        trading_days = len(trade_dates)
        
        # 计算平均每日交易次数
        avg_trades_per_day = len(trades) / trading_days if trading_days > 0 else 0
        
        # 统计最常交易的股票
        stock_trade_counts = {}
        for trade in trades:
            stock_trade_counts[trade.stock_code] = stock_trade_counts.get(trade.stock_code, 0) + 1
        
        most_traded_stock = max(stock_trade_counts.items(), key=lambda x: x[1]) if stock_trade_counts else None
        
        # 计算已清仓股票的表现
        closed_positions = AnalyticsService._calculate_closed_positions_detail(trades)
        
        best_performing = None
        worst_performing = None
        
        if closed_positions:
            best_performing = max(closed_positions, key=lambda x: x['profit_rate'])
            worst_performing = min(closed_positions, key=lambda x: x['profit_rate'])
        
        return create_success_response(
            data={
                'total_trades': len(trades),
                'trading_days': trading_days,
                'avg_trades_per_day': round(avg_trades_per_day, 2),
                'most_traded_stock': {
                    'stock_code': most_traded_stock[0],
                    'trade_count': most_traded_stock[1]
                } if most_traded_stock else None,
                'best_performing_stock': {
                    'stock_code': best_performing['stock_code'],
                    'stock_name': best_performing['stock_name'],
                    'profit_rate': round(best_performing['profit_rate'] * 100, 2),
                    'profit_amount': round(best_performing['profit_amount'], 2)
                } if best_performing else None,
                'worst_performing_stock': {
                    'stock_code': worst_performing['stock_code'],
                    'stock_name': worst_performing['stock_name'],
                    'profit_rate': round(worst_performing['profit_rate'] * 100, 2),
                    'profit_amount': round(worst_performing['profit_amount'], 2)
                } if worst_performing else None,
                'closed_positions_count': len(closed_positions)
            },
            message='获取投资表现指标成功'
        )
    except DatabaseError as e:
        return create_error_response('DATABASE_ERROR', str(e), 500)
    except Exception as e:
        return create_error_response('INTERNAL_ERROR', f'获取投资表现指标失败: {str(e)}', 500)