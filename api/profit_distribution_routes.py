"""
收益分布配置API路由
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models.profit_distribution_config import ProfitDistributionConfig
from services.analytics_service import AnalyticsService
from error_handlers import ValidationError, DatabaseError

profit_distribution_bp = Blueprint('profit_distribution', __name__)


@profit_distribution_bp.route('/api/profit-distribution/configs', methods=['GET'])
def get_profit_distribution_configs():
    """获取所有收益分布配置"""
    try:
        configs = ProfitDistributionConfig.query.order_by(ProfitDistributionConfig.sort_order).all()
        return jsonify({
            'success': True,
            'data': [config.to_dict() for config in configs]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取配置失败: {str(e)}'
        }), 500


@profit_distribution_bp.route('/api/profit-distribution/configs', methods=['POST'])
def create_profit_distribution_config():
    """创建新的收益分布配置"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('range_name'):
            raise ValidationError('区间名称不能为空')
        
        # 创建新配置
        config = ProfitDistributionConfig(
            range_name=data['range_name'],
            min_profit_rate=data.get('min_profit_rate'),
            max_profit_rate=data.get('max_profit_rate'),
            sort_order=data.get('sort_order', 0),
            is_active=data.get('is_active', True),
            created_by=data.get('created_by', 'user')
        )
        
        # 验证区间有效性
        config.validate_range()
        
        db.session.add(config)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '配置创建成功',
            'data': config.to_dict()
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'创建配置失败: {str(e)}'
        }), 500


@profit_distribution_bp.route('/api/profit-distribution/configs/<int:config_id>', methods=['PUT'])
def update_profit_distribution_config(config_id):
    """更新收益分布配置"""
    try:
        config = ProfitDistributionConfig.query.get_or_404(config_id)
        data = request.get_json()
        
        # 更新字段
        if 'range_name' in data:
            config.range_name = data['range_name']
        if 'min_profit_rate' in data:
            config.min_profit_rate = data['min_profit_rate']
        if 'max_profit_rate' in data:
            config.max_profit_rate = data['max_profit_rate']
        if 'sort_order' in data:
            config.sort_order = data['sort_order']
        if 'is_active' in data:
            config.is_active = data['is_active']
        
        # 验证区间有效性
        config.validate_range()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '配置更新成功',
            'data': config.to_dict()
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新配置失败: {str(e)}'
        }), 500


@profit_distribution_bp.route('/api/profit-distribution/configs/<int:config_id>', methods=['DELETE'])
def delete_profit_distribution_config(config_id):
    """删除收益分布配置"""
    try:
        config = ProfitDistributionConfig.query.get_or_404(config_id)
        
        db.session.delete(config)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '配置删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除配置失败: {str(e)}'
        }), 500


@profit_distribution_bp.route('/api/profit-distribution/configs/reset-default', methods=['POST'])
def reset_default_configs():
    """重置为默认配置"""
    try:
        # 删除所有现有配置
        ProfitDistributionConfig.query.delete()
        
        # 创建默认配置
        ProfitDistributionConfig.create_default_configs()
        
        return jsonify({
            'success': True,
            'message': '已重置为默认配置'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'重置配置失败: {str(e)}'
        }), 500


@profit_distribution_bp.route('/api/profit-distribution/analysis', methods=['GET'])
def get_profit_distribution_analysis():
    """获取收益分布分析结果"""
    try:
        # 获取查询参数
        use_trade_pairs = request.args.get('use_trade_pairs', 'true').lower() == 'true'
        
        # 获取分析结果
        result = AnalyticsService.get_profit_distribution(use_trade_pairs=use_trade_pairs)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分析结果失败: {str(e)}'
        }), 500


@profit_distribution_bp.route('/api/profit-distribution/trade-pairs', methods=['GET'])
def get_trade_pairs_analysis():
    """获取交易配对分析详情"""
    try:
        from services.trade_pair_analyzer import TradePairAnalyzer
        
        # 获取完整的交易配对分析
        completed_pairs = TradePairAnalyzer.analyze_completed_trades()
        
        # 获取当前持仓汇总
        current_holdings = TradePairAnalyzer.get_current_holdings_summary()
        
        return jsonify({
            'success': True,
            'data': {
                'completed_pairs': completed_pairs,
                'current_holdings': current_holdings,
                'total_completed_trades': len(completed_pairs)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取交易配对分析失败: {str(e)}'
        }), 500


@profit_distribution_bp.route('/api/profit-distribution/configs/batch-update', methods=['POST'])
def batch_update_configs():
    """批量更新配置排序"""
    try:
        data = request.get_json()
        configs_data = data.get('configs', [])
        
        if not configs_data:
            raise ValidationError('配置数据不能为空')
        
        # 批量更新排序
        for config_data in configs_data:
            config_id = config_data.get('id')
            sort_order = config_data.get('sort_order')
            
            if config_id and sort_order is not None:
                config = ProfitDistributionConfig.query.get(config_id)
                if config:
                    config.sort_order = sort_order
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '批量更新成功'
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'批量更新失败: {str(e)}'
        }), 500