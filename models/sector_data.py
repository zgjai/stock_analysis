"""
板块数据模型
"""
import json
from datetime import date
from extensions import db
from models.base import BaseModel
from error_handlers import ValidationError


class SectorData(BaseModel):
    """板块数据模型"""
    
    __tablename__ = 'sector_data'
    
    sector_name = db.Column(db.String(50), nullable=False, index=True)
    sector_code = db.Column(db.String(20))
    change_percent = db.Column(db.Numeric(5, 2), nullable=False)
    record_date = db.Column(db.Date, nullable=False, index=True)
    rank_position = db.Column(db.Integer)
    volume = db.Column(db.BigInteger)
    market_cap = db.Column(db.Numeric(15, 2))
    
    # 表约束
    __table_args__ = (
        db.UniqueConstraint('sector_name', 'record_date', name='unique_sector_date'),
        db.Index('idx_sector_date_rank', 'record_date', 'rank_position'),
        db.Index('idx_sector_name_date', 'sector_name', 'record_date'),
    )
    
    def __init__(self, **kwargs):
        # 数据验证
        self._validate_data(kwargs)
        super().__init__(**kwargs)
    
    def _validate_data(self, data):
        """验证板块数据"""
        if 'sector_name' in data and not data['sector_name']:
            raise ValidationError("板块名称不能为空", "sector_name")
        
        if 'change_percent' in data and data['change_percent'] is not None:
            try:
                change_percent = float(data['change_percent'])
                if change_percent < -100 or change_percent > 100:
                    raise ValidationError("涨跌幅必须在-100%到100%之间", "change_percent")
                data['change_percent'] = change_percent
            except (ValueError, TypeError):
                raise ValidationError("涨跌幅格式不正确", "change_percent")
        
        if 'record_date' in data and data['record_date'] is None:
            raise ValidationError("记录日期不能为空", "record_date")
        
        if 'rank_position' in data and data['rank_position'] is not None:
            try:
                rank_position = int(data['rank_position'])
                if rank_position < 1:
                    raise ValidationError("排名位置必须大于0", "rank_position")
                data['rank_position'] = rank_position
            except (ValueError, TypeError):
                raise ValidationError("排名位置必须是整数", "rank_position")
        
        if 'volume' in data and data['volume'] is not None:
            try:
                volume = int(data['volume'])
                if volume < 0:
                    raise ValidationError("成交量不能为负数", "volume")
                data['volume'] = volume
            except (ValueError, TypeError):
                raise ValidationError("成交量必须是整数", "volume")
        
        if 'market_cap' in data and data['market_cap'] is not None:
            try:
                market_cap = float(data['market_cap'])
                if market_cap < 0:
                    raise ValidationError("市值不能为负数", "market_cap")
                data['market_cap'] = market_cap
            except (ValueError, TypeError):
                raise ValidationError("市值格式不正确", "market_cap")
    
    @classmethod
    def get_by_date(cls, target_date):
        """获取指定日期的板块数据"""
        return cls.query.filter_by(record_date=target_date).order_by(cls.rank_position).all()
    
    @classmethod
    def get_latest_ranking(cls, limit=None):
        """获取最新的板块排名"""
        latest_date = db.session.query(db.func.max(cls.record_date)).scalar()
        if latest_date:
            query = cls.query.filter_by(record_date=latest_date).order_by(cls.rank_position)
            if limit:
                query = query.limit(limit)
            return query.all()
        return []
    
    @classmethod
    def get_top_performers(cls, days=30, top_k=10):
        """获取最近N天TOPK板块统计"""
        from datetime import timedelta
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # 查询指定时间范围内排名前K的板块
        result = db.session.query(
            cls.sector_name,
            db.func.count().label('appearances'),
            db.func.avg(cls.rank_position).label('avg_rank'),
            db.func.min(cls.rank_position).label('best_rank'),
            db.func.max(cls.record_date).label('latest_date')
        ).filter(
            cls.record_date.between(start_date, end_date),
            cls.rank_position <= top_k
        ).group_by(cls.sector_name).order_by(
            db.desc('appearances'), 'avg_rank'
        ).all()
        
        return result
    
    @classmethod
    def get_sector_history(cls, sector_name, days=30):
        """获取板块历史表现"""
        from datetime import timedelta
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        return cls.query.filter(
            cls.sector_name == sector_name,
            cls.record_date.between(start_date, end_date)
        ).order_by(cls.record_date.desc()).all()
    
    @classmethod
    def has_data_for_date(cls, target_date):
        """检查指定日期是否已有数据"""
        return cls.query.filter_by(record_date=target_date).first() is not None
    
    def to_dict(self):
        """转换为字典，包含特殊字段处理"""
        result = super().to_dict()
        # 转换Decimal类型为float
        for field in ['change_percent', 'market_cap']:
            if result.get(field) is not None:
                result[field] = float(result[field])
        # 转换日期
        if result.get('record_date'):
            result['record_date'] = result['record_date'].isoformat()
        return result
    
    def __repr__(self):
        return f'<SectorData {self.sector_name} {self.change_percent}% {self.record_date}>'


class SectorRanking(BaseModel):
    """板块排名历史模型"""
    
    __tablename__ = 'sector_rankings'
    
    record_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    ranking_data = db.Column(db.Text, nullable=False)  # JSON格式存储完整排名数据
    total_sectors = db.Column(db.Integer)  # 当日总板块数
    
    @property
    def ranking_list(self):
        """获取排名列表"""
        if self.ranking_data:
            try:
                return json.loads(self.ranking_data)
            except json.JSONDecodeError:
                return []
        return []
    
    @ranking_list.setter
    def ranking_list(self, value):
        """设置排名列表"""
        if isinstance(value, list):
            self.ranking_data = json.dumps(value, ensure_ascii=False)
        else:
            self.ranking_data = None
    
    @classmethod
    def get_by_date(cls, target_date):
        """获取指定日期的排名数据"""
        return cls.query.filter_by(record_date=target_date).first()
    
    @classmethod
    def create_or_update(cls, target_date, ranking_data, total_sectors):
        """创建或更新排名记录"""
        existing = cls.get_by_date(target_date)
        
        if existing:
            existing.ranking_list = ranking_data
            existing.total_sectors = total_sectors
            return existing.save()
        else:
            new_ranking = cls(
                record_date=target_date,
                total_sectors=total_sectors
            )
            new_ranking.ranking_list = ranking_data
            return new_ranking.save()
    
    def __repr__(self):
        return f'<SectorRanking {self.record_date} {self.total_sectors} sectors>'