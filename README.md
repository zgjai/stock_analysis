# 股票交易记录和复盘系统

个人投资管理工具，帮助用户记录每日交易操作、进行复盘分析、管理股票观察池，并提供收益统计分析。

## 功能特性

- 📈 交易记录管理：记录买卖操作，支持止损止盈设置
- 📊 复盘分析：5项评分标准的持仓复盘
- 👀 股票池管理：待观测池和待买入池管理
- 📸 案例管理：股票走势截图案例库
- 📈 统计分析：收益统计和分析报表
- 🔄 数据同步：基于Git的数据版本控制

## 技术架构

- **后端**: Python Flask + SQLAlchemy + SQLite
- **数据源**: AKShare股票数据接口
- **前端**: HTML5 + Bootstrap + JavaScript
- **数据存储**: SQLite本地数据库

## 快速开始

### 一键启动（推荐）
```bash
# Windows用户
start.bat

# macOS/Linux用户
./start.sh

# 或使用Python启动脚本
python start.py
```

### 手动启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd stock-trading-journal

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python init_db.py

# 5. 启动应用
python run.py
```

应用将在 http://localhost:5000 启动

## 文档指南

- **[用户使用手册](USER_MANUAL.md)** - 详细的功能使用说明
- **[API文档](API_DOCUMENTATION.md)** - 完整的API接口文档  
- **[部署配置指南](DEPLOYMENT_GUIDE.md)** - 安装、配置和维护指南
- **[Git同步指南](GIT_SYNC_GUIDE.md)** - 多设备数据同步配置
- **[数据库文档](DATABASE_README.md)** - 数据库结构和操作说明
- **[前端开发文档](FRONTEND_README.md)** - 前端架构和开发指南

## 数据管理

### 备份和恢复
```bash
# 创建备份
python backup_manager.py create --auto

# 列出备份
python backup_manager.py list

# 恢复备份
python backup_manager.py restore backup_filename.zip --confirm

# 清理过期备份
python backup_manager.py cleanup --days 30 --confirm
```

### Git同步
```bash
# 同步数据到Git仓库
python sync.py

# 查看Git状态
python sync.py status

# 初始化Git仓库
python sync.py init --remote https://github.com/yourusername/repo.git
```

## API接口

### 健康检查
- `GET /api/health` - 服务健康检查

### API信息
- `GET /api/` - 获取API基本信息

## 项目结构

```
stock-trading-journal/
├── app.py                 # 应用入口
├── config.py             # 配置文件
├── extensions.py         # Flask扩展
├── error_handlers.py     # 错误处理
├── init_db.py           # 数据库初始化
├── run.py               # 启动脚本
├── requirements.txt     # 依赖包
├── api/                 # API路由
├── models/              # 数据模型
├── services/            # 业务服务
├── utils/               # 工具函数
├── data/                # 数据库文件
└── uploads/             # 上传文件
```

## 开发指南

### 添加新的API端点

1. 在 `api/routes.py` 中添加路由
2. 在 `services/` 中添加业务逻辑
3. 在 `models/` 中添加数据模型（如需要）

### 数据库迁移

```bash
# 生成迁移文件
flask db migrate -m "描述信息"

# 应用迁移
flask db upgrade
```

## 许可证

MIT License