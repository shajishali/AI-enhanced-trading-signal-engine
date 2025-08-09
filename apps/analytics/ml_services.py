import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import joblib
import os
from datetime import datetime, timedelta
from decimal import Decimal
import json

class MLPredictor:
    """Machine Learning models for price prediction and signal generation"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_path = 'ml_models/'
        os.makedirs(self.model_path, exist_ok=True)
    
    def prepare_features(self, data, lookback_days=30):
        """Prepare features for ML models"""
        features = []
        
        # Convert Decimal fields to float for calculations
        close_price = data['close_price'].astype(float)
        volume = data['volume'].astype(float)
        
        # Technical indicators
        features.append(close_price.pct_change())  # Returns
        features.append(close_price.pct_change().rolling(5).mean())  # 5-day return
        features.append(close_price.pct_change().rolling(20).mean())  # 20-day return
        features.append(volume.pct_change())  # Volume change
        features.append(volume.rolling(5).mean() / volume)  # Volume ratio
        
        # Moving averages
        features.append(close_price / close_price.rolling(20).mean() - 1)  # MA ratio
        features.append(close_price / close_price.rolling(50).mean() - 1)  # MA ratio
        
        # Volatility
        features.append(close_price.pct_change().rolling(20).std())  # Volatility
        
        # RSI-like feature
        delta = close_price.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        features.append(rsi)
        
        # Create feature DataFrame
        feature_df = pd.concat(features, axis=1)
        feature_df.columns = ['returns', 'ret_5d', 'ret_20d', 'vol_change', 'vol_ratio', 
                             'ma_20_ratio', 'ma_50_ratio', 'volatility', 'rsi']
        
        # Create target (next day return)
        feature_df['target'] = data['close_price'].pct_change().shift(-1)
        
        # Remove NaN values
        feature_df = feature_df.dropna()
        
        return feature_df
    
    def train_price_predictor(self, symbol, data, model_type='random_forest'):
        """Train a price prediction model"""
        feature_df = self.prepare_features(data)
        
        if len(feature_df) < 100:
            return False, "Insufficient data for training"
        
        # Prepare features and target
        X = feature_df.drop('target', axis=1)
        y = feature_df['target']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        if model_type == 'random_forest':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == 'linear':
            model = LinearRegression()
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = model.score(X_test_scaled, y_test)
        
        # Save model
        model_key = f"{symbol}_{model_type}"
        self.models[model_key] = model
        self.scalers[model_key] = scaler
        
        # Save to disk
        joblib.dump(model, f"{self.model_path}{model_key}_model.pkl")
        joblib.dump(scaler, f"{self.model_path}{model_key}_scaler.pkl")
        
        return True, {
            'mse': mse,
            'r2': r2,
            'feature_importance': dict(zip(X.columns, model.feature_importances_)) if hasattr(model, 'feature_importances_') else {}
        }
    
    def predict_price_movement(self, symbol, data, model_type='random_forest'):
        """Predict price movement for next period"""
        model_key = f"{symbol}_{model_type}"
        
        if model_key not in self.models:
            return None, "Model not trained"
        
        # Prepare latest features
        feature_df = self.prepare_features(data)
        if len(feature_df) == 0:
            return None, "Insufficient data for prediction"
        
        latest_features = feature_df.iloc[-1:].drop('target', axis=1)
        
        # Scale features
        scaler = self.scalers[model_key]
        features_scaled = scaler.transform(latest_features)
        
        # Make prediction
        prediction = self.models[model_key].predict(features_scaled)[0]
        
        return prediction, "Success"
    
    def train_signal_classifier(self, symbol, data, signals, model_type='random_forest'):
        """Train a signal classification model"""
        feature_df = self.prepare_features(data)
        
        if len(feature_df) < 100:
            return False, "Insufficient data for training"
        
        # Prepare features
        X = feature_df.drop('target', axis=1)
        
        # Create signal labels (1 for buy, 0 for hold, -1 for sell)
        y = np.zeros(len(feature_df))
        for signal in signals:
            if signal.signal_type == 'BUY':
                y[feature_df.index.get_loc(signal.timestamp.date())] = 1
            elif signal.signal_type == 'SELL':
                y[feature_df.index.get_loc(signal.timestamp.date())] = -1
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        if model_type == 'random_forest':
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_type == 'logistic':
            model = LogisticRegression(random_state=42)
        else:
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Save model
        model_key = f"{symbol}_signal_{model_type}"
        self.models[model_key] = model
        self.scalers[model_key] = scaler
        
        return True, {
            'accuracy': accuracy,
            'classification_report': classification_report(y_test, y_pred)
        }

class MarketRegimeDetector:
    """Detect market regimes using clustering and statistical methods"""
    
    def __init__(self):
        self.regime_model = None
        self.regime_scaler = None
    
    def detect_regimes(self, data, n_regimes=3):
        """Detect market regimes using K-means clustering"""
        # Prepare features for regime detection
        features = []
        
        # Convert Decimal fields to float for calculations
        close_price = data['close_price'].astype(float)
        volume = data['volume'].astype(float)
        
        # Returns
        features.append(close_price.pct_change())
        
        # Volatility
        features.append(close_price.pct_change().rolling(20).std())
        
        # Volume
        features.append(volume.pct_change())
        
        # Create feature matrix
        feature_matrix = pd.concat(features, axis=1)
        feature_matrix.columns = ['returns', 'volatility', 'volume_change']
        feature_matrix = feature_matrix.dropna()
        
        if len(feature_matrix) < n_regimes * 10:
            return None, "Insufficient data for regime detection"
        
        # Scale features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(feature_matrix)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_regimes, random_state=42)
        regimes = kmeans.fit_predict(features_scaled)
        
        # Analyze regimes
        regime_analysis = {}
        for i in range(n_regimes):
            regime_data = feature_matrix[regimes == i]
            regime_analysis[f'regime_{i}'] = {
                'count': len(regime_data),
                'avg_return': regime_data['returns'].mean(),
                'avg_volatility': regime_data['volatility'].mean(),
                'avg_volume_change': regime_data['volume_change'].mean(),
                'color': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'][i % 5]
            }
        
        # Save model
        self.regime_model = kmeans
        self.regime_scaler = scaler
        
        return regimes, regime_analysis
    
    def predict_current_regime(self, data):
        """Predict current market regime"""
        if self.regime_model is None:
            return None, "Model not trained"
        
        # Convert Decimal fields to float for calculations
        close_price = data['close_price'].astype(float)
        volume = data['volume'].astype(float)
        
        # Prepare latest features
        latest_features = pd.DataFrame({
            'returns': [close_price.pct_change().iloc[-1]],
            'volatility': [close_price.pct_change().rolling(20).std().iloc[-1]],
            'volume_change': [volume.pct_change().iloc[-1]]
        })
        
        # Scale features
        features_scaled = self.regime_scaler.transform(latest_features)
        
        # Predict regime
        current_regime = self.regime_model.predict(features_scaled)[0]
        
        return current_regime, "Success"

class SentimentAnalyzer:
    """Advanced sentiment analysis using ML"""
    
    def __init__(self):
        self.sentiment_model = None
        self.sentiment_scaler = None
    
    def analyze_sentiment_features(self, sentiment_data):
        """Extract features from sentiment data"""
        features = []
        
        # Sentiment scores
        features.append(sentiment_data['compound_score'])
        features.append(sentiment_data['positive_score'])
        features.append(sentiment_data['negative_score'])
        features.append(sentiment_data['neutral_score'])
        
        # Sentiment trends
        features.append(sentiment_data['compound_score'].rolling(5).mean())
        features.append(sentiment_data['compound_score'].rolling(20).mean())
        
        # Sentiment volatility
        features.append(sentiment_data['compound_score'].rolling(10).std())
        
        # Volume-weighted sentiment
        if 'volume' in sentiment_data.columns:
            features.append((sentiment_data['compound_score'] * sentiment_data['volume']).rolling(5).mean())
        
        return pd.concat(features, axis=1)
    
    def train_sentiment_predictor(self, sentiment_data, price_data):
        """Train sentiment-based price prediction model"""
        # Prepare features
        sentiment_features = self.analyze_sentiment_features(sentiment_data)
        
        # Align with price data
        aligned_data = sentiment_features.join(price_data['close_price'], how='inner')
        aligned_data = aligned_data.dropna()
        
        if len(aligned_data) < 50:
            return False, "Insufficient data for training"
        
        # Create target (next day return)
        aligned_data['target'] = aligned_data['close_price'].pct_change().shift(-1)
        aligned_data = aligned_data.dropna()
        
        # Prepare features and target
        X = aligned_data.drop(['close_price', 'target'], axis=1)
        y = aligned_data['target']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = model.score(X_test_scaled, y_test)
        
        # Save model
        self.sentiment_model = model
        self.sentiment_scaler = scaler
        
        return True, {
            'mse': mse,
            'r2': r2,
            'feature_importance': dict(zip(X.columns, model.feature_importances_))
        }

class FeatureEngineer:
    """Automated feature engineering for ML models"""
    
    @staticmethod
    def create_technical_features(data):
        """Create comprehensive technical indicators"""
        features = {}
        
        # Convert Decimal fields to float for calculations
        close_price = data['close_price'].astype(float)
        volume = data['volume'].astype(float)
        
        # Price-based features
        features['price_change'] = close_price.pct_change()
        features['price_change_5d'] = close_price.pct_change(5)
        features['price_change_20d'] = close_price.pct_change(20)
        
        # Moving averages
        for period in [5, 10, 20, 50, 200]:
            features[f'sma_{period}'] = close_price.rolling(period).mean()
            features[f'ema_{period}'] = close_price.ewm(span=period).mean()
            features[f'price_sma_{period}_ratio'] = close_price / features[f'sma_{period}']
        
        # Volatility features
        for period in [5, 10, 20]:
            features[f'volatility_{period}'] = close_price.pct_change().rolling(period).std()
            features[f'atr_{period}'] = FeatureEngineer.calculate_atr(data, period)
        
        # Volume features
        features['volume_change'] = volume.pct_change()
        features['volume_sma_20'] = volume.rolling(20).mean()
        features['volume_ratio'] = volume / features['volume_sma_20']
        
        # Momentum indicators
        features['rsi'] = FeatureEngineer.calculate_rsi(close_price)
        features['macd'], features['macd_signal'] = FeatureEngineer.calculate_macd(close_price)
        features['stoch_k'], features['stoch_d'] = FeatureEngineer.calculate_stochastic(data)
        
        return pd.DataFrame(features)
    
    @staticmethod
    def calculate_atr(data, period=14):
        """Calculate Average True Range"""
        high = data['high_price'].astype(float)
        low = data['low_price'].astype(float)
        close = data['close_price'].astype(float)
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        
        return atr
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    @staticmethod
    def calculate_stochastic(data, k_period=14, d_period=3):
        """Calculate Stochastic Oscillator"""
        low_min = data['low_price'].astype(float).rolling(k_period).min()
        high_max = data['high_price'].astype(float).rolling(k_period).max()
        
        k = 100 * ((data['close_price'].astype(float) - low_min) / (high_max - low_min))
        d = k.rolling(d_period).mean()
        
        return k, d
