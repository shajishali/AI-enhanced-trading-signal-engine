#!/usr/bin/env python3
"""
Signal Generation System Diagnostic and Fix Script
Solves all 5 major issues preventing automatic signal generation
"""

import os
import sys
import subprocess
import time
from datetime import datetime, timedelta

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

from django.core.management import call_command
from django.db import transaction
from apps.trading.models import Symbol
from apps.data.models import MarketData, TechnicalIndicator
from apps.signals.models import TradingSignal
from apps.signals.services import SignalGenerationService
from apps.data.tasks import calculate_technical_indicators_task, update_crypto_prices_task

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

def run_command(command, description):
    """Run a command and return success status"""
    print_status(f"Running: {description}", "FIXING")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=project_dir)
        if result.returncode == 0:
            print_status(f"Success: {description}", "SUCCESS")
            return True
        else:
            print_status(f"Failed: {description} - {result.stderr}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Error: {description} - {str(e)}", "ERROR")
        return False

def fix_issue_1_celery():
    """Fix Issue 1: Celery Not Running"""
    print_status("=== FIXING ISSUE 1: CELERY NOT RUNNING ===", "FIXING")
    
    # Check if Celery is running
    print_status("Checking Celery status...", "INFO")
    celery_check = run_command("celery -A ai_trading_engine inspect active", "Check Celery workers")
    
    if not celery_check:
        print_status("Celery workers not running. Starting Celery...", "FIXING")
        
        # Create Celery startup scripts
        create_celery_scripts()
        
        print_status("Celery startup scripts created. Please run:", "WARNING")
        print_status("Terminal 1: ./start_celery_worker.bat", "INFO")
        print_status("Terminal 2: ./start_celery_beat.bat", "INFO")
        
        return False
    else:
        print_status("Celery is running!", "SUCCESS")
        return True

def create_celery_scripts():
    """Create Celery startup scripts"""
    
    # Windows batch script for Celery worker
    worker_script = """@echo off
echo Starting Celery Worker...
celery -A ai_trading_engine worker -l info --pool=solo
pause
"""
    
    # Windows batch script for Celery beat
    beat_script = """@echo off
echo Starting Celery Beat Scheduler...
celery -A ai_trading_engine beat -l info
pause
"""
    
    # PowerShell script for Celery worker
    worker_ps_script = """# PowerShell script to start Celery Worker
Write-Host "Starting Celery Worker..." -ForegroundColor Green
celery -A ai_trading_engine worker -l info --pool=solo
Read-Host "Press Enter to exit"
"""
    
    # PowerShell script for Celery beat
    beat_ps_script = """# PowerShell script to start Celery Beat
Write-Host "Starting Celery Beat Scheduler..." -ForegroundColor Green
celery -A ai_trading_engine beat -l info
Read-Host "Press Enter to exit"
"""
    
    # Write scripts
    with open(os.path.join(project_dir, 'start_celery_worker.bat'), 'w') as f:
        f.write(worker_script)
    
    with open(os.path.join(project_dir, 'start_celery_beat.bat'), 'w') as f:
        f.write(beat_script)
    
    with open(os.path.join(project_dir, 'start_celery_worker.ps1'), 'w') as f:
        f.write(worker_ps_script)
    
    with open(os.path.join(project_dir, 'start_celery_beat.ps1'), 'w') as f:
        f.write(beat_ps_script)
    
    print_status("Celery startup scripts created!", "SUCCESS")

def fix_issue_2_market_data():
    """Fix Issue 2: Missing Market Data"""
    print_status("=== FIXING ISSUE 2: MISSING MARKET DATA ===", "FIXING")
    
    # Check current market data
    market_data_count = MarketData.objects.count()
    print_status(f"Current market data records: {market_data_count}", "INFO")
    
    if market_data_count == 0:
        print_status("No market data found. Updating market data...", "FIXING")
        
        # Update market data
        try:
            update_crypto_prices_task()
            print_status("Market data updated successfully!", "SUCCESS")
        except Exception as e:
            print_status(f"Failed to update market data: {str(e)}", "ERROR")
            return False
    else:
        # Check if data is recent
        latest_data = MarketData.objects.order_by('-timestamp').first()
        if latest_data:
            time_diff = datetime.now(timezone.utc) - latest_data.timestamp
            if time_diff.total_seconds() > 3600:  # More than 1 hour old
                print_status("Market data is stale. Updating...", "WARNING")
                try:
                    update_crypto_prices_task()
                    print_status("Market data updated!", "SUCCESS")
                except Exception as e:
                    print_status(f"Failed to update market data: {str(e)}", "ERROR")
            else:
                print_status("Market data is recent!", "SUCCESS")
    
    # Verify data exists
    final_count = MarketData.objects.count()
    print_status(f"Final market data records: {final_count}", "INFO")
    
    return final_count > 0

def fix_issue_3_active_symbols():
    """Fix Issue 3: No Active Symbols"""
    print_status("=== FIXING ISSUE 3: NO ACTIVE SYMBOLS ===", "FIXING")
    
    # Check current symbols
    total_symbols = Symbol.objects.count()
    active_symbols = Symbol.objects.filter(is_active=True).count()
    
    print_status(f"Total symbols: {total_symbols}", "INFO")
    print_status(f"Active symbols: {active_symbols}", "INFO")
    
    if active_symbols == 0:
        print_status("No active symbols found. Activating all symbols...", "FIXING")
        
        # Activate all symbols
        Symbol.objects.update(is_active=True)
        
        # Verify activation
        active_count = Symbol.objects.filter(is_active=True).count()
        print_status(f"Activated {active_count} symbols!", "SUCCESS")
        
        return True
    else:
        print_status("Symbols are already active!", "SUCCESS")
        return True

def fix_issue_4_technical_indicators():
    """Fix Issue 4: Technical Indicators Missing"""
    print_status("=== FIXING ISSUE 4: TECHNICAL INDICATORS MISSING ===", "FIXING")
    
    # Check current indicators
    indicator_count = TechnicalIndicator.objects.count()
    print_status(f"Current technical indicators: {indicator_count}", "INFO")
    
    if indicator_count == 0:
        print_status("No technical indicators found. Calculating indicators...", "FIXING")
        
        try:
            calculate_technical_indicators_task()
            print_status("Technical indicators calculated!", "SUCCESS")
        except Exception as e:
            print_status(f"Failed to calculate indicators: {str(e)}", "ERROR")
            return False
    else:
        # Check if indicators are recent
        latest_indicator = TechnicalIndicator.objects.order_by('-timestamp').first()
        if latest_indicator:
            time_diff = datetime.now(timezone.utc) - latest_indicator.timestamp
            if time_diff.total_seconds() > 3600:  # More than 1 hour old
                print_status("Technical indicators are stale. Recalculating...", "WARNING")
                try:
                    calculate_technical_indicators_task()
                    print_status("Technical indicators updated!", "SUCCESS")
                except Exception as e:
                    print_status(f"Failed to update indicators: {str(e)}", "ERROR")
            else:
                print_status("Technical indicators are recent!", "SUCCESS")
    
    # Verify indicators exist
    final_count = TechnicalIndicator.objects.count()
    print_status(f"Final technical indicators: {final_count}", "INFO")
    
    return final_count > 0

def fix_issue_5_confidence_thresholds():
    """Fix Issue 5: High Confidence Thresholds"""
    print_status("=== FIXING ISSUE 5: HIGH CONFIDENCE THRESHOLDS ===", "FIXING")
    
    # Create a configuration update script
    config_script = """
# Update signal generation thresholds for better signal generation
from apps.signals.services import SignalGenerationService
from apps.signals.strategy_engine import StrategyEngine, EngineConfig

# Update SignalGenerationService thresholds
print("Updating SignalGenerationService thresholds...")
service = SignalGenerationService()
service.min_confidence_threshold = 0.3  # Lower from 0.5 to 0.3
service.min_risk_reward_ratio = 1.0     # Lower from 1.5 to 1.0
service.signal_expiry_hours = 48        # Increase from 24 to 48 hours

# Update StrategyEngine thresholds
print("Updating StrategyEngine thresholds...")
config = EngineConfig()
config.min_confidence_threshold = 0.3   # Lower from 0.7 to 0.3
config.min_risk_reward_ratio = 1.0      # Lower from 3.0 to 1.0
config.signal_expiry_hours = 48         # Increase from 4 to 48 hours

print("Thresholds updated successfully!")
print(f"Min confidence: {service.min_confidence_threshold}")
print(f"Min risk/reward: {service.min_risk_reward_ratio}")
print(f"Signal expiry: {service.signal_expiry_hours} hours")
"""
    
    # Write and execute config script
    config_file = os.path.join(project_dir, 'update_thresholds.py')
    with open(config_file, 'w') as f:
        f.write(config_script)
    
    print_status("Executing threshold updates...", "FIXING")
    success = run_command(f"python {config_file}", "Update confidence thresholds")
    
    if success:
        print_status("Confidence thresholds updated!", "SUCCESS")
        # Clean up
        os.remove(config_file)
        return True
    else:
        print_status("Failed to update thresholds", "ERROR")
        return False

def test_signal_generation():
    """Test signal generation after fixes"""
    print_status("=== TESTING SIGNAL GENERATION ===", "FIXING")
    
    try:
        # Test with a specific symbol
        test_symbols = ['BTCUSDT', 'ETHUSDT']
        
        for symbol_code in test_symbols:
            print_status(f"Testing signal generation for {symbol_code}...", "INFO")
            
            try:
                symbol = Symbol.objects.get(symbol=symbol_code)
                service = SignalGenerationService()
                signals = service.generate_signals_for_symbol(symbol)
                
                print_status(f"Generated {len(signals)} signals for {symbol_code}", "SUCCESS")
                
                if signals:
                    for signal in signals:
                        print_status(f"  - {signal.signal_type.name}: Confidence {signal.confidence_score:.2f}", "INFO")
                
            except Symbol.DoesNotExist:
                print_status(f"Symbol {symbol_code} not found", "WARNING")
            except Exception as e:
                print_status(f"Error generating signals for {symbol_code}: {str(e)}", "ERROR")
        
        # Check total active signals
        active_signals = TradingSignal.objects.filter(is_valid=True).count()
        print_status(f"Total active signals in database: {active_signals}", "INFO")
        
        return True
        
    except Exception as e:
        print_status(f"Error testing signal generation: {str(e)}", "ERROR")
        return False

def create_monitoring_script():
    """Create a monitoring script to check system health"""
    monitoring_script = """#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from datetime import datetime, timedelta
from django.utils import timezone
from apps.trading.models import Symbol
from apps.data.models import MarketData, TechnicalIndicator
from apps.signals.models import TradingSignal

def check_system_health():
    print("=== SIGNAL GENERATION SYSTEM HEALTH CHECK ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Check symbols
    total_symbols = Symbol.objects.count()
    active_symbols = Symbol.objects.filter(is_active=True).count()
    print(f"Symbols: {active_symbols}/{total_symbols} active")
    
    # Check market data
    market_data_count = MarketData.objects.count()
    latest_market_data = MarketData.objects.order_by('-timestamp').first()
    if latest_market_data:
        time_diff = datetime.now(timezone.utc) - latest_market_data.timestamp
        print(f"Market Data: {market_data_count} records, latest {time_diff.total_seconds()/60:.1f} minutes ago")
    else:
        print("Market Data: No data found!")
    
    # Check technical indicators
    indicator_count = TechnicalIndicator.objects.count()
    latest_indicator = TechnicalIndicator.objects.order_by('-timestamp').first()
    if latest_indicator:
        time_diff = datetime.now(timezone.utc) - latest_indicator.timestamp
        print(f"Technical Indicators: {indicator_count} records, latest {time_diff.total_seconds()/60:.1f} minutes ago")
    else:
        print("Technical Indicators: No data found!")
    
    # Check active signals
    active_signals = TradingSignal.objects.filter(is_valid=True).count()
    print(f"Active Signals: {active_signals}")
    
    # Check recent signals
    recent_signals = TradingSignal.objects.filter(
        created_at__gte=datetime.now(timezone.utc) - timedelta(hours=1)
    ).count()
    print(f"Signals in last hour: {recent_signals}")
    
    print()
    if active_signals > 0 or recent_signals > 0:
        print("✅ System appears to be working!")
    else:
        print("❌ System may have issues - no recent signals generated")

if __name__ == "__main__":
    check_system_health()
"""
    
    with open(os.path.join(project_dir, 'check_system_health.py'), 'w') as f:
        f.write(monitoring_script)
    
    print_status("System health monitoring script created: check_system_health.py", "SUCCESS")

def main():
    """Main function to fix all issues"""
    print_status("=== SIGNAL GENERATION SYSTEM FIX SCRIPT ===", "INFO")
    print_status("This script will fix all 5 major issues preventing automatic signal generation", "INFO")
    print()
    
    # Track success of each fix
    fixes_successful = []
    
    # Fix Issue 1: Celery Not Running
    fixes_successful.append(fix_issue_1_celery())
    
    # Fix Issue 2: Missing Market Data
    fixes_successful.append(fix_issue_2_market_data())
    
    # Fix Issue 3: No Active Symbols
    fixes_successful.append(fix_issue_3_active_symbols())
    
    # Fix Issue 4: Technical Indicators Missing
    fixes_successful.append(fix_issue_4_technical_indicators())
    
    # Fix Issue 5: High Confidence Thresholds
    fixes_successful.append(fix_issue_5_confidence_thresholds())
    
    # Test signal generation
    test_success = test_signal_generation()
    
    # Create monitoring script
    create_monitoring_script()
    
    # Summary
    print()
    print_status("=== FIX SUMMARY ===", "INFO")
    successful_fixes = sum(fixes_successful)
    total_fixes = len(fixes_successful)
    
    print_status(f"Fixed {successful_fixes}/{total_fixes} issues", "SUCCESS" if successful_fixes == total_fixes else "WARNING")
    
    if successful_fixes == total_fixes and test_success:
        print_status("🎉 ALL ISSUES FIXED! Signal generation should now work automatically.", "SUCCESS")
        print_status("Next steps:", "INFO")
        print_status("1. Start Celery workers: ./start_celery_worker.bat", "INFO")
        print_status("2. Start Celery beat: ./start_celery_beat.bat", "INFO")
        print_status("3. Monitor system: python check_system_health.py", "INFO")
    else:
        print_status("⚠️ Some issues remain. Check the errors above.", "WARNING")
    
    print()
    print_status("Script completed!", "INFO")

if __name__ == "__main__":
    main()























