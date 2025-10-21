#!/usr/bin/env python3
"""
Signal Data Fix Script
Regenerates all trading signals using the corrected market data
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.models import TradingSignal
from apps.trading.models import Symbol
from apps.data.models import MarketData

def fix_signal_data():
    """Fix signal data by regenerating signals with correct market data"""
    print("🔧 SIGNAL DATA FIX SCRIPT")
    print("=" * 50)
    
    # Get all USDT symbols
    usdt_symbols = Symbol.objects.filter(symbol__endswith='USDT').exclude(symbol='USDT')
    
    total_signals_fixed = 0
    total_signals_deleted = 0
    
    for symbol in usdt_symbols:
        print(f"\n📊 Processing {symbol.symbol}...")
        
        # Count existing signals
        existing_signals = TradingSignal.objects.filter(symbol=symbol).count()
        print(f"  Existing signals: {existing_signals}")
        
        if existing_signals > 0:
            # Delete all existing signals for this symbol
            deleted_count, _ = TradingSignal.objects.filter(symbol=symbol).delete()
            total_signals_deleted += deleted_count
            print(f"  Deleted {deleted_count} old signals")
        
        # Check if we have market data for this symbol
        market_data_count = MarketData.objects.filter(symbol=symbol).count()
        print(f"  Market data records: {market_data_count}")
        
        if market_data_count > 0:
            print(f"  ✅ {symbol.symbol} ready for signal regeneration")
        else:
            print(f"  ❌ No market data for {symbol.symbol}")
    
    print(f"\n📈 SUMMARY:")
    print(f"  Signals deleted: {total_signals_deleted}")
    print(f"  Symbols processed: {usdt_symbols.count()}")
    
    print(f"\n✅ NEXT STEPS:")
    print(f"  1. Run signal generation to create new signals with correct data")
    print(f"  2. Run backtesting to verify accuracy")
    print(f"  3. All signals will now use the corrected market data")
    
    return total_signals_deleted

def verify_signal_fix():
    """Verify that signals are fixed"""
    print(f"\n🔍 VERIFICATION:")
    
    # Check BTC signal for October 31, 2021
    btc = Symbol.objects.get(symbol='BTCUSDT')
    signals = TradingSignal.objects.filter(symbol=btc, created_at__date=datetime(2021,10,31).date())
    
    if signals.count() == 0:
        print(f"  ✅ No incorrect signals found for BTC on 2021-10-31")
        print(f"  ✅ Ready for fresh signal generation")
    else:
        print(f"  ⚠️  Still {signals.count()} signals found - may need manual cleanup")
    
    return signals.count() == 0

if __name__ == "__main__":
    print("⚠️  WARNING: This will delete ALL existing trading signals!")
    print("⚠️  Make sure you have backups if needed!")
    
    confirm = input("\nProceed with signal cleanup? (yes/no): ")
    
    if confirm.lower() == 'yes':
        deleted_count = fix_signal_data()
        success = verify_signal_fix()
        
        if success:
            print(f"\n🎉 SIGNAL CLEANUP COMPLETED!")
            print(f"   Deleted {deleted_count} incorrect signals")
            print(f"   Ready for fresh signal generation with correct data")
        else:
            print(f"\n⚠️  Cleanup may not be complete")
    else:
        print("Cleanup cancelled")












