"""
Database-driven signal generation service
Uses automated database data instead of live API calls
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

from django.utils import timezone
from django.db.models import Q, Avg, Max, Min
from django.core.cache import cache

from apps.trading.models import Symbol
from apps.data.models import MarketData, TechnicalIndicator
from apps.signals.models import TradingSignal, SignalType, SignalStrength
from apps.signals.strategies import (
    MovingAverageCrossoverStrategy,
    RSIMeanReversionStrategy,
    BollingerBandsStrategy,
    MACDStrategy,
    VolumeBreakoutStrategy
)

logger = logging.getLogger(__name__)


class DatabaseSignalService:
    """Signal generation using automated database data instead of live APIs"""
    
    def __init__(self):
        self.lookback_hours = 24  # Use last 24 hours of data
        self.min_data_points = 20  # Minimum data points required
        self.price_cache_timeout = 300  # 5 minutes cache
        self.signal_refresh_hours = 2  # Signal refresh interval
        
        # Initialize strategies
        self.strategies = {
            'ma_crossover': MovingAverageCrossoverStrategy(),
            'rsi_mean_reversion': RSIMeanReversionStrategy(),
            'bollinger_bands': BollingerBandsStrategy(),
            'macd': MACDStrategy(),
            'volume_breakout': VolumeBreakoutStrategy()
        }
    
    def generate_best_signals_for_all_coins(self) -> Dict[str, any]:
        """Generate the best 10 signals from all 200+ coins using database data"""
        logger.info("Starting database-driven signal generation for all coins")
        
        # Get symbols that don't have active signals (duplicate prevention)
        symbols_with_active_signals = set(
            TradingSignal.objects.filter(
                is_valid=True,
                created_at__gte=timezone.now() - timedelta(hours=self.signal_refresh_hours)
            ).values_list('symbol__symbol', flat=True)
        )
        
        # Get all active crypto symbols excluding those with recent signals
        all_symbols = Symbol.objects.filter(
            is_active=True, 
            is_crypto_symbol=True
        ).exclude(symbol__in=symbols_with_active_signals)
        
        logger.info(f"Found {len(symbols_with_active_signals)} symbols with recent signals")
        logger.info(f"Analyzing {all_symbols.count()} crypto symbols (excluding duplicates)")
        
        all_signals = []
        processed_count = 0
        
        # Generate signals for each symbol (only new ones)
        for symbol in all_symbols:
            try:
                # Check if we have sufficient recent data
                recent_data = self.get_recent_market_data(symbol, hours_back=self.lookback_hours)
                if recent_data.count() < self.min_data_points:
                    logger.warning(f"Insufficient data for {symbol.symbol}: {recent_data.count()} points")
                    continue
                
                symbol_signals = self.generate_logical_signals_for_symbol(symbol, recent_data)
                all_signals.extend(symbol_signals)
                processed_count += 1
                
                if processed_count % 50 == 0:
                    logger.info(f"Processed {processed_count}/{all_symbols.count()} symbols")
                    
            except Exception as e:
                logger.error(f"Error generating signals for {symbol.symbol}: {e}")
                continue
        
        logger.info(f"Generated {len(all_signals)} total signals from {processed_count} symbols")
        
        # Select the best 10 signals
        best_signals = self._select_best_signals(all_signals)
        
        return {
            'total_signals_generated': len(all_signals),
            'best_signals_selected': len(best_signals),
            'processed_symbols': processed_count,
            'best_signals': best_signals
        }
    
    def generate_logical_signals_for_symbol(self, symbol: Symbol, market_data) -> List[TradingSignal]:
        """Generate signals for a specific symbol using database data"""
        signals = []
        
        try:
            # Convert market data to DataFrame for analysis
            df = self._market_data_to_dataframe(market_data)
            if df is None or len(df) < self.min_data_points:
                return signals
            
            # Get current price from database
            current_price = self.get_latest_price(symbol)
            if not current_price or current_price <= 0:
                logger.warning(f"Invalid price for {symbol.symbol}: {current_price}")
                return signals
            
            # Generate signals using different strategies
            for strategy_name, strategy in self.strategies.items():
                try:
                    strategy_signals = strategy.generate_signals(df, current_price)
                    for signal_data in strategy_signals:
                        signal = self._create_trading_signal(symbol, signal_data, strategy_name)
                        if signal:
                            signals.append(signal)
                except Exception as e:
                    logger.error(f"Error in {strategy_name} for {symbol.symbol}: {e}")
                    continue
            
            logger.info(f"Generated {len(signals)} signals for {symbol.symbol}")
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals for {symbol.symbol}: {e}")
            return []
    
    def get_recent_market_data(self, symbol: Symbol, hours_back: int = 24) -> 'QuerySet':
        """Get recent market data from database"""
        cutoff_time = timezone.now() - timedelta(hours=hours_back)
        return MarketData.objects.filter(
            symbol=symbol,
            timeframe='1h',
            timestamp__gte=cutoff_time
        ).order_by('timestamp')
    
    def get_latest_price(self, symbol: Symbol) -> Optional[Decimal]:
        """Get latest price from database instead of live API"""
        cache_key = f"latest_price_{symbol.symbol}"
        
        # Try cache first
        cached_price = cache.get(cache_key)
        if cached_price and float(cached_price) > 0:
            return Decimal(str(cached_price))
        
        # Get from database
        latest_data = MarketData.objects.filter(
            symbol=symbol,
            timeframe='1h'
        ).order_by('-timestamp').first()
        
        if latest_data and latest_data.close_price and float(latest_data.close_price) > 0:
            price_decimal = Decimal(str(latest_data.close_price))
            cache.set(cache_key, float(price_decimal), self.price_cache_timeout)
            logger.info(f"Using database price for {symbol.symbol}: ${price_decimal:,}")
            return price_decimal
        
        logger.warning(f"No recent price data found for {symbol.symbol}")
        return None
    
    def get_latest_market_data(self, symbol: Symbol) -> Optional[Dict]:
        """Get latest market data for signal generation - uses database data"""
        try:
            # Get latest market data from database
            latest_data = MarketData.objects.filter(
                symbol=symbol,
                timeframe='1h'
            ).order_by('-timestamp').first()
            
            if latest_data and latest_data.close_price and float(latest_data.close_price) > 0:
                market_data = {
                    'close_price': latest_data.close_price,
                    'high_price': latest_data.high_price,
                    'low_price': latest_data.low_price,
                    'open_price': latest_data.open_price,
                    'volume': latest_data.volume,
                    'timestamp': latest_data.timestamp,
                    'data_source': 'database',
                    'symbol': symbol.symbol
                }
                
                logger.info(f"Using database market data for {symbol.symbol}: ${latest_data.close_price:,.2f}")
                return market_data
            else:
                logger.warning(f"No recent database data for {symbol.symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting database market data for {symbol.symbol}: {e}")
            return None
    
    def _market_data_to_dataframe(self, market_data) -> Optional[pd.DataFrame]:
        """Convert market data QuerySet to pandas DataFrame"""
        try:
            if not market_data.exists():
                return None
            
            data = []
            for record in market_data:
                data.append({
                    'timestamp': record.timestamp,
                    'open': float(record.open_price),
                    'high': float(record.high_price),
                    'low': float(record.low_price),
                    'close': float(record.close_price),
                    'volume': float(record.volume) if record.volume else 0
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error converting market data to DataFrame: {e}")
            return None
    
    def _create_trading_signal(self, symbol: Symbol, signal_data: Dict, strategy_name: str) -> Optional[TradingSignal]:
        """Create a TradingSignal from signal data"""
        try:
            # Get or create signal type
            signal_type, created = SignalType.objects.get_or_create(
                name=signal_data.get('signal_type', 'BUY'),
                defaults={'description': f'Generated by {strategy_name}'}
            )
            
            # Get or create signal strength
            strength_value = signal_data.get('strength', 'MODERATE')
            strength, created = SignalStrength.objects.get_or_create(
                name=strength_value,
                defaults={'description': f'Strength level: {strength_value}'}
            )
            
            # Calculate confidence score
            confidence_score = signal_data.get('confidence', 0.5)
            confidence_level = self._calculate_confidence_level(confidence_score)
            
            # Create trading signal
            trading_signal = TradingSignal.objects.create(
                symbol=symbol,
                signal_type=signal_type,
                strength=strength,
                confidence_score=confidence_score,
                confidence_level=confidence_level,
                entry_price=Decimal(str(signal_data.get('entry_price', 0))),
                target_price=Decimal(str(signal_data.get('target_price', 0))),
                stop_loss=Decimal(str(signal_data.get('stop_loss', 0))),
                risk_reward_ratio=signal_data.get('risk_reward_ratio', 0),
                timeframe=signal_data.get('timeframe', '1H'),
                investment_horizon=signal_data.get('investment_horizon', 'SHORT'),
                is_valid=True,
                data_source='database',
                strategy_used=strategy_name
            )
            
            logger.info(f"Created {signal_type.name} signal for {symbol.symbol} using {strategy_name}")
            return trading_signal
            
        except Exception as e:
            logger.error(f"Error creating trading signal for {symbol.symbol}: {e}")
            return None
    
    def _calculate_confidence_level(self, confidence_score: float) -> str:
        """Calculate confidence level from score"""
        if confidence_score >= 0.85:
            return 'VERY_HIGH'
        elif confidence_score >= 0.70:
            return 'HIGH'
        elif confidence_score >= 0.50:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _select_best_signals(self, all_signals: List[TradingSignal]) -> List[TradingSignal]:
        """Select the best 10 signals based on confidence, quality, news, and sentiment"""
        if not all_signals:
            return []
        
        # Calculate combined score for each signal (strategy + news + sentiment)
        scored_signals = []
        for signal in all_signals:
            # Base confidence from strategy (40% weight)
            strategy_score = signal.confidence_score * 0.4
            
            # Quality score (30% weight)
            quality_score = (signal.quality_score if hasattr(signal, 'quality_score') and signal.quality_score else 0.5) * 0.3
            
            # News score (15% weight) - get from signal metadata or calculate
            news_score = self._get_news_score_for_signal(signal) * 0.15
            
            # Sentiment score (15% weight) - get from signal metadata or calculate
            sentiment_score = self._get_sentiment_score_for_signal(signal) * 0.15
            
            # Combined score
            combined_score = strategy_score + quality_score + news_score + sentiment_score
            
            # Risk-reward bonus
            rr_bonus = min(0.1, (signal.risk_reward_ratio or 0) / 10)  # Up to 10% bonus
            
            final_score = combined_score + rr_bonus
            
            scored_signals.append((final_score, signal))
        
        # Sort by combined score
        scored_signals.sort(key=lambda x: x[0], reverse=True)
        
        # Return top 10 signals
        return [signal for _, signal in scored_signals[:10]]
    
    def _get_news_score_for_signal(self, signal: TradingSignal) -> float:
        """Get news sentiment score for a signal's symbol"""
        try:
            from apps.sentiment.models import CryptoMention, NewsArticle
            from datetime import timedelta
            
            # Get recent news mentions (last 24 hours)
            recent_mentions = CryptoMention.objects.filter(
                asset=signal.symbol,
                news_article__published_at__gte=timezone.now() - timedelta(hours=24),
                mention_type='news'
            )
            
            if not recent_mentions.exists():
                return 0.5  # Neutral if no news
            
            # Calculate weighted sentiment score
            total_score = 0.0
            total_weight = 0.0
            
            for mention in recent_mentions:
                hours_ago = (timezone.now() - mention.news_article.published_at).total_seconds() / 3600
                recency_weight = max(0, 1 - (hours_ago / 24))  # Decay over 24 hours
                weight = mention.confidence_score * recency_weight
                
                # Convert sentiment to score (-1 to 1, then normalize to 0-1)
                sentiment_value = mention.sentiment_score if mention.sentiment_label == 'POSITIVE' else -mention.sentiment_score
                normalized_sentiment = (sentiment_value + 1) / 2
                
                total_score += normalized_sentiment * weight
                total_weight += weight
            
            return total_score / total_weight if total_weight > 0 else 0.5
            
        except Exception as e:
            logger.debug(f"Error getting news score for {signal.symbol.symbol}: {e}")
            return 0.5
    
    def _get_sentiment_score_for_signal(self, signal: TradingSignal) -> float:
        """Get market sentiment score for a signal's symbol"""
        try:
            from apps.sentiment.models import SentimentAggregate
            from datetime import timedelta
            
            # Get recent sentiment aggregate (last 2 hours)
            recent_aggregate = SentimentAggregate.objects.filter(
                asset=signal.symbol,
                timeframe='1h',
                created_at__gte=timezone.now() - timedelta(hours=2)
            ).order_by('-created_at').first()
            
            if recent_aggregate:
                # Convert sentiment score (-1 to 1) to normalized score (0 to 1)
                normalized_score = (recent_aggregate.aggregate_sentiment_score + 1) / 2
                return normalized_score
            
            return 0.5  # Neutral if no sentiment data
            
        except Exception as e:
            logger.debug(f"Error getting sentiment score for {signal.symbol.symbol}: {e}")
            return 0.5
    
    def validate_database_data_quality(self, symbol: Symbol) -> Dict[str, any]:
        """Validate database data quality for a symbol"""
        try:
            # Check data freshness
            latest_data = MarketData.objects.filter(
                symbol=symbol,
                timeframe='1h'
            ).order_by('-timestamp').first()
            
            if not latest_data:
                return {
                    'is_valid': False,
                    'reason': 'No data found',
                    'data_age_hours': None,
                    'data_points': 0
                }
            
            data_age = timezone.now() - latest_data.timestamp
            data_age_hours = data_age.total_seconds() / 3600
            
            # Check data completeness
            recent_data = self.get_recent_market_data(symbol, hours_back=24)
            data_points = recent_data.count()
            
            # Validation criteria
            is_fresh = data_age_hours <= 2  # Data should be within 2 hours
            is_complete = data_points >= self.min_data_points
            
            return {
                'is_valid': is_fresh and is_complete,
                'reason': 'Valid' if (is_fresh and is_complete) else 'Invalid data',
                'data_age_hours': data_age_hours,
                'data_points': data_points,
                'is_fresh': is_fresh,
                'is_complete': is_complete
            }
            
        except Exception as e:
            logger.error(f"Error validating data quality for {symbol.symbol}: {e}")
            return {
                'is_valid': False,
                'reason': f'Validation error: {e}',
                'data_age_hours': None,
                'data_points': 0
            }


class DatabaseTechnicalAnalysis:
    """Calculate technical indicators from database data"""
    
    def __init__(self):
        self.indicators_cache_timeout = 1800  # 30 minutes
    
    def calculate_indicators_from_database(self, symbol: Symbol, hours_back: int = 168) -> Optional[Dict]:
        """Calculate indicators using database data (default: 1 week)"""
        try:
            # Get market data
            market_data = MarketData.objects.filter(
                symbol=symbol,
                timeframe='1h',
                timestamp__gte=timezone.now() - timedelta(hours=hours_back)
            ).order_by('timestamp')
            
            if market_data.count() < 20:
                logger.warning(f"Insufficient data for {symbol.symbol}: {market_data.count()} points")
                return None
            
            # Convert to DataFrame
            df = self._market_data_to_dataframe(market_data)
            if df is None:
                return None
            
            # Calculate indicators
            indicators = self._calculate_all_indicators(df)
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol.symbol}: {e}")
            return None
    
    def _market_data_to_dataframe(self, market_data) -> Optional[pd.DataFrame]:
        """Convert market data QuerySet to pandas DataFrame"""
        try:
            data = []
            for record in market_data:
                data.append({
                    'timestamp': record.timestamp,
                    'open': float(record.open_price),
                    'high': float(record.high_price),
                    'low': float(record.low_price),
                    'close': float(record.close_price),
                    'volume': float(record.volume) if record.volume else 0
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error converting market data to DataFrame: {e}")
            return None
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate all technical indicators"""
        indicators = {}
        
        try:
            # Moving averages
            indicators['sma_20'] = df['close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else None
            indicators['sma_50'] = df['close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else None
            indicators['ema_12'] = df['close'].ewm(span=12).mean().iloc[-1]
            indicators['ema_26'] = df['close'].ewm(span=26).mean().iloc[-1]
            
            # RSI
            indicators['rsi'] = self._calculate_rsi(df['close'], 14)
            
            # MACD
            macd_line, signal_line, histogram = self._calculate_macd(df['close'])
            indicators['macd'] = macd_line.iloc[-1] if not macd_line.empty else None
            indicators['macd_signal'] = signal_line.iloc[-1] if not signal_line.empty else None
            indicators['macd_histogram'] = histogram.iloc[-1] if not histogram.empty else None
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(df['close'])
            indicators['bb_upper'] = bb_upper.iloc[-1] if not bb_upper.empty else None
            indicators['bb_middle'] = bb_middle.iloc[-1] if not bb_middle.empty else None
            indicators['bb_lower'] = bb_lower.iloc[-1] if not bb_lower.empty else None
            
            # Volume indicators
            indicators['volume_sma'] = df['volume'].rolling(20).mean().iloc[-1] if len(df) >= 20 else None
            indicators['volume_ratio'] = df['volume'].iloc[-1] / indicators['volume_sma'] if indicators['volume_sma'] else None
            
            # Price change indicators
            indicators['price_change_1h'] = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100) if len(df) >= 2 else None
            indicators['price_change_24h'] = ((df['close'].iloc[-1] - df['close'].iloc[-24]) / df['close'].iloc[-24] * 100) if len(df) >= 24 else None
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}
        
        return indicators
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate RSI indicator"""
        try:
            if len(prices) < period + 1:
                return None
            
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.iloc[-1] if not rsi.empty else None
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None
    
    def _calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        try:
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return upper_band, sma, lower_band
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return pd.Series(), pd.Series(), pd.Series()


# Global instance
database_signal_service = DatabaseSignalService()
database_technical_analysis = DatabaseTechnicalAnalysis()














