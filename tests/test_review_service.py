"""
复盘记录和持仓管理服务测试
"""
import pytest
from datetime import date, datetime, timedelta
from services.review_service import ReviewService, HoldingService
from models.review_record import ReviewRecord
from models.trade_record import TradeRecord
from error_handlers import ValidationError, NotFoundError, DatabaseError


class TestReviewService:
    """复盘记录服务测试"""
    
    def test_create_review_success(self, app, db_session):
        """测试成功创建复盘记录"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 0,
            'trend_score': 1,
            'j_score': 0,
            'analysis': '今日表现良好',
            'decision': 'hold',
            'reason': '继续观察',
            'holding_days': 5
        }
        
        review = ReviewService.create_review(review_data)
        
        assert review.id is not None
        assert review.stock_code == '000001'
        assert review.review_date == date(2024, 1, 15)
        assert review.total_score == 3  # 1+1+0+1+0
        assert review.analysis == '今日表现良好'
        assert review.decision == 'hold'
        assert review.holding_days == 5
    
    def test_create_review_missing_required_fields(self, app, db_session):
        """测试创建复盘记录缺少必填字段"""
        review_data = {
            'price_up_score': 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ReviewService.create_review(review_data)
        
        assert "stock_code不能为空" in str(exc_info.value)
    
    def test_create_review_invalid_date_format(self, app, db_session):
        """测试创建复盘记录日期格式错误"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024/01/15',  # 错误格式
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ReviewService.create_review(review_data)
        
        assert "复盘日期格式不正确" in str(exc_info.value)
    
    def test_create_review_duplicate_stock_date(self, app, db_session):
        """测试创建重复股票和日期的复盘记录"""
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1
        }
        
        # 创建第一个记录
        ReviewService.create_review(review_data)
        
        # 尝试创建重复记录
        with pytest.raises(ValidationError) as exc_info:
            ReviewService.create_review(review_data)
        
        assert "已存在复盘记录" in str(exc_info.value)
    
    def test_update_review_success(self, app, db_session):
        """测试成功更新复盘记录"""
        # 创建初始记录
        review_data = {
            'stock_code': '000001',
            'review_date': '2024-01-15',
            'price_up_score': 1,
            'bbi_score': 0
        }
        review = ReviewService.create_review(review_data)
        
        # 更新记录
        update_data = {
            'bbi_score': 1,
            'analysis': '更新后的分析',
            'decision': 'sell_partial'
        }
        updated_review = ReviewService.update_review(review.id, update_data)
        
        assert updated_review.bbi_score == 1
        assert updated_review.total_score == 2  # 1+1+0+0+0
        assert updated_review.analysis == '更新后的分析'
        assert updated_review.decision == 'sell_partial'
    
    def test_update_review_not_found(self, app, db_session):
        """测试更新不存在的复盘记录"""
        with pytest.raises(NotFoundError):
            ReviewService.update_review(999, {'analysis': '测试'})
    
    def test_get_reviews_with_filters(self, app, db_session):
        """测试带筛选条件获取复盘记录"""
        # 创建测试数据
        reviews_data = [
            {
                'stock_code': '000001',
                'review_date': '2024-01-15',
                'price_up_score': 1,
                'bbi_score': 1,
                'decision': 'hold',
                'holding_days': 5
            },
            {
                'stock_code': '000002',
                'review_date': '2024-01-16',
                'price_up_score': 0,
                'bbi_score': 0,
                'decision': 'sell_all',
                'holding_days': 10
            },
            {
                'stock_code': '000001',
                'review_date': '2024-01-17',
                'price_up_score': 1,
                'bbi_score': 1,
                'decision': 'hold',
                'holding_days': 6
            }
        ]
        
        for data in reviews_data:
            ReviewService.create_review(data)
        
        # 测试按股票代码筛选
        result = ReviewService.get_reviews({'stock_code': '000001'})
        assert len(result['reviews']) == 2
        
        # 测试按决策筛选
        result = ReviewService.get_reviews({'decision': 'hold'})
        assert len(result['reviews']) == 2
        
        # 测试按评分筛选
        result = ReviewService.get_reviews({'min_score': 2})
        assert len(result['reviews']) == 2
        
        # 测试按持仓天数筛选
        result = ReviewService.get_reviews({'holding_days_min': 6})
        assert len(result['reviews']) == 2
    
    def test_get_reviews_with_pagination(self, app, db_session):
        """测试分页获取复盘记录"""
        # 创建5条测试数据
        for i in range(5):
            review_data = {
                'stock_code': f'00000{i+1}',
                'review_date': f'2024-01-{15+i:02d}',
                'price_up_score': 1
            }
            ReviewService.create_review(review_data)
        
        # 测试分页
        result = ReviewService.get_reviews(page=1, per_page=2)
        
        assert len(result['reviews']) == 2
        assert result['pagination']['page'] == 1
        assert result['pagination']['per_page'] == 2
        assert result['pagination']['total'] == 5
        assert result['pagination']['pages'] == 3
    
    def test_get_reviews_by_stock(self, app, db_session):
        """测试获取某股票的所有复盘记录"""
        # 创建测试数据
        stock_code = '000001'
        for i in range(3):
            review_data = {
                'stock_code': stock_code,
                'review_date': f'2024-01-{15+i:02d}',
                'price_up_score': 1
            }
            ReviewService.create_review(review_data)
        
        # 创建其他股票的记录
        ReviewService.create_review({
            'stock_code': '000002',
            'review_date': '2024-01-20',
            'price_up_score': 1
        })
        
        reviews = ReviewService.get_reviews_by_stock(stock_code)
        
        assert len(reviews) == 3
        for review in reviews:
            assert review.stock_code == stock_code
    
    def test_get_latest_review_by_stock(self, app, db_session):
        """测试获取某股票最新的复盘记录"""
        stock_code = '000001'
        
        # 创建多条记录
        dates = ['2024-01-15', '2024-01-17', '2024-01-16']
        for i, date_str in enumerate(dates):
            review_data = {
                'stock_code': stock_code,
                'review_date': date_str,
                'price_up_score': 1 if i % 2 == 0 else 0,  # 确保评分值为0或1
                'analysis': f'分析{i}'
            }
            ReviewService.create_review(review_data)
        
        latest_review = ReviewService.get_latest_review_by_stock(stock_code)
        
        assert latest_review is not None
        assert latest_review.review_date == date(2024, 1, 17)  # 最新日期
        assert latest_review.analysis == '分析1'


class TestHoldingService:
    """持仓管理服务测试"""
    
    def test_get_current_holdings_empty(self, app, db_session):
        """测试获取空持仓列表"""
        holdings = HoldingService.get_current_holdings()
        assert holdings == []
    
    def test_get_current_holdings_with_data(self, app, db_session):
        """测试获取有数据的持仓列表"""
        # 创建买入记录
        buy_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime(2024, 1, 10),
            'reason': '买入原因'
        }
        TradeRecord(**buy_data).save()
        
        # 创建部分卖出记录
        sell_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'sell',
            'price': 13.00,
            'quantity': 300,
            'trade_date': datetime(2024, 1, 15),
            'reason': '部分止盈'
        }
        TradeRecord(**sell_data).save()
        
        # 创建复盘记录
        review_data = {
            'stock_code': '000001',
            'review_date': date.today(),
            'holding_days': 8,
            'price_up_score': 1
        }
        ReviewService.create_review(review_data)
        
        holdings = HoldingService.get_current_holdings()
        
        assert len(holdings) == 1
        holding = holdings[0]
        assert holding['stock_code'] == '000001'
        assert holding['stock_name'] == '平安银行'
        assert holding['current_quantity'] == 700  # 1000 - 300
        assert holding['total_buy_quantity'] == 1000
        assert holding['total_sell_quantity'] == 300
        assert holding['avg_buy_price'] == 12.50
        assert holding['holding_days'] == 8
        assert holding['latest_review'] is not None
    
    def test_get_current_holdings_fully_sold(self, app, db_session):
        """测试完全卖出的股票不在持仓列表中"""
        # 创建买入记录
        buy_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime(2024, 1, 10),
            'reason': '买入原因'
        }
        TradeRecord(**buy_data).save()
        
        # 创建完全卖出记录
        sell_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'sell',
            'price': 13.00,
            'quantity': 1000,
            'trade_date': datetime(2024, 1, 15),
            'reason': '清仓'
        }
        TradeRecord(**sell_data).save()
        
        holdings = HoldingService.get_current_holdings()
        assert holdings == []
    
    def test_get_holding_by_stock(self, app, db_session):
        """测试获取特定股票的持仓信息"""
        # 创建买入记录
        buy_data = {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'trade_type': 'buy',
            'price': 12.50,
            'quantity': 1000,
            'trade_date': datetime(2024, 1, 10),
            'reason': '买入原因'
        }
        TradeRecord(**buy_data).save()
        
        holding = HoldingService.get_holding_by_stock('000001')
        
        assert holding is not None
        assert holding['stock_code'] == '000001'
        assert holding['current_quantity'] == 1000
        
        # 测试不存在的股票
        holding = HoldingService.get_holding_by_stock('999999')
        assert holding is None
    
    def test_update_holding_days_new_review(self, app, db_session):
        """测试更新持仓天数（创建新复盘记录）"""
        stock_code = '000001'
        holding_days = 10
        
        result = HoldingService.update_holding_days(stock_code, holding_days)
        
        assert result['stock_code'] == stock_code
        assert result['holding_days'] == holding_days
        assert result['review_date'] == date.today().isoformat()  # 比较ISO格式字符串
        
        # 验证数据库中的记录
        review = ReviewService.get_review_by_stock_and_date(stock_code, date.today())
        assert review is not None
        assert review.holding_days == holding_days
    
    def test_update_holding_days_existing_review(self, app, db_session):
        """测试更新持仓天数（更新现有复盘记录）"""
        stock_code = '000001'
        today = date.today()
        
        # 创建现有复盘记录
        review_data = {
            'stock_code': stock_code,
            'review_date': today,
            'holding_days': 5,
            'price_up_score': 1
        }
        ReviewService.create_review(review_data)
        
        # 更新持仓天数
        new_holding_days = 8
        result = HoldingService.update_holding_days(stock_code, new_holding_days)
        
        assert result['holding_days'] == new_holding_days
        
        # 验证数据库中的记录被更新
        review = ReviewService.get_review_by_stock_and_date(stock_code, today)
        assert review.holding_days == new_holding_days
    
    def test_update_holding_days_invalid(self, app, db_session):
        """测试更新无效的持仓天数"""
        with pytest.raises(ValidationError) as exc_info:
            HoldingService.update_holding_days('000001', -1)
        
        assert "持仓天数不能为负数" in str(exc_info.value)
    
    def test_calculate_holding_days_manual(self, app, db_session):
        """测试计算持仓天数（手动设置）"""
        first_buy_date = datetime(2024, 1, 10)
        manual_days = 15
        
        result = HoldingService._calculate_holding_days(first_buy_date, manual_days)
        assert result == manual_days
    
    def test_calculate_holding_days_auto(self, app, db_session):
        """测试计算持仓天数（自动计算）"""
        # 假设今天是2024-01-20，首次买入是2024-01-10
        first_buy_date = datetime(2024, 1, 10)
        
        with app.app_context():
            # 使用patch来mock date.today
            from unittest.mock import patch
            with patch('services.review_service.date') as mock_date:
                mock_date.today.return_value = date(2024, 1, 20)
                result = HoldingService._calculate_holding_days(first_buy_date, None)
                assert result == 11  # (2024-01-20 - 2024-01-10) + 1
    
    def test_get_holding_stats(self, app, db_session):
        """测试获取持仓统计信息"""
        # 创建多个持仓
        holdings_data = [
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'trade_type': 'buy',
                'price': 12.50,
                'quantity': 1000,
                'trade_date': datetime(2024, 1, 10),
                'reason': '买入原因'
            },
            {
                'stock_code': '000002',
                'stock_name': '万科A',
                'trade_type': 'buy',
                'price': 8.00,
                'quantity': 2000,
                'trade_date': datetime(2024, 1, 12),
                'reason': '买入原因'
            }
        ]
        
        for data in holdings_data:
            TradeRecord(**data).save()
        
        # 创建复盘记录设置持仓天数
        ReviewService.create_review({
            'stock_code': '000001',
            'review_date': date.today(),
            'holding_days': 10,
            'price_up_score': 1
        })
        
        ReviewService.create_review({
            'stock_code': '000002',
            'review_date': date.today(),
            'holding_days': 8,
            'price_up_score': 1
        })
        
        stats = HoldingService.get_holding_stats()
        
        assert stats['total_holdings'] == 2
        assert stats['total_market_value'] == 12500 + 16000  # 1000*12.5 + 2000*8
        assert stats['avg_holding_days'] == 9.0  # (10+8)/2
        assert len(stats['holdings_by_days']) == 2
        assert 10 in stats['holdings_by_days']
        assert 8 in stats['holdings_by_days']
    
    def test_get_holding_stats_empty(self, app, db_session):
        """测试获取空持仓统计信息"""
        stats = HoldingService.get_holding_stats()
        
        assert stats['total_holdings'] == 0
        assert stats['total_market_value'] == 0
        assert stats['avg_holding_days'] == 0
        assert stats['holdings_by_days'] == {}