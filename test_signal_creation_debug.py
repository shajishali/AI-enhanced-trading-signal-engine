#!/usr/bin/env python3
"""
Debug script to test signal creation directly
"""
import os
import sys
import django
import logging

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.trading.models import Symbol
from apps.signals.models import SignalType
from apps.signals.models import TradingSignal
from apps.signals.services import SignalGenerationService
from decimal import Decimal
import traceback

def test_single_signal_creation():
    """Test creating a single signal directly"""
    print("=" * 60)
    print("SINGLE SIGNAL CREATION DEBUG TEST")
    print("=" * 60)
    
    # Get AVAXUSDT symbol
    symbol = Symbol.objects.filter(symbol='AVAXUSDT').first()
    if not symbol:
        print("❌ AVAXUSDT symbol not found")
        return
    
    print(f"✅ Found symbol: {symbol.symbol} (ID: {symbol.pk})")
    
    # Get signal type
    signal_type = SignalType.objects.filter(name='STRONG_BUY').first()
    if not signal_type:
        print("❌ STRONG_BUY signal type not found")
        return
    
    print(f"✅ Found signal type: {signal_type.name} (ID: {signal_type.pk})")
    
    # Initialize signal generation service
    signal_service = SignalGenerationService()
    
    print("\n1. Testing direct signal creation via _create_signal method")
    print("-" * 60)
    
    try:
        # Create a signal directly
        signal = signal_service._create_signal(
            symbol=symbol,
            signal_type_name='STRONG_BUY',
            confidence_score=0.75,
            market_data={
                'close_price': 30.44,
                'high_price': 31.00,
                'low_price': 29.50,
                'volume': 1000000
            },
            technical_score=0.7,
            sentiment_score=0.6,
            news_score=0.5,
            volume_score=0.8,
            pattern_score=0.7,
            economic_score=0.6,
            sector_score=0.5
        )
        
        if signal:
            print("✅ Signal created successfully!")
            print(f"  Signal ID: {signal.pk}")
            print(f"  Symbol: {signal.symbol.symbol}")
            print(f"  Type: {signal.signal_type.name}")
            print(f"  Entry Price: ${signal.entry_price}")
            print(f"  Target Price: ${signal.target_price}")
            print(f"  Stop Loss: ${signal.stop_loss}")
            print(f"  Created: {signal.created_at}")
            print(f"  Is Valid: {signal.is_valid}")
            
            # Test if signal was saved to database
            db_signal = TradingSignal.objects.filter(pk=signal.pk).first()
            if db_signal:
                print("✅ Signal confirmed in database!")
            else:
                print("❌ Signal NOT found in database!")
        else:
            print("❌ Signal creation returned None")
            
    except Exception as e:
        print(f"❌ Error creating signal: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
    
    print("\n2. Testing generate_signals_for_symbol method")
    print("-" * 60)
    
    try:
        # Count existing signals
        initial_count = TradingSignal.objects.filter(symbol=symbol).count()
        print(f"Initial signal count for {symbol.symbol}: {initial_count}")
        
        # Generate signals for symbol
        signals = signal_service.generate_signals_for_symbol(symbol)
        print(f"Generated {len(signals)} signals")
        
        # Count signals after generation
        final_count = TradingSignal.objects.filter(symbol=symbol).count()
        print(f"Final signal count for {symbol.symbol}: {final_count}")
        
        if final_count > initial_count:
            print("✅ Signals were saved to database!")
            
            # Show the new signals
            new_signals = TradingSignal.objects.filter(symbol=symbol).order_by('-created_at')[:3]
            for signal in new_signals:
                print(f"  ID:{signal.pk} {signal.signal_type.name} "
                      f"Entry:${signal.entry_price:.6f} TP:${signal.target_price:.6f} "
                      f"SL:${signal.stop_loss:.6f} Created:{signal.created_at.strftime('%H:%M:%S')}")
        else:
            print("❌ No new signals were saved to database!")
            
    except Exception as e:
        print(f"❌ Error generating signals: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
    
    print("\n3. Checking for any validation errors")
    print("-" * 60)
    
    # Check if there are any constraint violations or validation issues
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%signal%';")
        signal_tables = cursor.fetchall()
        print(f"Signal-related tables: {[table[0] for table in signal_tables]}")
        
        # Check TradingSignal table structure
        cursor.execute("PRAGMA table_info(signals_tradingsignal);")
        columns = cursor.fetchall()
        print(f"TradingSignal columns: {len(columns)} columns")
        
        for col in columns[:5]:  # Show first 5 columns
            print(f"  - {col[1]} ({col[2]})")

if __name__ == "__main__":
    test_single_signal_creation()
