@echo off
echo Starting Celery Worker and Beat Scheduler...
echo.
echo This will run both worker and beat in a single window
echo.
echo Press Ctrl+C to stop the worker
echo.

cd /d "%~dp0"
python -m celery -A ai_trading_engine worker -B --loglevel=info --pool=solo

pause






