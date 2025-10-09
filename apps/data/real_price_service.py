"""
Real Price Service - Fetches live cryptocurrency prices from external APIs
"""

import requests
import logging
from decimal import Decimal
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class RealPriceService:
    """Service for fetching real cryptocurrency prices"""
    
    def __init__(self):
        self.binance_api = "https://api.binance.com/api/v3"
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.cache_timeout = 300  # Cache prices for 5 minutes instead of 30 seconds
        
        # Supported symbols for live data - 200+ popular cryptocurrencies
        self.live_symbols = [
            # Top 20 by Market Cap
            'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'USDC', 'XRP', 'STETH', 'ADA', 'AVAX',
            'DOGE', 'TRX', 'LINK', 'DOT', 'MATIC', 'TON', 'SHIB', 'DAI', 'UNI', 'BCH',
            
            # Major Altcoins
            'LTC', 'XLM', 'ATOM', 'ETC', 'FIL', 'NEAR', 'APT', 'OP', 'ARB', 'MKR',
            'VET', 'ICP', 'ALGO', 'FTM', 'THETA', 'XMR', 'HBAR', 'IMX', 'STX', 'GRT',
            
            # DeFi & Gaming
            'AAVE', 'COMP', 'CRV', 'SUSHI', 'YFI', 'SNX', 'BAL', 'REN', 'KNC', 'ZRX',
            'MANA', 'SAND', 'AXS', 'ENJ', 'CHZ', 'GALA', 'ROSE', 'ONE', 'HOT', 'BAT',
            
            # Layer 1 & 2
            'SUI', 'SEI', 'TIA', 'INJ', 'KAS', 'RUNE', 'FLOW', 'EGLD', 'ZIL', 'QTUM',
            'NEO', 'WAVES', 'XTZ', 'IOTA', 'NANO', 'XEM', 'VTHO', 'ICX', 'ONT', 'ZEN',
            
            # Exchange Tokens
            'OKB', 'HT', 'GT', 'KCS', 'BTT', 'CRO', 'FTT', 'LEO', 'HOT', 'BNT',
            
            # Meme & Social
            'PEPE', 'FLOKI', 'BONK', 'WIF', 'MYRO', 'POPCAT', 'BOOK', 'TURBO', 'SPX', 'BOME',
            'SLERF', 'CAT', 'DOG', 'MOON', 'ROCKET', 'LAMBO', 'YACHT', 'PLANET', 'STAR', 'GEM',
            
            # AI & Tech
            'FET', 'OCEAN', 'AGIX', 'RNDR', 'AKT', 'HFT', 'TAO', 'BITTENSOR', 'AI', 'GPT',
            'CHAT', 'BOT', 'ROBOT', 'NEURAL', 'BRAIN', 'MIND', 'THINK', 'LOGIC', 'SMART', 'GENIUS',
            
            # Privacy & Security
            'XMR', 'ZEC', 'DASH', 'XHV', 'BEAM', 'GRIN', 'PIVX', 'FIRO', 'XVG', 'ZEN',
            
            # Oracle & Data
            'BAND', 'API3', 'DIA', 'LINK', 'NEST', 'PENDLE', 'PERP', 'DYDX', 'GMX', 'SNX',
            
            # Metaverse & NFT
            'MANA', 'SAND', 'AXS', 'ENJ', 'CHZ', 'GALA', 'ROSE', 'ONE', 'HOT', 'BAT',
            'APE', 'DYDX', 'IMX', 'OP', 'ARB', 'MATIC', 'POLYGON', 'AVAX', 'FTM', 'SOL',
            
            # Additional Popular Coins
            'CAKE', 'BAKE', 'SXP', 'WIN', 'BTT', 'TRX', 'JST', 'SUN', 'BUSD', 'USDD',
            'TUSD', 'FRAX', 'LUSD', 'GUSD', 'PAX', 'USDP', 'BUSD', 'USDC', 'DAI', 'USDT',
            
            # More Altcoins
            'RVN', 'ERG', 'XDC', 'XRP', 'XLM', 'ADA', 'DOT', 'LINK', 'UNI', 'AAVE',
            'COMP', 'MKR', 'YFI', 'SNX', 'BAL', 'REN', 'KNC', 'ZRX', 'CRV', 'SUSHI',
            
            # Additional 50+ coins to reach 200+
            'ANKR', 'AR', 'AUDIO', 'BICO', 'BLZ', 'BNT', 'BOND', 'C98', 'CELO', 'CFX',
            'CHR', 'CLV', 'COCOS', 'CTSI', 'CTXC', 'CVP', 'DENT', 'DGB', 'DUSK', 'ELF',
            'ERN', 'FIDA', 'FLOW', 'FORTH', 'FRONT', 'FTM', 'FXS', 'GALA', 'GLM', 'GMT',
            'GODS', 'GOG', 'GRT', 'GTC', 'HFT', 'HIGH', 'HIVE', 'HOPR', 'ICP', 'IDEX',
            'ILV', 'IMX', 'INJ', 'IOTX', 'IRIS', 'JASMY', 'JOE', 'KAVA', 'KDA', 'KEY',
            'KLAY', 'KSM', 'LDO', 'LINA', 'LIT', 'LOKA', 'LPT', 'LQTY', 'LRC', 'MASK',
            'MINA', 'MKR', 'MLN', 'MOCA', 'MOVR', 'MTL', 'MULTI', 'NEO', 'NKN', 'NMR',
            'OCEAN', 'OGN', 'OM', 'ONG', 'ONT', 'OP', 'ORBS', 'OXT', 'PAXG', 'PEOPLE',
            'PERP', 'PHA', 'PLA', 'POLS', 'POLY', 'POND', 'POWR', 'PRO', 'PROM', 'QNT',
            'QUICK', 'RAD', 'RARE', 'RARI', 'RAY', 'RBN', 'REN', 'REP', 'REQ', 'RLC',
            'ROSE', 'RSR', 'RSS3', 'RUNE', 'SAND', 'SCRT', 'SFP', 'SHIB', 'SKL', 'SLP',
            'SNT', 'SNX', 'SOC', 'SPELL', 'SRM', 'STG', 'STMX', 'STORJ', 'STPT', 'STRAX',
            'SUPER', 'SUSHI', 'SWAP', 'SWEAT', 'SXP', 'SYN', 'SYS', 'T', 'TFUEL', 'THETA',
            'TLM', 'TOKE', 'TOMO', 'TORN', 'TRB', 'TRIBE', 'TRU', 'TRX', 'TUSD', 'TVK',
            'UMA', 'UNI', 'USDC', 'USDD', 'USDT', 'UTK', 'VET', 'VGX', 'VRA', 'VTHO',
            'WAVES', 'WAXL', 'WAXP', 'WBTC', 'WOO', 'XDC', 'XEC', 'XEM', 'XLM', 'XMR',
            'XRP', 'XTZ', 'XVG', 'YFI', 'YGG', 'ZEC', 'ZEN', 'ZIL', 'ZRX', '1INCH'
        ]
    
    def get_live_prices(self):
        """Get live cryptocurrency prices from multiple sources"""
        try:
            # Try to get from cache first
            cached_prices = cache.get('live_crypto_prices')
            if cached_prices:
                logger.debug("Returning cached prices")
                return cached_prices
            
            # Fetch from Binance API
            binance_prices = self._fetch_binance_prices()
            
            # Fetch from CoinGecko API
            coingecko_prices = self._fetch_coingecko_prices()
            
            # Merge prices (Binance takes priority for USDT pairs)
            live_prices = {}
            
            # Add Binance prices
            for symbol, data in binance_prices.items():
                if symbol in self.live_symbols:
                    live_prices[symbol] = data
            
            # Add CoinGecko prices for missing symbols
            for symbol, data in coingecko_prices.items():
                if symbol in self.live_symbols and symbol not in live_prices:
                    live_prices[symbol] = data
            
            # Cache the results
            cache.set('live_crypto_prices', live_prices, self.cache_timeout)
            
            logger.info(f"Fetched live prices for {len(live_prices)} symbols")
            return live_prices
            
        except Exception as e:
            logger.error(f"Error fetching live prices: {e}")
            # Return cached prices if available, otherwise empty dict
            return cache.get('live_crypto_prices', {})
    
    def _fetch_binance_prices(self):
        """Fetch prices from Binance API"""
        try:
            url = f"{self.binance_api}/ticker/24hr"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                prices = {}
                
                for ticker in data:
                    symbol = ticker['symbol']
                    
                    # Only process USDT pairs for major coins
                    if symbol.endswith('USDT'):
                        base_symbol = symbol[:-4]  # Remove 'USDT'
                        
                        if base_symbol in self.live_symbols:
                            price = float(ticker['lastPrice'])
                            change_24h = float(ticker['priceChangePercent'])
                            volume_24h = float(ticker['volume'])
                            
                            prices[base_symbol] = {
                                'price': price,
                                'change_24h': change_24h,
                                'volume_24h': volume_24h,
                                'source': 'Binance',
                                'last_updated': timezone.now().isoformat()
                            }
                
                return prices
            else:
                logger.warning(f"Binance API returned status {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching Binance prices: {e}")
            return {}
    
    def _fetch_coingecko_prices(self):
        """Fetch prices from CoinGecko API"""
        try:
            coin_ids = self._get_coingecko_ids()
            url = f"{self.coingecko_api}/simple/price"
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                prices = {}
                
                for coin_id, coin_data in data.items():
                    symbol = self._coingecko_id_to_symbol(coin_id)
                    if symbol in self.live_symbols:
                        price = coin_data.get('usd', 0)
                        change_24h = coin_data.get('usd_24h_change', 0)
                        volume_24h = coin_data.get('usd_24h_vol', 0)
                        
                        prices[symbol] = {
                            'price': price,
                            'change_24h': change_24h,
                            'volume_24h': volume_24h,
                            'source': 'CoinGecko',
                            'last_updated': timezone.now().isoformat()
                        }
                
                return prices
            else:
                logger.warning(f"CoinGecko API returned status {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching CoinGecko prices: {e}")
            return {}
    
    def get_symbol_price(self, symbol):
        """Get price for a specific symbol"""
        prices = self.get_live_prices()
        return prices.get(symbol, {})
    
    def refresh_prices(self):
        """Force refresh of prices (clear cache)"""
        cache.delete('live_crypto_prices')
        return self.get_live_prices()
    
    @staticmethod
    def _extract_base_symbol(symbol):
        """Extract base symbol from trading pair (e.g., BTCUSDT -> BTC)"""
        quote_currencies = ['USDT', 'BTC', 'ETH', 'BNB', 'USD']
        
        for quote in quote_currencies:
            if symbol.endswith(quote):
                return symbol[:-len(quote)]
        
        return symbol
    
    @staticmethod
    def _get_coingecko_ids():
        """Get CoinGecko coin IDs for supported symbols"""
        symbol_to_id = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'XRP': 'ripple',
            'USDT': 'tether',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'USDC': 'usd-coin',
            'DOGE': 'dogecoin',
            'TRX': 'tron',
            'ADA': 'cardano',
            'LINK': 'chainlink',
            'XLM': 'stellar'
        }
        
        return list(symbol_to_id.values())
    
    @staticmethod
    def _coingecko_id_to_symbol(coin_id):
        """Convert CoinGecko coin ID to symbol"""
        id_to_symbol = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'ripple': 'XRP',
            'tether': 'USDT',
            'binancecoin': 'BNB',
            'solana': 'SOL',
            'usd-coin': 'USDC',
            'dogecoin': 'DOGE',
            'tron': 'TRX',
            'cardano': 'ADA',
            'chainlink': 'LINK',
            'stellar': 'XLM'
        }
        
        return id_to_symbol.get(coin_id, coin_id.upper())


# Global instance
real_price_service = RealPriceService()


def get_live_prices():
    """Get live cryptocurrency prices"""
    return real_price_service.get_live_prices()


def get_symbol_price(symbol):
    """Get price for a specific symbol"""
    return real_price_service.get_symbol_price(symbol)


def refresh_prices():
    """Force refresh of prices"""
    return real_price_service.refresh_prices()
