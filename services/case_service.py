"""
案例管理服务
"""
import os
import json
import uuid
from datetime import datetime
from PIL import Image
from werkzeug.utils import secure_filename
from services.base_service import BaseService
from models.case_study import CaseStudy
from error_handlers import ValidationError, FileOperationError
from config import Config
from extensions import db


class CaseService(BaseService):
    """案例管理服务"""
    
    model = CaseStudy
    
    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.db = db
        
        # 确保上传目录存在
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def _allowed_file(self, filename):
        """检查文件扩展名是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def _generate_filename(self, original_filename):
        """生成唯一的文件名"""
        ext = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        return unique_filename
    
    def _convert_image_format(self, image_path, target_format='PNG'):
        """转换图片格式，确保跨平台兼容性"""
        try:
            with Image.open(image_path) as img:
                # 转换为RGB模式（如果是RGBA或其他模式）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 生成新的文件名
                base_name = os.path.splitext(image_path)[0]
                new_path = f"{base_name}.png"
                
                # 保存转换后的图片
                img.save(new_path, target_format, quality=95, optimize=True)
                
                # 如果原文件和新文件不同，删除原文件
                if image_path != new_path:
                    os.remove(image_path)
                
                return new_path
                
        except Exception as e:
            raise FileOperationError(f"图片格式转换失败: {str(e)}")
    
    def _resize_image_if_needed(self, image_path, max_width=1920, max_height=1080):
        """如果图片过大则调整尺寸"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                
                # 如果图片尺寸超过限制，则调整大小
                if width > max_width or height > max_height:
                    # 计算缩放比例，保持宽高比
                    ratio = min(max_width / width, max_height / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    
                    # 调整图片大小
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resized_img.save(image_path, quality=95, optimize=True)
                    
        except Exception as e:
            raise FileOperationError(f"图片尺寸调整失败: {str(e)}")
    
    def upload_image(self, file, stock_code=None, title=None, tags=None, notes=None):
        """
        上传案例图片
        
        Args:
            file: 上传的文件对象
            stock_code: 股票代码
            title: 案例标题
            tags: 标签列表
            notes: 备注说明
            
        Returns:
            dict: 包含案例信息的字典
        """
        if not file or file.filename == '':
            raise ValidationError("请选择要上传的文件", "file")
        
        if not self._allowed_file(file.filename):
            raise ValidationError("不支持的文件格式", "file")
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.max_file_size:
            raise ValidationError("文件大小超过限制（最大10MB）", "file")
        
        try:
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            unique_filename = self._generate_filename(filename)
            file_path = os.path.join(self.upload_folder, unique_filename)
            
            # 保存文件
            file.save(file_path)
            
            # 转换图片格式
            converted_path = self._convert_image_format(file_path)
            
            # 调整图片尺寸
            self._resize_image_if_needed(converted_path)
            
            # 获取相对路径用于存储
            relative_path = os.path.relpath(converted_path, start='.')
            
            # 创建案例记录
            case_data = {
                'stock_code': stock_code,
                'title': title or f"案例_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'image_path': relative_path,
                'tags': tags or [],
                'notes': notes
            }
            
            case = self.create(case_data)
            return case.to_dict()
            
        except Exception as e:
            # 如果创建记录失败，清理已上传的文件
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            if 'converted_path' in locals() and os.path.exists(converted_path):
                os.remove(converted_path)
            raise e
    
    def update_case(self, case_id, **kwargs):
        """
        更新案例信息
        
        Args:
            case_id: 案例ID
            **kwargs: 更新的字段
            
        Returns:
            dict: 更新后的案例信息
        """
        case = self.get_by_id(case_id)
        if not case:
            raise ValidationError("案例不存在", "case_id")
        
        # 处理标签更新
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            case.tags_list = kwargs['tags']
            del kwargs['tags']
        
        # 更新其他字段
        for key, value in kwargs.items():
            if hasattr(case, key):
                setattr(case, key, value)
        
        case.updated_at = datetime.utcnow()
        self.db.session.commit()
        
        return case.to_dict()
    
    def delete_case(self, case_id):
        """
        删除案例（包括关联的图片文件）
        
        Args:
            case_id: 案例ID
            
        Returns:
            bool: 删除是否成功
        """
        case = self.get_by_id(case_id)
        if not case:
            raise ValidationError("案例不存在", "case_id")
        
        # 删除关联的图片文件
        if case.image_path and os.path.exists(case.image_path):
            try:
                os.remove(case.image_path)
            except OSError:
                pass  # 文件删除失败不影响数据库记录删除
        
        # 删除数据库记录
        self.db.session.delete(case)
        self.db.session.commit()
        
        return True
    
    def get_cases_by_stock_code(self, stock_code):
        """
        根据股票代码获取案例列表
        
        Args:
            stock_code: 股票代码
            
        Returns:
            list: 案例列表
        """
        cases = CaseStudy.get_by_stock_code(stock_code)
        return [case.to_dict() for case in cases]
    
    def get_cases_by_tag(self, tag):
        """
        根据标签获取案例列表
        
        Args:
            tag: 标签名称
            
        Returns:
            list: 案例列表
        """
        cases = CaseStudy.get_by_tag(tag)
        return [case.to_dict() for case in cases]
    
    def search_cases(self, keyword=None, stock_code=None, tags=None, 
                    start_date=None, end_date=None, page=1, per_page=20):
        """
        搜索案例
        
        Args:
            keyword: 关键词
            stock_code: 股票代码
            tags: 标签列表
            start_date: 开始日期
            end_date: 结束日期
            page: 页码
            per_page: 每页数量
            
        Returns:
            dict: 包含案例列表和分页信息的字典
        """
        query = CaseStudy.query
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                self.db.or_(
                    CaseStudy.title.like(f'%{keyword}%'),
                    CaseStudy.notes.like(f'%{keyword}%'),
                    CaseStudy.stock_code.like(f'%{keyword}%'),
                    CaseStudy.tags.like(f'%{keyword}%')
                )
            )
        
        # 股票代码筛选
        if stock_code:
            query = query.filter(CaseStudy.stock_code == stock_code)
        
        # 标签筛选
        if tags:
            for tag in tags:
                query = query.filter(CaseStudy.tags.like(f'%"{tag}"%'))
        
        # 日期范围筛选
        if start_date:
            query = query.filter(CaseStudy.created_at >= start_date)
        if end_date:
            query = query.filter(CaseStudy.created_at <= end_date)
        
        # 排序和分页
        query = query.order_by(CaseStudy.created_at.desc())
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'cases': [case.to_dict() for case in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    def get_all_tags(self):
        """
        获取所有使用过的标签
        
        Returns:
            list: 标签列表，按使用频率排序
        """
        cases = CaseStudy.query.filter(CaseStudy.tags.isnot(None)).all()
        tag_count = {}
        
        for case in cases:
            tags = case.tags_list
            for tag in tags:
                tag_count[tag] = tag_count.get(tag, 0) + 1
        
        # 按使用频率排序
        sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
        return [{'tag': tag, 'count': count} for tag, count in sorted_tags]
    
    def get_statistics(self):
        """
        获取案例统计信息
        
        Returns:
            dict: 统计信息
        """
        total_cases = CaseStudy.query.count()
        cases_with_stock = CaseStudy.query.filter(CaseStudy.stock_code.isnot(None)).count()
        cases_with_tags = CaseStudy.query.filter(CaseStudy.tags.isnot(None)).count()
        
        # 获取最近30天的案例数量
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_cases = CaseStudy.query.filter(CaseStudy.created_at >= thirty_days_ago).count()
        
        return {
            'total_cases': total_cases,
            'cases_with_stock': cases_with_stock,
            'cases_with_tags': cases_with_tags,
            'recent_cases': recent_cases,
            'total_tags': len(self.get_all_tags())
        }