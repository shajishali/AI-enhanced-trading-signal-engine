#!/usr/bin/env python3
"""
Progress Monitor Script
Monitors the data import progress
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.models import MarketData
from apps.trading.models import Symbol

def check_progress():
    """Check the current import progress"""
    try:
        # Get total records imported so far
        total_records = MarketData.objects.count()
        
        # Get USDT symbols count
        usdt_symbols = Symbol.objects.filter(symbol__endswith='USDT').exclude(symbol='USDT').count()
        
        # Calculate expected total (roughly)
        # 2020-01-01 to 2025-10-14 = ~2100 days
        expected_records = usdt_symbols * 2100
        
        # Calculate progress percentage
        progress_percent = (total_records / expected_records) * 100 if expected_records > 0 else 0
        
        print(f"📊 Progress Update - {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Records imported: {total_records:,}")
        print(f"   Expected total: ~{expected_records:,}")
        print(f"   Progress: {progress_percent:.1f}%")
        
        # Check which symbols have data
        symbols_with_data = 0
        for symbol in Symbol.objects.filter(symbol__endswith='USDT').exclude(symbol='USDT'):
            if MarketData.objects.filter(symbol=symbol).exists():
                symbols_with_data += 1
        
        print(f"   Symbols completed: {symbols_with_data}/{usdt_symbols}")
        
        # Show recent data sample
        recent_data = MarketData.objects.order_by('-timestamp')[:3]
        if recent_data:
            print(f"   Latest data:")
            for data in recent_data:
                print(f"     {data.symbol.symbol}: {data.timestamp.date()} - Close: ${data.close_price}")
        
        return total_records > 0
        
    except Exception as e:
        print(f"❌ Error checking progress: {e}")
        return False

def main():
    """Main monitoring function"""
    print("🔍 CRYPTO DATA IMPORT PROGRESS MONITOR")
    print("=" * 50)
    
    while True:
        try:
            has_data = check_progress()
            
            if not has_data:
                print("⏳ Waiting for data import to start...")
            else:
                print("✅ Data import is active")
            
            print("-" * 50)
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()































