@echo off
echo ========================================
echo Redis Setup for AI Trading Engine
echo ========================================
echo.

echo [1/4] Checking if Redis is already installed...
redis-server --version >nul 2>&1
if %errorlevel% == 0 (
    echo Redis is already installed!
    goto :start_redis
)

echo [2/4] Redis not found. Downloading Redis for Windows...
echo.

REM Create temp directory
if not exist "temp_redis" mkdir temp_redis
cd temp_redis

REM Download Redis for Windows
echo Downloading Redis for Windows...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.msi' -OutFile 'Redis-x64-3.0.504.msi'"

if not exist "Redis-x64-3.0.504.msi" (
    echo Failed to download Redis. Please download manually from:
    echo https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.msi
    echo.
    echo Or try alternative download:
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip' -OutFile 'Redis-x64-5.0.14.1.zip'"
    
    if exist "Redis-x64-5.0.14.1.zip" (
        echo Extracting Redis...
        powershell -Command "Expand-Archive -Path 'Redis-x64-5.0.14.1.zip' -DestinationPath '.' -Force"
        
        if exist "Redis-x64-5.0.14.1\redis-server.exe" (
            echo Copying Redis to project directory...
            copy "Redis-x64-5.0.14.1\redis-server.exe" "..\redis-server.exe"
            copy "Redis-x64-5.0.14.1\redis-cli.exe" "..\redis-cli.exe"
            echo Redis installed successfully!
        ) else (
            echo Failed to extract Redis properly.
            goto :error
        )
    ) else (
        echo Failed to download Redis.
        goto :error
    )
) else (
    echo Installing Redis MSI...
    msiexec /i Redis-x64-3.0.504.msi /quiet
    echo Redis installed via MSI.
)

cd ..

:start_redis
echo.
echo [3/4] Starting Redis server...
echo.

REM Try to start Redis with config file
if exist "redis-server.exe" (
    echo Starting Redis with local executable...
    start "Redis Server" redis-server.exe redis.conf
) else (
    echo Starting Redis service...
    net start redis
    if %errorlevel% neq 0 (
        echo Redis service not found. Starting Redis manually...
        redis-server redis.conf
    )
)

echo.
echo [4/4] Testing Redis connection...
timeout /t 3 /nobreak >nul

python test_redis.py
if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo Redis setup completed successfully!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Start Celery worker: start_celery_worker.bat
    echo 2. Start Celery beat: start_celery_beat.bat
    echo 3. Check system status: python manage.py celery_monitor --all
    echo.
) else (
    echo.
    echo ========================================
    echo Redis setup failed!
    echo ========================================
    echo.
    echo Please try manual installation:
    echo 1. Download Redis from: https://github.com/tporadowski/redis/releases
    echo 2. Extract redis-server.exe to this directory
    echo 3. Run: redis-server.exe redis.conf
    echo.
)

pause
exit /b 0

:error
echo.
echo ========================================
echo Redis setup failed!
echo ========================================
echo.
echo Please install Redis manually:
echo 1. Download from: https://github.com/tporadowski/redis/releases
echo 2. Extract redis-server.exe to this directory
echo 3. Run: redis-server.exe redis.conf
echo.
pause
exit /b 1























