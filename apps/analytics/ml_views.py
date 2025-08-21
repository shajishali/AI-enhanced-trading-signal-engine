from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np

from .models import AnalyticsPortfolio, MarketData, BacktestResult
from .ml_services import MLPredictor, MarketRegimeDetector, SentimentAnalyzer, FeatureEngineer
from apps.signals.models import TradingSignal
from .models import SentimentData

@login_required
def ml_dashboard(request):
    """Machine Learning dashboard with model performance and predictions"""
    user = request.user
    
    # Initialize ML services
    ml_predictor = MLPredictor()
    regime_detector = MarketRegimeDetector()
    
    # Get available symbols
    symbols = MarketData.objects.values_list('symbol', flat=True).distinct()[:10]
    
    # Get recent predictions
    recent_predictions = []
    
    # Get model performance metrics
    model_performance = {
        'trained_models': len(ml_predictor.models),
        'active_predictions': 0,
        'avg_accuracy': 0.75,  # Placeholder
        'last_updated': timezone.now()
    }
    
    context = {
        'symbols': symbols,
        'recent_predictions': recent_predictions,
        'model_performance': model_performance,
        'ml_predictor': ml_predictor,
    }
    
    return render(request, 'analytics/ml_dashboard.html', context)

@login_required
def train_model(request):
    """Train ML models for price prediction"""
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        model_type = request.POST.get('model_type', 'random_forest')
        lookback_days = int(request.POST.get('lookback_days', 365))
        
        if not symbol:
            return JsonResponse({
                'success': False,
                'error': 'Symbol is required'
            }, status=400)
        
        try:
            # Get market data
            end_date = timezone.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            market_data = MarketData.objects.filter(
                symbol=symbol,
                date__range=[start_date, end_date]
            ).order_by('date')
            
            if len(market_data) < 100:
                return JsonResponse({
                    'success': False,
                    'error': f'Insufficient data for {symbol}. Need at least 100 data points.'
                }, status=400)
            
            # Convert to DataFrame
            data = pd.DataFrame(list(market_data.values()))
            data['date'] = pd.to_datetime(data['date'])
            data.set_index('date', inplace=True)
            
            # Train model
            ml_predictor = MLPredictor()
            success, result = ml_predictor.train_price_predictor(symbol, data, model_type)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f'Model trained successfully for {symbol}. R² Score: {result.get("r2", 0):.3f}',
                    'symbol': symbol,
                    'model_type': model_type,
                    'r2_score': result.get('r2', 0)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Model training failed: {result}'
                }, status=500)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Training error: {str(e)}'
            }, status=500)
    
    # For GET requests, return the form
    symbols = MarketData.objects.values_list('symbol', flat=True).distinct()[:20]
    
    context = {
        'symbols': symbols,
        'model_types': ['random_forest', 'linear'],
    }
    
    return render(request, 'analytics/train_model.html', context)

@login_required
def make_prediction(request):
    """Make price predictions using trained models"""
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        model_type = request.POST.get('model_type', 'random_forest')
        
        # Get recent market data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=60)
        
        market_data = MarketData.objects.filter(
            symbol=symbol,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        if len(market_data) < 30:
            return JsonResponse({
                'success': False,
                'error': 'Insufficient data for prediction'
            })
        
        # Convert to DataFrame
        data = pd.DataFrame(list(market_data.values()))
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        
        # Make prediction
        ml_predictor = MLPredictor()
        prediction, message = ml_predictor.predict_price_movement(symbol, data, model_type)
        
        if prediction is not None:
            # Get current price
            current_price = data['close_price'].iloc[-1]
            predicted_return = prediction
            predicted_price = current_price * (1 + predicted_return)
            
            # Determine signal strength
            if predicted_return > 0.02:
                signal = 'STRONG_BUY'
                confidence = min(abs(predicted_return) * 50, 95)
            elif predicted_return > 0.005:
                signal = 'BUY'
                confidence = min(abs(predicted_return) * 40, 80)
            elif predicted_return < -0.02:
                signal = 'STRONG_SELL'
                confidence = min(abs(predicted_return) * 50, 95)
            elif predicted_return < -0.005:
                signal = 'SELL'
                confidence = min(abs(predicted_return) * 40, 80)
            else:
                signal = 'HOLD'
                confidence = 50
            
            return JsonResponse({
                'success': True,
                'prediction': {
                    'symbol': symbol,
                    'current_price': float(current_price),
                    'predicted_return': float(predicted_return),
                    'predicted_price': float(predicted_price),
                    'signal': signal,
                    'confidence': confidence,
                    'timestamp': timezone.now().isoformat()
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': message
            })
    
    symbols = MarketData.objects.values_list('symbol', flat=True).distinct()[:20]
    
    context = {
        'symbols': symbols,
        'model_types': ['random_forest', 'linear'],
    }
    
    return render(request, 'analytics/make_prediction.html', context)

@login_required
def market_regime_analysis(request):
    """Analyze and detect market regimes"""
    if request.method == 'POST':
        symbol = request.POST.get('symbol', 'BTC')
        n_regimes = int(request.POST.get('n_regimes', 3))
        lookback_days = int(request.POST.get('lookback_days', 365))
        
        # Get market data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        market_data = MarketData.objects.filter(
            symbol=symbol,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        if len(market_data) < 100:
            messages.error(request, f"Insufficient data for regime analysis of {symbol}")
            return redirect('analytics:market_regime_analysis')
        
        # Convert to DataFrame
        data = pd.DataFrame(list(market_data.values()))
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        
        # Detect regimes
        regime_detector = MarketRegimeDetector()
        regimes, regime_analysis = regime_detector.detect_regimes(data, n_regimes)
        
        if regimes is not None:
            # Add regime information to data
            data['regime'] = regimes
            
            # Get current regime
            current_regime, _ = regime_detector.predict_current_regime(data)
            
            context = {
                'symbol': symbol,
                'regime_data': data.to_dict('records'),
                'regime_analysis': regime_analysis,
                'current_regime': current_regime,
                'n_regimes': n_regimes,
            }
            
            return render(request, 'analytics/market_regime_results.html', context)
        else:
            messages.error(request, f"Regime detection failed: {regime_analysis}")
            return redirect('analytics:market_regime_analysis')
    
    symbols = MarketData.objects.values_list('symbol', flat=True).distinct()[:20]
    
    context = {
        'symbols': symbols,
    }
    
    return render(request, 'analytics/market_regime_analysis.html', context)

@login_required
def sentiment_ml_analysis(request):
    """Advanced sentiment analysis using ML"""
    if request.method == 'POST':
        symbol = request.POST.get('symbol', 'BTC')
        lookback_days = int(request.POST.get('lookback_days', 90))
        
        # Get sentiment data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        sentiment_data = SentimentData.objects.filter(
            symbol=symbol,
            timestamp__range=[start_date, end_date]
        ).order_by('timestamp')
        
        # Get market data
        market_data = MarketData.objects.filter(
            symbol=symbol,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        if len(sentiment_data) < 30 or len(market_data) < 30:
            messages.error(request, f"Insufficient data for sentiment analysis of {symbol}")
            return redirect('analytics:sentiment_ml_analysis')
        
        # Convert to DataFrames
        sentiment_df = pd.DataFrame(list(sentiment_data.values()))
        sentiment_df['timestamp'] = pd.to_datetime(sentiment_df['timestamp'])
        sentiment_df.set_index('timestamp', inplace=True)
        
        market_df = pd.DataFrame(list(market_data.values()))
        market_df['date'] = pd.to_datetime(market_df['date'])
        market_df.set_index('date', inplace=True)
        
        # Train sentiment predictor
        sentiment_analyzer = SentimentAnalyzer()
        success, result = sentiment_analyzer.train_sentiment_predictor(sentiment_df, market_df)
        
        if success:
            context = {
                'symbol': symbol,
                'sentiment_data': sentiment_df.to_dict('records'),
                'market_data': market_df.to_dict('records'),
                'model_performance': result,
            }
            
            return render(request, 'analytics/sentiment_ml_results.html', context)
        else:
            messages.error(request, f"Sentiment analysis failed: {result}")
            return redirect('analytics:sentiment_ml_analysis')
    
    symbols = SentimentData.objects.values_list('symbol', flat=True).distinct()[:20]
    
    context = {
        'symbols': symbols,
    }
    
    return render(request, 'analytics/sentiment_ml_analysis.html', context)

@login_required
def feature_engineering_dashboard(request):
    """Dashboard for feature engineering and technical indicators"""
    if request.method == 'POST':
        symbol = request.POST.get('symbol', 'BTC')
        lookback_days = int(request.POST.get('lookback_days', 365))
        
        # Get market data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        market_data = MarketData.objects.filter(
            symbol=symbol,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        if len(market_data) < 50:
            messages.error(request, f"Insufficient data for feature engineering of {symbol}")
            return redirect('analytics:feature_engineering_dashboard')
        
        # Convert to DataFrame
        data = pd.DataFrame(list(market_data.values()))
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        
        # Generate technical features
        features = FeatureEngineer.create_technical_features(data)
        
        # Combine with original data
        combined_data = data.join(features)
        
        # Get feature statistics
        feature_stats = {}
        for column in features.columns:
            feature_stats[column] = {
                'mean': float(features[column].mean()),
                'std': float(features[column].std()),
                'min': float(features[column].min()),
                'max': float(features[column].max()),
                'correlation_with_price': float(features[column].corr(data['close_price']))
            }
        
        context = {
            'symbol': symbol,
            'feature_data': combined_data.to_dict('records'),
            'feature_stats': feature_stats,
            'feature_columns': list(features.columns),
        }
        
        return render(request, 'analytics/feature_engineering_results.html', context)
    
    symbols = MarketData.objects.values_list('symbol', flat=True).distinct()[:20]
    
    context = {
        'symbols': symbols,
    }
    
    return render(request, 'analytics/feature_engineering_dashboard.html', context)

@login_required
def model_performance_api(request):
    """API endpoint for model performance metrics"""
    ml_predictor = MLPredictor()
    
    # Get model statistics
    model_stats = {
        'total_models': len(ml_predictor.models),
        'model_types': list(set([key.split('_')[1] for key in ml_predictor.models.keys()])),
        'symbols': list(set([key.split('_')[0] for key in ml_predictor.models.keys()])),
    }
    
    return JsonResponse({
        'success': True,
        'model_stats': model_stats,
        'timestamp': timezone.now().isoformat()
    })

@login_required
def prediction_history_api(request):
    """API endpoint for prediction history"""
    symbol = request.GET.get('symbol', 'BTC')
    days = int(request.GET.get('days', 30))
    
    # This would typically come from a PredictionHistory model
    # For now, return sample data
    predictions = [
        {
            'date': (timezone.now() - timedelta(days=i)).isoformat(),
            'symbol': symbol,
            'predicted_return': round(np.random.normal(0, 0.02), 4),
            'actual_return': round(np.random.normal(0, 0.02), 4),
            'accuracy': round(np.random.uniform(0.6, 0.9), 2)
        }
        for i in range(days)
    ]
    
    return JsonResponse({
        'success': True,
        'predictions': predictions,
        'symbol': symbol
    })
