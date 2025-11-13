"""
Phase 1: System Diagnosis & Verification
This script checks all components of the automation system
"""

import sys
import os
import subprocess
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

try:
    import django
    django.setup()
    
    from django.utils import timezone
    from django.db import connection
    from apps.data.models import MarketData, DataSyncLog
    from apps.trading.models import Symbol
    from apps.signals.models import TradingSignal
    from apps.sentiment.models import NewsArticle, SentimentAggregate
    from django_celery_results.models import TaskResult
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

def check_redis():
    """Step 1.1: Verify Redis is Running"""
    print("\n" + "="*60)
    print("STEP 1.1: VERIFYING REDIS IS RUNNING")
    print("="*60)
    
    try:
        import redis
        r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True, socket_connect_timeout=2)
        result = r.ping()
        if result:
            print("✓ Redis Status: RUNNING")
            print(f"  Host: 127.0.0.1")
            print(f"  Port: 6379")
            
            # Get Redis info
            try:
                info = r.info('server')
                print(f"  Redis Version: {info.get('redis_version', 'Unknown')}")
            except:
                pass
            
            return True, "Redis is running"
        else:
            print("✗ Redis Status: NOT RESPONDING")
            return False, "Redis ping failed"
    except redis.ConnectionError:
        print("✗ Redis Status: NOT RUNNING")
        print("  Error: Cannot connect to Redis server")
        print("  Solution: Start Redis with 'redis-server.exe redis.conf'")
        return False, "Redis connection error"
    except ImportError:
        print("✗ Redis Status: PYTHON PACKAGE NOT INSTALLED")
        print("  Error: redis package not found")
        print("  Solution: Install with 'pip install redis'")
        return False, "Redis package not installed"
    except Exception as e:
        print(f"✗ Redis Status: ERROR - {e}")
        return False, str(e)

def check_celery_worker():
    """Step 1.2: Verify Celery Worker is Running"""
    print("\n" + "="*60)
    print("STEP 1.2: VERIFYING CELERY WORKER IS RUNNING")
    print("="*60)
    
    try:
        from celery import current_app
        from kombu import Connection
        
        # Try to connect to broker
        broker_url = current_app.conf.broker_url
        print(f"  Broker URL: {broker_url}")
        
        # Check if we can inspect workers
        try:
            inspect = current_app.control.inspect()
            active_workers = inspect.active()
            
            if active_workers:
                print("✓ Celery Worker Status: RUNNING")
                for worker_name, tasks in active_workers.items():
                    print(f"  Worker: {worker_name}")
                    print(f"  Active Tasks: {len(tasks)}")
                return True, "Celery worker is running"
            else:
                print("✗ Celery Worker Status: NOT RUNNING")
                print("  No active workers found")
                print("  Solution: Start worker with 'python -m celery -A ai_trading_engine worker --loglevel=info'")
                return False, "No active workers"
        except Exception as e:
            print("✗ Celery Worker Status: CANNOT CONNECT")
            print(f"  Error: {e}")
            print("  This might indicate:")
            print("    1. Worker is not running")
            print("    2. Redis broker is not accessible")
            print("    3. Network connectivity issues")
            return False, str(e)
            
    except Exception as e:
        print(f"✗ Celery Worker Status: ERROR - {e}")
        return False, str(e)

def check_celery_beat():
    """Step 1.3: Verify Celery Beat Scheduler is Running"""
    print("\n" + "="*60)
    print("STEP 1.3: VERIFYING CELERY BEAT SCHEDULER IS RUNNING")
    print("="*60)
    
    try:
        from celery import current_app
        
        # Check beat schedule
        beat_schedule = current_app.conf.beat_schedule
        print(f"  Scheduled Tasks: {len(beat_schedule) if beat_schedule else 0}")
        
        if beat_schedule:
            print("  Beat Schedule Tasks:")
            for task_name, task_config in list(beat_schedule.items())[:5]:
                print(f"    - {task_name}: {task_config.get('schedule', 'N/A')}")
            if len(beat_schedule) > 5:
                print(f"    ... and {len(beat_schedule) - 5} more")
        
        # Check if beat process is running (via process check)
        try:
            import psutil
            beat_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('celery' in str(cmd).lower() and 'beat' in str(cmd).lower() for cmd in cmdline):
                        beat_running = True
                        print(f"✓ Celery Beat Process: RUNNING (PID: {proc.info['pid']})")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not beat_running:
                print("✗ Celery Beat Process: NOT RUNNING")
                print("  Solution: Start beat with 'python -m celery -A ai_trading_engine beat --loglevel=info'")
                return False, "Beat process not running"
            else:
                return True, "Celery Beat is running"
        except ImportError:
            print("⚠ Celery Beat Process: CANNOT VERIFY (psutil not installed)")
            print("  Install psutil for process checking: pip install psutil")
            return None, "Cannot verify beat process"
        except Exception as e:
            print(f"⚠ Celery Beat Process: CHECK ERROR - {e}")
            return None, str(e)
            
    except Exception as e:
        print(f"✗ Celery Beat Status: ERROR - {e}")
        return False, str(e)

def check_database_connection():
    """Step 1.4: Verify Database Connection"""
    print("\n" + "="*60)
    print("STEP 1.4: VERIFYING DATABASE CONNECTION")
    print("="*60)
    
    try:
        # Test connection
        connection.ensure_connection()
        print("✓ Database Connection: CONNECTED")
        
        # Check recent market data
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_data = MarketData.objects.filter(
            timestamp__gte=one_hour_ago
        ).count()
        print(f"  Recent Market Data (last hour): {recent_data} records")
        
        # Check active symbols
        active_symbols = Symbol.objects.filter(
            is_active=True,
            is_crypto_symbol=True
        ).count()
        print(f"  Active Crypto Symbols: {active_symbols}")
        
        # Check total market data
        total_data = MarketData.objects.count()
        print(f"  Total Market Data Records: {total_data:,}")
        
        # Check latest data timestamp
        latest_data = MarketData.objects.order_by('-timestamp').first()
        if latest_data:
            data_age = timezone.now() - latest_data.timestamp
            hours_old = data_age.total_seconds() / 3600
            print(f"  Latest Data: {latest_data.timestamp} ({hours_old:.1f} hours ago)")
            
            if hours_old > 2:
                print("  ⚠ WARNING: Data is more than 2 hours old")
        else:
            print("  ⚠ WARNING: No market data found in database")
        
        return True, f"Database connected, {recent_data} recent records"
        
    except Exception as e:
        print(f"✗ Database Connection: ERROR - {e}")
        return False, str(e)

def check_recent_task_execution():
    """Step 1.5: Check Recent Task Execution"""
    print("\n" + "="*60)
    print("STEP 1.5: CHECKING RECENT TASK EXECUTION")
    print("="*60)
    
    try:
        two_hours_ago = timezone.now() - timedelta(hours=2)
        
        # Check recent task results
        recent_tasks = TaskResult.objects.filter(
            date_created__gte=two_hours_ago
        ).order_by('-date_created')
        
        total_recent = recent_tasks.count()
        print(f"  Recent Tasks (last 2 hours): {total_recent}")
        
        if total_recent > 0:
            # Count by status
            success_count = recent_tasks.filter(status='SUCCESS').count()
            failure_count = recent_tasks.filter(status='FAILURE').count()
            pending_count = recent_tasks.filter(status='PENDING').count()
            
            print(f"    - Success: {success_count}")
            print(f"    - Failure: {failure_count}")
            print(f"    - Pending: {pending_count}")
            
            # Show recent tasks
            print("\n  Recent Task Executions:")
            for task in recent_tasks[:10]:
                status_symbol = "✓" if task.status == "SUCCESS" else "✗" if task.status == "FAILURE" else "○"
                task_name = task.task_name.split('.')[-1] if task.task_name else "Unknown"
                print(f"    {status_symbol} {task_name}: {task.status} at {task.date_created}")
            
            # Check for data update tasks
            data_tasks = recent_tasks.filter(task_name__icontains='update_crypto_prices')
            print(f"\n  Data Update Tasks: {data_tasks.count()}")
            
            # Check for signal generation tasks
            signal_tasks = recent_tasks.filter(task_name__icontains='generate')
            print(f"  Signal Generation Tasks: {signal_tasks.count()}")
            
            if total_recent == 0:
                print("  ⚠ WARNING: No tasks executed in the last 2 hours")
                return False, "No recent task execution"
            else:
                return True, f"{total_recent} tasks executed"
        else:
            print("  ⚠ WARNING: No tasks found in the last 2 hours")
            print("  This indicates tasks may not be running automatically")
            return False, "No recent tasks"
            
    except Exception as e:
        print(f"✗ Task Execution Check: ERROR - {e}")
        print("  Note: django-celery-results may not be installed")
        return None, str(e)

def check_recent_signals():
    """Bonus: Check recent signal generation"""
    print("\n" + "="*60)
    print("BONUS: CHECKING RECENT SIGNAL GENERATION")
    print("="*60)
    
    try:
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        recent_signals = TradingSignal.objects.filter(
            created_at__gte=one_hour_ago,
            is_valid=True
        ).order_by('-confidence_score')
        
        signal_count = recent_signals.count()
        print(f"  Recent Valid Signals (last hour): {signal_count}")
        
        if signal_count > 0:
            print(f"  Top 5 Recent Signals:")
            for i, signal in enumerate(recent_signals[:5], 1):
                print(f"    {i}. {signal.symbol.symbol} - {signal.signal_type.name} - "
                      f"Confidence: {signal.confidence_score:.1%}")
            
            # Check if we have 10 signals
            if signal_count >= 10:
                print(f"  ✓ System generating {signal_count} signals (target: 10)")
            else:
                print(f"  ⚠ System generating {signal_count} signals (target: 10)")
        else:
            print("  ⚠ WARNING: No signals generated in the last hour")
        
        return signal_count
        
    except Exception as e:
        print(f"  Error checking signals: {e}")
        return 0

def main():
    """Run all Phase 1 diagnostic checks"""
    print("\n" + "="*60)
    print("PHASE 1: SYSTEM DIAGNOSIS & VERIFICATION")
    print("="*60)
    print(f"Diagnosis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run all checks
    results['redis'] = check_redis()
    results['celery_worker'] = check_celery_worker()
    results['celery_beat'] = check_celery_beat()
    results['database'] = check_database_connection()
    results['tasks'] = check_recent_task_execution()
    signal_count = check_recent_signals()
    
    # Summary
    print("\n" + "="*60)
    print("PHASE 1 DIAGNOSIS SUMMARY")
    print("="*60)
    
    all_ok = True
    for check_name, (status, message) in results.items():
        if status is False:
            all_ok = False
            symbol = "✗"
        elif status is None:
            symbol = "⚠"
        else:
            symbol = "✓"
        print(f"{symbol} {check_name.upper()}: {message}")
    
    print(f"\nRecent Signals Generated: {signal_count}")
    
    if all_ok:
        print("\n✓ All critical systems are operational")
    else:
        print("\n✗ Some issues detected - review the details above")
        print("\nRecommended Actions:")
        if not results['redis'][0]:
            print("  1. Start Redis: redis-server.exe redis.conf")
        if not results['celery_worker'][0]:
            print("  2. Start Celery Worker: python -m celery -A ai_trading_engine worker --loglevel=info")
        if not results['celery_beat'][0]:
            print("  3. Start Celery Beat: python -m celery -A ai_trading_engine beat --loglevel=info")
        if not results['tasks'][0]:
            print("  4. Verify tasks are scheduled in celery.py beat_schedule")
    
    print("="*60)
    
    return results

if __name__ == "__main__":
    main()


