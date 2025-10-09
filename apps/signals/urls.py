from django.urls import path
from . import views
from . import backtesting_api
from . import duplicate_signal_api

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
    
    # Backtesting API endpoints
    path('api/backtests/', backtesting_api.BacktestAPIView.as_view(), name='backtest_api'),
    path('api/backtests/search/', backtesting_api.BacktestSearchAPIView.as_view(), name='backtest_search_api'),
    path('api/backtests/tradingview/', backtesting_api.TradingViewExportAPIView.as_view(), name='backtest_tradingview_export'),
    path('api/backtests/history-export/', backtesting_api.BacktestingHistoryExportAPIView.as_view(), name='backtesting_history_export'),
    path('api/backtests/available-symbols/', backtesting_api.AvailableSymbolsAPIView.as_view(), name='backtest_available_symbols'),
    
    # Duplicate signal removal API endpoints
    path('api/duplicates/', duplicate_signal_api.DuplicateSignalAPIView.as_view(), name='duplicate_signals_api'),
    path('api/duplicates/dashboard/', duplicate_signal_api.DuplicateSignalDashboardAPIView.as_view(), name='duplicate_signals_dashboard_api'),
    
    # Dashboard views
    path('', views.signal_dashboard, name='signal_dashboard'),  # Main signals page
    path('signals/dashboard/', views.signal_dashboard, name='signal_dashboard_detail'),
    path('history/', views.signal_history, name='signal_history'),
    path('spot/', views.spot_signals_dashboard, name='spot_signals_dashboard'),
    path('duplicates/', views.duplicate_signals_dashboard, name='duplicate_signals_dashboard'),
    path('backtesting-history/', views.backtesting_signals_history, name='backtesting_signals_history'),
]
