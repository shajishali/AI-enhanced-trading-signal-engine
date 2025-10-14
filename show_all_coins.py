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

def show_all_coins_in_database():
    print("=== 🪙 ALL COINS IN YOUR DATABASE ===")
    print()
    
    # Get all symbols
    all_symbols = Symbol.objects.all().order_by('symbol')
    total_symbols = all_symbols.count()
    
    print(f"📊 TOTAL SYMBOLS: {total_symbols}")
    print()
    
    # Separate crypto and other symbols
    crypto_symbols = Symbol.objects.filter(symbol_type='CRYPTO').order_by('symbol')
    other_symbols = Symbol.objects.exclude(symbol_type='CRYPTO').order_by('symbol')
    
    print(f"🪙 CRYPTO COINS: {crypto_symbols.count()}")
    print(f"📈 OTHER SYMBOLS: {other_symbols.count()}")
    print()
    
    # Show crypto coins with data status
    print("1. CRYPTO COINS WITH DATA:")
    print("=" * 50)
    
    crypto_with_data = []
    crypto_without_data = []
    
    for symbol in crypto_symbols:
        data_count = MarketData.objects.filter(symbol=symbol).count()
        if data_count > 0:
            latest = MarketData.objects.filter(symbol=symbol).order_by('-timestamp').first()
            price_str = f"${float(latest.close_price):,.2f}" if latest else "N/A"
            crypto_with_data.append((symbol, data_count, price_str))
        else:
            crypto_without_data.append(symbol)
    
    print(f"✅ CRYPTO COINS WITH DATA ({len(crypto_with_data)}):")
    for i, (symbol, count, price) in enumerate(crypto_with_data, 1):
        print(f"   {i:2d}. {symbol.symbol:12s} | {count:5d} records | {price}")
    
    print(f"\n❌ CRYPTO COINS WITHOUT DATA ({len(crypto_without_data)}):")
    for i, symbol in enumerate(crypto_without_data, 1):
        print(f"   {i:2d}. {symbol.symbol:12s} | {symbol.name}")
    
    print()
    
    # Show other symbols
    print("2. OTHER SYMBOLS (STOCKS, ETC.):")
    print("=" * 40)
    for i, symbol in enumerate(other_symbols, 1):
        data_count = MarketData.objects.filter(symbol=symbol).count()
        status = "✅" if data_count > 0 else "❌"
        print(f"   {i:2d}. {symbol.symbol:12s} | {symbol.name:30s} | {status}")
    
    print()
    
    # Summary by data count
    print("3. DATA SUMMARY:")
    print("=" * 30)
    
    # Group by record count
    data_groups = {}
    for symbol in all_symbols:
        count = MarketData.objects.filter(symbol=symbol).count()
        if count > 0:
            if count not in data_groups:
                data_groups[count] = []
            data_groups[count].append(symbol)
    
    print("📊 Records per symbol:")
    for count in sorted(data_groups.keys(), reverse=True):
        symbols = data_groups[count]
        print(f"   {count:5d} records: {len(symbols):3d} symbols")
    
    print()
    
    # Top 20 coins by market cap (if they exist)
    print("4. TOP COINS BY DATA COUNT:")
    print("=" * 40)
    
    symbols_with_data_sorted = sorted(crypto_with_data, key=lambda x: x[1], reverse=True)
    for i, (symbol, count, price) in enumerate(symbols_with_data_sorted[:20], 1):
        print(f"   {i:2d}. {symbol.symbol:12s} | {count:5d} records | {price}")
    
    print()
    
    # Missing popular coins
    print("5. POPULAR COINS MISSING DATA:")
    print("=" * 40)
    
    popular_missing = []
    popular_coins = ['SAND', 'MANA', 'NEAR', 'APT', 'OP', 'ARB', 'MKR', 'RUNE', 'INJ', 'STX', 
                     'USDC', 'WBTC', 'SHIB', 'TON', 'SUI', 'PEPE', 'FLOKI', 'BONK', 'WIF', 'UNI']
    
    for coin in popular_coins:
        try:
            symbol = Symbol.objects.get(symbol=coin)
            data_count = MarketData.objects.filter(symbol=symbol).count()
            if data_count == 0:
                popular_missing.append(coin)
        except Symbol.DoesNotExist:
            popular_missing.append(f"{coin} (not in DB)")
    
    for i, coin in enumerate(popular_missing, 1):
        print(f"   {i:2d}. {coin}")
    
    print()
    
    # Available timeframes
    print("6. AVAILABLE TIMEFRAMES:")
    print("=" * 30)
    timeframes = MarketData.objects.values_list('timeframe', flat=True).distinct()
    for tf in timeframes:
        count = MarketData.objects.filter(timeframe=tf).count()
        symbols_count = MarketData.objects.filter(timeframe=tf).values('symbol').distinct().count()
        print(f"   {tf:4s}: {count:6d} records | {symbols_count:3d} symbols")
    
    print()
    
    # Date range
    print("7. DATA DATE RANGE:")
    print("=" * 25)
    earliest = MarketData.objects.order_by('timestamp').first()
    latest = MarketData.objects.order_by('-timestamp').first()
    if earliest and latest:
        print(f"   From: {earliest.timestamp}")
        print(f"   To:   {latest.timestamp}")
        print(f"   Span: {(latest.timestamp - earliest.timestamp).days} days")
        print(f"   Symbol: {earliest.symbol.symbol}")

if __name__ == "__main__":
    show_all_coins_in_database()
