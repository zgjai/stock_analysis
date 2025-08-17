"""
配置数据模型
"""
import json
from extensions import db
from models.base import BaseModel
from error_handlers import ValidationError


class Configuration(BaseModel):
    """配置模型"""
    
    __tablename__ = 'configurations'
    
    config_key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    
    def __init__(self, **kwargs):
        # 数据验证
        self._validate_data(kwargs)
        super().__init__(**kwargs)
    
    def _validate_data(self, data):
        """验证配置数据"""
        if 'config_key' in data and not data['config_key']:
            raise ValidationError("配置键不能为空", "config_key")
        
        if 'config_value' in data and data['config_value'] is None:
            raise ValidationError("配置值不能为空", "config_value")
    
    @classmethod
    def get_by_key(cls, key):
        """根据键获取配置"""
        return cls.query.filter_by(config_key=key).first()
    
    @classmethod
    def get_value(cls, key, default=None):
        """获取配置值"""
        config = cls.get_by_key(key)
        if config:
            try:
                # 尝试解析JSON
                return json.loads(config.config_value)
            except json.JSONDecodeError:
                # 如果不是JSON，返回原始字符串
                return config.config_value
        return default
    
    @classmethod
    def set_value(cls, key, value, description=None):
        """设置配置值"""
        config = cls.get_by_key(key)
        
        # 如果值是列表或字典，转换为JSON
        if isinstance(value, (list, dict)):
            value_str = json.dumps(value, ensure_ascii=False)
        else:
            value_str = str(value)
        
        if config:
            config.config_value = value_str
            if description:
                config.description = description
        else:
            config = cls(
                config_key=key,
                config_value=value_str,
                description=description
            )
        
        return config.save()
    
    @classmethod
    def get_buy_reasons(cls):
        """获取买入原因选项"""
        return cls.get_value('buy_reasons', [])
    
    @classmethod
    def get_sell_reasons(cls):
        """获取卖出原因选项"""
        return cls.get_value('sell_reasons', [])
    
    @classmethod
    def set_buy_reasons(cls, reasons):
        """设置买入原因选项"""
        return cls.set_value('buy_reasons', reasons, '买入原因选项')
    
    @classmethod
    def set_sell_reasons(cls, reasons):
        """设置卖出原因选项"""
        return cls.set_value('sell_reasons', reasons, '卖出原因选项')
    
    def __repr__(self):
        return f'<Configuration {self.config_key}>'