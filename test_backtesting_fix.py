#!/usr/bin/env python3
"""
Test Backtesting Fix

This script tests the fixed backtesting system to ensure it's working properly.
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from apps.trading.models import Symbol
from apps.data.models import MarketData
from apps.signals.models import TradingSignal


def test_backtesting_api():
    """Test the backtesting API"""
    print("🧪 Testing Backtesting API...")
    
    # Create a test client
    client = Client()
    
    # Login
    user = User.objects.get(username='testuser')
    client.force_login(user)
    
    # Test backtesting API
    symbol = Symbol.objects.get(symbol='AAVEUSDT')
    start_date = '2021-01-01'
    end_date = '2021-12-31'
    
    # Make API request
    response = client.post('/signals/api/backtests/', 
        data=json.dumps({
            'symbol': 'AAVEUSDT',
            'start_date': f'{start_date}T00:00:00Z',
            'end_date': f'{end_date}T23:59:59Z'
        }),
        content_type='application/json'
    )
    
    print(f'📊 API Response Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Success: {data.get("success")}')
        print(f'📈 Total signals: {data.get("total_signals", 0)}')
        print(f'🎯 Action: {data.get("action")}')
        
        signals = data.get('signals', [])
        if signals:
            print(f'📊 Sample signal:')
            sample = signals[0]
            print(f'   Symbol: {sample.get("symbol")}')
            print(f'   Type: {sample.get("signal_type")}')
            print(f'   Entry: ${sample.get("entry_price")}')
            print(f'   Target: ${sample.get("target_price")}')
            print(f'   Stop Loss: ${sample.get("stop_loss")}')
            print(f'   Confidence: {sample.get("confidence_score")}')
            print(f'   Created: {sample.get("created_at")}')
            
            # Check if prices are realistic
            entry_price = sample.get("entry_price", 0)
            if entry_price > 100:  # AAVE should be > $100 in 2021
                print("✅ Prices are realistic!")
            else:
                print("❌ Prices are still too low!")
        else:
            print("⚠️ No signals generated")
    else:
        print(f'❌ Error: {response.content.decode()}')


def test_data_quality():
    """Test the quality of market data"""
    print("\n🔍 Testing Data Quality...")
    
    # Check AAVEUSDT data
    aave_symbol = Symbol.objects.get(symbol='AAVEUSDT')
    
    # Check 2021 data
    from django.utils import timezone
    start_2021 = timezone.make_aware(datetime(2021, 1, 1))
    end_2021 = timezone.make_aware(datetime(2021, 12, 31))
    
    data_2021 = MarketData.objects.filter(
        symbol=aave_symbol,
        timestamp__gte=start_2021,
        timestamp__lte=end_2021
    ).order_by('timestamp')
    
    print(f'📊 AAVEUSDT 2021 records: {data_2021.count()}')
    
    if data_2021.exists():
        # Check price range
        prices = [float(d.close_price) for d in data_2021]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        print(f'💰 Price range: ${min_price:.2f} - ${max_price:.2f}')
        print(f'📈 Average price: ${avg_price:.2f}')
        
        # Check if prices are realistic for 2021
        if min_price > 100 and max_price < 1000:
            print("✅ Prices are realistic for AAVE in 2021!")
        else:
            print("❌ Prices are not realistic!")
        
        # Show sample data
        print(f'📊 Sample data points:')
        for i, data in enumerate(data_2021[:5]):
            print(f'   {data.timestamp.date()}: ${data.close_price}')


def test_signals_in_database():
    """Test signals in database"""
    print("\n📊 Testing Signals in Database...")
    
    # Check total signals
    total_signals = TradingSignal.objects.count()
    print(f'📈 Total signals in database: {total_signals}')
    
    # Check AAVEUSDT signals
    aave_signals = TradingSignal.objects.filter(symbol__symbol='AAVEUSDT')
    print(f'📊 AAVEUSDT signals: {aave_signals.count()}')
    
    if aave_signals.exists():
        sample_signal = aave_signals.first()
        print(f'📊 Sample signal:')
        print(f'   Symbol: {sample_signal.symbol.symbol}')
        print(f'   Type: {sample_signal.signal_type.name}')
        print(f'   Entry: ${sample_signal.entry_price}')
        print(f'   Target: ${sample_signal.target_price}')
        print(f'   Stop Loss: ${sample_signal.stop_loss}')
        print(f'   Confidence: {sample_signal.confidence_score}')
        print(f'   Created: {sample_signal.created_at}')
        
        # Check if prices are realistic
        entry_price = float(sample_signal.entry_price)
        if entry_price > 100:
            print("✅ Signal prices are realistic!")
        else:
            print("❌ Signal prices are still too low!")


def main():
    """Main function"""
    print("🧪 Backtesting Fix Test")
    print("=" * 50)
    
    # Test data quality
    test_data_quality()
    
    # Test signals in database
    test_signals_in_database()
    
    # Test API
    test_backtesting_api()
    
    print("\n🎉 Testing completed!")


if __name__ == '__main__':
    main()
