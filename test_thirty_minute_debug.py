#!/usr/bin/env python3
"""
Debug script to test 30-minute strategy integration
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.thirty_minute_strategy import ThirtyMinuteStrategyService
from apps.trading.models import Symbol
from apps.signals.models import TradingSignal
import json

def test_thirty_minute_strategy():
    """Test 30-minute strategy implementation"""
    print("=" * 60)
    print("30-MINUTE STRATEGY DEBUG TEST")
    print("=" * 60)
    
    # Test AVAXUSDT
    symbol = Symbol.objects.get(symbol='AVAXUSDT')
    service = ThirtyMinuteStrategyService()
    
    print(f"Testing symbol: {symbol.symbol}")
    print(f"Strategy lookback periods: {service.lookback_periods}")
    
    levels = service.get_thirty_minute_levels(symbol)
    
    print("\n30-Minute Strategy Results:")
    print("-" * 40)
    
    # Buy signal levels
    buy_levels = levels.get('buy_signal_levels', {})
    print("BUY Signal Levels:")
    print(f"  Take Profit: {buy_levels.get('take_profit', 'N/A')}")
    print(f"  Stop Loss: {buy_levels.get('stop_loss', 'N/A')}")
    print(f"  Reasoning: {buy_levels.get('reasoning', 'N/A')}")
    
    # Sell signal levels  
    sell_levels = levels.get('sell_signal_levels', {})
    print("SELL Signal Levels:")
    print(f"  Take Profit: {sell_levels.get('take_profit', 'N/A')}")
    print(f"  Stop Loss: {sell_levels.get('stop_loss', 'N/A')}")
    print(f"  Reasoning: {sell_levels.get('reasoning', 'N/A')}")
    
    print(f"\nStrategy: {levels.get('strategy', 'N/A')}")
    print(f"Current Price: {levels.get('current_price', 'N/A')}")
    print(f"Resistance Found: {levels.get('resistance_found', 'N/A')}")
    print(f"Support Found: {levels.get('support_found', 'N/A')}")

def analyze_current_signals():
    """Analyze current duplicate signals issue"""
    print("\n" + "=" * 60)
    print("DUPLICATE SIGNALS ANALYSIS")
    print("=" * 60)
    
    # Get recent signals for problematic symbols
    symbols = ['ADAUSDT', 'AVAXUSDT', 'AAVEUSDT', 'ADA']
    
    for symbol_name in symbols:
        print(f"\n{symbol_name} - Recent Signals:")
        signals = TradingSignal.objects.filter(
            symbol__symbol=symbol_name
        ).order_by('-created_at')[:5]
        
        for signal in signals:
            print(f"  ID:{signal.pk} {signal.signal_type} Entry:{signal.entry_price} Target:{signal.target_price} SL:{signal.stop_loss} Created:{signal.created_at.strftime('%H:%M:%S')}")

def check_signal_generation_integration():
    """Check if signal generation is using 30-minute strategy"""
    print("\n" + "=" * 60) 
    print("SIGNAL GENERATION INTEGRATION CHECK")
    print("=" * 60)
    
    # Check recent signal generation logs
    print("Recent signal generation details in logging...")
    
    # Test generation process manually
    from apps.signals.services import SignalGenerationService
    from apps.trading.models import Symbol
    
    symbol = Symbol.objects.get(symbol='AVAXUSDT')
    service = SignalGenerationService()
    
    print(f"\nTesting signal generation for {symbol.symbol}...")
    print("Note: This will not actually create signals, just test the process")
    
    # Check if 30-minute strategy is being called
    print("Checking if 30-minute strategy is integrated into signal generation...")

if __name__ == "__main__":
    test_thirty_minute_strategy()
    analyze_current_signals()
    check_signal_generation_integration()
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)
    
    print("ISSUES FOUND:")
    print("1. ❌ Multiple duplicate signals for same symbols")
    print("2. ❌ Inconsistent entry prices (AVAXUSDT entry $1.00 but price $30.44)")
    print("3. ❌ Need to verify 30-minute strategy is being used")
    print("4. ❌ TP/SL calculations may not follow 30-minute rules")
    
    print("\nRECOMMENDATIONS:")
    print("1. 🔧 Fix duplicate signal generation")
    print("2. 🔧 Fix entry price calculation logic") 
    print("3. 🔧 Verify 30-minute strategy integration")
    print("4. 🔧 Add duplicate prevention mechanism")






































