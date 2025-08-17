"""
交易策略数据模型
"""
import json
from extensions import db
from models.base import BaseModel
from error_handlers import ValidationError


class TradingStrategy(BaseModel):
    """交易策略模型"""
    
    __tablename__ = 'trading_strategies'
    
    strategy_name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    rules = db.Column(db.Text, nullable=False)  # JSON格式存储策略规则
    description = db.Column(db.Text)
    
    def __init__(self, **kwargs):
        # 数据验证
        self._validate_data(kwargs)
        super().__init__(**kwargs)
    
    def _validate_data(self, data):
        """验证交易策略数据"""
        if 'strategy_name' in data and not data['strategy_name']:
            raise ValidationError("策略名称不能为空", "strategy_name")
        
        if 'rules' in data:
            if not data['rules']:
                raise ValidationError("策略规则不能为空", "rules")
            
            # 如果是字符串，验证是否为有效JSON
            if isinstance(data['rules'], str):
                try:
                    json.loads(data['rules'])
                except json.JSONDecodeError:
                    raise ValidationError("策略规则必须是有效的JSON格式", "rules")
            # 如果是字典或列表，转换为JSON字符串
            elif isinstance(data['rules'], (dict, list)):
                data['rules'] = json.dumps(data['rules'], ensure_ascii=False)
    
    @property
    def rules_list(self):
        """获取策略规则列表"""
        if self.rules:
            try:
                return json.loads(self.rules)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @rules_list.setter
    def rules_list(self, value):
        """设置策略规则列表"""
        if isinstance(value, (dict, list)):
            self.rules = json.dumps(value, ensure_ascii=False)
        else:
            self.rules = None
    
    @classmethod
    def get_active_strategies(cls):
        """获取所有激活的策略"""
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_default_strategy(cls):
        """获取默认策略"""
        return cls.query.filter_by(strategy_name='默认持仓策略').first()
    
    def activate(self):
        """激活策略"""
        self.is_active = True
        return self.save()
    
    def deactivate(self):
        """停用策略"""
        self.is_active = False
        return self.save()
    
    def add_rule(self, rule):
        """添加策略规则"""
        rules = self.rules_list
        if 'rules' not in rules:
            rules['rules'] = []
        rules['rules'].append(rule)
        self.rules_list = rules
        return self.save()
    
    def remove_rule(self, rule_index):
        """移除策略规则"""
        rules = self.rules_list
        if 'rules' in rules and 0 <= rule_index < len(rules['rules']):
            rules['rules'].pop(rule_index)
            self.rules_list = rules
            return self.save()
        return False
    
    def to_dict(self):
        """转换为字典，包含规则列表"""
        result = super().to_dict()
        result['rules_list'] = self.rules_list
        return result
    
    def __repr__(self):
        return f'<TradingStrategy {self.strategy_name} {"Active" if self.is_active else "Inactive"}>'