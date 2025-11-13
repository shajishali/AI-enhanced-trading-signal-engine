# Start Automation Services Script
# This script starts Redis, Celery Worker, and Celery Beat

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Automation Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check if Redis is already running
$redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue

if (-not $redisRunning) {
    Write-Host "`n[1/3] Starting Redis Server..." -ForegroundColor Yellow
    if (Test-Path ".\redis-server.exe") {
        Start-Process -FilePath ".\redis-server.exe" -ArgumentList "redis.conf" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        
        # Verify Redis started
        $redisCheck = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($redisCheck) {
            Write-Host "  ✓ Redis Server started successfully" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Redis Server failed to start" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  ✗ redis-server.exe not found in current directory" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n[1/3] Redis Server: Already running" -ForegroundColor Green
}

# Check if Celery Worker is running
Write-Host "`n[2/3] Starting Celery Worker..." -ForegroundColor Yellow
$workerProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    $cmdLine -like "*celery*worker*"
}

if (-not $workerProcess) {
    $workerCmd = "cd '$scriptDir'; python -m celery -A ai_trading_engine worker --loglevel=info --pool=solo"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $workerCmd -WindowStyle Minimized
    Start-Sleep -Seconds 3
    Write-Host "  ✓ Celery Worker started in new window" -ForegroundColor Green
} else {
    Write-Host "  ✓ Celery Worker: Already running (PID: $($workerProcess.Id))" -ForegroundColor Green
}

# Check if Celery Beat is running
Write-Host "`n[3/3] Starting Celery Beat..." -ForegroundColor Yellow
$beatProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    $cmdLine -like "*celery*beat*"
}

if (-not $beatProcess) {
    $beatCmd = "cd '$scriptDir'; python -m celery -A ai_trading_engine beat --loglevel=info"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $beatCmd -WindowStyle Minimized
    Start-Sleep -Seconds 3
    Write-Host "  ✓ Celery Beat started in new window" -ForegroundColor Green
} else {
    Write-Host "  ✓ Celery Beat: Already running (PID: $($beatProcess.Id))" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "All services started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nServices running in separate windows:" -ForegroundColor Yellow
Write-Host "  - Redis Server (minimized)" -ForegroundColor White
Write-Host "  - Celery Worker (PowerShell window)" -ForegroundColor White
Write-Host "  - Celery Beat (PowerShell window)" -ForegroundColor White
Write-Host "`nTo verify services, run: python phase1_diagnosis.py" -ForegroundColor Yellow
Write-Host "`nServices are now running. Check the PowerShell windows for Celery Worker and Beat." -ForegroundColor Green

