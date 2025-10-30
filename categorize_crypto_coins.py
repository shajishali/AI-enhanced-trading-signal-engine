"""
Categorize Crypto Coins for Spot and Futures Trading
This script analyzes all crypto symbols and categorizes them for spot/futures trading
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.trading.models import Symbol

def categorize_crypto_coins():
    """Categorize all crypto coins for spot and futures trading"""
    print("🔍 Categorizing Crypto Coins for Spot and Futures Trading")
    print("=" * 70)
    
    # Get all crypto symbols
    crypto_symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True)
    total_symbols = crypto_symbols.count()
    
    print(f"📊 Found {total_symbols} crypto symbols to categorize")
    
    # Major cryptocurrencies that are typically available for both spot and futures
    major_cryptos = {
        'BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'LINK', 'UNI', 'AVAX', 'MATIC', 'ATOM',
        'ALGO', 'XRP', 'LTC', 'BCH', 'EOS', 'TRX', 'XLM', 'VET', 'FIL', 'ICP',
        'AAVE', 'COMP', 'MKR', 'SNX', 'YFI', 'SUSHI', 'CRV', '1INCH', 'BAL', 'LRC',
        'ZEC', 'DASH', 'XMR', 'ETC', 'NEO', 'QTUM', 'ZRX', 'BAT', 'REP', 'KNC',
        'MANA', 'SAND', 'AXS', 'ENJ', 'GALA', 'CHZ', 'FLOW', 'THETA', 'FTM', 'NEAR',
        'LUNA', 'UST', 'DOGE', 'SHIB', 'PEPE', 'FLOKI', 'BONK', 'WIF', 'BOME', 'POPCAT'
    }
    
    # DeFi tokens (usually spot only)
    defi_tokens = {
        'UNI', 'AAVE', 'COMP', 'MKR', 'SNX', 'YFI', 'SUSHI', 'CRV', '1INCH', 'BAL',
        'LRC', 'ZRX', 'BAT', 'REP', 'KNC', 'CAKE', 'PCS', 'PANCAKE', 'JUP', 'RAY'
    }
    
    # Layer 1 blockchains (usually both spot and futures)
    layer1_tokens = {
        'BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'AVAX', 'MATIC', 'ATOM', 'ALGO', 'XRP',
        'LTC', 'BCH', 'EOS', 'TRX', 'XLM', 'VET', 'FIL', 'ICP', 'FTM', 'NEAR',
        'LUNA', 'UST', 'APT', 'SUI', 'SEI', 'INJ', 'TIA', 'ARB', 'OP', 'BASE'
    }
    
    # Meme coins (usually spot only)
    meme_coins = {
        'DOGE', 'SHIB', 'PEPE', 'FLOKI', 'BONK', 'WIF', 'BOME', 'POPCAT', 'MYRO',
        'MEW', 'CAT', 'FARTCOIN', 'WOJAK', 'MEME', 'TURBO', 'SPONGE'
    }
    
    # Gaming/NFT tokens (usually spot only)
    gaming_tokens = {
        'MANA', 'SAND', 'AXS', 'ENJ', 'GALA', 'CHZ', 'FLOW', 'THETA', 'ILV',
        'SLP', 'GMT', 'STEPN', 'APE', 'LOOKS', 'BLUR', 'IMX', 'GODS'
    }
    
    spot_only_count = 0
    futures_only_count = 0
    both_count = 0
    
    print(f"\n🔄 Categorizing {total_symbols} symbols...")
    print("-" * 70)
    
    for symbol in crypto_symbols:
        symbol_name = symbol.symbol.upper()
        
        # Determine trading capabilities
        is_spot = False
        is_futures = False
        
        # Major cryptos and Layer 1 tokens can trade both spot and futures
        if symbol_name in major_cryptos or symbol_name in layer1_tokens:
            is_spot = True
            is_futures = True
        
        # DeFi tokens, meme coins, and gaming tokens are usually spot only
        elif (symbol_name in defi_tokens or 
              symbol_name in meme_coins or 
              symbol_name in gaming_tokens):
            is_spot = True
            is_futures = False
        
        # Everything else defaults to futures only (for short-term trading)
        else:
            is_spot = False
            is_futures = True
        
        # Update the symbol
        symbol.is_spot_tradable = is_spot
        symbol.is_futures_tradable = is_futures
        symbol.save()
        
        # Count categories
        if is_spot and is_futures:
            both_count += 1
            category = "BOTH"
        elif is_spot:
            spot_only_count += 1
            category = "SPOT"
        else:
            futures_only_count += 1
            category = "FUTURES"
        
        print(f"{symbol.symbol:8} | {symbol.name:20} | {category}")
    
    print("\n" + "=" * 70)
    print("📊 CATEGORIZATION SUMMARY")
    print("=" * 70)
    print(f"Total crypto symbols: {total_symbols}")
    print(f"Spot only: {spot_only_count}")
    print(f"Futures only: {futures_only_count}")
    print(f"Both spot and futures: {both_count}")
    print(f"Spot tradable total: {spot_only_count + both_count}")
    print(f"Futures tradable total: {futures_only_count + both_count}")
    
    # Show examples from each category
    print(f"\n📈 EXAMPLES BY CATEGORY:")
    print("-" * 70)
    
    spot_only_symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True, is_spot_tradable=True, is_futures_tradable=False)[:10]
    futures_only_symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True, is_spot_tradable=False, is_futures_tradable=True)[:10]
    both_symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True, is_spot_tradable=True, is_futures_tradable=True)[:10]
    
    print(f"🪙 SPOT ONLY ({spot_only_symbols.count()}):")
    for s in spot_only_symbols:
        print(f"  • {s.symbol}: {s.name}")
    
    print(f"\n⚡ FUTURES ONLY ({futures_only_symbols.count()}):")
    for s in futures_only_symbols:
        print(f"  • {s.symbol}: {s.name}")
    
    print(f"\n🔄 BOTH SPOT & FUTURES ({both_symbols.count()}):")
    for s in both_symbols:
        print(f"  • {s.symbol}: {s.name}")
    
    print(f"\n✅ Categorization completed!")
    print(f"🌐 Ready to generate signals:")
    print(f"   • Spot signals for: {spot_only_count + both_count} coins")
    print(f"   • Futures signals for: {futures_only_count + both_count} coins")

def main():
    """Main function"""
    try:
        categorize_crypto_coins()
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()































































