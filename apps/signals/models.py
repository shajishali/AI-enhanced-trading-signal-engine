from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.trading.models import Symbol
from apps.data.models import TechnicalIndicator
from apps.sentiment.models import SentimentAggregate


class SignalType(models.Model):
    """Types of trading signals"""
    SIGNAL_TYPES = [
        ('BUY', 'Buy Signal'),
        ('SELL', 'Sell Signal'),
        ('HOLD', 'Hold Signal'),
        ('STRONG_BUY', 'Strong Buy'),
        ('STRONG_SELL', 'Strong Sell'),
    ]
    
    name = models.CharField(max_length=20, choices=SIGNAL_TYPES, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#000000')  # Hex color
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class SignalFactor(models.Model):
    """Individual factors that contribute to signal generation"""
    FACTOR_TYPES = [
        ('TECHNICAL', 'Technical Indicator'),
        ('SENTIMENT', 'Sentiment Analysis'),
        ('NEWS', 'News Event'),
        ('VOLUME', 'Volume Analysis'),
        ('PATTERN', 'Chart Pattern'),
        ('CORRELATION', 'Correlation Analysis'),
    ]
    
    name = models.CharField(max_length=100)
    factor_type = models.CharField(max_length=20, choices=FACTOR_TYPES)
    weight = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.1,
        help_text="Weight of this factor in signal calculation (0-1)"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Signal Factor'
        verbose_name_plural = 'Signal Factors'
    
    def __str__(self):
        return f"{self.name} ({self.factor_type})"


class TradingSignal(models.Model):
    """Generated trading signals with quality metrics"""
    SIGNAL_STRENGTHS = [
        ('WEAK', 'Weak'),
        ('MODERATE', 'Moderate'),
        ('STRONG', 'Strong'),
        ('VERY_STRONG', 'Very Strong'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('LOW', 'Low (<50%)'),
        ('MEDIUM', 'Medium (50-70%)'),
        ('HIGH', 'High (70-85%)'),
        ('VERY_HIGH', 'Very High (>85%)'),
    ]
    
    # Basic signal information
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    signal_type = models.ForeignKey(SignalType, on_delete=models.CASCADE)
    strength = models.CharField(max_length=20, choices=SIGNAL_STRENGTHS)
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence score (0-1)"
    )
    confidence_level = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS)
    
    # Signal details
    entry_price = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    target_price = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    stop_loss = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    risk_reward_ratio = models.FloatField(null=True, blank=True)
    
    # Quality metrics
    quality_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Overall signal quality score"
    )
    is_valid = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Contributing factors
    technical_score = models.FloatField(default=0.0)
    sentiment_score = models.FloatField(default=0.0)
    news_score = models.FloatField(default=0.0)
    volume_score = models.FloatField(default=0.0)
    pattern_score = models.FloatField(default=0.0)
    
    # Performance tracking
    is_executed = models.BooleanField(default=False)
    executed_at = models.DateTimeField(null=True, blank=True)
    execution_price = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    is_profitable = models.BooleanField(null=True, blank=True)
    profit_loss = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Trading Signal'
        verbose_name_plural = 'Trading Signals'
        indexes = [
            models.Index(fields=['symbol', 'created_at']),
            models.Index(fields=['signal_type', 'confidence_score']),
            models.Index(fields=['is_valid', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.symbol.symbol} {self.signal_type.name} - {self.confidence_score:.2f}"
    
    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    @property
    def time_to_expiry(self):
        if not self.expires_at:
            return None
        return self.expires_at - timezone.now()


class SignalFactorContribution(models.Model):
    """Individual factor contributions to a signal"""
    signal = models.ForeignKey(TradingSignal, on_delete=models.CASCADE, related_name='factor_contributions')
    factor = models.ForeignKey(SignalFactor, on_delete=models.CASCADE)
    score = models.FloatField(help_text="Factor score (-1 to 1)")
    weight = models.FloatField(help_text="Weight applied to this factor")
    contribution = models.FloatField(help_text="Weighted contribution to final signal")
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Signal Factor Contribution'
        verbose_name_plural = 'Signal Factor Contributions'
    
    def __str__(self):
        return f"{self.signal.symbol.symbol} - {self.factor.name}: {self.contribution:.3f}"


class MarketRegime(models.Model):
    """Market regime classification for adaptive strategies"""
    REGIME_TYPES = [
        ('BULL', 'Bull Market'),
        ('BEAR', 'Bear Market'),
        ('SIDEWAYS', 'Sideways Market'),
        ('VOLATILE', 'High Volatility'),
        ('LOW_VOL', 'Low Volatility'),
    ]
    
    name = models.CharField(max_length=20, choices=REGIME_TYPES)
    description = models.TextField(blank=True)
    volatility_level = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Market volatility level (0-1)"
    )
    trend_strength = models.FloatField(
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="Trend strength (-1 to 1)"
    )
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Regime classification confidence"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Market Regime'
        verbose_name_plural = 'Market Regimes'
        indexes = [
            models.Index(fields=['name', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class SignalPerformance(models.Model):
    """Performance tracking for signal generation system"""
    PERIOD_TYPES = [
        ('1H', '1 Hour'),
        ('4H', '4 Hours'),
        ('1D', '1 Day'),
        ('1W', '1 Week'),
        ('1M', '1 Month'),
    ]
    
    period_type = models.CharField(max_length=3, choices=PERIOD_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Performance metrics
    total_signals = models.IntegerField(default=0)
    profitable_signals = models.IntegerField(default=0)
    win_rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Win rate (0-1)"
    )
    average_profit = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    average_loss = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    profit_factor = models.FloatField(default=0.0)
    max_drawdown = models.FloatField(default=0.0)
    
    # Signal quality metrics
    average_confidence = models.FloatField(default=0.0)
    average_quality_score = models.FloatField(default=0.0)
    signal_accuracy = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Signal Performance'
        verbose_name_plural = 'Signal Performances'
        indexes = [
            models.Index(fields=['period_type', 'start_date']),
        ]
    
    def __str__(self):
        return f"{self.period_type} Performance - {self.start_date.strftime('%Y-%m-%d')}"


class SignalAlert(models.Model):
    """Alerts and notifications for signal events"""
    ALERT_TYPES = [
        ('SIGNAL_GENERATED', 'Signal Generated'),
        ('SIGNAL_EXPIRED', 'Signal Expired'),
        ('SIGNAL_EXECUTED', 'Signal Executed'),
        ('PERFORMANCE_ALERT', 'Performance Alert'),
        ('SYSTEM_ALERT', 'System Alert'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='MEDIUM')
    title = models.CharField(max_length=200)
    message = models.TextField()
    signal = models.ForeignKey(TradingSignal, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Signal Alert'
        verbose_name_plural = 'Signal Alerts'
        indexes = [
            models.Index(fields=['alert_type', 'created_at']),
            models.Index(fields=['priority', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.alert_type} - {self.title}"
