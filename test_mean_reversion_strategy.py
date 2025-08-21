#!/usr/bin/env python
"""
Test script for Mean Reversion Strategy
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

from apps.signals.strategies import MeanReversionStrategy
from apps.trading.models import Symbol
from apps.data.models import TechnicalIndicator, MarketData
from apps.signals.models import TradingSignal
from django.utils import timezone
from datetime import timedelta


def create_test_data_price_deviation():
    """Create test data for price deviation from SMA scenario"""
    print("Creating test data for price deviation from SMA scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='DOTUSDT',
        defaults={
            'name': 'Polkadot',
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
    
    # Create test market data - oversold scenario (price below SMA)
    current_time = timezone.now()
    base_price = 7.0
    
    for i in range(25):  # 25 data points
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current) - oversold but starting to recover
            price = 6.30  # Significantly below SMA
            high_price = 6.35
            low_price = 6.25
            volume = 2500000  # High volume for confirmation
        elif i < 3:  # Recent periods - reversal confirmation (upward movement)
            price = 6.20 - (i * 0.1)  # Downward movement (establishing oversold)
            high_price = price + 0.08
            low_price = price - 0.08
            volume = 2000000 + (i * 100000)
        elif i < 10:  # Recent periods - establishing oversold condition
            price = 6.20 + (i * 0.02)  # Slight recovery
            high_price = price + 0.1
            low_price = price - 0.1
            volume = 1500000 + (i * 50000)
        else:  # Earlier periods - building SMA
            price = 7.00 + (i * 0.01)  # Building SMA around 7.0
            high_price = price + 0.15
            low_price = price - 0.15
            volume = 1000000 + (i * 20000)
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.05)),
            high_price=Decimal(str(high_price)),
            low_price=Decimal(str(low_price)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(volume))
        )
    
    # Create SMA indicators
    for i in range(3):
        timestamp = current_time - timedelta(hours=i)
        if i == 0:  # Current SMA
            sma_value = 7.0  # SMA is at 7.0, price at 6.30 (10% below)
        else:  # Previous SMAs
            sma_value = 7.0 + (i * 0.01)
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='SMA',
            period=20,
            value=str(sma_value),
            timestamp=timestamp
        )
    
    print("Created market data for price deviation scenario")
    return symbol


def create_test_data_rsi_reversion():
    """Create test data for RSI mean reversion scenario"""
    print("Creating test data for RSI mean reversion scenario...")
    
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
    
    # Create test market data - RSI oversold with reversal
    current_time = timezone.now()
    base_price = 15.0
    
    for i in range(20):  # 20 data points
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current) - reversal confirmation
            price = 14.2  # Starting to recover
            high_price = 14.3
            low_price = 14.1
            volume = 2200000  # High volume
        elif i == 1:  # 1 period ago
            price = 14.0  # Middle period
            high_price = price + 0.15
            low_price = price - 0.15
            volume = 2080000
        elif i == 2:  # 2 periods ago
            price = 13.8  # Earlier period (lowest)
            high_price = price + 0.15
            low_price = price - 0.15
            volume = 2160000
        elif i < 8:  # Recent periods - RSI oversold
            price = 13.5 + (i * 0.1)  # Building oversold condition
            high_price = price + 0.2
            low_price = price - 0.2
            volume = 1800000 + (i * 40000)
        else:  # Earlier periods - establishing base
            price = 15.0 + (i * 0.02)  # Building base around 15.0
            high_price = price + 0.25
            low_price = price - 0.25
            volume = 1200000 + (i * 30000)
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.1)),
            high_price=Decimal(str(high_price)),
            low_price=Decimal(str(low_price)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(volume))
        )
    
    # Create RSI indicators
    for i in range(3):
        timestamp = current_time - timedelta(hours=i)
        if i == 0:  # Current RSI
            rsi_value = 35.0  # RSI recovering from oversold
        else:  # Previous RSIs
            rsi_value = 25.0 + (i * 5.0)  # Was oversold, now recovering
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='RSI',
            period=14,
            value=str(rsi_value),
            timestamp=timestamp
        )
    
    # Create SMA indicators (needed for price deviation check)
    for i in range(3):
        timestamp = current_time - timedelta(hours=i)
        if i == 0:  # Current SMA
            sma_value = 15.0  # SMA is at 15.0, price at 14.2 (5.3% below)
        else:  # Previous SMAs
            sma_value = 15.0 + (i * 0.01)
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='SMA',
            period=20,
            value=Decimal(str(sma_value)),
            timestamp=timestamp
        )
    
    print("Created market data for RSI mean reversion scenario")
    return symbol


def create_test_data_bollinger_bands_reversion():
    """Create test data for Bollinger Bands mean reversion scenario"""
    print("Creating test data for Bollinger Bands mean reversion scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='UNIUSDT',
        defaults={
            'name': 'Uniswap',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    # Clear existing data
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    MarketData.objects.filter(symbol=symbol).delete()
    
    # Create test market data - price touching lower Bollinger Band
    current_time = timezone.now()
    base_price = 5.0
    
    for i in range(22):  # 22 data points
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current) - touching lower band
            price = 4.45  # At lower Bollinger Band
            high_price = 4.50
            low_price = 4.40
            volume = 1800000  # High volume for confirmation
        elif i == 1:  # 1 period ago
            price = 4.35  # Middle period
            high_price = price + 0.08
            low_price = price - 0.08
            volume = 1660000
        elif i == 2:  # 2 periods ago
            price = 4.25  # Earlier period (lowest)
            high_price = price + 0.08
            low_price = price - 0.08
            volume = 1720000
        elif i < 10:  # Recent periods - approaching lower band
            price = 4.60 + (i * 0.02)  # Moving toward lower band
            high_price = price + 0.1
            low_price = price - 0.1
            volume = 1400000 + (i * 30000)
        else:  # Earlier periods - establishing base
            price = 5.00 + (i * 0.01)  # Building base around 5.0
            high_price = price + 0.15
            low_price = price - 0.15
            volume = 1000000 + (i * 20000)
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.05)),
            high_price=Decimal(str(high_price)),
            low_price=Decimal(str(low_price)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(volume))
        )
    
    # Create Bollinger Bands indicators (separate upper, middle, lower)
    for i in range(3):
        timestamp = current_time - timedelta(hours=i)
        if i == 0:  # Current BB
            upper_value = 5.5
            middle_value = 5.0  # Middle band (mean)
            lower_value = 4.45   # Lower band (price is touching this)
        else:  # Previous BBs
            upper_value = 5.5 + (i * 0.01)
            middle_value = 5.0 + (i * 0.01)
            lower_value = 4.45 + (i * 0.01)
        
        # Create upper band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_UPPER',
            period=20,
            value=Decimal(str(upper_value)),
            timestamp=timestamp
        )
        
        # Create middle band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_MIDDLE',
            period=20,
            value=Decimal(str(middle_value)),
            timestamp=timestamp
        )
        
        # Create lower band indicator
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='BB_LOWER',
            period=20,
            value=Decimal(str(lower_value)),
            timestamp=timestamp
        )
    
    # Create SMA indicators (needed for price deviation check)
    for i in range(3):
        timestamp = current_time - timedelta(hours=i)
        if i == 0:  # Current SMA
            sma_value = 5.0  # SMA is at 5.0, price at 4.45 (11% below)
        else:  # Previous SMAs
            sma_value = 5.0 + (i * 0.01)
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='SMA',
            period=20,
            value=Decimal(str(sma_value)),
            timestamp=timestamp
        )
    
    print("Created market data for Bollinger Bands mean reversion scenario")
    return symbol


def create_test_data_stochastic_reversion():
    """Create test data for Stochastic oscillator mean reversion scenario"""
    print("Creating test data for Stochastic oscillator mean reversion scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='AAVEUSDT',
        defaults={
            'name': 'Aave',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    # Clear existing data
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    MarketData.objects.filter(symbol=symbol).delete()
    
    # Create test market data - Stochastic oversold with reversal
    current_time = timezone.now()
    base_price = 80.0
    
    for i in range(18):  # 18 data points
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current) - reversal confirmation
            price = 78.5  # Starting to recover
            high_price = 78.8
            low_price = 78.2
            volume = 1600000  # High volume
        elif i < 3:  # Recent periods - reversal confirmation
            price = 77.5 + (i * 0.5)  # Upward movement
            high_price = price + 1.0
            low_price = price - 1.0
            volume = 1500000 + (i * 50000)
        elif i < 8:  # Recent periods - Stochastic oversold
            price = 75.0 + (i * 0.5)  # Building oversold condition
            high_price = price + 1.5
            low_price = price - 1.5
            volume = 1300000 + (i * 40000)
        else:  # Earlier periods - establishing base
            price = 80.0 + (i * 0.1)  # Building base around 80.0
            high_price = price + 2.0
            low_price = price - 2.0
            volume = 1000000 + (i * 30000)
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.5)),
            high_price=Decimal(str(high_price)),
            low_price=Decimal(str(low_price)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(volume))
        )
    
    # Create Stochastic indicators
    for i in range(3):
        timestamp = current_time - timedelta(hours=i)
        if i == 0:  # Current Stochastic
            stoch_value = 25.0  # Stochastic recovering from oversold
        else:  # Previous Stochastics
            stoch_value = 15.0 + (i * 5.0)  # Was oversold, now recovering
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='STOCH',
            period=14,
            value=str(stoch_value),
            timestamp=timestamp
        )
    
    # Create SMA indicators (needed for price deviation check)
    for i in range(3):
        timestamp = current_time - timedelta(hours=i)
        if i == 0:  # Current SMA
            sma_value = 80.0  # SMA is at 80.0, price at 78.5 (1.9% below)
        else:  # Previous SMAs
            sma_value = 80.0 + (i * 0.01)
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='SMA',
            period=20,
            value=Decimal(str(sma_value)),
            timestamp=timestamp
        )
    
    print("Created market data for Stochastic mean reversion scenario")
    return symbol


def test_strategy(symbol, scenario_name):
    """Test the Mean Reversion Strategy"""
    print(f"\nTesting Mean Reversion Strategy for {symbol.symbol} ({scenario_name})...")
    
    # Initialize strategy
    strategy = MeanReversionStrategy()
    
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
    print("🚀 Testing Mean Reversion Strategy")
    print("=" * 50)
    
    total_signals = 0
    
    try:
        # Test 1: Price deviation from SMA scenario
        print("\n1. TESTING PRICE DEVIATION FROM SMA SCENARIO")
        print("-" * 40)
        symbol_ma = create_test_data_price_deviation()
        signals_ma = test_strategy(symbol_ma, "Price Deviation from SMA")
        total_signals += len(signals_ma)
        cleanup_test_data(symbol_ma)
        
        # Test 2: RSI mean reversion scenario
        print("\n2. TESTING RSI MEAN REVERSION SCENARIO")
        print("-" * 40)
        symbol_rsi = create_test_data_rsi_reversion()
        signals_rsi = test_strategy(symbol_rsi, "RSI Mean Reversion")
        total_signals += len(signals_rsi)
        cleanup_test_data(symbol_rsi)
        
        # Test 3: Bollinger Bands mean reversion scenario
        print("\n3. TESTING BOLLINGER BANDS MEAN REVERSION SCENARIO")
        print("-" * 40)
        symbol_bb = create_test_data_bollinger_bands_reversion()
        signals_bb = test_strategy(symbol_bb, "Bollinger Bands Mean Reversion")
        total_signals += len(signals_bb)
        cleanup_test_data(symbol_bb)
        
        # Test 4: Stochastic oscillator mean reversion scenario
        print("\n4. TESTING STOCHASTIC OSCILLATOR MEAN REVERSION SCENARIO")
        print("-" * 40)
        symbol_stoch = create_test_data_stochastic_reversion()
        signals_stoch = test_strategy(symbol_stoch, "Stochastic Mean Reversion")
        total_signals += len(signals_stoch)
        cleanup_test_data(symbol_stoch)
        
        # Summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY:")
        print(f"Total Signals Generated: {total_signals}")
        print(f"Price Deviation Signals: {len(signals_ma)}")
        print(f"RSI Mean Reversion Signals: {len(signals_rsi)}")
        print(f"Bollinger Bands Signals: {len(signals_bb)}")
        print(f"Stochastic Signals: {len(signals_stoch)}")
        
        if total_signals > 0:
            print("\n✅ Mean Reversion Strategy test completed successfully!")
        else:
            print("\n⚠️  No signals generated - check strategy logic")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
