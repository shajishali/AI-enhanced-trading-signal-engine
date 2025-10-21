#!/usr/bin/env python3
"""
Fix AVAXUSDT MarketData by copying/mapping from AVAX base symbol
"""

import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.trading.models import Symbol
from apps.data.models import MarketData

def fix_avaxusdt_marketdata():
    print("=" * 60)
    print("FIXING AVAXUSDT MARKETDATA")
    print("=" * 60)
    
    try:
        # Get symbols
        avax_symbol = Symbol.objects.get(symbol='AVAX')
        avaxusdt_symbol = Symbol.objects.get(symbol='AVAXUSDT')
        
        print(f"AVAX symbol ID: {avax_symbol.pk}")
        print(f"AVAXUSDT symbol ID: {avaxusdt_symbol.pk}")
        
        # Get AVAX market data
        avax_data = MarketData.objects.filter(symbol=avax_symbol).order_by('-timestamp')
        avax_count = avax_data.count()
        
        print(f"\nAVAX MarketData records: {avax_count}")
        print(f"AVAXUSDT MarketData records: {MarketData.objects.filter(symbol=avaxusdt_symbol).count()}")
        
        if avax_count > 0:
            # Copy AVAX data to AVAXUSDT
            print("\nCopying AVAX MarketData to AVAXUSDT...")
            
            copies_created = 0
            for md in avax_data[:10]:  # Copy recent 10 records first as test
                try:
                    # Create new MarketData for AVAXUSDT with same data
                    new_md = MarketData.objects.create(
                        symbol=avaxusdt_symbol,
                        timestamp=md.timestamp,
                        open_price=md.open_price,
                        high_price=md.high_price,
                        low_price=md.low_price,
                        close_price=md.close_price,
                        volume=md.volume,
                        source=md.source
                    )
                    copies_created += 1
                    
                except Exception as e:
                    print(f"Error copying record at {md.timestamp}: {e}")
            
            print(f"\n✅ Created {copies_created} AVAXUSDT MarketData records")
            
            # Verify the fix
            final_count = MarketData.objects.filter(symbol=avaxusdt_symbol).count()
            print(f"AVAXUSDT MarketData records now: {final_count}")
            
            if final_count > 0:
                print("✅ AVAXUSDT MarketData fix successful!")
                print("\nNext steps:")
                print("1. Test signal generation for AVAXUSDT")
                print("2. Verify TP/SL calculations use real prices")
                print("3. Check signal quality improves to 'stable'")
            else:
                print("❌ No MarketData created for AVAXUSDT")
                
        else:
            print("❌ No AVAX MarketData available to copy")
            
    except Exception as e:
        print(f"❌ Error fixing AVAXUSDT MarketData: {e}")
    
    print("\n" + "=" * 60)
    print("AVAXUSDT MARKETDATA FIX COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    fix_avaxusdt_marketdata()






































