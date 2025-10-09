#!/usr/bin/env python3
"""
Test the backtesting API endpoint directly to identify the exact error
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
import json

def test_backtesting_api_direct():
    """Test the backtesting API endpoint directly"""
    print("🔍 Testing Backtesting API Endpoint Directly")
    print("=" * 50)
    
    # Create test user
    user = User.objects.create_user(
        username='api_direct_user',
        email='api_direct@test.com',
        password='testpass123'
    )
    
    try:
        # Create test client
        client = Client()
        
        # Login
        login_success = client.login(username='api_direct_user', password='testpass123')
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
            'search_name': 'API Direct Test',
            'notes': 'Testing API directly'
        }
        
        print(f"API data: {api_data}")
        
        # Make API request
        response = client.post(
            '/signals/api/backtests/',
            data=json.dumps(api_data),
            content_type='application/json'
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API call successful!")
            print(f"Success: {data.get('success')}")
            print(f"Total signals: {data.get('total_signals')}")
            return True
        else:
            print(f"❌ API call failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        user.delete()

if __name__ == '__main__':
    test_backtesting_api_direct()




















