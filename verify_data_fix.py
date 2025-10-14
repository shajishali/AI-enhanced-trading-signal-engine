#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.models import MarketData
from apps.trading.models import Symbol
from datetime import datetime, timezone

def verify_complete_data():
    print("=== ✅ DATA FIX VERIFICATION ===")
    print()
    
    # Test cases to verify
    test_cases = [
        {
            'symbol': 'BTC',
            'date': '2023-01-04',
            'time': '04:00:00',
            'description': 'BTC Price on January 4th, 2023 at 4 AM'
        },
        {
            'symbol': 'DOT',
            'date': '2021-01-01',
            'time': '08:00:00',
            'description': 'DOT Price on January 1st, 2021 at 8 AM (TradingView comparison)'
        },
        {
            'symbol': 'ETH',
            'date': '2021-01-01',
            'time': '00:00:00',
            'description': 'ETH Price on January 1st, 2021 at midnight'
        }
    ]
    
    print("1. SPECIFIC PRICE VERIFICATION:")
    print("=" * 50)
    
    for test in test_cases:
        try:
            symbol_obj = Symbol.objects.get(symbol=test['symbol'])
            target_time = f"{test['date']} {test['time']}"
            
            data = MarketData.objects.filter(
                symbol=symbol_obj,
                timestamp=target_time,
                timeframe='1h'
            ).first()
            
            if data:
                print(f"✅ {test['description']}")
                print(f"   Symbol: {test['symbol']}")
                print(f"   Time: {target_time}")
                print(f"   Price: ${data.close_price}")
                print(f"   OHLC: O=${data.open_price} H=${data.high_price} L=${data.low_price} C=${data.close_price}")
            else:
                print(f"❌ {test['description']} - No data found")
            print()
            
        except Symbol.DoesNotExist:
            print(f"❌ {test['symbol']} symbol not found")
            print()
    
    print("2. 24-HOUR RECORDS VERIFICATION:")
    print("=" * 40)
    
    # Check 24-hour completeness for specific dates
    test_dates = [
        ('BTC', '2023-01-04'),
        ('DOT', '2021-01-01'),
        ('ETH', '2021-01-01')
    ]
    
    for symbol_name, test_date in test_dates:
        try:
            symbol_obj = Symbol.objects.get(symbol=symbol_name)
            count = MarketData.objects.filter(
                symbol=symbol_obj,
                timestamp__date=test_date,
                timeframe='1h'
            ).count()
            
            status = "✅" if count == 24 else "❌"
            print(f"{status} {symbol_name} on {test_date}: {count}/24 records")
            
        except Symbol.DoesNotExist:
            print(f"❌ {symbol_name} symbol not found")
    
    print()
    
    print("3. TOTAL DATA SUMMARY:")
    print("=" * 30)
    
    # Get updated counts
    total_symbols = Symbol.objects.count()
    symbols_with_data = MarketData.objects.values('symbol').distinct().count()
    total_records = MarketData.objects.count()
    
    print(f"📊 Total symbols in database: {total_symbols}")
    print(f"📈 Symbols with data: {symbols_with_data}")
    print(f"📋 Total market data records: {total_records:,}")
    
    # Top coins by record count
    print(f"\n🏆 TOP COINS BY RECORD COUNT:")
    from django.db.models import Count
    top_coins = MarketData.objects.values('symbol__symbol').annotate(
        record_count=Count('id')
    ).order_by('-record_count')[:10]
    
    for coin in top_coins:
        symbol_name = coin['symbol__symbol']
        count = coin['record_count']
        print(f"   {symbol_name:8s}: {count:6,} records")
    
    print()
    
    print("4. DATA SOURCE INFORMATION:")
    print("=" * 35)
    print("🔗 Data Source: Binance API (https://api.binance.com/api/v3/klines)")
    print("📅 Date Range: 2020-01-01 to 2025-10-14")
    print("⏰ Timeframe: 1h (hourly data)")
    print("🔄 Update Method: Historical data population commands")
    print("📊 Data Format: OHLCV (Open, High, Low, Close, Volume)")
    print()
    
    print("5. VERIFICATION QUERIES:")
    print("=" * 30)
    print("You can now run these SQL queries to verify:")
    print()
    print("-- BTC price on Jan 4, 2023 at 4 AM")
    print("SELECT close_price FROM data_marketdata WHERE symbol_id = (SELECT id FROM trading_symbol WHERE symbol = 'BTC') AND timestamp = '2023-01-04 04:00:00' AND timeframe = '1h';")
    print()
    print("-- DOT price on Jan 1, 2021 at 8 AM")
    print("SELECT close_price FROM data_marketdata WHERE symbol_id = (SELECT id FROM trading_symbol WHERE symbol = 'DOT') AND timestamp = '2021-01-01 08:00:00' AND timeframe = '1h';")
    print()
    print("-- Check 24-hour completeness for any date")
    print("SELECT COUNT(*) FROM data_marketdata WHERE symbol_id = (SELECT id FROM trading_symbol WHERE symbol = 'BTC') AND timestamp LIKE '2023-01-04%' AND timeframe = '1h';")
    print("-- Should return 24")

if __name__ == "__main__":
    verify_complete_data()
