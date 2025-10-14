#!/usr/bin/env python3
"""
Test the backtesting view to identify the 500 error
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from apps.analytics.views import backtesting_view
import traceback

def test_backtesting_view_error():
    """Test the backtesting view to identify the 500 error"""
    print("Testing backtesting view to identify 500 error...")
    
    # Create test user
    user = User.objects.create_user(
        username='error_test_user',
        email='error@test.com',
        password='testpass123'
    )
    
    try:
        # Create request factory
        factory = RequestFactory()
        
        # Create request
        request = factory.get('/analytics/backtesting/')
        request.user = user
        
        # Call the view directly and catch any exceptions
        try:
            response = backtesting_view(request)
            print(f"✅ View executed successfully - Status: {response.status_code}")
            return True
        except Exception as e:
            print(f"❌ View error: {e}")
            print(f"Error type: {type(e).__name__}")
            print(f"Traceback:")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Test setup error: {e}")
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        user.delete()

if __name__ == '__main__':
    test_backtesting_view_error()


























