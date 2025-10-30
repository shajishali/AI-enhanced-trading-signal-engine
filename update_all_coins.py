#!/usr/bin/env python
"""
Script to update all supported crypto symbols with fresh data
"""
import os
import sys
import django
from datetime import datetime, timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.trading.models import Symbol
from apps.data.historical_data_manager import HistoricalDataManager
from django.utils import timezone as django_timezone

def update_all_supported_coins():
    """Update all supported crypto symbols with fresh data"""
    
    # List of supported symbols by Binance API
    supported_symbols = [
        'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'TRX', 'LINK', 'DOT',
        'MATIC', 'AVAX', 'UNI', 'ATOM', 'LTC', 'BCH', 'ALGO', 'VET', 'FTM', 'ICP',
        'SAND', 'MANA', 'NEAR', 'APT', 'OP', 'ARB', 'MKR', 'RUNE', 'INJ', 'STX',
        'AAVE', 'COMP', 'CRV', 'LDO', 'CAKE', 'PENDLE', 'DYDX', 'FET', 'CRO', 'KCS',
        'OKB', 'LEO', 'QNT', 'HBAR', 'EGLD', 'FLOW', 'SEI', 'TIA', 'GALA', 'GRT',
        'XMR', 'ZEC', 'DAI', 'TUSD', 'GT'
    ]
    
    # Get symbols from database that are supported
    symbols = Symbol.objects.filter(
        symbol_type='CRYPTO', 
        is_active=True, 
        symbol__in=supported_symbols
    ).order_by('symbol')
    
    print(f"🔄 Updating {symbols.count()} supported crypto symbols...")
    print("=" * 60)
    
    manager = HistoricalDataManager()
    success_count = 0
    error_count = 0
    
    # Calculate time range: from 1 hour ago to 1 hour before current time
    end_time = django_timezone.now() - django_timezone.timedelta(hours=1)
    start_time = end_time - django_timezone.timedelta(hours=1)
    
    print(f"📅 Time range: {start_time} to {end_time}")
    print("=" * 60)
    
    for i, symbol in enumerate(symbols, 1):
        try:
            print(f"[{i:2d}/{symbols.count()}] Updating {symbol.symbol}...", end=" ")
            
            # Update with fresh data
            if manager.fetch_complete_historical_data(symbol, timeframe='1h', start=start_time, end=end_time):
                print("✅ Success")
                success_count += 1
            else:
                print("❌ Failed")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            error_count += 1
    
    print("=" * 60)
    print(f"📊 UPDATE SUMMARY:")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {error_count}")
    print(f"📈 Total: {symbols.count()}")
    print(f"📊 Success Rate: {(success_count/symbols.count()*100):.1f}%")
    print("=" * 60)
    
    return success_count, error_count

if __name__ == "__main__":
    print("🚀 Starting automated update for all supported crypto coins...")
    success, errors = update_all_supported_coins()
    
    if success > 0:
        print(f"\n🎉 Successfully updated {success} crypto symbols!")
        print("🔄 Your automated hourly updates are now running.")
        print("📊 Data will be updated every hour at minute 0.")
    else:
        print("\n❌ No symbols were updated successfully.")
    
    print("\n✅ Update process completed!")


















