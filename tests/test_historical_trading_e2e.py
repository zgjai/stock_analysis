"""
历史交易记录功能端到端测试
测试完整的用户流程，从数据同步到复盘功能
"""
import pytest
import json
import tempfile
import os
from datetime import datetime, date, timedelta
from flask import url_for
from models import TradingRecord, HistoricalTrade, TradeReview, ReviewImage
from services.historical_trade_service import HistoricalTradeService
from services.review_service import ReviewService


class TestHistoricalTradingE2E:
    """历史交易记录端到端测试"""
    
    def setup_method(self):
        """测试前准备数据"""
        self.test_stock_code = '000001'
        self.test_stock_name = '平安银行'
        
    def create_sample_trading_records(self, db_session):
        """创建示例交易记录"""
        # 创建买入记录
        buy_record = TradingRecord(
            stock_code=self.test_stock_code,
            stock_name=self.test_stock_name,
            trade_type='buy',
            price=10.00,
            quantity=1000,
            trade_date=datetime(2024, 1, 15, 9, 30, 0),
            reason='测试买入',
            stop_loss_price=9.00,
            take_profit_ratio=0.20
        )
        
        # 创建卖出记录
        sell_record = TradingRecord(
            stock_code=self.test_stock_code,
            stock_name=self.test_stock_name,
            trade_type='sell',
            price=12.00,
            quantity=1000,
            trade_date=datetime(2024, 1, 25, 14, 30, 0),
            reason='止盈卖出',
            sell_ratio=1.0
        )
        
        db_session.add(buy_record)
        db_session.add(sell_record)
        db_session.commit()
        
        return buy_record, sell_record
    
    def test_complete_historical_trading_workflow(self, client, db_session):
        """测试完整的历史交易工作流程"""
        # 1. 创建交易记录
        buy_record, sell_record = self.create_sample_trading_records(db_session)
        
        # 2. 同步生成历史交易记录
        response = client.post('/api/historical-trades/sync')
        assert response.status_code == 200
        
        # 验证历史交易记录已创建
        historical_trades = HistoricalTrade.query.all()
        assert len(historical_trades) == 1
        
        historical_trade = historical_trades[0]
        assert historical_trade.stock_code == self.test_stock_code
        assert historical_trade.total_investment == 10000.00  # 10.00 * 1000
        assert historical_trade.total_return == 2000.00      # (12.00 - 10.00) * 1000
        assert historical_trade.return_rate == 0.20          # 20%
        
        # 3. 获取历史交易列表
        response = client.get('/api/historical-trades')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total'] == 1
        assert len(data['trades']) == 1
        assert data['trades'][0]['stock_code'] == self.test_stock_code
        
        # 4. 创建复盘记录
        review_data = {
            'review_title': '平安银行交易复盘',
            'review_content': '这是一次成功的交易，严格按照计划执行。',
            'review_type': 'success',
            'strategy_score': 5,
            'timing_score': 4,
            'risk_control_score': 5,
            'overall_score': 5,
            'key_learnings': '严格执行止盈计划很重要',
            'improvement_areas': '可以在更好的时机买入'
        }
        
        response = client.post(
            f'/api/trade-reviews',
            data=json.dumps({
                'historical_trade_id': historical_trade.id,
                **review_data
            }),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # 5. 验证复盘记录已创建
        reviews = TradeReview.query.all()
        assert len(reviews) == 1
        
        review = reviews[0]
        assert review.historical_trade_id == historical_trade.id
        assert review.review_title == review_data['review_title']
        assert review.overall_score == 5
        
        # 6. 获取复盘记录
        response = client.get(f'/api/trade-reviews/{historical_trade.id}')
        assert response.status_code == 200
        
        review_data_response = json.loads(response.data)
        assert review_data_response['review_title'] == review_data['review_title']
        assert review_data_response['overall_score'] == 5
        
        # 7. 更新复盘记录
        updated_data = {
            'review_content': '更新后的复盘内容',
            'overall_score': 4
        }
        
        response = client.put(
            f'/api/trade-reviews/{review.id}',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # 验证更新成功
        updated_review = TradeReview.query.get(review.id)
        assert updated_review.review_content == updated_data['review_content']
        assert updated_review.overall_score == 4
    
    def test_historical_trading_with_multiple_trades(self, client, db_session):
        """测试多笔交易的历史记录处理"""
        # 创建多笔不同股票的交易记录
        stocks = [
            ('000001', '平安银行', 10.00, 12.00),
            ('000002', '万科A', 15.00, 18.00),
            ('600036', '招商银行', 35.00, 40.00)
        ]
        
        for stock_code, stock_name, buy_price, sell_price in stocks:
            # 买入记录
            buy_record = TradingRecord(
                stock_code=stock_code,
                stock_name=stock_name,
                trade_type='buy',
                price=buy_price,
                quantity=1000,
                trade_date=datetime(2024, 1, 15, 9, 30, 0),
                reason='测试买入'
            )
            
            # 卖出记录
            sell_record = TradingRecord(
                stock_code=stock_code,
                stock_name=stock_name,
                trade_type='sell',
                price=sell_price,
                quantity=1000,
                trade_date=datetime(2024, 1, 25, 14, 30, 0),
                reason='止盈卖出',
                sell_ratio=1.0
            )
            
            db_session.add(buy_record)
            db_session.add(sell_record)
        
        db_session.commit()
        
        # 同步生成历史交易记录
        response = client.post('/api/historical-trades/sync')
        assert response.status_code == 200
        
        # 验证所有历史交易记录都已创建
        historical_trades = HistoricalTrade.query.all()
        assert len(historical_trades) == 3
        
        # 测试筛选功能
        response = client.get('/api/historical-trades?stock_code=000001')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total'] == 1
        assert data['trades'][0]['stock_code'] == '000001'
        
        # 测试分页功能
        response = client.get('/api/historical-trades?page=1&per_page=2')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['trades']) == 2
        assert data['total'] == 3
        assert data['pages'] == 2
    
    def test_review_image_upload_workflow(self, client, db_session):
        """测试复盘图片上传工作流程"""
        # 创建历史交易记录
        buy_record, sell_record = self.create_sample_trading_records(db_session)
        
        # 同步生成历史交易记录
        client.post('/api/historical-trades/sync')
        historical_trade = HistoricalTrade.query.first()
        
        # 创建复盘记录
        review_data = {
            'historical_trade_id': historical_trade.id,
            'review_title': '测试复盘',
            'review_content': '测试内容'
        }
        
        response = client.post(
            '/api/trade-reviews',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        review = TradeReview.query.first()
        
        # 创建临时测试图片文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(b'fake image data')
            tmp_file_path = tmp_file.name
        
        try:
            # 测试图片上传
            with open(tmp_file_path, 'rb') as test_file:
                response = client.post(
                    f'/api/trade-reviews/{review.id}/images',
                    data={
                        'file': (test_file, 'test_image.png'),
                        'description': '测试图片'
                    },
                    content_type='multipart/form-data'
                )
            
            assert response.status_code == 201
            
            # 验证图片记录已创建
            images = ReviewImage.query.all()
            assert len(images) == 1
            
            image = images[0]
            assert image.trade_review_id == review.id
            assert image.original_filename == 'test_image.png'
            assert image.description == '测试图片'
            
            # 测试删除图片
            response = client.delete(f'/api/trade-reviews/images/{image.id}')
            assert response.status_code == 200
            
            # 验证图片记录已删除
            assert ReviewImage.query.count() == 0
            
        finally:
            # 清理临时文件
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def test_error_handling_scenarios(self, client, db_session):
        """测试错误处理场景"""
        # 测试获取不存在的历史交易
        response = client.get('/api/historical-trades/999')
        assert response.status_code == 404
        
        # 测试为不存在的历史交易创建复盘
        response = client.post(
            '/api/trade-reviews',
            data=json.dumps({
                'historical_trade_id': 999,
                'review_title': '测试'
            }),
            content_type='application/json'
        )
        assert response.status_code == 404
        
        # 测试无效的复盘数据
        response = client.post(
            '/api/trade-reviews',
            data=json.dumps({
                'historical_trade_id': 1,
                'strategy_score': 10  # 超出范围
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # 测试上传无效文件类型
        response = client.post(
            '/api/trade-reviews/1/images',
            data={
                'file': (tempfile.NamedTemporaryFile(suffix='.txt'), 'test.txt')
            },
            content_type='multipart/form-data'
        )
        assert response.status_code == 400
    
    def test_data_consistency_and_integrity(self, client, db_session):
        """测试数据一致性和完整性"""
        # 创建交易记录
        buy_record, sell_record = self.create_sample_trading_records(db_session)
        
        # 同步生成历史交易记录
        response = client.post('/api/historical-trades/sync')
        assert response.status_code == 200
        
        historical_trade = HistoricalTrade.query.first()
        
        # 验证计算的准确性
        expected_investment = buy_record.price * buy_record.quantity
        expected_return = (sell_record.price - buy_record.price) * sell_record.quantity
        expected_rate = expected_return / expected_investment
        
        assert abs(historical_trade.total_investment - expected_investment) < 0.01
        assert abs(historical_trade.total_return - expected_return) < 0.01
        assert abs(historical_trade.return_rate - expected_rate) < 0.0001
        
        # 验证关联记录ID的正确性
        buy_ids = json.loads(historical_trade.buy_records_ids)
        sell_ids = json.loads(historical_trade.sell_records_ids)
        
        assert buy_record.id in buy_ids
        assert sell_record.id in sell_ids
        
        # 验证持仓天数计算
        expected_holding_days = (sell_record.trade_date.date() - buy_record.trade_date.date()).days
        assert historical_trade.holding_days == expected_holding_days