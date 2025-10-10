#!/usr/bin/env python3
"""
Test Signal Date Handling

This script tests the signal date handling to ensure
signals are created with the correct dates.
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

from apps.signals.strategy_backtesting_service import StrategyBacktestingService
from apps.trading.models import Symbol

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

def test_signal_date_handling():
    """Test signal date handling"""
    print_status("Testing signal date handling", "INFO")
    
    try:
        # Get AAVE symbol
        aave_symbol = Symbol.objects.filter(symbol='AAVE').first()
        if not aave_symbol:
            print_status("AAVE symbol not found", "ERROR")
            return False
        
        # Test with specific dates
        start_date = datetime(2021, 10, 5)
        end_date = datetime(2021, 10, 11)
        
        # Make timezone aware
        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)
        
        print_status(f"Testing with dates: {start_date.date()} to {end_date.date()}", "INFO")
        
        # Create strategy service
        strategy_service = StrategyBacktestingService()
        
        # Generate signals
        signals = strategy_service.generate_historical_signals(aave_symbol, start_date, end_date)
        print_status(f"Generated {len(signals)} signals", "INFO")
        
        # Check signal dates
        for i, signal in enumerate(signals):
            signal_date = datetime.fromisoformat(signal['created_at'].replace('Z', '+00:00'))
            print_status(f"Signal {i+1}: {signal['signal_type']} on {signal_date.date()} at ${signal['entry_price']:.2f}", "INFO")
            
            # Check if date is in the correct range
            if signal_date.date() < start_date.date() or signal_date.date() > end_date.date():
                print_status(f"Signal {i+1} date {signal_date.date()} is outside range {start_date.date()} to {end_date.date()}", "WARNING")
        
        return len(signals) > 0
        
    except Exception as e:
        print_status(f"Error testing signal date handling: {e}", "ERROR")
        return False

def main():
    """Main function"""
    print_status("Testing signal date handling", "INFO")
    
    success = test_signal_date_handling()
    
    if success:
        print_status("✅ Signal date handling working", "SUCCESS")
    else:
        print_status("❌ Signal date handling failed", "ERROR")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



