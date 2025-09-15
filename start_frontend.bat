@echo off
echo ========================================
echo 启动实时数据采集系统 - 前端服务
echo ========================================
echo.

cd /d "%~dp0frontend"

echo 检查Node.js环境...
node --version
if errorlevel 1 (
    echo 错误：未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)
echo.

echo 安装Node.js依赖...
npm install
if errorlevel 1 (
    echo 错误：安装依赖失败
    pause
    exit /b 1
)
echo.

echo 启动Vue开发服务器...
echo 前端地址: http://localhost:3000
echo 按 Ctrl+C 停止服务器
echo.
npm run dev

pause