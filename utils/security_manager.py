"""
安全管理工具类
"""
import os
import hashlib
import mimetypes
import logging
from typing import Dict, Any, List, Optional, Tuple
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from PIL import Image
from flask import current_app, request
from error_handlers import ValidationError, SecurityError

logger = logging.getLogger(__name__)


class SecurityManager:
    """安全管理器"""
    
    # 允许的图片格式
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
        'image/bmp', 'image/webp'
    }
    
    # 文件大小限制
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGE_DIMENSION = 4096  # 最大图片尺寸
    
    # 危险文件扩展名黑名单
    DANGEROUS_EXTENSIONS = {
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar',
        'php', 'asp', 'aspx', 'jsp', 'py', 'pl', 'sh', 'ps1'
    }
    
    @classmethod
    def validate_image_file(cls, file: FileStorage) -> Dict[str, Any]:
        """
        验证图片文件安全性
        
        Args:
            file: 上传的文件
            
        Returns:
            Dict: 验证结果和文件信息
            
        Raises:
            ValidationError: 文件验证失败
            SecurityError: 安全检查失败
        """
        try:
            logger.info(f"开始验证图片文件: {file.filename}")
            
            # 基本文件检查
            if not file or not file.filename:
                raise ValidationError("文件不能为空")
            
            # 文件名安全检查
            cls._validate_filename_security(file.filename)
            
            # 文件扩展名检查
            extension = cls._get_file_extension(file.filename)
            cls._validate_file_extension(extension)
            
            # MIME类型检查
            cls._validate_mime_type(file.mimetype)
            
            # 文件大小检查
            file_size = cls._get_file_size(file)
            cls._validate_file_size(file_size)
            
            # 文件内容安全检查
            cls._validate_file_content(file)
            
            # 图片格式验证
            image_info = cls._validate_image_format(file)
            
            # 重置文件指针
            file.seek(0)
            
            validation_result = {
                'is_valid': True,
                'filename': file.filename,
                'extension': extension,
                'mime_type': file.mimetype,
                'file_size': file_size,
                'image_info': image_info,
                'security_checks_passed': True
            }
            
            logger.info(f"文件验证通过: {file.filename}")
            return validation_result
            
        except Exception as e:
            logger.error(f"文件验证失败: {file.filename}, 错误: {str(e)}")
            if isinstance(e, (ValidationError, SecurityError)):
                raise e
            raise SecurityError(f"文件安全检查失败: {str(e)}")
    
    @classmethod
    def generate_secure_filename(cls, original_filename: str) -> str:
        """
        生成安全的文件名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            str: 安全的文件名
        """
        try:
            # 获取文件扩展名
            extension = cls._get_file_extension(original_filename)
            
            # 生成基于时间戳和哈希的文件名
            import time
            timestamp = str(int(time.time() * 1000000))  # 微秒时间戳
            
            # 使用原始文件名生成哈希
            filename_hash = hashlib.md5(original_filename.encode('utf-8')).hexdigest()[:8]
            
            # 组合安全文件名
            secure_name = f"review_{timestamp}_{filename_hash}.{extension}"
            
            # 使用 werkzeug 的 secure_filename 进一步处理
            return secure_filename(secure_name)
            
        except Exception as e:
            logger.error(f"生成安全文件名失败: {original_filename}, 错误: {str(e)}")
            raise SecurityError(f"生成安全文件名失败: {str(e)}")
    
    @classmethod
    def create_secure_upload_directory(cls, base_dir: str = None) -> str:
        """
        创建安全的上传目录
        
        Args:
            base_dir: 基础目录
            
        Returns:
            str: 安全的上传目录路径
        """
        try:
            if base_dir is None:
                base_dir = current_app.config.get('REVIEW_IMAGES_UPLOAD_FOLDER', 'uploads/review_images')
            
            # 如果是相对路径，则相对于应用根目录
            if not os.path.isabs(base_dir):
                base_dir = os.path.join(current_app.root_path, base_dir)
            
            # 按年月创建子目录
            from datetime import datetime
            now = datetime.now()
            sub_dir = os.path.join(base_dir, str(now.year), f"{now.month:02d}")
            
            # 创建目录
            os.makedirs(sub_dir, exist_ok=True)
            
            # 设置目录权限（只有所有者可读写执行）
            os.chmod(sub_dir, 0o755)
            
            # 创建 .htaccess 文件防止直接访问
            htaccess_path = os.path.join(sub_dir, '.htaccess')
            if not os.path.exists(htaccess_path):
                with open(htaccess_path, 'w') as f:
                    f.write("Options -Indexes\n")
                    f.write("Options -ExecCGI\n")
                    f.write("<Files ~ \"\\.(php|asp|aspx|jsp|py|pl|sh)$\">\n")
                    f.write("    Order allow,deny\n")
                    f.write("    Deny from all\n")
                    f.write("</Files>\n")
            
            logger.info(f"安全上传目录创建成功: {sub_dir}")
            return sub_dir
            
        except Exception as e:
            logger.error(f"创建安全上传目录失败: {str(e)}")
            raise SecurityError(f"创建安全上传目录失败: {str(e)}")
    
    @classmethod
    def sanitize_file_content(cls, file_path: str) -> bool:
        """
        清理文件内容，移除潜在的恶意代码
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功清理
        """
        try:
            logger.info(f"开始清理文件内容: {file_path}")
            
            # 检查文件是否为图片
            if not cls._is_image_file(file_path):
                raise SecurityError("文件不是有效的图片格式")
            
            # 使用 PIL 重新保存图片以移除潜在的恶意内容
            with Image.open(file_path) as img:
                # 转换为RGB模式（移除可能的恶意元数据）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 保持透明度
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')
                
                # 重新保存图片
                img.save(file_path, optimize=True, quality=95)
            
            logger.info(f"文件内容清理完成: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"文件内容清理失败: {file_path}, 错误: {str(e)}")
            return False
    
    @classmethod
    def check_file_access_permission(cls, file_path: str, user_id: int = None) -> bool:
        """
        检查文件访问权限
        
        Args:
            file_path: 文件路径
            user_id: 用户ID
            
        Returns:
            bool: 是否有访问权限
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False
            
            # 检查文件是否在允许的目录内
            allowed_dirs = [
                current_app.config.get('REVIEW_IMAGES_UPLOAD_FOLDER', 'uploads/review_images')
            ]
            
            # 转换为绝对路径
            abs_file_path = os.path.abspath(file_path)
            
            is_allowed = False
            for allowed_dir in allowed_dirs:
                if not os.path.isabs(allowed_dir):
                    allowed_dir = os.path.join(current_app.root_path, allowed_dir)
                
                abs_allowed_dir = os.path.abspath(allowed_dir)
                
                # 检查文件是否在允许的目录内
                if abs_file_path.startswith(abs_allowed_dir):
                    is_allowed = True
                    break
            
            if not is_allowed:
                logger.warning(f"文件访问被拒绝，文件不在允许的目录内: {file_path}")
                return False
            
            # TODO: 根据需要添加更多权限检查逻辑
            # 例如：检查用户是否有权限访问特定的复盘记录
            
            return True
            
        except Exception as e:
            logger.error(f"检查文件访问权限失败: {file_path}, 错误: {str(e)}")
            return False
    
    @classmethod
    def _validate_filename_security(cls, filename: str) -> None:
        """验证文件名安全性"""
        if not filename or len(filename.strip()) == 0:
            raise ValidationError("文件名不能为空")
        
        # 检查文件名长度
        if len(filename) > 255:
            raise ValidationError("文件名过长")
        
        # 检查危险字符
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
        for char in dangerous_chars:
            if char in filename:
                raise SecurityError(f"文件名包含危险字符: {char}")
        
        # 检查是否以点开头（隐藏文件）
        if filename.startswith('.'):
            raise SecurityError("不允许上传隐藏文件")
    
    @classmethod
    def _get_file_extension(cls, filename: str) -> str:
        """获取文件扩展名"""
        if '.' not in filename:
            raise ValidationError("文件必须有扩展名")
        
        return filename.rsplit('.', 1)[1].lower()
    
    @classmethod
    def _validate_file_extension(cls, extension: str) -> None:
        """验证文件扩展名"""
        if extension in cls.DANGEROUS_EXTENSIONS:
            raise SecurityError(f"危险的文件扩展名: {extension}")
        
        if extension not in cls.ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(f"不支持的文件格式，支持的格式: {', '.join(cls.ALLOWED_IMAGE_EXTENSIONS)}")
    
    @classmethod
    def _validate_mime_type(cls, mime_type: str) -> None:
        """验证MIME类型"""
        if mime_type and mime_type not in cls.ALLOWED_MIME_TYPES:
            raise ValidationError(f"不支持的文件类型: {mime_type}")
    
    @classmethod
    def _get_file_size(cls, file: FileStorage) -> int:
        """获取文件大小"""
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        return file_size
    
    @classmethod
    def _validate_file_size(cls, file_size: int) -> None:
        """验证文件大小"""
        if file_size == 0:
            raise ValidationError("文件不能为空")
        
        if file_size > cls.MAX_FILE_SIZE:
            raise ValidationError(f"文件大小不能超过 {cls.MAX_FILE_SIZE / (1024 * 1024):.1f} MB")
    
    @classmethod
    def _validate_file_content(cls, file: FileStorage) -> None:
        """验证文件内容"""
        # 读取文件头部字节
        file.seek(0)
        header = file.read(1024)
        file.seek(0)
        
        # 检查是否包含可执行文件标识
        executable_signatures = [
            b'MZ',  # Windows PE
            b'\x7fELF',  # Linux ELF
            b'\xfe\xed\xfa',  # Mach-O
            b'<?php',  # PHP
            b'<script',  # JavaScript
        ]
        
        for signature in executable_signatures:
            if signature in header:
                raise SecurityError("文件包含可执行代码")
    
    @classmethod
    def _validate_image_format(cls, file: FileStorage) -> Dict[str, Any]:
        """验证图片格式"""
        try:
            file.seek(0)
            
            # 使用 PIL 验证图片
            with Image.open(file) as img:
                # 检查图片尺寸
                width, height = img.size
                if width > cls.MAX_IMAGE_DIMENSION or height > cls.MAX_IMAGE_DIMENSION:
                    raise ValidationError(f"图片尺寸过大，最大允许 {cls.MAX_IMAGE_DIMENSION}x{cls.MAX_IMAGE_DIMENSION}")
                
                # 检查图片格式
                if img.format.lower() not in ['jpeg', 'png', 'gif', 'bmp', 'webp']:
                    raise ValidationError(f"不支持的图片格式: {img.format}")
                
                image_info = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': width,
                    'height': height
                }
                
                return image_info
                
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"无效的图片文件: {str(e)}")
    
    @classmethod
    def _is_image_file(cls, file_path: str) -> bool:
        """检查文件是否为图片"""
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False


class InputSanitizer:
    """输入清理器"""
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = None) -> str:
        """
        清理字符串输入
        
        Args:
            input_str: 输入字符串
            max_length: 最大长度
            
        Returns:
            str: 清理后的字符串
        """
        if not input_str:
            return ""
        
        # 移除前后空白
        sanitized = input_str.strip()
        
        # 长度限制
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        # 移除危险字符
        dangerous_chars = ['<', '>', '"', "'", '&', '\0', '\r', '\n']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized
    
    @staticmethod
    def sanitize_html(input_html: str) -> str:
        """
        清理HTML输入
        
        Args:
            input_html: 输入HTML
            
        Returns:
            str: 清理后的HTML
        """
        import html
        
        if not input_html:
            return ""
        
        # HTML转义
        sanitized = html.escape(input_html)
        
        return sanitized
    
    @staticmethod
    def validate_stock_code(stock_code: str) -> str:
        """
        验证和清理股票代码
        
        Args:
            stock_code: 股票代码
            
        Returns:
            str: 清理后的股票代码
        """
        if not stock_code:
            raise ValidationError("股票代码不能为空")
        
        # 移除空白并转换为大写
        sanitized = stock_code.strip().upper()
        
        # 检查格式（6位数字）
        if not sanitized.isdigit() or len(sanitized) != 6:
            raise ValidationError("股票代码必须是6位数字")
        
        return sanitized
    
    @staticmethod
    def validate_numeric_input(value: Any, min_value: float = None, max_value: float = None) -> float:
        """
        验证数值输入
        
        Args:
            value: 输入值
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            float: 验证后的数值
        """
        try:
            numeric_value = float(value)
            
            if min_value is not None and numeric_value < min_value:
                raise ValidationError(f"数值不能小于 {min_value}")
            
            if max_value is not None and numeric_value > max_value:
                raise ValidationError(f"数值不能大于 {max_value}")
            
            return numeric_value
            
        except (ValueError, TypeError):
            raise ValidationError("无效的数值格式")


class SecurityError(Exception):
    """安全错误异常"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code or "SECURITY_ERROR"
        super().__init__(self.message)