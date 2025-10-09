@echo off
echo Starting Automated Signal Generation...
echo This will run signal generation every 15 minutes
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python run_signal_generation.py

pause



