#!/usr/bin/env python3
"""
图片文件存储目录和权限配置脚本
"""
import os
import sys
import stat
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config, ProductionConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StorageSetup:
    """存储配置管理器"""
    
    def __init__(self, config_class=Config):
        self.config = config_class()
        self.project_root = project_root
        
    def create_directories(self):
        """创建必要的目录结构"""
        directories = [
            # 基础目录
            self.project_root / 'data',
            self.project_root / 'logs',
            self.project_root / 'backups',
            
            # 上传目录
            self.config.UPLOAD_FOLDER,
            self.config.UPLOAD_FOLDER / 'reviews',
            self.config.UPLOAD_FOLDER / 'reviews' / 'images',
            self.config.UPLOAD_FOLDER / 'temp',
            
            # 静态文件目录
            self.project_root / 'static' / 'uploads',
            self.project_root / 'static' / 'uploads' / 'reviews',
        ]
        
        created_dirs = []
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                created_dirs.append(directory)
                logger.info(f"创建目录: {directory}")
            except Exception as e:
                logger.error(f"创建目录失败 {directory}: {e}")
                return False
        
        return created_dirs
    
    def set_directory_permissions(self, directories):
        """设置目录权限"""
        if os.name == 'nt':  # Windows
            logger.info("Windows系统，跳过权限设置")
            return True
        
        success = True
        for directory in directories:
            try:
                # 设置目录权限为755 (rwxr-xr-x)
                os.chmod(directory, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                logger.info(f"设置目录权限 755: {directory}")
            except Exception as e:
                logger.error(f"设置目录权限失败 {directory}: {e}")
                success = False
        
        return success
    
    def create_gitkeep_files(self, directories):
        """在空目录中创建.gitkeep文件"""
        for directory in directories:
            gitkeep_file = directory / '.gitkeep'
            if not any(directory.iterdir()) or not gitkeep_file.exists():
                try:
                    gitkeep_file.touch()
                    logger.info(f"创建.gitkeep文件: {gitkeep_file}")
                except Exception as e:
                    logger.error(f"创建.gitkeep文件失败 {gitkeep_file}: {e}")
    
    def create_nginx_config(self):
        """创建Nginx配置文件模板"""
        nginx_config = f"""
# Nginx配置 - 历史交易记录功能
server {{
    listen 80;
    server_name your-domain.com;
    
    # 主应用代理
    location / {{
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # 静态文件服务
    location /static/ {{
        alias {self.project_root}/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # 上传文件服务（需要认证）
    location /uploads/ {{
        alias {self.config.UPLOAD_FOLDER}/;
        
        # 安全设置
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        
        # 仅允许图片文件
        location ~* \\.(jpg|jpeg|png|gif)$ {{
            expires 1M;
            add_header Cache-Control "public";
        }}
        
        # 禁止访问其他文件类型
        location ~* \\.(php|jsp|asp|sh|py)$ {{
            deny all;
        }}
    }}
    
    # 文件上传大小限制
    client_max_body_size 16M;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}}
"""
        
        config_file = self.project_root / 'deployment' / 'nginx.conf'
        config_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(nginx_config.strip())
            logger.info(f"创建Nginx配置文件: {config_file}")
            return True
        except Exception as e:
            logger.error(f"创建Nginx配置文件失败: {e}")
            return False
    
    def create_systemd_service(self):
        """创建systemd服务文件"""
        service_config = f"""[Unit]
Description=Historical Trading Records Flask App
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory={self.project_root}
Environment=FLASK_ENV=production
Environment=PYTHONPATH={self.project_root}
ExecStart={sys.executable} {self.project_root}/run.py
Restart=always
RestartSec=10

# 安全设置
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={self.project_root}/data {self.project_root}/logs {self.config.UPLOAD_FOLDER}

[Install]
WantedBy=multi-user.target
"""
        
        service_file = self.project_root / 'deployment' / 'historical-trading.service'
        service_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(service_config.strip())
            logger.info(f"创建systemd服务文件: {service_file}")
            return True
        except Exception as e:
            logger.error(f"创建systemd服务文件失败: {e}")
            return False
    
    def create_security_config(self):
        """创建安全配置文件"""
        security_config = {
            'file_upload': {
                'max_file_size': '16MB',
                'allowed_extensions': ['png', 'jpg', 'jpeg', 'gif'],
                'scan_uploads': True,
                'quarantine_suspicious': True
            },
            'directory_permissions': {
                'uploads': '755',
                'data': '755',
                'logs': '755',
                'temp': '777'
            },
            'nginx_security': {
                'hide_server_tokens': True,
                'rate_limiting': '10r/s',
                'client_max_body_size': '16M'
            }
        }
        
        import json
        config_file = self.project_root / 'deployment' / 'security.json'
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(security_config, f, indent=2, ensure_ascii=False)
            logger.info(f"创建安全配置文件: {config_file}")
            return True
        except Exception as e:
            logger.error(f"创建安全配置文件失败: {e}")
            return False
    
    def setup_all(self):
        """执行完整的存储设置"""
        logger.info("开始存储配置设置...")
        
        # 创建目录
        directories = self.create_directories()
        if not directories:
            return False
        
        # 设置权限
        if not self.set_directory_permissions(directories):
            logger.warning("部分目录权限设置失败")
        
        # 创建.gitkeep文件
        self.create_gitkeep_files(directories)
        
        # 创建配置文件
        self.create_nginx_config()
        self.create_systemd_service()
        self.create_security_config()
        
        logger.info("存储配置设置完成")
        return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='存储配置设置脚本')
    parser.add_argument('--env', choices=['development', 'production'], 
                       default='development', help='运行环境')
    
    args = parser.parse_args()
    
    # 选择配置
    if args.env == 'production':
        config_class = ProductionConfig
    else:
        config_class = Config
    
    # 执行设置
    setup = StorageSetup(config_class)
    success = setup.setup_all()
    
    if success:
        logger.info("存储配置设置成功")
        sys.exit(0)
    else:
        logger.error("存储配置设置失败")
        sys.exit(1)


if __name__ == '__main__':
    main()