#!/usr/bin/env python3
"""
Debug script to check if signals are actually being saved to the database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.models import TradingSignal
from apps.data.models import Symbol
from datetime import datetime, timedelta
from django.utils import timezone

def debug_database_signals():
    """Check if signals are actually in the database"""
    print("🔍 Debugging Database Signals")
    print("=" * 50)
    
    try:
        # Get XRP symbol
        symbol = Symbol.objects.get(symbol='XRP')
        print(f"Found symbol: {symbol.symbol}")
        
        # Check all signals for XRP
        all_signals = TradingSignal.objects.filter(symbol=symbol)
        print(f"Total signals for XRP in database: {all_signals.count()}")
        
        if all_signals.exists():
            print("Recent signals:")
            for signal in all_signals.order_by('-created_at')[:5]:
                print(f"  ID: {signal.id}, Type: {signal.signal_type.name}, Created: {signal.created_at}")
        
        # Check signals in the date range we're testing
        today = datetime.now()
        start_date = today - timedelta(days=60)
        end_date = today - timedelta(days=30)
        
        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)
        
        print(f"\nChecking signals in date range: {start_date} to {end_date}")
        
        range_signals = TradingSignal.objects.filter(
            symbol=symbol,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        print(f"Signals in date range: {range_signals.count()}")
        
        if range_signals.exists():
            print("Signals in range:")
            for signal in range_signals.order_by('created_at'):
                print(f"  ID: {signal.id}, Type: {signal.signal_type.name}")
                print(f"    Created: {signal.created_at}")
                print(f"    Expires: {signal.expires_at}")
                print(f"    Strength: {signal.strength}")
                print(f"    Confidence: {signal.confidence_score}")
                print()
        
        return range_signals.count() > 0
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_database_signals()


























