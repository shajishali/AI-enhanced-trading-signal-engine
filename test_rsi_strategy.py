#!/usr/bin/env python
"""
Test script for RSI Strategy
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

from apps.signals.strategies import RSIStrategy
from apps.trading.models import Symbol
from apps.data.models import TechnicalIndicator, MarketData
from apps.signals.models import TradingSignal
from django.utils import timezone
from datetime import timedelta


def create_test_data_oversold():
    """Create test data for oversold RSI scenario"""
    print("Creating test data for oversold scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='ETHUSDT',
        defaults={
            'name': 'Ethereum',
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
    base_price = 3000.0
    
    for i in range(20):  # 20 data points
        timestamp = current_time - timedelta(hours=i)
        # Declining price trend
        price = base_price - (i * 20)  # Price going down
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price + 10)),
            high_price=Decimal(str(price + 15)),
            low_price=Decimal(str(price - 5)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(1000000 + i * 10000))
        )
    
    print("Created market data")
    
    # Create RSI indicators - oversold scenario
    for i in range(15):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            rsi_value = 25.0  # Oversold RSI
        elif i == 1:  # Previous period
            rsi_value = 28.0  # Still oversold but higher (turning up)
        else:  # Earlier periods - gradually increasing RSI
            rsi_value = 35.0 + (i * 2)  # RSI getting more oversold over time
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='RSI',
            period=14,
            timestamp=timestamp,
            value=Decimal(str(rsi_value)),
            source_id=1
        )
    
    print("Created RSI indicators (oversold scenario)")
    return symbol


def create_test_data_overbought():
    """Create test data for overbought RSI scenario"""
    print("Creating test data for overbought scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='ADAUSDT',
        defaults={
            'name': 'Cardano',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    # Clear existing data
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    MarketData.objects.filter(symbol=symbol).delete()
    
    # Create test market data
    current_time = timezone.now()
    base_price = 0.50
    
    for i in range(20):  # 20 data points
        timestamp = current_time - timedelta(hours=i)
        # Rising price trend
        price = base_price + (i * 0.01)  # Price going up
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.005)),
            high_price=Decimal(str(price + 0.01)),
            low_price=Decimal(str(price - 0.01)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(1000000 + i * 10000))
        )
    
    print("Created market data")
    
    # Create RSI indicators - overbought scenario
    for i in range(15):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            rsi_value = 75.0  # Overbought RSI
        elif i == 1:  # Previous period
            rsi_value = 77.0  # Even more overbought (turning down)
        else:  # Earlier periods - gradually decreasing RSI
            rsi_value = 65.0 - (i * 2)  # RSI getting more overbought over time
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='RSI',
            period=14,
            timestamp=timestamp,
            value=Decimal(str(rsi_value)),
            source_id=1
        )
    
    print("Created RSI indicators (overbought scenario)")
    return symbol


def create_test_data_divergence():
    """Create test data for RSI divergence scenario"""
    print("Creating test data for bullish divergence scenario...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='DOGEUSDT',
        defaults={
            'name': 'Dogecoin',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    # Clear existing data
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    MarketData.objects.filter(symbol=symbol).delete()
    
    # Create test market data for bullish divergence
    # Price makes lower lows, but RSI makes higher lows
    current_time = timezone.now()
    base_price = 0.08
    
    # Create price data with lower lows
    price_data = [
        0.080,  # Current (recent low)
        0.082,
        0.081,
        0.079,  # Previous low (higher than current)
        0.083,
        0.085,
        0.084,
        0.083,
        0.082,
        0.081
    ]
    
    for i, price in enumerate(price_data):
        timestamp = current_time - timedelta(hours=i)
        
        MarketData.objects.create(
            symbol=symbol,
            timestamp=timestamp,
            open_price=Decimal(str(price - 0.001)),
            high_price=Decimal(str(price + 0.002)),
            low_price=Decimal(str(price - 0.002)),
            close_price=Decimal(str(price)),
            volume=Decimal(str(1000000 + i * 10000))
        )
    
    print("Created market data for divergence")
    
    # Create RSI indicators for bullish divergence
    # RSI makes higher lows while price makes lower lows
    rsi_data = [
        32.0,  # Current RSI low (higher than previous)
        35.0,
        33.0,
        30.0,  # Previous RSI low (lower than current) 
        38.0,
        42.0,
        40.0,
        38.0,
        35.0,
        33.0
    ]
    
    for i, rsi_value in enumerate(rsi_data):
        timestamp = current_time - timedelta(hours=i)
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='RSI',
            period=14,
            timestamp=timestamp,
            value=Decimal(str(rsi_value)),
            source_id=1
        )
    
    print("Created RSI indicators (bullish divergence scenario)")
    return symbol


def test_strategy(symbol, scenario_name):
    """Test the RSI Strategy"""
    print(f"\nTesting RSI Strategy for {symbol.symbol} ({scenario_name})...")
    
    # Initialize strategy
    strategy = RSIStrategy()
    
    # Debug: Print RSI values
    rsi_indicators = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='RSI', period=14
    ).order_by('-timestamp')[:5]
    
    print(f"\nDebug: Latest RSI values:")
    for i, rsi in enumerate(rsi_indicators):
        print(f"  RSI[{i}]: {rsi.value:.1f}")
    
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
    print("🚀 Testing RSI Strategy")
    print("=" * 50)
    
    total_signals = 0
    
    try:
        # Test 1: Oversold scenario
        print("\n1. TESTING OVERSOLD SCENARIO")
        print("-" * 30)
        symbol_oversold = create_test_data_oversold()
        signals_oversold = test_strategy(symbol_oversold, "Oversold")
        total_signals += len(signals_oversold)
        cleanup_test_data(symbol_oversold)
        
        # Test 2: Overbought scenario
        print("\n2. TESTING OVERBOUGHT SCENARIO")
        print("-" * 30)
        symbol_overbought = create_test_data_overbought()
        signals_overbought = test_strategy(symbol_overbought, "Overbought")
        total_signals += len(signals_overbought)
        cleanup_test_data(symbol_overbought)
        
        # Test 3: Divergence scenario
        print("\n3. TESTING DIVERGENCE SCENARIO")
        print("-" * 30)
        symbol_divergence = create_test_data_divergence()
        signals_divergence = test_strategy(symbol_divergence, "Bullish Divergence")
        total_signals += len(signals_divergence)
        cleanup_test_data(symbol_divergence)
        
        # Summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY:")
        print(f"Total Signals Generated: {total_signals}")
        print(f"Oversold Signals: {len(signals_oversold)}")
        print(f"Overbought Signals: {len(signals_overbought)}")
        print(f"Divergence Signals: {len(signals_divergence)}")
        
        if total_signals > 0:
            print("\n✅ RSI Strategy test completed successfully!")
        else:
            print("\n⚠️  No signals generated - check strategy logic")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
