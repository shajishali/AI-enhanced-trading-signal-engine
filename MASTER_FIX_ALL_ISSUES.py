#!/usr/bin/env python3
"""
MASTER FIX SCRIPT - Solves All 5 Major Signal Generation Issues
This script runs all fixes in the correct order to resolve signal generation problems
"""

import os
import sys
import subprocess
import time
from datetime import datetime

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

def print_header():
    """Print script header"""
    print("=" * 80)
    print("🚀 AI TRADING ENGINE - MASTER FIX SCRIPT")
    print("=" * 80)
    print("This script will solve ALL 5 major issues preventing automatic signal generation:")
    print()
    print("1. 🔴 Celery Not Running")
    print("2. 🔴 Missing Market Data") 
    print("3. 🔴 No Active Symbols")
    print("4. 🔴 Technical Indicators Missing")
    print("5. 🔴 High Confidence Thresholds")
    print()
    print("=" * 80)
    print()

def print_status(message, status="INFO"):
    """Print status message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "FIXING": "🔧",
        "STEP": "📋"
    }
    print(f"[{timestamp}] {status_symbols.get(status, 'ℹ️')} {message}")

def run_script(script_name, description):
    """Run a Python script and return success status"""
    print_status(f"Running: {description}", "STEP")
    script_path = os.path.join(project_dir, script_name)
    
    if not os.path.exists(script_path):
        print_status(f"Script not found: {script_name}", "ERROR")
        return False
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, cwd=project_dir)
        
        if result.returncode == 0:
            print_status(f"✅ {description} - COMPLETED", "SUCCESS")
            return True
        else:
            print_status(f"❌ {description} - FAILED", "ERROR")
            print_status(f"Error: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ {description} - ERROR: {str(e)}", "ERROR")
        return False

def run_command(command, description):
    """Run a shell command and return success status"""
    print_status(f"Running: {description}", "STEP")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=project_dir)
        
        if result.returncode == 0:
            print_status(f"✅ {description} - COMPLETED", "SUCCESS")
            return True
        else:
            print_status(f"❌ {description} - FAILED", "ERROR")
            print_status(f"Error: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ {description} - ERROR: {str(e)}", "ERROR")
        return False

def check_system_requirements():
    """Check if system meets requirements"""
    print_status("=== CHECKING SYSTEM REQUIREMENTS ===", "FIXING")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 8:
        print_status(f"✅ Python {python_version.major}.{python_version.minor} - Compatible", "SUCCESS")
    else:
        print_status(f"❌ Python {python_version.major}.{python_version.minor} - Requires Python 3.8+", "ERROR")
        return False
    
    # Check Django
    try:
        import django
        print_status(f"✅ Django {django.get_version()} - Installed", "SUCCESS")
    except ImportError:
        print_status("❌ Django not installed", "ERROR")
        return False
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print_status("❌ manage.py not found - Wrong directory", "ERROR")
        return False
    else:
        print_status("✅ manage.py found - Correct directory", "SUCCESS")
    
    return True

def main():
    """Main function to run all fixes"""
    print_header()
    
    # Check system requirements
    if not check_system_requirements():
        print_status("❌ System requirements not met. Please fix and try again.", "ERROR")
        return
    
    print()
    print_status("🎯 Starting comprehensive fix process...", "INFO")
    print()
    
    # Track success of each step
    steps_completed = []
    
    # STEP 1: Setup Dependencies
    print_status("=== STEP 1: SETTING UP DEPENDENCIES ===", "FIXING")
    steps_completed.append(run_script('setup_dependencies.py', 'Setup Dependencies'))
    print()
    
    # STEP 2: Setup Database and Phase 5 Models
    print_status("=== STEP 2: SETTING UP DATABASE ===", "FIXING")
    steps_completed.append(run_script('setup_database_phase5.py', 'Setup Database and Phase 5 Models'))
    print()
    
    # STEP 3: Setup Celery Configuration
    print_status("=== STEP 3: SETTING UP CELERY ===", "FIXING")
    steps_completed.append(run_script('setup_celery_configuration.py', 'Setup Celery Configuration'))
    print()
    
    # STEP 4: Fix All Signal Generation Issues
    print_status("=== STEP 4: FIXING SIGNAL GENERATION ISSUES ===", "FIXING")
    steps_completed.append(run_script('fix_signal_generation_issues.py', 'Fix All Signal Generation Issues'))
    print()
    
    # STEP 5: Final System Check
    print_status("=== STEP 5: FINAL SYSTEM CHECK ===", "FIXING")
    
    # Check database migrations
    migration_success = run_command('python manage.py check', 'Check Django System')
    steps_completed.append(migration_success)
    
    # Check if we can import all models
    try:
        from apps.signals.models import TradingSignal, ChartImage, ChartPattern, EntryPoint, ChartMLModel
        from apps.trading.models import Symbol
        from apps.data.models import MarketData, TechnicalIndicator
        print_status("✅ All models imported successfully", "SUCCESS")
        steps_completed.append(True)
    except Exception as e:
        print_status(f"❌ Model import failed: {str(e)}", "ERROR")
        steps_completed.append(False)
    
    print()
    
    # FINAL SUMMARY
    print_status("=== FINAL SUMMARY ===", "INFO")
    successful_steps = sum(steps_completed)
    total_steps = len(steps_completed)
    
    print_status(f"Completed {successful_steps}/{total_steps} steps", 
                "SUCCESS" if successful_steps == total_steps else "WARNING")
    
    if successful_steps == total_steps:
        print()
        print_status("🎉 ALL ISSUES FIXED! Signal generation should now work automatically.", "SUCCESS")
        print()
        print_status("🚀 NEXT STEPS TO START AUTOMATIC SIGNAL GENERATION:", "INFO")
        print()
        print_status("1. Start Celery Worker (Terminal 1):", "INFO")
        if os.name == 'nt':  # Windows
            print_status("   Run: start_celery_worker.bat", "INFO")
        else:  # Linux/Mac
            print_status("   Run: ./start_celery_worker.sh", "INFO")
        print()
        print_status("2. Start Celery Beat Scheduler (Terminal 2):", "INFO")
        if os.name == 'nt':  # Windows
            print_status("   Run: start_celery_beat.bat", "INFO")
        else:  # Linux/Mac
            print_status("   Run: ./start_celery_beat.sh", "INFO")
        print()
        print_status("3. Monitor System Health:", "INFO")
        print_status("   Run: python check_system_health.py", "INFO")
        print()
        print_status("4. Check Signal Generation:", "INFO")
        print_status("   Run: python manage.py system_status", "INFO")
        print()
        print_status("5. Optional - Web Monitoring:", "INFO")
        if os.name == 'nt':  # Windows
            print_status("   Run: start_celery_flower.bat", "INFO")
        else:  # Linux/Mac
            print_status("   Run: celery -A ai_trading_engine flower", "INFO")
        print_status("   Then visit: http://localhost:5555", "INFO")
        print()
        print_status("🎯 Your system will now generate signals automatically every hour!", "SUCCESS")
        
    else:
        print()
        print_status("⚠️ Some issues remain. Please check the errors above.", "WARNING")
        print_status("You may need to run individual fix scripts manually.", "WARNING")
    
    print()
    print_status("Master fix script completed!", "INFO")
    print("=" * 80)

if __name__ == "__main__":
    main()

































































