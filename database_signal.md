# Database-Driven Signal Generation - Phase Process Plan

## Overview
This document outlines the complete phase process for transitioning from live API-based signal generation to database-driven signal generation using the automated historical data storage system.

## Current System Analysis

### Current Live API Signal Generation
- **Data Source**: Live API calls to Binance/CoinGecko every 15 minutes
- **Process**: `apps.signals.tasks.generate_signals_for_all_symbols` (every 15 minutes)
- **Price Source**: `get_live_prices()` from `apps.data.real_price_service`
- **Limitations**: API rate limits, network dependency, inconsistent data availability

### Automated Database System (Already Implemented)
- **Data Storage**: Every hour at minute 0 (`update_historical_data_task`)
- **Backup**: Daily at 2:30 AM UTC (`update_historical_data_daily_task`)
- **Gap Check**: Weekly on Sunday at 3:00 AM UTC (`weekly_gap_check_and_fill_task`)
- **Coverage**: All crypto symbols with 1h timeframe data from 2020-present
- **Storage**: `MarketData` model with OHLCV data

---

## Phase Process Plan

### Phase 1: Database Signal Service Creation
**Objective**: Create a new service that uses database data instead of live API calls

#### 1.1 Create Database Signal Service
```python
# apps/signals/database_signal_service.py
class DatabaseSignalService:
    """Signal generation using automated database data instead of live APIs"""
    
    def __init__(self):
        self.lookback_hours = 24  # Use last 24 hours of data
        self.min_data_points = 20  # Minimum data points required
        
    def get_latest_market_data(self, symbol: Symbol) -> Optional[Dict]:
        """Get latest market data from database instead of live API"""
        # Query MarketData for latest records
        # Use 1h timeframe data stored by automated system
        
    def generate_signals_for_symbol(self, symbol: Symbol) -> List[TradingSignal]:
        """Generate signals using database data"""
        # Use historical data from MarketData table
        # Calculate technical indicators from stored OHLCV data
```

#### 1.2 Database Data Query Methods
```python
def get_recent_market_data(symbol: Symbol, hours_back: int = 24) -> QuerySet:
    """Get recent market data from database"""
    cutoff_time = timezone.now() - timedelta(hours=hours_back)
    return MarketData.objects.filter(
        symbol=symbol,
        timeframe='1h',
        timestamp__gte=cutoff_time
    ).order_by('timestamp')

def get_latest_price(symbol: Symbol) -> Optional[Decimal]:
    """Get latest price from database instead of live API"""
    latest_data = MarketData.objects.filter(
        symbol=symbol,
        timeframe='1h'
    ).order_by('-timestamp').first()
    
    return latest_data.close_price if latest_data else None
```

### Phase 2: Update Signal Generation Tasks
**Objective**: Modify existing Celery tasks to use database data

#### 2.1 Update Main Signal Generation Task
```python
# apps/signals/tasks.py - Modified version
@shared_task
def generate_signals_for_all_symbols():
    """Generate signals using database data instead of live APIs"""
    logger.info("Starting database-driven signal generation...")
    
    # Use DatabaseSignalService instead of SignalGenerationService
    signal_service = DatabaseSignalService()
    active_symbols = Symbol.objects.filter(is_active=True, is_crypto_symbol=True)
    
    total_signals = 0
    generated_signals = []
    
    for symbol in active_symbols:
        try:
            # Check if we have recent data (last 24 hours)
            recent_data = get_recent_market_data(symbol, hours_back=24)
            if recent_data.count() < 20:  # Need minimum data points
                logger.warning(f"Insufficient data for {symbol.symbol}: {recent_data.count()} points")
                continue
                
            signals = signal_service.generate_signals_for_symbol(symbol)
            generated_signals.extend(signals)
            total_signals += len(signals)
            
        except Exception as e:
            logger.error(f"Error generating signals for {symbol.symbol}: {e}")
    
    logger.info(f"Database signal generation completed. Total signals: {total_signals}")
    return {
        'total_signals': total_signals,
        'symbols_processed': active_symbols.count(),
        'signals_generated': len(generated_signals)
    }
```

#### 2.2 Create Database-Specific Tasks
```python
@shared_task
def generate_database_signals_task():
    """Dedicated task for database-driven signal generation"""
    try:
        service = DatabaseSignalService()
        result = service.generate_best_signals_for_all_coins()
        return result
    except Exception as e:
        logger.error(f"Database signal generation failed: {e}")
        return False

@shared_task
def validate_database_data_quality():
    """Validate database data quality before signal generation"""
    try:
        # Check data freshness (should be within last 2 hours)
        latest_data = MarketData.objects.order_by('-timestamp').first()
        if latest_data:
            data_age = timezone.now() - latest_data.timestamp
            if data_age > timedelta(hours=2):
                logger.warning(f"Database data is {data_age} old")
                return False
        
        # Check data completeness for active symbols
        active_symbols = Symbol.objects.filter(is_active=True, is_crypto_symbol=True)
        symbols_with_recent_data = 0
        
        for symbol in active_symbols:
            recent_data = get_recent_market_data(symbol, hours_back=24)
            if recent_data.count() >= 20:
                symbols_with_recent_data += 1
        
        completeness = symbols_with_recent_data / active_symbols.count()
        logger.info(f"Data completeness: {completeness:.1%} ({symbols_with_recent_data}/{active_symbols.count()})")
        
        return completeness >= 0.8  # Require 80% completeness
        
    except Exception as e:
        logger.error(f"Data quality validation failed: {e}")
        return False
```

### Phase 3: Update Celery Beat Schedule
**Objective**: Modify the automated schedule to use database-driven signals

#### 3.1 Update Celery Configuration
```python
# ai_trading_engine/celery.py - Updated beat schedule
beat_schedule={
    # Keep existing data collection tasks
    'historical-incremental-hourly': {
        'task': 'apps.data.tasks.update_historical_data_task',
        'schedule': crontab(minute=0),  # Every hour at minute 0
        'priority': 5,
    },
    
    # NEW: Database-driven signal generation (every 30 minutes)
    'generate-database-signals': {
        'task': 'apps.signals.tasks.generate_database_signals_task',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'priority': 8,
    },
    
    # NEW: Data quality validation (every 15 minutes)
    'validate-database-quality': {
        'task': 'apps.signals.tasks.validate_database_data_quality',
        'schedule': crontab(minute='*/15'),
        'priority': 6,
    },
    
    # DISABLE: Old live API signal generation
    # 'generate-trading-signals': {
    #     'task': 'apps.signals.tasks.generate_signals_for_all_symbols',
    #     'schedule': crontab(minute='*/15'),
    #     'priority': 8,
    # },
}
```

### Phase 4: Technical Indicator Calculation from Database
**Objective**: Calculate technical indicators using stored OHLCV data

#### 4.1 Database-Based Technical Analysis
```python
# apps/signals/database_technical_analysis.py
class DatabaseTechnicalAnalysis:
    """Calculate technical indicators from database data"""
    
    def calculate_indicators_from_database(self, symbol: Symbol, hours_back: int = 168):
        """Calculate indicators using database data (default: 1 week)"""
        market_data = get_recent_market_data(symbol, hours_back=hours_back)
        
        if market_data.count() < 20:
            return None
            
        # Convert to pandas DataFrame for calculations
        df = pd.DataFrame(list(market_data.values(
            'timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'
        )))
        
        # Calculate indicators
        indicators = self._calculate_all_indicators(df)
        return indicators
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate all technical indicators"""
        indicators = {}
        
        # Moving averages
        indicators['sma_20'] = df['close_price'].rolling(20).mean().iloc[-1]
        indicators['sma_50'] = df['close_price'].rolling(50).mean().iloc[-1]
        
        # RSI
        indicators['rsi'] = self._calculate_rsi(df['close_price'], 14)
        
        # MACD
        macd_line, signal_line, histogram = self._calculate_macd(df['close_price'])
        indicators['macd'] = macd_line.iloc[-1]
        indicators['macd_signal'] = signal_line.iloc[-1]
        indicators['macd_histogram'] = histogram.iloc[-1]
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(df['close_price'])
        indicators['bb_upper'] = bb_upper.iloc[-1]
        indicators['bb_middle'] = bb_middle.iloc[-1]
        indicators['bb_lower'] = bb_lower.iloc[-1]
        
        return indicators
```

### Phase 5: Signal Quality and Performance Monitoring
**Objective**: Monitor signal quality and system performance

#### 5.1 Database Signal Monitoring
```python
# apps/signals/database_signal_monitoring.py
class DatabaseSignalMonitor:
    """Monitor database-driven signal generation performance"""
    
    def monitor_signal_quality(self):
        """Monitor signal quality metrics"""
        # Check signal generation success rate
        recent_signals = TradingSignal.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1)
        )
        
        # Check data freshness
        latest_data = MarketData.objects.order_by('-timestamp').first()
        data_age = timezone.now() - latest_data.timestamp
        
        # Check signal accuracy (if we have performance data)
        performance_metrics = self._calculate_signal_performance()
        
        return {
            'signals_generated': recent_signals.count(),
            'data_age_hours': data_age.total_seconds() / 3600,
            'signal_accuracy': performance_metrics.get('accuracy', 0),
            'system_health': self._assess_system_health()
        }
    
    def _assess_system_health(self) -> str:
        """Assess overall system health"""
        # Check data completeness
        # Check signal generation frequency
        # Check error rates
        return "HEALTHY"  # or "DEGRADED" or "CRITICAL"
```

### Phase 6: Migration and Rollback Strategy
**Objective**: Ensure smooth transition with rollback capability

#### 6.1 Feature Flag Implementation
```python
# apps/signals/feature_flags.py
class SignalGenerationMode:
    LIVE_API = "live_api"
    DATABASE = "database"
    HYBRID = "hybrid"  # Use database with live API fallback

def get_signal_generation_mode() -> str:
    """Get current signal generation mode from settings"""
    from django.conf import settings
    return getattr(settings, 'SIGNAL_GENERATION_MODE', SignalGenerationMode.DATABASE)

def should_use_database_signals() -> bool:
    """Check if we should use database-driven signals"""
    mode = get_signal_generation_mode()
    return mode in [SignalGenerationMode.DATABASE, SignalGenerationMode.HYBRID]
```

#### 6.2 Hybrid Mode Implementation
```python
# apps/signals/hybrid_signal_service.py
class HybridSignalService:
    """Hybrid service that uses database data with live API fallback"""
    
    def generate_signals_for_symbol(self, symbol: Symbol) -> List[TradingSignal]:
        """Generate signals with database-first approach"""
        try:
            # Try database first
            if should_use_database_signals():
                return self._generate_from_database(symbol)
        except Exception as e:
            logger.warning(f"Database signal generation failed for {symbol.symbol}: {e}")
        
        # Fallback to live API
        logger.info(f"Falling back to live API for {symbol.symbol}")
        return self._generate_from_live_api(symbol)
```

### Phase 7: Performance Optimization
**Objective**: Optimize database queries and signal generation performance

#### 7.1 Database Query Optimization
```python
# Optimized database queries
def get_optimized_market_data(symbol: Symbol, hours_back: int = 24):
    """Optimized query for market data"""
    cutoff_time = timezone.now() - timedelta(hours=hours_back)
    return MarketData.objects.filter(
        symbol=symbol,
        timeframe='1h',
        timestamp__gte=cutoff_time
    ).select_related('symbol').only(
        'timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'
    ).order_by('timestamp')

# Use database indexes
class MarketData(models.Model):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['symbol', 'timestamp', 'timeframe']),
            models.Index(fields=['timestamp', 'timeframe']),
        ]
```

#### 7.2 Caching Strategy
```python
# apps/signals/database_signal_cache.py
from django.core.cache import cache

class DatabaseSignalCache:
    """Cache for database-driven signals"""
    
    def get_cached_market_data(self, symbol: Symbol, hours_back: int = 24):
        """Get cached market data"""
        cache_key = f"market_data_{symbol.symbol}_{hours_back}h"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Fetch from database
        data = get_optimized_market_data(symbol, hours_back)
        cache.set(cache_key, data, timeout=1800)  # 30 minutes
        return data
```

### Phase 8: Testing and Validation
**Objective**: Comprehensive testing of database-driven signal generation

#### 8.1 Unit Tests
```python
# tests/test_database_signal_generation.py
class TestDatabaseSignalGeneration:
    def test_database_signal_service(self):
        """Test database signal service"""
        service = DatabaseSignalService()
        symbol = Symbol.objects.get(symbol='BTC')
        
        signals = service.generate_signals_for_symbol(symbol)
        assert len(signals) > 0
        assert all(isinstance(s, TradingSignal) for s in signals)
    
    def test_data_quality_validation(self):
        """Test data quality validation"""
        result = validate_database_data_quality()
        assert result is True
    
    def test_signal_performance(self):
        """Test signal generation performance"""
        start_time = time.time()
        generate_database_signals_task()
        execution_time = time.time() - start_time
        
        assert execution_time < 300  # Should complete within 5 minutes
```

#### 8.2 Integration Tests
```python
def test_end_to_end_database_signals():
    """Test end-to-end database signal generation"""
    # 1. Ensure database has recent data
    # 2. Run signal generation task
    # 3. Verify signals are created
    # 4. Check signal quality metrics
    pass
```

### Phase 9: Deployment and Monitoring
**Objective**: Deploy and monitor the new system

#### 9.1 Deployment Steps
1. **Deploy Database Signal Service**
   - Deploy new `DatabaseSignalService`
   - Update Celery tasks
   - Update beat schedule

2. **Feature Flag Rollout**
   - Start with `HYBRID` mode
   - Monitor performance
   - Switch to `DATABASE` mode

3. **Monitoring Setup**
   - Set up alerts for data quality
   - Monitor signal generation frequency
   - Track system performance

#### 9.2 Monitoring Dashboard
```python
# apps/signals/monitoring_views.py
def database_signal_dashboard(request):
    """Dashboard for database signal monitoring"""
    context = {
        'data_quality': get_data_quality_metrics(),
        'signal_performance': get_signal_performance_metrics(),
        'system_health': get_system_health_status(),
        'recent_signals': get_recent_signals_summary(),
    }
    return render(request, 'signals/database_dashboard.html', context)
```

---

## Implementation Timeline

### Week 1: Foundation
- [ ] Create `DatabaseSignalService`
- [ ] Implement database data query methods
- [ ] Create unit tests

### Week 2: Integration
- [ ] Update Celery tasks
- [ ] Implement hybrid mode
- [ ] Create monitoring tools

### Week 3: Testing
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Data quality validation

### Week 4: Deployment
- [ ] Feature flag rollout
- [ ] Monitoring setup
- [ ] Performance monitoring

---

## Benefits of Database-Driven Signal Generation

### 1. **Reliability**
- No dependency on external API availability
- Consistent data access
- Reduced network failures

### 2. **Performance**
- Faster data access (local database)
- Reduced API rate limiting
- Better caching capabilities

### 3. **Cost Efficiency**
- Reduced API calls
- Lower bandwidth usage
- Better resource utilization

### 4. **Data Consistency**
- Historical data alignment
- Consistent timeframes
- Better backtesting accuracy

### 5. **Scalability**
- Handle more symbols efficiently
- Better resource management
- Improved system stability

---

## Risk Mitigation

### 1. **Data Quality Monitoring**
- Real-time data freshness checks
- Automated data quality alerts
- Fallback to live API if needed

### 2. **Performance Monitoring**
- Signal generation success rates
- System resource usage
- Response time tracking

### 3. **Rollback Strategy**
- Feature flags for easy rollback
- Hybrid mode for gradual transition
- Comprehensive logging and monitoring

---

## Success Metrics

### 1. **Technical Metrics**
- Signal generation success rate: >95%
- Data freshness: <2 hours old
- System uptime: >99%

### 2. **Performance Metrics**
- Signal generation time: <5 minutes
- Database query performance: <1 second
- Memory usage: <2GB

### 3. **Quality Metrics**
- Signal accuracy: >70%
- Data completeness: >90%
- Error rate: <1%

---

## Conclusion

This phase process provides a comprehensive roadmap for transitioning from live API-based signal generation to database-driven signal generation. The automated database system already stores data every hour, making this transition natural and beneficial for system reliability, performance, and scalability.

The implementation follows a phased approach with proper testing, monitoring, and rollback capabilities to ensure a smooth transition while maintaining system reliability and performance.
