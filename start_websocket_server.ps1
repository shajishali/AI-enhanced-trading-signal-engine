# AI Trading Engine - WebSocket Server Startup Script
# Run this script to start the server with WebSocket support

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AI Trading Engine - WebSocket Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Testing Django imports..." -ForegroundColor Yellow
$djangoTest = python test_server.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Django import test failed. Please fix the import errors." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "[2/4] Testing Redis connection..." -ForegroundColor Yellow
$redisTest = python test_redis.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Redis test failed. Please start Redis server first." -ForegroundColor Red
    Write-Host ""
    Write-Host "To start Redis manually:" -ForegroundColor Yellow
    Write-Host "  redis-server redis.conf" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "[3/4] Redis connection successful!" -ForegroundColor Green
Write-Host ""

Write-Host "[4/4] Starting Django server with WebSocket support..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Starting with Daphne (ASGI server)..." -ForegroundColor White
Write-Host "WebSocket endpoints will be available at:" -ForegroundColor White
Write-Host "  - ws://localhost:8000/ws/market-data/" -ForegroundColor Cyan
Write-Host "  - ws://localhost:8000/ws/trading-signals/" -ForegroundColor Cyan
Write-Host "  - ws://localhost:8000/ws/notifications/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test page: http://localhost:8000/core/websocket-test/" -ForegroundColor Green
Write-Host ""

Write-Host "[5/5] Starting server..." -ForegroundColor Yellow
daphne -b 127.0.0.1 -p 8000 ai_trading_engine.asgi:application

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to continue"
