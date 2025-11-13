"""
Check what beat schedule Celery Beat is actually using
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

from celery import current_app

print("="*60)
print("CELERY BEAT SCHEDULE ANALYSIS")
print("="*60)

# Get beat schedule from current app
beat_schedule = current_app.conf.beat_schedule

print(f"\nTotal Scheduled Tasks: {len(beat_schedule)}")
print("\nCurrent Beat Schedule:")
for name, config in beat_schedule.items():
    schedule = config.get('schedule', 'N/A')
    task = config.get('task', 'N/A')
    print(f"\n  Task: {name}")
    print(f"    Function: {task}")
    print(f"    Schedule: {schedule}")

# Check what's in celery.py
print("\n" + "="*60)
print("EXPECTED SCHEDULE (from celery.py):")
print("="*60)
print("""
Expected tasks:
  1. update-crypto-prices - Every 30 minutes
  2. generate-trading-signals - Every 30 minutes  
  3. update-sentiment-analysis - Every 10 minutes
  4. cleanup-old-data - Daily at 2 AM
  5. historical-incremental-hourly - Every hour
  6. historical-incremental-daily-backup - Daily at 2:30 AM
  7. historical-weekly-gap-check - Weekly on Sunday
""")

if len(beat_schedule) < 5:
    print("\n⚠️  WARNING: Beat schedule is incomplete!")
    print("   Celery Beat is reading from settings.py instead of celery.py")
    print("   This will be fixed in Phase 2")
else:
    print("\n✓ Beat schedule looks complete")


