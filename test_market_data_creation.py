#!/usr/bin/env python3
"""
Test the MarketData creation to identify the 500 error
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from apps.trading.models import Symbol
from apps.data.models import MarketData
from apps.signals.services import HistoricalSignalService
from datetime import datetime
from django.utils import timezone

def test_market_data_creation():
    """Test MarketData creation to identify the 500 error"""
    print("Testing MarketData creation...")
    
    # Create test user
    user = User.objects.create_user(
        username='market_data_user',
        email='market_data@test.com',
        password='testpass123'
    )
    
    try:
        # Get XRP symbol
        symbol = Symbol.objects.get(symbol='XRP')
        
        # Create timezone-aware dates
        start_date = datetime.fromisoformat('2024-09-01T00:00:00+00:00')
        end_date = datetime.fromisoformat('2024-09-02T00:00:00+00:00')
        
        print(f"Testing with symbol: {symbol.symbol}")
        print(f"Start date: {start_date}")
        print(f"End date: {end_date}")
        
        # Test the HistoricalSignalService
        historical_service = HistoricalSignalService()
        
        # Test _generate_synthetic_data directly
        print("Testing _generate_synthetic_data...")
        historical_service._generate_synthetic_data(symbol, start_date, end_date)
        print("✅ _generate_synthetic_data completed successfully")
        
        # Check if data was created
        data_count = MarketData.objects.filter(symbol=symbol).count()
        print(f"✅ Created {data_count} MarketData records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during MarketData creation: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        user.delete()

if __name__ == '__main__':
    test_market_data_creation()






























































