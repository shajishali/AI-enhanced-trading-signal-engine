@echo off
title AI Trading Engine - Master Control
color 0B

cls
echo.
echo ================================================================
echo          AI TRADING ENGINE - ALL SERVICES LAUNCHER
echo ================================================================
echo.
echo This will start:
echo   [1] Celery Worker - Background task processor
echo   [2] Celery Beat - Task scheduler  
echo   [3] Django Server - Web application server
echo.
echo Services will open in separate windows.
echo Keep all windows open for the application to work.
echo.
echo ================================================================
echo.

cd /d "%~dp0"

echo Starting all services now...
echo.

REM Start Celery Worker
echo [1/3] Starting Celery Worker...
start "Celery Worker" cmd /k "python -m celery -A ai_trading_engine worker --loglevel=info --pool=solo"
timeout /t 3 /nobreak > nul

REM Start Celery Beat Scheduler
echo [2/3] Starting Celery Beat Scheduler...
start "Celery Beat" cmd /k "python -m celery -A ai_trading_engine beat --loglevel=info"
timeout /t 3 /nobreak > nul

REM Start Django Development Server
echo [3/3] Starting Django Server...
start "Django Server" cmd /k "python manage.py runserver 0.0.0.0:8000"
timeout /t 3 /nobreak > nul

echo.
echo All services started!
echo.
echo Waiting 10 seconds for servers to start...
timeout /t 10 /nobreak > nul

cls
echo.
echo ================================================================
echo              ✅ SERVICES STARTED SUCCESSFULLY
echo ================================================================
echo.
echo 📊 Celery Worker     - Processing background tasks
echo ⏰ Celery Beat        - Scheduling tasks
echo 🌐 Django Server      - http://localhost:8000
echo.
echo Opening web browser in 3 seconds...
timeout /t 3 /nobreak > nul

REM Open the web browser
start http://localhost:8000

cls
echo.
echo ================================================================
echo              🌐 WEB INTERFACE OPENED
echo ================================================================
echo.
echo Services are running in 3 separate windows:
echo.
echo   1. "Celery Worker" - Background tasks
echo   2. "Celery Beat" - Task scheduler
echo   3. "Django Server" - Web server
echo.
echo ================================================================
echo                     IMPORTANT NOTES
echo ================================================================
echo.
echo ⚠️  Keep ALL THREE windows open!
echo.
echo To stop services:
echo   - Close all three service windows
echo.
echo ================================================================
echo.
echo This window will close in 5 seconds...
timeout /t 5 /nobreak > nul
