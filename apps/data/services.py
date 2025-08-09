import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
import logging
from django.utils import timezone
from django.db import transaction
from pycoingecko import CoinGeckoAPI
import ccxt
import websocket
import json
import threading
import time

from .models import (
    DataSource, MarketData, DataFeed, TechnicalIndicator, 
    DataSyncLog
)
from apps.trading.models import Symbol

logger = logging.getLogger(__name__)


class CoinGeckoService:
    """Service for CoinGecko API integration"""
    
    def __init__(self):
        self.api = CoinGeckoAPI()
        self.base_url = "https://api.coingecko.com/api/v3"
        
    def get_top_coins(self, limit: int = 200) -> List[Dict]:
        """Get top coins by market cap"""
        try:
            coins = self.api.get_coins_markets(
                vs_currency='usd',
                order='market_cap_desc',
                per_page=limit,
                page=1,
                sparkline=False
            )
            return coins
        except Exception as e:
            logger.error(f"Error fetching top coins: {e}")
            return []
    
    def get_coin_data(self, coin_id: str) -> Optional[Dict]:
        """Get detailed data for a specific coin"""
        try:
            data = self.api.get_coin_by_id(coin_id)
            return data
        except Exception as e:
            logger.error(f"Error fetching coin data for {coin_id}: {e}")
            return None
    
    def get_historical_data(self, coin_id: str, days: int = 30) -> Optional[List[Dict]]:
        """Get historical price data"""
        try:
            data = self.api.get_coin_market_chart_by_id(
                id=coin_id,
                vs_currency='usd',
                days=days
            )
            return data
        except Exception as e:
            logger.error(f"Error fetching historical data for {coin_id}: {e}")
            return None


class CryptoDataIngestionService:
    """Service for ingesting crypto market data"""
    
    def __init__(self):
        self.coingecko = CoinGeckoService()
        self.data_source, _ = DataSource.objects.get_or_create(
            name='CoinGecko',
            defaults={
                'source_type': 'API',
                'base_url': 'https://api.coingecko.com/api/v3',
                'is_active': True
            }
        )
    
    def sync_crypto_symbols(self) -> bool:
        """Sync crypto symbols from CoinGecko"""
        try:
            coins = self.coingecko.get_top_coins(limit=200)
            
            with transaction.atomic():
                for coin in coins:
                    symbol, created = Symbol.objects.get_or_create(
                        symbol=coin['symbol'].upper(),
                        defaults={
                            'name': coin['name'],
                            'symbol_type': 'CRYPTO',
                            'exchange': 'CoinGecko',
                            'is_active': True
                        }
                    )
                    
                    if created:
                        logger.info(f"Created new symbol: {symbol.symbol}")
            
            return True
        except Exception as e:
            logger.error(f"Error syncing crypto symbols: {e}")
            return False
    
    def sync_market_data(self, symbol: Symbol) -> bool:
        """Sync market data for a specific symbol"""
        try:
            # Get historical data for the symbol
            coin_id = symbol.symbol.lower()
            historical_data = self.coingecko.get_historical_data(coin_id, days=30)
            
            if not historical_data or 'prices' not in historical_data:
                logger.warning(f"No historical data found for {symbol.symbol}")
                return False
            
            with transaction.atomic():
                for price_data in historical_data['prices']:
                    timestamp = datetime.fromtimestamp(price_data[0] / 1000)
                    price = Decimal(str(price_data[1]))
                    
                    # Create or update market data
                    market_data, created = MarketData.objects.get_or_create(
                        symbol=symbol,
                        timestamp=timestamp,
                        defaults={
                            'open_price': price,
                            'high_price': price,
                            'low_price': price,
                            'close_price': price,
                            'volume': Decimal('0'),
                            'source': self.data_source
                        }
                    )
                    
                    if not created:
                        market_data.close_price = price
                        market_data.save()
            
            return True
        except Exception as e:
            logger.error(f"Error syncing market data for {symbol.symbol}: {e}")
            return False


class TechnicalAnalysisService:
    """Service for calculating technical indicators"""
    
    def __init__(self):
        self.data_source, _ = DataSource.objects.get_or_create(
            name='Technical Analysis',
            defaults={
                'source_type': 'CALCULATED',
                'is_active': True
            }
        )
    
    def get_market_data_df(self, symbol: Symbol, limit: int = 100) -> pd.DataFrame:
        """Get market data as pandas DataFrame"""
        market_data = MarketData.objects.filter(
            symbol=symbol
        ).order_by('-timestamp')[:limit]
        
        if not market_data:
            return pd.DataFrame()
        
        data = []
        for md in market_data:
            data.append({
                'timestamp': md.timestamp,
                'open': float(md.open_price),
                'high': float(md.high_price),
                'low': float(md.low_price),
                'close': float(md.close_price),
                'volume': float(md.volume)
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('timestamp')
        return df
    
    def calculate_rsi(self, symbol: Symbol, period: int = 14) -> Optional[float]:
        """Calculate RSI for a symbol"""
        try:
            df = self.get_market_data_df(symbol)
            if df.empty or len(df) < period:
                return None
            
            # Calculate RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            latest_rsi = rsi.iloc[-1]
            
            if not pd.isna(latest_rsi):
                # Save to database
                TechnicalIndicator.objects.create(
                    symbol=symbol,
                    indicator_type='RSI',
                    period=period,
                    value=Decimal(str(latest_rsi)),
                    timestamp=timezone.now(),
                    source=self.data_source
                )
                
                return float(latest_rsi)
            
            return None
        except Exception as e:
            logger.error(f"Error calculating RSI for {symbol.symbol}: {e}")
            return None
    
    def calculate_macd(self, symbol: Symbol, fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[Dict]:
        """Calculate MACD for a symbol"""
        try:
            df = self.get_market_data_df(symbol)
            if df.empty or len(df) < slow:
                return None
            
            # Calculate MACD
            exp1 = df['close'].ewm(span=fast).mean()
            exp2 = df['close'].ewm(span=slow).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=signal).mean()
            histogram = macd - signal_line
            
            latest_macd = macd.iloc[-1]
            latest_signal = signal_line.iloc[-1]
            latest_histogram = histogram.iloc[-1]
            
            if not pd.isna(latest_macd):
                # Save to database
                TechnicalIndicator.objects.create(
                    symbol=symbol,
                    indicator_type='MACD',
                    period=fast,
                    value=Decimal(str(latest_macd)),
                    timestamp=timezone.now(),
                    source=self.data_source
                )
                
                return {
                    'macd': float(latest_macd),
                    'signal': float(latest_signal),
                    'histogram': float(latest_histogram)
                }
            
            return None
        except Exception as e:
            logger.error(f"Error calculating MACD for {symbol.symbol}: {e}")
            return None
    
    def calculate_bollinger_bands(self, symbol: Symbol, period: int = 20, std_dev: int = 2) -> Optional[Dict]:
        """Calculate Bollinger Bands for a symbol"""
        try:
            df = self.get_market_data_df(symbol)
            if df.empty or len(df) < period:
                return None
            
            # Calculate Bollinger Bands
            middle = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()
            upper = middle + (std * std_dev)
            lower = middle - (std * std_dev)
            
            latest_middle = middle.iloc[-1]
            latest_upper = upper.iloc[-1]
            latest_lower = lower.iloc[-1]
            
            if not pd.isna(latest_middle):
                # Save to database
                TechnicalIndicator.objects.create(
                    symbol=symbol,
                    indicator_type='BB_MIDDLE',
                    period=period,
                    value=Decimal(str(latest_middle)),
                    timestamp=timezone.now(),
                    source=self.data_source
                )
                
                return {
                    'upper': float(latest_upper),
                    'middle': float(latest_middle),
                    'lower': float(latest_lower)
                }
            
            return None
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands for {symbol.symbol}: {e}")
            return None
    
    def calculate_all_indicators(self, symbol: Symbol) -> bool:
        """Calculate all technical indicators for a symbol"""
        try:
            success_count = 0
            
            # Calculate RSI
            if self.calculate_rsi(symbol):
                success_count += 1
            
            # Calculate MACD
            if self.calculate_macd(symbol):
                success_count += 1
            
            # Calculate Bollinger Bands
            if self.calculate_bollinger_bands(symbol):
                success_count += 1
            
            logger.info(f"Calculated {success_count}/3 indicators for {symbol.symbol}")
            return success_count > 0
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol.symbol}: {e}")
            return False


class RiskManagementService:
    """Service for risk management calculations"""
    
    def get_market_data_df(self, symbol: Symbol, limit: int = 100) -> pd.DataFrame:
        """Get market data as pandas DataFrame"""
        market_data = MarketData.objects.filter(
            symbol=symbol
        ).order_by('-timestamp')[:limit]
        
        if not market_data:
            return pd.DataFrame()
        
        data = []
        for md in market_data:
            data.append({
                'timestamp': md.timestamp,
                'open': float(md.open_price),
                'high': float(md.high_price),
                'low': float(md.low_price),
                'close': float(md.close_price),
                'volume': float(md.volume)
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('timestamp')
        return df
    
    def calculate_volatility(self, symbol: Symbol, period: int = 20) -> Optional[float]:
        """Calculate price volatility"""
        try:
            df = self.get_market_data_df(symbol, limit=period)
            if df.empty or len(df) < period:
                return None
            
            # Calculate daily returns
            returns = df['close'].pct_change().dropna()
            
            # Calculate volatility (standard deviation of returns)
            volatility = returns.std() * np.sqrt(252)  # Annualized
            
            return float(volatility)
        except Exception as e:
            logger.error(f"Error calculating volatility for {symbol.symbol}: {e}")
            return None
    
    def calculate_position_size(self, account_size: float, risk_per_trade: float, stop_loss_pct: float) -> float:
        """Calculate position size based on risk management rules"""
        try:
            risk_amount = account_size * risk_per_trade
            position_size = risk_amount / stop_loss_pct
            return min(position_size, account_size)  # Don't exceed account size
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float, take_profit: float) -> float:
        """Calculate risk-reward ratio"""
        try:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            
            if risk == 0:
                return 0.0
            
            return reward / risk
        except Exception as e:
            logger.error(f"Error calculating risk-reward ratio: {e}")
            return 0.0




