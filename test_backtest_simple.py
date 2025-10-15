#!/usr/bin/env python3
"""
Simple test to create a user and test backtesting page
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import TestCase

class BacktestingPageTest(TestCase):
    def test_backtesting_page_works(self):
        """Test that backtesting page works"""
        # Create user
        user = User.objects.create_user(
            username='testuser4',
            email='test4@example.com',
            password='testpass123'
        )
        
        # Login
        self.client.login(username='testuser4', password='testpass123')
        
        # Test backtesting page
        response = self.client.get('/analytics/backtesting/')
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backtesting page loads successfully")
            
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
            print(f"❌ Backtesting page failed with status {response.status_code}")
            return False

if __name__ == '__main__':
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(BacktestingPageTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n🎉 Backtesting page test passed!")
    else:
        print("\n❌ Backtesting page test failed!")
































