"""
复盘记录和持仓管理服务
"""
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy import func, and_, or_, desc, asc
from extensions import db
from services.base_service import BaseService
from models.review_record import ReviewRecord
from models.trade_record import TradeRecord
from error_handlers import ValidationError, NotFoundError, DatabaseError


class ReviewService(BaseService):
    """复盘记录服务"""
    
    model = ReviewRecord
    
    @classmethod
    def create_review(cls, data: Dict[str, Any]) -> ReviewRecord:
        """创建复盘记录"""
        try:
            # 验证必填字段
            required_fields = ['stock_code', 'review_date']
            for field in required_fields:
                if field not in data or data[field] is None:
                    raise ValidationError(f"{field}不能为空")
            
            # 处理日期格式
            if isinstance(data['review_date'], str):
                try:
                    data['review_date'] = datetime.strptime(data['review_date'], '%Y-%m-%d').date()
                except ValueError:
                    raise ValidationError("复盘日期格式不正确，应为YYYY-MM-DD")
            
            # 检查是否已存在相同股票和日期的复盘记录
            existing = ReviewRecord.query.filter_by(
                stock_code=data['stock_code'],
                review_date=data['review_date']
            ).first()
            
            if existing:
                raise ValidationError(f"股票{data['stock_code']}在{data['review_date']}已存在复盘记录")
            
            # 创建复盘记录
            review = ReviewRecord(**data)
            return review.save()
            
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise e
            raise DatabaseError(f"创建复盘记录失败: {str(e)}")
    
    @classmethod
    def update_review(cls, review_id: int, data: Dict[str, Any]) -> ReviewRecord:
        """更新复盘记录"""
        try:
            review = cls.get_by_id(review_id)
            
            # 处理日期格式
            if 'review_date' in data and isinstance(data['review_date'], str):
                try:
                    data['review_date'] = datetime.strptime(data['review_date'], '%Y-%m-%d').date()
                except ValueError:
                    raise ValidationError("复盘日期格式不正确，应为YYYY-MM-DD")
            
            # 检查是否与其他记录冲突
            if 'stock_code' in data or 'review_date' in data:
                stock_code = data.get('stock_code', review.stock_code)
                review_date = data.get('review_date', review.review_date)
                
                existing = ReviewRecord.query.filter(
                    and_(
                        ReviewRecord.stock_code == stock_code,
                        ReviewRecord.review_date == review_date,
                        ReviewRecord.id != review_id
                    )
                ).first()
                
                if existing:
                    raise ValidationError(f"股票{stock_code}在{review_date}已存在复盘记录")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(review, key):
                    setattr(review, key, value)
            
            # 重新计算总分
            review._calculate_total_score()
            
            return review.save()
            
        except Exception as e:
            if isinstance(e, (ValidationError, NotFoundError, DatabaseError)):
                raise e
            raise DatabaseError(f"更新复盘记录失败: {str(e)}")
    
    @classmethod
    def get_reviews(cls, filters: Dict[str, Any] = None, page: int = None, 
                   per_page: int = None, sort_by: str = 'review_date', 
                   sort_order: str = 'desc') -> Dict[str, Any]:
        """获取复盘记录列表"""
        try:
            query = ReviewRecord.query
            
            # 应用筛选条件
            if filters:
                if filters.get('stock_code'):
                    query = query.filter(ReviewRecord.stock_code == filters['stock_code'])
                
                if filters.get('start_date'):
                    start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
                    query = query.filter(ReviewRecord.review_date >= start_date)
                
                if filters.get('end_date'):
                    end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
                    query = query.filter(ReviewRecord.review_date <= end_date)
                
                if filters.get('decision'):
                    query = query.filter(ReviewRecord.decision == filters['decision'])
                
                if filters.get('min_score') is not None:
                    query = query.filter(ReviewRecord.total_score >= filters['min_score'])
                
                if filters.get('max_score') is not None:
                    query = query.filter(ReviewRecord.total_score <= filters['max_score'])
                
                if filters.get('holding_days_min') is not None:
                    query = query.filter(ReviewRecord.holding_days >= filters['holding_days_min'])
                
                if filters.get('holding_days_max') is not None:
                    query = query.filter(ReviewRecord.holding_days <= filters['holding_days_max'])
            
            # 应用排序
            if hasattr(ReviewRecord, sort_by):
                order_func = desc if sort_order.lower() == 'desc' else asc
                query = query.order_by(order_func(getattr(ReviewRecord, sort_by)))
            
            # 应用分页
            if page and per_page:
                pagination = query.paginate(
                    page=page,
                    per_page=per_page,
                    error_out=False
                )
                
                return {
                    'reviews': [review.to_dict() for review in pagination.items],
                    'pagination': {
                        'page': pagination.page,
                        'per_page': pagination.per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_prev': pagination.has_prev,
                        'has_next': pagination.has_next
                    }
                }
            else:
                reviews = query.all()
                return {
                    'reviews': [review.to_dict() for review in reviews],
                    'total': len(reviews)
                }
                
        except Exception as e:
            raise DatabaseError(f"获取复盘记录失败: {str(e)}")
    
    @classmethod
    def get_review_by_stock_and_date(cls, stock_code: str, review_date: date) -> Optional[ReviewRecord]:
        """根据股票代码和日期获取复盘记录"""
        try:
            return ReviewRecord.query.filter_by(
                stock_code=stock_code,
                review_date=review_date
            ).first()
        except Exception as e:
            raise DatabaseError(f"获取复盘记录失败: {str(e)}")
    
    @classmethod
    def get_reviews_by_stock(cls, stock_code: str) -> List[ReviewRecord]:
        """获取某股票的所有复盘记录"""
        try:
            return ReviewRecord.query.filter_by(stock_code=stock_code)\
                .order_by(ReviewRecord.review_date.desc()).all()
        except Exception as e:
            raise DatabaseError(f"获取股票复盘记录失败: {str(e)}")
    
    @classmethod
    def get_latest_review_by_stock(cls, stock_code: str) -> Optional[ReviewRecord]:
        """获取某股票最新的复盘记录"""
        try:
            return ReviewRecord.query.filter_by(stock_code=stock_code)\
                .order_by(ReviewRecord.review_date.desc()).first()
        except Exception as e:
            raise DatabaseError(f"获取最新复盘记录失败: {str(e)}")


class HoldingService:
    """持仓管理服务"""
    
    @classmethod
    def get_current_holdings(cls) -> List[Dict[str, Any]]:
        """获取当前持仓列表"""
        try:
            # 查询所有买入记录，按股票代码分组
            buy_records = db.session.query(
                TradeRecord.stock_code,
                TradeRecord.stock_name,
                func.sum(TradeRecord.quantity).label('total_buy_quantity'),
                func.avg(TradeRecord.price).label('avg_buy_price'),
                func.min(TradeRecord.trade_date).label('first_buy_date'),
                func.max(TradeRecord.trade_date).label('last_buy_date')
            ).filter(
                and_(
                    TradeRecord.trade_type == 'buy',
                    TradeRecord.is_corrected == False
                )
            ).group_by(TradeRecord.stock_code, TradeRecord.stock_name).all()
            
            # 查询所有卖出记录，按股票代码分组
            sell_records = db.session.query(
                TradeRecord.stock_code,
                func.sum(TradeRecord.quantity).label('total_sell_quantity')
            ).filter(
                and_(
                    TradeRecord.trade_type == 'sell',
                    TradeRecord.is_corrected == False
                )
            ).group_by(TradeRecord.stock_code).all()
            
            # 转换为字典便于查找
            sell_dict = {record.stock_code: record.total_sell_quantity for record in sell_records}
            
            holdings = []
            for buy_record in buy_records:
                stock_code = buy_record.stock_code
                total_buy = int(buy_record.total_buy_quantity)
                total_sell = int(sell_dict.get(stock_code, 0))
                current_quantity = total_buy - total_sell
                
                # 只有当前持仓大于0的股票才算持仓
                if current_quantity > 0:
                    # 获取最新复盘记录
                    latest_review = ReviewService.get_latest_review_by_stock(stock_code)
                    
                    # 计算持仓天数
                    holding_days = cls._calculate_holding_days(
                        buy_record.first_buy_date,
                        latest_review.holding_days if latest_review else None
                    )
                    
                    holding = {
                        'stock_code': stock_code,
                        'stock_name': buy_record.stock_name,
                        'current_quantity': current_quantity,
                        'total_buy_quantity': total_buy,
                        'total_sell_quantity': total_sell,
                        'avg_buy_price': float(buy_record.avg_buy_price),
                        'first_buy_date': buy_record.first_buy_date.isoformat(),
                        'last_buy_date': buy_record.last_buy_date.isoformat(),
                        'holding_days': holding_days,
                        'latest_review': latest_review.to_dict() if latest_review else None
                    }
                    
                    holdings.append(holding)
            
            # 按持仓天数倒序排列
            holdings.sort(key=lambda x: x['holding_days'], reverse=True)
            
            return holdings
            
        except Exception as e:
            raise DatabaseError(f"获取当前持仓失败: {str(e)}")
    
    @classmethod
    def get_holding_by_stock(cls, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取特定股票的持仓信息"""
        try:
            holdings = cls.get_current_holdings()
            for holding in holdings:
                if holding['stock_code'] == stock_code:
                    return holding
            return None
        except Exception as e:
            raise DatabaseError(f"获取股票持仓信息失败: {str(e)}")
    
    @classmethod
    def update_holding_days(cls, stock_code: str, holding_days: int) -> Dict[str, Any]:
        """更新持仓天数（通过创建或更新复盘记录）"""
        try:
            if holding_days < 0:
                raise ValidationError("持仓天数不能为负数")
            
            # 获取今日复盘记录，如果不存在则创建
            today = date.today()
            review = ReviewService.get_review_by_stock_and_date(stock_code, today)
            
            if review:
                # 更新现有复盘记录的持仓天数
                review.holding_days = holding_days
                review.save()
            else:
                # 创建新的复盘记录，只设置持仓天数
                review_data = {
                    'stock_code': stock_code,
                    'review_date': today,
                    'holding_days': holding_days,
                    'price_up_score': 0,
                    'bbi_score': 0,
                    'volume_score': 0,
                    'trend_score': 0,
                    'j_score': 0
                }
                review = ReviewService.create_review(review_data)
            
            return review.to_dict()
            
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise e
            raise DatabaseError(f"更新持仓天数失败: {str(e)}")
    
    @classmethod
    def _calculate_holding_days(cls, first_buy_date: datetime, manual_holding_days: Optional[int]) -> int:
        """计算持仓天数"""
        if manual_holding_days is not None:
            return manual_holding_days
        
        # 如果没有手动设置，则根据首次买入日期计算
        if isinstance(first_buy_date, datetime):
            first_buy_date = first_buy_date.date()
        
        return (date.today() - first_buy_date).days + 1
    
    @classmethod
    def get_holding_stats(cls) -> Dict[str, Any]:
        """获取持仓统计信息"""
        try:
            holdings = cls.get_current_holdings()
            
            if not holdings:
                return {
                    'total_holdings': 0,
                    'total_market_value': 0,
                    'avg_holding_days': 0,
                    'holdings_by_days': {}
                }
            
            total_holdings = len(holdings)
            total_market_value = sum(h['current_quantity'] * h['avg_buy_price'] for h in holdings)
            avg_holding_days = sum(h['holding_days'] for h in holdings) / total_holdings
            
            # 按持仓天数分组统计
            holdings_by_days = {}
            for holding in holdings:
                days = holding['holding_days']
                if days not in holdings_by_days:
                    holdings_by_days[days] = []
                holdings_by_days[days].append({
                    'stock_code': holding['stock_code'],
                    'stock_name': holding['stock_name'],
                    'current_quantity': holding['current_quantity']
                })
            
            return {
                'total_holdings': total_holdings,
                'total_market_value': total_market_value,
                'avg_holding_days': round(avg_holding_days, 1),
                'holdings_by_days': holdings_by_days
            }
            
        except Exception as e:
            raise DatabaseError(f"获取持仓统计失败: {str(e)}")