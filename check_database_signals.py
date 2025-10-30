#!/usr/bin/env python3
"""
Check Database Signals

This script checks if signals are actually being saved to the database.
"""

import os
import sys
import django
from datetime import datetime
from django.utils import timezone

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.trading.models import Symbol
from apps.signals.models import TradingSignal

def print_status(message, status="INFO"):
    """Print status message with timestamp and emoji"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "DEBUG": "🔍"
    }
    print(f"[{timestamp}] {status_symbols.get(status, 'ℹ️')} {message}")

def check_database_signals():
    """Check what signals are in the database"""
    print_status("Checking database signals", "INFO")
    
    try:
        # Get AAVE symbol
        aave_symbol = Symbol.objects.filter(symbol='AAVE').first()
        if not aave_symbol:
            print_status("AAVE symbol not found", "ERROR")
            return
        
        # Check all signals for AAVE
        all_signals = TradingSignal.objects.filter(symbol=aave_symbol).order_by('-created_at')
        print_status(f"Total signals for AAVE in database: {all_signals.count()}", "INFO")
        
        # Show recent signals
        for i, signal in enumerate(all_signals[:5]):
            print_status(f"Signal {i+1}: {signal.signal_type.name if signal.signal_type else 'N/A'} on {signal.created_at.date()} at ${signal.entry_price} -> ${signal.target_price} | Stop: ${signal.stop_loss}", "INFO")
        
        # Check signals in the test period
        start_date = timezone.make_aware(datetime(2021, 10, 5))
        end_date = timezone.make_aware(datetime(2021, 10, 11))
        
        period_signals = TradingSignal.objects.filter(
            symbol=aave_symbol,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).order_by('created_at')
        
        print_status(f"Signals in test period (2021-10-05 to 2021-10-11): {period_signals.count()}", "INFO")
        
        for i, signal in enumerate(period_signals):
            print_status(f"Period Signal {i+1}: {signal.signal_type.name if signal.signal_type else 'N/A'} on {signal.created_at.date()} at ${signal.entry_price} -> ${signal.target_price} | Stop: ${signal.stop_loss}", "INFO")
        
        return period_signals.count() > 0
        
    except Exception as e:
        print_status(f"Error checking database signals: {e}", "ERROR")
        return False

def main():
    """Main function"""
    print_status("Checking database signals", "INFO")
    
    has_signals = check_database_signals()
    
    if has_signals:
        print_status("✅ Signals are being saved to database", "SUCCESS")
    else:
        print_status("❌ No signals found in database", "ERROR")
    
    return has_signals

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)










































