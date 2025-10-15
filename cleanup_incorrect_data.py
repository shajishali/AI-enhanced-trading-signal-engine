#!/usr/bin/env python3
"""
Database Cleanup Script
Removes incorrect historical data and prepares for fresh data import
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.models import MarketData
from apps.trading.models import Symbol

def cleanup_incorrect_data():
    """Remove incorrect historical data"""
    print("Starting database cleanup...")
    
    # Get all USDT symbols
    usdt_symbols = Symbol.objects.filter(symbol__endswith='USDT').exclude(symbol='USDT')
    
    total_deleted = 0
    
    for symbol in usdt_symbols:
        print(f"Cleaning data for {symbol.symbol}...")
        
        # Delete all existing market data for this symbol
        deleted_count = MarketData.objects.filter(symbol=symbol).count()
        MarketData.objects.filter(symbol=symbol).delete()
        
        print(f"  Deleted {deleted_count} records for {symbol.symbol}")
        total_deleted += deleted_count
    
    print(f"Cleanup completed. Total records deleted: {total_deleted}")
    return total_deleted

def verify_cleanup():
    """Verify that cleanup was successful"""
    print("\nVerifying cleanup...")
    
    remaining_records = MarketData.objects.count()
    print(f"Remaining market data records: {remaining_records}")
    
    if remaining_records == 0:
        print("✓ Cleanup successful - all market data removed")
    else:
        print("⚠ Warning - some records still remain")
    
    return remaining_records == 0

if __name__ == "__main__":
    print("=== DATABASE CLEANUP SCRIPT ===")
    print("This will remove all existing market data for USDT pairs")
    
    confirm = input("Are you sure you want to proceed? (yes/no): ")
    
    if confirm.lower() == 'yes':
        deleted_count = cleanup_incorrect_data()
        success = verify_cleanup()
        
        if success:
            print("\n✓ Database is ready for fresh data import")
            print("You can now run: python fetch_daily_crypto_data.py")
        else:
            print("\n⚠ Cleanup may not have completed successfully")
    else:
        print("Cleanup cancelled")
