#!/usr/bin/env python
"""
Test script for Bollinger Bands Strategy
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

from apps.signals.strategies import BollingerBandsStrategy
from apps.trading.models import Symbol
from apps.data.models import TechnicalIndicator, MarketData
from apps.signals.models import TradingSignal
from django.utils import timezone
from datetime import timedelta


def create_test_data_price_position():
    """Create test data for price position scenario"""
    print("Creating test data for price position scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='ADAUSDT',
        defaults={
            'name': 'Cardano',
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
    base_price = 0.50
    
    for i in range(20):  # 20 data points
        timestamp = current_time - timedelta(hours=i)
        # Stable price trend
        price = base_price + (i * 0.001)  # Slight upward trend
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.002)),
            high_price=Decimal(str(price + 0.003)),
            low_price=Decimal(str(price - 0.002)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(1000000 + i * 10000))
        )
    
    print("Created market data")
    
    # Create Bollinger Bands indicators - oversold scenario
    # Price near lower band
    for i in range(10):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            upper_value = 0.520  # Upper band
            middle_value = 0.505  # Middle band (SMA)
            lower_value = 0.490  # Lower band
            # Current price is 0.501, very close to lower band (0.490)
        else:  # Previous periods
            upper_value = 0.518 + (i * 0.001)
            middle_value = 0.504 + (i * 0.0005)
            lower_value = 0.489 + (i * 0.0005)
        
        # Create upper band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_UPPER',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(upper_value)),
            source_id=1
        )
        
        # Create middle band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_MIDDLE',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(middle_value)),
            source_id=1
        )
        
        # Create lower band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_LOWER',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(lower_value)),
            source_id=1
        )
    
    print("Created Bollinger Bands indicators (oversold scenario)")
    return symbol


def create_test_data_band_width():
    """Create test data for band width scenario"""
    print("Creating test data for band width scenario...")
    
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
        # Stable price trend
        price = base_price + (i * 0.01)  # Slight upward trend
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.02)),
            high_price=Decimal(str(price + 0.03)),
            low_price=Decimal(str(price - 0.02)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(1000000 + i * 10000))
        )
    
    print("Created market data")
    
    # Create Bollinger Bands indicators - volatility expansion scenario
    # Bands widening significantly
    for i in range(10):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            upper_value = 5.25  # Upper band - expanded
            middle_value = 5.10  # Middle band
            lower_value = 4.95   # Lower band - expanded
            # Band width: 5.25 - 4.95 = 0.30 (expanded)
        elif i == 1:  # Previous period
            upper_value = 5.20  # Upper band - normal
            middle_value = 5.09  # Middle band
            lower_value = 5.00   # Lower band - normal
            # Band width: 5.20 - 5.00 = 0.20 (normal)
        else:  # Earlier periods
            upper_value = 5.18 + (i * 0.001)
            middle_value = 5.08 + (i * 0.0005)
            lower_value = 5.01 + (i * 0.0005)
        
        # Create upper band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_UPPER',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(upper_value)),
            source_id=1
        )
        
        # Create middle band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_MIDDLE',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(middle_value)),
            source_id=1
        )
        
        # Create lower band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_LOWER',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(lower_value)),
            source_id=1
        )
    
    print("Created Bollinger Bands indicators (volatility expansion scenario)")
    return symbol


def create_test_data_squeeze():
    """Create test data for squeeze scenario"""
    print("Creating test data for squeeze scenario...")
    
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
        # Stable price trend
        price = base_price + (i * 0.01)  # Slight upward trend
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.02)),
            high_price=Decimal(str(price + 0.03)),
            low_price=Decimal(str(price - 0.02)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(1000000 + i * 10000))
        )
    
    print("Created market data")
    
    # Create Bollinger Bands indicators - squeeze scenario
    # Bands compressing significantly
    for i in range(10):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            upper_value = 15.08  # Upper band - compressed
            middle_value = 15.04  # Middle band
            lower_value = 15.00   # Lower band - compressed
            # Current band width: 15.08 - 15.00 = 0.08 (very compressed)
        elif i == 1:  # Previous period
            upper_value = 15.10  # Upper band - normal
            middle_value = 15.03  # Middle band
            lower_value = 14.98   # Lower band - normal
            # Band width: 15.10 - 14.98 = 0.12 (normal)
        else:  # Earlier periods - wider bands
            upper_value = 15.15 + (i * 0.001)
            middle_value = 15.02 + (i * 0.0005)
            lower_value = 14.95 + (i * 0.0005)
        
        # Create upper band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_UPPER',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(upper_value)),
            source_id=1
        )
        
        # Create middle band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_MIDDLE',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(middle_value)),
            source_id=1
        )
        
        # Create lower band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_LOWER',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(lower_value)),
            source_id=1
        )
    
    print("Created Bollinger Bands indicators (squeeze scenario)")
    return symbol


def create_test_data_mean_reversion():
    """Create test data for mean reversion scenario"""
    print("Creating test data for mean reversion scenario...")
    
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
    
    # Create test market data
    current_time = timezone.now()
    base_price = 0.80
    
    for i in range(20):  # 20 data points
        timestamp = current_time - timedelta(hours=i)
        # Stable price trend
        price = base_price + (i * 0.001)  # Slight upward trend
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.002)),
            high_price=Decimal(str(price + 0.003)),
            low_price=Decimal(str(price - 0.002)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(1000000 + i * 10000))
        )
    
    print("Created market data")
    
    # Create Bollinger Bands indicators - mean reversion scenario
    # Price significantly above middle band
    for i in range(10):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            upper_value = 0.820  # Upper band
            middle_value = 0.805  # Middle band (SMA)
            lower_value = 0.790  # Lower band
            # Current price is 0.801, above middle band (0.805) - expect reversion down
        else:  # Previous periods
            upper_value = 0.818 + (i * 0.001)
            middle_value = 0.804 + (i * 0.0005)
            lower_value = 0.789 + (i * 0.0005)
        
        # Create upper band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_UPPER',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(upper_value)),
            source_id=1
        )
        
        # Create middle band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_MIDDLE',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(middle_value)),
            source_id=1
        )
        
        # Create lower band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_LOWER',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(lower_value)),
            source_id=1
        )
    
    print("Created Bollinger Bands indicators (mean reversion scenario)")
    return symbol


def test_strategy(symbol, scenario_name):
    """Test the Bollinger Bands Strategy"""
    print(f"\nTesting Bollinger Bands Strategy for {symbol.symbol} ({scenario_name})...")
    
    # Initialize strategy
    strategy = BollingerBandsStrategy()
    
    # Debug: Print Bollinger Bands values
    upper_band = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='BB_UPPER', period=20
    ).order_by('-timestamp')[:5]
    
    middle_band = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='BB_MIDDLE', period=20
    ).order_by('-timestamp')[:5]
    
    lower_band = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='BB_LOWER', period=20
    ).order_by('-timestamp')[:5]
    
    print(f"\nDebug: Latest Bollinger Bands values:")
    for i in range(min(5, len(upper_band), len(middle_band), len(lower_band))):
        print(f"  Period[{i}]: Upper={upper_band[i].value:.4f}, Middle={middle_band[i].value:.4f}, Lower={lower_band[i].value:.4f}")
    
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
    print("🚀 Testing Bollinger Bands Strategy")
    print("=" * 50)
    
    total_signals = 0
    
    try:
        # Test 1: Price Position scenario
        print("\n1. TESTING PRICE POSITION SCENARIO")
        print("-" * 30)
        symbol_position = create_test_data_price_position()
        signals_position = test_strategy(symbol_position, "Price Position (Oversold)")
        total_signals += len(signals_position)
        cleanup_test_data(symbol_position)
        
        # Test 2: Band Width scenario
        print("\n2. TESTING BAND WIDTH SCENARIO")
        print("-" * 30)
        symbol_width = create_test_data_band_width()
        signals_width = test_strategy(symbol_width, "Volatility Expansion")
        total_signals += len(signals_width)
        cleanup_test_data(symbol_width)
        
        # Test 3: Squeeze scenario
        print("\n3. TESTING SQUEEZE SCENARIO")
        print("-" * 30)
        symbol_squeeze = create_test_data_squeeze()
        signals_squeeze = test_strategy(symbol_squeeze, "Band Squeeze")
        total_signals += len(signals_squeeze)
        cleanup_test_data(symbol_squeeze)
        
        # Test 4: Mean Reversion scenario
        print("\n4. TESTING MEAN REVERSION SCENARIO")
        print("-" * 30)
        symbol_reversion = create_test_data_mean_reversion()
        signals_reversion = test_strategy(symbol_reversion, "Mean Reversion")
        total_signals += len(signals_reversion)
        cleanup_test_data(symbol_reversion)
        
        # Summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY:")
        print(f"Total Signals Generated: {total_signals}")
        print(f"Position Signals: {len(signals_position)}")
        print(f"Width Signals: {len(signals_width)}")
        print(f"Squeeze Signals: {len(signals_squeeze)}")
        print(f"Reversion Signals: {len(signals_reversion)}")
        
        if total_signals > 0:
            print("\n✅ Bollinger Bands Strategy test completed successfully!")
        else:
            print("\n⚠️  No signals generated - check strategy logic")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
