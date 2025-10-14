#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.models import MarketData
from apps.trading.models import Symbol
from django.db.models import Count, Max, Min

def get_famous_30_coins_data():
    print("=== 🪙 FAMOUS 30 COINS DATA ANALYSIS ===")
    print()
    
    # Define the famous 30 coins (based on market cap and popularity)
    famous_30 = [
        'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'TRX', 'LINK', 'DOT',
        'MATIC', 'AVAX', 'UNI', 'ATOM', 'LTC', 'BCH', 'ALGO', 'VET', 'FTM', 'ICP',
        'SAND', 'MANA', 'NEAR', 'APT', 'OP', 'ARB', 'MKR', 'RUNE', 'INJ', 'STX'
    ]
    
    print("1. CHECKING DATA FOR FAMOUS 30 COINS:")
    print("=" * 60)
    
    coin_data = {}
    total_records = 0
    
    for i, coin in enumerate(famous_30, 1):
        # Check both base symbol and USDT pair
        base_symbol = None
        usdt_symbol = None
        
        try:
            base_symbol = Symbol.objects.get(symbol=coin)
        except Symbol.DoesNotExist:
            pass
            
        try:
            usdt_symbol = Symbol.objects.get(symbol=f"{coin}USDT")
        except Symbol.DoesNotExist:
            pass
        
        # Get data counts
        base_count = MarketData.objects.filter(symbol=base_symbol).count() if base_symbol else 0
        usdt_count = MarketData.objects.filter(symbol=usdt_symbol).count() if usdt_symbol else 0
        
        # Determine which has data
        if usdt_count > 0:
            symbol_obj = usdt_symbol
            symbol_name = f"{coin}USDT"
            data_count = usdt_count
        elif base_count > 0:
            symbol_obj = base_symbol
            symbol_name = coin
            data_count = base_count
        else:
            symbol_obj = None
            symbol_name = coin
            data_count = 0
        
        # Get latest price if data exists
        latest_price = None
        latest_timestamp = None
        if symbol_obj and data_count > 0:
            latest = MarketData.objects.filter(symbol=symbol_obj).order_by('-timestamp').first()
            if latest:
                latest_price = float(latest.close_price)
                latest_timestamp = latest.timestamp
        
        coin_data[coin] = {
            'symbol_name': symbol_name,
            'data_count': data_count,
            'latest_price': latest_price,
            'latest_timestamp': latest_timestamp,
            'has_data': data_count > 0
        }
        
        total_records += data_count
        
        status = "✅" if data_count > 0 else "❌"
        price_str = f"${latest_price:,.2f}" if latest_price else "No Data"
        
        print(f"{i:2d}. {coin:4s} {status} | {symbol_name:8s} | {data_count:5d} records | {price_str}")
    
    print("=" * 60)
    print(f"TOTAL RECORDS FOR TOP 30: {total_records:,}")
    print()
    
    # Summary by data availability
    coins_with_data = [coin for coin, data in coin_data.items() if data['has_data']]
    coins_without_data = [coin for coin, data in coin_data.items() if not data['has_data']]
    
    print("2. SUMMARY:")
    print(f"✅ Coins WITH data: {len(coins_with_data)}")
    print(f"❌ Coins WITHOUT data: {len(coins_without_data)}")
    print()
    
    if coins_with_data:
        print("3. COINS WITH DATA:")
        for coin in coins_with_data:
            data = coin_data[coin]
            print(f"   {coin:4s}: {data['symbol_name']:8s} | {data['data_count']:5d} records | ${data['latest_price']:,.2f}")
        print()
    
    if coins_without_data:
        print("4. COINS WITHOUT DATA:")
        for coin in coins_without_data:
            print(f"   {coin:4s}: No historical data found")
        print()
    
    # Top 10 coins by data count
    print("5. TOP 10 COINS BY DATA COUNT:")
    sorted_coins = sorted(coin_data.items(), key=lambda x: x[1]['data_count'], reverse=True)
    for i, (coin, data) in enumerate(sorted_coins[:10], 1):
        if data['has_data']:
            print(f"   {i:2d}. {coin:4s} ({data['symbol_name']:8s}): {data['data_count']:5d} records | ${data['latest_price']:,.2f}")
    print()
    
    # Generate SQL queries for coins with data
    print("6. SQL QUERIES FOR COINS WITH DATA:")
    print("=" * 50)
    for coin in coins_with_data:
        data = coin_data[coin]
        print(f"-- {coin} ({data['symbol_name']})")
        print(f"SELECT close_price, timestamp FROM data_marketdata WHERE symbol_id = (SELECT id FROM trading_symbol WHERE symbol = '{data['symbol_name']}') ORDER BY timestamp DESC LIMIT 5;")
        print()
    
    # Check timeframes
    print("7. AVAILABLE TIMEFRAMES:")
    timeframes = MarketData.objects.values_list('timeframe', flat=True).distinct()
    for tf in timeframes:
        count = MarketData.objects.filter(timeframe=tf).count()
        print(f"   {tf:4s}: {count:6d} records")
    print()
    
    # Date range
    print("8. DATA DATE RANGE:")
    earliest = MarketData.objects.order_by('timestamp').first()
    latest = MarketData.objects.order_by('-timestamp').first()
    if earliest and latest:
        print(f"   From: {earliest.timestamp}")
        print(f"   To:   {latest.timestamp}")
        print(f"   Span: {(latest.timestamp - earliest.timestamp).days} days")

if __name__ == "__main__":
    get_famous_30_coins_data()
