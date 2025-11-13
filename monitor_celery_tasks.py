"""
Phase 6, Step 6.2: Monitor Celery Task Execution
This script checks task results in the database to monitor Celery task execution.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from django_celery_results.models import TaskResult

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def check_recent_tasks(hours=1):
    """Check recent task execution"""
    print_section(f"Recent Task Execution (Last {hours} hour(s))")
    
    try:
        cutoff_time = timezone.now() - timedelta(hours=hours)
        recent_tasks = TaskResult.objects.filter(
            date_created__gte=cutoff_time
        ).order_by('-date_created')
        
        task_count = recent_tasks.count()
        print(f"Total tasks executed: {task_count}")
        
        if task_count == 0:
            print("\n⚠ No tasks found in the specified time period.")
            print("This may mean:")
            print("  - Celery Beat is not running")
            print("  - Tasks haven't been scheduled yet")
            print("  - Task results are not being saved to database")
            return
        
        # Group by status
        status_counts = {}
        task_groups = {}
        
        for task in recent_tasks:
            status = task.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            task_name = task.task_name
            if task_name not in task_groups:
                task_groups[task_name] = []
            task_groups[task_name].append(task)
        
        # Print status summary
        print("\nTask Status Summary:")
        print("-" * 70)
        for status, count in sorted(status_counts.items()):
            status_icon = "✓" if status == "SUCCESS" else "✗" if status == "FAILURE" else "⏳"
            print(f"{status_icon} {status:10s}: {count:4d} tasks")
        
        # Print task details
        print("\nTask Details:")
        print("-" * 70)
        for task_name, tasks in sorted(task_groups.items()):
            print(f"\n{task_name}:")
            for task in tasks[:5]:  # Show last 5 executions per task
                status_icon = "✓" if task.status == "SUCCESS" else "✗" if task.status == "FAILURE" else "⏳"
                print(f"  {status_icon} {task.status:10s} - {task.date_created.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if task.status == "FAILURE" and task.traceback:
                    # Show first few lines of error
                    error_lines = task.traceback.split('\n')[:3]
                    for line in error_lines:
                        if line.strip():
                            print(f"    Error: {line.strip()[:100]}")
                            break
        
        # Show failed tasks in detail
        failed_tasks = recent_tasks.filter(status='FAILURE')
        if failed_tasks.exists():
            print_section("Failed Tasks Details")
            for task in failed_tasks[:5]:  # Show first 5 failures
                print(f"\nTask: {task.task_name}")
                print(f"Date: {task.date_created}")
                print(f"Error:")
                if task.traceback:
                    # Print first 10 lines of traceback
                    lines = task.traceback.split('\n')[:10]
                    for line in lines:
                        print(f"  {line}")
                print("-" * 70)
        
    except Exception as e:
        print(f"✗ Error checking tasks: {e}")
        import traceback
        traceback.print_exc()

def check_specific_tasks():
    """Check specific automation tasks"""
    print_section("Automation Tasks Status")
    
    task_names = [
        'apps.data.tasks.update_crypto_prices',
        'apps.sentiment.tasks.collect_news_data',
        'apps.sentiment.tasks.aggregate_sentiment_scores',
        'apps.signals.unified_signal_task.generate_unified_signals_task',
    ]
    
    try:
        cutoff_time = timezone.now() - timedelta(hours=24)
        
        for task_name in task_names:
            tasks = TaskResult.objects.filter(
                task_name=task_name,
                date_created__gte=cutoff_time
            ).order_by('-date_created')
            
            if tasks.exists():
                latest = tasks.first()
                success_count = tasks.filter(status='SUCCESS').count()
                failure_count = tasks.filter(status='FAILURE').count()
                total_count = tasks.count()
                
                status_icon = "✓" if latest.status == "SUCCESS" else "✗" if latest.status == "FAILURE" else "⏳"
                
                print(f"\n{status_icon} {task_name.split('.')[-1]}:")
                print(f"   Latest: {latest.status} at {latest.date_created.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Last 24h: {success_count} success, {failure_count} failed, {total_count} total")
            else:
                print(f"\n⚠ {task_name.split('.')[-1]}: No executions found in last 24 hours")
                
    except Exception as e:
        print(f"✗ Error checking specific tasks: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main monitoring function"""
    print("\n" + "=" * 70)
    print("PHASE 6: CELERY TASK MONITORING")
    print("=" * 70)
    print("\nThis script monitors Celery task execution from the database.")
    
    # Check recent tasks (last hour)
    check_recent_tasks(hours=1)
    
    # Check specific automation tasks (last 24 hours)
    check_specific_tasks()
    
    print("\n" + "=" * 70)
    print("Monitoring complete. Check the output above for task status.")
    print("=" * 70)
    print("\nNote: If no tasks are found, ensure:")
    print("  1. Celery Beat is running")
    print("  2. Celery Worker is running")
    print("  3. Redis is running")
    print("  4. Tasks are scheduled in celery.py")
    print("=" * 70)

if __name__ == "__main__":
    main()









