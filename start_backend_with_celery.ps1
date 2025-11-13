Param(
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'

# Resolve paths
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvBin = Join-Path $root '.venv\Scripts'
$python = 'python'
$celery = 'celery'

if (Test-Path (Join-Path $venvBin 'python.exe')) {
    $python = Join-Path $venvBin 'python.exe'
}
if (Test-Path (Join-Path $venvBin 'celery.exe')) {
    $celery = Join-Path $venvBin 'celery.exe'
}

# Ensure logs directory exists
$logs = Join-Path $root 'logs'
if (-not (Test-Path $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

# Helper to start a process in its own window
function Start-Proc([string]$title, [string]$cmd) {
    $ps = "`$host.ui.RawUI.WindowTitle='$title'; cd '$root'; $cmd"
    Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-Command",$ps |
        Out-Null
}

# Start Django runserver
Start-Proc "Django Dev Server" "& '$python' manage.py runserver $HostAddress`:$Port 2>&1 | Tee-Object -FilePath '$logs\\django_server.log'"

# Start Celery worker via python -m celery (works even when celery.exe isn't on PATH)
Start-Proc "Celery Worker" "& '$python' -m celery -A ai_trading_engine worker --loglevel=INFO 2>&1 | Tee-Object -FilePath '$logs\\celery_worker.log'"

# Start Celery beat scheduler via python -m celery
Start-Proc "Celery Beat" "& '$python' -m celery -A ai_trading_engine beat --loglevel=INFO 2>&1 | Tee-Object -FilePath '$logs\\celery_beat.log'"

Write-Host "Started Django, Celery worker, and Celery beat. Logs: $logs" -ForegroundColor Green
