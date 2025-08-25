"""
交易录入流程端到端测试
测试买入/卖出工作流程、股票数量验证规则等
"""
import pytest
import json
from datetime import datetime, date
from decimal import Decimal
from models.trade_record import TradeRecord
from models.stock_price import StockPrice
from utils.stock_utils import is_star_market_stock, validate_stock_quantity


class TestTradingEntryWorkflowE2E:
    """交易录入流程端到端测试类"""
    
    def test_buy_workflow_regular_stock(self, client, db_session):
        """测试普通股票买入流程"""
        trade_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': '10.50',
            'quantity': 1000,  # 100的倍数
            'trade_date': '2024-01-15 09:30:00',
            'reason': '技术突破',
            'notes': '测试买入'
        }
        
        response = client.post('/api/trades', 
                             data=json.dumps(trade_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        # 验证数据库中的记录
        trade = TradeRecord.query.filter_by(stock_code='000001').first()
        assert trade is not None
        assert trade.trade_type == 'buy'
        assert trade.quantity == 1000
        assert float(trade.price) == 10.50
    
    def test_buy_workflow_star_market_stock(self, client, db_session):
        """测试科创板股票买入流程"""
        trade_data = {
            'stock_code': '688001',
            'stock_name': '华兴源创',
            'trade_type': 'buy',
            'price': '25.80',
            'quantity': 150,  # 科创板允许非100倍数
            'trade_date': '2024-01-15 09:30:00',
            'reason': '科创板投资',
            'notes': '测试科创板买入'
        }
        
        response = client.post('/api/trades',
                             data=json.dumps(trade_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        # 验证数据库中的记录
        trade = TradeRecord.query.filter_by(stock_code='688001').first()
        assert trade is not None
        assert trade.quantity == 150
    
    def test_buy_workflow_invalid_quantity_regular_stock(self, client, db_session):
        """测试普通股票无效数量的买入流程"""
        trade_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': '10.50',
            'quantity': 150,  # 不是100的倍数
            'trade_date': '2024-01-15 09:30:00',
            'reason': '技术突破'
        }
        
        response = client.post('/api/trades',
                             data=json.dumps(trade_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'quantity' in response_data['message'].lower()
    
    def test_sell_workflow_with_holdings(self, client, db_session):
        """测试有持仓情况下的卖出流程"""
        # 先创建买入记录
        buy_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.00'),
            quantity=1000,
            trade_date=datetime(2024, 1, 15),
            reason='买入建仓'
        )
        db_session.add(buy_trade)
        db_session.commit()
        
        # 测试卖出
        sell_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'sell',
            'price': '12.00',
            'quantity': 500,  # 部分卖出
            'trade_date': '2024-02-15 14:30:00',
            'reason': '止盈卖出'
        }
        
        response = client.post('/api/trades',
                             data=json.dumps(sell_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        # 验证卖出记录
        sell_trade = TradeRecord.query.filter_by(
            stock_code='000001', 
            trade_type='sell'
        ).first()
        assert sell_trade is not None
        assert sell_trade.quantity == 500
    
    def test_sell_workflow_insufficient_holdings(self, client, db_session):
        """测试持仓不足的卖出流程"""
        # 创建少量持仓
        buy_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.00'),
            quantity=500,
            trade_date=datetime(2024, 1, 15),
            reason='少量买入'
        )
        db_session.add(buy_trade)
        db_session.commit()
        
        # 尝试卖出超过持仓数量
        sell_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'sell',
            'price': '12.00',
            'quantity': 1000,  # 超过持仓
            'trade_date': '2024-02-15 14:30:00',
            'reason': '卖出'
        }
        
        response = client.post('/api/trades',
                             data=json.dumps(sell_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'insufficient' in response_data['message'].lower() or '不足' in response_data['message']
    
    def test_get_current_holdings_for_sell(self, client, db_session):
        """测试获取当前持仓用于卖出选择"""
        # 创建多只股票的持仓
        holdings = [
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='buy', price=Decimal('10.00'), quantity=1000,
                trade_date=datetime(2024, 1, 15), reason='买入1'
            ),
            TradeRecord(
                stock_code='000002', stock_name='万科A',
                trade_type='buy', price=Decimal('15.00'), quantity=500,
                trade_date=datetime(2024, 1, 20), reason='买入2'
            ),
            # 部分卖出
            TradeRecord(
                stock_code='000001', stock_name='平安银行',
                trade_type='sell', price=Decimal('11.00'), quantity=300,
                trade_date=datetime(2024, 2, 15), reason='部分卖出'
            )
        ]
        
        db_session.add_all(holdings)
        db_session.commit()
        
        # 获取当前持仓
        response = client.get('/api/trades/current-holdings')
        assert response.status_code == 200
        
        holdings_data = json.loads(response.data)
        assert len(holdings_data) == 2  # 两只股票
        
        # 验证持仓数量
        stock_001 = next(h for h in holdings_data if h['stock_code'] == '000001')
        stock_002 = next(h for h in holdings_data if h['stock_code'] == '000002')
        
        assert stock_001['quantity'] == 700  # 1000 - 300
        assert stock_002['quantity'] == 500
    
    def test_stock_quantity_validation_utils(self):
        """测试股票数量验证工具函数"""
        # 测试科创板股票识别
        assert is_star_market_stock('688001') == True
        assert is_star_market_stock('688999') == True
        assert is_star_market_stock('000001') == False
        assert is_star_market_stock('300001') == False
        
        # 测试普通股票数量验证
        assert validate_stock_quantity('000001', 100) == True
        assert validate_stock_quantity('000001', 1000) == True
        assert validate_stock_quantity('000001', 150) == False
        assert validate_stock_quantity('000001', 0) == False
        
        # 测试科创板股票数量验证
        assert validate_stock_quantity('688001', 100) == True
        assert validate_stock_quantity('688001', 150) == True
        assert validate_stock_quantity('688001', 1) == True
        assert validate_stock_quantity('688001', 0) == False
    
    def test_trade_type_selection_workflow(self, client, db_session):
        """测试交易类型选择工作流程"""
        # 创建一些持仓
        buy_trade = TradeRecord(
            stock_code='000001',
            stock_name='平安银行',
            trade_type='buy',
            price=Decimal('10.00'),
            quantity=1000,
            trade_date=datetime(2024, 1, 15),
            reason='建仓'
        )
        db_session.add(buy_trade)
        db_session.commit()
        
        # 测试获取交易选项（买入时应该允许任意股票）
        response = client.get('/api/trades/options?type=buy')
        assert response.status_code == 200
        
        # 测试获取卖出选项（应该只返回有持仓的股票）
        response = client.get('/api/trades/options?type=sell')
        assert response.status_code == 200
        
        options_data = json.loads(response.data)
        assert len(options_data) >= 1
        assert any(stock['stock_code'] == '000001' for stock in options_data)
    
    def test_complete_buy_sell_cycle(self, client, db_session):
        """测试完整的买卖周期"""
        # 1. 买入
        buy_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': '10.00',
            'quantity': 1000,
            'trade_date': '2024-01-15 09:30:00',
            'reason': '技术突破',
            'stop_loss_price': '9.00',
            'take_profit_ratio': '0.15',
            'sell_ratio': '0.5'
        }
        
        response = client.post('/api/trades',
                             data=json.dumps(buy_data),
                             content_type='application/json')
        assert response.status_code == 201
        
        # 2. 验证持仓
        response = client.get('/api/trades/current-holdings')
        holdings = json.loads(response.data)
        assert len(holdings) == 1
        assert holdings[0]['quantity'] == 1000
        
        # 3. 部分卖出
        sell_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'sell',
            'price': '12.00',
            'quantity': 500,
            'trade_date': '2024-02-15 14:30:00',
            'reason': '止盈'
        }
        
        response = client.post('/api/trades',
                             data=json.dumps(sell_data),
                             content_type='application/json')
        assert response.status_code == 201
        
        # 4. 验证剩余持仓
        response = client.get('/api/trades/current-holdings')
        holdings = json.loads(response.data)
        assert len(holdings) == 1
        assert holdings[0]['quantity'] == 500
        
        # 5. 全部卖出
        sell_all_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'sell',
            'price': '11.50',
            'quantity': 500,
            'trade_date': '2024-03-15 14:30:00',
            'reason': '清仓'
        }
        
        response = client.post('/api/trades',
                             data=json.dumps(sell_all_data),
                             content_type='application/json')
        assert response.status_code == 201
        
        # 6. 验证无持仓
        response = client.get('/api/trades/current-holdings')
        holdings = json.loads(response.data)
        assert len(holdings) == 0
    
    def test_profit_target_percentage_handling(self, client, db_session):
        """测试止盈目标百分比处理"""
        trade_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': '10.00',
            'quantity': 1000,
            'trade_date': '2024-01-15 09:30:00',
            'reason': '买入',
            'take_profit_ratio': '15',  # 15% (用户输入格式)
            'sell_ratio': '50'  # 50% (用户输入格式)
        }
        
        response = client.post('/api/trades',
                             data=json.dumps(trade_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        # 验证百分比正确存储
        trade = TradeRecord.query.filter_by(stock_code='000001').first()
        assert trade is not None
        # 验证百分比转换正确（15% -> 0.15）
        assert abs(float(trade.take_profit_ratio) - 0.15) < 0.001
        assert abs(float(trade.sell_ratio) - 0.50) < 0.001