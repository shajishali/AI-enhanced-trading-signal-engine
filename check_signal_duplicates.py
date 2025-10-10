#!/usr/bin/env python3
"""
Duplicate Signal Detection and Prevention

This script checks for duplicate signals in the backtesting system and
implements prevention mechanisms.
"""

import os
import sys
import django
from datetime import datetime
from django.utils import timezone
from collections import defaultdict

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

def check_signal_duplicates(signals):
    """Check for duplicate signals based on various criteria"""
    print_status("Checking for duplicate signals", "INFO")
    
    duplicates_found = []
    
    # Check for exact duplicates (same timestamp, symbol, signal_type)
    timestamp_symbol_type = defaultdict(list)
    
    # Check for price duplicates (same entry_price, target_price, stop_loss)
    price_triplets = defaultdict(list)
    
    # Check for date duplicates (same date)
    date_signals = defaultdict(list)
    
    for i, signal in enumerate(signals):
        timestamp = signal['created_at'][:10]  # Get date part
        symbol = signal['symbol']
        signal_type = signal['signal_type']
        entry_price = signal['entry_price']
        target_price = signal['target_price']
        stop_loss = signal['stop_loss']
        
        # Check timestamp + symbol + type duplicates
        key1 = f"{timestamp}_{symbol}_{signal_type}"
        timestamp_symbol_type[key1].append(i)
        
        # Check price triplet duplicates
        key2 = f"{entry_price}_{target_price}_{stop_loss}"
        price_triplets[key2].append(i)
        
        # Check date duplicates
        date_signals[timestamp].append(i)
    
    # Report duplicates
    duplicate_count = 0
    
    # Check timestamp + symbol + type duplicates
    for key, indices in timestamp_symbol_type.items():
        if len(indices) > 1:
            duplicates_found.append(f"Exact duplicates (timestamp+symbol+type): Signals {indices} - {key}")
            duplicate_count += len(indices) - 1
    
    # Check price triplet duplicates
    for key, indices in price_triplets.items():
        if len(indices) > 1:
            duplicates_found.append(f"Price duplicates: Signals {indices} - Entry:${key.split('_')[0]}, Target:${key.split('_')[1]}, Stop:${key.split('_')[2]}")
            duplicate_count += len(indices) - 1
    
    # Check date duplicates (same day)
    for date, indices in date_signals.items():
        if len(indices) > 1:
            duplicates_found.append(f"Same date signals: Signals {indices} on {date}")
            duplicate_count += len(indices) - 1
    
    if duplicates_found:
        print_status(f"Found {duplicate_count} duplicate signals:", "WARNING")
        for duplicate in duplicates_found:
            print_status(f"  - {duplicate}", "WARNING")
        return False
    else:
        print_status("No duplicate signals found", "SUCCESS")
        return True

def analyze_signal_patterns(signals):
    """Analyze signal patterns for potential issues"""
    print_status("Analyzing signal patterns", "INFO")
    
    # Group signals by date
    signals_by_date = defaultdict(list)
    for signal in signals:
        date = signal['created_at'][:10]
        signals_by_date[date].append(signal)
    
    # Check for multiple signals on same date
    same_date_count = 0
    for date, date_signals in signals_by_date.items():
        if len(date_signals) > 1:
            same_date_count += len(date_signals)
            print_status(f"Multiple signals on {date}: {len(date_signals)} signals", "WARNING")
    
    # Check signal type alternation
    signal_types = [signal['signal_type'] for signal in signals]
    consecutive_same_type = 0
    max_consecutive = 0
    current_consecutive = 1
    
    for i in range(1, len(signal_types)):
        if signal_types[i] == signal_types[i-1]:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 1
    
    if max_consecutive > 1:
        print_status(f"Consecutive same-type signals: {max_consecutive} in a row", "WARNING")
    
    # Check price progression
    entry_prices = [signal['entry_price'] for signal in signals]
    price_changes = []
    for i in range(1, len(entry_prices)):
        change = entry_prices[i] - entry_prices[i-1]
        price_changes.append(change)
    
    if len(price_changes) > 0:
        avg_change = sum(price_changes) / len(price_changes)
        print_status(f"Average price change between signals: ${avg_change:.2f}", "INFO")
    
    return {
        'same_date_count': same_date_count,
        'max_consecutive_same_type': max_consecutive,
        'total_signals': len(signals)
    }

def test_duplicate_prevention():
    """Test the current signal generation for duplicates"""
    print_status("Testing signal generation for duplicates", "INFO")
    
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
        
        # Generate signals multiple times to check for consistency
        print_status("Generating signals multiple times to check consistency", "INFO")
        
        all_signals = []
        for test_run in range(3):
            print_status(f"Test run {test_run + 1}/3", "DEBUG")
            signals = strategy_service.generate_historical_signals(aave_symbol, start_date, end_date)
            all_signals.extend(signals)
            print_status(f"Run {test_run + 1}: Generated {len(signals)} signals", "INFO")
        
        print_status(f"Total signals across all runs: {len(all_signals)}", "INFO")
        
        # Check for duplicates
        no_duplicates = check_signal_duplicates(all_signals)
        
        # Analyze patterns
        patterns = analyze_signal_patterns(all_signals)
        
        return no_duplicates and patterns['max_consecutive_same_type'] <= 2
        
    except Exception as e:
        print_status(f"Error testing duplicate prevention: {e}", "ERROR")
        return False

def check_database_duplicates():
    """Check for duplicates in the database"""
    print_status("Checking database for duplicate signals", "INFO")
    
    try:
        # Check for signals with same symbol, signal_type, and created_at
        from django.db.models import Count
        from apps.signals.models import TradingSignal
        
        duplicates = TradingSignal.objects.values('symbol', 'signal_type', 'created_at').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicates.exists():
            print_status(f"Found {duplicates.count()} duplicate groups in database", "WARNING")
            for dup in duplicates[:5]:  # Show first 5
                print_status(f"  - {dup['symbol']} {dup['signal_type']} on {dup['created_at']} ({dup['count']} times)", "WARNING")
            return False
        else:
            print_status("No duplicates found in database", "SUCCESS")
            return True
            
    except Exception as e:
        print_status(f"Error checking database duplicates: {e}", "ERROR")
        return False

def main():
    """Main duplicate checking function"""
    print_status("Starting duplicate signal detection", "INFO")
    
    # Test 1: Check signal generation for duplicates
    generation_clean = test_duplicate_prevention()
    
    # Test 2: Check database for duplicates
    database_clean = check_database_duplicates()
    
    # Summary
    print_status("=== DUPLICATE CHECK SUMMARY ===", "INFO")
    print_status(f"Signal generation duplicates: {'NONE FOUND' if generation_clean else 'DUPLICATES FOUND'}", "SUCCESS" if generation_clean else "WARNING")
    print_status(f"Database duplicates: {'NONE FOUND' if database_clean else 'DUPLICATES FOUND'}", "SUCCESS" if database_clean else "WARNING")
    
    if not generation_clean or not database_clean:
        print_status("", "INFO")
        print_status("⚠️ DUPLICATE ISSUES DETECTED:", "WARNING")
        print_status("• Consider implementing duplicate prevention logic", "INFO")
        print_status("• Add unique constraints to prevent database duplicates", "INFO")
        print_status("• Implement signal deduplication before saving", "INFO")
    
    return generation_clean and database_clean

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



