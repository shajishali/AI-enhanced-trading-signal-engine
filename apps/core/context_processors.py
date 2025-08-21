"""
Global context processors for the AI Trading Engine
Automatically adds live cryptocurrency prices to every page
"""

from django.core.cache import cache


def live_crypto_prices(request):
    """Global context processor for live cryptocurrency prices"""
    try:
        # Try to get cached prices first
        live_prices = cache.get('live_crypto_prices')
        
        if not live_prices:
            # If no cached prices, try to fetch from real price service
            try:
                from apps.data.real_price_service import get_live_prices
                live_prices = get_live_prices()
            except:
                live_prices = {}
        
        # Get all available cryptocurrencies for display
        global_crypto_prices = {}
        
        # Sort symbols by market cap/importance (Top 20 first, then others)
        priority_symbols = [
            'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'USDC', 'XRP', 'STETH', 'ADA', 'AVAX',
            'DOGE', 'TRX', 'LINK', 'DOT', 'MATIC', 'TON', 'SHIB', 'DAI', 'UNI', 'BCH'
        ]
        other_symbols = []
        
        for symbol in live_prices.keys():
            if symbol not in priority_symbols:
                other_symbols.append(symbol)
        
        # Add priority symbols first, then all others
        all_symbols = priority_symbols + sorted(other_symbols)
        
        for symbol in all_symbols:
            if symbol in live_prices:
                price_data = live_prices[symbol]
                global_crypto_prices[symbol] = {
                    'price': price_data['price'],
                    'change_24h': price_data['change_24h'],
                    'volume_24h': price_data['volume_24h'],
                    'source': price_data.get('source', 'API')
                }
        
        return {
            'global_crypto_prices': global_crypto_prices,
            'has_live_prices': len(global_crypto_prices) > 0
        }
        
    except Exception:
        # Return empty data if anything fails
        return {
            'global_crypto_prices': {},
            'has_live_prices': False
        }


def market_status(request):
    """Global context processor for market status"""
    try:
        # Get market status from cache or calculate
        market_status_data = cache.get('market_status')
        
        if not market_status_data:
            # Calculate basic market status
            try:
                from apps.data.real_price_service import get_live_prices
                live_prices = get_live_prices()
                
                if live_prices:
                    # Calculate overall market sentiment
                    total_change = 0
                    positive_count = 0
                    
                    for symbol, data in live_prices.items():
                        change = data.get('change_24h', 0)
                        total_change += change
                        if change > 0:
                            positive_count += 1
                    
                    total_symbols = len(live_prices)
                    market_sentiment = 'bullish' if positive_count > total_symbols / 2 else 'bearish'
                    avg_change = total_change / total_symbols if total_symbols > 0 else 0
                    
                    market_status_data = {
                        'sentiment': market_sentiment,
                        'average_change': round(avg_change, 2),
                        'positive_symbols': positive_count,
                        'total_symbols': total_symbols,
                        'last_updated': 'Live'
                    }
                else:
                    market_status_data = {
                        'sentiment': 'neutral',
                        'average_change': 0,
                        'positive_symbols': 0,
                        'total_symbols': 0,
                        'last_updated': 'Offline'
                    }
                
                # Cache for 1 minute
                cache.set('market_status', market_status_data, 60)
                
            except:
                market_status_data = {
                    'sentiment': 'neutral',
                    'average_change': 0,
                    'positive_symbols': 0,
                    'total_symbols': 0,
                    'last_updated': 'Offline'
                }
        
        return {
            'market_status': market_status_data
        }
        
    except Exception:
        return {
            'market_status': {
                'sentiment': 'neutral',
                'average_change': 0,
                'positive_symbols': 0,
                'total_symbols': 0,
                'last_updated': 'Offline'
            }
        }

