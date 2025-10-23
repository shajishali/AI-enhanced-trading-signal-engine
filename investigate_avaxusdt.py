#!/usr/bin/env python3
"""
Investigate AVAXUSDT MarketData issue
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.trading.models import Symbol
from apps.data.models import MarketData

def investigate_avaxusdt():
    """Investigate AVAXUSDT MarketData availability"""
    print("=" * 60)
    print("AVAXUSDT MARKETDATA INVESTIGATION")
    print("=" * 60)
    
    # Check if AVAXUSDT symbol exists
    avax_symbol = Symbol.objects.filter(symbol='AVAXUSDT').first()
    if not avax_symbol:
        print("❌ AVAXUSDT symbol not found in database!")
        return
    
    print(f"✅ AVAXUSDT symbol exists: {avax_symbol.symbol}")
    print(f"Symbol ID: {avax_symbol.id}")
    
    # Check MarketData for AVAXUSDT
    avax_data_count = MarketData.objects.filter(symbol=avax_symbol).count()
    print(f"MarketData records for AVAXUSDT: {avax_data_count}")
    
    if avax_data_count == 0:
        print("❌ No MarketData found for AVAXUSDT")
        
        # Check what symbols DO have MarketData
        print("\nSymbols WITH MarketData:")
        symbols_with_data = MarketData.objects.values_list('symbol__symbol', flat=True).distinct()[:10]
        for symbol_name in symbols_with_data:
            count = MarketData.objects.filter(symbol__symbol=symbol_name).count()
            print(f"  - {symbol_name}: {count} records")
    else:
        print("✅ AVAXUSDT MarketData found!")
        recent_data = MarketData.objects.filter(symbol=avax_symbol).order_by('-timestamp')[:3]
        for data in recent_data:
            print(f"  - ${data.close_price} at {data.timestamp}")
    
    # Check related symbols (AVAX vs AVAXUSDT)
    print(f"\nChecking related symbols:")
    avax_symbols = Symbol.objects.filter(symbol__startswith='AVAX')
    for symbol in avax_symbols:
        count = MarketData.objects.filter(symbol=symbol).count()
        print(f"  - {symbol.symbol}: {count} MarketData records")

if __name__ == "__main__":
    investigate_avaxusdt()












































