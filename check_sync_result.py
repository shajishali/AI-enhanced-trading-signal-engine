#!/usr/bin/env python3
"""
Check what the Sync Prices actually updated
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.models import TradingSignal
from apps.data.models import MarketData
from apps.trading.models import Symbol

def check_sync_result():
    """Check what the Sync Prices updated"""
    print("=" * 60)
    print("SYNC PRICES RESULTS CHECK")
    print("=" * 60)
    
    # Check MarketData
    print("\n1. MARKETDATA STATUS:")
    total_data = MarketData.objects.count()
    print(f"Total MarketData records: {total_data}")
    
    if total_data == 0:
        print("❌ MarketData is still empty!")
    else:
        print("✅ MarketData has records!")
        recent_data = MarketData.objects.order_by('-timestamp')[:3]
        for data in recent_data:
            print(f"  - {data.symbol.symbol}: ${data.close_price} at {data.timestamp}")
    
    # Check recent signals
    print("\n2. RECENT SIGNALS:")
    recent_signals = TradingSignal.objects.order_by('-updated_at')[:5]
    for signal in recent_signals:
        print(f"  - {signal.symbol.symbol}: Entry ${signal.entry_price}, Target ${signal.target_price}, SL ${signal.stop_loss}")
    
    # Check specific problematic symbols
    print("\n3. PROBLEMATIC SYMBOLS CHECK:")
    symbols_to_check = ['AVAXUSDT', 'AAVEUSDT', 'ADAUSDT']
    for symbol_name in symbols_to_check:
        symbol = Symbol.objects.filter(symbol=symbol_name).first()
        if symbol:
            market_data_count = MarketData.objects.filter(symbol=symbol).count()
            signals_count = TradingSignal.objects.filter(symbol=symbol).count()
            print(f"  {symbol_name}: {market_data_count} MarketData, {signals_count} Signals")

if __name__ == "__main__":
    check_sync_result()
