#!/usr/bin/env python3
"""
Automatic Signal Generation Script
Runs signal generation every hour using Celery tasks
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

def print_status(message, status="INFO"):
    """Print status message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{status}] {message}")

def run_signal_generation():
    """Run signal generation Celery task and management command"""
    # 1. Celery task
    try:
        from apps.signals.tasks import generate_signals_for_all_symbols
        print_status("Starting signal generation (Celery task)...", "INFO")
        result = generate_signals_for_all_symbols.delay()
        print_status("Celery signal generation fired (see Celery logs for completion)", "INFO")
    except Exception as e:
        print_status(f"Celery task error: {e}", "WARNING")

    # 2. Management command
    try:
        print_status("Starting signal generation (management command)...", "INFO")
        cmd = [sys.executable, "manage.py", "generate_signals", "--update-indicators"]
        mgmt_result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_dir)
        print(mgmt_result.stdout)
        if mgmt_result.returncode == 0:
            print_status("Management command completed successfully!", "SUCCESS")
        else:
            print_status(f"Management command error: {mgmt_result.stderr}", "ERROR")
    except Exception as e:
        print_status(f"Management command exception: {e}", "ERROR")

def main():
    """Main function - run signal generation every hour"""
    print("=" * 80)
    print("AUTOMATIC SIGNAL GENERATION - RUNNING EVERY HOUR")
    print("=" * 80)
    print("This script will generate signals every hour automatically")
    print("Press Ctrl+C to stop\n")
    try:
        while True:
            run_signal_generation()
            print_status("Waiting 1 hour until next signal generation...", "INFO")
            time.sleep(3600)
    except KeyboardInterrupt:
        print_status("Stopping automatic signal generation...", "INFO")

if __name__ == "__main__":
    main()
































































