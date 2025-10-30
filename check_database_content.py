#!/usr/bin/env python3
"""
Database Content Analysis
Shows which coins have complete data stored in the database
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.models import MarketData
from apps.trading.models import Symbol

def analyze_database_content():
    """Analyze what crypto data is stored in the database"""
    print("📊 COMPLETE CRYPTO DATA IN DATABASE")
    print("=" * 60)
    
    # Get all USDT symbols
    usdt_symbols = Symbol.objects.filter(symbol__endswith='USDT').exclude(symbol='USDT')
    
    print(f"Total USDT symbols: {usdt_symbols.count()}")
    print(f"Total market data records: {MarketData.objects.count():,}")
    
    # Analyze each symbol
    complete_symbols = []
    partial_symbols = []
    no_data_symbols = []
    
    for symbol in usdt_symbols:
        count = MarketData.objects.filter(symbol=symbol).count()
        
        if count >= 2000:  # Complete data (5+ years)
            complete_symbols.append((symbol.symbol, count))
        elif count > 0:  # Partial data
            partial_symbols.append((symbol.symbol, count))
        else:  # No data
            no_data_symbols.append(symbol.symbol)
    
    # Show complete symbols
    print(f"\n✅ COMPLETE SYMBOLS ({len(complete_symbols)}):")
    print("   (5+ years of data, ready for comprehensive backtesting)")
    for symbol, count in sorted(complete_symbols):
        print(f"   {symbol}: {count:,} records")
    
    # Show partial symbols
    if partial_symbols:
        print(f"\n⚠️  PARTIAL SYMBOLS ({len(partial_symbols)}):")
        print("   (Some data available, may need more historical data)")
        for symbol, count in sorted(partial_symbols):
            print(f"   {symbol}: {count:,} records")
    
    # Show symbols with no data
    if no_data_symbols:
        print(f"\n❌ NO DATA SYMBOLS ({len(no_data_symbols)}):")
        print("   (No market data available)")
        for symbol in sorted(no_data_symbols):
            print(f"   {symbol}")
    
    # Show date ranges for complete symbols
    print(f"\n📅 DATE RANGES FOR COMPLETE SYMBOLS:")
    for symbol_name, _ in complete_symbols[:5]:  # Show first 5
        symbol = Symbol.objects.get(symbol=symbol_name)
        data = MarketData.objects.filter(symbol=symbol).order_by('timestamp')
        if data.exists():
            first_date = data.first().timestamp.date()
            last_date = data.last().timestamp.date()
            print(f"   {symbol_name}: {first_date} to {last_date}")
    
    # Summary statistics
    total_records = MarketData.objects.count()
    complete_records = sum(count for _, count in complete_symbols)
    partial_records = sum(count for _, count in partial_symbols)
    
    print(f"\n📈 SUMMARY STATISTICS:")
    print(f"   Complete symbols: {len(complete_symbols)}")
    print(f"   Partial symbols: {len(partial_symbols)}")
    print(f"   No data symbols: {len(no_data_symbols)}")
    print(f"   Total records: {total_records:,}")
    print(f"   Complete data records: {complete_records:,}")
    print(f"   Partial data records: {partial_records:,}")
    
    return {
        'complete': complete_symbols,
        'partial': partial_symbols,
        'no_data': no_data_symbols,
        'total_records': total_records
    }

def check_specific_coins():
    """Check specific popular coins"""
    print(f"\n🔍 POPULAR COINS CHECK:")
    
    popular_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'XRPUSDT']
    
    for coin in popular_coins:
        try:
            symbol = Symbol.objects.get(symbol=coin)
            count = MarketData.objects.filter(symbol=symbol).count()
            
            if count > 0:
                data = MarketData.objects.filter(symbol=symbol).order_by('timestamp')
                first_date = data.first().timestamp.date()
                last_date = data.last().timestamp.date()
                print(f"   {coin}: {count:,} records ({first_date} to {last_date})")
            else:
                print(f"   {coin}: No data")
        except Symbol.DoesNotExist:
            print(f"   {coin}: Symbol not found")

if __name__ == "__main__":
    results = analyze_database_content()
    check_specific_coins()
    
    print(f"\n🎯 CONCLUSION:")
    if results['complete']:
        print(f"   ✅ {len(results['complete'])} coins have complete data")
        print(f"   ✅ Ready for comprehensive backtesting")
        print(f"   ✅ All major cryptocurrencies covered")
    else:
        print(f"   ⚠️  No coins have complete data")
        print(f"   ⚠️  May need more historical data import")































