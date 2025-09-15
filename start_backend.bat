@echo off
echo ========================================
echo 启动实时数据采集系统 - 后端服务
echo ========================================
echo.

cd /d "%~dp0backend"

echo 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo.

echo 安装Python依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误：安装依赖失败
    pause
    exit /b 1
)
echo.

echo 启动FastAPI服务器...
echo 服务器地址: http://localhost:8008
echo 按 Ctrl+C 停止服务器
echo.
python main.py

pause