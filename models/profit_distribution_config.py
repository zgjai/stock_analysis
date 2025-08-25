"""
收益分布配置数据模型
"""
from extensions import db
from models.base import BaseModel
from sqlalchemy import Index


class ProfitDistributionConfig(BaseModel):
    """收益分布配置模型"""
    __tablename__ = 'profit_distribution_configs'
    
    range_name = db.Column(db.String(50), nullable=False, comment='区间名称')
    min_profit_rate = db.Column(db.Numeric(8, 4), comment='最小收益率（小数形式，如0.1表示10%）')
    max_profit_rate = db.Column(db.Numeric(8, 4), comment='最大收益率（小数形式，如0.2表示20%）')
    sort_order = db.Column(db.Integer, default=0, comment='排序顺序')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_by = db.Column(db.String(50), default='system', comment='创建者')
    
    # 添加索引
    __table_args__ = (
        Index('idx_profit_config_active_order', 'is_active', 'sort_order'),
    )
    
    def __repr__(self):
        return f'<ProfitDistributionConfig {self.range_name}: {self.min_profit_rate}-{self.max_profit_rate}>'
    
    @classmethod
    def get_active_configs(cls):
        """获取所有启用的配置，按排序顺序"""
        return cls.query.filter_by(is_active=True).order_by(cls.sort_order).all()
    
    @classmethod
    def create_default_configs(cls):
        """创建默认的收益分布区间配置"""
        default_configs = [
            {'range_name': '严重亏损', 'min_profit_rate': None, 'max_profit_rate': -0.2, 'sort_order': 1},
            {'range_name': '中度亏损', 'min_profit_rate': -0.2, 'max_profit_rate': -0.1, 'sort_order': 2},
            {'range_name': '轻微亏损', 'min_profit_rate': -0.1, 'max_profit_rate': 0, 'sort_order': 3},
            {'range_name': '微盈利', 'min_profit_rate': 0, 'max_profit_rate': 0.05, 'sort_order': 4},
            {'range_name': '小幅盈利', 'min_profit_rate': 0.05, 'max_profit_rate': 0.1, 'sort_order': 5},
            {'range_name': '中等盈利', 'min_profit_rate': 0.1, 'max_profit_rate': 0.2, 'sort_order': 6},
            {'range_name': '高盈利', 'min_profit_rate': 0.2, 'max_profit_rate': 0.5, 'sort_order': 7},
            {'range_name': '超高盈利', 'min_profit_rate': 0.5, 'max_profit_rate': None, 'sort_order': 8},
        ]
        
        for config_data in default_configs:
            existing = cls.query.filter_by(range_name=config_data['range_name']).first()
            if not existing:
                config = cls(**config_data)
                db.session.add(config)
        
        db.session.commit()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'range_name': self.range_name,
            'min_profit_rate': float(self.min_profit_rate) if self.min_profit_rate is not None else None,
            'max_profit_rate': float(self.max_profit_rate) if self.max_profit_rate is not None else None,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def validate_range(self):
        """验证收益率区间的有效性"""
        if self.min_profit_rate is not None and self.max_profit_rate is not None:
            if self.min_profit_rate >= self.max_profit_rate:
                raise ValueError("最小收益率必须小于最大收益率")
        
        # 检查与其他区间是否有重叠
        overlapping = self.query.filter(
            self.id != self.id if self.id else True,
            self.is_active == True
        )
        
        if self.min_profit_rate is not None:
            overlapping = overlapping.filter(
                db.or_(
                    db.and_(
                        ProfitDistributionConfig.min_profit_rate <= self.min_profit_rate,
                        ProfitDistributionConfig.max_profit_rate > self.min_profit_rate
                    ),
                    db.and_(
                        ProfitDistributionConfig.min_profit_rate < self.max_profit_rate,
                        ProfitDistributionConfig.max_profit_rate >= self.max_profit_rate
                    ) if self.max_profit_rate is not None else False
                )
            )
        
        if overlapping.first():
            raise ValueError("收益率区间与现有配置重叠")