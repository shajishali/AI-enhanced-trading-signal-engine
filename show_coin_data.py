#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.models import MarketData
from apps.trading.models import Symbol

def show_coin_data():
    print("=== 🪙 YOUR AI TRADING ENGINE - COIN DATA ===")
    print(f"Total Symbols: {Symbol.objects.count()}")
    print(f"Total Market Data Records: {MarketData.objects.count()}")
    
    print("\n=== 🚀 CRYPTO SYMBOLS ===")
    crypto = Symbol.objects.filter(symbol_type='CRYPTO')
    print(f"Crypto Coins: {crypto.count()}")
    for s in crypto[:20]:
        print(f"  {s.symbol:6} - {s.name}")
    
    print("\n=== 📈 STOCK SYMBOLS ===")
    stocks = Symbol.objects.filter(symbol_type='STOCK')
    print(f"Stocks: {stocks.count()}")
    for s in stocks:
        print(f"  {s.symbol:6} - {s.name}")
    
    print("\n=== 💰 LATEST MARKET DATA (Top 20) ===")
    print(f"{'Symbol':<6} | {'Close Price':<12} | {'Volume':<15} | {'Timestamp'}")
    print("-" * 60)
    
    data = MarketData.objects.select_related('symbol').order_by('-timestamp')[:20]
    for d in data:
        try:
            print(f"{d.symbol.symbol:<6} | ${d.close_price:<11.2f} | {d.volume:<14,.0f} | {d.timestamp.strftime('%Y-%m-%d %H:%M')}")
        except:
            print(f"{d.symbol.symbol:<6} | {'N/A':<11} | {'N/A':<14} | {d.timestamp.strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    show_coin_data()
