#!/usr/bin/env python3
"""
Automated Signal Generation Script
Runs signal generation every 1 hour
"""

import os
import sys
import time
import subprocess
from datetime import datetime, timedelta

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

def run_signal_generation():
    """Run the signal generation command"""
    try:
        print(f"[{datetime.now()}] Starting signal generation...")
        
        # Run the management command
        result = subprocess.run([
            sys.executable, 'manage.py', 'generate_signals', '--update-indicators'
        ], capture_output=True, text=True, cwd=project_dir)
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] Signal generation completed successfully")
            print("Output:", result.stdout)
        else:
            print(f"[{datetime.now()}] Signal generation failed")
            print("Error:", result.stderr)
            
    except Exception as e:
        print(f"[{datetime.now()}] Error running signal generation: {e}")

def main():
    """Main loop - run every hour at :49 minutes"""
    print(f"[{datetime.now()}] Starting automated signal generation...")
    print("Press Ctrl+C to stop")
    print("Signal generation will run at :49 minutes past each hour (18:49, 19:49, 20:49, etc.)")
    
    try:
        while True:
            now = datetime.now()
            
            # Calculate seconds until next :49 minute mark
            current_minute = now.minute
            current_second = now.second
            
            if current_minute < 49:
                # Next run is at :49 of current hour
                minutes_to_wait = 49 - current_minute
                seconds_to_wait = (minutes_to_wait * 60) - current_second
            elif current_minute == 49:
                # We're at :49, check if we just started or if we should wait for next hour
                if current_second < 10:
                    # Just started, wait for next hour's :49
                    minutes_to_wait = 60  # Wait until next hour
                    seconds_to_wait = (minutes_to_wait * 60) - current_second
                else:
                    # Already past :49, wait for next hour's :49
                    minutes_to_wait = 60 - current_minute + 49
                    seconds_to_wait = (minutes_to_wait * 60) - current_second
            else:
                # Current minute > 49, wait for next hour's :49
                minutes_to_wait = (60 - current_minute) + 49
                seconds_to_wait = (minutes_to_wait * 60) - current_second
            
            next_run_time = now.replace(second=0, microsecond=0) + timedelta(seconds=seconds_to_wait)
            print(f"[{now}] Next signal generation scheduled for: {next_run_time.strftime('%H:%M:%S')}")
            print(f"[{now}] Waiting {seconds_to_wait} seconds ({minutes_to_wait} minutes)...")
            
            time.sleep(seconds_to_wait)
            
            # Run signal generation
            run_signal_generation()
            
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Stopping automated signal generation...")
    except Exception as e:
        print(f"[{datetime.now()}] Unexpected error: {e}")

if __name__ == "__main__":
    main()



