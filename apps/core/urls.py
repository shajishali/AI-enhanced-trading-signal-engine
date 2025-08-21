from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Performance monitoring (Phase 5)
    path('api/performance/', views.performance_metrics, name='performance_metrics'),
    
    # Real-time features (Phase 6)
    path('api/realtime/connect/', views.RealTimeConnectionView.as_view(), name='realtime_connect'),
    path('api/realtime/streaming/', views.MarketDataStreamingView.as_view(), name='market_data_streaming'),
    path('api/realtime/notifications/', views.RealTimeNotificationsView.as_view(), name='realtime_notifications'),
    path('api/realtime/status/', views.WebSocketStatusView.as_view(), name='websocket_status'),
    
    # Real-time dashboard (Phase 6)
    path('realtime-dashboard/', views.realtime_dashboard, name='realtime_dashboard'),
    
    # WebSocket test page (Phase 6)
    path('websocket-test/', views.websocket_test, name='websocket_test'),
    path('api/run-websocket-test/', views.run_websocket_test, name='run_websocket_test'),
]
