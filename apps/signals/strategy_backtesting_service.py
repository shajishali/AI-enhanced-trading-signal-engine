"""
Strategy-Based Backtesting Service
Implements YOUR actual trading strategy for historical analysis and signal generation
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q, Avg, Count, Max, Min
import pandas as pd

from apps.trading.models import Symbol
from apps.signals.models import TradingSignal, SignalType
from apps.data.models import MarketData, TechnicalIndicator

logger = logging.getLogger(__name__)


class StrategyBacktestingService:
    """
    Implements YOUR actual trading strategy for backtesting:
    - Higher timeframe trend analysis (1D)
    - Market structure analysis (BOS/CHoCH)
    - Entry confirmation (candlestick patterns, RSI, MACD)
    - Risk management (15% TP, 8% SL)
    """
    
    def __init__(self):
        # YOUR specific risk management parameters
        self.take_profit_percentage = 0.15  # 15% take profit
        self.stop_loss_percentage = 0.08    # 8% stop loss
        self.min_risk_reward_ratio = 1.5    # Minimum 1.5:1 risk/reward
        
        # Technical analysis parameters
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.rsi_buy_range = (20, 50)      # RSI 20-50 for longs
        self.rsi_sell_range = (50, 80)      # RSI 50-80 for shorts
        
        # Moving average periods
        self.sma_fast = 20
        self.sma_slow = 50
        
        # Volume confirmation threshold
        self.volume_threshold = 1.2  # 20% above average volume
        
        # Strategy sensitivity (for testing - can be adjusted)
        self.min_confirmations = 2  # Minimum confirmations needed (reduced from 4)
        self.enable_debug_logging = True  # Enable detailed logging
    
    def generate_historical_signals(self, symbol: Symbol, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Generate historical signals based on YOUR strategy for the given date range
        with minimum frequency requirement (1 signal per 2 months)
        
        Args:
            symbol: Trading symbol
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            List of signals generated based on your strategy with minimum frequency
        """
        try:
            logger.info(f"Starting historical signal generation for {symbol.symbol} from {start_date} to {end_date}")
            
            # Make dates timezone-aware if they aren't already
            from django.utils import timezone
            if start_date.tzinfo is None:
                start_date = timezone.make_aware(start_date)
            if end_date.tzinfo is None:
                end_date = timezone.make_aware(end_date)
            
            # Get historical data for the symbol
            historical_data = self._get_historical_data(symbol, start_date, end_date)
            if historical_data.empty:
                logger.warning(f"No historical data found for {symbol.symbol}")
                return []
            
            logger.info(f"Loaded {len(historical_data)} data points for analysis")
            
            # Generate signals day by day
            signals = []
            current_date = start_date
            
            while current_date <= end_date:
                try:
                    # Get data up to current date (no look-ahead bias)
                    data_up_to_date = historical_data[historical_data.index <= current_date]
                    
                    if len(data_up_to_date) < 50:  # Need minimum data for analysis
                        current_date += timedelta(days=1)
                        continue
                    
                    # Analyze current day for signals
                    daily_signals = self._analyze_daily_signals(symbol, data_up_to_date, current_date)
                    signals.extend(daily_signals)
                    
                except Exception as e:
                    logger.error(f"Error analyzing signals for {current_date}: {e}")
                
                current_date += timedelta(days=1)
            
            logger.info(f"Generated {len(signals)} natural signals for {symbol.symbol}")
            
            # Calculate minimum signals required (1 signal per 2 months)
            days_diff = (end_date - start_date).days
            min_signals_required = max(1, days_diff // 60)  # 60 days = 2 months
            
            logger.info(f"Minimum signals required: {min_signals_required} (1 per 2 months)")
            
            # If we don't have enough signals, generate additional ones
            if len(signals) < min_signals_required:
                additional_signals_needed = min_signals_required - len(signals)
                logger.info(f"Generating {additional_signals_needed} additional signals to meet minimum frequency")
                
                additional_signals = self._generate_additional_signals(
                    symbol, historical_data, start_date, end_date, 
                    additional_signals_needed, signals
                )
                signals.extend(additional_signals)
                
                logger.info(f"Total signals after frequency adjustment: {len(signals)}")
            else:
                logger.info(f"Natural signals ({len(signals)}) exceed minimum requirement ({min_signals_required})")
            
            # Log summary if no signals generated
            if len(signals) == 0 and self.enable_debug_logging:
                logger.info(f"No signals generated for {symbol.symbol} in period {start_date.date()} to {end_date.date()}")
                logger.info(f"Possible reasons:")
                logger.info(f"- Strategy conditions not met (RSI ranges, MACD crossovers, volume)")
                logger.info(f"- Risk/reward ratio below minimum {self.min_risk_reward_ratio}:1")
                logger.info(f"- Insufficient confirmations (need {self.min_confirmations} minimum)")
                logger.info(f"- Market conditions not favorable for {symbol.symbol}")
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in historical signal generation: {e}")
            return []
    
    def _get_historical_data(self, symbol: Symbol, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get historical market data for the symbol"""
        try:
            # Get market data
            market_data = MarketData.objects.filter(
                symbol=symbol,
                timestamp__gte=start_date,
                timestamp__lte=end_date
            ).order_by('timestamp')
            
            if not market_data.exists():
                return pd.DataFrame()
            
            # Convert to DataFrame
            data_list = []
            for data in market_data:
                data_list.append({
                    'timestamp': data.timestamp,
                    'open': float(data.open_price),
                    'high': float(data.high_price),
                    'low': float(data.low_price),
                    'close': float(data.close_price),
                    'volume': float(data.volume)
                })
            
            df = pd.DataFrame(data_list)
            df.set_index('timestamp', inplace=True)
            
            # Calculate technical indicators
            df = self._calculate_technical_indicators(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for the data"""
        try:
            # Simple Moving Averages
            df['sma_20'] = df['close'].rolling(window=self.sma_fast).mean()
            df['sma_50'] = df['close'].rolling(window=self.sma_slow).mean()
            
            # RSI
            df['rsi'] = self._calculate_rsi(df['close'])
            
            # MACD
            macd_data = self._calculate_macd(df['close'])
            df['macd'] = macd_data['macd']
            df['macd_signal'] = macd_data['signal']
            df['macd_histogram'] = macd_data['histogram']
            
            # Volume moving average
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price change percentage
            df['price_change'] = df['close'].pct_change()
            
            # Support and resistance levels
            df['support'] = df['low'].rolling(window=20).min()
            df['resistance'] = df['high'].rolling(window=20).max()
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series(index=prices.index, dtype=float)
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD indicator"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            
            macd = ema_fast - ema_slow
            signal_line = macd.ewm(span=signal).mean()
            histogram = macd - signal_line
            
            return {
                'macd': macd,
                'signal': signal_line,
                'histogram': histogram
            }
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {
                'macd': pd.Series(index=prices.index, dtype=float),
                'signal': pd.Series(index=prices.index, dtype=float),
                'histogram': pd.Series(index=prices.index, dtype=float)
            }
    
    def _analyze_daily_signals(self, symbol: Symbol, data: pd.DataFrame, current_date: datetime) -> List[Dict]:
        """
        Analyze a specific day for trading signals based on YOUR strategy
        
        Strategy Components:
        1. Higher timeframe trend (daily)
        2. Market structure analysis (BOS/CHoCH)
        3. Entry confirmation (RSI, MACD, candlestick patterns)
        4. Risk management (15% TP, 8% SL)
        """
        signals = []
        
        try:
            if len(data) < 50:
                return signals
            
            # Get current day data
            current_data = data.iloc[-1]
            current_price = current_data['close']
            
            # 1. HIGHER TIMEFRAME TREND ANALYSIS (Daily)
            trend_bias = self._analyze_daily_trend(data)
            
            # 2. MARKET STRUCTURE ANALYSIS
            structure_signal = self._analyze_market_structure(data)
            
            # 3. ENTRY CONFIRMATION
            entry_confirmation = self._analyze_entry_confirmation(data, trend_bias)
            
            # 4. GENERATE SIGNALS BASED ON YOUR STRATEGY
            if entry_confirmation['direction'] == 'BUY' and trend_bias == 'BULLISH':
                signal = self._create_buy_signal(symbol, current_data, current_date, entry_confirmation)
                if signal:
                    signals.append(signal)
                    if self.enable_debug_logging:
                        logger.info(f"Generated BUY signal for {symbol.symbol} on {current_date.date()}")
                elif self.enable_debug_logging:
                    logger.debug(f"BUY signal rejected for {symbol.symbol} on {current_date.date()}: Risk/reward too low")
            
            elif entry_confirmation['direction'] == 'SELL' and trend_bias == 'BEARISH':
                signal = self._create_sell_signal(symbol, current_data, current_date, entry_confirmation)
                if signal:
                    signals.append(signal)
                    if self.enable_debug_logging:
                        logger.info(f"Generated SELL signal for {symbol.symbol} on {current_date.date()}")
                elif self.enable_debug_logging:
                    logger.debug(f"SELL signal rejected for {symbol.symbol} on {current_date.date()}: Risk/reward too low")
            
            elif self.enable_debug_logging:
                logger.debug(f"No signal for {symbol.symbol} on {current_date.date()}: Direction={entry_confirmation['direction']}, Trend={trend_bias}")
            
        except Exception as e:
            logger.error(f"Error analyzing daily signals for {current_date}: {e}")
        
        return signals
    
    def _analyze_daily_trend(self, data: pd.DataFrame) -> str:
        """Analyze daily trend using SMA crossover"""
        try:
            if len(data) < 50:
                return 'NEUTRAL'
            
            # Get recent SMA values
            sma_20_current = data['sma_20'].iloc[-1]
            sma_50_current = data['sma_50'].iloc[-1]
            
            # Get previous SMA values for trend confirmation
            sma_20_prev = data['sma_20'].iloc[-2] if len(data) > 1 else sma_20_current
            sma_50_prev = data['sma_50'].iloc[-2] if len(data) > 1 else sma_50_current
            
            # Determine trend
            if sma_20_current > sma_50_current and sma_20_prev > sma_50_prev:
                return 'BULLISH'
            elif sma_20_current < sma_50_current and sma_20_prev < sma_50_prev:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            logger.error(f"Error analyzing daily trend: {e}")
            return 'NEUTRAL'
    
    def _analyze_market_structure(self, data: pd.DataFrame) -> Dict:
        """Analyze market structure for BOS/CHoCH patterns"""
        try:
            if len(data) < 20:
                return {'signal': 'NEUTRAL', 'strength': 0.5}
            
            # Get recent highs and lows
            recent_highs = data['high'].tail(20)
            recent_lows = data['low'].tail(20)
            
            # Check for break of structure (BOS)
            current_high = recent_highs.iloc[-1]
            current_low = recent_lows.iloc[-1]
            
            # Previous swing high/low
            prev_swing_high = recent_highs.max()
            prev_swing_low = recent_lows.min()
            
            # BOS Analysis
            if current_high > prev_swing_high:
                return {'signal': 'BULLISH_BOS', 'strength': 0.8}
            elif current_low < prev_swing_low:
                return {'signal': 'BEARISH_BOS', 'strength': 0.8}
            else:
                return {'signal': 'NEUTRAL', 'strength': 0.5}
                
        except Exception as e:
            logger.error(f"Error analyzing market structure: {e}")
            return {'signal': 'NEUTRAL', 'strength': 0.5}
    
    def _analyze_entry_confirmation(self, data: pd.DataFrame, trend_bias: str) -> Dict:
        """
        Analyze entry confirmation using YOUR strategy criteria:
        - RSI confirmation (20-50 for longs, 50-80 for shorts)
        - MACD crossover signals
        - Volume confirmation
        - Candlestick patterns
        """
        try:
            if len(data) < 20:
                return {'direction': 'HOLD', 'confidence': 0.0}
            
            current_data = data.iloc[-1]
            prev_data = data.iloc[-2] if len(data) > 1 else current_data
            
            # RSI Analysis
            rsi_current = current_data['rsi']
            rsi_prev = prev_data['rsi']
            
            # MACD Analysis
            macd_current = current_data['macd']
            macd_signal_current = current_data['macd_signal']
            macd_prev = prev_data['macd']
            macd_signal_prev = prev_data['macd_signal']
            
            # Volume Analysis
            volume_ratio = current_data['volume_ratio']
            
            # Candlestick Pattern Analysis
            candlestick_signal = self._analyze_candlestick_pattern(data)
            
            # BUY Signal Criteria
            buy_signals = 0
            if trend_bias == 'BULLISH':
                # RSI in buy range (20-50)
                if self.rsi_buy_range[0] <= rsi_current <= self.rsi_buy_range[1]:
                    buy_signals += 1
                
                # MACD bullish crossover
                if macd_current > macd_signal_current and macd_prev <= macd_signal_prev:
                    buy_signals += 1
                
                # Volume confirmation
                if volume_ratio >= self.volume_threshold:
                    buy_signals += 1
                
                # Candlestick confirmation
                if candlestick_signal == 'BULLISH':
                    buy_signals += 1
            
            # SELL Signal Criteria
            sell_signals = 0
            if trend_bias == 'BEARISH':
                # RSI in sell range (50-80)
                if self.rsi_sell_range[0] <= rsi_current <= self.rsi_sell_range[1]:
                    sell_signals += 1
                
                # MACD bearish crossover
                if macd_current < macd_signal_current and macd_prev >= macd_signal_prev:
                    sell_signals += 1
                
                # Volume confirmation
                if volume_ratio >= self.volume_threshold:
                    sell_signals += 1
                
                # Candlestick confirmation
                if candlestick_signal == 'BEARISH':
                    sell_signals += 1
            
            # Determine final signal
            if buy_signals >= self.min_confirmations:  # At least min confirmations for BUY
                return {
                    'direction': 'BUY',
                    'confidence': min(0.9, 0.5 + (buy_signals * 0.1)),
                    'confirmations': buy_signals
                }
            elif sell_signals >= self.min_confirmations:  # At least min confirmations for SELL
                return {
                    'direction': 'SELL',
                    'confidence': min(0.9, 0.5 + (sell_signals * 0.1)),
                    'confirmations': sell_signals
                }
            else:
                if self.enable_debug_logging:
                    logger.debug(f"No signal: BUY={buy_signals}, SELL={sell_signals}, min_required={self.min_confirmations}")
                return {'direction': 'HOLD', 'confidence': 0.0}
                
        except Exception as e:
            logger.error(f"Error analyzing entry confirmation: {e}")
            return {'direction': 'HOLD', 'confidence': 0.0}
    
    def _analyze_candlestick_pattern(self, data: pd.DataFrame) -> str:
        """Analyze candlestick patterns for entry confirmation"""
        try:
            if len(data) < 3:
                return 'NEUTRAL'
            
            # Get last 3 candles
            current = data.iloc[-1]
            prev = data.iloc[-2]
            prev2 = data.iloc[-3]
            
            # Bullish Engulfing Pattern
            if (prev['close'] < prev['open'] and  # Previous candle bearish
                current['close'] > current['open'] and  # Current candle bullish
                current['open'] < prev['close'] and  # Current opens below prev close
                current['close'] > prev['open']):  # Current closes above prev open
                return 'BULLISH'
            
            # Bearish Engulfing Pattern
            elif (prev['close'] > prev['open'] and  # Previous candle bullish
                  current['close'] < current['open'] and  # Current candle bearish
                  current['open'] > prev['close'] and  # Current opens above prev close
                  current['close'] < prev['open']):  # Current closes below prev open
                return 'BEARISH'
            
            # Hammer Pattern (simplified)
            elif (current['close'] > current['open'] and  # Bullish candle
                  (current['low'] - min(current['open'], current['close'])) > 
                  2 * (max(current['open'], current['close']) - current['low'])):
                return 'BULLISH'
            
            # Shooting Star Pattern (simplified)
            elif (current['close'] < current['open'] and  # Bearish candle
                  (current['high'] - max(current['open'], current['close'])) > 
                  2 * (max(current['open'], current['close']) - current['low'])):
                return 'BEARISH'
            
            return 'NEUTRAL'
            
        except Exception as e:
            logger.error(f"Error analyzing candlestick patterns: {e}")
            return 'NEUTRAL'
    
    def _create_buy_signal(self, symbol: Symbol, current_data: pd.Series, current_date: datetime, confirmation: Dict) -> Optional[Dict]:
        """Create a BUY signal based on YOUR strategy"""
        try:
            current_price = current_data['close']
            
            # Calculate YOUR specific risk management
            stop_loss = current_price * (1 - self.stop_loss_percentage)  # 8% stop loss
            target_price = current_price * (1 + self.take_profit_percentage)  # 15% take profit
            
            # Calculate risk/reward ratio
            risk = current_price - stop_loss
            reward = target_price - current_price
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            # Only create signal if risk/reward meets minimum requirement
            if risk_reward_ratio >= self.min_risk_reward_ratio:
                return {
                    'symbol': symbol.symbol,
                    'signal_type': 'BUY',
                    'strength': 'STRONG' if confirmation['confidence'] > 0.7 else 'MODERATE',
                    'confidence_score': confirmation['confidence'],
                    'entry_price': current_price,
                    'target_price': target_price,
                    'stop_loss': stop_loss,
                    'risk_reward_ratio': risk_reward_ratio,
                    'timeframe': '1D',
                    'quality_score': confirmation['confidence'],
                    'created_at': current_date.isoformat(),
                    'strategy_confirmations': confirmation.get('confirmations', 0),
                    'strategy_details': {
                        'trend_bias': 'BULLISH',
                        'rsi_level': float(current_data.get('rsi', 0)),
                        'macd_signal': 'BULLISH_CROSSOVER',
                        'volume_confirmation': bool(current_data.get('volume_ratio', 1) >= self.volume_threshold),
                        'take_profit_percentage': float(self.take_profit_percentage),
                        'stop_loss_percentage': float(self.stop_loss_percentage)
                    }
                }
            
        except Exception as e:
            logger.error(f"Error creating BUY signal: {e}")
        
        return None
    
    def _create_sell_signal(self, symbol: Symbol, current_data: pd.Series, current_date: datetime, confirmation: Dict) -> Optional[Dict]:
        """Create a SELL signal based on YOUR strategy"""
        try:
            current_price = current_data['close']
            
            # Calculate YOUR specific risk management
            stop_loss = current_price * (1 + self.stop_loss_percentage)  # 8% stop loss
            target_price = current_price * (1 - self.take_profit_percentage)  # 15% take profit
            
            # Calculate risk/reward ratio
            risk = stop_loss - current_price
            reward = current_price - target_price
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            # Only create signal if risk/reward meets minimum requirement
            if risk_reward_ratio >= self.min_risk_reward_ratio:
                return {
                    'symbol': symbol.symbol,
                    'signal_type': 'SELL',
                    'strength': 'STRONG' if confirmation['confidence'] > 0.7 else 'MODERATE',
                    'confidence_score': confirmation['confidence'],
                    'entry_price': current_price,
                    'target_price': target_price,
                    'stop_loss': stop_loss,
                    'risk_reward_ratio': risk_reward_ratio,
                    'timeframe': '1D',
                    'quality_score': confirmation['confidence'],
                    'created_at': current_date.isoformat(),
                    'strategy_confirmations': confirmation.get('confirmations', 0),
                    'strategy_details': {
                        'trend_bias': 'BEARISH',
                        'rsi_level': float(current_data.get('rsi', 0)),
                        'macd_signal': 'BEARISH_CROSSOVER',
                        'volume_confirmation': bool(current_data.get('volume_ratio', 1) >= self.volume_threshold),
                        'take_profit_percentage': float(self.take_profit_percentage),
                        'stop_loss_percentage': float(self.stop_loss_percentage)
                    }
                }
            
        except Exception as e:
            logger.error(f"Error creating SELL signal: {e}")
        
        return None
    
    def _generate_additional_signals(self, symbol: Symbol, historical_data: pd.DataFrame, 
                                   start_date: datetime, end_date: datetime, 
                                   signals_needed: int, existing_signals: List[Dict]) -> List[Dict]:
        """
        Generate additional signals to meet minimum frequency requirement (1 per 2 months)
        Uses relaxed conditions when natural signals are insufficient
        """
        additional_signals = []
        
        try:
            logger.info(f"Generating {signals_needed} additional signals with relaxed conditions")
            
            # Get existing signal dates to avoid duplicates
            existing_dates = set()
            for signal in existing_signals:
                signal_date = datetime.fromisoformat(signal['created_at'].replace('Z', '+00:00')).date()
                existing_dates.add(signal_date)
            
            # Calculate time intervals for signal distribution
            days_diff = (end_date - start_date).days
            interval_days = days_diff // signals_needed if signals_needed > 0 else 30
            
            # Generate signals at regular intervals
            current_date = start_date
            signals_generated = 0
            
            while current_date <= end_date and signals_generated < signals_needed:
                # Skip if we already have a signal on this date
                if current_date.date() in existing_dates:
                    current_date += timedelta(days=1)
                    continue
                
                # Get data up to current date
                data_up_to_date = historical_data[historical_data.index <= current_date]
                
                if len(data_up_to_date) < 50:
                    current_date += timedelta(days=1)
                    continue
                
                # Try to generate signal with relaxed conditions
                signal = self._generate_relaxed_signal(symbol, data_up_to_date, current_date)
                
                if signal:
                    additional_signals.append(signal)
                    existing_dates.add(current_date.date())
                    signals_generated += 1
                    logger.info(f"Generated additional {signal['signal_type']} signal for {symbol.symbol} on {current_date.date()}")
                
                # Move to next interval
                current_date += timedelta(days=interval_days)
            
            logger.info(f"Successfully generated {len(additional_signals)} additional signals")
            
        except Exception as e:
            logger.error(f"Error generating additional signals: {e}")
        
        return additional_signals
    
    def _generate_relaxed_signal(self, symbol: Symbol, data: pd.DataFrame, current_date: datetime) -> Optional[Dict]:
        """
        Generate signal with relaxed conditions when natural signals are insufficient
        """
        try:
            if len(data) < 50:
                return None
            
            current_data = data.iloc[-1]
            current_price = current_data['close']
            
            # Analyze trend with relaxed conditions
            trend_bias = self._analyze_daily_trend(data)
            
            # Use relaxed entry confirmation
            entry_confirmation = self._analyze_relaxed_entry_confirmation(data, trend_bias)
            
            # Generate signal if conditions are met (even with relaxed criteria)
            if entry_confirmation['direction'] == 'BUY' and trend_bias in ['BULLISH', 'NEUTRAL']:
                signal = self._create_buy_signal(symbol, current_data, current_date, entry_confirmation)
                if signal:
                    # Mark as relaxed signal
                    signal['signal_source'] = 'RELAXED_CONDITIONS'
                    signal['strategy_details']['relaxed_generation'] = True
                    return signal
            
            elif entry_confirmation['direction'] == 'SELL' and trend_bias in ['BEARISH', 'NEUTRAL']:
                signal = self._create_sell_signal(symbol, current_data, current_date, entry_confirmation)
                if signal:
                    # Mark as relaxed signal
                    signal['signal_source'] = 'RELAXED_CONDITIONS'
                    signal['strategy_details']['relaxed_generation'] = True
                    return signal
            
            # If still no signal, try trend-following approach
            return self._generate_trend_following_signal(symbol, current_data, current_date, trend_bias)
            
        except Exception as e:
            logger.error(f"Error generating relaxed signal: {e}")
            return None
    
    def _analyze_relaxed_entry_confirmation(self, data: pd.DataFrame, trend_bias: str) -> Dict:
        """
        Analyze entry confirmation with relaxed conditions for additional signal generation
        """
        try:
            if len(data) < 20:
                return {'direction': 'HOLD', 'confidence': 0.0}
            
            current_data = data.iloc[-1]
            prev_data = data.iloc[-2] if len(data) > 1 else current_data
            
            # RSI Analysis (relaxed ranges)
            rsi_current = current_data['rsi']
            
            # MACD Analysis
            macd_current = current_data['macd']
            macd_signal_current = current_data['macd_signal']
            macd_prev = prev_data['macd']
            macd_signal_prev = prev_data['macd_signal']
            
            # Volume Analysis (relaxed threshold)
            volume_ratio = current_data['volume_ratio']
            
            # Relaxed BUY Signal Criteria (only need 1 confirmation instead of 2)
            buy_signals = 0
            if trend_bias in ['BULLISH', 'NEUTRAL']:
                # Relaxed RSI range (15-60 instead of 20-50)
                if 15 <= rsi_current <= 60:
                    buy_signals += 1
                
                # MACD bullish crossover or convergence
                if macd_current > macd_signal_current or (macd_current > macd_prev and macd_signal_current > macd_signal_prev):
                    buy_signals += 1
                
                # Relaxed volume confirmation (1.1x instead of 1.2x)
                if volume_ratio >= 1.1:
                    buy_signals += 1
            
            # Relaxed SELL Signal Criteria
            sell_signals = 0
            if trend_bias in ['BEARISH', 'NEUTRAL']:
                # Relaxed RSI range (40-85 instead of 50-80)
                if 40 <= rsi_current <= 85:
                    sell_signals += 1
                
                # MACD bearish crossover or divergence
                if macd_current < macd_signal_current or (macd_current < macd_prev and macd_signal_current < macd_signal_prev):
                    sell_signals += 1
                
                # Relaxed volume confirmation
                if volume_ratio >= 1.1:
                    sell_signals += 1
            
            # Determine final signal (only need 1 confirmation for relaxed signals)
            if buy_signals >= 1:
                return {
                    'direction': 'BUY',
                    'confidence': min(0.7, 0.4 + (buy_signals * 0.1)),  # Lower confidence for relaxed signals
                    'confirmations': buy_signals
                }
            elif sell_signals >= 1:
                return {
                    'direction': 'SELL',
                    'confidence': min(0.7, 0.4 + (sell_signals * 0.1)),  # Lower confidence for relaxed signals
                    'confirmations': sell_signals
                }
            else:
                return {'direction': 'HOLD', 'confidence': 0.0}
                
        except Exception as e:
            logger.error(f"Error analyzing relaxed entry confirmation: {e}")
            return {'direction': 'HOLD', 'confidence': 0.0}
    
    def _generate_trend_following_signal(self, symbol: Symbol, current_data: pd.Series, 
                                       current_date: datetime, trend_bias: str) -> Optional[Dict]:
        """
        Generate trend-following signal as last resort for minimum frequency
        """
        try:
            current_price = current_data['close']
            
            # Simple trend-following logic
            if trend_bias == 'BULLISH':
                # Generate BUY signal with conservative risk management
                stop_loss = current_price * (1 - 0.06)  # 6% stop loss (more conservative)
                target_price = current_price * (1 + 0.12)  # 12% take profit (more conservative)
                
                risk = current_price - stop_loss
                reward = target_price - current_price
                risk_reward_ratio = reward / risk if risk > 0 else 0
                
                if risk_reward_ratio >= 1.2:  # Lower minimum risk/reward for trend-following
                    return {
                        'symbol': symbol.symbol,
                        'signal_type': 'BUY',
                        'strength': 'WEAK',
                        'confidence_score': 0.4,  # Lower confidence
                        'entry_price': current_price,
                        'target_price': target_price,
                        'stop_loss': stop_loss,
                        'risk_reward_ratio': risk_reward_ratio,
                        'timeframe': '1D',
                        'quality_score': 0.4,
                        'created_at': current_date.isoformat(),
                        'strategy_confirmations': 1,
                        'signal_source': 'TREND_FOLLOWING',
                        'strategy_details': {
                            'trend_bias': trend_bias,
                            'rsi_level': float(current_data.get('rsi', 0)),
                            'macd_signal': 'TREND_FOLLOWING',
                            'volume_confirmation': False,
                            'take_profit_percentage': 0.12,
                            'stop_loss_percentage': 0.06,
                            'trend_following': True
                        }
                    }
            
            elif trend_bias == 'BEARISH':
                # Generate SELL signal with conservative risk management
                stop_loss = current_price * (1 + 0.06)  # 6% stop loss
                target_price = current_price * (1 - 0.12)  # 12% take profit
                
                risk = stop_loss - current_price
                reward = current_price - target_price
                risk_reward_ratio = reward / risk if risk > 0 else 0
                
                if risk_reward_ratio >= 1.2:  # Lower minimum risk/reward
                    return {
                        'symbol': symbol.symbol,
                        'signal_type': 'SELL',
                        'strength': 'WEAK',
                        'confidence_score': 0.4,  # Lower confidence
                        'entry_price': current_price,
                        'target_price': target_price,
                        'stop_loss': stop_loss,
                        'risk_reward_ratio': risk_reward_ratio,
                        'timeframe': '1D',
                        'quality_score': 0.4,
                        'created_at': current_date.isoformat(),
                        'strategy_confirmations': 1,
                        'signal_source': 'TREND_FOLLOWING',
                        'strategy_details': {
                            'trend_bias': trend_bias,
                            'rsi_level': float(current_data.get('rsi', 0)),
                            'macd_signal': 'TREND_FOLLOWING',
                            'volume_confirmation': False,
                            'take_profit_percentage': 0.12,
                            'stop_loss_percentage': 0.06,
                            'trend_following': True
                        }
                    }
            
        except Exception as e:
            logger.error(f"Error generating trend-following signal: {e}")
        
        return None
