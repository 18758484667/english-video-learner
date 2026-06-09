@echo off
chcp 65001 >nul
cls
echo ========================================
echo   英语学习视频工具 - React版
echo ========================================
echo.

REM 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Node.js
    echo.
    echo 请先安装Node.js: https://nodejs.org/
    pause
    exit /b 1
)

echo [✓] Node.js已安装
echo.

cd frontend

REM 检查依赖是否已安装
if not exist "node_modules" (
    echo [1/3] 首次运行,正在安装依赖(只需一次)...
    call npm install
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo.
) else (
    echo [1/3] 依赖已存在,跳过安装
)

echo [2/3] 启动开发服务器...
echo.
echo ========================================
echo   服务器启动中...
echo   访问地址: http://localhost:5173
echo   按 Ctrl+C 停止服务器
echo ========================================
echo.

call npm run dev

pause
