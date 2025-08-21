import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

app = Celery('ai_trading_engine')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Phase 5: Enhanced Celery Configuration
app.conf.update(
    # Task prioritization and routing
    task_routes={
        'apps.trading.tasks.*': {'queue': 'trading', 'priority': 10},
        'apps.signals.tasks.*': {'queue': 'signals', 'priority': 8},
        'apps.sentiment.tasks.*': {'queue': 'sentiment', 'priority': 6},
        'apps.data.tasks.*': {'queue': 'data', 'priority': 4},
        'apps.analytics.tasks.*': {'queue': 'analytics', 'priority': 5},
    },
    
    # Task execution settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Performance optimization
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Task retry and failure handling
    task_annotations={
        '*': {
            'retry_backoff': True,
            'retry_backoff_max': 600,
            'max_retries': 3,
        }
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'update-crypto-prices': {
            'task': 'apps.data.tasks.update_crypto_prices',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
            'priority': 10,
        },
        'generate-trading-signals': {
            'task': 'apps.signals.tasks.generate_signals',
            'schedule': crontab(minute='*/15'),  # Every 15 minutes
            'priority': 8,
        },
        'update-sentiment-analysis': {
            'task': 'apps.sentiment.tasks.update_sentiment',
            'schedule': crontab(minute='*/10'),  # Every 10 minutes
            'priority': 6,
        },
        'cleanup-old-data': {
            'task': 'apps.data.tasks.cleanup_old_data',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
            'priority': 2,
        },
    },
    
    # Result backend configuration
    result_backend='django-db',
    result_expires=3600,  # 1 hour
    
    # Worker settings
    worker_max_tasks_per_child=1000,
    worker_max_memory_per_child=200000,  # 200MB
    
    # Monitoring and logging
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Phase 5: Task monitoring and health checks
@app.task(bind=True)
def health_check(self):
    """Health check task for monitoring Celery worker status"""
    return {
        'status': 'healthy',
        'worker_id': self.request.id,
        'timestamp': self.request.timestamp,
    }


@app.task(bind=True)
def performance_metrics(self):
    """Collect performance metrics for monitoring"""
    from django.core.cache import cache
    from django.db import connection
    
    # Database connection status
    db_status = 'healthy'
    try:
        connection.ensure_connection()
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    # Cache status
    cache_status = 'healthy'
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
    except Exception as e:
        cache_status = f'unhealthy: {str(e)}'
    
    return {
        'database': db_status,
        'cache': cache_status,
        'worker_id': self.request.id,
        'timestamp': self.request.timestamp,
    }
