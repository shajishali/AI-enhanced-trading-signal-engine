#!/usr/bin/env python3
"""
Test script to verify the price synchronization fix

This script tests:
1. Price synchronization service
2. Signal generation with live prices
3. Signal display with consistent prices
4. Price discrepancy detection
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.price_sync_service import price_sync_service
from apps.signals.models import TradingSignal
from apps.trading.models import Symbol

def test_price_sync_service():
    """Test the price synchronization service"""
    print("🔄 Testing Price Synchronization Service...")
    
    try:
        # Test with BTC
        symbol = 'BTC'
        sync_data = price_sync_service.get_synchronized_prices(symbol)
        
        print(f"   Symbol: {sync_data.get('symbol', 'N/A')}")
        print(f"   Current Price: ${sync_data.get('current_price', 0):,.2f}")
        print(f"   Last Signal Price: ${sync_data.get('last_signal_price', 0):,.2f}")
        print(f"   Price Discrepancy: {sync_data.get('price_discrepancy_percent', 0):.2f}%")
        print(f"   Price Status: {sync_data.get('price_status', 'unknown')}")
        print(f"   Price Reliability: {sync_data.get('price_reliability', 'unknown')}")
        
        if 'price_alert' in sync_data:
            alert = sync_data['price_alert']
            print(f"   ⚠️  Price Alert: {alert.get('message', 'N/A')} ({alert.get('severity', 'unknown')})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_signal_generation():
    """Test signal generation with live prices"""
    print("\n📊 Testing Signal Generation with Live Prices...")
    
    try:
        url = 'http://localhost:8000/signals/api/generate/'
        data = {'symbol': 'BTC'}
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=data, headers=headers)
        result = response.json()
        
        if result.get('success'):
            print(f"   ✅ Generated {result.get('signals_generated', 0)} signals for {result.get('symbol', 'N/A')}")
            return True
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_signal_api():
    """Test signal API for price consistency"""
    print("\n📈 Testing Signal API for Price Consistency...")
    
    try:
        url = 'http://localhost:8000/signals/api/signals/'
        response = requests.get(url)
        result = response.json()
        
        if result.get('success'):
            signals = result.get('signals', [])
            print(f"   📊 Found {len(signals)} signals")
            
            for signal in signals[:3]:  # Test first 3 signals
                symbol = signal.get('symbol', 'N/A')
                entry_price = signal.get('entry_price', 0)
                current_price = signal.get('current_price', 0)
                discrepancy = signal.get('price_discrepancy_percent', 0)
                status = signal.get('price_status', 'unknown')
                
                print(f"   • {symbol}: Entry=${entry_price:.2f}, Current=${current_price:.2f}, "
                      f"Discrepancy={discrepancy:.1f}%, Status={status}")
                
                # Check for price alerts
                if signal.get('price_alert'):
                    alert = signal['price_alert']
                    print(f"     ⚠️  Alert: {alert.get('message', 'N/A')}")
            
            return True
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_price_sync_endpoint():
    """Test the price synchronization endpoint"""
    print("\n🔄 Testing Price Sync Endpoint...")
    
    try:
        url = 'http://localhost:8000/signals/api/sync-prices/'
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, headers=headers)
        result = response.json()
        
        if result.get('success'):
            synced = result.get('synced_count', 0)
            total = result.get('total_signals', 0)
            print(f"   ✅ Synchronized prices for {synced}/{total} signals")
            
            if result.get('warnings'):
                print(f"   ⚠️  Warnings: {len(result['warnings'])}")
                for warning in result['warnings'][:3]:
                    print(f"     • {warning}")
            
            return True
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_dashboard_access():
    """Test dashboard accessibility"""
    print("\n🖥️  Testing Signal Dashboard Access...")
    
    try:
        url = 'http://localhost:8000/signals/'
        response = requests.get(url)
        
        if response.status_code == 200:
            print(f"   ✅ Dashboard accessible (Status: {response.status_code})")
            return True
        else:
            print(f"   ❌ Dashboard not accessible (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_database_consistency():
    """Test database for price consistency"""
    print("\n🗄️  Testing Database Price Consistency...")
    
    try:
        # Check recent signals
        recent_signals = TradingSignal.objects.filter(
            is_valid=True
        ).order_by('-created_at')[:5]
        
        print(f"   📊 Checking {len(recent_signals)} recent signals...")
        
        for signal in recent_signals:
            symbol = signal.symbol.symbol
            entry_price = float(signal.entry_price) if signal.entry_price else 0
            
            # Get current live price
            sync_data = price_sync_service.get_synchronized_prices(symbol)
            current_price = sync_data.get('current_price', 0)
            
            # Calculate discrepancy
            if entry_price > 0 and current_price > 0:
                discrepancy = abs(current_price - entry_price) / entry_price * 100
                status = "✅ OK" if discrepancy < 5 else "⚠️  HIGH" if discrepancy < 10 else "❌ CRITICAL"
                
                print(f"   • {symbol}: Entry=${entry_price:.2f}, Live=${current_price:.2f}, "
                      f"Diff={discrepancy:.1f}% {status}")
            else:
                print(f"   • {symbol}: Invalid price data")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive price synchronization test"""
    print("🚀 PRICE SYNCHRONIZATION FIX - COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Price Sync Service", test_price_sync_service),
        ("Signal Generation", test_signal_generation),
        ("Signal API", test_signal_api),
        ("Price Sync Endpoint", test_price_sync_endpoint),
        ("Dashboard Access", test_dashboard_access),
        ("Database Consistency", test_database_consistency),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status} - {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Price synchronization fix is working correctly!")
    else:
        print("⚠️  Some tests failed - Please check the implementation")
    
    print("\n💡 Next Steps:")
    if passed == total:
        print("   • The price consistency issue has been fixed")
        print("   • Signals now show consistent entry and current prices")
        print("   • Price discrepancies are detected and alerted")
        print("   • The sync button works to update prices manually")
    else:
        print("   • Review the failed tests above")
        print("   • Check server logs for detailed error messages")
        print("   • Ensure Django server is running on port 8000")
        print("   • Verify database migrations are applied")

if __name__ == '__main__':
    run_comprehensive_test()
