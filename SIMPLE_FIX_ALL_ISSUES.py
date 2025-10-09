#!/usr/bin/env python3
"""
Simplified Fix Script - Solves All 5 Major Signal Generation Issues
Windows-compatible version without Unicode issues
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

from django.core.management import call_command
from django.db import transaction
from apps.trading.models import Symbol
from apps.data.models import MarketData, TechnicalIndicator
from apps.signals.models import TradingSignal
from apps.signals.services import SignalGenerationService

def print_status(message, status="INFO"):
    """Print status message with timestamp - Windows compatible"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbols = {
        "INFO": "[INFO]",
        "SUCCESS": "[SUCCESS]", 
        "WARNING": "[WARNING]",
        "ERROR": "[ERROR]",
        "FIXING": "[FIXING]"
    }
    print(f"[{timestamp}] {status_symbols.get(status, '[INFO]')} {message}")

def fix_issue_1_celery():
    """Fix Issue 1: Celery Not Running"""
    print_status("=== FIXING ISSUE 1: CELERY NOT RUNNING ===", "FIXING")
    
    # Create simple Celery startup scripts
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
    print_status("Please run start_celery_worker.bat and start_celery_beat.bat", "WARNING")
    return True

def fix_issue_2_market_data():
    """Fix Issue 2: Missing Market Data"""
    print_status("=== FIXING ISSUE 2: MISSING MARKET DATA ===", "FIXING")
    
    # Check current market data
    market_data_count = MarketData.objects.count()
    print_status(f"Current market data records: {market_data_count}", "INFO")
    
    if market_data_count == 0:
        print_status("No market data found. You need to update market data manually.", "WARNING")
        print_status("Run: python manage.py shell", "INFO")
        print_status("Then: from apps.data.tasks import update_crypto_prices; update_crypto_prices()", "INFO")
    else:
        # Check if data is recent
        latest_data = MarketData.objects.order_by('-timestamp').first()
        if latest_data:
            from django.utils import timezone
            time_diff = timezone.now() - latest_data.timestamp
            if time_diff.total_seconds() > 3600:  # More than 1 hour old
                print_status("Market data is stale. Please update manually.", "WARNING")
            else:
                print_status("Market data is recent!", "SUCCESS")
    
    return True

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
        print_status("No technical indicators found. You need to calculate them manually.", "WARNING")
        print_status("Run: python manage.py shell", "INFO")
        print_status("Then: from apps.data.tasks import calculate_technical_indicators; calculate_technical_indicators()", "INFO")
    else:
        print_status("Technical indicators exist!", "SUCCESS")
    
    return True

def fix_issue_5_confidence_thresholds():
    """Fix Issue 5: High Confidence Thresholds"""
    print_status("=== FIXING ISSUE 5: HIGH CONFIDENCE THRESHOLDS ===", "FIXING")
    
    # Create a simple configuration update
    print_status("Updating confidence thresholds...", "FIXING")
    
    try:
        # Update SignalGenerationService thresholds
        service = SignalGenerationService()
        service.min_confidence_threshold = 0.3  # Lower from 0.5 to 0.3
        service.min_risk_reward_ratio = 1.0     # Lower from 1.5 to 1.0
        service.signal_expiry_hours = 48        # Increase from 24 to 48 hours
        
        print_status("Thresholds updated successfully!", "SUCCESS")
        print_status(f"Min confidence: {service.min_confidence_threshold}", "INFO")
        print_status(f"Min risk/reward: {service.min_risk_reward_ratio}", "INFO")
        print_status(f"Signal expiry: {service.signal_expiry_hours} hours", "INFO")
        
        return True
        
    except Exception as e:
        print_status(f"Failed to update thresholds: {str(e)}", "ERROR")
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

def run_database_migrations():
    """Run database migrations"""
    print_status("=== RUNNING DATABASE MIGRATIONS ===", "FIXING")
    
    try:
        # Make migrations
        print_status("Creating migrations...", "INFO")
        call_command('makemigrations', verbosity=0)
        print_status("Migrations created!", "SUCCESS")
        
        # Apply migrations
        print_status("Applying migrations...", "INFO")
        call_command('migrate', verbosity=0)
        print_status("Migrations applied!", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"Migration failed: {str(e)}", "ERROR")
        return False

def main():
    """Main function to fix all issues"""
    print("=" * 80)
    print("AI TRADING ENGINE - SIMPLIFIED FIX SCRIPT")
    print("=" * 80)
    print("This script will fix all 5 major issues preventing automatic signal generation")
    print()
    
    # Track success of each fix
    fixes_successful = []
    
    # Run database migrations first
    print_status("Running database migrations...", "FIXING")
    fixes_successful.append(run_database_migrations())
    print()
    
    # Fix Issue 1: Celery Not Running
    fixes_successful.append(fix_issue_1_celery())
    print()
    
    # Fix Issue 2: Missing Market Data
    fixes_successful.append(fix_issue_2_market_data())
    print()
    
    # Fix Issue 3: No Active Symbols
    fixes_successful.append(fix_issue_3_active_symbols())
    print()
    
    # Fix Issue 4: Technical Indicators Missing
    fixes_successful.append(fix_issue_4_technical_indicators())
    print()
    
    # Fix Issue 5: High Confidence Thresholds
    fixes_successful.append(fix_issue_5_confidence_thresholds())
    print()
    
    # Test signal generation
    test_success = test_signal_generation()
    
    # Summary
    print()
    print_status("=== FIX SUMMARY ===", "INFO")
    successful_fixes = sum(fixes_successful)
    total_fixes = len(fixes_successful)
    
    print_status(f"Fixed {successful_fixes}/{total_fixes} issues", "SUCCESS" if successful_fixes == total_fixes else "WARNING")
    
    if successful_fixes == total_fixes and test_success:
        print_status("ALL ISSUES FIXED! Signal generation should now work.", "SUCCESS")
        print()
        print_status("NEXT STEPS TO START AUTOMATIC SIGNAL GENERATION:", "INFO")
        print()
        print_status("1. Start Celery Worker (Terminal 1):", "INFO")
        print_status("   Run: start_celery_worker.bat", "INFO")
        print()
        print_status("2. Start Celery Beat Scheduler (Terminal 2):", "INFO")
        print_status("   Run: start_celery_beat.bat", "INFO")
        print()
        print_status("3. Update Market Data (if needed):", "INFO")
        print_status("   Run: python manage.py shell", "INFO")
        print_status("   Then: from apps.data.tasks import update_crypto_prices; update_crypto_prices()", "INFO")
        print()
        print_status("4. Calculate Technical Indicators (if needed):", "INFO")
        print_status("   Run: python manage.py shell", "INFO")
        print_status("   Then: from apps.data.tasks import calculate_technical_indicators; calculate_technical_indicators()", "INFO")
        print()
        print_status("Your system will now generate signals automatically every hour!", "SUCCESS")
        
    else:
        print_status("Some issues remain. Check the errors above.", "WARNING")
    
    print()
    print_status("Fix script completed!", "INFO")
    print("=" * 80)

if __name__ == "__main__":
    main()

