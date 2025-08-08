from django.db import models
from apps.trading.models import Symbol


class DataSource(models.Model):
    """Data sources for market data"""
    SOURCE_TYPES = [
        ('API', 'API'),
        ('WEBSOCKET', 'WebSocket'),
        ('FILE', 'File'),
        ('DATABASE', 'Database'),
    ]
    
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPES)
    base_url = models.URLField(blank=True)
    api_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class MarketData(models.Model):
    """Market data OHLCV records"""
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    open_price = models.DecimalField(max_digits=15, decimal_places=6)
    high_price = models.DecimalField(max_digits=15, decimal_places=6)
    low_price = models.DecimalField(max_digits=15, decimal_places=6)
    close_price = models.DecimalField(max_digits=15, decimal_places=6)
    volume = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['symbol', 'timestamp']
        indexes = [
            models.Index(fields=['symbol', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.symbol.symbol} - {self.timestamp}"


class DataFeed(models.Model):
    """Real-time data feeds"""
    FEED_TYPES = [
        ('REALTIME', 'Real-time'),
        ('HISTORICAL', 'Historical'),
        ('STREAMING', 'Streaming'),
    ]
    
    name = models.CharField(max_length=100)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    feed_type = models.CharField(max_length=10, choices=FEED_TYPES)
    is_active = models.BooleanField(default=True)
    last_update = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.symbol.symbol}"


class TechnicalIndicator(models.Model):
    """Technical indicators calculated from market data"""
    INDICATOR_TYPES = [
        ('SMA', 'Simple Moving Average'),
        ('EMA', 'Exponential Moving Average'),
        ('RSI', 'Relative Strength Index'),
        ('MACD', 'MACD'),
        ('BB', 'Bollinger Bands'),
        ('ATR', 'Average True Range'),
        ('STOCH', 'Stochastic'),
        ('CCI', 'Commodity Channel Index'),
    ]
    
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    indicator_type = models.CharField(max_length=10, choices=INDICATOR_TYPES)
    period = models.IntegerField()
    value = models.DecimalField(max_digits=15, decimal_places=6)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['symbol', 'indicator_type', 'period', 'timestamp']
        indexes = [
            models.Index(fields=['symbol', 'indicator_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.symbol.symbol} {self.indicator_type}({self.period}) - {self.timestamp}"


class DataSyncLog(models.Model):
    """Log for data synchronization operations"""
    SYNC_TYPES = [
        ('MARKET_DATA', 'Market Data'),
        ('TECHNICAL_INDICATORS', 'Technical Indicators'),
        ('SIGNALS', 'Signals'),
    ]
    
    SYNC_STATUS = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=15, choices=SYNC_STATUS, default='PENDING')
    records_processed = models.IntegerField(default=0)
    records_added = models.IntegerField(default=0)
    records_updated = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.sync_type} - {self.symbol.symbol if self.symbol else 'All'} - {self.status}"
