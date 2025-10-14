#!/usr/bin/env python3
"""
Check for gaps between Signal symbols and MarketData symbols
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
from apps.signals.models import TradingSignal

def check_symbol_gaps():
    """Check for symbol data gaps"""
    print("=" * 60)
    print("SYMBOL DATA GAPS ANALYSIS")
    print("=" * 60)
    
    # Get symbols that have signals
    symbols_with_signals = set(TradingSignal.objects.values_list('symbol__symbol', flat=True).distinct())
    print(f"Symbols with Signals: {len(symbols_with_signals)}")
    
    # Get symbols that have MarketData
    symbols_with_data = set(MarketData.objects.values_list('symbol__symbol', flat=True).distinct())
    print(f"Symbols with MarketData: {len(symbols_with_data)}")
    
    # Find gaps
    signals_without_data = symbols_with_signals - symbols_with_data
    data_without_signals = symbols_with_data - symbols_with_signals
    
    print(f"\n❌ SYMBOLS WITH SIGNALS BUT NO MARKETDATA ({len(signals_without_data)}):")
    for symbol in sorted(signals_without_data)[:10]:
        signal_count = TradingSignal.objects.filter(symbol__symbol=symbol).count()
        print(f"  - {symbol}: {signal_count} signals, 0 MarketData")
    
    print(f"\n✅ SYMBOLS WITH MARKETDATA BUT NO SIGNALS ({len(data_without_signals)}):")
    for symbol in sorted(data_without_signals)[:10]:
        market_count = MarketData.objects.filter(symbol__symbol=symbol).count()
        print(f"  - {symbol}: 0 signals, {market_count} MarketData")
    
    # Check specific problematic pairs
    print(f"\n🔍 CHECKING SPECIFIC PAIRS:")
    problematic_pairs = [
        ('AVAX', 'AVAXUSDT'),
        ('ADA', 'ADAUSDT'), 
        ('AAVE', 'AAVEUSDT'),
        ('ETH', 'ETHUSDT'),
        ('BTC', 'BTCUSDT')
    ]
    
    for base, pair in problematic_pairs:
        base_signals = MarketData.objects.filter(symbol__symbol=base).count()
        pair_signals = MarketData.objects.filter(symbol__symbol=pair).count()
        pair_signals_generated = TradingSignal.objects.filter(symbol__symbol=pair).count()
        
        print(f"  {base}: {base_signals} MarketData")
        print(f"  {pair}: {pair_signals} MarketData, {pair_signals_generated} signals")
        if pair_signals == 0 and pair_signals_generated > 0:
            print(f"    ❌ PROBLEM: {pair} has signals but no MarketData!")

if __name__ == "__main__":
    check_symbol_gaps()





















