#!/usr/bin/env python3
"""
Backtesting Verification Script
Verifies that the corrected signal will work properly in backtesting
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.models import TradingSignal
from apps.trading.models import Symbol
from apps.data.models import MarketData

def verify_backtesting_signal():
    """Verify the signal will work correctly in backtesting"""
    print("🔍 BACKTESTING VERIFICATION")
    print("=" * 40)
    
    # Get the signal
    btc = Symbol.objects.get(symbol='BTCUSDT')
    signal = TradingSignal.objects.filter(
        symbol=btc, 
        created_at__date=datetime(2021,10,31).date()
    ).first()
    
    if not signal:
        print("❌ No signal found")
        return False
    
    print(f"📊 Signal Details:")
    print(f"   Entry Price: ${signal.entry_price}")
    print(f"   Target Price: ${signal.target_price}")
    print(f"   Stop Loss: ${signal.stop_loss}")
    print(f"   Signal Date: {signal.created_at.date()}")
    
    # Get market data for the signal date
    market_data = MarketData.objects.filter(
        symbol=btc,
        timestamp__date=datetime(2021,10,31).date()
    ).first()
    
    if not market_data:
        print("❌ No market data found for signal date")
        return False
    
    print(f"\n📈 Market Data:")
    print(f"   Open: ${market_data.open_price}")
    print(f"   High: ${market_data.high_price}")
    print(f"   Low: ${market_data.low_price}")
    print(f"   Close: ${market_data.close_price}")
    
    # Verify signal execution
    entry_price = float(signal.entry_price)
    target_price = float(signal.target_price)
    stop_loss = float(signal.stop_loss)
    
    day_low = float(market_data.low_price)
    day_high = float(market_data.high_price)
    day_close = float(market_data.close_price)
    
    print(f"\n🎯 Execution Analysis:")
    
    # Check if entry is possible
    if day_low <= entry_price <= day_high:
        print(f"   ✅ Entry at ${entry_price:,.2f} is POSSIBLE")
        print(f"      (Day range: ${day_low:,.2f} - ${day_high:,.2f})")
    else:
        print(f"   ❌ Entry at ${entry_price:,.2f} is IMPOSSIBLE")
        print(f"      (Day range: ${day_low:,.2f} - ${day_high:,.2f})")
        return False
    
    # Check if target is hit
    if day_high >= target_price:
        print(f"   ✅ Target ${target_price:,.2f} would be HIT")
        print(f"      (Day high: ${day_high:,.2f})")
        execution_price = target_price
        execution_status = "TARGET_HIT"
        pnl_percent = ((target_price - entry_price) / entry_price) * 100
    else:
        print(f"   ❌ Target ${target_price:,.2f} would NOT be hit")
        print(f"      (Day high: ${day_high:,.2f})")
        
        # Check if stop loss is hit
        if day_low <= stop_loss:
            print(f"   ❌ Stop Loss ${stop_loss:,.2f} would be HIT")
            print(f"      (Day low: ${day_low:,.2f})")
            execution_price = stop_loss
            execution_status = "STOP_LOSS_HIT"
            pnl_percent = ((stop_loss - entry_price) / entry_price) * 100
        else:
            print(f"   ⚠️  Neither target nor stop loss hit")
            print(f"      Close at end of day: ${day_close:,.2f}")
            execution_price = day_close
            execution_status = "END_OF_DAY"
            pnl_percent = ((day_close - entry_price) / entry_price) * 100
    
    print(f"\n💰 Backtesting Result:")
    print(f"   Execution Price: ${execution_price:,.2f}")
    print(f"   Status: {execution_status}")
    print(f"   P&L: {pnl_percent:+.2f}%")
    
    if execution_status == "TARGET_HIT":
        print(f"   🎉 PROFITABLE TRADE!")
    elif execution_status == "STOP_LOSS_HIT":
        print(f"   📉 LOSS TRADE")
    else:
        print(f"   ⚖️  NEUTRAL TRADE")
    
    return True

if __name__ == "__main__":
    success = verify_backtesting_signal()
    
    if success:
        print(f"\n✅ BACKTESTING VERIFICATION COMPLETE")
        print(f"   The corrected signal will now show realistic results")
        print(f"   No more impossible entry prices!")
    else:
        print(f"\n❌ VERIFICATION FAILED")






























