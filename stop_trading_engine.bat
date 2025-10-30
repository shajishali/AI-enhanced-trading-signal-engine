@echo off
title AI Trading Engine - Stop All Services
color 0C

cls
echo.
echo ================================================================
echo          AI TRADING ENGINE - STOP ALL SERVICES
echo ================================================================
echo.

cd /d "%~dp0"

echo Stopping all services...
echo.

REM Stop Django Server (port 8000)
echo [1] Stopping Django Server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do (
    echo     Stopping process %%a
    taskkill /F /PID %%a >nul 2>&1
)
echo.

REM Stop Celery Workers
echo [2] Stopping Celery Workers...
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" ^| findstr "python.exe"') do (
    tasklist /FI "PID eq %%a" ^| findstr "celery" >nul
    if "!ERRORLEVEL!"=="0" (
        echo     Stopping Celery process %%a
        taskkill /F /PID %%a >nul 2>&1
    )
)
echo.

REM Alternative: Kill all Python processes related to this project
echo [3] Cleaning up remaining Python processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq AI Trading Engine*" >nul 2>&1

echo.
echo ================================================================
echo                ✅ SERVICES STOPPED
echo ================================================================
echo.
echo All services have been stopped.
echo You can now safely close this window.
echo.
echo ================================================================
echo.

timeout /t 3 > nul







