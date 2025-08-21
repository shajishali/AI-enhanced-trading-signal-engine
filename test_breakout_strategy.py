#!/usr/bin/env python
"""
Test script for Breakout Strategy
"""

import os
import sys
import django
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.strategies import BreakoutStrategy
from apps.trading.models import Symbol
from apps.data.models import TechnicalIndicator, MarketData
from apps.signals.models import TradingSignal
from django.utils import timezone
from datetime import timedelta


def create_test_data_support_resistance():
    """Create test data for support/resistance breakout scenario"""
    print("Creating test data for support/resistance breakout scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='SOLUSDT',
        defaults={
            'name': 'Solana',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    if created:
        print(f"Created symbol: {symbol.symbol}")
    else:
        print(f"Using existing symbol: {symbol.symbol}")
    
    # Clear existing data
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    MarketData.objects.filter(symbol=symbol).delete()
    
    # Create test market data - resistance breakout scenario
    current_time = timezone.now()
    base_price = 100.0
    
    for i in range(25):  # 25 data points
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current) - breakout above resistance
            price = 105.0  # Above resistance level
            high_price = 106.0
            low_price = 104.0
            volume = 2000000  # High volume for confirmation
        elif i < 10:  # Recent periods - testing resistance
            price = 102.0 + (i * 0.1)  # Approaching resistance
            high_price = price + 1.0
            low_price = price - 1.0
            volume = 1500000 + (i * 50000)
        else:  # Earlier periods - establishing resistance
            price = 95.0 + (i * 0.2)  # Building up to resistance
            high_price = price + 1.5
            low_price = price - 1.5
            volume = 1000000 + (i * 20000)
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.5)),
            high_price=Decimal(str(high_price)),
            low_price=Decimal(str(low_price)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(volume))
        )
    
    print("Created market data for resistance breakout scenario")
    return symbol


def create_test_data_triangle_pattern():
    """Create test data for triangle pattern breakout scenario"""
    print("Creating test data for triangle pattern breakout scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='AVAXUSDT',
        defaults={
            'name': 'Avalanche',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    # Clear existing data
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    MarketData.objects.filter(symbol=symbol).delete()
    
    # Create test market data - ascending triangle breakout
    current_time = timezone.now()
    base_price = 25.0
    
    for i in range(20):  # 20 data points
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current) - breakout above triangle
            price = 28.5  # Above upper trendline
            high_price = 29.0
            low_price = 28.0
            volume = 1800000  # High volume for confirmation
        elif i < 8:  # Recent periods - triangle formation
            # Converging highs and lows
            high_price = 28.0 - (i * 0.1)  # Declining highs
            low_price = 26.0 + (i * 0.05)  # Rising lows
            price = (high_price + low_price) / 2
            volume = 1200000 + (i * 50000)
        else:  # Earlier periods - establishing triangle base
            high_price = 27.0 + (i * 0.1)
            low_price = 25.5 + (i * 0.05)
            price = (high_price + low_price) / 2
            volume = 1000000 + (i * 20000)
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.3)),
            high_price=Decimal(str(high_price)),
            low_price=Decimal(str(low_price)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(volume))
        )
    
    print("Created market data for triangle pattern breakout scenario")
    return symbol


def create_test_data_rectangle_pattern():
    """Create test data for rectangle pattern breakout scenario"""
    print("Creating test data for rectangle pattern breakout scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='ATOMUSDT',
        defaults={
            'name': 'Cosmos',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    # Clear existing data
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    MarketData.objects.filter(symbol=symbol).delete()
    
    # Create test market data - rectangle breakout
    current_time = timezone.now()
    base_price = 8.0
    
    for i in range(18):  # 18 data points
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current) - breakout above rectangle
            price = 8.8  # Above upper boundary
            high_price = 8.9
            low_price = 8.7
            volume = 1600000  # High volume for confirmation
        elif i < 12:  # Recent periods - rectangle formation (sideways)
            # Sideways movement within rectangle
            if i % 2 == 0:
                price = 8.2  # Lower part of rectangle
            else:
                price = 8.6  # Upper part of rectangle
            high_price = price + 0.1
            low_price = price - 0.1
            volume = 800000 + (i * 30000)
        else:  # Earlier periods - establishing rectangle base
            price = 8.0 + (i * 0.1)  # Building up to rectangle
            high_price = price + 0.15
            low_price = price - 0.15
            volume = 600000 + (i * 20000)
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.05)),
            high_price=Decimal(str(high_price)),
            low_price=Decimal(str(low_price)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(volume))
        )
    
    print("Created market data for rectangle pattern breakout scenario")
    return symbol


def create_test_data_momentum_breakout():
    """Create test data for momentum breakout scenario"""
    print("Creating test data for momentum breakout scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='NEARUSDT',
        defaults={
            'name': 'NEAR Protocol',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    # Clear existing data
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    MarketData.objects.filter(symbol=symbol).delete()
    
    # Create test market data - strong momentum breakout
    current_time = timezone.now()
    base_price = 3.0
    
    for i in range(15):  # 15 data points
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current) - strong momentum
            price = 3.45  # Strong upward move
            high_price = 3.50
            low_price = 3.40
            volume = 1400000  # High volume
        elif i < 5:  # Recent periods - building momentum
            price = 3.20 + (i * 0.05)  # Steady upward movement
            high_price = price + 0.08
            low_price = price - 0.08
            volume = 1000000 + (i * 80000)
        else:  # Earlier periods - base formation
            price = 3.00 + (i * 0.02)  # Slow upward drift
            high_price = price + 0.05
            low_price = price - 0.05
            volume = 800000 + (i * 20000)
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.02)),
            high_price=Decimal(str(high_price)),
            low_price=Decimal(str(low_price)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(volume))
        )
    
    print("Created market data for momentum breakout scenario")
    return symbol


def test_strategy(symbol, scenario_name):
    """Test the Breakout Strategy"""
    print(f"\nTesting Breakout Strategy for {symbol.symbol} ({scenario_name})...")
    
    # Initialize strategy
    strategy = BreakoutStrategy()
    
    # Debug: Print latest market data
    recent_data = MarketData.objects.filter(
        symbol=symbol
    ).order_by('-timestamp')[:5]
    
    print(f"\nDebug: Latest market data:")
    for i, data in enumerate(recent_data):
        print(f"  Period[{i}]: Price={data.close_price:.4f}, High={data.high_price:.4f}, Low={data.low_price:.4f}, Volume={data.volume}")
    
    # Generate signals
    signals = strategy.generate_signals(symbol)
    
    print(f"Generated {len(signals)} signals")
    
    # Display signals
    for i, signal in enumerate(signals, 1):
        print(f"\nSignal {i}:")
        print(f"  Type: {signal.signal_type.name}")
        print(f"  Strength: {signal.strength}")
        print(f"  Confidence: {signal.confidence_score:.2f}")
        print(f"  Entry Price: ${signal.entry_price:,.4f}")
        print(f"  Target Price: ${signal.target_price:,.4f}")
        print(f"  Stop Loss: ${signal.stop_loss:,.4f}")
        print(f"  Risk/Reward: {signal.risk_reward_ratio:.2f}")
        print(f"  Quality Score: {signal.quality_score:.2f}")
        print(f"  Notes: {signal.notes}")
    
    return signals


def cleanup_test_data(symbol):
    """Clean up test data"""
    print(f"\nCleaning up test data for {symbol.symbol}...")
    
    # Delete test signals
    TradingSignal.objects.filter(symbol=symbol).delete()
    
    # Delete test indicators
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    
    # Delete test market data
    MarketData.objects.filter(symbol=symbol).delete()
    
    print("Test data cleaned up")


def main():
    """Main test function"""
    print("🚀 Testing Breakout Strategy")
    print("=" * 50)
    
    total_signals = 0
    
    try:
        # Test 1: Support/Resistance breakout scenario
        print("\n1. TESTING SUPPORT/RESISTANCE BREAKOUT SCENARIO")
        print("-" * 40)
        symbol_sr = create_test_data_support_resistance()
        signals_sr = test_strategy(symbol_sr, "Support/Resistance Breakout")
        total_signals += len(signals_sr)
        cleanup_test_data(symbol_sr)
        
        # Test 2: Triangle pattern breakout scenario
        print("\n2. TESTING TRIANGLE PATTERN BREAKOUT SCENARIO")
        print("-" * 40)
        symbol_triangle = create_test_data_triangle_pattern()
        signals_triangle = test_strategy(symbol_triangle, "Triangle Pattern Breakout")
        total_signals += len(signals_triangle)
        cleanup_test_data(symbol_triangle)
        
        # Test 3: Rectangle pattern breakout scenario
        print("\n3. TESTING RECTANGLE PATTERN BREAKOUT SCENARIO")
        print("-" * 40)
        symbol_rectangle = create_test_data_rectangle_pattern()
        signals_rectangle = test_strategy(symbol_rectangle, "Rectangle Pattern Breakout")
        total_signals += len(signals_rectangle)
        cleanup_test_data(symbol_rectangle)
        
        # Test 4: Momentum breakout scenario
        print("\n4. TESTING MOMENTUM BREAKOUT SCENARIO")
        print("-" * 40)
        symbol_momentum = create_test_data_momentum_breakout()
        signals_momentum = test_strategy(symbol_momentum, "Momentum Breakout")
        total_signals += len(signals_momentum)
        cleanup_test_data(symbol_momentum)
        
        # Summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY:")
        print(f"Total Signals Generated: {total_signals}")
        print(f"Support/Resistance Signals: {len(signals_sr)}")
        print(f"Triangle Pattern Signals: {len(signals_triangle)}")
        print(f"Rectangle Pattern Signals: {len(signals_rectangle)}")
        print(f"Momentum Signals: {len(signals_momentum)}")
        
        if total_signals > 0:
            print("\n✅ Breakout Strategy test completed successfully!")
        else:
            print("\n⚠️  No signals generated - check strategy logic")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
