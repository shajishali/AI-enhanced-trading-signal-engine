from django.urls import path
from . import views

app_name = 'data'

urlpatterns = [
    path('market-data/<int:symbol_id>/', views.get_market_data, name='market_data'),
    path('indicators/<int:symbol_id>/', views.get_technical_indicators, name='technical_indicators'),
    path('sync/', views.sync_data_manual, name='sync_data'),
    path('calculate-indicators/', views.calculate_indicators_manual, name='calculate_indicators'),
    path('dashboard/', views.data_dashboard, name='dashboard'),
]
