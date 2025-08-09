from django.urls import path
from . import views

app_name = 'signals'

urlpatterns = [
    # API endpoints
    path('api/signals/', views.SignalAPIView.as_view(), name='signal_api'),
    path('api/signals/<int:signal_id>/', views.SignalDetailView.as_view(), name='signal_detail'),
    path('api/performance/', views.SignalPerformanceView.as_view(), name='signal_performance'),
    path('api/regimes/', views.MarketRegimeView.as_view(), name='market_regime'),
    path('api/alerts/', views.SignalAlertView.as_view(), name='signal_alerts'),
    path('api/statistics/', views.signal_statistics, name='signal_statistics'),
    path('api/generate/', views.generate_signals_manual, name='generate_signals'),
    
    # Dashboard views
    path('dashboard/', views.signal_dashboard, name='signal_dashboard'),
]
