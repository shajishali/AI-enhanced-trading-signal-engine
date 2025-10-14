"""
Spot Trading Setup and Test Script
This script sets up spot trading data and tests the spot trading signal generation
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.utils import timezone
from apps.trading.models import Symbol
from apps.signals.models import TradingType, SpotTradingSignal, SignalType
from apps.signals.services import SignalGenerationService
from apps.data.models import MarketData

def setup_trading_types():
    """Create trading types"""
    print("🔧 Setting up trading types...")
    
    trading_types = [
        ('FUTURES', 'Futures Trading - Short-term leveraged trading'),
        ('SPOT', 'Spot Trading - Long-term cryptocurrency accumulation'),
        ('MARGIN', 'Margin Trading - Leveraged spot trading'),
        ('STAKING', 'Staking - Earn rewards by holding cryptocurrencies'),
    ]
    
    for name, description in trading_types:
        trading_type, created = TradingType.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
        if created:
            print(f"  ✅ Created trading type: {name}")
        else:
            print(f"  ℹ️  Trading type already exists: {name}")

def setup_spot_tradable_symbols():
    """Set up symbols for spot trading"""
    print("🔧 Setting up spot tradable symbols...")
    
    # Major cryptocurrencies suitable for spot trading
    spot_crypto_symbols = [
        {
            'symbol': 'BTC',
            'name': 'Bitcoin',
            'symbol_type': 'CRYPTO',
            'is_crypto': True,
            'is_spot_tradable': True,
            'is_futures_tradable': True,
            'spot_exchange': 'Binance',
            'spot_pair_format': 'BTC/USDT',
            'base_currency': 'BTC',
            'quote_currency': 'USDT',
            'market_cap_rank': 1,
            'circulating_supply': Decimal('19500000'),
            'total_supply': Decimal('21000000'),
            'max_supply': Decimal('21000000'),
        },
        {
            'symbol': 'ETH',
            'name': 'Ethereum',
            'symbol_type': 'CRYPTO',
            'is_crypto': True,
            'is_spot_tradable': True,
            'is_futures_tradable': True,
            'spot_exchange': 'Binance',
            'spot_pair_format': 'ETH/USDT',
            'base_currency': 'ETH',
            'quote_currency': 'USDT',
            'market_cap_rank': 2,
            'circulating_supply': Decimal('120000000'),
            'total_supply': Decimal('120000000'),
            'max_supply': None,
        },
        {
            'symbol': 'SOL',
            'name': 'Solana',
            'symbol_type': 'CRYPTO',
            'is_crypto': True,
            'is_spot_tradable': True,
            'is_futures_tradable': True,
            'spot_exchange': 'Binance',
            'spot_pair_format': 'SOL/USDT',
            'base_currency': 'SOL',
            'quote_currency': 'USDT',
            'market_cap_rank': 5,
            'circulating_supply': Decimal('450000000'),
            'total_supply': Decimal('500000000'),
            'max_supply': Decimal('500000000'),
        },
        {
            'symbol': 'ADA',
            'name': 'Cardano',
            'symbol_type': 'CRYPTO',
            'is_crypto': True,
            'is_spot_tradable': True,
            'is_futures_tradable': True,
            'spot_exchange': 'Binance',
            'spot_pair_format': 'ADA/USDT',
            'base_currency': 'ADA',
            'quote_currency': 'USDT',
            'market_cap_rank': 8,
            'circulating_supply': Decimal('35000000000'),
            'total_supply': Decimal('45000000000'),
            'max_supply': Decimal('45000000000'),
        },
        {
            'symbol': 'DOT',
            'name': 'Polkadot',
            'symbol_type': 'CRYPTO',
            'is_crypto': True,
            'is_spot_tradable': True,
            'is_futures_tradable': True,
            'spot_exchange': 'Binance',
            'spot_pair_format': 'DOT/USDT',
            'base_currency': 'DOT',
            'quote_currency': 'USDT',
            'market_cap_rank': 12,
            'circulating_supply': Decimal('1200000000'),
            'total_supply': Decimal('1200000000'),
            'max_supply': Decimal('1200000000'),
        },
        {
            'symbol': 'AVAX',
            'name': 'Avalanche',
            'symbol_type': 'CRYPTO',
            'is_crypto': True,
            'is_spot_tradable': True,
            'is_futures_tradable': True,
            'spot_exchange': 'Binance',
            'spot_pair_format': 'AVAX/USDT',
            'base_currency': 'AVAX',
            'quote_currency': 'USDT',
            'market_cap_rank': 15,
            'circulating_supply': Decimal('350000000'),
            'total_supply': Decimal('720000000'),
            'max_supply': Decimal('720000000'),
        },
        {
            'symbol': 'LINK',
            'name': 'Chainlink',
            'symbol_type': 'CRYPTO',
            'is_crypto': True,
            'is_spot_tradable': True,
            'is_futures_tradable': True,
            'spot_exchange': 'Binance',
            'spot_pair_format': 'LINK/USDT',
            'base_currency': 'LINK',
            'quote_currency': 'USDT',
            'market_cap_rank': 18,
            'circulating_supply': Decimal('500000000'),
            'total_supply': Decimal('1000000000'),
            'max_supply': Decimal('1000000000'),
        },
        {
            'symbol': 'UNI',
            'name': 'Uniswap',
            'symbol_type': 'CRYPTO',
            'is_crypto': True,
            'is_spot_tradable': True,
            'is_futures_tradable': True,
            'spot_exchange': 'Binance',
            'spot_pair_format': 'UNI/USDT',
            'base_currency': 'UNI',
            'quote_currency': 'USDT',
            'market_cap_rank': 20,
            'circulating_supply': Decimal('600000000'),
            'total_supply': Decimal('1000000000'),
            'max_supply': Decimal('1000000000'),
        },
    ]
    
    for symbol_data in spot_crypto_symbols:
        symbol, created = Symbol.objects.get_or_create(
            symbol=symbol_data['symbol'],
            defaults=symbol_data
        )
        
        if created:
            print(f"  ✅ Created spot tradable symbol: {symbol.symbol}")
        else:
            # Update existing symbol with spot trading fields
            for field, value in symbol_data.items():
                if field != 'symbol':
                    setattr(symbol, field, value)
            symbol.save()
            print(f"  🔄 Updated symbol for spot trading: {symbol.symbol}")

def setup_signal_types():
    """Ensure all required signal types exist"""
    print("🔧 Setting up signal types...")
    
    signal_types = [
        ('BUY', 'Buy Signal', '#28a745'),
        ('SELL', 'Sell Signal', '#dc3545'),
        ('HOLD', 'Hold Signal', '#6c757d'),
        ('STRONG_BUY', 'Strong Buy', '#20c997'),
        ('STRONG_SELL', 'Strong Sell', '#fd7e14'),
    ]
    
    for name, description, color in signal_types:
        signal_type, created = SignalType.objects.get_or_create(
            name=name,
            defaults={'description': description, 'color': color}
        )
        if created:
            print(f"  ✅ Created signal type: {name}")
        else:
            print(f"  ℹ️  Signal type already exists: {name}")

def test_spot_signal_generation():
    """Test spot trading signal generation"""
    print("🧪 Testing spot trading signal generation...")
    
    # Get spot tradable symbols
    spot_symbols = Symbol.objects.filter(
        is_crypto=True,
        is_spot_tradable=True,
        is_active=True
    )[:5]  # Test with first 5 symbols
    
    if not spot_symbols:
        print("  ❌ No spot tradable symbols found!")
        return
    
    print(f"  📊 Testing with {len(spot_symbols)} symbols:")
    for symbol in spot_symbols:
        print(f"    - {symbol.symbol} ({symbol.name})")
    
    # Initialize signal generation service
    signal_service = SignalGenerationService()
    
    total_signals = 0
    spot_signals_count = 0
    
    for symbol in spot_symbols:
        print(f"\n  🔍 Generating signals for {symbol.symbol}...")
        
        try:
            # Generate signals
            signals = signal_service.generate_signals_for_symbol(symbol)
            
            # Count spot signals
            spot_signals = [s for s in signals if s.metadata.get('signal_type') == 'SPOT_TRADING']
            
            print(f"    ✅ Generated {len(signals)} total signals ({len(spot_signals)} spot signals)")
            
            # Display spot signal details
            for signal in spot_signals:
                metadata = signal.metadata
                print(f"      📈 Spot Signal: {signal.signal_type.name}")
                print(f"         Category: {metadata.get('signal_category')}")
                print(f"         Horizon: {metadata.get('investment_horizon')}")
                print(f"         Allocation: {metadata.get('recommended_allocation', 0):.1%}")
                print(f"         DCA: {metadata.get('dca_frequency')}")
                print(f"         Confidence: {signal.confidence_score:.2f}")
                print(f"         Fundamental: {metadata.get('fundamental_score', 0):.2f}")
                print(f"         Technical: {metadata.get('technical_score', 0):.2f}")
                print(f"         Sentiment: {metadata.get('sentiment_score', 0):.2f}")
            
            total_signals += len(signals)
            spot_signals_count += len(spot_signals)
            
        except Exception as e:
            print(f"    ❌ Error generating signals for {symbol.symbol}: {e}")
    
    print(f"\n  📊 Test Results:")
    print(f"    Total signals generated: {total_signals}")
    print(f"    Spot signals generated: {spot_signals_count}")
    print(f"    Success rate: {(spot_signals_count / len(spot_symbols)) * 100:.1f}%")

def display_spot_signals():
    """Display recent spot trading signals"""
    print("\n📈 Recent Spot Trading Signals:")
    
    # Get recent spot trading signals
    recent_signals = SpotTradingSignal.objects.filter(
        is_active=True
    ).order_by('-created_at')[:10]
    
    if not recent_signals:
        print("  No spot trading signals found.")
        return
    
    for signal in recent_signals:
        print(f"\n  🎯 {signal.symbol.symbol} - {signal.signal_category}")
        print(f"     Horizon: {signal.investment_horizon}")
        print(f"     Scores: F={signal.fundamental_score:.2f} T={signal.technical_score:.2f} S={signal.sentiment_score:.2f}")
        print(f"     Overall: {signal.overall_score:.2f} ({signal.confidence_level})")
        print(f"     Allocation: {signal.recommended_allocation:.1%}")
        print(f"     DCA: {signal.dca_frequency}")
        if signal.target_price_1y:
            print(f"     1Y Target: ${signal.target_price_1y:,.2f}")

def main():
    """Main setup and test function"""
    print("🚀 Spot Trading System Setup and Test")
    print("=" * 50)
    
    try:
        # Setup
        setup_trading_types()
        setup_spot_tradable_symbols()
        setup_signal_types()
        
        print("\n" + "=" * 50)
        
        # Test
        test_spot_signal_generation()
        display_spot_signals()
        
        print("\n" + "=" * 50)
        print("✅ Spot Trading System Setup Complete!")
        print("\n📋 Next Steps:")
        print("1. Start Celery workers to enable automatic spot signal generation")
        print("2. Access the signals page to view spot trading signals")
        print("3. Monitor signal performance and adjust strategies as needed")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()




























