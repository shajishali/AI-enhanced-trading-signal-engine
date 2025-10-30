#!/usr/bin/env python3
"""
Test the datetime fix for the backtesting functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from apps.trading.models import Symbol
from apps.signals.services import HistoricalSignalService
from datetime import datetime
from django.utils import timezone

def test_datetime_fix():
    """Test that the datetime comparison error is fixed"""
    print("Testing datetime fix...")
    
    # Create test user
    user = User.objects.create_user(
        username='datetime_test_user',
        email='datetime@test.com',
        password='testpass123'
    )
    
    try:
        # Get XRP symbol
        symbol = Symbol.objects.get(symbol='XRP')
        
        # Create timezone-naive dates (like from frontend)
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)
        
        print(f"Testing with timezone-naive dates:")
        print(f"  Start date: {start_date} (tzinfo: {start_date.tzinfo})")
        print(f"  End date: {end_date} (tzinfo: {end_date.tzinfo})")
        
        # Test the HistoricalSignalService
        historical_service = HistoricalSignalService()
        
        # Test validate_date_range
        is_valid, error_msg = historical_service.validate_date_range(start_date, end_date)
        print(f"✅ validate_date_range result: {is_valid}, error: {error_msg}")
        
        # Test generate_signals_for_period
        signals = historical_service.generate_signals_for_period(symbol, start_date, end_date)
        print(f"✅ generate_signals_for_period result: {len(signals)} signals generated")
        
        print("✅ Datetime fix test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during datetime test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        user.delete()

if __name__ == '__main__':
    test_datetime_fix()






























































