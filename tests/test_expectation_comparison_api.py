"""
期望对比API端点测试
"""
import pytest
import json
from app import create_app
from extensions import db
from models.trade_record import TradeRecord
from datetime import datetime, timedelta


class TestExpectationComparisonAPI:
    """期望对比API端点测试类"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    def test_expectation_comparison_endpoint_basic(self, client):
        """测试期望对比API端点基本功能
        
        Requirements: 2.1, 8.1, 8.2
        """
        response = client.get('/api/analytics/expectation-comparison')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # 验证响应格式
        assert data['success'] is True
        assert 'data' in data
        assert 'message' in data
        assert data['message'] == '获取期望对比数据成功'
        
        # 验证数据结构
        comparison_data = data['data']
        assert 'expectation' in comparison_data
        assert 'actual' in comparison_data
        assert 'comparison' in comparison_data
        assert 'time_range' in comparison_data
        assert 'base_capital' in comparison_data
        
        # 验证默认基准本金
        assert comparison_data['base_capital'] == 3200000
    
    def test_time_range_parameter_handling(self, client):
        """测试时间范围参数处理
        
        Requirements: 6.1, 6.2, 6.3
        """
        valid_ranges = ['30d', '90d', '1y', 'all']
        
        for time_range in valid_ranges:
            response = client.get(f'/api/analytics/expectation-comparison?time_range={time_range}')
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['time_range']['range'] == time_range
    
    def test_invalid_time_range_validation(self, client):
        """测试无效时间范围验证
        
        Requirements: 6.3, 8.1
        """
        response = client.get('/api/analytics/expectation-comparison?time_range=invalid')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert '时间范围必须是以下之一' in data['error']['message']
    
    def test_base_capital_parameter_handling(self, client):
        """测试基准本金参数处理
        
        Requirements: 7.1, 7.2
        """
        # 测试自定义基准本金
        response = client.get('/api/analytics/expectation-comparison?base_capital=5000000')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['base_capital'] == 5000000
        
        # 验证期望收益金额按比例调整
        expected_return_amount = data['data']['expectation']['return_amount']
        assert expected_return_amount == 5000000 * 0.041  # 期望收益率 * 基准本金
    
    def test_invalid_base_capital_validation(self, client):
        """测试无效基准本金验证
        
        Requirements: 8.1, 8.2
        """
        # 测试负数基准本金
        response = client.get('/api/analytics/expectation-comparison?base_capital=-1000')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert '基准本金必须大于0' in data['error']['message']
        
        # 测试零基准本金
        response = client.get('/api/analytics/expectation-comparison?base_capital=0')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_api_response_format(self, client):
        """测试API响应格式
        
        Requirements: 2.1, 8.1
        """
        response = client.get('/api/analytics/expectation-comparison')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # 验证期望指标格式
        expectation = data['data']['expectation']
        required_expectation_fields = ['return_rate', 'return_amount', 'holding_days', 'success_rate']
        for field in required_expectation_fields:
            assert field in expectation
            assert isinstance(expectation[field], (int, float))
        
        # 验证实际指标格式
        actual = data['data']['actual']
        required_actual_fields = ['return_rate', 'return_amount', 'holding_days', 'success_rate', 'total_trades', 'completed_trades']
        for field in required_actual_fields:
            assert field in actual
            assert isinstance(actual[field], (int, float))
        
        # 验证对比结果格式
        comparison = data['data']['comparison']
        required_comparison_fields = [
            'return_rate_diff', 'return_amount_diff', 'holding_days_diff', 'success_rate_diff',
            'return_rate_pct_diff', 'holding_days_pct_diff', 'success_rate_pct_diff'
        ]
        for field in required_comparison_fields:
            assert field in comparison
            assert isinstance(comparison[field], (int, float))
        
        # 验证状态字段格式
        status_fields = ['return_rate_status', 'holding_days_status', 'success_rate_status']
        for status_field in status_fields:
            assert status_field in comparison
            status = comparison[status_field]
            assert 'status' in status
            assert 'message' in status
            assert 'color' in status
        
        # 验证时间范围信息格式
        time_range = data['data']['time_range']
        required_time_fields = ['range', 'range_name', 'start_date', 'end_date', 'total_trades']
        for field in required_time_fields:
            assert field in time_range
    
    def test_error_handling(self, client):
        """测试错误处理
        
        Requirements: 8.1, 8.2
        """
        # 测试多个无效参数
        response = client.get('/api/analytics/expectation-comparison?time_range=invalid&base_capital=-1000')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_combined_parameters(self, client):
        """测试组合参数
        
        Requirements: 6.1, 6.2, 7.1, 7.2
        """
        response = client.get('/api/analytics/expectation-comparison?time_range=90d&base_capital=1000000')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['time_range']['range'] == '90d'
        assert data['data']['base_capital'] == 1000000
        
        # 验证期望收益金额按新基准本金计算
        expected_return_amount = data['data']['expectation']['return_amount']
        assert expected_return_amount == 1000000 * 0.041
    
    def test_api_endpoint_path(self, client):
        """测试API端点路径
        
        Requirements: 2.1
        """
        # 验证正确的端点路径
        response = client.get('/api/analytics/expectation-comparison')
        assert response.status_code == 200
        
        # 验证错误的端点路径返回404
        response = client.get('/api/analytics/expectation-compare')
        assert response.status_code == 404
        
        response = client.get('/api/expectation-comparison')
        assert response.status_code == 404
    
    def test_http_method_validation(self, client):
        """测试HTTP方法验证
        
        Requirements: 2.1
        """
        # 验证GET方法可用
        response = client.get('/api/analytics/expectation-comparison')
        assert response.status_code == 200
        
        # 验证其他方法不可用
        response = client.post('/api/analytics/expectation-comparison')
        assert response.status_code == 405
        
        response = client.put('/api/analytics/expectation-comparison')
        assert response.status_code == 405
        
        response = client.delete('/api/analytics/expectation-comparison')
        assert response.status_code == 405