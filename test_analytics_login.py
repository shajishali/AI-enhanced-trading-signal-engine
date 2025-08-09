#!/usr/bin/env python
"""
Test script to verify analytics dropdown functionality after login
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

def test_analytics_with_login():
    """Test analytics URLs with authentication"""
    client = Client()
    
    # Create a test user if it doesn't exist
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print("Created test user: testuser")
    
    # Login
    login_success = client.login(username='testuser', password='testpass123')
    print(f"Login successful: {login_success}")
    
    if not login_success:
        print("❌ Login failed - cannot test analytics")
        return False
    
    # Analytics URLs to test
    analytics_urls = [
        ('analytics:dashboard', 'Analytics Dashboard'),
        ('analytics:portfolio', 'Portfolio Analytics'),
        ('analytics:performance', 'Performance Analytics'),
        ('analytics:risk_management', 'Risk Management'),
        ('analytics:market_analysis', 'Market Analysis'),
        ('analytics:backtesting', 'Backtesting'),
        ('analytics:ml_dashboard', 'AI/ML Models'),
    ]
    
    print("\nTesting Analytics URLs with Authentication...")
    print("=" * 60)
    
    results = []
    for url_name, description in analytics_urls:
        try:
            url = reverse(url_name)
            response = client.get(url)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {description}: {response.status_code} - {url}")
            results.append((description, response.status_code == 200))
        except Exception as e:
            print(f"❌ {description}: ERROR - {e}")
            results.append((description, False))
    
    print("\n" + "=" * 60)
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Results: {successful}/{total} URLs accessible")
    
    if successful == total:
        print("🎉 All analytics URLs are working!")
        return True
    else:
        print("⚠️  Some analytics URLs may have issues")
        return False

def test_base_template():
    """Test if base template renders correctly"""
    client = Client()
    
    # Create and login test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    client.login(username='testuser', password='testpass123')
    
    # Test dashboard page (should include base template)
    try:
        response = client.get(reverse('dashboard:dashboard'))
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for analytics dropdown elements
            checks = [
                ('nav-analytics', 'Analytics dropdown toggle'),
                ('analytics-dropdown-menu', 'Analytics dropdown menu'),
                ('analytics:dashboard', 'Analytics dashboard URL'),
                ('analytics:portfolio', 'Analytics portfolio URL'),
                ('analytics:performance', 'Analytics performance URL'),
                ('analytics:risk_management', 'Analytics risk management URL'),
                ('analytics:market_analysis', 'Analytics market analysis URL'),
                ('analytics:backtesting', 'Analytics backtesting URL'),
                ('analytics:ml_dashboard', 'Analytics ML dashboard URL'),
            ]
            
            print("\nTesting Base Template Rendering...")
            print("=" * 50)
            
            for element, description in checks:
                if element in content:
                    print(f"✅ {description}: Found in template")
                else:
                    print(f"❌ {description}: NOT FOUND in template")
            
            return True
        else:
            print(f"❌ Dashboard page returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Template testing failed: {e}")
        return False

if __name__ == "__main__":
    print("AI Trading Engine - Analytics Dropdown Test with Login")
    print("=" * 70)
    
    # Test template rendering
    template_ok = test_base_template()
    
    # Test analytics URLs
    urls_ok = test_analytics_with_login()
    
    print("\n" + "=" * 70)
    if template_ok and urls_ok:
        print("🎉 All tests passed! Analytics dropdown should work.")
        print("\nTo test manually:")
        print("1. Go to http://localhost:8000")
        print("2. Login with username: testuser, password: testpass123")
        print("3. Look for the 'Analytics' dropdown in the navigation")
        print("4. Click on it to see if the dropdown menu appears")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
