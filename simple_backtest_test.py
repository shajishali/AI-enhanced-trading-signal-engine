#!/usr/bin/env python3
"""
Simple test to check backtesting page functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_backtesting_page_simple():
    """Simple test of backtesting page"""
    print("Testing backtesting page...")
    
    # Create test client
    client = Client()
    
    # Create test user
    user = User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='testpass123'
    )
    
    # Login
    login_success = client.login(username='testuser2', password='testpass123')
    print(f"Login successful: {login_success}")
    
    if not login_success:
        print("❌ Failed to login")
        return False
    
    # Test backtesting page
    try:
        response = client.get('/analytics/backtesting/')
        print(f"Backtesting page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backtesting page loads successfully")
            
            # Check if the page contains expected elements
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
            print(f"❌ Backtesting page failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing backtesting page: {e}")
        return False
    
    finally:
        # Clean up
        user.delete()

if __name__ == '__main__':
    test_backtesting_page_simple()


























