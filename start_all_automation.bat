@echo off
title AI Trading Engine - All Automation
color 0B

cls
echo.
echo ================================================================
echo          AI TRADING ENGINE - ALL AUTOMATION
echo ================================================================
echo.
echo Starting all services in separate windows:
echo.
echo   [1] Django Server - Web interface
echo   [2] Signal Generation - Generate trading signals
echo   [3] Update Coins - Update coin data in database
echo   [4] Update News Live - Continuously update cryptocurrency news
echo.
echo Each service will run in its own terminal window.
echo Keep all windows open for the application to work.
echo.
echo ================================================================
echo.

cd /d "%~dp0"

echo Starting all services now...
echo.

REM Start Django Server
echo [1/4] Starting Django Server...
start "Django Server" cmd /k "cd /d %~dp0 && python manage.py runserver 0.0.0.0:8000"
timeout /t 2 /nobreak > nul

REM Start Signal Generation
echo [2/4] Starting Signal Generation...
start "Signal Generation" cmd /k "cd /d %~dp0 && python -u run_signal_generation.py"
timeout /t 2 /nobreak > nul

REM Start Update Coins
echo [3/4] Starting Update Coins...
start "Update Coins" cmd /k "cd /d %~dp0 && python update_all_coins.py"
timeout /t 2 /nobreak > nul

REM Start Update News Live
echo [4/4] Starting Update News Live...
start "Update News Live" cmd /k "cd /d %~dp0 && python update_news_live.py"
timeout /t 2 /nobreak > nul

echo.
echo All services started!
echo.
echo Waiting 5 seconds for services to initialize...
timeout /t 5 /nobreak > nul

cls
echo.
echo ================================================================
echo              ✅ ALL SERVICES STARTED SUCCESSFULLY
echo ================================================================
echo.
echo 🌐 Django Server      - http://localhost:8000
echo 📈 Signal Generation  - Generating trading signals
echo 💰 Update Coins       - Updating coin data in database
echo 📰 Update News Live   - Continuously updating cryptocurrency news
echo.
echo Services are running in 4 separate windows:
echo.
echo   1. "Django Server" - Web interface
echo   2. "Signal Generation" - Signal generation process
echo   3. "Update Coins" - Database update process
echo   4. "Update News Live" - Live news collection and analysis
echo.
echo ================================================================
echo                     IMPORTANT NOTES
echo ================================================================
echo.
echo ⚠️  Keep ALL FOUR windows open!
echo.
echo Each service runs independently:
echo   - Django Server: Web interface at http://localhost:8000
echo   - Signal Generation: Continuously generates trading signals
echo   - Update Coins: Updates coin data in database
echo   - Update News Live: Fetches and analyzes crypto news every 15 minutes
echo.
echo To stop services:
echo   - Close the respective windows
echo   - Or use stop_all_automation.bat
echo.
echo ================================================================
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
echo All automation services are now running!
echo.
echo This window will close in 5 seconds...
timeout /t 5 /nobreak > nul

