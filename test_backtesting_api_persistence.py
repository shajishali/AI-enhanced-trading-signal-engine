#!/usr/bin/env python3
"""
Test Backtesting API Database Persistence

This script tests that the backtesting API properly uses database persistence
and prevents duplicate signal generation.
"""

import os
import sys
import django
import json
from datetime import datetime
from django.utils import timezone

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.backtesting_api import BacktestAPIView
from apps.trading.models import Symbol
from apps.signals.models import TradingSignal
from django.test import RequestFactory

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

def clear_test_signals():
    """Clear test signals for clean testing"""
    try:
        # Clear signals for AAVE in the test period
        start_date = datetime(2021, 10, 5)
        end_date = datetime(2021, 10, 11)
        
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
                print_status(f"Cleared {deleted_count} existing test signals", "INFO")
            else:
                print_status("No existing test signals to clear", "INFO")
        
        return True
        
    except Exception as e:
        print_status(f"Error clearing test signals: {e}", "ERROR")
        return False

def test_backtesting_api_persistence():
    """Test that backtesting API uses database persistence"""
    print_status("Testing backtesting API database persistence", "INFO")
    
    try:
        # Create request factory
        factory = RequestFactory()
        
        # Test data
        test_data = {
            'symbol': 'AAVE',
            'start_date': '2021-10-05',
            'end_date': '2021-10-11',
            'action': 'generate_signals'
        }
        
        # Create API view instance
        api_view = BacktestAPIView()
        
        # First request - should generate new signals
        print_status("First API request - should generate new signals", "INFO")
        request1 = factory.post('/api/backtesting/', 
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        response1 = api_view.post(request1)
        response_data1 = json.loads(response1.content)
        
        if response_data1['success']:
            signals1 = response_data1['signals']
            source1 = response_data1.get('source', 'unknown')
            print_status(f"First request: {len(signals1)} signals, source: {source1}", "SUCCESS")
        else:
            print_status(f"First request failed: {response_data1.get('error', 'Unknown error')}", "ERROR")
            return False
        
        # Check if signals were saved to database
        aave_symbol = Symbol.objects.filter(symbol='AAVE').first()
        if aave_symbol:
            db_signals = TradingSignal.objects.filter(
                symbol=aave_symbol,
                created_at__gte=timezone.make_aware(datetime(2021, 10, 5)),
                created_at__lte=timezone.make_aware(datetime(2021, 10, 11))
            )
            print_status(f"Found {db_signals.count()} signals in database after first request", "INFO")
        
        # Second request - should return cached signals
        print_status("Second API request - should return cached signals", "INFO")
        request2 = factory.post('/api/backtesting/', 
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        response2 = api_view.post(request2)
        response_data2 = json.loads(response2.content)
        
        if response_data2['success']:
            signals2 = response_data2['signals']
            source2 = response_data2.get('source', 'unknown')
            print_status(f"Second request: {len(signals2)} signals, source: {source2}", "SUCCESS")
        else:
            print_status(f"Second request failed: {response_data2.get('error', 'Unknown error')}", "ERROR")
            return False
        
        # Verify signals are identical (cached)
        if len(signals1) == len(signals2):
            print_status("Signal count matches between requests", "SUCCESS")
            
            # Check if signals are identical (should be cached)
            identical_count = 0
            for i, (s1, s2) in enumerate(zip(signals1, signals2)):
                if (s1['entry_price'] == s2['entry_price'] and 
                    s1['target_price'] == s2['target_price'] and 
                    s1['stop_loss'] == s2['stop_loss']):
                    identical_count += 1
            
            if identical_count == len(signals1):
                print_status("All signals are identical (cached correctly)", "SUCCESS")
                
                # Check source
                if source1 == 'newly_generated' and source2 == 'database_cache':
                    print_status("Source tracking working correctly", "SUCCESS")
                    return True
                else:
                    print_status(f"Source tracking issue: {source1} -> {source2}", "WARNING")
                    return False
            else:
                print_status(f"Only {identical_count}/{len(signals1)} signals are identical", "WARNING")
                return False
        else:
            print_status("Signal count doesn't match between requests", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Error testing API persistence: {e}", "ERROR")
        return False

def test_signal_uniqueness_in_api():
    """Test that API returns unique signals"""
    print_status("Testing signal uniqueness in API response", "INFO")
    
    try:
        # Create request factory
        factory = RequestFactory()
        
        # Test data
        test_data = {
            'symbol': 'AAVE',
            'start_date': '2021-10-05',
            'end_date': '2021-10-11',
            'action': 'generate_signals'
        }
        
        # Create API view instance
        api_view = BacktestAPIView()
        
        # Make request
        request = factory.post('/api/backtesting/', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        response = api_view.post(request)
        response_data = json.loads(response.content)
        
        if not response_data['success']:
            print_status(f"API request failed: {response_data.get('error', 'Unknown error')}", "ERROR")
            return False
        
        signals = response_data['signals']
        print_status(f"API returned {len(signals)} signals", "INFO")
        
        # Check uniqueness
        unique_entry_prices = set()
        unique_target_prices = set()
        unique_stop_losses = set()
        unique_dates = set()
        
        for signal in signals:
            unique_entry_prices.add(signal['entry_price'])
            unique_target_prices.add(signal['target_price'])
            unique_stop_losses.add(signal['stop_loss'])
            unique_dates.add(signal['created_at'][:10])  # Date part only
        
        print_status("API Signal uniqueness analysis:", "INFO")
        print_status(f"  - Unique entry prices: {len(unique_entry_prices)}", "SUCCESS" if len(unique_entry_prices) == len(signals) else "WARNING")
        print_status(f"  - Unique target prices: {len(unique_target_prices)}", "SUCCESS" if len(unique_target_prices) == len(signals) else "WARNING")
        print_status(f"  - Unique stop losses: {len(unique_stop_losses)}", "SUCCESS" if len(unique_stop_losses) == len(signals) else "WARNING")
        print_status(f"  - Unique dates: {len(unique_dates)}", "SUCCESS" if len(unique_dates) == len(signals) else "WARNING")
        
        # Show sample signals
        print_status("Sample API signals:", "INFO")
        for i, signal in enumerate(signals[:3]):
            print_status(f"  Signal {i+1}: {signal['signal_type']} on {signal['created_at'][:10]} at ${signal['entry_price']:.2f} -> ${signal['target_price']:.2f} | Stop: ${signal['stop_loss']:.2f}", "INFO")
        
        # Check if all signals are unique
        all_unique = (len(unique_entry_prices) == len(signals) and 
                     len(unique_target_prices) == len(signals) and 
                     len(unique_stop_losses) == len(signals) and 
                     len(unique_dates) == len(signals))
        
        return all_unique
        
    except Exception as e:
        print_status(f"Error testing API uniqueness: {e}", "ERROR")
        return False

def main():
    """Main test function"""
    print_status("Starting backtesting API persistence test", "INFO")
    
    # Clear test signals for clean test
    clear_test_signals()
    
    # Test 1: API persistence
    api_persistence_working = test_backtesting_api_persistence()
    
    # Test 2: API signal uniqueness
    api_uniqueness_working = test_signal_uniqueness_in_api()
    
    # Summary
    print_status("=== BACKTESTING API PERSISTENCE TEST SUMMARY ===", "INFO")
    print_status(f"API persistence: {'WORKING' if api_persistence_working else 'FAILED'}", "SUCCESS" if api_persistence_working else "ERROR")
    print_status(f"API uniqueness: {'WORKING' if api_uniqueness_working else 'FAILED'}", "SUCCESS" if api_uniqueness_working else "ERROR")
    
    if api_persistence_working and api_uniqueness_working:
        print_status("", "INFO")
        print_status("✅ BACKTESTING API ISSUE FIXED:", "SUCCESS")
        print_status("• API now checks database first before generating signals", "INFO")
        print_status("• Cached signals are returned on subsequent requests", "INFO")
        print_status("• Each signal has unique characteristics", "INFO")
        print_status("• No more duplicate signal generation", "INFO")
        print_status("• Backtesting page will now show unique signals", "INFO")
    
    return api_persistence_working and api_uniqueness_working

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

