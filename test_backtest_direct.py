#!/usr/bin/env python3
"""
Test backtesting page by simulating browser access
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

def test_backtesting_view_direct():
    """Test the backtesting view directly"""
    print("Testing backtesting view directly...")
    
    # Create test user
    user = User.objects.create_user(
        username='testuser3',
        email='test3@example.com',
        password='testpass123'
    )
    
    try:
        # Create request factory
        factory = RequestFactory()
        
        # Create request
        request = factory.get('/analytics/backtesting/')
        request.user = user
        
        # Call the view directly
        response = backtesting_view(request)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backtesting view works directly")
            
            # Check content
            content = response.content.decode('utf-8')
            
            # Check for key elements
            checks = [
                ('Enhanced Backtesting', 'Page title'),
                ('symbol', 'Symbol dropdown'),
                ('start_date', 'Start date input'),
                ('end_date', 'End date input'),
                ('action', 'Action dropdown'),
                ('backtestForm', 'Form element'),
                ('loadSymbols', 'JavaScript function'),
                ('handleFormSubmit', 'Form submission handler')
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} missing")
            
            return True
        else:
            print(f"❌ Backtesting view failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing backtesting view: {e}")
        return False
    
    finally:
        # Clean up
        user.delete()

if __name__ == '__main__':
    test_backtesting_view_direct()




















