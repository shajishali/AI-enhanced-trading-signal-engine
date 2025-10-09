#!/usr/bin/env python
"""
Test script for duplicate signal removal system

This script demonstrates how to use the duplicate signal removal system
and provides examples of common usage patterns.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

from apps.signals.duplicate_signal_removal_service import duplicate_removal_service
from apps.signals.models import TradingSignal, SignalType
from apps.trading.models import Symbol
from decimal import Decimal


def test_duplicate_detection():
    """Test duplicate detection functionality"""
    print("=== Testing Duplicate Detection ===")
    
    # Get statistics
    print("\n1. Getting current statistics...")
    stats = duplicate_removal_service.get_duplicate_statistics()
    
    if stats['success']:
        print(f"Total signals: {stats['total_signals']}")
        print(f"Total duplicates: {stats['total_duplicates']}")
        print(f"Duplicate percentage: {stats['duplicate_percentage']:.2f}%")
        print(f"Duplicate groups: {stats['duplicate_groups_count']}")
        
        if stats['symbols_with_duplicates']:
            print(f"Symbols with duplicates: {', '.join(stats['symbols_with_duplicates'])}")
    else:
        print(f"Error getting statistics: {stats['error']}")
    
    # Identify duplicates for a specific symbol
    print("\n2. Identifying duplicates for AAVEUSDT...")
    result = duplicate_removal_service.identify_duplicates(
        symbol='AAVEUSDT',
        tolerance_percentage=0.01
    )
    
    if result['success']:
        print(f"Signals analyzed: {result['total_signals_analyzed']}")
        print(f"Duplicate groups found: {result['duplicate_groups_found']}")
        print(f"Total duplicate signals: {result['total_duplicate_signals']}")
        
        # Show example duplicate groups
        if result['duplicate_groups']:
            print("\nExample duplicate groups:")
            for i, group in enumerate(result['duplicate_groups'][:3]):
                signal = group['signals'][0]
                print(f"  Group {i+1}: {signal.symbol.symbol} - {signal.signal_type.name}")
                print(f"    Entry: ${signal.entry_price}, Target: ${signal.target_price}")
                print(f"    Duplicates: {group['count']}")
                print(f"    Date range: {min(s.created_at for s in group['signals'])} to {max(s.created_at for s in group['signals'])}")
    else:
        print(f"Error identifying duplicates: {result['error']}")


def test_dry_run_removal():
    """Test dry run removal (safe preview)"""
    print("\n=== Testing Dry Run Removal ===")
    
    # Perform dry run removal
    result = duplicate_removal_service.remove_duplicates(
        symbol='AAVEUSDT',
        dry_run=True,
        tolerance_percentage=0.01
    )
    
    if result['success']:
        print(f"DRY RUN RESULTS:")
        print(f"  Signals that would be removed: {result['removed_count']}")
        print(f"  Signals that would be kept: {result['kept_count']}")
        print(f"  Total signals analyzed: {result.get('total_signals_analyzed', 'N/A')}")
        
        if result['removed_count'] > 0:
            print(f"\n  This is a preview. To actually remove duplicates, set dry_run=False")
        else:
            print(f"\n  No duplicates found to remove.")
    else:
        print(f"Error in dry run: {result['error']}")


def test_cleanup_old_duplicates():
    """Test cleanup of old duplicates"""
    print("\n=== Testing Cleanup of Old Duplicates ===")
    
    # Cleanup duplicates older than 30 days (dry run)
    result = duplicate_removal_service.cleanup_old_duplicates(
        days_old=30,
        dry_run=True
    )
    
    if result['success']:
        print(f"OLD DUPLICATES CLEANUP (DRY RUN):")
        print(f"  Duplicates older than 30 days that would be removed: {result['removed_count']}")
        print(f"  Signals that would be kept: {result['kept_count']}")
    else:
        print(f"Error in cleanup: {result['error']}")


def demonstrate_usage_patterns():
    """Demonstrate common usage patterns"""
    print("\n=== Common Usage Patterns ===")
    
    print("\n1. Check for duplicates before backtesting:")
    print("   python manage.py remove_duplicate_signals --statistics-only")
    
    print("\n2. Preview duplicates for specific symbol:")
    print("   python manage.py remove_duplicate_signals --symbol AAVEUSDT --dry-run")
    
    print("\n3. Remove duplicates with custom tolerance:")
    print("   python manage.py remove_duplicate_signals --tolerance 0.02 --dry-run")
    
    print("\n4. Cleanup old duplicates:")
    print("   python manage.py remove_duplicate_signals --cleanup-old --days-old 30 --dry-run")
    
    print("\n5. Remove duplicates for date range:")
    print("   python manage.py remove_duplicate_signals --start-date 2021-09-01 --end-date 2021-10-31 --dry-run")
    
    print("\n6. Actually remove duplicates (remove --dry-run):")
    print("   python manage.py remove_duplicate_signals --symbol AAVEUSDT")


def main():
    """Main test function"""
    print("Duplicate Signal Removal System - Test Script")
    print("=" * 50)
    
    try:
        # Test duplicate detection
        test_duplicate_detection()
        
        # Test dry run removal
        test_dry_run_removal()
        
        # Test cleanup of old duplicates
        test_cleanup_old_duplicates()
        
        # Show usage patterns
        demonstrate_usage_patterns()
        
        print("\n" + "=" * 50)
        print("Test completed successfully!")
        print("\nNext steps:")
        print("1. Visit /signals/duplicates/ in your browser for the web interface")
        print("2. Use the management command for command-line operations")
        print("3. Always use --dry-run first to preview changes")
        print("4. Check the README for detailed usage instructions")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
