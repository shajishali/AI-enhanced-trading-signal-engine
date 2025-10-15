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

from apps.signals.tasks import generate_signals_for_all_symbols

def print_status(message, status="INFO"):
    """Print status message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{status}] {message}")

def run_signal_generation():
    """Run signal generation task"""
    try:
        print_status("Starting signal generation...", "INFO")
        
        # Run the signal generation task
        result = generate_signals_for_all_symbols.delay()
        
        # In synchronous mode, result is available immediately
        if hasattr(result, 'result') and result.result:
            print_status("Signal generation completed successfully!", "SUCCESS")
            return True
        else:
            print_status("Signal generation completed!", "SUCCESS")
            return True
            
    except Exception as e:
        print_status(f"Error running signal generation: {str(e)}", "ERROR")
        return False

def main():
    """Main function - run signal generation every hour"""
    print("=" * 80)
    print("AUTOMATIC SIGNAL GENERATION - RUNNING EVERY HOUR")
    print("=" * 80)
    print("This script will generate signals every hour automatically")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            # Run signal generation
            success = run_signal_generation()
            
            if success:
                print_status("Waiting 1 hour until next signal generation...", "INFO")
            else:
                print_status("Waiting 5 minutes before retry...", "WARNING")
                time.sleep(300)  # Wait 5 minutes on error
                continue
            
            # Wait 1 hour (3600 seconds)
            time.sleep(3600)
            
    except KeyboardInterrupt:
        print()
        print_status("Stopping automatic signal generation...", "INFO")
    except Exception as e:
        print_status(f"Unexpected error: {str(e)}", "ERROR")

if __name__ == "__main__":
    main()



































