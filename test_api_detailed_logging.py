#!/usr/bin/env python3
"""
Test to capture the exact datetime comparison error with detailed logging
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

def test_api_with_detailed_logging():
    """Test the API with detailed logging to capture exact error"""
    print("🔍 Testing API with Detailed Logging")
    print("=" * 50)
    
    # Create test user
    user = User.objects.create_user(
        username='api_logging_user',
        email='api_logging@test.com',
        password='testpass123'
    )
    
    try:
        # Create request factory
        factory = RequestFactory()
        
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
            'search_name': 'API Logging Test',
            'notes': 'Testing API with detailed logging'
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
        print(f"Response content: {response.content.decode()}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        user.delete()

if __name__ == '__main__':
    test_api_with_detailed_logging()
