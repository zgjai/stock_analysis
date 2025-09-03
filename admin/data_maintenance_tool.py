"""
数据维护管理工具
提供Web界面用于数据同步和维护操作
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from datetime import datetime, timedelta
import json
from services.data_sync_service import DataSyncService
from services.historical_trade_service import HistoricalTradeService
from error_handlers import ValidationError, DatabaseError


# 创建蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/data-maintenance')
def data_maintenance():
    """数据维护主页面"""
    try:
        # 获取同步状态
        sync_status = DataSyncService.get_sync_status()
        
        # 获取基本统计
        trade_stats = HistoricalTradeService.get_trade_statistics()
        
        # 获取完整性检查状态（简化版）
        integrity_summary = _get_integrity_summary()
        
        return render_template('admin/data_maintenance.html',
                             sync_status=sync_status,
                             trade_stats=trade_stats,
                             integrity_summary=integrity_summary)
    except Exception as e:
        flash(f'获取数据维护信息失败: {str(e)}', 'error')
        return render_template('admin/data_maintenance.html',
                             sync_status=None,
                             trade_stats=None,
                             integrity_summary=None)


@admin_bp.route('/api/sync/initialize', methods=['POST'])
def api_initialize_data():
    """API: 初始化历史数据"""
    try:
        data = request.get_json() or {}
        force_regenerate = data.get('force_regenerate', False)
        
        result = DataSyncService.initialize_historical_data(force_regenerate=force_regenerate)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '数据初始化完成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '数据初始化失败'
        }), 500


@admin_bp.route('/api/sync/incremental', methods=['POST'])
def api_incremental_sync():
    """API: 增量同步"""
    try:
        result = DataSyncService.incremental_sync()
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '增量同步完成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '增量同步失败'
        }), 500


@admin_bp.route('/api/integrity/check', methods=['POST'])
def api_check_integrity():
    """API: 检查数据完整性"""
    try:
        result = DataSyncService.check_data_integrity()
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '完整性检查完成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '完整性检查失败'
        }), 500


@admin_bp.route('/api/integrity/repair', methods=['POST'])
def api_repair_integrity():
    """API: 修复数据完整性"""
    try:
        data = request.get_json() or {}
        repair_options = {
            'remove_duplicates': data.get('remove_duplicates', False),
            'fix_inconsistencies': data.get('fix_inconsistencies', False),
            'update_references': data.get('update_references', False)
        }
        
        result = DataSyncService.repair_data_integrity(repair_options)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '数据修复完成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '数据修复失败'
        }), 500


@admin_bp.route('/api/sync/status')
def api_sync_status():
    """API: 获取同步状态"""
    try:
        status = DataSyncService.get_sync_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/api/statistics')
def api_statistics():
    """API: 获取交易统计"""
    try:
        stats = HistoricalTradeService.get_trade_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/api/maintenance/cleanup', methods=['POST'])
def api_cleanup_data():
    """API: 清理数据"""
    try:
        data = request.get_json() or {}
        cleanup_type = data.get('type', 'orphaned_records')
        
        if cleanup_type == 'orphaned_records':
            result = _cleanup_orphaned_records()
        elif cleanup_type == 'old_logs':
            result = _cleanup_old_logs(data.get('days', 30))
        elif cleanup_type == 'temp_files':
            result = _cleanup_temp_files()
        else:
            raise ValidationError(f"不支持的清理类型: {cleanup_type}")
        
        return jsonify({
            'success': True,
            'data': result,
            'message': f'{cleanup_type} 清理完成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '数据清理失败'
        }), 500


@admin_bp.route('/api/maintenance/backup', methods=['POST'])
def api_backup_data():
    """API: 备份数据"""
    try:
        data = request.get_json() or {}
        backup_type = data.get('type', 'historical_trades')
        
        if backup_type == 'historical_trades':
            result = _backup_historical_trades()
        elif backup_type == 'all_data':
            result = _backup_all_data()
        else:
            raise ValidationError(f"不支持的备份类型: {backup_type}")
        
        return jsonify({
            'success': True,
            'data': result,
            'message': f'{backup_type} 备份完成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '数据备份失败'
        }), 500


@admin_bp.route('/reports/integrity')
def integrity_report():
    """完整性检查报告页面"""
    try:
        # 执行完整性检查
        integrity_result = DataSyncService.check_data_integrity()
        
        return render_template('admin/integrity_report.html',
                             integrity_result=integrity_result)
    except Exception as e:
        flash(f'生成完整性报告失败: {str(e)}', 'error')
        return redirect(url_for('admin.data_maintenance'))


@admin_bp.route('/reports/statistics')
def statistics_report():
    """统计报告页面"""
    try:
        # 获取详细统计
        trade_stats = HistoricalTradeService.get_trade_statistics()
        
        # 获取月度统计
        monthly_stats = _get_monthly_statistics()
        
        # 获取股票统计
        stock_stats = _get_stock_statistics()
        
        return render_template('admin/statistics_report.html',
                             trade_stats=trade_stats,
                             monthly_stats=monthly_stats,
                             stock_stats=stock_stats)
    except Exception as e:
        flash(f'生成统计报告失败: {str(e)}', 'error')
        return redirect(url_for('admin.data_maintenance'))


# 辅助函数

def _get_integrity_summary():
    """获取完整性检查摘要"""
    try:
        # 执行快速完整性检查
        from models.historical_trade import HistoricalTrade
        from models.trade_record import TradeRecord
        
        total_historical = HistoricalTrade.query.count()
        total_trades = TradeRecord.query.filter_by(is_corrected=False).count()
        
        # 检查是否有明显问题
        has_issues = False
        issues_count = 0
        
        # 检查重复记录
        from sqlalchemy import func
        duplicate_count = HistoricalTrade.query.with_entities(
            HistoricalTrade.stock_code,
            HistoricalTrade.buy_date,
            HistoricalTrade.sell_date,
            func.count(HistoricalTrade.id).label('count')
        ).group_by(
            HistoricalTrade.stock_code,
            HistoricalTrade.buy_date,
            HistoricalTrade.sell_date
        ).having(func.count(HistoricalTrade.id) > 1).count()
        
        if duplicate_count > 0:
            has_issues = True
            issues_count += duplicate_count
        
        return {
            'total_historical_trades': total_historical,
            'total_trade_records': total_trades,
            'has_issues': has_issues,
            'issues_count': issues_count,
            'duplicate_records': duplicate_count,
            'last_check': datetime.now().isoformat()
        }
        
    except Exception:
        return {
            'total_historical_trades': 0,
            'total_trade_records': 0,
            'has_issues': True,
            'issues_count': 1,
            'error': '无法获取完整性摘要'
        }


def _cleanup_orphaned_records():
    """清理孤立记录"""
    # 这里可以实现清理孤立记录的逻辑
    return {
        'type': 'orphaned_records',
        'cleaned_count': 0,
        'message': '暂未实现孤立记录清理'
    }


def _cleanup_old_logs(days):
    """清理旧日志"""
    import os
    import glob
    from datetime import datetime, timedelta
    
    cleaned_count = 0
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # 清理日志文件
    log_pattern = 'logs/*.log'
    for log_file in glob.glob(log_pattern):
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            if file_time < cutoff_date:
                os.remove(log_file)
                cleaned_count += 1
        except Exception:
            continue
    
    return {
        'type': 'old_logs',
        'cleaned_count': cleaned_count,
        'cutoff_days': days
    }


def _cleanup_temp_files():
    """清理临时文件"""
    import os
    import glob
    
    cleaned_count = 0
    temp_patterns = ['tmp/*', 'temp/*', '*.tmp', '*.temp']
    
    for pattern in temp_patterns:
        for temp_file in glob.glob(pattern):
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                    cleaned_count += 1
            except Exception:
                continue
    
    return {
        'type': 'temp_files',
        'cleaned_count': cleaned_count
    }


def _backup_historical_trades():
    """备份历史交易数据"""
    import os
    from models.historical_trade import HistoricalTrade
    
    # 创建备份目录
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'historical_trades_{timestamp}.json')
    
    # 导出数据
    trades = HistoricalTrade.query.all()
    backup_data = {
        'backup_time': datetime.now().isoformat(),
        'total_records': len(trades),
        'data': [trade.to_dict() for trade in trades]
    }
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
    
    return {
        'type': 'historical_trades',
        'backup_file': backup_file,
        'records_count': len(trades),
        'file_size': os.path.getsize(backup_file)
    }


def _backup_all_data():
    """备份所有数据"""
    # 这里可以实现完整数据备份
    return {
        'type': 'all_data',
        'message': '完整数据备份功能待实现'
    }


def _get_monthly_statistics():
    """获取月度统计"""
    from models.historical_trade import HistoricalTrade
    from sqlalchemy import func, extract
    
    # 按月统计
    monthly_query = HistoricalTrade.query.with_entities(
        extract('year', HistoricalTrade.completion_date).label('year'),
        extract('month', HistoricalTrade.completion_date).label('month'),
        func.count(HistoricalTrade.id).label('trade_count'),
        func.sum(HistoricalTrade.total_return).label('total_return'),
        func.avg(HistoricalTrade.return_rate).label('avg_return_rate')
    ).group_by(
        extract('year', HistoricalTrade.completion_date),
        extract('month', HistoricalTrade.completion_date)
    ).order_by(
        extract('year', HistoricalTrade.completion_date).desc(),
        extract('month', HistoricalTrade.completion_date).desc()
    ).limit(12).all()
    
    monthly_stats = []
    for row in monthly_query:
        monthly_stats.append({
            'year': int(row.year),
            'month': int(row.month),
            'trade_count': row.trade_count,
            'total_return': float(row.total_return) if row.total_return else 0,
            'avg_return_rate': float(row.avg_return_rate) * 100 if row.avg_return_rate else 0
        })
    
    return monthly_stats


def _get_stock_statistics():
    """获取股票统计"""
    from models.historical_trade import HistoricalTrade
    from sqlalchemy import func
    
    # 按股票统计
    stock_query = HistoricalTrade.query.with_entities(
        HistoricalTrade.stock_code,
        HistoricalTrade.stock_name,
        func.count(HistoricalTrade.id).label('trade_count'),
        func.sum(HistoricalTrade.total_return).label('total_return'),
        func.avg(HistoricalTrade.return_rate).label('avg_return_rate'),
        func.sum(HistoricalTrade.total_investment).label('total_investment')
    ).group_by(
        HistoricalTrade.stock_code,
        HistoricalTrade.stock_name
    ).order_by(
        func.count(HistoricalTrade.id).desc()
    ).limit(20).all()
    
    stock_stats = []
    for row in stock_query:
        stock_stats.append({
            'stock_code': row.stock_code,
            'stock_name': row.stock_name,
            'trade_count': row.trade_count,
            'total_return': float(row.total_return) if row.total_return else 0,
            'avg_return_rate': float(row.avg_return_rate) * 100 if row.avg_return_rate else 0,
            'total_investment': float(row.total_investment) if row.total_investment else 0
        })
    
    return stock_stats