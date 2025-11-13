# Celery Divided Workers Setup

## Overview

This setup divides Celery work into separate workers for better performance, isolation, and debugging.

## Why Divided Workers?

### Benefits:
1. **Reduced Memory Usage** - Each worker only loads tasks for its specific queue
2. **Better Isolation** - Issues in one worker don't affect others
3. **Improved Performance** - Tasks can run in parallel without blocking
4. **Easier Debugging** - Problems are isolated to specific workers
5. **Better Resource Management** - Can scale individual workers as needed

## Worker Configuration

### Queue Distribution:

| Worker | Queue | Tasks Handled |
|--------|-------|---------------|
| **Data Worker** | `data` | Market data updates, historical data sync, data cleanup |
| **Signals Worker** | `signals` | Signal generation, validation, monitoring |
| **Sentiment Worker** | `sentiment` | News collection, social media, sentiment analysis |
| **Trading Worker** | `trading` | Trade execution, order management |
| **Analytics Worker** | `analytics` | Analytics calculations, performance metrics |

## Startup Scripts

### Option 1: All Workers + Django (Recommended)
```batch
start_trading_engine_divided.bat
```
Starts all 5 workers + Celery Beat + Django Server (7 windows total)

### Option 2: Only Celery Workers
```batch
start_all_celery_workers.bat
```
Starts all 5 workers + Celery Beat (6 windows total)

### Option 3: Individual Workers
- `start_celery_data_worker.bat` - Data tasks only
- `start_celery_signals_worker.bat` - Signal tasks only
- `start_celery_sentiment_worker.bat` - Sentiment tasks only
- `start_celery_trading_worker.bat` - Trading tasks only
- `start_celery_analytics_worker.bat` - Analytics tasks only

## Stopping Workers

```batch
stop_all_celery_workers.bat
```
Stops all Celery workers (Django server not affected)

## Task Routing

Tasks are automatically routed to the correct queue based on their app:

```python
task_routes={
    'apps.trading.tasks.*': {'queue': 'trading', 'priority': 10},
    'apps.signals.tasks.*': {'queue': 'signals', 'priority': 8},
    'apps.sentiment.tasks.*': {'queue': 'sentiment', 'priority': 6},
    'apps.data.tasks.*': {'queue': 'data', 'priority': 4},
    'apps.analytics.tasks.*': {'queue': 'analytics', 'priority': 5},
}
```

## Monitoring

### Check Worker Status:
```bash
python -m celery -A ai_trading_engine inspect active
```

### Check Registered Tasks:
```bash
python -m celery -A ai_trading_engine inspect registered
```

### Check Worker Stats:
```bash
python -m celery -A ai_trading_engine inspect stats
```

## Troubleshooting

### Issue: Worker not starting
- Check Redis is running: `tasklist | findstr redis`
- Check for port conflicts
- Verify Python environment is activated

### Issue: Tasks not executing
- Verify worker is listening to correct queue
- Check Celery Beat is running
- Verify task routing configuration

### Issue: Memory issues
- Each worker uses less memory than single worker
- Monitor individual worker memory usage
- Restart specific worker if needed

## Performance Tips

1. **Start only needed workers** - If you don't use trading, don't start trading worker
2. **Monitor worker logs** - Each worker has its own log window
3. **Restart individual workers** - No need to restart all workers if one has issues
4. **Scale as needed** - Can start multiple workers for same queue if needed

## Migration from Single Worker

If you were using `start_trading_engine.bat` (single worker):
1. Stop the old single worker
2. Use `start_trading_engine_divided.bat` instead
3. All tasks will automatically route to correct workers

## Notes

- All workers use `--pool=solo` for Windows compatibility
- Each worker has a unique hostname for identification
- Celery Beat schedules tasks to appropriate queues
- Django server is independent and can run separately








