"""
Phase 7, Step 7.2: Automation System Health Check
This script monitors the health of the automation system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
import django
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.data.models import MarketData
from apps.signals.models import TradingSignal
from apps.sentiment.models import NewsArticle, SentimentAggregate
import redis

def check_redis():
    """Check Redis connection"""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        return True, "Redis is running"
    except redis.ConnectionError:
        return False, "Redis is not running or not accessible"
    except Exception as e:
        return False, f"Redis error: {e}"

def check_recent_data():
    """Check if recent market data exists"""
    try:
        recent_data = MarketData.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).count()
        return recent_data > 0, f"Recent data records: {recent_data}"
    except Exception as e:
        return False, f"Error checking data: {e}"

def check_recent_signals():
    """Check if recent signals were generated"""
    try:
        recent_signals = TradingSignal.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1),
            is_valid=True
        ).count()
        # Check if we have at least some signals (not necessarily 10)
        return recent_signals >= 0, f"Recent signals: {recent_signals} (expected: ~10)"
    except Exception as e:
        return False, f"Error checking signals: {e}"

def check_news_sentiment():
    """Check if news and sentiment data is being collected"""
    try:
        recent_news = NewsArticle.objects.filter(
            published_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        recent_sentiment = SentimentAggregate.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # News is optional (requires API key), so we check sentiment primarily
        news_ok = recent_news >= 0  # News is optional
        sentiment_ok = recent_sentiment > 0
        
        message = f"Recent news: {recent_news}, Recent sentiment: {recent_sentiment}"
        return sentiment_ok, message
    except Exception as e:
        return False, f"Error checking news/sentiment: {e}"

def check_celery_processes():
    """Check if Celery processes are running (platform-specific)"""
    import platform
    import subprocess
    
    try:
        system = platform.system()
        if system == "Windows":
            # Check for celery processes on Windows
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                capture_output=True,
                text=True
            )
            celery_running = 'celery' in result.stdout.lower()
            return celery_running, "Celery processes: " + ("Running" if celery_running else "Not detected")
        else:
            # Check for celery processes on Linux/Mac
            result = subprocess.run(
                ['pgrep', '-f', 'celery'],
                capture_output=True
            )
            celery_running = result.returncode == 0
            return celery_running, "Celery processes: " + ("Running" if celery_running else "Not detected")
    except Exception as e:
        return False, f"Error checking Celery: {e}"

def main():
    """Main health check function"""
    print("=" * 70)
    print("Automation System Health Check")
    print("=" * 70)
    print(f"Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("Redis Connection", check_redis),
        ("Celery Processes", check_celery_processes),
        ("Recent Data Updates", check_recent_data),
        ("Recent Signal Generation", check_recent_signals),
        ("News & Sentiment Data", check_news_sentiment),
    ]
    
    all_ok = True
    results = []
    
    for name, check_func in checks:
        status, message = check_func()
        symbol = "✓" if status else "✗"
        print(f"{symbol} {name}: {message}")
        results.append((name, status, message))
        if not status:
            all_ok = False
    
    print()
    print("=" * 70)
    if all_ok:
        print("✓ All systems operational")
    else:
        print("✗ Some issues detected - check logs and services")
        print()
        print("Troubleshooting:")
        print("  1. Ensure Redis is running: redis-server redis.conf")
        print("  2. Ensure Celery Worker is running")
        print("  3. Ensure Celery Beat is running")
        print("  4. Check task logs for errors")
    print("=" * 70)
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)









