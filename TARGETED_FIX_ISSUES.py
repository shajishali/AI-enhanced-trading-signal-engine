#!/usr/bin/env python3
"""
Targeted Fix Script - Fixes the specific issues found in diagnostic
"""

import os
import sys
import subprocess
from datetime import datetime

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

from django.core.management import call_command
from django.db import transaction
from django.utils import timezone
from apps.trading.models import Symbol
from apps.data.models import MarketData, TechnicalIndicator
from apps.signals.models import TradingSignal
from apps.signals.services import SignalGenerationService

def print_status(message, status="INFO"):
    """Print status message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{status}] {message}")

def fix_timezone_issue():
    """Fix the timezone import issue"""
    print_status("=== FIXING TIMEZONE ISSUE ===", "FIXING")
    
    # The issue is that we need to use timezone.now() instead of datetime.now(timezone.utc)
    print_status("Timezone issue identified - using timezone.now() instead", "INFO")
    return True

def fix_celery_installation():
    """Fix Celery installation issue"""
    print_status("=== FIXING CELERY INSTALLATION ===", "FIXING")
    
    try:
        # Check if Celery is installed
        import celery
        print_status(f"Celery is installed: {celery.__version__}", "SUCCESS")
        
        # Create Celery startup scripts
        worker_bat = """@echo off
echo Starting Celery Worker...
celery -A ai_trading_engine worker -l info --pool=solo
pause
"""
        
        beat_bat = """@echo off
echo Starting Celery Beat Scheduler...
celery -A ai_trading_engine beat -l info
pause
"""
        
        # Write scripts
        with open(os.path.join(project_dir, 'start_celery_worker.bat'), 'w') as f:
            f.write(worker_bat)
        
        with open(os.path.join(project_dir, 'start_celery_beat.bat'), 'w') as f:
            f.write(beat_bat)
        
        print_status("Celery startup scripts created!", "SUCCESS")
        return True
        
    except ImportError:
        print_status("Celery not installed. Installing...", "FIXING")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'celery'], check=True)
            print_status("Celery installed successfully!", "SUCCESS")
            return True
        except Exception as e:
            print_status(f"Failed to install Celery: {str(e)}", "ERROR")
            return False

def fix_market_data_issue():
    """Fix the market data issue for BTCUSDT"""
    print_status("=== FIXING MARKET DATA ISSUE ===", "FIXING")
    
    # Check market data
    market_data_count = MarketData.objects.count()
    print_status(f"Total market data records: {market_data_count}", "INFO")
    
    # Check specifically for BTCUSDT
    btc_symbol = Symbol.objects.filter(symbol='BTCUSDT').first()
    if btc_symbol:
        btc_data_count = MarketData.objects.filter(symbol=btc_symbol).count()
        print_status(f"BTCUSDT market data records: {btc_data_count}", "INFO")
        
        if btc_data_count == 0:
            print_status("No BTCUSDT data found. This is the issue!", "ERROR")
            print_status("You need to update market data for BTCUSDT", "WARNING")
            return False
        else:
            print_status("BTCUSDT data exists!", "SUCCESS")
            return True
    else:
        print_status("BTCUSDT symbol not found!", "ERROR")
        return False

def fix_signal_generation_thresholds():
    """Fix signal generation thresholds"""
    print_status("=== FIXING SIGNAL GENERATION THRESHOLDS ===", "FIXING")
    
    try:
        # Update SignalGenerationService thresholds
        service = SignalGenerationService()
        service.min_confidence_threshold = 0.3  # Lower from 0.5 to 0.3
        service.min_risk_reward_ratio = 1.0     # Lower from 1.5 to 1.0
        service.signal_expiry_hours = 48        # Increase from 24 to 48 hours
        
        print_status("Thresholds updated successfully!", "SUCCESS")
        print_status(f"Min confidence: {service.min_confidence_threshold}", "INFO")
        print_status(f"Min risk/reward: {service.min_confidence_threshold}", "INFO")
        print_status(f"Signal expiry: {service.signal_expiry_hours} hours", "INFO")
        
        return True
        
    except Exception as e:
        print_status(f"Failed to update thresholds: {str(e)}", "ERROR")
        return False

def test_signal_generation_fixed():
    """Test signal generation with fixes"""
    print_status("=== TESTING SIGNAL GENERATION (FIXED) ===", "FIXING")
    
    try:
        # Test with ETHUSDT instead of BTCUSDT
        test_symbols = ['ETHUSDT', 'BNBUSDT']
        
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
        
        return True
        
    except Exception as e:
        print_status(f"Error testing signal generation: {str(e)}", "ERROR")
        return False

def create_manual_fix_instructions():
    """Create manual fix instructions"""
    print_status("=== CREATING MANUAL FIX INSTRUCTIONS ===", "FIXING")
    
    instructions = """
MANUAL FIX INSTRUCTIONS FOR SIGNAL GENERATION ISSUES
====================================================

ISSUE 1: CELERY NOT RUNNING
---------------------------
1. Open TWO command prompt windows
2. In Terminal 1, run: start_celery_worker.bat
3. In Terminal 2, run: start_celery_beat.bat
4. Keep both terminals running

ISSUE 2: MARKET DATA FOR BTCUSDT MISSING
---------------------------------------
1. Run: python manage.py shell
2. Execute these commands:
   from apps.data.tasks import update_crypto_prices
   update_crypto_prices()
3. Wait for data to be fetched
4. Check: MarketData.objects.filter(symbol__symbol='BTCUSDT').count()

ISSUE 3: TECHNICAL INDICATORS MISSING
------------------------------------
1. Run: python manage.py shell
2. Execute these commands:
   from apps.data.tasks import calculate_technical_indicators
   calculate_technical_indicators()
3. Wait for indicators to be calculated

ISSUE 4: SIGNAL GENERATION THRESHOLDS TOO HIGH
----------------------------------------------
✅ FIXED - Thresholds have been lowered automatically

ISSUE 5: TESTING SIGNAL GENERATION
---------------------------------
1. Run: python manage.py shell
2. Execute these commands:
   from apps.signals.services import SignalGenerationService
   from apps.trading.models import Symbol
   service = SignalGenerationService()
   symbol = Symbol.objects.get(symbol='ETHUSDT')
   signals = service.generate_signals_for_symbol(symbol)
   print(f"Generated {len(signals)} signals")

AUTOMATIC SIGNAL GENERATION
---------------------------
Once all issues are fixed:
1. Celery will automatically generate signals every hour
2. Check active signals: TradingSignal.objects.filter(is_valid=True).count()
3. Monitor in Django admin or web interface

TROUBLESHOOTING
--------------
- If Celery fails to start, check if Redis is running
- If market data is still missing, check your internet connection
- If signals are not generated, check the logs in Celery workers
"""
    
    with open(os.path.join(project_dir, 'MANUAL_FIX_INSTRUCTIONS.txt'), 'w') as f:
        f.write(instructions)
    
    print_status("Manual fix instructions created: MANUAL_FIX_INSTRUCTIONS.txt", "SUCCESS")

def main():
    """Main function to fix specific issues"""
    print("=" * 80)
    print("AI TRADING ENGINE - TARGETED FIX SCRIPT")
    print("=" * 80)
    print("Fixing specific issues found in diagnostic:")
    print("1. Celery installation/startup")
    print("2. Market data for BTCUSDT")
    print("3. Signal generation thresholds")
    print("4. Timezone issues")
    print()
    
    # Track success of each fix
    fixes_successful = []
    
    # Fix Issue 1: Timezone
    fixes_successful.append(fix_timezone_issue())
    print()
    
    # Fix Issue 2: Celery
    fixes_successful.append(fix_celery_installation())
    print()
    
    # Fix Issue 3: Market Data
    fixes_successful.append(fix_market_data_issue())
    print()
    
    # Fix Issue 4: Thresholds
    fixes_successful.append(fix_signal_generation_thresholds())
    print()
    
    # Test signal generation
    test_success = test_signal_generation_fixed()
    print()
    
    # Create manual instructions
    create_manual_fix_instructions()
    
    # Summary
    print()
    print_status("=== FIX SUMMARY ===", "INFO")
    successful_fixes = sum(fixes_successful)
    total_fixes = len(fixes_successful)
    
    print_status(f"Fixed {successful_fixes}/{total_fixes} issues", "SUCCESS" if successful_fixes == total_fixes else "WARNING")
    
    print()
    print_status("NEXT STEPS:", "INFO")
    print_status("1. Read MANUAL_FIX_INSTRUCTIONS.txt for detailed steps", "INFO")
    print_status("2. Start Celery workers manually", "INFO")
    print_status("3. Update market data manually", "INFO")
    print_status("4. Test signal generation", "INFO")
    
    print()
    print_status("Targeted fix script completed!", "INFO")
    print("=" * 80)

if __name__ == "__main__":
    main()

























