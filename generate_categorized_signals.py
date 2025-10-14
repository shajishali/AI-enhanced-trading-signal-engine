"""
Generate Signals for Properly Categorized Coins
This script generates spot signals for spot coins and futures signals for all crypto coins
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.trading.models import Symbol
from apps.signals.services import SignalGenerationService
from apps.signals.models import SpotTradingSignal, TradingSignal

def generate_signals_for_categorized_coins():
    """Generate signals for properly categorized coins"""
    print("🚀 Generating Signals for Categorized Crypto Coins")
    print("=" * 70)
    
    # Get categorized symbols
    spot_symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True, is_spot_tradable=True)
    futures_symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True, is_futures_tradable=True)
    all_crypto_symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True)
    
    print(f"📊 Symbol Categories:")
    print(f"   • Spot tradable: {spot_symbols.count()}")
    print(f"   • Futures tradable: {futures_symbols.count()}")
    print(f"   • All crypto symbols: {all_crypto_symbols.count()}")
    
    # Initialize signal generation service
    signal_service = SignalGenerationService()
    
    print(f"\n🔄 Generating signals...")
    print("-" * 70)
    
    # Generate signals for all crypto symbols (this will generate both futures and spot based on categorization)
    total_signals_generated = 0
    successful_symbols = 0
    failed_symbols = 0
    
    for i, symbol in enumerate(all_crypto_symbols, 1):
        try:
            print(f"[{i:3d}/{all_crypto_symbols.count()}] Processing {symbol.symbol} ({symbol.name})...")
            
            # Generate signals for this symbol
            signals = signal_service.generate_signals_for_symbol(symbol)
            
            if signals:
                total_signals_generated += len(signals)
                successful_symbols += 1
                print(f"    ✅ Generated {len(signals)} signals")
            else:
                print(f"    ⚪ No signals generated")
            
        except Exception as e:
            failed_symbols += 1
            print(f"    ❌ Error: {str(e)[:100]}...")
    
    print("\n" + "=" * 70)
    print("📊 GENERATION SUMMARY")
    print("=" * 70)
    print(f"Total symbols processed: {all_crypto_symbols.count()}")
    print(f"Successful symbols: {successful_symbols}")
    print(f"Failed symbols: {failed_symbols}")
    print(f"Total signals generated: {total_signals_generated}")
    print(f"Success rate: {(successful_symbols/all_crypto_symbols.count())*100:.1f}%")
    
    # Show signal counts by type
    spot_signals = SpotTradingSignal.objects.filter(is_active=True).count()
    futures_signals = TradingSignal.objects.filter(is_active=True, metadata__signal_type='FUTURES_TRADING').count()
    
    print(f"\n📈 SIGNAL BREAKDOWN:")
    print(f"   • Spot signals: {spot_signals}")
    print(f"   • Futures signals: {futures_signals}")
    
    # Show recent spot signals
    recent_spot_signals = SpotTradingSignal.objects.filter(is_active=True).order_by('-analyzed_at')[:10]
    
    if recent_spot_signals:
        print(f"\n🪙 Recent Spot Signals ({recent_spot_signals.count()}):")
        print("-" * 70)
        for signal in recent_spot_signals:
            print(f"• {signal.symbol.symbol}: {signal.signal_category} ({signal.investment_horizon})")
            print(f"  Scores: F={signal.fundamental_score:.2f} T={signal.technical_score:.2f} S={signal.sentiment_score:.2f}")
            print(f"  Overall: {signal.overall_score:.2f} | Allocation: {signal.recommended_allocation:.1%}")
            print(f"  Analyzed: {signal.analyzed_at.strftime('%Y-%m-%d %H:%M')} (SL Time)")
            print()
    
    # Show recent futures signals
    recent_futures_signals = TradingSignal.objects.filter(is_active=True).order_by('-analyzed_at')[:10]
    
    if recent_futures_signals:
        print(f"\n⚡ Recent Futures Signals ({recent_futures_signals.count()}):")
        print("-" * 70)
        for signal in recent_futures_signals:
            print(f"• {signal.symbol.symbol}: {signal.signal_type} - {signal.action}")
            print(f"  Confidence: {signal.confidence_score:.2f} | Price: ${signal.current_price}")
            print(f"  Analyzed: {signal.analyzed_at.strftime('%Y-%m-%d %H:%M')} (SL Time)")
            print()
    
    print("✅ Signal generation completed!")
    print(f"🌐 View results:")
    print(f"   • Spot signals: http://localhost:8000/signals/spot/")
    print(f"   • All signals: http://localhost:8000/signals/")

def main():
    """Main function"""
    try:
        generate_signals_for_categorized_coins()
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()




























