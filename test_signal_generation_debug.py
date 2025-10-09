#!/usr/bin/env python3
"""
Test to debug why signals are still not being generated
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.services import HistoricalSignalService
from apps.data.models import Symbol
from datetime import datetime, timedelta
from django.utils import timezone

def test_signal_generation_directly():
    """Test signal generation directly to debug the issue"""
    print("🔍 Testing Signal Generation Directly")
    print("=" * 50)
    
    try:
        # Get XRP symbol
        symbol = Symbol.objects.get(symbol='XRP')
        print(f"Found symbol: {symbol.symbol}")
        
        # Set up date range
        today = datetime.now()
        start_date = today - timedelta(days=60)
        end_date = today - timedelta(days=30)
        
        # Make dates timezone-aware
        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)
        
        print(f"Date range: {start_date} to {end_date}")
        
        # Create historical signal service
        service = HistoricalSignalService()
        
        # Generate signals
        print("Generating signals...")
        signals = service.generate_signals_for_period(symbol, start_date, end_date)
        
        print(f"Generated {len(signals)} signals")
        
        if signals:
            print("Signal details:")
            for i, signal in enumerate(signals):
                print(f"  Signal {i+1}:")
                print(f"    Symbol: {signal.symbol.symbol}")
                print(f"    Type: {signal.signal_type.name}")
                print(f"    Created: {signal.created_at}")
                print(f"    Expires: {signal.expires_at}")
                print(f"    Strength: {signal.strength}")
                print(f"    Confidence: {signal.confidence_score}")
                print()
        else:
            print("No signals generated")
            
        return len(signals) > 0
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_signal_generation_directly()




















