import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import numpy as np
from django.utils import timezone
from django.db.models import Q, Avg, Count, Max, Min
from django.conf import settings

from apps.signals.models import (
    TradingSignal, SignalType, SignalFactor, SignalFactorContribution,
    MarketRegime, SignalPerformance, SignalAlert
)
from apps.trading.models import Symbol
from apps.data.models import TechnicalIndicator, MarketData
from apps.data.services import EconomicDataService, SectorAnalysisService
from apps.sentiment.models import SentimentAggregate, CryptoMention
from apps.signals.strategies import MovingAverageCrossoverStrategy, RSIStrategy, MACDStrategy, BollingerBandsStrategy, BreakoutStrategy, MeanReversionStrategy

logger = logging.getLogger(__name__)


class SignalGenerationService:
    """Main service for generating trading signals"""
    
    def __init__(self):
        self.min_confidence_threshold = 0.7  # 70% minimum confidence
        self.min_risk_reward_ratio = 3.0     # 3:1 minimum risk-reward
        self.signal_expiry_hours = 24        # Signal expires in 24 hours
        
        # Initialize trading strategies
        self.ma_crossover_strategy = MovingAverageCrossoverStrategy()
        self.rsi_strategy = RSIStrategy()
        self.macd_strategy = MACDStrategy()
        self.bb_strategy = BollingerBandsStrategy()
        self.breakout_strategy = BreakoutStrategy()
        self.mean_reversion_strategy = MeanReversionStrategy()
        
        # Initialize economic data service
        self.economic_service = EconomicDataService()
        
        # Initialize sector analysis service
        self.sector_service = SectorAnalysisService()
        
    def generate_signals_for_symbol(self, symbol: Symbol) -> List[TradingSignal]:
        """Generate signals for a specific symbol"""
        logger.info(f"Generating signals for {symbol.symbol}")
        
        signals = []
        
        # Get latest market data and indicators
        market_data = self._get_latest_market_data(symbol)
        if not market_data:
            logger.warning(f"No market data available for {symbol.symbol}")
            return signals
        
        # Get sentiment data
        sentiment_data = self._get_latest_sentiment_data(symbol)
        
        # Calculate technical scores
        technical_score = self._calculate_technical_score(symbol)
        
        # Calculate sentiment scores
        sentiment_score = self._calculate_sentiment_score(sentiment_data)
        
        # Calculate news impact
        news_score = self._calculate_news_score(symbol)
        
        # Calculate volume analysis
        volume_score = self._calculate_volume_score(symbol)
        
        # Calculate pattern recognition
        pattern_score = self._calculate_pattern_score(symbol)
        
        # Calculate economic/fundamental score
        economic_score = self._calculate_economic_score(symbol)
        
        # Calculate sector analysis score
        sector_score = self._calculate_sector_score(symbol)
        
        # Generate signals based on combined analysis
        signals.extend(self._generate_buy_signals(
            symbol, market_data, technical_score, sentiment_score, 
            news_score, volume_score, pattern_score, economic_score, sector_score
        ))
        
        signals.extend(self._generate_sell_signals(
            symbol, market_data, technical_score, sentiment_score,
            news_score, volume_score, pattern_score, economic_score, sector_score
        ))
        
        # Generate signals from trading strategies
        ma_strategy_signals = self.ma_crossover_strategy.generate_signals(symbol)
        signals.extend(ma_strategy_signals)
        
        rsi_strategy_signals = self.rsi_strategy.generate_signals(symbol)
        signals.extend(rsi_strategy_signals)
        
        macd_strategy_signals = self.macd_strategy.generate_signals(symbol)
        signals.extend(macd_strategy_signals)
        
        # Generate signals from Bollinger Bands strategy
        bb_strategy_signals = self.bb_strategy.generate_signals(symbol)
        signals.extend(bb_strategy_signals)
        
        # Generate signals from Breakout strategy
        breakout_strategy_signals = self.breakout_strategy.generate_signals(symbol)
        signals.extend(breakout_strategy_signals)
        
        # Generate signals from Mean Reversion strategy
        mean_reversion_signals = self.mean_reversion_strategy.generate_signals(symbol)
        signals.extend(mean_reversion_signals)
        
        # Filter signals by quality criteria
        filtered_signals = self._filter_signals_by_quality(signals)
        
        logger.info(f"Generated {len(filtered_signals)} quality signals for {symbol.symbol}")
        return filtered_signals
    
    def _get_latest_market_data(self, symbol: Symbol) -> Optional[Dict]:
        """Get latest market data for signal generation"""
        try:
            latest_data = MarketData.objects.filter(
                symbol=symbol
            ).order_by('-timestamp').first()
            
            if not latest_data:
                return None
            
            return {
                'close_price': float(latest_data.close_price),
                'high_price': float(latest_data.high_price),
                'low_price': float(latest_data.low_price),
                'volume': float(latest_data.volume),
                'timestamp': latest_data.timestamp
            }
        except Exception as e:
            logger.error(f"Error getting market data for {symbol.symbol}: {e}")
            return None
    
    def _get_latest_sentiment_data(self, symbol: Symbol) -> Optional[Dict]:
        """Get latest sentiment data for signal generation"""
        try:
            latest_sentiment = SentimentAggregate.objects.filter(
                asset=symbol,
                timeframe='1h'
            ).order_by('-created_at').first()
            
            if not latest_sentiment:
                return None
            
            return {
                'combined_score': latest_sentiment.combined_sentiment_score,
                'social_score': latest_sentiment.social_sentiment_score,
                'news_score': latest_sentiment.news_sentiment_score,
                'confidence_score': latest_sentiment.confidence_score,
                'total_mentions': latest_sentiment.total_mentions
            }
        except Exception as e:
            logger.error(f"Error getting sentiment data for {symbol.symbol}: {e}")
            return None
    
    def _calculate_technical_score(self, symbol: Symbol) -> float:
        """Calculate technical analysis score (-1 to 1)"""
        try:
            # Get latest technical indicators
            indicators = TechnicalIndicator.objects.filter(
                symbol=symbol
            ).order_by('-timestamp')[:10]  # Last 10 indicators
            
            if not indicators.exists():
                return 0.0
            
            # Calculate RSI score
            rsi_indicators = indicators.filter(indicator_type='RSI')
            rsi_score = 0.0
            if rsi_indicators.exists():
                latest_rsi = float(rsi_indicators.first().value)
                if latest_rsi < 30:
                    rsi_score = 0.8  # Oversold - bullish
                elif latest_rsi > 70:
                    rsi_score = -0.8  # Overbought - bearish
                else:
                    rsi_score = (latest_rsi - 50) / 50  # Normalized
            
            # Calculate MACD score
            macd_indicators = indicators.filter(indicator_type='MACD')
            macd_score = 0.0
            if macd_indicators.exists():
                latest_macd = float(macd_indicators.first().value)
                macd_score = np.tanh(latest_macd)  # Normalize to -1 to 1
            
            # Calculate moving average score
            sma_indicators = indicators.filter(indicator_type='SMA')
            ema_indicators = indicators.filter(indicator_type='EMA')
            ma_score = 0.0
            if sma_indicators.exists() and ema_indicators.exists():
                sma_value = float(sma_indicators.first().value)
                ema_value = float(ema_indicators.first().value)
                if ema_value > sma_value:
                    ma_score = 0.6  # Bullish crossover
                else:
                    ma_score = -0.6  # Bearish crossover
            
            # Combine technical scores
            technical_score = (rsi_score * 0.3 + macd_score * 0.4 + ma_score * 0.3)
            return max(-1.0, min(1.0, technical_score))
            
        except Exception as e:
            logger.error(f"Error calculating technical score for {symbol.symbol}: {e}")
            return 0.0
    
    def _calculate_sentiment_score(self, sentiment_data: Optional[Dict]) -> float:
        """Calculate sentiment analysis score (-1 to 1)"""
        if not sentiment_data:
            return 0.0
        
        try:
            # Combine sentiment scores with weights
            combined_score = sentiment_data['combined_score']
            social_score = sentiment_data['social_score']
            news_score = sentiment_data['news_score']
            confidence = sentiment_data['confidence_score']
            
            # Weighted sentiment score
            sentiment_score = (
                combined_score * 0.5 +
                social_score * 0.3 +
                news_score * 0.2
            ) * confidence
            
            return max(-1.0, min(1.0, sentiment_score))
            
        except Exception as e:
            logger.error(f"Error calculating sentiment score: {e}")
            return 0.0
    
    def _calculate_news_score(self, symbol: Symbol) -> float:
        """Calculate news impact score (-1 to 1)"""
        try:
            # Get recent news mentions
            recent_mentions = CryptoMention.objects.filter(
                asset=symbol,
                mention_type='news',
                created_at__gte=timezone.now() - timedelta(hours=24)
            )
            
            if not recent_mentions.exists():
                return 0.0
            
            # Calculate weighted news score
            total_score = 0.0
            total_weight = 0.0
            
            for mention in recent_mentions:
                weight = mention.impact_weight
                score = mention.sentiment_score
                total_score += score * weight
                total_weight += weight
            
            if total_weight > 0:
                news_score = total_score / total_weight
                return max(-1.0, min(1.0, news_score))
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating news score for {symbol.symbol}: {e}")
            return 0.0
    
    def _calculate_volume_score(self, symbol: Symbol) -> float:
        """Calculate volume analysis score (-1 to 1)"""
        try:
            # Get recent volume data
            recent_data = MarketData.objects.filter(
                symbol=symbol
            ).order_by('-timestamp')[:20]  # Last 20 data points
            
            if not recent_data.exists():
                return 0.0
            
            volumes = [float(data.volume) for data in recent_data]
            avg_volume = np.mean(volumes)
            current_volume = volumes[0]
            
            # Volume ratio
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Normalize to -1 to 1
            volume_score = np.tanh((volume_ratio - 1.0) * 2)
            
            return volume_score
            
        except Exception as e:
            logger.error(f"Error calculating volume score for {symbol.symbol}: {e}")
            return 0.0
    
    def _calculate_pattern_score(self, symbol: Symbol) -> float:
        """Calculate pattern recognition score (-1 to 1)"""
        try:
            # Get recent price data for pattern analysis
            recent_data = MarketData.objects.filter(
                symbol=symbol
            ).order_by('-timestamp')[:50]  # Last 50 data points
            
            if not recent_data.exists() or len(recent_data) < 20:
                return 0.0
            
            prices = [float(data.close_price) for data in recent_data]
            
            # Simple pattern detection
            # Check for bullish/bearish patterns
            pattern_score = 0.0
            
            # Higher highs and higher lows (bullish)
            if len(prices) >= 10:
                highs = [max(prices[i:i+5]) for i in range(0, len(prices)-5, 5)]
                lows = [min(prices[i:i+5]) for i in range(0, len(prices)-5, 5)]
                
                if len(highs) >= 2 and len(lows) >= 2:
                    if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
                        pattern_score = 0.6  # Bullish pattern
                    elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
                        pattern_score = -0.6  # Bearish pattern
            
            return pattern_score
            
        except Exception as e:
            logger.error(f"Error calculating pattern score for {symbol.symbol}: {e}")
            return 0.0
    
    def _calculate_economic_score(self, symbol: Symbol) -> float:
        """Calculate economic/fundamental analysis score (-1 to 1)"""
        try:
            # Determine the country/region for the symbol
            # For crypto, we'll primarily use US economic data
            # as it's the global reserve currency and affects crypto markets
            country = 'US'
            
            # Get market impact score from economic service
            economic_impact = self.economic_service.get_market_impact_score(country)
            
            # Check for upcoming high-impact events
            upcoming_events = self.economic_service.check_upcoming_events(days_ahead=3)
            
            event_impact = 0.0
            if upcoming_events:
                for event in upcoming_events:
                    if event.impact_level in ['HIGH', 'CRITICAL']:
                        event_analysis = self.economic_service.analyze_event_impact(event)
                        if event_analysis:
                            # Weight by time proximity (closer events have more impact)
                            time_weight = max(0.1, 1.0 - (event_analysis.get('time_to_event', 72) / 72))
                            event_impact += event_analysis.get('market_impact', 0.0) * time_weight
            
            # Combine economic sentiment and event impact
            combined_economic_score = (economic_impact * 0.7) + (event_impact * 0.3)
            
            # Normalize to -1 to 1 range
            normalized_score = max(-1.0, min(1.0, combined_economic_score))
            
            logger.debug(f"Economic score for {symbol.symbol}: {normalized_score:.3f} "
                        f"(sentiment: {economic_impact:.3f}, events: {event_impact:.3f})")
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Error calculating economic score for {symbol.symbol}: {e}")
            return 0.0
    
    def _calculate_sector_score(self, symbol: Symbol) -> float:
        """Calculate sector analysis score (-1 to 1)"""
        try:
            # Get sector impact score from sector service
            sector_impact = self.sector_service.get_sector_impact_score(symbol)
            
            # Normalize to -1 to 1 range (sector_impact is already in this range)
            sector_score = max(-1.0, min(1.0, sector_impact))
            
            logger.debug(f"Sector score for {symbol.symbol}: {sector_score}")
            return sector_score
            
        except Exception as e:
            logger.error(f"Error calculating sector score for {symbol.symbol}: {e}")
            return 0.0
    
    def _generate_buy_signals(self, symbol: Symbol, market_data: Dict, 
                             technical_score: float, sentiment_score: float,
                             news_score: float, volume_score: float, 
                             pattern_score: float, economic_score: float, sector_score: float) -> List[TradingSignal]:
        """Generate buy signals based on analysis"""
        signals = []
        
        # Calculate combined score
        combined_score = (
            technical_score * 0.25 +
            sentiment_score * 0.20 +
            news_score * 0.15 +
            volume_score * 0.15 +
            pattern_score * 0.10 +
            economic_score * 0.10 +
            sector_score * 0.05
        )
        
        # Generate buy signal if conditions are met
        if combined_score > 0.3:  # Bullish threshold
            confidence_score = min(1.0, combined_score + 0.5)
            
            if confidence_score >= self.min_confidence_threshold:
                signal = self._create_signal(
                    symbol=symbol,
                    signal_type_name='BUY',
                    confidence_score=confidence_score,
                    market_data=market_data,
                    technical_score=technical_score,
                    sentiment_score=sentiment_score,
                    news_score=news_score,
                    volume_score=volume_score,
                    pattern_score=pattern_score,
                    economic_score=economic_score,
                    sector_score=sector_score
                )
                
                if signal:
                    signals.append(signal)
        
        # Generate strong buy signal
        if combined_score > 0.6:
            confidence_score = min(1.0, combined_score + 0.3)
            
            if confidence_score >= self.min_confidence_threshold:
                signal = self._create_signal(
                    symbol=symbol,
                    signal_type_name='STRONG_BUY',
                    confidence_score=confidence_score,
                    market_data=market_data,
                    technical_score=technical_score,
                    sentiment_score=sentiment_score,
                    news_score=news_score,
                    volume_score=volume_score,
                    pattern_score=pattern_score,
                    economic_score=economic_score,
                    sector_score=sector_score
                )
                
                if signal:
                    signals.append(signal)
        
        return signals
    
    def _generate_sell_signals(self, symbol: Symbol, market_data: Dict,
                              technical_score: float, sentiment_score: float,
                              news_score: float, volume_score: float,
                              pattern_score: float, economic_score: float, sector_score: float) -> List[TradingSignal]:
        """Generate sell signals based on analysis"""
        signals = []
        
        # Calculate combined score
        combined_score = (
            technical_score * 0.25 +
            sentiment_score * 0.20 +
            news_score * 0.15 +
            volume_score * 0.15 +
            pattern_score * 0.10 +
            economic_score * 0.10 +
            sector_score * 0.05
        )
        
        # Generate sell signal if conditions are met
        if combined_score < -0.3:  # Bearish threshold
            confidence_score = min(1.0, abs(combined_score) + 0.5)
            
            if confidence_score >= self.min_confidence_threshold:
                signal = self._create_signal(
                    symbol=symbol,
                    signal_type_name='SELL',
                    confidence_score=confidence_score,
                    market_data=market_data,
                    technical_score=technical_score,
                    sentiment_score=sentiment_score,
                    news_score=news_score,
                    volume_score=volume_score,
                    pattern_score=pattern_score,
                    economic_score=economic_score,
                    sector_score=sector_score
                )
                
                if signal:
                    signals.append(signal)
        
        # Generate strong sell signal
        if combined_score < -0.6:
            confidence_score = min(1.0, abs(combined_score) + 0.3)
            
            if confidence_score >= self.min_confidence_threshold:
                signal = self._create_signal(
                    symbol=symbol,
                    signal_type_name='STRONG_SELL',
                    confidence_score=confidence_score,
                    market_data=market_data,
                    technical_score=technical_score,
                    sentiment_score=sentiment_score,
                    news_score=news_score,
                    volume_score=volume_score,
                    pattern_score=pattern_score,
                    economic_score=economic_score,
                    sector_score=sector_score
                )
                
                if signal:
                    signals.append(signal)
        
        return signals
    
    def _create_signal(self, symbol: Symbol, signal_type_name: str,
                      confidence_score: float, market_data: Dict,
                      technical_score: float, sentiment_score: float,
                      news_score: float, volume_score: float,
                      pattern_score: float, economic_score: float, sector_score: float) -> Optional[TradingSignal]:
        """Create a trading signal with all details"""
        try:
            # Get signal type
            signal_type, created = SignalType.objects.get_or_create(
                name=signal_type_name,
                defaults={'description': f'{signal_type_name} signal'}
            )
            
            # Calculate signal strength
            if confidence_score >= 0.9:
                strength = 'VERY_STRONG'
            elif confidence_score >= 0.8:
                strength = 'STRONG'
            elif confidence_score >= 0.7:
                strength = 'MODERATE'
            else:
                strength = 'WEAK'
            
            # Calculate confidence level
            if confidence_score >= 0.85:
                confidence_level = 'VERY_HIGH'
            elif confidence_score >= 0.7:
                confidence_level = 'HIGH'
            elif confidence_score >= 0.5:
                confidence_level = 'MEDIUM'
            else:
                confidence_level = 'LOW'
            
            # Calculate entry price and targets
            entry_price = Decimal(str(market_data['close_price']))
            
            # Calculate target price based on signal type
            if signal_type_name in ['BUY', 'STRONG_BUY']:
                target_price = entry_price * Decimal('1.05')  # 5% target
                stop_loss = entry_price * Decimal('0.97')    # 3% stop loss
            else:
                target_price = entry_price * Decimal('0.95')  # 5% target
                stop_loss = entry_price * Decimal('1.03')    # 3% stop loss
            
            # Calculate risk-reward ratio
            risk = abs(float(entry_price - stop_loss))
            reward = abs(float(target_price - entry_price))
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            # Calculate quality score
            quality_score = (
                confidence_score * 0.4 +
                (1.0 if risk_reward_ratio >= self.min_risk_reward_ratio else 0.0) * 0.25 +
                (technical_score + 1.0) / 2.0 * 0.15 +
                (sentiment_score + 1.0) / 2.0 * 0.08 +
                (economic_score + 1.0) / 2.0 * 0.07 +
                (sector_score + 1.0) / 2.0 * 0.05
            )
            
            # Create signal
            signal = TradingSignal.objects.create(
                symbol=symbol,
                signal_type=signal_type,
                strength=strength,
                confidence_score=confidence_score,
                confidence_level=confidence_level,
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                risk_reward_ratio=risk_reward_ratio,
                quality_score=quality_score,
                expires_at=timezone.now() + timedelta(hours=self.signal_expiry_hours),
                technical_score=technical_score,
                sentiment_score=sentiment_score,
                news_score=news_score,
                volume_score=volume_score,
                pattern_score=pattern_score,
                economic_score=economic_score,
                sector_score=sector_score
            )
            
            # Create factor contributions
            self._create_factor_contributions(signal, {
                'technical': technical_score,
                'sentiment': sentiment_score,
                'news': news_score,
                'volume': volume_score,
                'pattern': pattern_score,
                'economic': economic_score,
                'sector': sector_score
            })
            
            # Create alert
            self._create_signal_alert(signal)
            
            return signal
            
        except Exception as e:
            logger.error(f"Error creating signal for {symbol.symbol}: {e}")
            return None
    
    def _create_factor_contributions(self, signal: TradingSignal, scores: Dict):
        """Create factor contribution records"""
        try:
            factors = {
                'technical': SignalFactor.objects.get_or_create(
                    name='Technical Analysis',
                    factor_type='TECHNICAL',
                    defaults={'weight': 0.35, 'description': 'Technical indicators analysis'}
                )[0],
                'sentiment': SignalFactor.objects.get_or_create(
                    name='Sentiment Analysis',
                    factor_type='SENTIMENT',
                    defaults={'weight': 0.25, 'description': 'Social media and news sentiment'}
                )[0],
                'news': SignalFactor.objects.get_or_create(
                    name='News Impact',
                    factor_type='NEWS',
                    defaults={'weight': 0.15, 'description': 'News event impact analysis'}
                )[0],
                'volume': SignalFactor.objects.get_or_create(
                    name='Volume Analysis',
                    factor_type='VOLUME',
                    defaults={'weight': 0.15, 'description': 'Volume pattern analysis'}
                )[0],
                'pattern': SignalFactor.objects.get_or_create(
                    name='Pattern Recognition',
                    factor_type='PATTERN',
                    defaults={'weight': 0.10, 'description': 'Chart pattern analysis'}
                )[0],
                'economic': SignalFactor.objects.get_or_create(
                    name='Economic Analysis',
                    factor_type='ECONOMIC',
                    defaults={'weight': 0.10, 'description': 'Economic and fundamental analysis'}
                )[0],
                'sector': SignalFactor.objects.get_or_create(
                    name='Sector Analysis',
                    factor_type='SECTOR',
                    defaults={'weight': 0.05, 'description': 'Sector momentum and rotation analysis'}
                )[0]
            }
            
            for factor_name, factor in factors.items():
                score = scores.get(factor_name, 0.0)
                contribution = score * factor.weight
                
                SignalFactorContribution.objects.create(
                    signal=signal,
                    factor=factor,
                    score=score,
                    weight=factor.weight,
                    contribution=contribution,
                    details={'factor_type': factor.factor_type}
                )
                
        except Exception as e:
            logger.error(f"Error creating factor contributions for signal {signal.id}: {e}")
    
    def _create_signal_alert(self, signal: TradingSignal):
        """Create alert for new signal"""
        try:
            SignalAlert.objects.create(
                alert_type='SIGNAL_GENERATED',
                priority='HIGH' if signal.confidence_score >= 0.8 else 'MEDIUM',
                title=f"New {signal.signal_type.name} Signal for {signal.symbol.symbol}",
                message=f"Confidence: {signal.confidence_score:.2%}, Quality: {signal.quality_score:.2%}",
                signal=signal
            )
        except Exception as e:
            logger.error(f"Error creating signal alert: {e}")
    
    def _filter_signals_by_quality(self, signals: List[TradingSignal]) -> List[TradingSignal]:
        """Filter signals by quality criteria"""
        filtered_signals = []
        
        for signal in signals:
            # Check minimum confidence
            if signal.confidence_score < self.min_confidence_threshold:
                continue
            
            # Check risk-reward ratio
            if signal.risk_reward_ratio and signal.risk_reward_ratio < self.min_risk_reward_ratio:
                continue
            
            # Check quality score
            if signal.quality_score < 0.6:
                continue
            
            filtered_signals.append(signal)
        
        return filtered_signals


class MarketRegimeService:
    """Service for market regime detection and classification"""
    
    def __init__(self):
        self.volatility_window = 20  # Days for volatility calculation
        self.trend_window = 50       # Days for trend calculation
    
    def detect_market_regime(self, symbol: Symbol) -> Optional[MarketRegime]:
        """Detect current market regime for a symbol"""
        try:
            # Get historical data
            historical_data = MarketData.objects.filter(
                symbol=symbol
            ).order_by('-timestamp')[:self.trend_window]
            
            if not historical_data.exists():
                return None
            
            # Calculate volatility
            prices = [float(data.close_price) for data in historical_data]
            returns = np.diff(np.log(prices))
            volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
            
            # Calculate trend strength
            trend_strength = self._calculate_trend_strength(prices)
            
            # Classify regime
            regime_name, confidence = self._classify_regime(volatility, trend_strength)
            
            # Create regime record
            regime = MarketRegime.objects.create(
                name=regime_name,
                volatility_level=min(1.0, volatility),
                trend_strength=trend_strength,
                confidence=confidence,
                description=f"Detected {regime_name} regime for {symbol.symbol}"
            )
            
            return regime
            
        except Exception as e:
            logger.error(f"Error detecting market regime for {symbol.symbol}: {e}")
            return None
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength (-1 to 1)"""
        try:
            if len(prices) < 10:
                return 0.0
            
            # Linear regression slope
            x = np.arange(len(prices))
            slope = np.polyfit(x, prices, 1)[0]
            
            # Normalize slope to -1 to 1
            max_slope = np.std(prices) * 2
            trend_strength = np.tanh(slope / max_slope) if max_slope > 0 else 0.0
            
            return trend_strength
            
        except Exception as e:
            logger.error(f"Error calculating trend strength: {e}")
            return 0.0
    
    def _classify_regime(self, volatility: float, trend_strength: float) -> Tuple[str, float]:
        """Classify market regime based on volatility and trend"""
        try:
            # High volatility threshold
            high_vol_threshold = 0.4
            
            # Strong trend threshold
            strong_trend_threshold = 0.3
            
            if volatility > high_vol_threshold:
                if abs(trend_strength) > strong_trend_threshold:
                    if trend_strength > 0:
                        return 'BULL', 0.8
                    else:
                        return 'BEAR', 0.8
                else:
                    return 'VOLATILE', 0.9
            else:
                if abs(trend_strength) > strong_trend_threshold:
                    if trend_strength > 0:
                        return 'BULL', 0.7
                    else:
                        return 'BEAR', 0.7
                else:
                    return 'SIDEWAYS', 0.6
                    
        except Exception as e:
            logger.error(f"Error classifying regime: {e}")
            return 'SIDEWAYS', 0.5


class SignalPerformanceService:
    """Service for tracking signal performance"""
    
    def calculate_performance_metrics(self, period_type: str = '1D') -> Dict:
        """Calculate performance metrics for signals"""
        try:
            # Get date range
            end_date = timezone.now()
            if period_type == '1H':
                start_date = end_date - timedelta(hours=1)
            elif period_type == '4H':
                start_date = end_date - timedelta(hours=4)
            elif period_type == '1D':
                start_date = end_date - timedelta(days=1)
            elif period_type == '1W':
                start_date = end_date - timedelta(weeks=1)
            elif period_type == '1M':
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=1)
            
            # Get signals in period
            signals = TradingSignal.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                is_executed=True
            )
            
            if not signals.exists():
                return self._empty_performance_metrics()
            
            # Calculate metrics
            total_signals = signals.count()
            profitable_signals = signals.filter(is_profitable=True).count()
            win_rate = profitable_signals / total_signals if total_signals > 0 else 0.0
            
            # Calculate profit/loss metrics
            profits = signals.filter(is_profitable=True).aggregate(
                avg_profit=Avg('profit_loss')
            )['avg_profit'] or Decimal('0')
            
            losses = signals.filter(is_profitable=False).aggregate(
                avg_loss=Avg('profit_loss')
            )['avg_loss'] or Decimal('0')
            
            profit_factor = abs(profits / losses) if losses != 0 else 0.0
            
            # Calculate quality metrics
            avg_confidence = signals.aggregate(
                avg_confidence=Avg('confidence_score')
            )['avg_confidence'] or 0.0
            
            avg_quality = signals.aggregate(
                avg_quality=Avg('quality_score')
            )['avg_quality'] or 0.0
            
            # Create performance record
            performance = SignalPerformance.objects.create(
                period_type=period_type,
                start_date=start_date,
                end_date=end_date,
                total_signals=total_signals,
                profitable_signals=profitable_signals,
                win_rate=win_rate,
                average_profit=profits,
                average_loss=abs(losses),
                profit_factor=profit_factor,
                average_confidence=avg_confidence,
                average_quality_score=avg_quality
            )
            
            return {
                'period_type': period_type,
                'total_signals': total_signals,
                'profitable_signals': profitable_signals,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'average_confidence': avg_confidence,
                'average_quality': avg_quality
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return self._empty_performance_metrics()
    
    def _empty_performance_metrics(self) -> Dict:
        """Return empty performance metrics"""
        return {
            'period_type': '1D',
            'total_signals': 0,
            'profitable_signals': 0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'average_confidence': 0.0,
            'average_quality': 0.0
        }
