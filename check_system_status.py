#!/usr/bin/env python3
"""
System Status Check for Signal Generation
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
from apps.trading.models import Symbol
from apps.data.models import MarketData
from datetime import datetime, timedelta

def check_system_status():
    print("=" * 80)
    print("AI TRADING ENGINE - SYSTEM STATUS CHECK")
    print("=" * 80)
    
    # 1. Check TradingSignal table status
    print("\n1. TRADINGSIGNAL STATUS:")
    total_signals = TradingSignal.objects.count()
    active_signals = TradingSignal.objects.filter(is_valid=True).count()
    recent_signals = TradingSignal.objects.filter(
        created_at__gte=datetime.now() - timedelta(hours=1)
    ).count()
    
    print(f"   Total signals in database: {total_signals}")
    print(f"   Active signals: {active_signals}")
    print(f"   Signals created in last hour: {recent_signals}")
    
    # 2. Check specific symbols
    print("\n2. SYMBOL STATUS:")
    test_symbols = ['AVAXUSDT', 'ADAUSDT', 'ETH', 'BTC']
    
    for symbol_name in test_symbols:
        try:
            symbol = Symbol.objects.get(symbol=symbol_name)
            signals_count = TradingSignal.objects.filter(symbol=symbol).count()
            active_count = TradingSignal.objects.filter(symbol=symbol, is_valid=True).count()
            
            # Check MarketData
            market_data_count = MarketData.objects.filter(symbol=symbol).count()
            
            print(f"   {symbol_name}:")
            print(f"     - Signals: {signals_count} (Active: {active_count})")
            print(f"     - MarketData: {market_data_count}")
            
            # Show most recent signals for this symbol
            recent_sigs = TradingSignal.objects.filter(symbol=symbol).order_by('-created_at')[:3]
            if recent_sigs:
                print(f"     Recent signals:")
                for sig in recent_sigs:
                    print(f"       ID:{sig.pk} {sig.signal_type.name} Entry:${sig.entry_price:.6f} TP:${sig.target_price:.6f} SL:${sig.stop_loss:.6f} Created:{sig.created_at.strftime('%H:%M:%S')}")
            
        except Symbol.DoesNotExist:
            print(f"   {symbol_name}: Symbol not found")
        
        except Exception as e:
            print(f"   {symbol_name}: Error - {e}")
    
    # 3. Check MarketData availability
    print("\n3. MARKETDATA AVAILABILITY:")
    symbols_with_data = Symbol.objects.filter(marketdata__isnull=False).distinct().count()
    symbols_with_signals = Symbol.objects.filter(tradingsignal__isnull=False).distinct().count()
    
    print(f"   Symbols with MarketData: {symbols_with_data}")
    print(f"   Symbols with signals: {symbols_with_signals}")
    
    # 4. Signal generation test (simulation)
    print("\n4. SIGNAL GENERATION TEST:")
    try:
        from apps.signals.services import SignalGenerationService
        
        service = SignalGenerationService()
        symbol = Symbol.objects.get(symbol='AVAXUSDT')
        
        print(f"   Testing signal generation for {symbol.symbol}...")
        
        # Test without creating actual signals
        print("   Service initialized successfully ✓")
        
        # Check if 30-minute strategy is working
        try:
            from apps.signals.thirty_minute_strategy import ThirtyMinuteStrategyService
            strategy_service = ThirtyMinuteStrategyService()
            print("   30-minute strategy service: ✓")
        except Exception as e:
            print(f"   30-minute strategy service: ✗ Error - {e}")
            
    except Exception as e:
        print(f"   Signal generation test failed: {e}")
    
    # 5. Overall system health
    print("\n5. SYSTEM HEALTH:")
    issues = []
    if total_signals == 0:
        issues.append("No signals in database")
    if active_signals == 0 and total_signals > 0:
        issues.append("No active signals")
    
    symbols_without_data = []
    for symbol_name in test_symbols:
        try:
            symbol = Symbol.objects.get(symbol=symbol_name)
            if MarketData.objects.filter(symbol=symbol).count() == 0:
                symbols_without_data.append(symbol_name)
        except:
            pass
    
    if symbols_without_data:
        issues.append(f"Symbols without MarketData: {', '.join(symbols_without_data)}")
    
    if issues:
        print("   ❌ ISSUES FOUND:")
        for issue in issues:
            print(f"     - {issue}")
    else:
        print("   ✅ System appears healthy")
    
    print("\n" + "=" * 80)
    print("STATUS CHECK COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    check_system_status()





















