#!/usr/bin/env python3
"""
Comprehensive Database Cleanup Script
Removes ALL market data to start fresh
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.models import MarketData

def comprehensive_cleanup():
    """Remove ALL market data from the database"""
    print("Starting comprehensive database cleanup...")
    
    # Get total count before cleanup
    total_records = MarketData.objects.count()
    print(f"Total market data records before cleanup: {total_records:,}")
    
    if total_records == 0:
        print("No records to clean up")
        return True
    
    # Delete all market data records
    print("Deleting all market data records...")
    deleted_count, _ = MarketData.objects.all().delete()
    
    print(f"Deleted {deleted_count} market data records")
    
    # Verify cleanup
    remaining_records = MarketData.objects.count()
    print(f"Remaining market data records: {remaining_records}")
    
    if remaining_records == 0:
        print("✅ Comprehensive cleanup successful!")
        return True
    else:
        print("⚠️ Warning - some records still remain")
        return False

if __name__ == "__main__":
    print("=== COMPREHENSIVE DATABASE CLEANUP ===")
    print("This will remove ALL market data from the database")
    
    success = comprehensive_cleanup()
    
    if success:
        print("\n✅ Database is completely clean and ready for fresh data import")
        print("You can now run: python fetch_daily_crypto_data.py")
    else:
        print("\n❌ Cleanup failed - manual intervention may be required")












