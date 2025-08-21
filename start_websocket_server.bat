@echo off
echo ========================================
echo    AI Trading Engine - WebSocket Server
echo ========================================
echo.

echo [1/4] Testing Django imports...
python test_server.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Django import test failed. Please fix the import errors.
    echo.
    pause
    exit /b 1
)

echo.
echo [2/4] Testing Redis connection...
python test_redis.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Redis test failed. Please start Redis server first.
    echo.
    echo To start Redis manually:
    echo   redis-server redis.conf
    echo.
    pause
    exit /b 1
)

echo.
echo [3/4] Redis connection successful!
echo.

echo [4/4] Starting Django server with WebSocket support...
echo.
echo Starting with Daphne (ASGI server)...
echo WebSocket endpoints will be available at:
echo   - ws://localhost:8000/ws/market-data/
echo   - ws://localhost:8000/ws/trading-signals/
echo   - ws://localhost:8000/ws/notifications/
echo.
echo Test page: http://localhost:8000/core/websocket-test/
echo.

echo [5/5] Starting server...
daphne -b 127.0.0.1 -p 8000 ai_trading_engine.asgi:application

echo.
echo Server stopped.
pause
