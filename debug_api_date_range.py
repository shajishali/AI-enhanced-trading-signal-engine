#!/usr/bin/env python3
"""
Test to debug the API date range issue
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.models import TradingSignal
from apps.data.models import Symbol
from datetime import datetime
from django.utils import timezone

def debug_api_date_range():
    """Debug the exact date range the API is using"""
    print("🔍 Debugging API Date Range")
    print("=" * 50)
    
    try:
        # Get XRP symbol
        symbol = Symbol.objects.get(symbol='XRP')
        print(f"Found symbol: {symbol.symbol}")
        
        # Use the exact same date parsing as the API
        start_date_str = '2025-08-02T00:00:00Z'
        end_date_str = '2025-09-01T23:59:59Z'
        
        print(f"API date strings: {start_date_str} to {end_date_str}")
        
        # Parse dates exactly like the API does
        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        
        print(f"Parsed dates: {start_date} to {end_date}")
        print(f"Start tzinfo: {start_date.tzinfo}")
        print(f"End tzinfo: {end_date.tzinfo}")
        
        # Query signals in this exact range
        signals = TradingSignal.objects.filter(
            symbol=symbol,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).order_by('created_at')
        
        print(f"Signals in API date range: {signals.count()}")
        
        if signals.exists():
            print("Signals found:")
            for signal in signals:
                print(f"  ID: {signal.id}, Type: {signal.signal_type.name}")
                print(f"    Created: {signal.created_at}")
                print(f"    Expires: {signal.expires_at}")
                print(f"    Strength: {signal.strength}")
                print(f"    Confidence: {signal.confidence_score}")
                print()
        else:
            print("No signals found in API date range")
            
            # Check what signals exist around this time
            print("\nChecking signals around this time:")
            nearby_signals = TradingSignal.objects.filter(
                symbol=symbol,
                created_at__gte=start_date - timezone.timedelta(days=1),
                created_at__lte=end_date + timezone.timedelta(days=1)
            ).order_by('created_at')
            
            print(f"Nearby signals: {nearby_signals.count()}")
            for signal in nearby_signals:
                print(f"  ID: {signal.id}, Created: {signal.created_at}")
        
        return signals.count() > 0
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_api_date_range()





























































