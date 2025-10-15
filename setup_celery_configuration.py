#!/usr/bin/env python3
"""
Celery Configuration and Startup Script
Fixes Celery issues and provides proper startup scripts
"""

import os
import sys
import subprocess
from datetime import datetime

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def print_status(message, status="INFO"):
    """Print status message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "FIXING": "🔧"
    }
    print(f"[{timestamp}] {status_symbols.get(status, 'ℹ️')} {message}")

def create_celery_config():
    """Create proper Celery configuration"""
    print_status("=== CREATING CELERY CONFIGURATION ===", "FIXING")
    
    # Enhanced Celery configuration
    celery_config = """
# Celery Configuration for AI Trading Engine
import os
from celery import Celery
from celery.schedules import crontab
from kombu import Queue

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

app = Celery('ai_trading_engine')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Configuration
app.conf.update(
    # Task routing
    task_routes={
        'apps.data.tasks.*': {'queue': 'data'},
        'apps.signals.tasks.*': {'queue': 'signals'},
        'apps.sentiment.tasks.*': {'queue': 'sentiment'},
    },
    
    # Queue configuration
    task_default_queue='default',
    task_queues=(
        Queue('default', routing_key='default'),
        Queue('data', routing_key='data'),
        Queue('signals', routing_key='signals'),
        Queue('sentiment', routing_key='sentiment'),
    ),
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'update-crypto-prices': {
            'task': 'apps.data.tasks.update_crypto_prices_task',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
            'options': {'queue': 'data'},
        },
        'generate-trading-signals': {
            'task': 'apps.signals.tasks.generate_signals_for_all_symbols',
            'schedule': crontab(minute=0),  # Every hour at minute 0
            'options': {'queue': 'signals'},
        },
        'update-sentiment-analysis': {
            'task': 'apps.sentiment.tasks.update_sentiment_task',
            'schedule': crontab(minute='*/10'),  # Every 10 minutes
            'options': {'queue': 'sentiment'},
        },
        'cleanup-old-data': {
            'task': 'apps.data.tasks.cleanup_old_data_task',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
            'options': {'queue': 'data'},
        },
        'system-health-check': {
            'task': 'apps.signals.tasks.signal_health_check',
            'schedule': crontab(minute='*/15'),  # Every 15 minutes
            'options': {'queue': 'signals'},
        },
    },
    
    # Result backend configuration
    result_backend='django-db',
    result_expires=3600,  # 1 hour
    
    # Worker settings
    worker_max_tasks_per_child=1000,
    worker_max_memory_per_child=200000,  # 200MB
    worker_prefetch_multiplier=1,
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Monitoring and logging
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Error handling
    task_acks_late=True,
    worker_disable_rate_limits=True,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

@app.task(bind=True)
def health_check(self):
    """Health check task for monitoring Celery worker status"""
    return {
        'status': 'healthy',
        'worker': self.request.hostname,
        'timestamp': datetime.now().isoformat()
    }
"""
    
    # Write the enhanced Celery configuration
    celery_file = os.path.join(project_dir, 'ai_trading_engine', 'celery.py')
    with open(celery_file, 'w') as f:
        f.write(celery_config)
    
    print_status("Enhanced Celery configuration created!", "SUCCESS")

def create_startup_scripts():
    """Create comprehensive startup scripts"""
    print_status("=== CREATING STARTUP SCRIPTS ===", "FIXING")
    
    # Windows Batch Scripts
    worker_bat = """@echo off
title Celery Worker - AI Trading Engine
echo ========================================
echo Starting Celery Worker
echo ========================================
echo.
echo This will start the Celery worker for signal generation
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"

echo Starting Celery Worker...
celery -A ai_trading_engine worker -l info --pool=solo --concurrency=2

echo.
echo Celery Worker stopped.
pause
"""
    
    beat_bat = """@echo off
title Celery Beat Scheduler - AI Trading Engine
echo ========================================
echo Starting Celery Beat Scheduler
echo ========================================
echo.
echo This will start the Celery beat scheduler for periodic tasks
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"

echo Starting Celery Beat Scheduler...
celery -A ai_trading_engine beat -l info

echo.
echo Celery Beat Scheduler stopped.
pause
"""
    
    flower_bat = """@echo off
title Celery Flower Monitor - AI Trading Engine
echo ========================================
echo Starting Celery Flower Monitor
echo ========================================
echo.
echo This will start Flower for monitoring Celery tasks
echo Access at: http://localhost:5555
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"

echo Starting Celery Flower...
celery -A ai_trading_engine flower --port=5555

echo.
echo Celery Flower stopped.
pause
"""
    
    # PowerShell Scripts
    worker_ps1 = """# PowerShell script to start Celery Worker
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Celery Worker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will start the Celery worker for signal generation" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

Set-Location $PSScriptRoot

Write-Host "Starting Celery Worker..." -ForegroundColor Green
celery -A ai_trading_engine worker -l info --pool=solo --concurrency=2

Write-Host ""
Write-Host "Celery Worker stopped." -ForegroundColor Red
Read-Host "Press Enter to exit"
"""
    
    beat_ps1 = """# PowerShell script to start Celery Beat Scheduler
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Celery Beat Scheduler" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will start the Celery beat scheduler for periodic tasks" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

Set-Location $PSScriptRoot

Write-Host "Starting Celery Beat Scheduler..." -ForegroundColor Green
celery -A ai_trading_engine beat -l info

Write-Host ""
Write-Host "Celery Beat Scheduler stopped." -ForegroundColor Red
Read-Host "Press Enter to exit"
"""
    
    # Linux/Mac Scripts
    worker_sh = """#!/bin/bash
echo "========================================"
echo "Starting Celery Worker"
echo "========================================"
echo ""
echo "This will start the Celery worker for signal generation"
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"

echo "Starting Celery Worker..."
celery -A ai_trading_engine worker -l info --concurrency=2

echo ""
echo "Celery Worker stopped."
"""
    
    beat_sh = """#!/bin/bash
echo "========================================"
echo "Starting Celery Beat Scheduler"
echo "========================================"
echo ""
echo "This will start the Celery beat scheduler for periodic tasks"
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"

echo "Starting Celery Beat Scheduler..."
celery -A ai_trading_engine beat -l info

echo ""
echo "Celery Beat Scheduler stopped."
"""
    
    # Write all scripts
    scripts = [
        ('start_celery_worker.bat', worker_bat),
        ('start_celery_beat.bat', beat_bat),
        ('start_celery_flower.bat', flower_bat),
        ('start_celery_worker.ps1', worker_ps1),
        ('start_celery_beat.ps1', beat_ps1),
        ('start_celery_worker.sh', worker_sh),
        ('start_celery_beat.sh', beat_sh),
    ]
    
    for filename, content in scripts:
        filepath = os.path.join(project_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        
        # Make shell scripts executable on Unix systems
        if filename.endswith('.sh'):
            os.chmod(filepath, 0o755)
    
    print_status("All startup scripts created!", "SUCCESS")

def create_systemd_services():
    """Create systemd service files for Linux"""
    print_status("=== CREATING SYSTEMD SERVICES ===", "FIXING")
    
    # Celery Worker Service
    worker_service = """[Unit]
Description=Celery Worker for AI Trading Engine
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
EnvironmentFile=/path/to/your/project/.env
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/project/venv/bin/celery -A ai_trading_engine worker -l info --detach
ExecStop=/path/to/your/project/venv/bin/celery -A ai_trading_engine control shutdown
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    # Celery Beat Service
    beat_service = """[Unit]
Description=Celery Beat Scheduler for AI Trading Engine
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
EnvironmentFile=/path/to/your/project/.env
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/project/venv/bin/celery -A ai_trading_engine beat -l info --detach
ExecStop=/path/to/your/project/venv/bin/celery -A ai_trading_engine control shutdown
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    # Write service files
    with open(os.path.join(project_dir, 'celery-worker.service'), 'w') as f:
        f.write(worker_service)
    
    with open(os.path.join(project_dir, 'celery-beat.service'), 'w') as f:
        f.write(beat_service)
    
    print_status("Systemd service files created!", "SUCCESS")
    print_status("Note: Update paths in service files before using", "WARNING")

def create_monitoring_script():
    """Create a comprehensive monitoring script"""
    monitoring_script = """#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from datetime import datetime

def check_celery_status():
    print("=== CELERY STATUS CHECK ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    try:
        # Check active workers
        result = subprocess.run(['celery', '-A', 'ai_trading_engine', 'inspect', 'active'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Celery workers are running")
            print(result.stdout)
        else:
            print("❌ Celery workers are not running")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error checking Celery status: {e}")
    
    print()
    
    try:
        # Check scheduled tasks
        result = subprocess.run(['celery', '-A', 'ai_trading_engine', 'inspect', 'scheduled'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Scheduled tasks:")
            print(result.stdout)
        else:
            print("❌ No scheduled tasks found")
    except Exception as e:
        print(f"❌ Error checking scheduled tasks: {e}")
    
    print()
    
    try:
        # Check registered tasks
        result = subprocess.run(['celery', '-A', 'ai_trading_engine', 'inspect', 'registered'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Registered tasks:")
            print(result.stdout)
        else:
            print("❌ No registered tasks found")
    except Exception as e:
        print(f"❌ Error checking registered tasks: {e}")

if __name__ == "__main__":
    check_celery_status()
"""
    
    with open(os.path.join(project_dir, 'monitor_celery.py'), 'w') as f:
        f.write(monitoring_script)
    
    print_status("Celery monitoring script created: monitor_celery.py", "SUCCESS")

def main():
    """Main function to setup Celery configuration"""
    print_status("=== CELERY CONFIGURATION AND STARTUP SCRIPT ===", "INFO")
    print_status("This script will fix Celery configuration and create startup scripts", "INFO")
    print()
    
    # Create Celery configuration
    create_celery_config()
    
    # Create startup scripts
    create_startup_scripts()
    
    # Create systemd services
    create_systemd_services()
    
    # Create monitoring script
    create_monitoring_script()
    
    print()
    print_status("=== CELERY SETUP COMPLETE ===", "SUCCESS")
    print_status("Next steps:", "INFO")
    print_status("1. Windows: Run start_celery_worker.bat and start_celery_beat.bat", "INFO")
    print_status("2. Linux/Mac: Run ./start_celery_worker.sh and ./start_celery_beat.sh", "INFO")
    print_status("3. Monitor: python monitor_celery.py", "INFO")
    print_status("4. Web UI: Run start_celery_flower.bat and visit http://localhost:5555", "INFO")
    
    print()
    print_status("Celery setup completed!", "INFO")

if __name__ == "__main__":
    main()



































