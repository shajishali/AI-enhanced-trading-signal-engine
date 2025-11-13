"""
Phase 4: Test Unified Signal Generation
Test that the unified signal generation produces 10 best signals with news and sentiment
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.signals.unified_signal_task import generate_unified_signals_task
from apps.signals.models import TradingSignal

print("="*60)
print("PHASE 4: TESTING UNIFIED SIGNAL GENERATION")
print("="*60)

# Check current signals
print("\n1. CURRENT SIGNAL STATUS")
print("-" * 60)

recent_signals = TradingSignal.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=1),
    is_valid=True
).order_by('-confidence_score')

print(f"Recent valid signals (last hour): {recent_signals.count()}")

if recent_signals.exists():
    print(f"\nTop 5 Recent Signals:")
    for i, signal in enumerate(recent_signals[:5], 1):
        print(f"  {i}. {signal.symbol.symbol} - {signal.signal_type.name} - "
              f"Confidence: {signal.confidence_score:.1%}")

# Test unified signal generation
print("\n2. TESTING UNIFIED SIGNAL GENERATION")
print("-" * 60)
print("Running unified signal generation task...")

try:
    result = generate_unified_signals_task()
    
    print(f"\nTask Result:")
    print(f"  Success: {result.get('success', False)}")
    print(f"  Total Signals Generated: {result.get('total_signals', 0)}")
    print(f"  Best Signals Selected: {result.get('best_signals', 0)}")
    print(f"  Signals Saved: {result.get('saved_signals', 0)}")
    print(f"  Symbols Processed: {result.get('processed_symbols', 0)}")
    
    if result.get('success'):
        print("\n✓ Task completed successfully")
        
        # Check for new signals
        new_signals = TradingSignal.objects.filter(
            created_at__gte=timezone.now() - timedelta(minutes=5),
            is_valid=True
        ).order_by('-confidence_score')
        
        print(f"\nNew signals created (last 5 minutes): {new_signals.count()}")
        
        if new_signals.count() >= 10:
            print("✓ Generated 10 or more signals")
        elif new_signals.count() > 0:
            print(f"⚠ Generated {new_signals.count()} signals (target: 10)")
        else:
            print("⚠ No new signals generated")
        
        if new_signals.exists():
            print(f"\nTop 10 New Signals:")
            for i, signal in enumerate(new_signals[:10], 1):
                print(f"  {i}. {signal.symbol.symbol} - {signal.signal_type.name} - "
                      f"Confidence: {signal.confidence_score:.1%}")
    else:
        print("\n✗ Task did not complete successfully")
        
except Exception as e:
    print(f"\n✗ Task failed with error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)














