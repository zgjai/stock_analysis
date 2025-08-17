"""
通用辅助函数
"""
import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """检查文件扩展名是否被允许"""
    if not filename:
        return False
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def secure_filename_custom(filename):
    """生成安全的文件名，使用UUID避免重名"""
    if not filename:
        return None
    
    # 获取文件扩展名
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    
    return secure_filename(unique_filename)

def ensure_dir_exists(dir_path):
    """确保目录存在，不存在则创建"""
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def get_file_size(file_path):
    """获取文件大小（字节）"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def format_file_size(size_bytes):
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"