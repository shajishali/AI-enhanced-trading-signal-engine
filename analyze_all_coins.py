#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.models import MarketData
from apps.trading.models import Symbol
from django.db.models import Count

def analyze_all_coins_data():
    print("=== 🔍 COMPLETE COIN DATA ANALYSIS ===")
    print()
    
    # Get all symbols
    all_symbols = Symbol.objects.all().order_by('symbol')
    total_symbols = all_symbols.count()
    
    print(f"1. TOTAL SYMBOLS IN DATABASE: {total_symbols}")
    print()
    
    # Analyze data availability
    symbols_with_data = []
    symbols_without_data = []
    
    for symbol in all_symbols:
        data_count = MarketData.objects.filter(symbol=symbol).count()
        if data_count > 0:
            symbols_with_data.append((symbol, data_count))
        else:
            symbols_without_data.append(symbol)
    
    print(f"2. DATA AVAILABILITY SUMMARY:")
    print(f"   ✅ Symbols WITH data: {len(symbols_with_data)}")
    print(f"   ❌ Symbols WITHOUT data: {len(symbols_without_data)}")
    print()
    
    # Show symbols with data (grouped by record count)
    print("3. SYMBOLS WITH DATA (grouped by record count):")
    print("=" * 60)
    
    # Group by record count
    data_groups = {}
    for symbol, count in symbols_with_data:
        if count not in data_groups:
            data_groups[count] = []
        data_groups[count].append(symbol)
    
    # Sort by record count (descending)
    for count in sorted(data_groups.keys(), reverse=True):
        symbols = data_groups[count]
        print(f"\n📊 {count:,} records ({len(symbols)} symbols):")
        for symbol in symbols[:10]:  # Show first 10
            latest = MarketData.objects.filter(symbol=symbol).order_by('-timestamp').first()
            price_str = f"${float(latest.close_price):,.2f}" if latest else "N/A"
            print(f"   {symbol.symbol:12s} | {price_str}")
        
        if len(symbols) > 10:
            print(f"   ... and {len(symbols) - 10} more symbols")
    
    print("\n" + "=" * 60)
    
    # Show symbols without data
    print(f"\n4. SYMBOLS WITHOUT DATA ({len(symbols_without_data)} total):")
    print("=" * 50)
    
    # Group by symbol type (crypto vs others)
    crypto_no_data = []
    other_no_data = []
    
    for symbol in symbols_without_data:
        if symbol.symbol_type == 'CRYPTO':
            crypto_no_data.append(symbol)
        else:
            other_no_data.append(symbol)
    
    print(f"\n🪙 CRYPTO COINS WITHOUT DATA ({len(crypto_no_data)}):")
    for i, symbol in enumerate(crypto_no_data, 1):
        print(f"   {i:2d}. {symbol.symbol:12s} | {symbol.name}")
    
    if other_no_data:
        print(f"\n📈 OTHER SYMBOLS WITHOUT DATA ({len(other_no_data)}):")
        for i, symbol in enumerate(other_no_data, 1):
            print(f"   {i:2d}. {symbol.symbol:12s} | {symbol.name}")
    
    print()
    
    # Check for USDT pairs that might be missing
    print("5. MISSING USDT PAIRS ANALYSIS:")
    print("=" * 40)
    
    # Get all crypto symbols
    crypto_symbols = Symbol.objects.filter(symbol_type='CRYPTO').exclude(symbol__endswith='USDT')
    
    missing_usdt_pairs = []
    for symbol in crypto_symbols:
        usdt_symbol_name = f"{symbol.symbol}USDT"
        try:
            usdt_symbol = Symbol.objects.get(symbol=usdt_symbol_name)
            usdt_data_count = MarketData.objects.filter(symbol=usdt_symbol).count()
            if usdt_data_count == 0:
                missing_usdt_pairs.append((symbol.symbol, usdt_symbol_name))
        except Symbol.DoesNotExist:
            missing_usdt_pairs.append((symbol.symbol, usdt_symbol_name))
    
    if missing_usdt_pairs:
        print(f"Found {len(missing_usdt_pairs)} missing USDT pairs:")
        for base_symbol, usdt_symbol in missing_usdt_pairs[:20]:
            print(f"   {base_symbol:8s} → {usdt_symbol}")
        if len(missing_usdt_pairs) > 20:
            print(f"   ... and {len(missing_usdt_pairs) - 20} more")
    else:
        print("All USDT pairs have data!")
    
    print()
    
    # Check timeframes
    print("6. TIMEFRAME ANALYSIS:")
    print("=" * 30)
    timeframes = MarketData.objects.values_list('timeframe', flat=True).distinct()
    for tf in timeframes:
        count = MarketData.objects.filter(timeframe=tf).count()
        symbols_count = MarketData.objects.filter(timeframe=tf).values('symbol').distinct().count()
        print(f"   {tf:4s}: {count:6d} records | {symbols_count:3d} symbols")
    
    print()
    
    # Date range analysis
    print("7. DATE RANGE ANALYSIS:")
    print("=" * 30)
    earliest = MarketData.objects.order_by('timestamp').first()
    latest = MarketData.objects.order_by('-timestamp').first()
    if earliest and latest:
        print(f"   Earliest: {earliest.timestamp}")
        print(f"   Latest:   {latest.timestamp}")
        print(f"   Span:     {(latest.timestamp - earliest.timestamp).days} days")
        print(f"   Symbol:   {earliest.symbol.symbol}")
    
    print()
    
    # Recommendations
    print("8. RECOMMENDATIONS:")
    print("=" * 30)
    print("   📈 To populate missing coin data:")
    print("   1. Use: python manage.py populate_historical_data --symbol SYMBOL --timeframe 1h")
    print("   2. Use: python manage.py populate_historical_data --timeframe 1h (for all symbols)")
    print("   3. Check: apps/data/management/commands/populate_historical_data.py")
    print()
    
    if crypto_no_data:
        print("   🎯 Priority coins to populate:")
        for symbol in crypto_no_data[:10]:
            print(f"      - {symbol.symbol} ({symbol.name})")

if __name__ == "__main__":
    analyze_all_coins_data()
