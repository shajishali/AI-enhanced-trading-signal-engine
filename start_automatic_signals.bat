@echo off
echo ========================================
echo AI Trading Engine - Automatic Signal Generation
echo ========================================
echo.
echo This will run signal generation every hour automatically
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"

echo Starting automatic signal generation...
python run_automatic_signals.py

echo.
echo Automatic signal generation stopped.
pause























