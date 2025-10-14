#!/usr/bin/env python3
"""
Simple test to check what's causing the 500 error
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import TestCase

class BacktestingErrorTest(TestCase):
    def test_backtesting_page_error(self):
        """Test what's causing the 500 error"""
        # Create user
        user = User.objects.create_user(
            username='testuser5',
            email='test5@example.com',
            password='testpass123'
        )
        
        # Login
        self.client.login(username='testuser5', password='testpass123')
        
        # Test backtesting page
        response = self.client.get('/analytics/backtesting/')
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 500:
            print("500 Error detected!")
            print(f"Response content: {response.content.decode('utf-8')[:500]}")
        else:
            print("✅ Page loads successfully")
            print(f"Response content length: {len(response.content)}")

if __name__ == '__main__':
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(BacktestingErrorTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


























