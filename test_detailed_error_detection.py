#!/usr/bin/env python3
"""
Comprehensive error detection test with detailed logging
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
import traceback

def test_detailed_error_detection():
    """Test with detailed error logging to identify exact source"""
    print("🔍 Detailed Error Detection Test")
    print("=" * 50)
    
    # Create test user
    user = User.objects.create_user(
        username='detailed_error_user',
        email='detailed_error@test.com',
        password='testpass123'
    )
    
    try:
        # Get XRP symbol
        symbol = Symbol.objects.get(symbol='XRP')
        
        # Use actual past dates
        today = datetime.now()
        start_date = (today - timezone.timedelta(days=60)).strftime('%Y-%m-%d')
        end_date = (today - timezone.timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"Testing with past dates: {start_date} to {end_date}")
        
        # Parse dates
        start_date_dt = datetime.fromisoformat(f'{start_date}T00:00:00+00:00')
        end_date_dt = datetime.fromisoformat(f'{end_date}T23:59:59+00:00')
        
        print(f"Parsed dates:")
        print(f"  Start: {start_date_dt} (tzinfo: {start_date_dt.tzinfo})")
        print(f"  End: {end_date_dt} (tzinfo: {end_date_dt.tzinfo})")
        
        # Test HistoricalSignalService step by step
        historical_service = HistoricalSignalService()
        
        print("\n1️⃣ Testing validate_date_range...")
        try:
            is_valid, error_msg = historical_service.validate_date_range(start_date_dt, end_date_dt)
            print(f"✅ validate_date_range: {is_valid}, error: {error_msg}")
        except Exception as e:
            print(f"❌ validate_date_range error: {e}")
            traceback.print_exc()
            return False
        
        print("\n2️⃣ Testing _get_historical_data...")
        try:
            historical_data = historical_service._get_historical_data(symbol, start_date_dt, end_date_dt)
            print(f"✅ _get_historical_data: {historical_data.count()} records")
        except Exception as e:
            print(f"❌ _get_historical_data error: {e}")
            traceback.print_exc()
            return False
        
        print("\n3️⃣ Testing _generate_synthetic_data...")
        try:
            historical_service._generate_synthetic_data(symbol, start_date_dt, end_date_dt)
            print("✅ _generate_synthetic_data completed")
        except Exception as e:
            print(f"❌ _generate_synthetic_data error: {e}")
            traceback.print_exc()
            return False
        
        print("\n4️⃣ Testing signal generation...")
        try:
            # Test the main signal service
            from apps.signals.services import SignalGenerationService
            signal_service = SignalGenerationService()
            
            print("4a. Testing generate_signals_for_symbol...")
            signals = signal_service.generate_signals_for_symbol(symbol)
            print(f"✅ generate_signals_for_symbol: {len(signals)} signals")
            
            # Check each signal for datetime issues
            for i, signal in enumerate(signals):
                print(f"  Signal {i+1}:")
                print(f"    ID: {signal.id}")
                print(f"    Created at: {signal.created_at} (tzinfo: {signal.created_at.tzinfo if signal.created_at else None})")
                print(f"    Expires at: {signal.expires_at} (tzinfo: {signal.expires_at.tzinfo if signal.expires_at else None})")
                
                # Test datetime comparisons
                try:
                    if signal.created_at and signal.expires_at:
                        is_expired = signal.created_at < signal.expires_at
                        print(f"    ✅ DateTime comparison works: {is_expired}")
                except Exception as e:
                    print(f"    ❌ DateTime comparison error: {e}")
                    traceback.print_exc()
                    return False
            
        except Exception as e:
            print(f"❌ Signal generation error: {e}")
            traceback.print_exc()
            return False
        
        print("\n5️⃣ Testing generate_signals_for_period...")
        try:
            period_signals = historical_service.generate_signals_for_period(symbol, start_date_dt, end_date_dt)
            print(f"✅ generate_signals_for_period: {len(period_signals)} signals")
        except Exception as e:
            print(f"❌ generate_signals_for_period error: {e}")
            traceback.print_exc()
            return False
        
        print("\n✅ All tests passed! No datetime comparison errors found.")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False
    finally:
        user.delete()

if __name__ == '__main__':
    test_detailed_error_detection()


























