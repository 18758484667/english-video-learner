@echo off
chcp 65001 >nul

echo =========================================
echo GitHub Pages 一键推送脚本
echo =========================================
echo.

REM 设置变量
set "GITHUB_USERNAME=18758484667"
set "REPO_NAME=english-video-learner"
set "REMOTE_URL=https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git"

echo GitHub 用户名: %GITHUB_USERNAME%
echo 仓库名: %REPO_NAME%
echo 远程地址: %REMOTE_URL%
echo.

REM 检查是否在正确的目录
if not exist "frontend\" (
    echo 错误: 当前目录不是项目根目录
echo 请在项目根目录运行此脚本
    pause
    exit /b 1
)

echo 正在检查 Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Git 未安装，请先安装 Git
    pause
    exit /b 1
)

echo Git 检查通过
echo.

REM 设置 remote
echo 正在设置远程仓库...
git remote remove origin 2>nul
git remote add origin %REMOTE_URL%

echo.
echo =========================================
echo 请先确保已在 GitHub 上创建仓库:
echo.
echo 1. 打开 https://github.com/new
echo 2. Repository name 填写: %REPO_NAME%
echo 3. 选择 Public
echo 4. 点击 Create repository
echo.
echo 创建完成后，按任意键继续推送...
echo =========================================
pause >nul

echo.
echo 正在推送到 GitHub...
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo 推送失败，可能原因:
    echo 1. 仓库不存在，请先在 GitHub 上创建
    echo 2. 需要登录 GitHub 账号
    echo 3. 网络问题
    echo.
    echo 请手动执行以下命令:
    echo git remote add origin %REMOTE_URL%
    echo git branch -M main
    echo git push -u origin main
    pause
    exit /b 1
)

echo.
echo =========================================
echo 推送成功!
echo.
echo 接下来需要在 GitHub 上启用 Pages:
echo 1. 打开 https://github.com/%GITHUB_USERNAME%/%REPO_NAME%/settings/pages
echo 2. Source 选择 "Deploy from a branch"
echo 3. Branch 选择 "gh-pages"
echo 4. 点击 Save
echo.
echo 或者等待 GitHub Actions 自动部署
echo =========================================
pause
