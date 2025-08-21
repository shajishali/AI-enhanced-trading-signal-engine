from django.urls import path
from . import views

app_name = 'signals'

urlpatterns = [
    # API endpoints
    path('api/signals/', views.SignalAPIView.as_view(), name='signal_api'),
    path('api/signals/<int:signal_id>/', views.SignalDetailView.as_view(), name='signal_detail'),
    path('api/signals/<int:signal_id>/execute/', views.execute_signal, name='execute_signal'),
    path('api/performance/', views.SignalPerformanceView.as_view(), name='signal_performance'),
    path('api/regimes/', views.MarketRegimeView.as_view(), name='market_regime'),
    path('api/alerts/', views.SignalAlertView.as_view(), name='signal_alerts'),
    path('api/statistics/', views.signal_statistics, name='signal_statistics'),
    path('api/generate/', views.generate_signals_manual, name='generate_signals'),
    path('api/reset-testing/', views.reset_signals_for_testing, name='reset_signals_testing'),
    path('api/sync-prices/', views.sync_signal_prices, name='sync_signal_prices'),
    
    # Dashboard views
    path('', views.signal_dashboard, name='signal_dashboard'),  # Main signals page
    path('signals/dashboard/', views.signal_dashboard, name='signal_dashboard_detail'),
]
