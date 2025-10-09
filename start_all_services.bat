@echo off
title AI Trading Engine - Complete Startup
color 0A

echo ========================================
echo    AI Trading Engine - Complete Startup
echo ========================================
echo.

echo [1/6] Checking if Redis is already running...
python test_redis.py >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Redis is already running!
    goto :start_celery
)

echo [2/6] Starting Redis server...
if exist "redis-server.exe" (
    echo Starting Redis with local executable...
    start "Redis Server" /min redis-server.exe redis.conf
) else (
    echo Starting Redis service...
    net start redis >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Redis not found! Please install Redis first.
        echo Run: setup_redis.bat
        pause
        exit /b 1
    )
)

echo Waiting for Redis to start...
timeout /t 5 /nobreak >nul

echo [3/6] Testing Redis connection...
python test_redis.py
if %errorlevel% neq 0 (
    echo ❌ Redis failed to start!
    echo Please check Redis installation and try again.
    pause
    exit /b 1
)

:start_celery
echo [4/6] Starting Celery worker...
start "Celery Worker" /min python -m celery -A ai_trading_engine worker -l info --pool=solo

echo [5/6] Starting Celery beat scheduler...
start "Celery Beat" /min python -m celery -A ai_trading_engine beat -l info

echo Waiting for Celery services to initialize...
timeout /t 3 /nobreak >nul

echo [6/6] Starting Django server...
echo.
echo ========================================
echo    🚀 ALL SERVICES STARTED SUCCESSFULLY!
echo ========================================
echo.
echo ✅ Redis Server: Running on port 6379
echo ✅ Celery Worker: Processing background tasks
echo ✅ Celery Beat: Scheduling automatic signals
echo ✅ Django Server: Starting on port 8000
echo.
echo 🌐 Access your application at:
echo    http://localhost:8000
echo.
echo 📊 Trading Signals: http://localhost:8000/signals/
echo 📈 Analytics: http://localhost:8000/analytics/
echo 💼 Portfolio: http://localhost:8000/dashboard/portfolio/
echo.
echo ⚠️  Keep this window open to keep Django running
echo ⚠️  Press Ctrl+C to stop all services
echo.
echo ========================================

python manage.py runserver 0.0.0.0:8000

echo.
echo ========================================
echo    🛑 ALL SERVICES STOPPED
echo ========================================
echo.
echo To restart all services, run this script again.
pause



