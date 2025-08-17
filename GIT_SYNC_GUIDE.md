# Git同步配置指南

## 目录
- [概述](#概述)
- [初始设置](#初始设置)
- [同步策略](#同步策略)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [自动化脚本](#自动化脚本)

## 概述

股票交易记录和复盘系统支持通过Git进行数据同步，让您可以在多个设备间保持数据一致性，同时享受版本控制的好处。

### 同步内容
- **数据库文件**: `data/trading_journal.db`
- **上传图片**: `uploads/` 目录下的所有文件
- **配置文件**: 系统配置和用户设置
- **备份文件**: `backups/` 目录（可选）

### 不同步内容
- **日志文件**: `logs/` 目录
- **临时文件**: 缓存和临时数据
- **虚拟环境**: `venv/` 目录
- **系统文件**: `__pycache__/`, `.DS_Store` 等

## 初始设置

### 1. 创建Git仓库

#### 方式一：从现有项目创建
```bash
# 在项目根目录执行
git init
git add .
git commit -m "Initial commit: Stock Trading Journal System"

# 添加远程仓库（替换为您的仓库地址）
git remote add origin https://github.com/yourusername/stock-trading-journal.git
git push -u origin main
```

#### 方式二：克隆现有仓库
```bash
# 克隆仓库
git clone https://github.com/yourusername/stock-trading-journal.git
cd stock-trading-journal

# 安装依赖并初始化
pip install -r requirements.txt
python init_db.py
```

### 2. 配置.gitignore文件

系统已包含合适的`.gitignore`配置：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# 日志文件
logs/
*.log

# 临时文件
.DS_Store
Thumbs.db
*.tmp
*.temp

# IDE文件
.vscode/
.idea/
*.swp
*.swo

# 系统特定文件
.pytest_cache/
.coverage
htmlcov/

# 可选：备份文件（如果不想同步备份）
# backups/
```

### 3. 配置Git用户信息

```bash
# 设置用户名和邮箱
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 可选：为此项目单独设置
git config --local user.name "Your Name"
git config --local user.email "your.email@example.com"
```

## 同步策略

### 日常同步流程

#### 1. 工作开始前同步
```bash
# 拉取最新更改
git pull origin main

# 如果有冲突，解决后提交
git add .
git commit -m "Resolve merge conflicts"
```

#### 2. 工作结束后推送
```bash
# 添加所有更改
git add .

# 提交更改（使用有意义的提交信息）
git commit -m "Add trading records for 2024-01-01"

# 推送到远程仓库
git push origin main
```

### 自动同步脚本

创建自动同步脚本 `sync.py`：

```python
#!/usr/bin/env python3
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """执行命令并处理错误"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ {description} 失败:")
            print(result.stderr)
            return False
        else:
            print(f"✅ {description} 成功")
            if result.stdout.strip():
                print(result.stdout)
            return True
    except Exception as e:
        print(f"❌ {description} 出错: {str(e)}")
        return False

def sync_data():
    """同步数据"""
    print("🔄 开始数据同步...")
    
    # 检查Git状态
    if not run_command("git status --porcelain", "检查Git状态"):
        return False
    
    # 拉取远程更改
    if not run_command("git pull origin main", "拉取远程更改"):
        return False
    
    # 添加本地更改
    if not run_command("git add data/ uploads/", "添加数据文件"):
        return False
    
    # 检查是否有更改需要提交
    result = subprocess.run("git diff --cached --quiet", shell=True)
    if result.returncode == 0:
        print("📝 没有新的更改需要提交")
        return True
    
    # 提交更改
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Auto sync: {timestamp}"
    
    if not run_command(f'git commit -m "{commit_message}"', "提交更改"):
        return False
    
    # 推送到远程
    if not run_command("git push origin main", "推送到远程仓库"):
        return False
    
    print("🎉 数据同步完成!")
    return True

if __name__ == "__main__":
    success = sync_data()
    sys.exit(0 if success else 1)
```

## 最佳实践

### 1. 提交信息规范

使用清晰的提交信息：

```bash
# 好的提交信息示例
git commit -m "Add trading records for AAPL and TSLA on 2024-01-01"
git commit -m "Update review analysis for current holdings"
git commit -m "Add new case study screenshots"
git commit -m "Fix: Correct trade record for stock 000001"

# 避免的提交信息
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

### 2. 分支管理策略

#### 单用户场景（推荐）
```bash
# 直接在main分支工作
git checkout main
git pull origin main
# 进行更改...
git add .
git commit -m "Descriptive message"
git push origin main
```

#### 多设备场景
```bash
# 为每个设备创建分支
git checkout -b device-laptop
git checkout -b device-desktop

# 定期合并到main分支
git checkout main
git merge device-laptop
git push origin main
```

### 3. 冲突解决

当多个设备同时修改数据时可能出现冲突：

```bash
# 拉取时出现冲突
git pull origin main
# Auto-merging data/trading_journal.db
# CONFLICT (content): Merge conflict in data/trading_journal.db

# 解决冲突的步骤：
# 1. 备份当前数据
cp data/trading_journal.db data/trading_journal.db.backup

# 2. 选择要保留的版本
git checkout --ours data/trading_journal.db    # 保留本地版本
# 或
git checkout --theirs data/trading_journal.db  # 保留远程版本

# 3. 标记冲突已解决
git add data/trading_journal.db

# 4. 完成合并
git commit -m "Resolve database merge conflict"
```

### 4. 数据安全措施

#### 定期备份
```bash
# 在同步前创建备份
python backup_manager.py create --auto

# 同步数据
python sync.py

# 验证同步结果
git log --oneline -5
```

#### 使用Git钩子
创建 `.git/hooks/pre-commit` 文件：

```bash
#!/bin/bash
# 提交前自动备份数据库

echo "Creating backup before commit..."
python backup_manager.py create --auto

if [ $? -ne 0 ]; then
    echo "Backup failed, aborting commit"
    exit 1
fi

echo "Backup created successfully"
exit 0
```

### 5. 多设备同步工作流

#### 设备A（主要设备）
```bash
# 每日开始
git pull origin main
python run.py  # 开始工作

# 每日结束
git add .
git commit -m "Daily trading records - $(date +%Y-%m-%d)"
git push origin main
```

#### 设备B（辅助设备）
```bash
# 使用前同步
git pull origin main

# 使用后同步
git add .
git commit -m "Updates from device B - $(date +%Y-%m-%d)"
git push origin main
```

## 常见问题

### Q: 数据库文件冲突怎么办？
A: SQLite数据库文件是二进制文件，Git无法自动合并。建议：
1. 选择一个版本作为主版本
2. 手动导入另一个版本的数据
3. 使用备份恢复功能

### Q: 图片文件占用空间太大？
A: 可以考虑：
1. 压缩图片文件
2. 使用Git LFS存储大文件
3. 定期清理不需要的图片

### Q: 如何在新设备上设置？
A: 
```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/stock-trading-journal.git
cd stock-trading-journal

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行系统
python start.py
```

### Q: 忘记推送数据怎么办？
A: 
```bash
# 检查未推送的提交
git log origin/main..HEAD

# 推送所有未推送的提交
git push origin main
```

## 自动化脚本

### 定时同步脚本

创建 `auto_sync.py`：

```python
#!/usr/bin/env python3
"""
自动同步脚本 - 可配置定时任务
"""

import schedule
import time
import subprocess
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sync.log'),
        logging.StreamHandler()
    ]
)

def sync_data():
    """执行数据同步"""
    try:
        logging.info("开始自动同步...")
        
        # 执行同步脚本
        result = subprocess.run(['python', 'sync.py'], capture_output=True, text=True)
        
        if result.returncode == 0:
            logging.info("自动同步成功")
        else:
            logging.error(f"自动同步失败: {result.stderr}")
            
    except Exception as e:
        logging.error(f"自动同步出错: {str(e)}")

def main():
    """主函数"""
    # 每天晚上10点自动同步
    schedule.every().day.at("22:00").do(sync_data)
    
    # 每4小时检查一次
    schedule.every(4).hours.do(sync_data)
    
    logging.info("自动同步服务已启动")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    main()
```

### 系统服务配置（Linux）

创建 `/etc/systemd/system/trading-journal-sync.service`：

```ini
[Unit]
Description=Trading Journal Auto Sync Service
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/stock-trading-journal
ExecStart=/path/to/stock-trading-journal/venv/bin/python auto_sync.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable trading-journal-sync
sudo systemctl start trading-journal-sync
sudo systemctl status trading-journal-sync
```

## 安全建议

1. **私有仓库**: 使用私有Git仓库存储敏感的交易数据
2. **访问控制**: 设置适当的仓库访问权限
3. **定期备份**: 除了Git同步，还要定期创建本地备份
4. **敏感信息**: 不要在提交信息中包含敏感的交易细节
5. **网络安全**: 使用HTTPS或SSH连接Git仓库

---

通过遵循这些指南，您可以安全、高效地在多个设备间同步股票交易记录数据，同时享受版本控制带来的便利。