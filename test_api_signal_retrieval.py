#!/usr/bin/env python3
"""
Test to simulate the exact API call and see where signals are lost
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from apps.signals.views import BacktestAPIView
from datetime import datetime, timedelta
from django.utils import timezone
import json

def test_api_signal_retrieval():
    """Test the exact API call to see where signals are lost"""
    print("🔍 Testing API Signal Retrieval")
    print("=" * 50)
    
    # Create test user
    user = User.objects.create_user(
        username='api_signal_test_user',
        email='api_signal_test@test.com',
        password='testpass123'
    )
    
    try:
        # Create request factory
        factory = RequestFactory()
        
        # Use the exact same dates as the browser test
        start_date_str = '2025-08-02T00:00:00Z'
        end_date_str = '2025-09-01T23:59:59Z'
        
        print(f"Using API dates: {start_date_str} to {end_date_str}")
        
        # Prepare API data exactly like the browser test
        api_data = {
            'action': 'generate_signals',
            'symbol': 'XRP',
            'start_date': start_date_str,
            'end_date': end_date_str,
            'search_name': 'API Signal Test',
            'notes': 'Testing API signal retrieval'
        }
        
        print(f"API data: {api_data}")
        
        # Create request
        request = factory.post(
            '/signals/api/backtests/',
            data=json.dumps(api_data),
            content_type='application/json'
        )
        request.user = user
        
        # Create view instance
        view = BacktestAPIView()
        
        # Call the view method directly
        print("Calling BacktestAPIView.post()...")
        response = view.post(request)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse response content
            import json as json_lib
            response_data = json_lib.loads(response.content.decode())
            
            print(f"✅ API call successful!")
            print(f"Success: {response_data.get('success')}")
            print(f"Total signals: {response_data.get('total_signals')}")
            
            signals = response_data.get('signals', [])
            if signals:
                print(f"📊 Generated {len(signals)} signals:")
                for i, signal in enumerate(signals):
                    print(f"  Signal {i+1}: {signal.get('symbol')} - {signal.get('signal_type')}")
                    print(f"    Created: {signal.get('created_at')}")
                    print(f"    Strength: {signal.get('strength')}")
                    print(f"    Confidence: {signal.get('confidence_score')}")
                    print()
            else:
                print("⚠️  No signals in API response")
            
            return len(signals) > 0
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response content: {response.content.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        user.delete()

if __name__ == '__main__':
    test_api_signal_retrieval()





























































