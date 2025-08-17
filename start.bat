@echo off
REM 股票交易记录和复盘系统启动脚本 (Windows)
REM Stock Trading Journal System Startup Script (Windows)

echo 股票交易记录和复盘系统 - 启动脚本
echo Stock Trading Journal System - Startup Script
echo ==============================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python
    echo Error: Python not found
    pause
    exit /b 1
)

REM 检查虚拟环境
if "%VIRTUAL_ENV%"=="" (
    echo 建议: 使用虚拟环境运行此应用
    echo Recommendation: Use virtual environment to run this application
    echo 创建虚拟环境: python -m venv venv
    echo 激活虚拟环境: venv\Scripts\activate
    echo.
)

REM 检查requirements.txt
if not exist "requirements.txt" (
    echo 错误: 未找到requirements.txt文件
    echo Error: requirements.txt file not found
    pause
    exit /b 1
)

echo 检查并安装依赖包...
echo Checking and installing dependencies...
pip install -r requirements.txt

REM 运行Python启动脚本
echo 启动应用程序...
echo Starting application...
python start.py

pause