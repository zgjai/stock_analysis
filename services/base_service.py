"""
基础服务类
"""
from extensions import db
from error_handlers import DatabaseError, NotFoundError

class BaseService:
    """基础服务类，提供通用的数据库操作方法"""
    
    model = None  # 子类需要设置对应的模型类
    
    @classmethod
    def get_by_id(cls, id):
        """根据ID获取记录"""
        if not cls.model:
            raise NotImplementedError("子类必须设置model属性")
        
        try:
            record = cls.model.get_by_id(id)
            if not record:
                raise NotFoundError(f"{cls.model.__name__} with id {id} not found")
            return record
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise e
            raise DatabaseError(f"获取{cls.model.__name__}记录失败: {str(e)}")
    
    @classmethod
    def get_all(cls, page=None, per_page=None):
        """获取所有记录，支持分页"""
        if not cls.model:
            raise NotImplementedError("子类必须设置model属性")
        
        try:
            query = cls.model.query
            
            if page and per_page:
                return query.paginate(
                    page=page, 
                    per_page=per_page, 
                    error_out=False
                )
            else:
                return query.all()
        except Exception as e:
            raise DatabaseError(f"获取{cls.model.__name__}记录列表失败: {str(e)}")
    
    @classmethod
    def create(cls, data):
        """创建新记录"""
        if not cls.model:
            raise NotImplementedError("子类必须设置model属性")
        
        try:
            from flask import current_app
            current_app.logger.info(f"=== BaseService.create 开始 ===")
            current_app.logger.info(f"模型类: {cls.model.__name__}")
            current_app.logger.info(f"创建数据: {data}")
            
            current_app.logger.info("开始创建模型实例")
            record = cls.model(**data)
            current_app.logger.info(f"模型实例创建成功: {record}")
            
            current_app.logger.info("开始保存记录")
            saved_record = record.save()
            current_app.logger.info(f"记录保存成功，ID: {saved_record.id}")
            
            return saved_record
        except Exception as e:
            current_app.logger.error(f"BaseService.create 发生错误: {str(e)}")
            current_app.logger.error(f"错误类型: {type(e)}")
            import traceback
            current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
            raise DatabaseError(f"创建{cls.model.__name__}记录失败: {str(e)}")
    
    @classmethod
    def update(cls, id, data):
        """更新记录"""
        if not cls.model:
            raise NotImplementedError("子类必须设置model属性")
        
        try:
            record = cls.get_by_id(id)
            for key, value in data.items():
                if hasattr(record, key):
                    # 只更新非None值，避免覆盖必填字段
                    if value is not None:
                        setattr(record, key, value)
            return record.save()
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise e
            raise DatabaseError(f"更新{cls.model.__name__}记录失败: {str(e)}")
    
    @classmethod
    def delete(cls, id):
        """删除记录"""
        if not cls.model:
            raise NotImplementedError("子类必须设置model属性")
        
        try:
            record = cls.get_by_id(id)
            return record.delete()
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise e
            raise DatabaseError(f"删除{cls.model.__name__}记录失败: {str(e)}")
    
    @classmethod
    def count(cls):
        """获取记录总数"""
        if not cls.model:
            raise NotImplementedError("子类必须设置model属性")
        
        try:
            return cls.model.query.count()
        except Exception as e:
            raise DatabaseError(f"获取{cls.model.__name__}记录数量失败: {str(e)}")