"""
Generate Spot Signals for All Crypto Symbols
This script generates spot trading signals for all available cryptocurrency symbols
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
from apps.signals.models import SpotTradingSignal

def generate_spot_signals_for_all_crypto():
    """Generate spot signals for all crypto symbols"""
    print("🚀 Generating Spot Signals for All Crypto Symbols")
    print("=" * 60)
    
    # Get all crypto symbols
    crypto_symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True)
    total_symbols = crypto_symbols.count()
    
    print(f"📊 Found {total_symbols} crypto symbols to analyze")
    
    # Initialize signal generation service
    signal_service = SignalGenerationService()
    
    total_signals_generated = 0
    successful_symbols = 0
    failed_symbols = 0
    
    print(f"\n🔄 Starting signal generation for {total_symbols} symbols...")
    print("-" * 60)
    
    for i, symbol in enumerate(crypto_symbols, 1):
        try:
            print(f"[{i:3d}/{total_symbols}] Processing {symbol.symbol} ({symbol.name})...")
            
            # Generate signals for this symbol
            signals = signal_service.generate_signals_for_symbol(symbol)
            
            # Count spot signals
            spot_signals = [s for s in signals if s.metadata.get('signal_type') == 'SPOT_TRADING']
            
            if spot_signals:
                total_signals_generated += len(spot_signals)
                successful_symbols += 1
                print(f"    ✅ Generated {len(spot_signals)} spot signals")
            else:
                print(f"    ⚪ No spot signals generated")
            
        except Exception as e:
            failed_symbols += 1
            print(f"    ❌ Error: {str(e)[:100]}...")
    
    print("\n" + "=" * 60)
    print("📊 GENERATION SUMMARY")
    print("=" * 60)
    print(f"Total symbols processed: {total_symbols}")
    print(f"Successful symbols: {successful_symbols}")
    print(f"Failed symbols: {failed_symbols}")
    print(f"Total spot signals generated: {total_signals_generated}")
    print(f"Success rate: {(successful_symbols/total_symbols)*100:.1f}%")
    
    # Show recent spot signals
    recent_signals = SpotTradingSignal.objects.filter(is_active=True).order_by('-created_at')[:10]
    
    if recent_signals:
        print(f"\n📈 Recent Spot Signals ({recent_signals.count()}):")
        print("-" * 60)
        for signal in recent_signals:
            print(f"• {signal.symbol.symbol}: {signal.signal_category} ({signal.investment_horizon})")
            print(f"  Scores: F={signal.fundamental_score:.2f} T={signal.technical_score:.2f} S={signal.sentiment_score:.2f}")
            print(f"  Overall: {signal.overall_score:.2f} | Allocation: {signal.recommended_allocation:.1%}")
            print(f"  DCA: {signal.dca_frequency} | Created: {signal.created_at}")
            print()
    
    print("✅ Spot signal generation completed!")
    print(f"🌐 View results at: http://localhost:8000/signals/spot/")

def main():
    """Main function"""
    try:
        generate_spot_signals_for_all_crypto()
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
































































