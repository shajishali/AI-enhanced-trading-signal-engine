@echo off
REM Windows batch script to start Celery services for automated database updates
REM Run this script to start the automated backtesting database updates

echo ========================================
echo Starting Automated Database Updates
echo ========================================
echo.

cd /d "D:\Research Development"

echo Starting Celery Worker...
start "Celery Worker" cmd /k "python -m celery -A ai_trading_engine worker -l info --pool=solo"

timeout /t 3 /nobreak >nul

echo Starting Celery Beat Scheduler...
start "Celery Beat" cmd /k "python -m celery -A ai_trading_engine beat -l info"

echo.
echo ========================================
echo Celery Services Started Successfully!
echo ========================================
echo.
echo Automated Update Schedule:
echo - Hourly historical data update: Every hour at minute 0
echo - Daily backup update: 2:30 AM UTC (backup safety)
echo - Weekly gap check and fill: Sunday 3:00 AM UTC  
echo - Data cleanup: DISABLED (preserves all data from 2020)
echo.
echo Your backtesting database will now automatically 
echo update every hour until 1 hour before current time!
echo.
echo To check database status, run: python quick_status_check.py
echo To stop services, close the Celery Worker and Beat windows
echo.
pause
