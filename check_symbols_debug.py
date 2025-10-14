#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.models import MarketData
from apps.trading.models import Symbol

def debug_database():
    print("=== DATABASE DEBUG ANALYSIS ===")
    print()
    
    # Check total symbols
    total_symbols = Symbol.objects.count()
    print(f"1. Total symbols in database: {total_symbols}")
    
    # Check total market data
    total_market_data = MarketData.objects.count()
    print(f"2. Total market data records: {total_market_data}")
    print()
    
    # List all available symbols
    print("3. Available symbols:")
    symbols = Symbol.objects.all().order_by('symbol')
    for i, symbol in enumerate(symbols[:30], 1):
        print(f"   {i:2d}. ID: {symbol.id:3d} | Symbol: {symbol.symbol:8s} | Name: {symbol.name}")
    
    if total_symbols > 30:
        print(f"   ... and {total_symbols - 30} more symbols")
    print()
    
    # Check specific symbols we're looking for
    target_symbols = ['ADA', 'ETH', 'BTC', 'XRP', 'SOL']
    print("4. Checking specific symbols:")
    for symbol_name in target_symbols:
        try:
            symbol = Symbol.objects.get(symbol=symbol_name)
            data_count = MarketData.objects.filter(symbol=symbol).count()
            print(f"   {symbol_name:4s}: Found | ID: {symbol.id:3d} | Records: {data_count:6d}")
            
            if data_count > 0:
                latest = MarketData.objects.filter(symbol=symbol).order_by('-timestamp').first()
                earliest = MarketData.objects.filter(symbol=symbol).order_by('timestamp').first()
                print(f"         Latest: ${latest.close_price:8.2f} at {latest.timestamp}")
                print(f"         Range:  {earliest.timestamp} to {latest.timestamp}")
        except Symbol.DoesNotExist:
            print(f"   {symbol_name:4s}: NOT FOUND")
        print()
    
    # Check which symbols have the most data
    print("5. Top 10 symbols by data count:")
    from django.db.models import Count
    symbol_counts = Symbol.objects.annotate(
        data_count=Count('marketdata')
    ).order_by('-data_count')[:10]
    
    for symbol in symbol_counts:
        print(f"   {symbol.symbol:8s}: {symbol.data_count:6d} records")
    print()
    
    # Check data timeframes
    print("6. Available timeframes:")
    timeframes = MarketData.objects.values_list('timeframe', flat=True).distinct()
    for tf in timeframes:
        count = MarketData.objects.filter(timeframe=tf).count()
        print(f"   {tf:4s}: {count:6d} records")
    print()
    
    # Check date ranges
    print("7. Date range analysis:")
    earliest = MarketData.objects.order_by('timestamp').first()
    latest = MarketData.objects.order_by('-timestamp').first()
    if earliest and latest:
        print(f"   Earliest data: {earliest.timestamp}")
        print(f"   Latest data:   {latest.timestamp}")
        print(f"   Symbol:        {earliest.symbol.symbol}")
    print()
    
    # Check if there are any ADA/ETH related symbols
    print("8. Searching for ADA/ETH related symbols:")
    ada_symbols = Symbol.objects.filter(symbol__icontains='ADA')
    eth_symbols = Symbol.objects.filter(symbol__icontains='ETH')
    
    print(f"   ADA-related: {ada_symbols.count()} symbols")
    for symbol in ada_symbols:
        data_count = MarketData.objects.filter(symbol=symbol).count()
        print(f"     {symbol.symbol:10s}: {data_count:6d} records")
    
    print(f"   ETH-related: {eth_symbols.count()} symbols")
    for symbol in eth_symbols:
        data_count = MarketData.objects.filter(symbol=symbol).count()
        print(f"     {symbol.symbol:10s}: {data_count:6d} records")

if __name__ == "__main__":
    debug_database()
