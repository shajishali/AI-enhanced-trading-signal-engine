import numpy as np
import pandas as pd
from decimal import Decimal
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import math

class PortfolioAnalytics:
    """Advanced portfolio analytics and risk management"""
    
    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio for a series of returns"""
        if len(returns) < 2:
            return Decimal('0.00')
        
        returns_array = np.array([float(r) for r in returns])
        excess_returns = returns_array - (risk_free_rate / 252)  # Daily risk-free rate
        
        if np.std(excess_returns) == 0:
            return Decimal('0.00')
        
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return Decimal(str(sharpe))

    @staticmethod
    def calculate_max_drawdown(values):
        """Calculate maximum drawdown from peak"""
        if len(values) < 2:
            return Decimal('0.00')
        
        values_array = np.array([float(v) for v in values])
        peak = np.maximum.accumulate(values_array)
        drawdown = (values_array - peak) / peak
        max_drawdown = np.min(drawdown)
        
        return Decimal(str(abs(max_drawdown) * 100))

    @staticmethod
    def calculate_var(returns, confidence_level=0.95):
        """Calculate Value at Risk"""
        if len(returns) < 2:
            return Decimal('0.00')
        
        returns_array = np.array([float(r) for r in returns])
        var = np.percentile(returns_array, (1 - confidence_level) * 100)
        
        return Decimal(str(abs(var) * 100))

    @staticmethod
    def calculate_volatility(returns):
        """Calculate annualized volatility"""
        if len(returns) < 2:
            return Decimal('0.00')
        
        returns_array = np.array([float(r) for r in returns])
        volatility = np.std(returns_array) * np.sqrt(252) * 100
        
        return Decimal(str(volatility))

    @staticmethod
    def calculate_beta(portfolio_returns, market_returns):
        """Calculate portfolio beta relative to market"""
        if len(portfolio_returns) < 2 or len(market_returns) < 2:
            return Decimal('1.00')
        
        portfolio_array = np.array([float(r) for r in portfolio_returns])
        market_array = np.array([float(r) for r in market_returns])
        
        # Ensure same length
        min_length = min(len(portfolio_array), len(market_array))
        portfolio_array = portfolio_array[:min_length]
        market_array = market_array[:min_length]
        
        covariance = np.cov(portfolio_array, market_array)[0, 1]
        market_variance = np.var(market_array)
        
        if market_variance == 0:
            return Decimal('1.00')
        
        beta = covariance / market_variance
        return Decimal(str(beta))

class TechnicalIndicators:
    """Technical analysis indicators"""
    
    @staticmethod
    def calculate_sma(prices, period):
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return None
        
        prices_array = np.array([float(p) for p in prices])
        sma = np.convolve(prices_array, np.ones(period)/period, mode='valid')
        return sma[-1] if len(sma) > 0 else None

    @staticmethod
    def calculate_ema(prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
        
        prices_array = np.array([float(p) for p in prices])
        alpha = 2 / (period + 1)
        ema = [prices_array[0]]
        
        for price in prices_array[1:]:
            ema.append(alpha * price + (1 - alpha) * ema[-1])
        
        return ema[-1]

    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return None
        
        prices_array = np.array([float(p) for p in prices])
        deltas = np.diff(prices_array)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow:
            return None, None
        
        prices_array = np.array([float(p) for p in prices])
        
        ema_fast = TechnicalIndicators.calculate_ema(prices_array, fast)
        ema_slow = TechnicalIndicators.calculate_ema(prices_array, slow)
        
        if ema_fast is None or ema_slow is None:
            return None, None
        
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line (EMA of MACD)
        macd_values = []
        for i in range(slow, len(prices_array)):
            ema_fast_i = TechnicalIndicators.calculate_ema(prices_array[:i+1], fast)
            ema_slow_i = TechnicalIndicators.calculate_ema(prices_array[:i+1], slow)
            macd_values.append(ema_fast_i - ema_slow_i)
        
        if len(macd_values) < signal:
            return macd_line, None
        
        signal_line = TechnicalIndicators.calculate_ema(macd_values, signal)
        
        return macd_line, signal_line

    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return None, None, None
        
        prices_array = np.array([float(p) for p in prices])
        sma = TechnicalIndicators.calculate_sma(prices_array, period)
        
        if sma is None:
            return None, None, None
        
        # Calculate standard deviation
        recent_prices = prices_array[-period:]
        std = np.std(recent_prices)
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        return upper_band, sma, lower_band

class BacktestEngine:
    """Backtesting engine for strategy validation"""
    
    @staticmethod
    def run_backtest(strategy, start_date, end_date, initial_capital=10000):
        """Run backtest for a given strategy"""
        # This is a simplified backtest engine
        # In a real implementation, you would load historical data and execute the strategy
        
        # Simulate some results for demonstration
        total_return = Decimal('15.5')
        annualized_return = Decimal('12.3')
        sharpe_ratio = Decimal('1.8')
        max_drawdown = Decimal('8.2')
        win_rate = Decimal('65.5')
        profit_factor = Decimal('2.1')
        total_trades = 45
        winning_trades = 30
        losing_trades = 15
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'final_capital': initial_capital * (1 + total_return / 100)
        }

class RiskManager:
    """Risk management and position sizing"""
    
    @staticmethod
    def calculate_position_size(portfolio_value, risk_per_trade, stop_loss_pct):
        """Calculate position size based on risk management rules"""
        if stop_loss_pct <= 0:
            return Decimal('0.00')
        
        risk_amount = portfolio_value * (risk_per_trade / 100)
        position_size = risk_amount / (stop_loss_pct / 100)
        
        return position_size

    @staticmethod
    def calculate_portfolio_risk(positions, portfolio_value):
        """Calculate overall portfolio risk"""
        total_risk = Decimal('0.00')
        
        for position in positions:
            # Simplified risk calculation - convert to float for calculation
            position_risk = (float(position.market_value) / float(portfolio_value)) * 0.1  # 10% volatility assumption
            total_risk += Decimal(str(position_risk))
        
        return total_risk

class MarketAnalyzer:
    """Market analysis and sentiment"""
    
    @staticmethod
    def calculate_market_sentiment(symbol, days=30):
        """Calculate market sentiment for a symbol"""
        # This would integrate with sentiment analysis from Phase 2
        # For now, return a simulated sentiment score
        
        import random
        sentiment_score = random.uniform(-1, 1)  # Range from -1 (very bearish) to 1 (very bullish)
        
        if sentiment_score > 0.5:
            sentiment = "Very Bullish"
        elif sentiment_score > 0.1:
            sentiment = "Bullish"
        elif sentiment_score > -0.1:
            sentiment = "Neutral"
        elif sentiment_score > -0.5:
            sentiment = "Bearish"
        else:
            sentiment = "Very Bearish"
        
        return {
            'score': Decimal(str(sentiment_score)),
            'sentiment': sentiment,
            'confidence': Decimal(str(random.uniform(0.6, 0.95)))
        }

    @staticmethod
    def get_market_overview():
        """Get overall market overview"""
        # Simulate market overview data
        return {
            'sp500_change': Decimal('0.85'),
            'nasdaq_change': Decimal('1.23'),
            'dow_change': Decimal('0.67'),
            'vix': Decimal('18.5'),
            'market_sentiment': 'Bullish',
            'trending_sectors': ['Technology', 'Healthcare', 'Energy'],
            'market_volatility': 'Low'
        }
