#!/usr/bin/env python
"""
Test script for MACD Strategy
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

from apps.signals.strategies import MACDStrategy
from apps.trading.models import Symbol
from apps.data.models import TechnicalIndicator, MarketData
from apps.signals.models import TradingSignal
from django.utils import timezone
from datetime import timedelta


def create_test_data_crossover():
    """Create test data for MACD crossover scenario"""
    print("Creating test data for MACD crossover scenario...")
    
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
    
    # Create test market data
    current_time = timezone.now()
    base_price = 100.0
    
    for i in range(20):  # 20 data points
        timestamp = current_time - timedelta(hours=i)
        # Rising price trend
        price = base_price + (i * 2)  # Price going up
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 1)),
            high_price=Decimal(str(price + 1)),
            low_price=Decimal(str(price - 1)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(1000000 + i * 10000))
        )
    
    print("Created market data")
    
    # Create MACD indicators - bullish crossover scenario
    # MACD line crosses above signal line
    for i in range(10):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            macd_value = 0.005  # MACD above signal
            signal_value = 0.003  # Signal below MACD
            hist_value = 0.002   # Positive histogram
        elif i == 1:  # Previous period
            macd_value = 0.002  # MACD below signal (for crossover)
            signal_value = 0.003  # Signal above MACD
            hist_value = -0.001  # Negative histogram
        else:  # Earlier periods
            macd_value = 0.001 + (i * 0.0005)  # Gradually increasing MACD
            signal_value = 0.002 + (i * 0.0003)  # Gradually increasing signal
            hist_value = macd_value - signal_value  # Histogram difference
        
        # Create MACD line indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_LINE',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(macd_value)),
            source_id=1
        )
        
        # Create signal line indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_SIGNAL',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(signal_value)),
            source_id=1
        )
        
        # Create histogram indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_HISTOGRAM',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(hist_value)),
            source_id=1
        )
    
    print("Created MACD indicators (bullish crossover scenario)")
    return symbol


def create_test_data_histogram():
    """Create test data for MACD histogram scenario"""
    print("Creating test data for MACD histogram scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='DOTUSDT',
        defaults={
            'name': 'Polkadot',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    # Clear existing data
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    MarketData.objects.filter(symbol=symbol).delete()
    
    # Create test market data
    current_time = timezone.now()
    base_price = 5.0
    
    for i in range(20):  # 20 data points
        timestamp = current_time - timedelta(hours=i)
        # Declining price trend
        price = base_price - (i * 0.1)  # Price going down
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price + 0.05)),
            high_price=Decimal(str(price + 0.1)),
            low_price=Decimal(str(price - 0.05)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(1000000 + i * 10000))
        )
    
    print("Created market data")
    
    # Create MACD indicators - histogram reversal scenario
    # Histogram turns from negative to positive
    for i in range(10):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            macd_value = -0.001  # MACD still negative but improving
            signal_value = -0.002  # Signal more negative
            hist_value = 0.001   # Positive histogram (reversal)
        elif i == 1:  # Previous period
            macd_value = -0.002  # MACD at low point
            signal_value = -0.002  # Signal at same level
            hist_value = 0.000   # Zero histogram (turning point)
        else:  # Earlier periods
            macd_value = -0.003 - (i * 0.0005)  # Gradually decreasing MACD
            signal_value = -0.002 - (i * 0.0003)  # Gradually decreasing signal
            hist_value = macd_value - signal_value  # Histogram difference
        
        # Create MACD line indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_LINE',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(macd_value)),
            source_id=1
        )
        
        # Create signal line indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_SIGNAL',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(signal_value)),
            source_id=1
        )
        
        # Create histogram indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_HISTOGRAM',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(hist_value)),
            source_id=1
        )
    
    print("Created MACD indicators (histogram reversal scenario)")
    return symbol


def create_test_data_momentum():
    """Create test data for MACD momentum scenario"""
    print("Creating test data for MACD momentum scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='LINKUSDT',
        defaults={
            'name': 'Chainlink',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    # Clear existing data
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    MarketData.objects.filter(symbol=symbol).delete()
    
    # Create test market data
    current_time = timezone.now()
    base_price = 15.0
    
    for i in range(20):  # 20 data points
        timestamp = current_time - timedelta(hours=i)
        # Strong rising price trend
        price = base_price + (i * 0.5)  # Price going up strongly
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.2)),
            high_price=Decimal(str(price + 0.3)),
            low_price=Decimal(str(price - 0.2)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(1000000 + i * 10000))
        )
    
    print("Created market data")
    
    # Create MACD indicators - strong momentum scenario
    # Both MACD and histogram showing strong upward momentum
    for i in range(10):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            macd_value = 0.008  # Strong positive MACD
            signal_value = 0.005  # Positive signal
            hist_value = 0.003   # Strong positive histogram
        elif i == 1:  # Previous period
            macd_value = 0.006  # Good MACD
            signal_value = 0.004  # Good signal
            hist_value = 0.002   # Positive histogram
        else:  # Earlier periods
            macd_value = 0.004 + (i * 0.0005)  # Gradually increasing MACD
            signal_value = 0.003 + (i * 0.0003)  # Gradually increasing signal
            hist_value = macd_value - signal_value  # Histogram difference
        
        # Create MACD line indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_LINE',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(macd_value)),
            source_id=1
        )
        
        # Create signal line indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_SIGNAL',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(signal_value)),
            source_id=1
        )
        
        # Create histogram indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_HISTOGRAM',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(hist_value)),
            source_id=1
        )
    
    print("Created MACD indicators (momentum scenario)")
    return symbol


def create_test_data_divergence():
    """Create test data for MACD divergence scenario"""
    print("Creating test data for MACD divergence scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='MATICUSDT',
        defaults={
            'name': 'Polygon',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    # Clear existing data
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    MarketData.objects.filter(symbol=symbol).delete()
    
    # Create test market data for bullish divergence
    # Price makes lower lows, but MACD makes higher lows
    current_time = timezone.now()
    base_price = 0.80
    
    # Create price data with lower lows
    price_data = [
        0.800,  # Current (recent low)
        0.805,
        0.802,
        0.810,  # Previous low (higher than current)
        0.815,
        0.820,
        0.818,
        0.816,
        0.812,
        0.808
    ]
    
    for i, price in enumerate(price_data):
        timestamp = current_time - timedelta(hours=i)
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.005)),
            high_price=Decimal(str(price + 0.010)),
            low_price=Decimal(str(price - 0.010)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(1000000 + i * 10000))
        )
    
    print("Created market data for divergence")
    
    # Create MACD indicators for bullish divergence
    # MACD makes higher lows while price makes lower lows
    macd_data = [
        -0.002,  # Current MACD low (higher than previous)
        -0.001,
        -0.0015,
        -0.003,  # Previous MACD low (lower than current) 
        -0.001,
        0.001,
        0.000,
        -0.001,
        -0.0015,
        -0.002
    ]
    
    for i, macd_value in enumerate(macd_data):
        timestamp = current_time - timedelta(hours=i)
        
        # Create MACD line indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_LINE',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(macd_value)),
            source_id=1
        )
        
        # Create signal line indicator (simple calculation)
        signal_value = macd_value * 0.8  # Signal follows MACD but smoother
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_SIGNAL',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(signal_value)),
            source_id=1
        )
        
        # Create histogram indicator
        hist_value = macd_value - signal_value
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='MACD_HISTOGRAM',
            period=0,
            timestamp=timestamp,
            value=Decimal(str(hist_value)),
            source_id=1
        )
    
    print("Created MACD indicators (bullish divergence scenario)")
    return symbol


def test_strategy(symbol, scenario_name):
    """Test the MACD Strategy"""
    print(f"\nTesting MACD Strategy for {symbol.symbol} ({scenario_name})...")
    
    # Initialize strategy
    strategy = MACDStrategy()
    
    # Debug: Print MACD values
    macd_line = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='MACD_LINE', period=0
    ).order_by('-timestamp')[:5]
    
    signal_line = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='MACD_SIGNAL', period=0
    ).order_by('-timestamp')[:5]
    
    histogram = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='MACD_HISTOGRAM', period=0
    ).order_by('-timestamp')[:5]
    
    print(f"\nDebug: Latest MACD values:")
    for i in range(min(5, len(macd_line), len(signal_line), len(histogram))):
        print(f"  Period[{i}]: MACD={macd_line[i].value:.6f}, Signal={signal_line[i].value:.6f}, Hist={histogram[i].value:.6f}")
    
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
    print("🚀 Testing MACD Strategy")
    print("=" * 50)
    
    total_signals = 0
    
    try:
        # Test 1: MACD Crossover scenario
        print("\n1. TESTING MACD CROSSOVER SCENARIO")
        print("-" * 30)
        symbol_crossover = create_test_data_crossover()
        signals_crossover = test_strategy(symbol_crossover, "MACD Crossover")
        total_signals += len(signals_crossover)
        cleanup_test_data(symbol_crossover)
        
        # Test 2: Histogram scenario
        print("\n2. TESTING HISTOGRAM SCENARIO")
        print("-" * 30)
        symbol_histogram = create_test_data_histogram()
        signals_histogram = test_strategy(symbol_histogram, "Histogram Reversal")
        total_signals += len(signals_histogram)
        cleanup_test_data(symbol_histogram)
        
        # Test 3: Momentum scenario
        print("\n3. TESTING MOMENTUM SCENARIO")
        print("-" * 30)
        symbol_momentum = create_test_data_momentum()
        signals_momentum = test_strategy(symbol_momentum, "Strong Momentum")
        total_signals += len(signals_momentum)
        cleanup_test_data(symbol_momentum)
        
        # Test 4: Divergence scenario
        print("\n4. TESTING DIVERGENCE SCENARIO")
        print("-" * 30)
        symbol_divergence = create_test_data_divergence()
        signals_divergence = test_strategy(symbol_divergence, "Bullish Divergence")
        total_signals += len(signals_divergence)
        cleanup_test_data(symbol_divergence)
        
        # Summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY:")
        print(f"Total Signals Generated: {total_signals}")
        print(f"Crossover Signals: {len(signals_crossover)}")
        print(f"Histogram Signals: {len(signals_histogram)}")
        print(f"Momentum Signals: {len(signals_momentum)}")
        print(f"Divergence Signals: {len(signals_divergence)}")
        
        if total_signals > 0:
            print("\n✅ MACD Strategy test completed successfully!")
        else:
            print("\n⚠️  No signals generated - check strategy logic")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
