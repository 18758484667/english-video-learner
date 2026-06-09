@echo off
chcp 65001 >nul
cls
echo ========================================
echo   英语学习视频工具 - 后端服务器
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    echo.
    echo 请先安装Python 3.9+: https://www.python.org/
    pause
    exit /b 1
)

echo [✓] Python已安装
echo.

REM 检查虚拟环境
if not exist "venv" (
    echo [1/4] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo [2/4] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败
    pause
    exit /b 1
)

REM 安装依赖
echo [3/4] 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 首次运行,正在安装依赖(只需一次)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo 依赖已存在
)

REM 初始化数据库
echo [4/4] 初始化数据库...
cd app
python init_db.py
cd ..

echo.
echo ========================================
echo   后端服务器启动中...
echo   API地址: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo   按 Ctrl+C 停止服务器
echo ========================================
echo.

REM 启动服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
