#!/usr/bin/env python3
"""
Test the BacktestSearch creation to identify the 500 error
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from apps.trading.models import Symbol
from apps.signals.models import BacktestSearch
from datetime import datetime
from django.utils import timezone

def test_backtest_search_creation():
    """Test BacktestSearch creation to identify the 500 error"""
    print("Testing BacktestSearch creation...")
    
    # Create test user
    user = User.objects.create_user(
        username='backtest_search_user',
        email='backtest_search@test.com',
        password='testpass123'
    )
    
    try:
        # Get XRP symbol
        symbol = Symbol.objects.get(symbol='XRP')
        
        # Create timezone-aware dates (like from the API)
        start_date = datetime.fromisoformat('2025-09-01T00:00:00+00:00')
        end_date = datetime.fromisoformat('2025-10-01T23:59:59+00:00')
        
        print(f"Testing with timezone-aware dates:")
        print(f"  Start date: {start_date} (tzinfo: {start_date.tzinfo})")
        print(f"  End date: {end_date} (tzinfo: {end_date.tzinfo})")
        
        # Test the BacktestSearch creation
        search, created = BacktestSearch.objects.get_or_create(
            user=user,
            symbol=symbol,
            start_date=start_date.date(),
            end_date=end_date.date(),
            defaults={
                'signals_generated': 5,
                'search_name': 'Test Search',
                'notes': 'Test notes'
            }
        )
        
        print(f"✅ BacktestSearch creation successful: created={created}, id={search.id}")
        return True
        
    except Exception as e:
        print(f"❌ Error during BacktestSearch creation: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        user.delete()

if __name__ == '__main__':
    test_backtest_search_creation()






























































