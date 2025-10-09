#!/usr/bin/env python3
"""
Automated Signal Generation Script
Runs signal generation every 1 hour
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
    """Main loop - run every 1 hour"""
    print(f"[{datetime.now()}] Starting automated signal generation...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            run_signal_generation()
            
            # Wait 1 hour (3600 seconds)
            print(f"[{datetime.now()}] Waiting 1 hour until next run...")
            time.sleep(3600)
            
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Stopping automated signal generation...")
    except Exception as e:
        print(f"[{datetime.now()}] Unexpected error: {e}")

if __name__ == "__main__":
    main()



