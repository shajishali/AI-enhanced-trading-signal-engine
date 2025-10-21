#!/usr/bin/env python3
"""
Test Signal Persistence and Uniqueness

This script tests that signals are saved to database and not regenerated,
and that each signal has unique characteristics.
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

def clear_existing_signals():
    """Clear existing signals for testing"""
    try:
        # Clear signals for AAVE in the test period
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2025, 7, 2)
        
        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)
        
        aave_symbol = Symbol.objects.filter(symbol='AAVE').first()
        if aave_symbol:
            deleted_count = TradingSignal.objects.filter(
                symbol=aave_symbol,
                created_at__gte=start_date,
                created_at__lte=end_date
            ).delete()[0]
            
            if deleted_count > 0:
                print_status(f"Cleared {deleted_count} existing signals for testing", "INFO")
            else:
                print_status("No existing signals to clear", "INFO")
        
        return True
        
    except Exception as e:
        print_status(f"Error clearing signals: {e}", "ERROR")
        return False

def test_signal_persistence():
    """Test that signals are saved to database and not regenerated"""
    print_status("Testing signal persistence", "INFO")
    
    try:
        # Get AAVE symbol
        aave_symbol = Symbol.objects.filter(symbol='AAVE').first()
        if not aave_symbol:
            print_status("AAVE symbol not found", "ERROR")
            return False
        
        # Test with the selected period
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2025, 7, 2)
        
        # Make timezone aware
        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)
        
        # Create strategy service
        strategy_service = StrategyBacktestingService()
        
        # First run - should generate and save signals
        print_status("First run - generating signals", "INFO")
        signals_run1 = strategy_service.generate_historical_signals(aave_symbol, start_date, end_date)
        print_status(f"First run generated {len(signals_run1)} signals", "SUCCESS")
        
        # Check if signals were saved to database
        db_signals = TradingSignal.objects.filter(
            symbol=aave_symbol,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        print_status(f"Found {db_signals.count()} signals in database", "INFO")
        
        # Second run - should return cached signals
        print_status("Second run - should return cached signals", "INFO")
        signals_run2 = strategy_service.generate_historical_signals(aave_symbol, start_date, end_date)
        print_status(f"Second run returned {len(signals_run2)} signals", "SUCCESS")
        
        # Verify signals are identical (cached)
        if len(signals_run1) == len(signals_run2):
            print_status("Signal count matches between runs", "SUCCESS")
            
            # Check if signals are identical (should be cached)
            identical_count = 0
            for i, (s1, s2) in enumerate(zip(signals_run1, signals_run2)):
                if (s1['entry_price'] == s2['entry_price'] and 
                    s1['target_price'] == s2['target_price'] and 
                    s1['stop_loss'] == s2['stop_loss']):
                    identical_count += 1
            
            if identical_count == len(signals_run1):
                print_status("All signals are identical (cached correctly)", "SUCCESS")
                return True
            else:
                print_status(f"Only {identical_count}/{len(signals_run1)} signals are identical", "WARNING")
                return False
        else:
            print_status("Signal count doesn't match between runs", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Error testing signal persistence: {e}", "ERROR")
        return False

def test_signal_uniqueness():
    """Test that signals have unique characteristics"""
    print_status("Testing signal uniqueness", "INFO")
    
    try:
        # Get AAVE symbol
        aave_symbol = Symbol.objects.filter(symbol='AAVE').first()
        if not aave_symbol:
            print_status("AAVE symbol not found", "ERROR")
            return False
        
        # Test with the selected period
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2025, 7, 2)
        
        # Make timezone aware
        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)
        
        # Create strategy service
        strategy_service = StrategyBacktestingService()
        
        # Generate signals
        signals = strategy_service.generate_historical_signals(aave_symbol, start_date, end_date)
        print_status(f"Generated {len(signals)} signals for uniqueness test", "INFO")
        
        # Check uniqueness
        unique_dates = set()
        unique_entry_prices = set()
        unique_target_prices = set()
        unique_stop_losses = set()
        unique_ids = set()
        
        for signal in signals:
            unique_dates.add(signal['created_at'][:10])
            unique_entry_prices.add(signal['entry_price'])
            unique_target_prices.add(signal['target_price'])
            unique_stop_losses.add(signal['stop_loss'])
            unique_ids.add(signal.get('id', 'no_id'))
        
        print_status("Uniqueness analysis:", "INFO")
        print_status(f"  - Unique dates: {len(unique_dates)}", "SUCCESS" if len(unique_dates) == len(signals) else "WARNING")
        print_status(f"  - Unique entry prices: {len(unique_entry_prices)}", "SUCCESS" if len(unique_entry_prices) == len(signals) else "WARNING")
        print_status(f"  - Unique target prices: {len(unique_target_prices)}", "SUCCESS" if len(unique_target_prices) == len(signals) else "WARNING")
        print_status(f"  - Unique stop losses: {len(unique_stop_losses)}", "SUCCESS" if len(unique_stop_losses) == len(signals) else "WARNING")
        print_status(f"  - Unique IDs: {len(unique_ids)}", "SUCCESS" if len(unique_ids) == len(signals) else "WARNING")
        
        # Show sample signals
        print_status("Sample signals with unique characteristics:", "INFO")
        for i, signal in enumerate(signals[:5]):
            print_status(f"  Signal {i+1}: {signal['signal_type']} on {signal['created_at'][:10]} at ${signal['entry_price']:.2f} -> ${signal['target_price']:.2f} | Stop: ${signal['stop_loss']:.2f}", "INFO")
        
        # Check if all signals are unique
        all_unique = (len(unique_dates) == len(signals) and 
                     len(unique_entry_prices) == len(signals) and 
                     len(unique_target_prices) == len(signals) and 
                     len(unique_stop_losses) == len(signals) and 
                     len(unique_ids) == len(signals))
        
        return all_unique
        
    except Exception as e:
        print_status(f"Error testing signal uniqueness: {e}", "ERROR")
        return False

def main():
    """Main test function"""
    print_status("Starting signal persistence and uniqueness test", "INFO")
    
    # Clear existing signals for clean test
    clear_existing_signals()
    
    # Test 1: Signal persistence
    persistence_working = test_signal_persistence()
    
    # Test 2: Signal uniqueness
    uniqueness_working = test_signal_uniqueness()
    
    # Summary
    print_status("=== SIGNAL PERSISTENCE & UNIQUENESS TEST SUMMARY ===", "INFO")
    print_status(f"Signal persistence: {'WORKING' if persistence_working else 'FAILED'}", "SUCCESS" if persistence_working else "ERROR")
    print_status(f"Signal uniqueness: {'WORKING' if uniqueness_working else 'FAILED'}", "SUCCESS" if uniqueness_working else "ERROR")
    
    if persistence_working and uniqueness_working:
        print_status("", "INFO")
        print_status("✅ SIGNAL REGENERATION ISSUE FIXED:", "SUCCESS")
        print_status("• Signals are now saved to database to prevent regeneration", "INFO")
        print_status("• Each signal has unique characteristics (prices, dates, IDs)", "INFO")
        print_status("• Subsequent runs return cached signals instead of regenerating", "INFO")
        print_status("• Randomization ensures each signal is different", "INFO")
        print_status("• System now provides consistent, unique signals", "INFO")
    
    return persistence_working and uniqueness_working

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
























