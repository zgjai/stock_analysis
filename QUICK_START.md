# 快速启动指南 / Quick Start Guide

## 问题解决 / Problem Solved

✅ **端口冲突问题已修复** / Port conflict issue fixed
- 应用现在默认使用端口 5001 而不是 5000
- Application now uses port 5001 instead of 5000 by default

✅ **URL路由问题已修复** / URL routing issue fixed
- 修复了模板中的 `url_for` 端点命名问题
- Fixed `url_for` endpoint naming issues in templates
- 所有路由现在正确使用蓝图前缀 `frontend.`
- All routes now correctly use blueprint prefix `frontend.`

## 启动方式 / Startup Methods

### 方法1: Python启动脚本（推荐）
```bash
python3 start.py
```

### 方法2: Shell脚本启动
```bash
chmod +x start.sh
./start.sh
```

### 方法3: 直接启动Flask应用
```bash
python3 run.py
```

## 访问地址 / Access URLs

启动成功后，在浏览器中访问：
After successful startup, access in browser:

- **本地访问**: http://localhost:5001
- **网络访问**: http://192.168.1.2:5001 (根据你的IP地址)

## 端口配置 / Port Configuration

如果需要使用其他端口，可以通过以下方式设置：

### 环境变量方式
```bash
export PORT=8080
python3 start.py
```

### .env文件方式
编辑 `.env` 文件中的 `PORT=5001` 行

## 常见问题 / Common Issues

### 1. 端口仍然被占用
如果5001端口也被占用，启动脚本会自动查找下一个可用端口。

### 2. macOS AirPlay Receiver冲突
如果想继续使用5000端口，可以在系统偏好设置中禁用AirPlay Receiver：
- 系统偏好设置 → 通用 → 隔空投送与接力 → 关闭"隔空播放接收器"

### 3. 权限问题
确保启动脚本有执行权限：
```bash
chmod +x start.sh
```

## 停止应用 / Stop Application

在终端中按 `Ctrl+C` 停止应用程序。

## 开发模式 / Development Mode

应用默认以开发模式启动，包含：
- 调试模式开启
- 代码热重载
- 详细错误信息

生产环境部署请参考 `DEPLOYMENT_GUIDE.md`。
## 验证修复
 / Verify Fix

可以运行以下命令验证路由修复是否成功：
You can run the following command to verify the route fix:

```bash
python3 test_routes_fix.py
```

这将自动测试所有主要路由是否正常工作。
This will automatically test if all main routes are working properly.

## 修复详情 / Fix Details

### 修复的问题 / Fixed Issues:
1. **端点命名冲突**: 模板中使用 `url_for('index')` 但实际端点是 `frontend.index`
2. **蓝图前缀缺失**: 所有前端路由都需要 `frontend.` 前缀
3. **端口占用**: 5000端口被macOS AirPlay Receiver占用

### 修复的文件 / Fixed Files:
- `templates/base.html`: 更新所有导航链接
- `templates/dashboard.html`: 更新页面内链接
- `run.py`: 改进端口配置和启动信息
- `start.py`: 添加智能端口检测功能