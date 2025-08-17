# 部署配置指南

## 目录
- [快速开始](#快速开始)
- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [数据管理](#数据管理)
- [维护和监控](#维护和监控)
- [故障排除](#故障排除)

## 快速开始

### 一键启动（推荐）

#### Windows
```cmd
# 双击运行
start.bat
```

#### macOS/Linux
```bash
# 终端运行
./start.sh
```

#### 手动启动
```bash
# 使用Python启动脚本
python start.py
```

### 访问系统
启动成功后，在浏览器中访问：
- 本地访问: http://localhost:5000
- 局域网访问: http://[您的IP地址]:5000

## 系统要求

### 最低要求
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **内存**: 4GB RAM
- **存储**: 2GB 可用空间
- **网络**: 互联网连接（用于获取股票数据）

### 推荐配置
- **操作系统**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.9 或更高版本
- **内存**: 8GB RAM
- **存储**: 10GB 可用空间（包含数据和备份）
- **网络**: 稳定的宽带连接

## 安装步骤

### 1. 环境准备

#### 安装Python
```bash
# 检查Python版本
python --version
python3 --version

# 如果没有Python 3.8+，请从官网下载安装
# https://www.python.org/downloads/
```

#### 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 获取代码

#### 方式一：下载源码包
1. 下载项目源码包
2. 解压到目标目录
3. 进入项目目录

#### 方式二：Git克隆
```bash
git clone https://github.com/yourusername/stock-trading-journal.git
cd stock-trading-journal
```

### 3. 安装依赖
```bash
# 安装Python依赖包
pip install -r requirements.txt

# 如果安装速度慢，可以使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 4. 初始化系统
```bash
# 运行启动脚本（会自动初始化）
python start.py

# 或手动初始化数据库
python init_db.py
```

### 5. 验证安装
```bash
# 检查数据库文件
ls -la data/trading_journal.db

# 检查必要目录
ls -la uploads/ logs/ backups/

# 启动系统测试
python run.py
```

## 配置说明

### 主配置文件

#### config.py
系统主配置文件，包含数据库、文件上传等基础配置。

#### config.local.py
本地开发配置，可以覆盖主配置文件的设置：

```python
# 数据库配置
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/trading_journal.db'

# 文件上传配置
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/trading_journal.log'

# AKShare配置
AKSHARE_TIMEOUT = 30
PRICE_CACHE_MINUTES = 5
```

### 环境变量配置

创建 `.env` 文件：
```bash
# Flask配置
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=sqlite:///data/trading_journal.db

# 日志级别
LOG_LEVEL=INFO

# AKShare配置
AKSHARE_TIMEOUT=30
```

### 端口配置

默认端口为5000，如需修改：

#### 方式一：修改run.py
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

#### 方式二：环境变量
```bash
export FLASK_RUN_PORT=8080
python run.py
```

### 网络访问配置

#### 仅本地访问
```python
app.run(host='127.0.0.1', port=5000)
```

#### 局域网访问
```python
app.run(host='0.0.0.0', port=5000)
```

## 数据管理

### 数据存储结构
```
data/
├── trading_journal.db          # 主数据库文件
└── trading_journal_backup_*.db # 自动备份文件

uploads/
├── *.png, *.jpg, *.jpeg       # 上传的图片文件
└── ...

backups/
├── trading_journal_backup_*.zip # 完整备份文件
└── ...

logs/
├── trading_journal.log         # 应用日志
└── ...
```

### 备份策略

#### 自动备份
系统每7天自动创建备份，保留30天内的备份文件。

#### 手动备份
```bash
# 创建备份
python backup_manager.py create --auto

# 列出备份
python backup_manager.py list

# 恢复备份
python backup_manager.py restore backup_filename.zip --confirm
```

### 数据迁移

#### 导出数据
```bash
# 创建完整备份
python backup_manager.py create --name migration_backup

# 导出统计数据
curl "http://localhost:5000/api/analytics/export?format=excel" -o trading_data.xlsx
```

#### 导入数据
```bash
# 恢复备份
python backup_manager.py restore migration_backup.zip --confirm

# 重启系统
python run.py
```

## 维护和监控

### 日志管理

#### 查看日志
```bash
# 查看最新日志
tail -f logs/trading_journal.log

# 查看错误日志
grep "ERROR" logs/trading_journal.log

# 查看特定时间的日志
grep "2024-01-01" logs/trading_journal.log
```

#### 日志轮转
系统自动进行日志轮转，保留最近10个日志文件，每个文件最大10MB。

### 性能监控

#### 数据库性能
```bash
# 检查数据库大小
ls -lh data/trading_journal.db

# 数据库统计信息
sqlite3 data/trading_journal.db "SELECT name, COUNT(*) FROM sqlite_master WHERE type='table' GROUP BY name;"
```

#### 系统资源
```bash
# 检查磁盘使用
df -h

# 检查内存使用
free -h  # Linux
top      # macOS/Linux
```

### 定期维护任务

#### 每日任务
- 检查系统运行状态
- 查看错误日志
- 验证数据备份

#### 每周任务
- 清理临时文件
- 检查磁盘空间
- 更新股票价格数据

#### 每月任务
- 清理过期日志
- 清理过期备份
- 系统性能评估

### 自动化维护脚本

创建 `maintenance.py`：
```python
#!/usr/bin/env python3
"""
系统维护脚本
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from services.backup_service import BackupService

def cleanup_logs():
    """清理过期日志"""
    logs_dir = Path('logs')
    cutoff_date = datetime.now() - timedelta(days=30)
    
    for log_file in logs_dir.glob('*.log.*'):
        if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
            log_file.unlink()
            print(f"删除过期日志: {log_file}")

def cleanup_temp_files():
    """清理临时文件"""
    temp_patterns = ['*.tmp', '*.temp', '.DS_Store', 'Thumbs.db']
    
    for pattern in temp_patterns:
        for temp_file in Path('.').rglob(pattern):
            temp_file.unlink()
            print(f"删除临时文件: {temp_file}")

def check_disk_space():
    """检查磁盘空间"""
    total, used, free = shutil.disk_usage('.')
    free_gb = free // (1024**3)
    
    if free_gb < 1:
        print(f"警告: 磁盘空间不足 ({free_gb}GB)")
        return False
    
    print(f"磁盘空间充足: {free_gb}GB 可用")
    return True

def auto_backup():
    """自动备份检查"""
    backup_service = BackupService()
    result = backup_service.auto_backup_check()
    
    if result['success'] and result['needs_backup']:
        print("执行自动备份...")
        backup_result = backup_service.create_backup()
        if backup_result['success']:
            print(f"自动备份完成: {backup_result['backup_name']}")
        else:
            print(f"自动备份失败: {backup_result['error']}")

def main():
    """主维护函数"""
    print(f"开始系统维护 - {datetime.now()}")
    
    cleanup_logs()
    cleanup_temp_files()
    check_disk_space()
    auto_backup()
    
    print("系统维护完成")

if __name__ == '__main__':
    main()
```

## 故障排除

### 常见问题

#### 1. 启动失败
**症状**: 运行start.py时出错
**解决方案**:
```bash
# 检查Python版本
python --version

# 检查依赖安装
pip list | grep -E "(flask|sqlalchemy|akshare)"

# 查看详细错误
python start.py 2>&1 | tee startup.log
```

#### 2. 数据库错误
**症状**: 数据库操作失败
**解决方案**:
```bash
# 检查数据库文件
ls -la data/trading_journal.db

# 验证数据库完整性
sqlite3 data/trading_journal.db "PRAGMA integrity_check;"

# 重新初始化数据库
mv data/trading_journal.db data/trading_journal.db.backup
python init_db.py
```

#### 3. 端口占用
**症状**: 端口5000被占用
**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# 杀死占用进程或更改端口
export FLASK_RUN_PORT=8080
python run.py
```

#### 4. 权限问题
**症状**: 文件读写权限错误
**解决方案**:
```bash
# 检查文件权限
ls -la data/ uploads/ logs/

# 修复权限
chmod -R 755 data/ uploads/ logs/
chown -R $USER:$USER data/ uploads/ logs/
```

#### 5. 网络连接问题
**症状**: 无法获取股票数据
**解决方案**:
```bash
# 测试网络连接
ping baidu.com

# 检查防火墙设置
# 尝试手动获取数据
python -c "import akshare as ak; print(ak.stock_zh_a_spot_em().head())"
```

### 日志分析

#### 错误级别
- **ERROR**: 严重错误，需要立即处理
- **WARNING**: 警告信息，建议关注
- **INFO**: 一般信息，正常运行记录
- **DEBUG**: 调试信息，开发时使用

#### 常见错误模式
```bash
# 数据库连接错误
grep "database" logs/trading_journal.log

# API调用错误
grep "akshare\|API" logs/trading_journal.log

# 文件操作错误
grep "FileNotFoundError\|PermissionError" logs/trading_journal.log
```

### 性能优化

#### 数据库优化
```sql
-- 重建索引
REINDEX;

-- 清理数据库
VACUUM;

-- 分析查询计划
EXPLAIN QUERY PLAN SELECT * FROM trade_records WHERE stock_code = '000001';
```

#### 系统优化
```bash
# 清理Python缓存
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# 优化图片文件
# 可以使用工具压缩uploads目录中的图片
```

### 恢复策略

#### 数据恢复
1. **从备份恢复**:
   ```bash
   python backup_manager.py list
   python backup_manager.py restore latest_backup.zip --confirm
   ```

2. **从Git恢复**:
   ```bash
   git pull origin main
   python init_db.py  # 如果需要
   ```

3. **部分数据恢复**:
   ```bash
   # 恢复特定表的数据
   sqlite3 data/trading_journal.db ".dump trade_records" > trade_records.sql
   ```

#### 系统重置
```bash
# 完全重置（谨慎操作）
rm -rf data/ uploads/ logs/
python init_db.py
python run.py
```

---

通过遵循这个部署指南，您可以成功安装、配置和维护股票交易记录和复盘系统。如遇到问题，请参考故障排除部分或查看系统日志获取更多信息。