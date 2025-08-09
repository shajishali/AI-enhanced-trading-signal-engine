from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import json

class SentimentData(models.Model):
    """Sentiment data for ML analysis"""
    symbol = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    compound_score = models.FloatField()  # VADER compound score (-1 to 1)
    positive_score = models.FloatField()  # Positive sentiment (0 to 1)
    negative_score = models.FloatField()  # Negative sentiment (0 to 1)
    neutral_score = models.FloatField()   # Neutral sentiment (0 to 1)
    source = models.CharField(max_length=50, default='unknown')  # Data source
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['symbol', 'timestamp', 'source']
        indexes = [
            models.Index(fields=['symbol', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.timestamp} - {self.compound_score:.3f}"

class AnalyticsPortfolio(models.Model):
    """Portfolio model for tracking user investments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_portfolios')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    initial_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('10000.00'))
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('10000.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    @property
    def total_return(self):
        """Calculate total return percentage"""
        if self.initial_balance > 0:
            return ((self.current_balance - self.initial_balance) / self.initial_balance) * 100
        return 0

    @property
    def total_return_amount(self):
        """Calculate total return amount"""
        return self.current_balance - self.initial_balance

class AnalyticsPosition(models.Model):
    """Position model for tracking individual holdings"""
    portfolio = models.ForeignKey(AnalyticsPortfolio, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    entry_price = models.DecimalField(max_digits=15, decimal_places=2)
    current_price = models.DecimalField(max_digits=15, decimal_places=2)
    entry_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.symbol} - {self.quantity} @ ${self.entry_price}"

    @property
    def market_value(self):
        """Calculate current market value"""
        return self.quantity * self.current_price

    @property
    def unrealized_pnl(self):
        """Calculate unrealized profit/loss"""
        return (self.current_price - self.entry_price) * self.quantity

    @property
    def unrealized_pnl_percent(self):
        """Calculate unrealized profit/loss percentage"""
        if self.entry_price > 0:
            return ((self.current_price - self.entry_price) / self.entry_price) * 100
        return 0

class AnalyticsTrade(models.Model):
    """Trade model for tracking executed trades"""
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    portfolio = models.ForeignKey(AnalyticsPortfolio, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    timestamp = models.DateTimeField(auto_now_add=True)
    signal = models.ForeignKey('signals.TradingSignal', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.trade_type} {self.quantity} {self.symbol} @ ${self.price}"

    @property
    def total_value(self):
        """Calculate total trade value"""
        return self.quantity * self.price

    @property
    def net_value(self):
        """Calculate net trade value after commission"""
        return self.total_value - self.commission

class PerformanceMetrics(models.Model):
    """Performance metrics for portfolio analysis"""
    portfolio = models.ForeignKey(AnalyticsPortfolio, on_delete=models.CASCADE)
    date = models.DateField()
    
    # Basic metrics
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    daily_return = models.DecimalField(max_digits=10, decimal_places=6)
    cumulative_return = models.DecimalField(max_digits=10, decimal_places=6)
    
    # Risk metrics
    volatility = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    var_95 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)  # Value at Risk 95%
    
    # Additional metrics
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    profit_factor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    avg_win = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    avg_loss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['portfolio', 'date']

    def __str__(self):
        return f"{self.portfolio.name} - {self.date}"

class BacktestResult(models.Model):
    """Backtest results for strategy validation"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    strategy_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    initial_capital = models.DecimalField(max_digits=15, decimal_places=2)
    final_capital = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Performance metrics
    total_return = models.DecimalField(max_digits=10, decimal_places=6)
    annualized_return = models.DecimalField(max_digits=10, decimal_places=6)
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=6)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=6)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2)
    profit_factor = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Trade statistics
    total_trades = models.IntegerField()
    winning_trades = models.IntegerField()
    losing_trades = models.IntegerField()
    
    # Strategy parameters (stored as JSON)
    parameters = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.strategy_name} - {self.start_date} to {self.end_date}"

    @property
    def total_trades_count(self):
        return self.winning_trades + self.losing_trades

class MarketData(models.Model):
    """Market data for technical analysis"""
    symbol = models.CharField(max_length=10)
    date = models.DateTimeField()
    open_price = models.DecimalField(max_digits=15, decimal_places=2)
    high_price = models.DecimalField(max_digits=15, decimal_places=2)
    low_price = models.DecimalField(max_digits=15, decimal_places=2)
    close_price = models.DecimalField(max_digits=15, decimal_places=2)
    volume = models.BigIntegerField()
    
    # Technical indicators
    sma_20 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    sma_50 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    sma_200 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    rsi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    macd = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    macd_signal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    bollinger_upper = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    bollinger_lower = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['symbol', 'date']
        indexes = [
            models.Index(fields=['symbol', 'date']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.date}"

class Alert(models.Model):
    """Trading alerts and notifications"""
    ALERT_TYPES = [
        ('PRICE', 'Price Alert'),
        ('SIGNAL', 'Signal Alert'),
        ('PORTFOLIO', 'Portfolio Alert'),
        ('SYSTEM', 'System Alert'),
    ]
    
    ALERT_STATUS = [
        ('PENDING', 'Pending'),
        ('TRIGGERED', 'Triggered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    symbol = models.CharField(max_length=10, blank=True)
    price_target = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=ALERT_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.alert_type} - {self.title}"

    class Meta:
        ordering = ['-created_at']
