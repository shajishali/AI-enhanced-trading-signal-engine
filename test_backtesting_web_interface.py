#!/usr/bin/env python3
"""
Test Backtesting Web Interface Fix

This script tests the backtesting web interface to ensure
signals are unique and not regenerated.
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

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

def test_backtesting_web_interface():
    """Test the backtesting web interface"""
    print_status("Testing backtesting web interface", "INFO")
    
    try:
        # Test data
        test_data = {
            'symbol': 'AAVE',
            'start_date': '2021-10-05',
            'end_date': '2021-10-11',
            'action': 'generate_signals'
        }
        
        # Make first request
        print_status("Making first request to backtesting API", "INFO")
        response1 = requests.post(
            'http://localhost:8000/signals/api/backtests/',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response1.status_code == 200:
            data1 = response1.json()
            if data1['success']:
                signals1 = data1['signals']
                source1 = data1.get('source', 'unknown')
                print_status(f"First request: {len(signals1)} signals, source: {source1}", "SUCCESS")
            else:
                print_status(f"First request failed: {data1.get('error', 'Unknown error')}", "ERROR")
                return False
        else:
            print_status(f"First request HTTP error: {response1.status_code}", "ERROR")
            return False
        
        # Make second request
        print_status("Making second request to backtesting API", "INFO")
        response2 = requests.post(
            'http://localhost:8000/signals/api/backtests/',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            if data2['success']:
                signals2 = data2['signals']
                source2 = data2.get('source', 'unknown')
                print_status(f"Second request: {len(signals2)} signals, source: {source2}", "SUCCESS")
            else:
                print_status(f"Second request failed: {data2.get('error', 'Unknown error')}", "ERROR")
                return False
        else:
            print_status(f"Second request HTTP error: {response2.status_code}", "ERROR")
            return False
        
        # Check if signals are identical (should be cached)
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
            
    except requests.exceptions.ConnectionError:
        print_status("Could not connect to server. Make sure Django server is running on localhost:8000", "ERROR")
        return False
    except Exception as e:
        print_status(f"Error testing web interface: {e}", "ERROR")
        return False

def test_signal_uniqueness_web():
    """Test signal uniqueness via web interface"""
    print_status("Testing signal uniqueness via web interface", "INFO")
    
    try:
        # Test data
        test_data = {
            'symbol': 'AAVE',
            'start_date': '2021-10-05',
            'end_date': '2021-10-11',
            'action': 'generate_signals'
        }
        
        # Make request
        response = requests.post(
            'http://localhost:8000/signals/api/backtests/',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                signals = data['signals']
                print_status(f"Web API returned {len(signals)} signals", "INFO")
                
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
                
                print_status("Web API Signal uniqueness analysis:", "INFO")
                print_status(f"  - Unique entry prices: {len(unique_entry_prices)}", "SUCCESS" if len(unique_entry_prices) == len(signals) else "WARNING")
                print_status(f"  - Unique target prices: {len(unique_target_prices)}", "SUCCESS" if len(unique_target_prices) == len(signals) else "WARNING")
                print_status(f"  - Unique stop losses: {len(unique_stop_losses)}", "SUCCESS" if len(unique_stop_losses) == len(signals) else "WARNING")
                print_status(f"  - Unique dates: {len(unique_dates)}", "SUCCESS" if len(unique_dates) == len(signals) else "WARNING")
                
                # Show sample signals
                print_status("Sample web API signals:", "INFO")
                for i, signal in enumerate(signals[:3]):
                    print_status(f"  Signal {i+1}: {signal['signal_type']} on {signal['created_at'][:10]} at ${signal['entry_price']:.2f} -> ${signal['target_price']:.2f} | Stop: ${signal['stop_loss']:.2f}", "INFO")
                
                # Check if all signals are unique
                all_unique = (len(unique_entry_prices) == len(signals) and 
                             len(unique_target_prices) == len(signals) and 
                             len(unique_stop_losses) == len(signals) and 
                             len(unique_dates) == len(signals))
                
                return all_unique
            else:
                print_status(f"Web API request failed: {data.get('error', 'Unknown error')}", "ERROR")
                return False
        else:
            print_status(f"Web API HTTP error: {response.status_code}", "ERROR")
            return False
            
    except requests.exceptions.ConnectionError:
        print_status("Could not connect to server. Make sure Django server is running on localhost:8000", "ERROR")
        return False
    except Exception as e:
        print_status(f"Error testing web uniqueness: {e}", "ERROR")
        return False

def main():
    """Main test function"""
    print_status("Starting backtesting web interface test", "INFO")
    
    # Test 1: Web interface persistence
    web_persistence_working = test_backtesting_web_interface()
    
    # Test 2: Web interface uniqueness
    web_uniqueness_working = test_signal_uniqueness_web()
    
    # Summary
    print_status("=== BACKTESTING WEB INTERFACE TEST SUMMARY ===", "INFO")
    print_status(f"Web persistence: {'WORKING' if web_persistence_working else 'FAILED'}", "SUCCESS" if web_persistence_working else "ERROR")
    print_status(f"Web uniqueness: {'WORKING' if web_uniqueness_working else 'FAILED'}", "SUCCESS" if web_uniqueness_working else "ERROR")
    
    if web_persistence_working and web_uniqueness_working:
        print_status("", "INFO")
        print_status("✅ BACKTESTING WEB INTERFACE FIXED:", "SUCCESS")
        print_status("• Web interface now uses database persistence", "INFO")
        print_status("• Signals are cached and not regenerated", "INFO")
        print_status("• Each signal has unique characteristics", "INFO")
        print_status("• Backtesting page shows unique signals", "INFO")
        print_status("• No more duplicate signal generation", "INFO")
    
    return web_persistence_working and web_uniqueness_working

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
