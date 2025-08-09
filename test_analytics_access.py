#!/usr/bin/env python
"""
Test script to verify analytics dropdown functionality
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

def test_analytics_urls():
    """Test if analytics URLs are accessible"""
    client = Client()
    
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
    
    print("Testing Analytics URLs...")
    print("=" * 50)
    
    for url_name, description in analytics_urls:
        try:
            url = reverse(url_name)
            print(f"✓ {description}: {url}")
        except Exception as e:
            print(f"✗ {description}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("URL Testing Complete")

def test_navigation_template():
    """Test if the navigation template includes analytics dropdown"""
    try:
        from django.template.loader import get_template
        template = get_template('base.html')
        template_content = template.template.source
        
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
        
        print("\nTesting Navigation Template...")
        print("=" * 50)
        
        for element, description in checks:
            if element in template_content:
                print(f"✓ {description}: Found")
            else:
                print(f"✗ {description}: NOT FOUND")
        
        print("\n" + "=" * 50)
        print("Template Testing Complete")
        
    except Exception as e:
        print(f"✗ Template testing failed: {e}")

def test_analytics_views():
    """Test if analytics views are properly configured"""
    try:
        from apps.analytics import views
        
        view_functions = [
            ('analytics_dashboard', 'Analytics Dashboard View'),
            ('portfolio_view', 'Portfolio View'),
            ('performance_analytics', 'Performance Analytics View'),
            ('risk_management', 'Risk Management View'),
            ('market_analysis', 'Market Analysis View'),
            ('backtesting_view', 'Backtesting View'),
        ]
        
        print("\nTesting Analytics Views...")
        print("=" * 50)
        
        for view_name, description in view_functions:
            if hasattr(views, view_name):
                print(f"✓ {description}: Found")
            else:
                print(f"✗ {description}: NOT FOUND")
        
        print("\n" + "=" * 50)
        print("Views Testing Complete")
        
    except Exception as e:
        print(f"✗ Views testing failed: {e}")

if __name__ == "__main__":
    print("AI Trading Engine - Analytics Dropdown Test")
    print("=" * 60)
    
    test_analytics_urls()
    test_navigation_template()
    test_analytics_views()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("\nTo test the dropdown manually:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Open http://localhost:8000 in your browser")
    print("3. Look for the 'Analytics' dropdown in the navigation")
    print("4. Click on it to see if the dropdown menu appears")
    print("5. Try clicking on dropdown items to navigate")
