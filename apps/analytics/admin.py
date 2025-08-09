from django.contrib import admin
from .models import AnalyticsPortfolio, AnalyticsPosition, AnalyticsTrade, PerformanceMetrics, BacktestResult, MarketData, Alert

@admin.register(AnalyticsPortfolio)
class AnalyticsPortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'initial_balance', 'current_balance', 'total_return', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'name']
    readonly_fields = ['total_return', 'total_return_amount']

@admin.register(AnalyticsPosition)
class AnalyticsPositionAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'symbol', 'quantity', 'entry_price', 'current_price', 'unrealized_pnl', 'is_open']
    list_filter = ['is_open', 'entry_date']
    search_fields = ['symbol', 'portfolio__name']
    readonly_fields = ['market_value', 'unrealized_pnl', 'unrealized_pnl_percent']

@admin.register(AnalyticsTrade)
class AnalyticsTradeAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'symbol', 'trade_type', 'quantity', 'price', 'total_value', 'timestamp']
    list_filter = ['trade_type', 'timestamp']
    search_fields = ['symbol', 'portfolio__name']
    readonly_fields = ['total_value', 'net_value']

@admin.register(PerformanceMetrics)
class PerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'date', 'total_value', 'daily_return', 'sharpe_ratio', 'max_drawdown']
    list_filter = ['date']
    search_fields = ['portfolio__name']

@admin.register(BacktestResult)
class BacktestResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'strategy_name', 'start_date', 'end_date', 'total_return', 'sharpe_ratio', 'win_rate']
    list_filter = ['start_date', 'end_date']
    search_fields = ['strategy_name', 'user__username']
    readonly_fields = ['total_trades_count']

@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'date', 'close_price', 'volume', 'rsi', 'sma_20']
    list_filter = ['symbol', 'date']
    search_fields = ['symbol']
    readonly_fields = ['created_at']

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'alert_type', 'title', 'status', 'created_at', 'is_read']
    list_filter = ['alert_type', 'status', 'created_at', 'is_read']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at']
