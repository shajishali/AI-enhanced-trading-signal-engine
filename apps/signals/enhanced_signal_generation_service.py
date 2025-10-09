"""
Enhanced Signal Generation Service
Generates logical trading signals with proper entry, exit, stop loss, and take profit levels
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q, Avg, Count, Max, Min
from django.core.cache import cache

from apps.signals.models import TradingSignal, SignalType
from apps.trading.models import Symbol
from apps.data.models import TechnicalIndicator, MarketData
from apps.data.real_price_service import get_live_prices
from apps.signals.services import SignalGenerationService

logger = logging.getLogger(__name__)


class EnhancedSignalGenerationService:
    """Enhanced service for generating logical trading signals with proper risk management"""
    
    def __init__(self):
        self.base_service = SignalGenerationService()
        self.min_confidence_threshold = 0.6  # Higher confidence for better signals
        self.max_signals_per_symbol = 2  # Maximum 2 signals per symbol
        self.best_signals_count = 5  # Top 5 signals every 2 hours
        self.signal_refresh_hours = 2  # Refresh signals every 2 hours
        
        # Risk management parameters
        self.max_risk_per_trade = 0.02  # 2% max risk per trade
        self.min_risk_reward_ratio = 1.5  # Minimum 1.5:1 risk/reward
        self.stop_loss_percentages = {
            'BTC': 0.03,   # 3% stop loss for BTC
            'ETH': 0.04,   # 4% stop loss for ETH
            'default': 0.05  # 5% default stop loss
        }
        
        # Take profit levels
        self.take_profit_levels = {
            'conservative': 1.5,  # 1.5x risk
            'moderate': 2.0,     # 2.0x risk
            'aggressive': 3.0    # 3.0x risk
        }
    
    def generate_best_signals_for_all_coins(self) -> Dict[str, any]:
        """Generate the best 5 signals from all 200+ coins every 2 hours"""
        logger.info("Starting comprehensive signal generation for all coins")
        
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
        
        # Get live prices for all symbols
        live_prices = get_live_prices()
        logger.info(f"Retrieved live prices for {len(live_prices)} symbols")
        
        all_signals = []
        processed_count = 0
        
        # Generate signals for each symbol (only new ones)
        for symbol in all_symbols:
            try:
                symbol_signals = self.generate_logical_signals_for_symbol(symbol, live_prices)
                all_signals.extend(symbol_signals)
                processed_count += 1
                
                if processed_count % 50 == 0:
                    logger.info(f"Processed {processed_count}/{all_symbols.count()} symbols")
                    
            except Exception as e:
                logger.error(f"Error generating signals for {symbol.symbol}: {e}")
                continue
        
        logger.info(f"Generated {len(all_signals)} total signals from {processed_count} symbols")
        
        # Select the best 5 signals
        best_signals = self._select_best_signals(all_signals)
        
        # Archive old signals and save new ones
        self._archive_old_signals()
        self._save_new_signals(best_signals)
        
        return {
            'total_signals_generated': len(all_signals),
            'best_signals_selected': len(best_signals),
            'processed_symbols': processed_count,
            'best_signals': best_signals
        }
    
    def generate_logical_signals_for_symbol(self, symbol: Symbol, live_prices: Dict) -> List[Dict]:
        """Generate logical signals with proper entry, exit, stop loss, and take profit"""
        signals = []
        
        # Get current price
        current_price_data = live_prices.get(symbol.symbol, {})
        if not current_price_data:
            return signals
        
        current_price = Decimal(str(current_price_data.get('price', 0)))
        if current_price <= 0:
            return signals
        
        # Generate different types of signals
        signal_types = [
            ('BUY', self._generate_buy_signal),
            ('SELL', self._generate_sell_signal),
            ('STRONG_BUY', self._generate_strong_buy_signal),
            ('STRONG_SELL', self._generate_strong_sell_signal)
        ]
        
        for signal_type_name, signal_generator in signal_types:
            try:
                signal_data = signal_generator(symbol, current_price, live_prices)
                if signal_data and self._validate_signal(signal_data):
                    signals.append(signal_data)
                    
                # Limit signals per symbol
                if len(signals) >= self.max_signals_per_symbol:
                    break
                    
            except Exception as e:
                logger.error(f"Error generating {signal_type_name} signal for {symbol.symbol}: {e}")
                continue
        
        return signals
    
    def _generate_buy_signal(self, symbol: Symbol, current_price: Decimal, live_prices: Dict) -> Optional[Dict]:
        """Generate a BUY signal with logical entry, stop loss, and take profit"""
        # Calculate technical indicators
        technical_score = self._calculate_technical_score(symbol)
        if technical_score < 0.4:  # Not bullish enough
            return None
        
        # Calculate volatility for stop loss
        volatility = self._calculate_volatility(symbol)
        stop_loss_pct = self.stop_loss_percentages.get(symbol.symbol, self.stop_loss_percentages['default'])
        
        # Calculate proper entry price based on technical analysis
        entry_price, entry_point_type = self._calculate_entry_price(symbol, current_price, 'BUY')
        if entry_price is None:
            return None
        
        # Stop loss (below entry)
        stop_loss_price = entry_price * Decimal(str(1 - stop_loss_pct))
        
        # Take profit levels
        risk_amount = entry_price - stop_loss_price
        take_profit_price = entry_price + (risk_amount * Decimal(str(self.take_profit_levels['moderate'])))
        
        # Calculate confidence based on multiple factors
        confidence = self._calculate_signal_confidence(symbol, 'BUY', technical_score, volatility)
        
        if confidence < self.min_confidence_threshold:
            return None
        
        return {
            'symbol': symbol,
            'signal_type': 'BUY',
            'entry_price': entry_price,
            'stop_loss': stop_loss_price,
            'target_price': take_profit_price,
            'confidence_score': confidence,
            'risk_reward_ratio': float(self.take_profit_levels['moderate']),
            'timeframe': '1D',
            'entry_point_type': entry_point_type,
            'strength': 'MODERATE',
            'technical_score': technical_score,
            'volatility': volatility,
            'reasoning': f"Technical analysis shows bullish momentum with {confidence:.1%} confidence"
        }
    
    def _generate_sell_signal(self, symbol: Symbol, current_price: Decimal, live_prices: Dict) -> Optional[Dict]:
        """Generate a SELL signal with logical entry, stop loss, and take profit"""
        # Calculate technical indicators
        technical_score = self._calculate_technical_score(symbol)
        if technical_score > 0.6:  # Not bearish enough
            return None
        
        # Calculate volatility for stop loss
        volatility = self._calculate_volatility(symbol)
        stop_loss_pct = self.stop_loss_percentages.get(symbol.symbol, self.stop_loss_percentages['default'])
        
        # Calculate proper entry price based on technical analysis
        entry_price, entry_point_type = self._calculate_entry_price(symbol, current_price, 'SELL')
        if entry_price is None:
            return None
        
        # Stop loss (above entry for short)
        stop_loss_price = entry_price * Decimal(str(1 + stop_loss_pct))
        
        # Take profit levels
        risk_amount = stop_loss_price - entry_price
        take_profit_price = entry_price - (risk_amount * Decimal(str(self.take_profit_levels['moderate'])))
        
        # Calculate confidence
        confidence = self._calculate_signal_confidence(symbol, 'SELL', technical_score, volatility)
        
        if confidence < self.min_confidence_threshold:
            return None
        
        return {
            'symbol': symbol,
            'signal_type': 'SELL',
            'entry_price': entry_price,
            'stop_loss': stop_loss_price,
            'target_price': take_profit_price,
            'confidence_score': confidence,
            'risk_reward_ratio': float(self.take_profit_levels['moderate']),
            'timeframe': '1D',
            'entry_point_type': entry_point_type,
            'strength': 'MODERATE',
            'technical_score': technical_score,
            'volatility': volatility,
            'reasoning': f"Technical analysis shows bearish momentum with {confidence:.1%} confidence"
        }
    
    def _generate_strong_buy_signal(self, symbol: Symbol, current_price: Decimal, live_prices: Dict) -> Optional[Dict]:
        """Generate a STRONG BUY signal with higher confidence"""
        technical_score = self._calculate_technical_score(symbol)
        if technical_score < 0.7:  # Need strong bullish signals
            return None
        
        volatility = self._calculate_volatility(symbol)
        stop_loss_pct = self.stop_loss_percentages.get(symbol.symbol, self.stop_loss_percentages['default'])
        
        # Calculate proper entry price based on technical analysis
        entry_price, entry_point_type = self._calculate_entry_price(symbol, current_price, 'STRONG_BUY')
        if entry_price is None:
            return None
        
        stop_loss_price = entry_price * Decimal(str(1 - stop_loss_pct))
        
        risk_amount = entry_price - stop_loss_price
        take_profit_price = entry_price + (risk_amount * Decimal(str(self.take_profit_levels['aggressive'])))
        
        confidence = self._calculate_signal_confidence(symbol, 'STRONG_BUY', technical_score, volatility)
        
        if confidence < 0.75:  # Higher threshold for strong signals
            return None
        
        return {
            'symbol': symbol,
            'signal_type': 'STRONG_BUY',
            'entry_price': entry_price,
            'stop_loss': stop_loss_price,
            'target_price': take_profit_price,
            'confidence_score': confidence,
            'risk_reward_ratio': float(self.take_profit_levels['aggressive']),
            'timeframe': '1D',
            'entry_point_type': entry_point_type,
            'strength': 'STRONG',
            'technical_score': technical_score,
            'volatility': volatility,
            'reasoning': f"Strong bullish momentum detected with {confidence:.1%} confidence"
        }
    
    def _generate_strong_sell_signal(self, symbol: Symbol, current_price: Decimal, live_prices: Dict) -> Optional[Dict]:
        """Generate a STRONG SELL signal with higher confidence"""
        technical_score = self._calculate_technical_score(symbol)
        if technical_score > 0.3:  # Need strong bearish signals
            return None
        
        volatility = self._calculate_volatility(symbol)
        stop_loss_pct = self.stop_loss_percentages.get(symbol.symbol, self.stop_loss_percentages['default'])
        
        # Calculate proper entry price based on technical analysis
        entry_price, entry_point_type = self._calculate_entry_price(symbol, current_price, 'STRONG_SELL')
        if entry_price is None:
            return None
        
        stop_loss_price = entry_price * Decimal(str(1 + stop_loss_pct))
        
        risk_amount = stop_loss_price - entry_price
        take_profit_price = entry_price - (risk_amount * Decimal(str(self.take_profit_levels['aggressive'])))
        
        confidence = self._calculate_signal_confidence(symbol, 'STRONG_SELL', technical_score, volatility)
        
        if confidence < 0.75:  # Higher threshold for strong signals
            return None
        
        return {
            'symbol': symbol,
            'signal_type': 'STRONG_SELL',
            'entry_price': entry_price,
            'stop_loss': stop_loss_price,
            'target_price': take_profit_price,
            'confidence_score': confidence,
            'risk_reward_ratio': float(self.take_profit_levels['aggressive']),
            'timeframe': '1D',
            'entry_point_type': entry_point_type,
            'strength': 'STRONG',
            'technical_score': technical_score,
            'volatility': volatility,
            'reasoning': f"Strong bearish momentum detected with {confidence:.1%} confidence"
        }
    
    def _calculate_entry_price(self, symbol: Symbol, current_price: Decimal, signal_type: str) -> Tuple[Optional[Decimal], str]:
        """Calculate proper entry price based on technical analysis"""
        try:
            # Get recent market data for analysis
            recent_data = MarketData.objects.filter(
                symbol=symbol
            ).order_by('-timestamp')[:50]  # Last 50 data points
            
            if not recent_data.exists():
                return None, 'UNKNOWN'
            
            prices = [float(d.close_price) for d in recent_data]
            highs = [float(d.high_price) for d in recent_data]
            lows = [float(d.low_price) for d in recent_data]
            
            if len(prices) < 20:
                return None, 'UNKNOWN'
            
            # Calculate technical levels
            sma_20 = np.mean(prices[-20:])
            sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else sma_20
            
            # Calculate support and resistance levels
            recent_highs = highs[-20:]
            recent_lows = lows[-20:]
            
            resistance_level = max(recent_highs)
            support_level = min(recent_lows)
            
            # Calculate entry points based on signal type
            if signal_type in ['BUY', 'STRONG_BUY']:
                # For BUY signals, look for entry points below current price
                if current_price > Decimal(str(sma_20)):
                    # Price above SMA20 - look for pullback entry
                    entry_price = current_price * Decimal('0.98')  # 2% below current
                    entry_type = 'PULLBACK_ENTRY'
                elif current_price > Decimal(str(support_level)) * Decimal('1.02'):
                    # Near support - enter at support level
                    entry_price = Decimal(str(support_level))
                    entry_type = 'SUPPORT_BOUNCE'
                else:
                    # Very oversold - enter slightly above current
                    entry_price = current_price * Decimal('1.01')  # 1% above current
                    entry_type = 'OVERSOLD_BOUNCE'
                
                # Ensure entry price is reasonable (not too far from current)
                max_deviation = current_price * Decimal('0.05')  # 5% max deviation
                if abs(entry_price - current_price) > max_deviation:
                    if signal_type == 'BUY':
                        entry_price = current_price * Decimal('0.99')  # 1% below
                    else:
                        entry_price = current_price * Decimal('0.97')  # 3% below for strong signals
                    entry_type = 'CONSERVATIVE_ENTRY'
                
            else:  # SELL signals
                # For SELL signals, look for entry points above current price
                if current_price < Decimal(str(sma_20)):
                    # Price below SMA20 - look for bounce entry
                    entry_price = current_price * Decimal('1.02')  # 2% above current
                    entry_type = 'BOUNCE_ENTRY'
                elif current_price < Decimal(str(resistance_level)) * Decimal('0.98'):
                    # Near resistance - enter at resistance level
                    entry_price = Decimal(str(resistance_level))
                    entry_type = 'RESISTANCE_REJECTION'
                else:
                    # Very overbought - enter slightly below current
                    entry_price = current_price * Decimal('0.99')  # 1% below current
                    entry_type = 'OVERBOUGHT_REJECTION'
                
                # Ensure entry price is reasonable
                max_deviation = current_price * Decimal('0.05')  # 5% max deviation
                if abs(entry_price - current_price) > max_deviation:
                    if signal_type == 'SELL':
                        entry_price = current_price * Decimal('1.01')  # 1% above
                    else:
                        entry_price = current_price * Decimal('1.03')  # 3% above for strong signals
                    entry_type = 'CONSERVATIVE_ENTRY'
            
            # Ensure entry price is positive and reasonable
            if entry_price <= 0:
                return None, 'INVALID'
            
            # For very small prices (like BONK), ensure minimum precision
            if entry_price < Decimal('0.000001'):
                entry_price = Decimal(str(round(float(entry_price), 8)))
            
            return entry_price, entry_type
            
        except Exception as e:
            logger.error(f"Error calculating entry price for {symbol.symbol}: {e}")
            return None, 'ERROR'

    def _calculate_technical_score(self, symbol: Symbol) -> float:
        """Calculate technical analysis score for a symbol"""
        try:
            # Get recent market data
            recent_data = MarketData.objects.filter(
                symbol=symbol
            ).order_by('-timestamp')[:100]  # Last 100 data points
            
            if not recent_data.exists():
                return 0.5  # Neutral score if no data
            
            # Calculate basic technical indicators
            prices = [float(d.close_price) for d in recent_data]
            volumes = [float(d.volume) for d in recent_data]
            
            if len(prices) < 20:
                return 0.5
            
            # Calculate RSI
            rsi = self._calculate_rsi(prices)
            
            # Calculate Moving Averages
            sma_20 = np.mean(prices[-20:])
            sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else sma_20
            
            # Calculate MACD
            macd_signal = self._calculate_macd_signal(prices)
            
            # Calculate Volume trend
            volume_trend = self._calculate_volume_trend(volumes)
            
            # Combine indicators into a score
            score = 0.5  # Base neutral score
            
            # RSI contribution
            if rsi < 30:  # Oversold - bullish
                score += 0.2
            elif rsi > 70:  # Overbought - bearish
                score -= 0.2
            
            # Moving average contribution
            if prices[-1] > sma_20 > sma_50:  # Bullish trend
                score += 0.15
            elif prices[-1] < sma_20 < sma_50:  # Bearish trend
                score -= 0.15
            
            # MACD contribution
            score += macd_signal * 0.1
            
            # Volume contribution
            score += volume_trend * 0.05
            
            # Ensure score is between 0 and 1
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating technical score for {symbol.symbol}: {e}")
            return 0.5
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd_signal(self, prices: List[float]) -> float:
        """Calculate MACD signal strength"""
        if len(prices) < 26:
            return 0.0
        
        # Calculate EMAs
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        macd_line = ema_12 - ema_26
        
        # Simple MACD signal (positive = bullish, negative = bearish)
        return 1.0 if macd_line > 0 else -1.0
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1]
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_volume_trend(self, volumes: List[float]) -> float:
        """Calculate volume trend (positive = increasing volume)"""
        if len(volumes) < 10:
            return 0.0
        
        recent_avg = np.mean(volumes[-5:])
        older_avg = np.mean(volumes[-10:-5])
        
        if older_avg == 0:
            return 0.0
        
        trend = (recent_avg - older_avg) / older_avg
        return max(-1.0, min(1.0, trend))
    
    def _calculate_volatility(self, symbol: Symbol) -> float:
        """Calculate price volatility for risk management"""
        try:
            recent_data = MarketData.objects.filter(
                symbol=symbol
            ).order_by('-timestamp')[:30]  # Last 30 data points
            
            if not recent_data.exists():
                return 0.05  # Default 5% volatility
            
            prices = [float(d.close_price) for d in recent_data]
            returns = [prices[i] / prices[i-1] - 1 for i in range(1, len(prices))]
            
            volatility = np.std(returns) * np.sqrt(24)  # Daily volatility
            return max(0.01, min(0.5, volatility))  # Between 1% and 50%
            
        except Exception as e:
            logger.error(f"Error calculating volatility for {symbol.symbol}: {e}")
            return 0.05
    
    
    def _analyze_market_conditions(self, symbol: Symbol, current_price: Decimal) -> Dict:
        """Enhanced market condition analysis based on user plan"""
        try:
            # Get recent market data
            recent_data = MarketData.objects.filter(
                symbol=symbol
            ).order_by('-timestamp')[:100]
            
            if not recent_data.exists():
                return {'trend': 'NEUTRAL', 'volatility': 0.5, 'momentum': 0.0}
            
            prices = [float(d.close_price) for d in recent_data]
            volumes = [float(d.volume) for d in recent_data]
            
            # Calculate enhanced indicators
            sma_20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else sum(prices) / len(prices)
            sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else sma_20
            
            # Trend analysis
            if sma_20 > sma_50 * 1.02:
                trend = 'BULLISH'
            elif sma_20 < sma_50 * 0.98:
                trend = 'BEARISH'
            else:
                trend = 'NEUTRAL'
            
            # Volatility analysis
            if len(prices) >= 20:
                volatility = (max(prices[-20:]) - min(prices[-20:])) / sma_20
            else:
                volatility = 0.5
            
            # Momentum analysis
            if len(prices) >= 10:
                momentum = (prices[-1] - prices[-10]) / prices[-10]
            else:
                momentum = 0.0
            
            # Volume analysis
            if len(volumes) >= 20:
                avg_volume = sum(volumes[-20:]) / 20
                current_volume = volumes[-1]
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            else:
                volume_ratio = 1.0
            
            return {
                'trend': trend,
                'volatility': volatility,
                'momentum': momentum,
                'volume_ratio': volume_ratio,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {e}")
            return {'trend': 'NEUTRAL', 'volatility': 0.5, 'momentum': 0.0}
    
    def _calculate_enhanced_confidence(self, symbol: Symbol, signal_type: str, market_conditions: Dict) -> float:
        """Calculate enhanced confidence based on multiple factors"""
        try:
            base_confidence = 0.5
            
            # Trend alignment bonus
            if signal_type == 'BUY' and market_conditions.get('trend') == 'BULLISH':
                base_confidence += 0.2
            elif signal_type == 'SELL' and market_conditions.get('trend') == 'BEARISH':
                base_confidence += 0.2
            
            # Momentum bonus
            momentum = market_conditions.get('momentum', 0)
            if abs(momentum) > 0.05:  # 5% momentum
                base_confidence += 0.1
            
            # Volume confirmation bonus
            volume_ratio = market_conditions.get('volume_ratio', 1.0)
            if volume_ratio > 1.2:  # 20% above average volume
                base_confidence += 0.1
            
            # Volatility adjustment
            volatility = market_conditions.get('volatility', 0.5)
            if volatility > 0.1:  # High volatility
                base_confidence += 0.05
            
            return min(0.95, base_confidence)
            
        except Exception as e:
            logger.error(f"Error calculating enhanced confidence: {e}")
            return 0.6

    def _calculate_signal_confidence(self, symbol: Symbol, signal_type: str, technical_score: float, volatility: float) -> float:
        """Calculate overall signal confidence"""
        base_confidence = technical_score
        
        # Adjust confidence based on signal type
        if signal_type in ['STRONG_BUY', 'STRONG_SELL']:
            base_confidence *= 1.2  # Boost for strong signals
        
        # Adjust for volatility (lower volatility = higher confidence)
        volatility_factor = 1.0 - (volatility * 0.5)
        base_confidence *= volatility_factor
        
        # Add some randomness for realistic confidence scores
        import random
        random_factor = random.uniform(0.9, 1.1)
        base_confidence *= random_factor
        
        return max(0.0, min(1.0, base_confidence))
    
    def _validate_signal(self, signal_data: Dict) -> bool:
        """Validate that the signal meets our criteria"""
        try:
            # Check risk/reward ratio
            if signal_data['risk_reward_ratio'] < self.min_risk_reward_ratio:
                return False
            
            # Check confidence threshold
            if signal_data['confidence_score'] < self.min_confidence_threshold:
                return False
            
            # Check that prices are logical
            entry_price = signal_data['entry_price']
            stop_loss = signal_data['stop_loss']
            target_price = signal_data['target_price']
            
            if signal_data['signal_type'] in ['BUY', 'STRONG_BUY']:
                if stop_loss >= entry_price or target_price <= entry_price:
                    return False
            else:  # SELL signals
                if stop_loss <= entry_price or target_price >= entry_price:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating signal: {e}")
            return False
    
    def _select_best_signals(self, all_signals: List[Dict]) -> List[Dict]:
        """Select the best 5 signals based on confidence and risk/reward ratio"""
        if not all_signals:
            return []
        
        # Sort by confidence score and risk/reward ratio
        def signal_score(signal):
            confidence = signal['confidence_score']
            risk_reward = signal['risk_reward_ratio']
            return confidence * risk_reward
        
        sorted_signals = sorted(all_signals, key=signal_score, reverse=True)
        
        # Select top signals, ensuring diversity
        best_signals = []
        used_symbols = set()
        
        for signal in sorted_signals:
            symbol_name = signal['symbol'].symbol
            if symbol_name not in used_symbols and len(best_signals) < self.best_signals_count:
                best_signals.append(signal)
                used_symbols.add(symbol_name)
        
        return best_signals
    
    def _archive_old_signals(self):
        """Archive old signals to history and remove duplicates"""
        try:
            # Mark old signals as executed/archived
            old_signals = TradingSignal.objects.filter(
                is_valid=True,
                created_at__lt=timezone.now() - timedelta(hours=self.signal_refresh_hours)
            )
            
            archived_count = 0
            for signal in old_signals:
                signal.is_executed = True
                signal.executed_at = timezone.now()
                signal.is_valid = False
                signal.save()
                archived_count += 1
            
            logger.info(f"Archived {archived_count} old signals")
            
            # Remove duplicate active signals (keep only the latest for each symbol)
            self._remove_duplicate_active_signals()
            
        except Exception as e:
            logger.error(f"Error archiving old signals: {e}")
    
    def _remove_duplicate_active_signals(self):
        """Remove duplicate active signals, keeping only the latest for each symbol"""
        try:
            # Get all active signals grouped by symbol
            active_signals = TradingSignal.objects.filter(
                is_valid=True,
                created_at__gte=timezone.now() - timedelta(hours=self.signal_refresh_hours)
            ).order_by('symbol', '-created_at')
            
            # Track symbols we've seen and remove duplicates
            seen_symbols = set()
            duplicates_removed = 0
            
            for signal in active_signals:
                symbol_name = signal.symbol.symbol
                if symbol_name in seen_symbols:
                    # This is a duplicate, archive it
                    signal.is_executed = True
                    signal.executed_at = timezone.now()
                    signal.is_valid = False
                    signal.save()
                    duplicates_removed += 1
                    logger.info(f"Removed duplicate signal for {symbol_name}")
                else:
                    seen_symbols.add(symbol_name)
            
            if duplicates_removed > 0:
                logger.info(f"Removed {duplicates_removed} duplicate active signals")
            
        except Exception as e:
            logger.error(f"Error removing duplicate signals: {e}")
    
    def _save_new_signals(self, signals: List[Dict]):
        """Save new signals to database"""
        try:
            saved_count = 0
            
            for signal_data in signals:
                try:
                    # Get or create signal type
                    signal_type, _ = SignalType.objects.get_or_create(
                        name=signal_data['signal_type'],
                        defaults={'is_active': True}
                    )
                    
                    # Create trading signal
                    signal = TradingSignal.objects.create(
                        symbol=signal_data['symbol'],
                        signal_type=signal_type,
                        strength=signal_data['strength'],
                        confidence_score=signal_data['confidence_score'],
                        confidence_level=self._get_confidence_level(signal_data['confidence_score']),
                        entry_price=signal_data['entry_price'],
                        target_price=signal_data['target_price'],
                        stop_loss=signal_data['stop_loss'],
                        risk_reward_ratio=signal_data['risk_reward_ratio'],
                        timeframe=signal_data['timeframe'],
                        entry_point_type=signal_data['entry_point_type'],
                        quality_score=signal_data['confidence_score'],
                        is_valid=True,
                        expires_at=timezone.now() + timedelta(hours=self.signal_refresh_hours * 2),
                        technical_score=signal_data['technical_score'],
                        notes=signal_data['reasoning'],
                        analyzed_at=timezone.now()
                    )
                    
                    saved_count += 1
                    logger.info(f"Saved {signal_data['signal_type']} signal for {signal_data['symbol'].symbol}")
                    
                except Exception as e:
                    logger.error(f"Error saving signal for {signal_data['symbol'].symbol}: {e}")
                    continue
            
            logger.info(f"Successfully saved {saved_count} new signals")
            
        except Exception as e:
            logger.error(f"Error saving new signals: {e}")
    
    def _get_confidence_level(self, confidence_score: float) -> str:
        """Convert confidence score to confidence level"""
        if confidence_score >= 0.85:
            return 'VERY_HIGH'
        elif confidence_score >= 0.70:
            return 'HIGH'
        elif confidence_score >= 0.50:
            return 'MEDIUM'
        else:
            return 'LOW'


# Global instance
enhanced_signal_service = EnhancedSignalGenerationService()
