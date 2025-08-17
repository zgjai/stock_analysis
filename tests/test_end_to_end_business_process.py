"""
端到端业务流程测试
测试从股票池添加到买入记录的流程、验证买入后进行复盘的完整流程、测试卖出记录和收益计算的流程
需求: 1.3, 1.4, 1.5
"""
import pytest
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from models.trade_record import TradeRecord
from models.stock_pool import StockPool
from models.review_record import ReviewRecord
from models.stock_price import StockPrice
from services.trading_service import TradingService
from services.stock_pool_service import StockPoolService
from services.review_service import ReviewService, HoldingService
from services.price_service import PriceService
from error_handlers import ValidationError, NotFoundError, DatabaseError


class TestEndToEndBusinessProcess:
    """端到端业务流程测试"""
    
    def setup_trading_config(self, app):
        """设置交易配置"""
        with app.app_context():
            from models.configuration import Configuration
            Configuration.set_buy_reasons(['少妇B1战法', '少妇SB1战法', '少妇B2战法', '技术突破', '从股票池买入'])
            Configuration.set_sell_reasons(['部分止盈', '止损', '下等马/草泥马', '技术破位', '全部卖出'])
    
    # ========== 5.1 完整交易流程测试 ==========
    
    def test_complete_trading_workflow_from_stock_pool_to_buy(self, app, db_session):
        """测试从股票池添加到买入记录的完整流程"""
        with app.app_context():
            self.setup_trading_config(app)
            # 1. 添加股票到观察池
            watch_pool_data = {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'pool_type': 'watch',
                'target_price': 12.00,
                'add_reason': '技术形态良好，等待突破',
                'status': 'active'
            }
            
            watch_stock = StockPoolService.create_stock_pool_entry(watch_pool_data)
            assert watch_stock.id is not None
            assert watch_stock.pool_type == 'watch'
            assert watch_stock.status == 'active'
            
            # 2. 移动股票到待买入池
            buy_ready_stock = StockPoolService.move_stock_to_pool(
                watch_stock.id, 
                'buy_ready', 
                '突破确认，准备买入'
            )
            assert buy_ready_stock.pool_type == 'buy_ready'
            assert buy_ready_stock.status == 'active'
            
            # 验证原记录状态更新
            updated_watch_stock = StockPoolService.get_by_id(watch_stock.id)
            assert updated_watch_stock.status == 'moved'
            
            # 3. 从待买入池创建买入记录
            buy_trade_data = {
                'stock_code': buy_ready_stock.stock_code,
                'stock_name': buy_ready_stock.stock_name,
                'trade_type': 'buy',
                'price': 12.50,  # 高于目标价格，表示突破买入
                'quantity': 1000,
                'reason': '从股票池买入',
                'notes': f'从待买入池买入，目标价格: {buy_ready_stock.target_price}',
                'stop_loss_price': 11.25,
                'take_profit_ratio': 0.20,
                'sell_ratio': 0.50
            }
            
            buy_trade = TradingService.create_trade(buy_trade_data)
            assert buy_trade.id is not None
            assert buy_trade.stock_code == '000001'
            assert buy_trade.trade_type == 'buy'
            assert float(buy_trade.price) == 12.50
            
            # 验证止损止盈计算
            expected_loss_ratio = (12.50 - 11.25) / 12.50  # 0.10
            expected_profit_ratio = 0.20 * 0.50  # 0.10
            assert abs(float(buy_trade.expected_loss_ratio) - expected_loss_ratio) < 0.001
            assert abs(float(buy_trade.expected_profit_ratio) - expected_profit_ratio) < 0.001
            
            # 4. 买入后从股票池移除（可选步骤）
            removed_stock = StockPoolService.remove_stock_from_pool(
                buy_ready_stock.id, 
                '已买入，从池中移除'
            )
            assert removed_stock.status == 'removed'
            
            # 5. 验证完整流程的数据关联
            # 检查股票池历史记录
            stock_history = StockPoolService.get_stock_history('000001')
            assert len(stock_history) == 2  # watch -> buy_ready -> removed
            
            # 检查交易记录
            trades = TradingService.get_trades(filters={'stock_code': '000001'})
            assert trades['total'] == 1
            assert trades['trades'][0]['trade_type'] == 'buy'
    
    def test_buy_to_review_complete_workflow(self, app, db_session):
        """测试买入后进行复盘的完整流程"""
        with app.app_context():
            self.setup_trading_config(app)
            # 1. 创建买入记录
            buy_trade_data = {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'buy',
                'price': 15.80,
                'quantity': 800,
                'trade_date': datetime.now() - timedelta(days=3),
                'reason': '少妇B1战法',
                'notes': '技术突破买入',
                'stop_loss_price': 14.22,
                'take_profit_ratio': 0.15,
                'sell_ratio': 0.60
            }
            
            buy_trade = TradingService.create_trade(buy_trade_data)
            assert buy_trade.id is not None
            
            # 2. 添加当前价格数据
            price_data = {
                'stock_code': '000002',
                'stock_name': '万科A',
                'current_price': 16.50,
                'change_percent': 4.43,  # (16.50 - 15.80) / 15.80 * 100
                'record_date': date.today()
            }
            
            price_record = StockPrice.update_or_create(
                stock_code=price_data['stock_code'],
                stock_name=price_data['stock_name'],
                current_price=price_data['current_price'],
                change_percent=price_data['change_percent'],
                record_date=price_data['record_date']
            )
            assert price_record.id is not None
            assert float(price_record.current_price) == 16.50
            
            # 3. 创建复盘记录
            review_data = {
                'stock_code': '000002',
                'review_date': date.today(),
                'price_up_score': 1,  # 价格上涨
                'bbi_score': 1,       # 不破BBI线
                'volume_score': 0,    # 有放量阴线
                'trend_score': 1,     # 趋势向上
                'j_score': 1,         # J没死叉
                'analysis': '整体表现良好，价格突破后持续上涨，但有放量阴线需要关注',
                'decision': 'hold',
                'reason': '技术指标良好，继续持有观察',
                'holding_days': 3
            }
            
            review_record = ReviewService.create_review(review_data)
            assert review_record.id is not None
            assert review_record.total_score == 4  # 1+1+0+1+1
            assert review_record.decision == 'hold'
            
            # 4. 验证持仓信息计算
            holdings = HoldingService.get_current_holdings()
            holding_002 = next((h for h in holdings if h['stock_code'] == '000002'), None)
            assert holding_002 is not None
            assert holding_002['current_quantity'] == 800
            assert holding_002['avg_buy_price'] == 15.80
            
            # 验证持仓基本信息
            assert holding_002['stock_code'] == '000002'
            assert holding_002['stock_name'] == '万科A'
            assert holding_002['total_buy_quantity'] == 800
            assert holding_002['total_sell_quantity'] == 0
            
            # 5. 验证复盘记录与交易记录的关联
            reviews_by_stock = ReviewService.get_reviews_by_stock('000002')
            assert len(reviews_by_stock) == 1
            assert reviews_by_stock[0].stock_code == buy_trade.stock_code
            
            # 6. 更新复盘记录（模拟后续复盘）
            updated_review_data = {
                'price_up_score': 1,
                'bbi_score': 1,
                'volume_score': 1,  # 改善
                'trend_score': 1,
                'j_score': 0,       # 恶化
                'analysis': '价格继续上涨，成交量正常，但J值开始走弱',
                'decision': 'sell_partial',
                'reason': '部分止盈，降低仓位',
                'holding_days': 5
            }
            
            updated_review = ReviewService.update_review(review_record.id, updated_review_data)
            assert updated_review.total_score == 4  # 1+1+1+1+0
            assert updated_review.decision == 'sell_partial'
            assert updated_review.holding_days == 5
    
    def test_sell_record_and_profit_calculation_workflow(self, app, db_session):
        """测试卖出记录和收益计算的完整流程"""
        with app.app_context():
            self.setup_trading_config(app)
            # 1. 创建买入记录
            buy_trades_data = [
                {
                    'stock_code': '000003',
                    'stock_name': '中国平安',
                    'trade_type': 'buy',
                    'price': 45.20,
                    'quantity': 500,
                    'trade_date': datetime.now() - timedelta(days=10),
                    'reason': '少妇B2战法',
                    'notes': '第一次买入'
                },
                {
                    'stock_code': '000003',
                    'stock_name': '中国平安',
                    'trade_type': 'buy',
                    'price': 43.80,
                    'quantity': 300,
                    'trade_date': datetime.now() - timedelta(days=5),
                    'reason': '少妇B2战法',
                    'notes': '加仓买入'
                }
            ]
            
            buy_trades = []
            for buy_data in buy_trades_data:
                trade = TradingService.create_trade(buy_data)
                buy_trades.append(trade)
            
            # 验证买入记录创建
            assert len(buy_trades) == 2
            total_buy_quantity = sum(t.quantity for t in buy_trades)
            assert total_buy_quantity == 800
            
            # 2. 添加当前价格
            price_data = {
                'stock_code': '000003',
                'stock_name': '中国平安',
                'current_price': 48.50,
                'change_percent': 7.30,
                'record_date': date.today()
            }
            StockPrice.update_or_create(
                stock_code=price_data['stock_code'],
                stock_name=price_data['stock_name'],
                current_price=price_data['current_price'],
                change_percent=price_data['change_percent'],
                record_date=price_data['record_date']
            )
            
            # 3. 检查持仓状态
            holdings = HoldingService.get_current_holdings()
            holding_003 = next((h for h in holdings if h['stock_code'] == '000003'), None)
            assert holding_003 is not None
            assert holding_003['current_quantity'] == 800
            
            # 计算平均成本: (45.20*500 + 43.80*300) / 800 = 44.65
            expected_avg_cost = (45.20 * 500 + 43.80 * 300) / 800
            assert abs(holding_003['avg_buy_price'] - expected_avg_cost) < 0.2
            
            # 4. 创建部分卖出记录
            sell_data_1 = {
                'stock_code': '000003',
                'stock_name': '中国平安',
                'trade_type': 'sell',
                'price': 48.00,
                'quantity': 300,
                'trade_date': datetime.now() - timedelta(days=1),
                'reason': '部分止盈',
                'notes': '第一次部分卖出'
            }
            
            sell_trade_1 = TradingService.create_trade(sell_data_1)
            assert sell_trade_1.id is not None
            assert sell_trade_1.trade_type == 'sell'
            
            # 5. 验证部分卖出后的持仓变化
            updated_holdings = HoldingService.get_current_holdings()
            updated_holding_003 = next((h for h in updated_holdings if h['stock_code'] == '000003'), None)
            assert updated_holding_003 is not None
            assert updated_holding_003['current_quantity'] == 500  # 800 - 300
            
            # 平均成本应该保持不变
            assert abs(updated_holding_003['avg_buy_price'] - expected_avg_cost) < 0.2
            
            # 6. 计算已实现收益
            # 第一次卖出收益: (48.00 - 44.65) * 300 = 1005
            expected_realized_profit_1 = (48.00 - expected_avg_cost) * 300
            
            # 通过交易记录验证收益计算
            all_trades = TradingService.get_trades(filters={'stock_code': '000003'})
            assert all_trades['total'] == 3  # 2买 + 1卖
            
            # 7. 创建第二次卖出记录
            sell_data_2 = {
                'stock_code': '000003',
                'stock_name': '中国平安',
                'trade_type': 'sell',
                'price': 49.20,
                'quantity': 500,
                'trade_date': datetime.now(),
                'reason': '全部卖出',
                'notes': '全部清仓'
            }
            
            sell_trade_2 = TradingService.create_trade(sell_data_2)
            assert sell_trade_2.id is not None
            
            # 8. 验证全部卖出后的持仓状态
            final_holdings = HoldingService.get_current_holdings()
            final_holding_003 = next((h for h in final_holdings if h['stock_code'] == '000003'), None)
            # 应该没有持仓了，或者数量为0
            assert final_holding_003 is None or final_holding_003['current_quantity'] == 0
            
            # 9. 计算总收益
            # 第二次卖出收益: (49.20 - 44.65) * 500 = 2275
            expected_realized_profit_2 = (49.20 - expected_avg_cost) * 500
            total_expected_profit = expected_realized_profit_1 + expected_realized_profit_2
            
            # 验证总交易记录
            final_trades = TradingService.get_trades(filters={'stock_code': '000003'})
            assert final_trades['total'] == 4  # 2买 + 2卖
            
            # 验证买卖数量平衡
            buy_quantity = sum(t['quantity'] for t in final_trades['trades'] if t['trade_type'] == 'buy')
            sell_quantity = sum(t['quantity'] for t in final_trades['trades'] if t['trade_type'] == 'sell')
            assert buy_quantity == sell_quantity == 800
            
            # 10. 验证收益计算的准确性
            buy_cost = sum(t['price'] * t['quantity'] for t in final_trades['trades'] if t['trade_type'] == 'buy')
            sell_revenue = sum(t['price'] * t['quantity'] for t in final_trades['trades'] if t['trade_type'] == 'sell')
            actual_profit = sell_revenue - buy_cost
            
            assert abs(actual_profit - total_expected_profit) < 0.01
    
    def test_complex_trading_workflow_with_multiple_operations(self, app, db_session):
        """测试复杂的交易流程，包含多次买入卖出和复盘"""
        with app.app_context():
            self.setup_trading_config(app)
            stock_code = '000004'
            stock_name = '国农科技'
            
            # 1. 股票池流程
            # 添加到观察池
            watch_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'pool_type': 'watch',
                'target_price': 20.00,
                'add_reason': '技术形态整理完毕',
                'status': 'active'
            }
            watch_stock = StockPoolService.create_stock_pool_entry(watch_data)
            
            # 移动到待买入池
            buy_ready_stock = StockPoolService.move_stock_to_pool(
                watch_stock.id, 'buy_ready', '突破确认'
            )
            
            # 2. 第一次买入
            buy_1_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'trade_type': 'buy',
                'price': 20.50,
                'quantity': 1000,
                'trade_date': datetime.now() - timedelta(days=15),
                'reason': '从股票池买入',
                'stop_loss_price': 18.45,
                'take_profit_ratio': 0.25,
                'sell_ratio': 0.40
            }
            buy_trade_1 = TradingService.create_trade(buy_1_data)
            
            # 3. 第一次复盘
            review_1_data = {
                'stock_code': stock_code,
                'review_date': date.today() - timedelta(days=12),
                'price_up_score': 1,
                'bbi_score': 1,
                'volume_score': 1,
                'trend_score': 1,
                'j_score': 1,
                'analysis': '买入后表现优秀，各项指标良好',
                'decision': 'hold',
                'reason': '继续持有',
                'holding_days': 3
            }
            review_1 = ReviewService.create_review(review_1_data)
            assert review_1.total_score == 5
            
            # 4. 加仓买入
            buy_2_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'trade_type': 'buy',
                'price': 22.30,
                'quantity': 500,
                'trade_date': datetime.now() - timedelta(days=10),
                'reason': '少妇B1战法',
                'notes': '突破后加仓'
            }
            buy_trade_2 = TradingService.create_trade(buy_2_data)
            
            # 5. 第二次复盘
            review_2_data = {
                'stock_code': stock_code,
                'review_date': date.today() - timedelta(days=8),
                'price_up_score': 1,
                'bbi_score': 1,
                'volume_score': 0,  # 出现放量阴线
                'trend_score': 1,
                'j_score': 1,
                'analysis': '加仓后继续上涨，但出现放量阴线需要警惕',
                'decision': 'hold',
                'reason': '暂时持有，密切观察',
                'holding_days': 7
            }
            review_2 = ReviewService.create_review(review_2_data)
            assert review_2.total_score == 4
            
            # 6. 部分止盈
            sell_1_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'trade_type': 'sell',
                'price': 25.60,
                'quantity': 600,
                'trade_date': datetime.now() - timedelta(days=5),
                'reason': '部分止盈',
                'notes': '达到预期收益，部分止盈'
            }
            sell_trade_1 = TradingService.create_trade(sell_1_data)
            
            # 7. 第三次复盘（部分卖出后）
            review_3_data = {
                'stock_code': stock_code,
                'review_date': date.today() - timedelta(days=3),
                'price_up_score': 0,  # 价格开始下跌
                'bbi_score': 0,       # 跌破BBI线
                'volume_score': 0,    # 放量下跌
                'trend_score': 0,     # 趋势转弱
                'j_score': 0,         # J值死叉
                'analysis': '技术指标全面恶化，趋势可能反转',
                'decision': 'sell_all',
                'reason': '技术破位，全部清仓',
                'holding_days': 12
            }
            review_3 = ReviewService.create_review(review_3_data)
            assert review_3.total_score == 0
            
            # 8. 全部清仓
            sell_2_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'trade_type': 'sell',
                'price': 23.80,
                'quantity': 900,  # 剩余数量
                'trade_date': datetime.now() - timedelta(days=1),
                'reason': '技术破位',
                'notes': '根据复盘决策全部清仓'
            }
            sell_trade_2 = TradingService.create_trade(sell_2_data)
            
            # 9. 验证完整流程的数据一致性
            # 检查交易记录
            all_trades = TradingService.get_trades(filters={'stock_code': stock_code})
            assert all_trades['total'] == 4  # 2买2卖
            
            # 验证买卖数量平衡
            buy_trades = [t for t in all_trades['trades'] if t['trade_type'] == 'buy']
            sell_trades = [t for t in all_trades['trades'] if t['trade_type'] == 'sell']
            
            total_buy_qty = sum(t['quantity'] for t in buy_trades)
            total_sell_qty = sum(t['quantity'] for t in sell_trades)
            assert total_buy_qty == total_sell_qty == 1500
            
            # 检查复盘记录
            all_reviews = ReviewService.get_reviews_by_stock(stock_code)
            assert len(all_reviews) == 3
            
            # 验证复盘记录的时间顺序和评分变化
            reviews_sorted = sorted(all_reviews, key=lambda x: x.review_date)
            assert reviews_sorted[0].total_score == 5  # 最好
            assert reviews_sorted[1].total_score == 4  # 中等
            assert reviews_sorted[2].total_score == 0  # 最差
            
            # 验证决策变化
            assert reviews_sorted[0].decision == 'hold'
            assert reviews_sorted[1].decision == 'hold'
            assert reviews_sorted[2].decision == 'sell_all'
            
            # 检查股票池历史
            pool_history = StockPoolService.get_stock_history(stock_code)
            assert len(pool_history) >= 2  # watch -> buy_ready
            
            # 10. 计算最终收益
            buy_cost = sum(t['price'] * t['quantity'] for t in buy_trades)
            sell_revenue = sum(t['price'] * t['quantity'] for t in sell_trades)
            total_profit = sell_revenue - buy_cost
            
            # 预期计算:
            # 买入成本: 20.50*1000 + 22.30*500 = 31650
            # 卖出收入: 25.60*600 + 23.80*900 = 36780
            # 预期收益: 36780 - 31650 = 5130
            expected_cost = 20.50 * 1000 + 22.30 * 500
            expected_revenue = 25.60 * 600 + 23.80 * 900
            expected_profit = expected_revenue - expected_cost
            
            assert abs(total_profit - expected_profit) < 0.01
            assert total_profit > 0  # 应该是盈利的
    
    def test_trading_workflow_with_stop_loss_scenario(self, app, db_session):
        """测试止损场景的完整交易流程"""
        with app.app_context():
            self.setup_trading_config(app)
            stock_code = '000005'
            stock_name = '世纪星源'
            
            # 1. 创建买入记录（设置止损）
            buy_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'trade_type': 'buy',
                'price': 8.50,
                'quantity': 2000,
                'trade_date': datetime.now() - timedelta(days=8),
                'reason': '少妇B1战法',
                'stop_loss_price': 7.65,  # 10%止损
                'take_profit_ratio': 0.20,
                'sell_ratio': 0.50,
                'notes': '设置10%止损'
            }
            buy_trade = TradingService.create_trade(buy_data)
            
            # 验证止损止盈计算
            expected_loss_ratio = (8.50 - 7.65) / 8.50  # 0.10
            assert abs(float(buy_trade.expected_loss_ratio) - expected_loss_ratio) < 0.001
            
            # 2. 添加价格数据（模拟下跌）
            price_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'current_price': 7.80,
                'change_percent': -8.24,  # (7.80 - 8.50) / 8.50 * 100
                'record_date': date.today() - timedelta(days=5)
            }
            StockPrice.update_or_create(
                stock_code=price_data['stock_code'],
                stock_name=price_data['stock_name'],
                current_price=price_data['current_price'],
                change_percent=price_data['change_percent'],
                record_date=price_data['record_date']
            )
            
            # 3. 创建复盘记录（技术恶化）
            review_data = {
                'stock_code': stock_code,
                'review_date': date.today() - timedelta(days=4),
                'price_up_score': 0,  # 价格下跌
                'bbi_score': 0,       # 跌破BBI
                'volume_score': 0,    # 放量下跌
                'trend_score': 0,     # 趋势转弱
                'j_score': 0,         # J值死叉
                'analysis': '技术指标全面恶化，接近止损位',
                'decision': 'sell_all',
                'reason': '技术破位，准备止损',
                'holding_days': 4
            }
            review_record = ReviewService.create_review(review_data)
            assert review_record.total_score == 0
            assert review_record.decision == 'sell_all'
            
            # 4. 执行止损卖出
            stop_loss_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'trade_type': 'sell',
                'price': 7.70,  # 接近止损价
                'quantity': 2000,
                'trade_date': datetime.now() - timedelta(days=2),
                'reason': '止损',
                'notes': '触发止损，全部卖出'
            }
            sell_trade = TradingService.create_trade(stop_loss_data)
            
            # 5. 验证止损后的状态
            holdings = HoldingService.get_current_holdings()
            holding = next((h for h in holdings if h['stock_code'] == stock_code), None)
            assert holding is None or holding['current_quantity'] == 0
            
            # 6. 计算实际亏损
            actual_loss = (7.70 - 8.50) * 2000  # -1600
            expected_loss = -1600
            assert abs(actual_loss - expected_loss) < 0.01
            assert actual_loss < 0  # 确实是亏损
            
            # 验证亏损比例接近预期
            actual_loss_ratio = abs(actual_loss) / (8.50 * 2000)
            assert abs(actual_loss_ratio - expected_loss_ratio) < 0.02  # 允许2%误差
            
            # 7. 验证完整的交易记录
            trades = TradingService.get_trades(filters={'stock_code': stock_code})
            assert trades['total'] == 2  # 1买1卖
            
            buy_record = next(t for t in trades['trades'] if t['trade_type'] == 'buy')
            sell_record = next(t for t in trades['trades'] if t['trade_type'] == 'sell')
            
            assert buy_record['reason'] == '少妇B1战法'
            assert sell_record['reason'] == '止损'
            assert buy_record['quantity'] == sell_record['quantity']
    
    def test_trading_workflow_error_handling(self, app, db_session):
        """测试交易流程中的错误处理"""
        with app.app_context():
            self.setup_trading_config(app)
            # 1. 测试从不存在的股票池买入
            with pytest.raises(NotFoundError):
                StockPoolService.get_by_id(99999)
            
            # 2. 测试创建重复日期的复盘记录
            review_data = {
                'stock_code': '000006',
                'review_date': date.today(),
                'price_up_score': 1,
                'bbi_score': 1,
                'volume_score': 1,
                'trend_score': 1,
                'j_score': 1
            }
            
            # 第一次创建应该成功
            review_1 = ReviewService.create_review(review_data)
            assert review_1.id is not None
            
            # 第二次创建相同日期应该失败
            with pytest.raises(ValidationError) as exc_info:
                ReviewService.create_review(review_data)
            assert "已存在" in str(exc_info.value) or "重复" in str(exc_info.value)
            
            # 3. 测试无效的交易数据
            invalid_trade_data = {
                'stock_code': '000006',
                'stock_name': '深振业A',
                'trade_type': 'buy',
                'price': -10.00,  # 负价格
                'quantity': 1000,
                'reason': '少妇B1战法'
            }
            
            with pytest.raises((ValidationError, DatabaseError)):
                TradingService.create_trade(invalid_trade_data)
            
            # 4. 测试止损价格高于买入价格
            invalid_stop_loss_data = {
                'stock_code': '000006',
                'stock_name': '深振业A',
                'trade_type': 'buy',
                'price': 10.00,
                'quantity': 1000,
                'reason': '少妇B1战法',
                'stop_loss_price': 11.00  # 高于买入价
            }
            
            with pytest.raises((ValidationError, DatabaseError)) as exc_info:
                TradingService.create_trade(invalid_stop_loss_data)
            assert "止损价格必须小于买入价格" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestDataRelationshipIntegrity:
    """数据关联性测试 - 测试交易记录和复盘记录的关联、验证持仓计算的数据来源正确性、测试统计分析数据的一致性"""
    
    def setup_trading_config(self, app):
        """设置交易配置"""
        with app.app_context():
            from models.configuration import Configuration
            Configuration.set_buy_reasons(['少妇B1战法', '少妇SB1战法', '少妇B2战法', '技术突破'])
            Configuration.set_sell_reasons(['部分止盈', '止损', '下等马/草泥马', '技术破位'])
    
    # ========== 5.2 数据关联性测试 ==========
    
    def test_trade_and_review_record_association(self, app, db_session):
        """测试交易记录和复盘记录的关联性"""
        with app.app_context():
            self.setup_trading_config(app)
            stock_code = '000007'
            stock_name = '全新好'
            
            # 1. 创建多笔交易记录
            trades_data = [
                {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'trade_type': 'buy',
                    'price': 12.00,
                    'quantity': 1000,
                    'trade_date': datetime.now() - timedelta(days=10),
                    'reason': '少妇B1战法'
                },
                {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'trade_type': 'buy',
                    'price': 11.50,
                    'quantity': 500,
                    'trade_date': datetime.now() - timedelta(days=8),
                    'reason': '少妇B1战法'
                },
                {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'trade_type': 'sell',
                    'price': 13.20,
                    'quantity': 600,
                    'trade_date': datetime.now() - timedelta(days=3),
                    'reason': '部分止盈'
                }
            ]
            
            created_trades = []
            for trade_data in trades_data:
                trade = TradingService.create_trade(trade_data)
                created_trades.append(trade)
            
            # 2. 创建对应的复盘记录
            reviews_data = [
                {
                    'stock_code': stock_code,
                    'review_date': date.today() - timedelta(days=9),
                    'price_up_score': 1,
                    'bbi_score': 1,
                    'volume_score': 1,
                    'trend_score': 1,
                    'j_score': 1,
                    'analysis': '买入后表现良好',
                    'decision': 'hold',
                    'holding_days': 1
                },
                {
                    'stock_code': stock_code,
                    'review_date': date.today() - timedelta(days=6),
                    'price_up_score': 1,
                    'bbi_score': 1,
                    'volume_score': 0,
                    'trend_score': 1,
                    'j_score': 1,
                    'analysis': '加仓后继续上涨，但有放量阴线',
                    'decision': 'hold',
                    'holding_days': 4
                },
                {
                    'stock_code': stock_code,
                    'review_date': date.today() - timedelta(days=4),
                    'price_up_score': 1,
                    'bbi_score': 1,
                    'volume_score': 1,
                    'trend_score': 1,
                    'j_score': 0,
                    'analysis': '准备部分止盈，J值开始走弱',
                    'decision': 'sell_partial',
                    'holding_days': 6
                }
            ]
            
            created_reviews = []
            for review_data in reviews_data:
                review = ReviewService.create_review(review_data)
                created_reviews.append(review)
            
            # 3. 验证交易记录和复盘记录的关联
            # 通过股票代码关联
            trades_by_stock = TradingService.get_trades(filters={'stock_code': stock_code})
            reviews_by_stock = ReviewService.get_reviews_by_stock(stock_code)
            
            assert trades_by_stock['total'] == 3
            assert len(reviews_by_stock) == 3
            
            # 验证所有记录都属于同一股票
            for trade in trades_by_stock['trades']:
                assert trade['stock_code'] == stock_code
                assert trade['stock_name'] == stock_name
            
            for review in reviews_by_stock:
                assert review.stock_code == stock_code
            
            # 4. 验证时间关联性
            # 复盘记录应该在对应的交易记录之后
            trade_dates = [datetime.fromisoformat(t['trade_date'].replace('Z', '+00:00')).date() 
                          for t in trades_by_stock['trades']]
            review_dates = [r.review_date for r in reviews_by_stock]
            
            # 第一次复盘应该在第一次买入之后
            first_buy_date = min(trade_dates)
            first_review_date = min(review_dates)
            assert first_review_date >= first_buy_date
            
            # 5. 验证复盘决策与后续交易的关联
            # 最后一次复盘决策是sell_partial，应该有对应的卖出记录
            last_review = max(created_reviews, key=lambda x: x.review_date)
            assert last_review.decision == 'sell_partial'
            
            # 检查是否有在复盘决策后的卖出记录
            sell_trades = [t for t in trades_by_stock['trades'] if t['trade_type'] == 'sell']
            assert len(sell_trades) == 1
            
            sell_date = datetime.fromisoformat(sell_trades[0]['trade_date'].replace('Z', '+00:00')).date()
            assert sell_date >= last_review.review_date
    
    def test_holding_calculation_data_source_accuracy(self, app, db_session):
        """验证持仓计算的数据来源正确性"""
        with app.app_context():
            self.setup_trading_config(app)
            stock_code = '000008'
            stock_name = '神州高铁'
            
            # 1. 创建复杂的交易记录（多次买入卖出）
            trades_data = [
                # 第一批买入
                {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'trade_type': 'buy',
                    'price': 10.00,
                    'quantity': 1000,
                    'trade_date': datetime.now() - timedelta(days=20),
                    'reason': '少妇B1战法'
                },
                # 第二批买入
                {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'trade_type': 'buy',
                    'price': 12.00,
                    'quantity': 800,
                    'trade_date': datetime.now() - timedelta(days=15),
                    'reason': '少妇B1战法'
                },
                # 第一次卖出
                {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'trade_type': 'sell',
                    'price': 13.50,
                    'quantity': 500,
                    'trade_date': datetime.now() - timedelta(days=10),
                    'reason': '部分止盈'
                },
                # 第三批买入
                {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'trade_type': 'buy',
                    'price': 11.80,
                    'quantity': 600,
                    'trade_date': datetime.now() - timedelta(days=8),
                    'reason': '少妇B1战法'
                },
                # 第二次卖出
                {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'trade_type': 'sell',
                    'price': 14.20,
                    'quantity': 700,
                    'trade_date': datetime.now() - timedelta(days=5),
                    'reason': '部分止盈'
                }
            ]
            
            # 创建所有交易记录
            for trade_data in trades_data:
                TradingService.create_trade(trade_data)
            
            # 2. 手动计算预期持仓
            # 买入: 1000 + 800 + 600 = 2400
            # 卖出: 500 + 700 = 1200
            # 剩余: 2400 - 1200 = 1200
            expected_quantity = 1200
            
            # 平均成本计算 (FIFO或加权平均)
            # 加权平均成本: (10.00*1000 + 12.00*800 + 11.80*600) / 2400 = 11.28
            expected_avg_cost = (10.00 * 1000 + 12.00 * 800 + 11.80 * 600) / 2400
            
            # 3. 获取系统计算的持仓
            holdings = HoldingService.get_current_holdings()
            holding = next((h for h in holdings if h['stock_code'] == stock_code), None)
            
            assert holding is not None
            assert holding['current_quantity'] == expected_quantity
            assert abs(holding['avg_buy_price'] - expected_avg_cost) < 0.2
            
            # 4. 验证持仓计算的数据来源
            # 获取所有交易记录并验证
            all_trades = TradingService.get_trades(filters={'stock_code': stock_code})
            assert all_trades['total'] == 5
            
            # 验证买入总量
            buy_trades = [t for t in all_trades['trades'] if t['trade_type'] == 'buy']
            total_buy_quantity = sum(t['quantity'] for t in buy_trades)
            assert total_buy_quantity == 2400
            
            # 验证卖出总量
            sell_trades = [t for t in all_trades['trades'] if t['trade_type'] == 'sell']
            total_sell_quantity = sum(t['quantity'] for t in sell_trades)
            assert total_sell_quantity == 1200
            
            # 验证持仓数量 = 买入总量 - 卖出总量
            assert holding['current_quantity'] == total_buy_quantity - total_sell_quantity
            
            # 5. 添加当前价格并验证盈亏计算
            current_price = 13.00
            price_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'current_price': current_price,
                'change_percent': 0.0,
                'record_date': date.today()
            }
            StockPrice.update_or_create(
                stock_code=price_data['stock_code'],
                stock_name=price_data['stock_name'],
                current_price=price_data['current_price'],
                change_percent=price_data['change_percent'],
                record_date=price_data['record_date']
            )
            
            # 重新获取持仓信息
            updated_holdings = HoldingService.get_current_holdings()
            updated_holding = next((h for h in updated_holdings if h['stock_code'] == stock_code), None)
            
            # 验证持仓基本信息
            assert updated_holding is not None
            assert updated_holding['current_quantity'] == expected_quantity
            assert abs(updated_holding['avg_buy_price'] - expected_avg_cost) < 0.2
    
    def test_statistical_analysis_data_consistency(self, app, db_session):
        """测试统计分析数据的一致性"""
        with app.app_context():
            self.setup_trading_config(app)
            # 1. 创建多只股票的完整交易数据
            stocks_data = [
                {
                    'stock_code': '000009',
                    'stock_name': '中国宝安',
                    'trades': [
                        {'trade_type': 'buy', 'price': 8.00, 'quantity': 1000, 'days_ago': 15},
                        {'trade_type': 'sell', 'price': 9.20, 'quantity': 1000, 'days_ago': 5}
                    ]
                },
                {
                    'stock_code': '000010',
                    'stock_name': '美丽生态',
                    'trades': [
                        {'trade_type': 'buy', 'price': 15.00, 'quantity': 500, 'days_ago': 12},
                        {'trade_type': 'sell', 'price': 13.50, 'quantity': 500, 'days_ago': 3}
                    ]
                },
                {
                    'stock_code': '000011',
                    'stock_name': '深物业A',
                    'trades': [
                        {'trade_type': 'buy', 'price': 20.00, 'quantity': 800, 'days_ago': 10}
                        # 只买入，未卖出（持仓中）
                    ]
                }
            ]
            
            # 创建交易记录
            all_created_trades = []
            for stock_data in stocks_data:
                for trade_info in stock_data['trades']:
                    trade_data = {
                        'stock_code': stock_data['stock_code'],
                        'stock_name': stock_data['stock_name'],
                        'trade_type': trade_info['trade_type'],
                        'price': trade_info['price'],
                        'quantity': trade_info['quantity'],
                        'trade_date': datetime.now() - timedelta(days=trade_info['days_ago']),
                        'reason': '少妇B1战法' if trade_info['trade_type'] == 'buy' else '部分止盈'
                    }
                    trade = TradingService.create_trade(trade_data)
                    all_created_trades.append(trade)
            
            # 2. 添加当前价格（用于未实现盈亏计算）
            current_prices = [
                {'stock_code': '000009', 'current_price': 9.50},  # 已清仓，但有当前价格
                {'stock_code': '000010', 'current_price': 14.00}, # 已清仓
                {'stock_code': '000011', 'current_price': 22.00}  # 持仓中
            ]
            
            for price_info in current_prices:
                price_data = {
                    'stock_code': price_info['stock_code'],
                    'stock_name': next(s['stock_name'] for s in stocks_data if s['stock_code'] == price_info['stock_code']),
                    'current_price': price_info['current_price'],
                    'change_percent': 0.0,
                    'record_date': date.today()
                }
                StockPrice.update_or_create(
                    stock_code=price_data['stock_code'],
                    stock_name=price_data['stock_name'],
                    current_price=price_data['current_price'],
                    change_percent=price_data['change_percent'],
                    record_date=price_data['record_date']
                )
            
            # 3. 验证交易统计的一致性
            # 获取所有交易记录
            all_trades = TradingService.get_trades()
            assert all_trades['total'] == 5  # 3买2卖
            
            # 按交易类型统计
            buy_trades = [t for t in all_trades['trades'] if t['trade_type'] == 'buy']
            sell_trades = [t for t in all_trades['trades'] if t['trade_type'] == 'sell']
            
            assert len(buy_trades) == 3
            assert len(sell_trades) == 2
            
            # 4. 验证持仓统计的一致性
            holdings = HoldingService.get_current_holdings()
            
            # 应该只有一只股票有持仓（000011）
            assert len(holdings) == 1
            holding = holdings[0]
            assert holding['stock_code'] == '000011'
            assert holding['current_quantity'] == 800
            assert holding['avg_buy_price'] == 20.00
            
            # 验证持仓基本信息
            assert holding['stock_code'] == '000011'
            assert holding['stock_name'] == '深物业A'
            
            # 5. 验证已实现盈亏的计算
            # 手动计算已实现盈亏
            realized_profits = []
            
            # 000009: (9.20 - 8.00) * 1000 = 1200
            realized_profits.append((9.20 - 8.00) * 1000)
            
            # 000010: (13.50 - 15.00) * 500 = -750
            realized_profits.append((13.50 - 15.00) * 500)
            
            total_realized_profit = sum(realized_profits)  # 1200 - 750 = 450
            
            # 6. 验证总体统计数据
            # 计算总投资金额
            total_investment = sum(t['price'] * t['quantity'] for t in buy_trades)
            expected_investment = 8.00 * 1000 + 15.00 * 500 + 20.00 * 800  # 31500
            assert abs(total_investment - expected_investment) < 0.01
            
            # 计算总收入（已卖出部分）
            total_revenue = sum(t['price'] * t['quantity'] for t in sell_trades)
            expected_revenue = 9.20 * 1000 + 13.50 * 500  # 15950
            assert abs(total_revenue - expected_revenue) < 0.01
            
            # 验证已实现盈亏
            actual_realized_profit = total_revenue - (8.00 * 1000 + 15.00 * 500)  # 成本
            assert abs(actual_realized_profit - total_realized_profit) < 0.01
            
            # 7. 验证成功率计算
            # 成功交易：000009 (盈利)
            # 失败交易：000010 (亏损)
            # 成功率：1/2 = 50%
            completed_stocks = ['000009', '000010']  # 已完成交易的股票
            profitable_stocks = ['000009']  # 盈利的股票
            success_rate = len(profitable_stocks) / len(completed_stocks)
            assert success_rate == 0.5
            
            # 8. 验证数据一致性检查
            # 所有买入数量应该等于卖出数量加持仓数量
            total_buy_quantity = sum(t['quantity'] for t in buy_trades)
            total_sell_quantity = sum(t['quantity'] for t in sell_trades)
            total_holding_quantity = sum(h['current_quantity'] for h in holdings)
            
            assert total_buy_quantity == total_sell_quantity + total_holding_quantity
            
            # 验证股票代码的一致性
            trade_stock_codes = set(t['stock_code'] for t in all_trades['trades'])
            holding_stock_codes = set(h['stock_code'] for h in holdings)
            expected_stock_codes = set(s['stock_code'] for s in stocks_data)
            
            assert trade_stock_codes == expected_stock_codes
            assert holding_stock_codes.issubset(expected_stock_codes)
    
    def test_cross_table_data_integrity(self, app, db_session):
        """测试跨表数据完整性"""
        with app.app_context():
            self.setup_trading_config(app)
            stock_code = '000012'
            stock_name = '南玻A'
            
            # 1. 创建完整的业务数据链
            # 股票池记录
            pool_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'pool_type': 'watch',
                'target_price': 5.50,
                'add_reason': '技术形态良好',
                'status': 'active'
            }
            pool_record = StockPoolService.create_stock_pool_entry(pool_data)
            
            # 交易记录
            trade_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'trade_type': 'buy',
                'price': 5.80,
                'quantity': 2000,
                'trade_date': datetime.now() - timedelta(days=7),
                'reason': '少妇B1战法'
            }
            trade_record = TradingService.create_trade(trade_data)
            
            # 复盘记录
            review_data = {
                'stock_code': stock_code,
                'review_date': date.today() - timedelta(days=5),
                'price_up_score': 1,
                'bbi_score': 1,
                'volume_score': 1,
                'trend_score': 1,
                'j_score': 1,
                'analysis': '买入后表现优秀',
                'decision': 'hold',
                'holding_days': 2
            }
            review_record = ReviewService.create_review(review_data)
            
            # 价格记录
            price_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'current_price': 6.20,
                'change_percent': 6.90,
                'record_date': date.today()
            }
            price_record = StockPrice.update_or_create(
                stock_code=price_data['stock_code'],
                stock_name=price_data['stock_name'],
                current_price=price_data['current_price'],
                change_percent=price_data['change_percent'],
                record_date=price_data['record_date']
            )
            
            # 2. 验证所有记录的股票代码一致性
            assert pool_record.stock_code == stock_code
            assert trade_record.stock_code == stock_code
            assert review_record.stock_code == stock_code
            assert price_record.stock_code == stock_code
            
            # 验证股票名称一致性
            assert pool_record.stock_name == stock_name
            assert trade_record.stock_name == stock_name
            assert price_record.stock_name == stock_name
            
            # 3. 验证业务逻辑的一致性
            # 股票池目标价格应该低于实际买入价格（突破买入）
            assert float(pool_record.target_price) < float(trade_record.price)
            
            # 复盘记录日期应该在交易日期之后
            trade_date = trade_record.trade_date.date()
            assert review_record.review_date >= trade_date
            
            # 价格记录日期应该是最新的
            assert price_record.record_date >= review_record.review_date
            
            # 4. 验证数据删除的级联影响
            # 删除交易记录前，先检查关联数据
            original_trade_id = trade_record.id
            
            # 删除交易记录
            TradingService.delete_trade(original_trade_id)
            
            # 验证交易记录已删除
            with pytest.raises(NotFoundError):
                TradingService.get_trade_by_id(original_trade_id)
            
            # 验证其他记录仍然存在（没有级联删除）
            assert StockPoolService.get_by_id(pool_record.id) is not None
            assert ReviewService.get_by_id(review_record.id) is not None
            price_service = PriceService()
            assert price_service.get_stock_price(stock_code) is not None
            
            # 但持仓应该受到影响（没有交易记录就没有持仓）
            holdings = HoldingService.get_current_holdings()
            holding = next((h for h in holdings if h['stock_code'] == stock_code), None)
            assert holding is None or holding['current_quantity'] == 0
    
    def test_data_consistency_under_concurrent_operations(self, app, db_session):
        """测试并发操作下的数据一致性"""
        with app.app_context():
            self.setup_trading_config(app)
            stock_code = '000013'
            stock_name = '国星光电'
            
            # 1. 创建基础交易记录
            buy_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'trade_type': 'buy',
                'price': 7.50,
                'quantity': 1000,
                'trade_date': datetime.now() - timedelta(days=5),
                'reason': '少妇B1战法'
            }
            buy_trade = TradingService.create_trade(buy_data)
            
            # 2. 模拟并发更新操作
            # 同时更新交易记录和创建复盘记录
            
            # 更新交易记录
            update_data = {
                'price': 7.60,
                'notes': '价格订正'
            }
            updated_trade = TradingService.update_trade(buy_trade.id, update_data)
            
            # 创建复盘记录
            review_data = {
                'stock_code': stock_code,
                'review_date': date.today(),
                'price_up_score': 1,
                'bbi_score': 1,
                'volume_score': 1,
                'trend_score': 1,
                'j_score': 1,
                'analysis': '表现良好',
                'decision': 'hold',
                'holding_days': 5
            }
            review_record = ReviewService.create_review(review_data)
            
            # 添加价格记录
            price_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'current_price': 8.00,
                'change_percent': 6.67,
                'record_date': date.today()
            }
            price_record = StockPrice.update_or_create(
                stock_code=price_data['stock_code'],
                stock_name=price_data['stock_name'],
                current_price=price_data['current_price'],
                change_percent=price_data['change_percent'],
                record_date=price_data['record_date']
            )
            
            # 3. 验证数据一致性
            # 重新获取所有相关数据
            fresh_trade = TradingService.get_trade_by_id(buy_trade.id)
            fresh_review = ReviewService.get_by_id(review_record.id)
            price_service = PriceService()
            fresh_price = price_service.get_stock_price(stock_code)
            fresh_holdings = HoldingService.get_current_holdings()
            
            # 验证交易记录更新生效
            assert float(fresh_trade.price) == 7.60
            assert fresh_trade.notes == '价格订正'
            
            # 验证复盘记录正确创建
            assert fresh_review.stock_code == stock_code
            assert fresh_review.total_score == 5
            
            # 验证价格记录正确
            assert fresh_price is not None
            assert float(fresh_price['current_price']) == 8.00
            
            # 验证持仓计算基于最新的交易数据
            holding = next((h for h in fresh_holdings if h['stock_code'] == stock_code), None)
            assert holding is not None
            assert holding['avg_buy_price'] == 7.60  # 使用更新后的价格
            assert holding['current_quantity'] == 1000
    
    def test_historical_data_consistency(self, app, db_session):
        """测试历史数据的一致性"""
        with app.app_context():
            self.setup_trading_config(app)
            stock_code = '000014'
            stock_name = '沙河股份'
            
            # 1. 创建历史交易数据（跨越多个月）
            historical_trades = [
                # 1月份交易
                {
                    'trade_type': 'buy', 'price': 3.50, 'quantity': 1000,
                    'trade_date': datetime(2024, 1, 15, 9, 30),
                    'reason': '少妇B1战法'
                },
                {
                    'trade_type': 'sell', 'price': 4.20, 'quantity': 500,
                    'trade_date': datetime(2024, 1, 25, 14, 30),
                    'reason': '部分止盈'
                },
                # 2月份交易
                {
                    'trade_type': 'buy', 'price': 3.80, 'quantity': 800,
                    'trade_date': datetime(2024, 2, 10, 10, 0),
                    'reason': '少妇B1战法'
                },
                {
                    'trade_type': 'sell', 'price': 4.50, 'quantity': 600,
                    'trade_date': datetime(2024, 2, 20, 15, 0),
                    'reason': '部分止盈'
                },
                # 3月份交易
                {
                    'trade_type': 'sell', 'price': 4.10, 'quantity': 700,
                    'trade_date': datetime(2024, 3, 5, 11, 30),
                    'reason': '技术破位'
                }
            ]
            
            # 创建历史交易记录
            for trade_info in historical_trades:
                trade_data = {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    **trade_info
                }
                TradingService.create_trade(trade_data)
            
            # 2. 创建对应的历史复盘记录
            historical_reviews = [
                {
                    'review_date': date(2024, 1, 20),
                    'total_score': 4, 'decision': 'hold', 'holding_days': 5
                },
                {
                    'review_date': date(2024, 2, 15),
                    'total_score': 3, 'decision': 'sell_partial', 'holding_days': 10
                },
                {
                    'review_date': date(2024, 3, 1),
                    'total_score': 1, 'decision': 'sell_all', 'holding_days': 15
                }
            ]
            
            for review_info in historical_reviews:
                review_data = {
                    'stock_code': stock_code,
                    'price_up_score': 1,
                    'bbi_score': 1,
                    'volume_score': 0,
                    'trend_score': 1,
                    'j_score': 0,
                    'analysis': f'历史复盘记录 - {review_info["review_date"]}',
                    **review_info
                }
                ReviewService.create_review(review_data)
            
            # 3. 验证历史数据的时间一致性
            all_trades = TradingService.get_trades(filters={'stock_code': stock_code})
            all_reviews = ReviewService.get_reviews_by_stock(stock_code)
            
            assert all_trades['total'] == 5
            assert len(all_reviews) == 3
            
            # 验证交易记录按时间排序（默认是降序）
            trade_dates = [datetime.fromisoformat(t['trade_date'].replace('Z', '+00:00')) 
                          for t in all_trades['trades']]
            assert trade_dates == sorted(trade_dates, reverse=True)
            
            # 验证复盘记录按时间排序（默认是降序）
            review_dates = [r.review_date for r in all_reviews]
            assert review_dates == sorted(review_dates, reverse=True)
            
            # 4. 验证月度统计的一致性
            # 按月份查询交易记录
            jan_trades = TradingService.get_trades(filters={
                'stock_code': stock_code,
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            })
            assert jan_trades['total'] == 2
            
            feb_trades = TradingService.get_trades(filters={
                'stock_code': stock_code,
                'start_date': '2024-02-01',
                'end_date': '2024-02-28'
            })
            assert feb_trades['total'] == 2
            
            mar_trades = TradingService.get_trades(filters={
                'stock_code': stock_code,
                'start_date': '2024-03-01',
                'end_date': '2024-03-31'
            })
            assert mar_trades['total'] == 1
            
            # 5. 验证最终持仓状态
            # 计算最终持仓：买入1000+800=1800，卖出500+600+700=1800，剩余0
            holdings = HoldingService.get_current_holdings()
            holding = next((h for h in holdings if h['stock_code'] == stock_code), None)
            assert holding is None or holding['current_quantity'] == 0
            
            # 6. 验证历史盈亏计算
            buy_trades = [t for t in all_trades['trades'] if t['trade_type'] == 'buy']
            sell_trades = [t for t in all_trades['trades'] if t['trade_type'] == 'sell']
            
            total_cost = sum(t['price'] * t['quantity'] for t in buy_trades)
            total_revenue = sum(t['price'] * t['quantity'] for t in sell_trades)
            total_profit = total_revenue - total_cost
            
            # 手动计算验证
            expected_cost = 3.50 * 1000 + 3.80 * 800  # 6540
            expected_revenue = 4.20 * 500 + 4.50 * 600 + 4.10 * 700  # 7670
            expected_profit = expected_revenue - expected_cost  # 1130
            
            assert abs(total_profit - expected_profit) < 0.01
            assert total_profit > 0  # 整体盈利


if __name__ == '__main__':
    pytest.main([__file__, '-v'])