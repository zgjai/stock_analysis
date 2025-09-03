# 历史交易记录功能部署指南

## 概述

本指南详细说明了如何部署历史交易记录功能到生产环境。该功能包括历史交易数据展示、复盘功能和图片上传等特性。

## 部署前准备

### 1. 系统要求

- Python 3.8+
- SQLite 3.x (或 MySQL/PostgreSQL)
- Nginx (推荐)
- 至少 2GB 可用磁盘空间
- 至少 512MB 可用内存

### 2. 依赖检查

```bash
# 检查Python版本
python3 --version

# 检查pip
pip3 --version

# 安装系统依赖 (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-dev python3-pip nginx supervisor

# 安装系统依赖 (CentOS/RHEL)
sudo yum install python3-devel python3-pip nginx supervisor
```

## 部署步骤

### 第一步：环境配置

1. **克隆项目代码**
```bash
git clone <repository-url>
cd historical-trading-records
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
# 复制环境配置文件
cp .env.production .env

# 编辑配置文件
nano .env
```

重要配置项：
- `SECRET_KEY`: 设置强密码
- `DATABASE_URL`: 配置数据库连接
- `UPLOAD_FOLDER`: 设置上传目录路径

### 第二步：存储配置

运行存储配置脚本：

```bash
python3 scripts/setup_storage.py --env production
```

这将：
- 创建必要的目录结构
- 设置正确的文件权限
- 生成Nginx和systemd配置文件

### 第三步：数据库迁移

1. **运行迁移脚本（干运行）**
```bash
python3 scripts/deploy_migrations.py --env production --dry-run
```

2. **执行实际迁移**
```bash
python3 scripts/deploy_migrations.py --env production
```

3. **验证数据库结构**
```bash
# 检查表是否创建成功
sqlite3 data/trading_journal.db ".tables"
```

### 第四步：Web服务器配置

1. **配置Nginx**
```bash
# 复制生成的配置文件
sudo cp deployment/nginx.conf /etc/nginx/sites-available/historical-trading
sudo ln -s /etc/nginx/sites-available/historical-trading /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

2. **配置systemd服务**
```bash
# 复制服务文件
sudo cp deployment/historical-trading.service /etc/systemd/system/

# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable historical-trading

# 启动服务
sudo systemctl start historical-trading
```

### 第五步：部署测试

运行部署测试脚本：

```bash
python3 scripts/deployment_test.py --env production --base-url http://your-domain.com
```

测试内容包括：
- 数据库连接
- 表结构完整性
- 目录权限
- API端点响应
- 静态文件服务
- 安全头配置

### 第六步：备份配置

1. **创建初始备份**
```bash
python3 scripts/backup_restore.py backup --type full --env production
```

2. **设置定时备份**
```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天凌晨2点备份）
0 2 * * * /path/to/project/venv/bin/python /path/to/project/scripts/backup_restore.py backup --type full --env production

# 添加清理任务（每周清理旧备份）
0 3 * * 0 /path/to/project/venv/bin/python /path/to/project/scripts/backup_restore.py cleanup --retention-days 30 --env production
```

## 监控和维护

### 日志监控

```bash
# 查看应用日志
tail -f logs/app.log

# 查看系统服务日志
sudo journalctl -u historical-trading -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 性能监控

1. **检查服务状态**
```bash
sudo systemctl status historical-trading
sudo systemctl status nginx
```

2. **监控资源使用**
```bash
# CPU和内存使用
top -p $(pgrep -f "historical-trading")

# 磁盘使用
df -h
du -sh uploads/
```

### 备份管理

```bash
# 列出所有备份
python3 scripts/backup_restore.py list --env production

# 验证备份完整性
python3 scripts/backup_restore.py verify --path backups/full_backup_20240101_020000.tar.gz --env production

# 恢复备份（谨慎操作）
python3 scripts/backup_restore.py restore --path backups/full_backup_20240101_020000.tar.gz --env production
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库文件权限
   - 验证DATABASE_URL配置
   - 确认数据目录存在

2. **文件上传失败**
   - 检查uploads目录权限
   - 验证MAX_CONTENT_LENGTH设置
   - 确认磁盘空间充足

3. **静态文件无法访问**
   - 检查Nginx配置
   - 验证static目录权限
   - 确认文件路径正确

4. **服务无法启动**
   - 查看systemd日志
   - 检查端口占用
   - 验证Python环境

### 调试命令

```bash
# 测试应用启动
python3 app.py

# 检查端口占用
sudo netstat -tlnp | grep :5001

# 测试数据库连接
python3 -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.engine.execute('SELECT 1')"

# 检查文件权限
ls -la uploads/
ls -la data/
```

## 安全建议

1. **定期更新**
   - 保持系统和依赖包更新
   - 定期检查安全漏洞

2. **访问控制**
   - 配置防火墙规则
   - 使用HTTPS
   - 限制文件上传类型和大小

3. **监控告警**
   - 设置日志监控
   - 配置错误告警
   - 监控异常访问

4. **备份策略**
   - 定期备份数据
   - 测试恢复流程
   - 异地备份存储

## 升级指南

### 应用升级

1. **备份当前版本**
```bash
python3 scripts/backup_restore.py backup --type full --env production
```

2. **更新代码**
```bash
git pull origin main
```

3. **更新依赖**
```bash
pip install -r requirements.txt
```

4. **运行迁移**
```bash
python3 scripts/deploy_migrations.py --env production
```

5. **重启服务**
```bash
sudo systemctl restart historical-trading
```

6. **验证升级**
```bash
python3 scripts/deployment_test.py --env production
```

### 回滚流程

如果升级出现问题：

1. **停止服务**
```bash
sudo systemctl stop historical-trading
```

2. **恢复备份**
```bash
python3 scripts/backup_restore.py restore --path backups/full_backup_before_upgrade.tar.gz --env production
```

3. **重启服务**
```bash
sudo systemctl start historical-trading
```

## 联系支持

如果遇到部署问题，请：

1. 检查部署测试报告：`deployment_test_report.json`
2. 收集相关日志文件
3. 记录错误信息和复现步骤
4. 联系技术支持团队

---

**注意**: 在生产环境部署前，请务必在测试环境中完整验证所有功能。