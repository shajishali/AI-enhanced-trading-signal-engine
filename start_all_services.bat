@echo off
title AI Trading Engine - All Services
color 0A

echo.
echo ========================================
echo   AI TRADING ENGINE - ALL SERVICES
echo ========================================
echo.
echo Starting all services in separate windows...
echo.

cd /d "%~dp0"

REM Start Celery Worker and Beat
echo Starting Celery Worker and Beat Scheduler...
start "Celery Worker" cmd /k "python -m celery -A ai_trading_engine worker -B --loglevel=info --pool=solo"

REM Wait a moment for Celery to initialize
timeout /t 3 /nobreak > nul

REM Start Django Development Server
echo Starting Django Development Server...
start "Django Server" cmd /k "python manage.py runserver 0.0.0.0:8000"

REM Wait a moment for Django to initialize
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo   SERVICES STARTED SUCCESSFULLY
echo ========================================
echo.
echo ✅ Celery Worker - Processing background tasks
echo ✅ Django Server - Running on http://0.0.0.0:8000
echo.
echo Services are running in separate windows.
echo Keep all windows open for the application to work.
echo.
echo Press any key to open the web interface...
pause > nul

REM Open the web browser
start http://localhost:8000

echo.
echo Opening web browser...
echo.
echo To stop services:
echo - Close the "Celery Worker" window
echo - Close the "Django Server" window
echo.
