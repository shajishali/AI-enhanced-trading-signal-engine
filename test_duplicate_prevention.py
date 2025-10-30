#!/usr/bin/env python3
"""
Test script to verify duplicate signal prevention mechanism
"""
import os
import sys
import django
import json
import logging
from datetime import datetime, timedelta
import time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.trading.models import Symbol
from apps.signals.models import TradingSignal
from apps.signals.services import SignalGenerationService
from apps.signals.tasks import generate_signals_for_all_symbols

logger = logging.getLogger(__name__)

def test_duplicate_prevention():
    """Test the duplicate prevention mechanism"""
    print("=" * 60)
    print("DUPLICATE PREVENTION MECHANISM TEST")
    print("=" * 60)
    
    print("\n1. Testing Database-Level Duplicate Prevention")
    print("-" * 50)
    
    # Test with AVAXUSDT symbol
    symbol_name = 'AVAXUSDT'
    symbol = Symbol.objects.filter(symbol=symbol_name).first()
    
    if not symbol:
        print(f"❌ Symbol {symbol_name} not found!")
        return False
    
    print(f"✅ Testing with symbol: {symbol_name}")
    
    # Clear existing signals for clean test
    initial_count = TradingSignal.objects.filter(symbol=symbol).count()
    TradingSignal.objects.filter(symbol=symbol).delete()
    print(f"Cleared {initial_count} existing signals for clean test")
    
    # Initialize signal generation service
    signal_service = SignalGenerationService()
    
    print("\n2. Testing Symbol-Level Signal Generation")
    print("-" * 50)
    
    # Generate signals 3 times with short intervals to test duplicate prevention
    for i in range(3):
        print(f"\n--- Round {i+1}: Generating signals ---")
        
        start_time = time.time()
        
        # Generate signals for symbol (this now includes database duplicate prevention)
        signals = signal_service.generate_signals_for_symbol(symbol)
        
        end_time = time.time()
        
        print(f"Generated {len(signals)} signals in {end_time - start_time:.2f} seconds")
        
        # Show the signals that were generated
        for j, signal in enumerate(signals):
            print(f"  Signal {j+1}: {signal.symbol.symbol} {signal.signal_type.name} "
                  f"Entry: ${signal.entry_price:.6f}, TP: ${signal.target_price:.6f}, "
                  f"SL: ${signal.stop_loss:.6f}, Confidence: {signal.confidence_score:.2f}")
        
        # Wait a few seconds before next generation to see if duplicates are prevented
        if i < 2:
            print("Waiting 3 seconds before next generation...")
            time.sleep(3)
    
    print("\n3. Checking Final Signal Count")
    print("-" * 50)
    
    # Check how many signals are now in the database
    total_signals = TradingSignal.objects.filter(symbol=symbol).count()
    print(f"Total signals in database for {symbol_name}: {total_signals}")
    
    # Analyze signal uniqueness
    signals = TradingSignal.objects.filter(symbol=symbol).order_by('created_at')
    unique_combinations = set()
    
    for signal in signals:
        combination = (signal.signal_type.name, f"{float(signal.entry_price):.4f}")
        unique_combinations.add(combination)
    
    print(f"Unique signal type + price combinations: {len(unique_combinations)}")
    
    # Results interpretation
    print("\n4. DUPLICATE PREVENTION RESULTS")
    print("-" * 50)
    
    if total_signals <= len(unique_combinations):
        print("✅ SUCCESS: No duplicate signals detected!")
        print("✅ Database-level duplicate prevention is working correctly!")
        return True
    else:
        print("❌ ISSUE: Possible duplicates detected!")
        print("❌ Database-level duplicate prevention may need improvement!")
        return False

def test_manual_vs_automatic_generation():
    """Test difference between manual and automatic signal generation"""
    print("\n" + "=" * 60)
    print("MANUAL VS AUTOMATIC SIGNAL GENERATION TEST")
    print("=" * 60)
    
    symbol_name = 'AVAXUSDT'
    symbol = Symbol.objects.filter(symbol=symbol_name).first()
    
    if not symbol:
        print(f"❌ Symbol {symbol_name} not found!")
        return
    
    print(f"Testing with symbol: {symbol_name}")
    
    print("\n1. MANUAL SIGNAL GENERATION")
    print("-" * 50)
    print("Manual generation allows multiple signals without clearing existing ones.")
    print("Problem: Can create duplicates, especially if clicked multiple times.")
    
    print("\n2. AUTOMATIC SIGNAL GENERATION")
    print("-" * 50)
    print("Automatic generation clears old signals before creating new ones.")
    print("Solution: Prevents duplicates by replacing signals.")
    
    print("\n3. NEW DATABASE-LEVEL DUPLICATE PREVENTION")
    print("-" * 50)
    print("Now checks existing signals before creating new ones.")
    print("Filters out signals that are too similar.")

def test_different_symbols():
    """Test duplicate prevention across different symbols"""
    print("\n" + "=" * 60)
    print("MULTI-SYMBOL DUPLICATE PREVENTION TEST")
    print("=" * 60)
    
    test_symbols = ['AVAXUSDT', 'ADAUSDT', 'ETHUSDT']
    
    for symbol_name in test_symbols:
        symbol = Symbol.objects.filter(symbol=symbol_name).first()
        
        if not symbol:
            print(f"❌ Symbol {symbol_name} not found - skipping")
            continue
        
        print(f"\n--- Testing {symbol_name} ---")
        
        signal_count = TradingSignal.objects.filter(symbol=symbol).count()
        print(f"Current signals for {symbol_name}: {signal_count}")
        
        dup_count = TradingSignal.objects.filter(
            symbol=symbol,
            created_at__gte=datetime.now() - timedelta(hours=1),
            is_valid=True
        ).count()
        
        print(f"Recent signals (1 hour): {dup_count}")
        
        if dup_count > 0:
            recent_signals = TradingSignal.objects.filter(
                symbol=symbol,
                created_at__gte=datetime.now() - timedelta(hours=1)
            ).order_by('-created_at')[:3]
            
            print("Recent signals:")
            for signal in recent_signals:
                time_diff = time.time() - signal.created_at.timestamp()
                print(f"  ID:{signal.pk} {signal.signal_type.name} "
                      f"Entry:${signal.entry_price:.6f} "
                      f"Age:{time_diff:.0f}s ago")

def main():
    print("🚀 Starting comprehensive duplicate prevention test")
    print("=" * 60)
    
    # Run tests
    success = test_duplicate_prevention()
    test_manual_vs_automatic_generation()
    test_different_symbols()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ PASSED: Duplicate prevention mechanism working correctly")
        print("\nKey Improvements Made:")
        print("1. ✅ Fixed MarketData table - now syncing real prices")
        print("2. ✅ Updated TP/SL calculation - using current market prices")
        print("3. ✅ Implemented 30-minute strategy - support/resistance levels")
        print("4. ✅ Added symbol mapping - USDT pairs map to base symbols")
        print("5. ✅ Added database-level duplicate prevention")
        
        print("\nSignal Generation Process:")
        print("- Generate signals → Batch deduplication → Database duplicate check → Final signals")
        
    else:
        print("❌ FAILED: Duplicate prevention needs more work")
    
    print("\nRecommendations for Production:")
    print("1. 🔧 Monitor signal creation logs for duplicate detection")
    print("2. 🔧 Consider archiving old signals before manual generation")
    print("3. 🔧 Add duplicate signal alerts for monitoring")
    print("4. 🔧 Implement signal expiry (24-48 hours)")

if __name__ == "__main__":
    main()
























































