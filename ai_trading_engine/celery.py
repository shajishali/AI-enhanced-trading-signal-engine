import os
from celery import Celery
from celery.schedules import crontab
from kombu import Queue
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
    
    # Queue definitions
    task_default_queue='default',
    task_queues=(
        Queue('default', routing_key='default'),
        Queue('data', routing_key='data'),
        Queue('signals', routing_key='signals'),
        Queue('sentiment', routing_key='sentiment'),
        Queue('trading', routing_key='trading'),
        Queue('analytics', routing_key='analytics'),
    ),
    
    # Task execution settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Broker connection settings
    broker_connection_retry_on_startup=True,  # Fix deprecation warning for Celery 6.0+
    
    # Performance optimization
    worker_prefetch_multiplier=1,  # Reduced to prevent memory issues
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Worker pool settings for better performance
    worker_pool='solo',  # Use solo pool for Windows compatibility
    worker_concurrency=1,  # Single thread per worker (divided workers handle concurrency)
    
    # Task retry and failure handling
    task_annotations={
        '*': {
            'retry_backoff': True,
            'retry_backoff_max': 600,
            'max_retries': 3,
        }
    },
    
    # Beat schedule for periodic tasks
    # Tasks are automatically routed to correct queues via task_routes
    beat_schedule={
        'update-crypto-prices': {
            'task': 'apps.data.tasks.update_crypto_prices',
            'schedule': crontab(minute='*/30'),  # Every 30 minutes
            'options': {'queue': 'data', 'priority': 10},  # Explicitly route to data queue
        },
        'generate-trading-signals': {
            'task': 'apps.signals.unified_signal_task.generate_unified_signals_task',
            'schedule': crontab(minute=49),  # Every hour at :49 minutes (18:49, 19:49, 20:49, etc.)
            'options': {'queue': 'signals', 'priority': 8},  # Explicitly route to signals queue
        },
        'update-sentiment-analysis': {
            'task': 'apps.sentiment.tasks.aggregate_sentiment_scores',
            'schedule': crontab(minute='*/10'),  # Every 10 minutes
            'options': {'queue': 'sentiment', 'priority': 6},  # Explicitly route to sentiment queue
        },
        'collect-news-data': {
            'task': 'apps.sentiment.tasks.collect_news_data',
            'schedule': crontab(minute='*/15'),  # Every 15 minutes
            'options': {'queue': 'sentiment', 'priority': 7},  # Explicitly route to sentiment queue
        },
        'collect-social-media-data': {
            'task': 'apps.sentiment.tasks.collect_social_media_data',
            'schedule': crontab(minute='*/20'),  # Every 20 minutes
            'options': {'queue': 'sentiment', 'priority': 6},  # Explicitly route to sentiment queue
        },
        'cleanup-old-data': {
            'task': 'apps.data.tasks.cleanup_old_data_task',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
            'options': {'queue': 'data', 'priority': 2},  # Explicitly route to data queue
        },
        # Historical data update tasks for backtesting database
        'historical-incremental-hourly': {
            'task': 'apps.data.tasks.update_historical_data_task',
            'schedule': crontab(minute=0),  # Every hour at minute 0
            'options': {'queue': 'data', 'priority': 5},  # Explicitly route to data queue
        },
        'historical-incremental-daily-backup': {
            'task': 'apps.data.tasks.update_historical_data_daily_task',
            'schedule': crontab(hour=2, minute=30),  # Daily at 2:30 AM UTC (backup)
            'options': {'queue': 'data', 'priority': 4},  # Explicitly route to data queue
        },
        'historical-weekly-gap-check': {
            'task': 'apps.data.tasks.weekly_gap_check_and_fill_task',
            'schedule': crontab(hour=3, minute=0, day_of_week='sun'),  # Weekly on Sunday at 3 AM UTC
            'options': {'queue': 'data', 'priority': 3},  # Explicitly route to data queue
        },
        # DISABLED: Monthly cleanup to preserve all historical data from 2020
        # 'historical-cleanup-monthly': {
        #     'task': 'apps.data.tasks.cleanup_old_data_task',
        #     'schedule': crontab(hour=4, minute=0, day_of_month='1'),  # Monthly on 1st at 4 AM UTC
        #     'priority': 1,
        # },
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
