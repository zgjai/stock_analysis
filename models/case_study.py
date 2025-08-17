"""
案例研究数据模型
"""
import json
import os
from extensions import db
from models.base import BaseModel
from utils.validators import validate_stock_code
from error_handlers import ValidationError


class CaseStudy(BaseModel):
    """案例研究模型"""
    
    __tablename__ = 'case_studies'
    
    stock_code = db.Column(db.String(10), index=True)
    title = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    tags = db.Column(db.Text)  # JSON格式存储标签
    notes = db.Column(db.Text)
    
    # 索引
    __table_args__ = (
        db.Index('idx_case_stock_code', 'stock_code'),
        db.Index('idx_case_created_at', 'created_at'),
    )
    
    def __init__(self, **kwargs):
        # 数据验证
        self._validate_data(kwargs)
        # 处理tags参数
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            kwargs['tags'] = json.dumps(kwargs['tags'], ensure_ascii=False)
        super().__init__(**kwargs)
    
    def _validate_data(self, data):
        """验证案例研究数据"""
        if 'stock_code' in data and data['stock_code']:
            validate_stock_code(data['stock_code'])
        
        if 'title' in data and not data['title']:
            raise ValidationError("案例标题不能为空", "title")
        
        if 'image_path' in data:
            if not data['image_path']:
                raise ValidationError("图片路径不能为空", "image_path")
            # 验证图片文件扩展名
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
            file_ext = os.path.splitext(data['image_path'])[1].lower()
            if file_ext not in allowed_extensions:
                raise ValidationError("不支持的图片格式", "image_path")
    
    @property
    def tags_list(self):
        """获取标签列表"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except json.JSONDecodeError:
                return []
        return []
    
    @tags_list.setter
    def tags_list(self, value):
        """设置标签列表"""
        if isinstance(value, list):
            self.tags = json.dumps(value, ensure_ascii=False)
        else:
            self.tags = None
    
    def add_tag(self, tag):
        """添加标签"""
        tags = self.tags_list
        if tag not in tags:
            tags.append(tag)
            self.tags_list = tags
    
    def remove_tag(self, tag):
        """移除标签"""
        tags = self.tags_list
        if tag in tags:
            tags.remove(tag)
            self.tags_list = tags
    
    @classmethod
    def get_by_stock_code(cls, stock_code):
        """根据股票代码获取案例"""
        return cls.query.filter_by(stock_code=stock_code).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_tag(cls, tag):
        """根据标签获取案例"""
        return cls.query.filter(cls.tags.like(f'%"{tag}"%')).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def search_by_keyword(cls, keyword):
        """根据关键词搜索案例"""
        return cls.query.filter(
            db.or_(
                cls.title.like(f'%{keyword}%'),
                cls.notes.like(f'%{keyword}%'),
                cls.stock_code.like(f'%{keyword}%'),
                cls.tags.like(f'%{keyword}%')
            )
        ).order_by(cls.created_at.desc()).all()
    
    def to_dict(self):
        """转换为字典，包含标签列表"""
        result = super().to_dict()
        result['tags_list'] = self.tags_list
        return result
    
    def __repr__(self):
        return f'<CaseStudy {self.stock_code} {self.title}>'