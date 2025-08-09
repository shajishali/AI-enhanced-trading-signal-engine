#!/usr/bin/env python
"""
Phase 5B Setup Script - Advanced Analytics & Machine Learning Integration
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.utils import timezone
from apps.analytics.models import MarketData, AnalyticsPortfolio, AnalyticsPosition, AnalyticsTrade, PerformanceMetrics
from apps.signals.models import TradingSignal
from apps.analytics.models import SentimentData
from apps.analytics.ml_services import MLPredictor, MarketRegimeDetector, FeatureEngineer

def create_ml_models_directory():
    """Create directory for storing ML models"""
    models_dir = 'ml_models'
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"✅ Created ML models directory: {models_dir}")
    else:
        print(f"✅ ML models directory already exists: {models_dir}")

def generate_sample_market_data():
    """Generate sample market data for ML training"""
    symbols = ['BTC', 'ETH', 'AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'NVDA']
    
    for symbol in symbols:
        # Check if data already exists
        if MarketData.objects.filter(symbol=symbol).count() > 0:
            print(f"✅ Market data already exists for {symbol}")
            continue
        
        # Generate 2 years of daily data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=730)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate realistic price data
        base_price = random.uniform(50, 500) if symbol not in ['BTC', 'ETH'] else random.uniform(20000, 50000)
        prices = []
        
        for i, date in enumerate(dates):
            if i == 0:
                price = base_price
            else:
                # Add some random walk with trend
                change = random.gauss(0, 0.02)  # 2% daily volatility
                price = prices[-1] * (1 + change)
            
            prices.append(max(price, 1))  # Ensure price doesn't go negative
        
        # Create market data records
        market_data_records = []
        for i, date in enumerate(dates):
            price = prices[i]
            high = price * random.uniform(1.01, 1.05)
            low = price * random.uniform(0.95, 0.99)
            volume = random.randint(1000000, 10000000)
            
            market_data_records.append(MarketData(
                symbol=symbol,
                date=date,
                open_price=price,
                high_price=high,
                low_price=low,
                close_price=price,
                volume=volume
            ))
        
        # Bulk create
        MarketData.objects.bulk_create(market_data_records)
        print(f"✅ Generated {len(market_data_records)} market data records for {symbol}")

def generate_sample_sentiment_data():
    """Generate sample sentiment data for ML analysis"""
    symbols = ['BTC', 'ETH', 'AAPL', 'GOOGL']
    
    for symbol in symbols:
        # Check if data already exists
        if SentimentData.objects.filter(symbol=symbol).count() > 0:
            print(f"✅ Sentiment data already exists for {symbol}")
            continue
        
        # Generate 6 months of sentiment data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=180)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        sentiment_records = []
        for date in dates:
            # Generate realistic sentiment scores
            compound_score = random.gauss(0, 0.3)  # Centered around 0
            positive_score = max(0, random.gauss(0.3, 0.2))
            negative_score = max(0, random.gauss(0.2, 0.15))
            neutral_score = max(0, 1 - positive_score - negative_score)
            
            sentiment_records.append(SentimentData(
                symbol=symbol,
                timestamp=date,
                compound_score=compound_score,
                positive_score=positive_score,
                negative_score=negative_score,
                neutral_score=neutral_score,
                source='sample_data'
            ))
        
        # Bulk create
        SentimentData.objects.bulk_create(sentiment_records)
        print(f"✅ Generated {len(sentiment_records)} sentiment records for {symbol}")

def create_sample_portfolio():
    """Create sample portfolio for analytics"""
    from django.contrib.auth.models import User
    
    # Get or create admin user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
    )
    if created:
        user.set_password('admin123')
        user.save()
        print("✅ Created admin user")
    
    # Create portfolio
    portfolio, created = AnalyticsPortfolio.objects.get_or_create(
        user=user,
        defaults={
            'name': 'Sample Portfolio',
            'description': 'Sample portfolio for testing analytics',
            'initial_balance': 100000,
            'current_balance': 105000
        }
    )
    
    if created:
        print("✅ Created sample portfolio")
    
    return portfolio

def generate_sample_positions(portfolio):
    """Generate sample positions for portfolio"""
    symbols = ['BTC', 'ETH', 'AAPL', 'GOOGL', 'TSLA']
    
    for symbol in symbols:
        # Check if position already exists
        if AnalyticsPosition.objects.filter(portfolio=portfolio, symbol=symbol).exists():
            continue
        
        # Create position
        quantity = random.uniform(1, 10)
        entry_price = random.uniform(50, 500) if symbol not in ['BTC', 'ETH'] else random.uniform(20000, 50000)
        current_price = entry_price * random.uniform(0.8, 1.3)  # -20% to +30%
        
        position = AnalyticsPosition.objects.create(
            portfolio=portfolio,
            symbol=symbol,
            quantity=quantity,
            entry_price=entry_price,
            current_price=current_price,
            is_open=True
        )
        
        print(f"✅ Created position: {symbol} - {quantity:.2f} @ ${entry_price:.2f}")

def generate_sample_trades(portfolio):
    """Generate sample trades for portfolio"""
    symbols = ['BTC', 'ETH', 'AAPL', 'GOOGL', 'TSLA']
    
    for symbol in symbols:
        # Generate 10-20 trades per symbol
        num_trades = random.randint(10, 20)
        
        for i in range(num_trades):
            trade_date = timezone.now() - timedelta(days=random.randint(1, 365))
            trade_type = random.choice(['BUY', 'SELL'])
            quantity = random.uniform(0.1, 5)
            price = random.uniform(50, 500) if symbol not in ['BTC', 'ETH'] else random.uniform(20000, 50000)
            
            trade = AnalyticsTrade.objects.create(
                portfolio=portfolio,
                symbol=symbol,
                trade_type=trade_type,
                quantity=quantity,
                price=price,
                commission=random.uniform(1, 10),
                timestamp=trade_date
            )
        
        print(f"✅ Generated {num_trades} trades for {symbol}")

def generate_sample_performance_metrics(portfolio):
    """Generate sample performance metrics"""
    # Generate daily performance metrics for the last 30 days
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        
        # Skip if already exists
        if PerformanceMetrics.objects.filter(portfolio=portfolio, date=date).exists():
            continue
        
        # Generate realistic metrics
        total_value = random.uniform(95000, 110000)
        daily_return = random.gauss(0, 0.02)  # 2% daily volatility
        cumulative_return = random.uniform(0.05, 0.15)  # 5-15% cumulative return
        volatility = random.uniform(0.15, 0.35)
        sharpe_ratio = random.uniform(0.5, 2.0)
        max_drawdown = random.uniform(0.05, 0.25)
        var_95 = random.uniform(0.02, 0.08)
        win_rate = random.uniform(0.4, 0.7)
        profit_factor = random.uniform(1.0, 3.0)
        
        PerformanceMetrics.objects.create(
            portfolio=portfolio,
            date=date,
            total_value=total_value,
            daily_return=daily_return,
            cumulative_return=cumulative_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            var_95=var_95,
            win_rate=win_rate,
            profit_factor=profit_factor
        )
    
    print("✅ Generated performance metrics")

def test_ml_services():
    """Test ML services with sample data"""
    print("\n🧪 Testing ML Services...")
    
    # Test with BTC data
    btc_data = MarketData.objects.filter(symbol='BTC').order_by('date')
    
    if btc_data.count() > 100:
        # Convert to DataFrame
        data = pd.DataFrame(list(btc_data.values()))
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        
        # Test ML Predictor
        ml_predictor = MLPredictor()
        success, result = ml_predictor.train_price_predictor('BTC', data, 'random_forest')
        
        if success:
            print(f"✅ ML Predictor test successful - R² Score: {result['r2']:.3f}")
        else:
            print(f"❌ ML Predictor test failed: {result}")
        
        # Test Market Regime Detector
        regime_detector = MarketRegimeDetector()
        regimes, regime_analysis = regime_detector.detect_regimes(data, 3)
        
        if regimes is not None:
            print(f"✅ Market Regime Detector test successful - Found {len(regime_analysis)} regimes")
        else:
            print(f"❌ Market Regime Detector test failed: {regime_analysis}")
        
        # Test Feature Engineer
        features = FeatureEngineer.create_technical_features(data)
        print(f"✅ Feature Engineer test successful - Generated {len(features.columns)} features")
    
    else:
        print("⚠️  Insufficient data for ML testing")

def main():
    """Main setup function"""
    print("🚀 Starting Phase 5B Setup - Advanced Analytics & Machine Learning Integration")
    print("=" * 80)
    
    try:
        # Create ML models directory
        create_ml_models_directory()
        
        # Generate sample data
        print("\n📊 Generating Sample Data...")
        generate_sample_market_data()
        generate_sample_sentiment_data()
        
        # Create portfolio and related data
        print("\n💼 Setting up Portfolio...")
        portfolio = create_sample_portfolio()
        generate_sample_positions(portfolio)
        generate_sample_trades(portfolio)
        generate_sample_performance_metrics(portfolio)
        
        # Test ML services
        test_ml_services()
        
        print("\n" + "=" * 80)
        print("🎉 Phase 5B Setup Complete!")
        print("\n📋 What's Available:")
        print("   • ML Dashboard: /analytics/ml/")
        print("   • Model Training: /analytics/ml/train/")
        print("   • Price Predictions: /analytics/ml/predict/")
        print("   • Market Regime Analysis: /analytics/ml/regime/")
        print("   • Sentiment ML Analysis: /analytics/ml/sentiment/")
        print("   • Feature Engineering: /analytics/ml/features/")
        print("\n🔧 ML Features:")
        print("   • Random Forest & Linear Regression models")
        print("   • Market regime detection using K-means clustering")
        print("   • Sentiment-based price prediction")
        print("   • Automated feature engineering")
        print("   • Technical indicators (RSI, MACD, Bollinger Bands)")
        print("   • Performance metrics (Sharpe ratio, VaR, Max drawdown)")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
