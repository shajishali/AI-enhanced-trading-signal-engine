"""
Phase 3: Test Data Update Task
This script tests the update_crypto_prices task to ensure it works correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.data.tasks import update_crypto_prices
from apps.data.models import MarketData, DataSyncLog
from apps.trading.models import Symbol

print("="*60)
print("PHASE 3: TESTING DATA UPDATE TASK")
print("="*60)

# Check current data status
print("\n1. CURRENT DATA STATUS")
print("-" * 60)

latest_data = MarketData.objects.order_by('-timestamp').first()
if latest_data:
    data_age = timezone.now() - latest_data.timestamp
    hours_old = data_age.total_seconds() / 3600
    print(f"Latest data: {latest_data.timestamp}")
    print(f"Age: {hours_old:.1f} hours old")
else:
    print("No market data found in database")

# Count active symbols
active_symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True)
print(f"Active crypto symbols: {active_symbols.count()}")

# Count recent data
one_hour_ago = timezone.now() - timedelta(hours=1)
recent_data = MarketData.objects.filter(timestamp__gte=one_hour_ago).count()
print(f"Recent data (last hour): {recent_data} records")

# Test the task
print("\n2. TESTING UPDATE_CRYPTO_PRICES TASK")
print("-" * 60)
print("Running task...")

try:
    result = update_crypto_prices()
    print(f"Task result: {result}")
    
    if result:
        print("✓ Task completed successfully")
        
        # Check for new data
        new_latest = MarketData.objects.order_by('-timestamp').first()
        if new_latest:
            new_data_age = timezone.now() - new_latest.timestamp
            new_hours_old = new_data_age.total_seconds() / 3600
            print(f"\nNew latest data: {new_latest.timestamp}")
            print(f"Age: {new_hours_old:.1f} hours old")
            
            if new_hours_old < 1:
                print("✓ Fresh data was added")
            else:
                print("⚠ Data is still old - task may not have fetched new data")
        
        # Check recent data count
        new_recent = MarketData.objects.filter(timestamp__gte=one_hour_ago).count()
        print(f"Recent data after task: {new_recent} records")
        
        if new_recent > recent_data:
            print(f"✓ Added {new_recent - recent_data} new records")
        else:
            print("⚠ No new records added")
            
    else:
        print("✗ Task returned False - may have failed")
        
except Exception as e:
    print(f"✗ Task failed with error: {e}")
    import traceback
    traceback.print_exc()

# Check sync logs
print("\n3. DATA SYNC LOGS")
print("-" * 60)
recent_logs = DataSyncLog.objects.order_by('-started_at')[:5]
if recent_logs:
    for log in recent_logs:
        print(f"{log.start_time}: {log.sync_type} - {log.status} ({log.records_processed} records)")
else:
    print("No recent sync logs found")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)

