#!/bin/bash
# 股票交易记录和复盘系统启动脚本 (Linux/macOS)
# Stock Trading Journal System Startup Script (Linux/macOS)

set -e

echo "股票交易记录和复盘系统 - 启动脚本"
echo "Stock Trading Journal System - Startup Script"
echo "=============================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    echo "Error: Python3 not found"
    exit 1
fi

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "建议: 使用虚拟环境运行此应用"
    echo "Recommendation: Use virtual environment to run this application"
    echo "创建虚拟环境: python3 -m venv venv"
    echo "激活虚拟环境: source venv/bin/activate"
    echo ""
fi

# 安装依赖
if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到requirements.txt文件"
    echo "Error: requirements.txt file not found"
    exit 1
fi

echo "检查并安装依赖包..."
echo "Checking and installing dependencies..."
pip install -r requirements.txt

# 设置端口环境变量（避免5000端口冲突）
export PORT=5001

# 运行Python启动脚本
echo "启动应用程序..."
echo "Starting application..."
python3 start.py