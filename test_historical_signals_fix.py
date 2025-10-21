#!/usr/bin/env python3
"""
Test to verify that historical signals are now generated with proper timestamps
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from datetime import datetime, timedelta
from django.utils import timezone
import json

def test_historical_signals_fix():
    """Test that historical signals are now generated with proper timestamps"""
    print("🔍 Testing Historical Signals Fix")
    print("=" * 50)
    
    # Create test user
    user = User.objects.create_user(
        username='historical_test_user',
        email='historical_test@test.com',
        password='testpass123'
    )
    
    try:
        # Create test client
        client = Client()
        
        # Login
        login_success = client.login(username='historical_test_user', password='testpass123')
        print(f"Login successful: {login_success}")
        
        # Use actual past dates
        today = datetime.now()
        start_date = (today - timedelta(days=60)).strftime('%Y-%m-%d')
        end_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"Testing with past dates: {start_date} to {end_date}")
        
        # Prepare API data
        api_data = {
            'action': 'generate_signals',
            'symbol': 'XRP',
            'start_date': f'{start_date}T00:00:00Z',
            'end_date': f'{end_date}T23:59:59Z',
            'search_name': 'Historical Signals Test',
            'notes': 'Testing historical signals with proper timestamps'
        }
        
        print(f"API data: {api_data}")
        
        # Make HTTP request
        response = client.post(
            '/signals/api/backtests/',
            data=json.dumps(api_data),
            content_type='application/json'
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ HTTP request successful!")
            print(f"Success: {data.get('success')}")
            print(f"Total signals: {data.get('total_signals')}")
            
            signals = data.get('signals', [])
            if signals:
                print(f"📊 Generated {len(signals)} signals:")
                for i, signal in enumerate(signals[:3]):  # Show first 3 signals
                    print(f"  Signal {i+1}: {signal.get('symbol')} - {signal.get('signal_type')}")
                    print(f"    Created: {signal.get('created_at')}")
                    print(f"    Expires: {signal.get('expires_at')}")
                    print(f"    Strength: {signal.get('strength')}")
                    print(f"    Confidence: {signal.get('confidence_score')}")
                    print()
            else:
                print("⚠️  No signals generated - this might indicate the fix didn't work")
            
            return True
        else:
            print(f"❌ HTTP request failed with status {response.status_code}")
            print(f"Response content: {response.content.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        user.delete()

if __name__ == '__main__':
    test_historical_signals_fix()











































