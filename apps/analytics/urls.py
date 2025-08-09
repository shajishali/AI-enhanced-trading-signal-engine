from django.urls import path
from . import views
from . import ml_views

app_name = 'analytics'

urlpatterns = [
    # Main analytics views
    path('', views.analytics_dashboard, name='dashboard'),
    path('portfolio/', views.portfolio_view, name='portfolio'),
    path('performance/', views.performance_analytics, name='performance'),
    path('backtesting/', views.backtesting_view, name='backtesting'),
    path('risk/', views.risk_management, name='risk_management'),
    path('market/', views.market_analysis, name='market_analysis'),
    
    # Machine Learning views (Phase 5B)
    path('ml/', ml_views.ml_dashboard, name='ml_dashboard'),
    path('ml/train/', ml_views.train_model, name='train_model'),
    path('ml/predict/', ml_views.make_prediction, name='make_prediction'),
    path('ml/regime/', ml_views.market_regime_analysis, name='market_regime_analysis'),
    path('ml/sentiment/', ml_views.sentiment_ml_analysis, name='sentiment_ml_analysis'),
    path('ml/features/', ml_views.feature_engineering_dashboard, name='feature_engineering_dashboard'),
    
    # API endpoints
    path('api/portfolio-data/', views.portfolio_data_api, name='portfolio_data_api'),
    path('api/position-data/', views.position_data_api, name='position_data_api'),
    path('api/market-data/', views.market_data_api, name='market_data_api'),
    
    # ML API endpoints
    path('api/ml/performance/', ml_views.model_performance_api, name='model_performance_api'),
    path('api/ml/predictions/', ml_views.prediction_history_api, name='prediction_history_api'),
]
