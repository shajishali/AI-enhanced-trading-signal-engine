#!/usr/bin/env python
"""
Test script for Moving Average Crossover Strategy
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

from apps.signals.strategies import MovingAverageCrossoverStrategy
from apps.trading.models import Symbol
from apps.data.models import TechnicalIndicator, MarketData
from apps.signals.models import TradingSignal
from django.utils import timezone
from datetime import timedelta


def create_test_data():
    """Create test data for the strategy with actual crossover scenario"""
    print("Creating test data...")
    
    # Get or create a test symbol
    symbol, created = Symbol.objects.get_or_create(
        symbol='BTCUSDT',
        defaults={
            'name': 'Bitcoin',
            'exchange': 'Binance',
            'is_active': True
        }
    )
    
    if created:
        print(f"Created symbol: {symbol.symbol}")
    else:
        print(f"Using existing symbol: {symbol.symbol}")
    
    # Create test market data
    current_time = timezone.now()
    base_price = 50000.0
    
    for i in range(60):  # 60 data points
        timestamp = current_time - timedelta(hours=i)
        price = base_price + (i * 100)  # Increasing price trend
        
        MarketData.objects.get_or_create(
            symbol=symbol,
            timestamp=timestamp,
            defaults={
                'open_price': Decimal(str(price)),
                'high_price': Decimal(str(price + 50)),
                'low_price': Decimal(str(price - 50)),
                'close_price': Decimal(str(price)),
                'volume': Decimal(str(1000000 + i * 10000))
            }
        )
    
    print("Created market data")
    
    # Clear existing indicators for this symbol
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    
    # Create test technical indicators with CROSSOVER scenario
    # We need to create a scenario where 20 SMA crosses above 50 SMA
    
    # 20 SMA - create crossover scenario
    for i in range(20):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            sma_value = base_price + 1500  # 20 SMA above 50 SMA
        elif i == 1:  # Previous period
            sma_value = base_price + 1200  # 20 SMA below 50 SMA (for crossover)
        else:  # Earlier periods
            sma_value = base_price + (i * 50)  # Gradual increase
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='SMA',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(sma_value)),
            source_id=1
        )
    
    # 50 SMA - slower moving average
    for i in range(50):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            sma_value = base_price + 1400  # 50 SMA below 20 SMA
        elif i == 1:  # Previous period
            sma_value = base_price + 1250  # 50 SMA above 20 SMA (for crossover)
        else:  # Earlier periods
            sma_value = base_price + (i * 40)  # Gradual increase
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='SMA',
            period=50,
            timestamp=timestamp,
            value=Decimal(str(sma_value)),
            source_id=1
        )
    
    # 10 EMA - create crossover scenario
    for i in range(20):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            ema_value = base_price + 1600  # 10 EMA above 20 EMA
        elif i == 1:  # Previous period
            ema_value = base_price + 1300  # 10 EMA below 20 EMA (for crossover)
        else:  # Earlier periods
            ema_value = base_price + (i * 60)  # Gradual increase
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='EMA',
            period=10,
            timestamp=timestamp,
            value=Decimal(str(ema_value)),
            source_id=1
        )
    
    # 20 EMA - slower exponential moving average
    for i in range(20):
        timestamp = current_time - timedelta(hours=i)
        
        if i == 0:  # Most recent (current)
            ema_value = base_price + 1450  # 20 EMA below 10 EMA
        elif i == 1:  # Previous period
            ema_value = base_price + 1350  # 20 EMA above 10 EMA (for crossover)
        else:  # Earlier periods
            ema_value = base_price + (i * 50)  # Gradual increase
        
        TechnicalIndicator.objects.create(
            symbol=symbol,
            indicator_type='EMA',
            period=20,
            timestamp=timestamp,
            value=Decimal(str(ema_value)),
            source_id=1
        )
    
    print("Created technical indicators with crossover scenarios")
    
    # Debug: Print the values to verify crossover
    print("\nDebug: Latest indicator values:")
    latest_20_sma = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='SMA', period=20
    ).order_by('-timestamp').first()
    latest_50_sma = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='SMA', period=50
    ).order_by('-timestamp').first()
    latest_10_ema = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='EMA', period=10
    ).order_by('-timestamp').first()
    latest_20_ema = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='EMA', period=20
    ).order_by('-timestamp').first()
    
    if latest_20_sma and latest_50_sma:
        print(f"20 SMA: {latest_20_sma.value:.2f}")
        print(f"50 SMA: {latest_50_sma.value:.2f}")
        print(f"SMA Diff: {float(latest_20_sma.value) - float(latest_50_sma.value):.2f}")
    
    if latest_10_ema and latest_20_ema:
        print(f"10 EMA: {latest_10_ema.value:.2f}")
        print(f"20 EMA: {latest_20_ema.value:.2f}")
        print(f"EMA Diff: {float(latest_10_ema.value) - float(latest_20_ema.value):.2f}")
    
    # Debug: Check if we have enough historical data
    print("\nDebug: Historical data check:")
    sma_20_count = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='SMA', period=20
    ).count()
    sma_50_count = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='SMA', period=50
    ).count()
    ema_10_count = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='EMA', period=10
    ).count()
    ema_20_count = TechnicalIndicator.objects.filter(
        symbol=symbol, indicator_type='EMA', period=20
    ).count()
    
    print(f"20 SMA indicators: {sma_20_count}")
    print(f"50 SMA indicators: {sma_50_count}")
    print(f"10 EMA indicators: {ema_10_count}")
    print(f"20 EMA indicators: {ema_20_count}")
    
    # Check if we have at least 2 data points for crossover detection
    if sma_20_count >= 2 and sma_50_count >= 2:
        # Get previous values for crossover check
        prev_20_sma = TechnicalIndicator.objects.filter(
            symbol=symbol, indicator_type='SMA', period=20
        ).order_by('-timestamp')[1]  # Second most recent
        prev_50_sma = TechnicalIndicator.objects.filter(
            symbol=symbol, indicator_type='SMA', period=50
        ).order_by('-timestamp')[1]  # Second most recent
        
        current_diff = float(latest_20_sma.value) - float(latest_50_sma.value)
        prev_diff = float(prev_20_sma.value) - float(prev_50_sma.value)
        
        print(f"\nCrossover Check:")
        print(f"Previous 20 SMA: {prev_20_sma.value:.2f}")
        print(f"Previous 50 SMA: {prev_50_sma.value:.2f}")
        print(f"Previous Diff: {prev_diff:.2f}")
        print(f"Current Diff: {current_diff:.2f}")
        print(f"Crossover detected: {prev_diff <= 0 and current_diff > 0}")
    
    return symbol


def test_strategy(symbol):
    """Test the Moving Average Crossover Strategy"""
    print(f"\nTesting Moving Average Crossover Strategy for {symbol.symbol}...")
    
    # Initialize strategy
    strategy = MovingAverageCrossoverStrategy()
    
    # Generate signals
    signals = strategy.generate_signals(symbol)
    
    print(f"Generated {len(signals)} signals")
    
    # Display signals
    for i, signal in enumerate(signals, 1):
        print(f"\nSignal {i}:")
        print(f"  Type: {signal.signal_type.name}")
        print(f"  Strength: {signal.strength}")
        print(f"  Confidence: {signal.confidence_score:.2f}")
        print(f"  Entry Price: ${signal.entry_price:,.2f}")
        print(f"  Target Price: ${signal.target_price:,.2f}")
        print(f"  Stop Loss: ${signal.stop_loss:,.2f}")
        print(f"  Risk/Reward: {signal.risk_reward_ratio:.2f}")
        print(f"  Quality Score: {signal.quality_score:.2f}")
        print(f"  Notes: {signal.notes}")
    
    return signals


def cleanup_test_data(symbol):
    """Clean up test data"""
    print("\nCleaning up test data...")
    
    # Delete test signals
    TradingSignal.objects.filter(symbol=symbol).delete()
    
    # Delete test indicators
    TechnicalIndicator.objects.filter(symbol=symbol).delete()
    
    # Delete test market data
    MarketData.objects.filter(symbol=symbol).delete()
    
    print("Test data cleaned up")


def main():
    """Main test function"""
    print("🚀 Testing Moving Average Crossover Strategy")
    print("=" * 50)
    
    try:
        # Create test data
        symbol = create_test_data()
        
        # Test strategy
        signals = test_strategy(symbol)
        
        # Summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY:")
        print(f"Symbol: {symbol.symbol}")
        print(f"Signals Generated: {len(signals)}")
        
        if signals:
            buy_signals = [s for s in signals if 'BUY' in s.signal_type.name]
            sell_signals = [s for s in signals if 'SELL' in s.signal_type.name]
            print(f"Buy Signals: {len(buy_signals)}")
            print(f"Sell Signals: {len(sell_signals)}")
            
            avg_confidence = sum(s.confidence_score for s in signals) / len(signals)
            print(f"Average Confidence: {avg_confidence:.2f}")
            
            print("\n✅ Strategy test completed successfully!")
        else:
            print("\n⚠️  No signals generated - check data and strategy logic")
        
        # Clean up
        cleanup_test_data(symbol)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
