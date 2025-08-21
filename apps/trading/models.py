from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Portfolio(models.Model):
    """Portfolio model to track user's trading portfolio"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Portfolio - {self.name}"


class Symbol(models.Model):
    """Trading symbol/instrument model"""
    SYMBOL_TYPES = [
        ('STOCK', 'Stock'),
        ('CRYPTO', 'Cryptocurrency'),
        ('FOREX', 'Forex'),
        ('COMMODITY', 'Commodity'),
        ('INDEX', 'Index'),
    ]
    
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    symbol_type = models.CharField(max_length=10, choices=SYMBOL_TYPES)
    exchange = models.CharField(max_length=50, blank=True)
    sector = models.ForeignKey('data.Sector', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"


class Position(models.Model):
    """Position model to track open positions"""
    POSITION_TYPES = [
        ('LONG', 'Long'),
        ('SHORT', 'Short'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    position_type = models.CharField(max_length=5, choices=POSITION_TYPES)
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    entry_price = models.DecimalField(max_digits=15, decimal_places=6)
    current_price = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    stop_loss = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    take_profit = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    is_open = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.symbol.symbol} {self.position_type} - {self.quantity}"
    
    @property
    def unrealized_pnl(self):
        if not self.current_price or not self.is_open:
            return 0
        if self.position_type == 'LONG':
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity


class Trade(models.Model):
    """Trade model to track executed trades"""
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    price = models.DecimalField(max_digits=15, decimal_places=6)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    executed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.symbol.symbol} {self.trade_type} - {self.quantity} @ {self.price}"
    
    @property
    def total_value(self):
        return self.quantity * self.price


class RiskSettings(models.Model):
    """Risk management settings for portfolios"""
    portfolio = models.OneToOneField(Portfolio, on_delete=models.CASCADE)
    max_position_size = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_risk_per_trade = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=2.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    stop_loss_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=5.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    take_profit_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    def __str__(self):
        return f"Risk Settings for {self.portfolio.name}"
