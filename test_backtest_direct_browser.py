#!/usr/bin/env python3
"""
Test backtesting page directly through browser to identify 500 error
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from playwright.sync_api import sync_playwright

def test_backtesting_direct():
    """Test backtesting page directly to identify errors"""
    print("Testing backtesting page directly...")
    
    # Create test user
    user = User.objects.create_user(
        username='direct_test_user',
        email='direct@test.com',
        password='testpass123'
    )
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Enable console logging
            page.on("console", lambda msg: print(f"Console: {msg.text}"))
            page.on("pageerror", lambda error: print(f"Page Error: {error}"))
            
            # Navigate to login page
            print("Navigating to login page...")
            page.goto("http://localhost:8000/login/")
            
            # Check if login page loads
            print(f"Login page title: {page.title()}")
            
            # Login
            print("Attempting login...")
            page.fill('input[name="username"]', 'direct_test_user')
            page.fill('input[name="password"]', 'testpass123')
            page.click('button[type="submit"]')
            
            # Wait for redirect
            page.wait_for_load_state('networkidle')
            print(f"After login, current URL: {page.url}")
            print(f"After login, page title: {page.title()}")
            
            # Navigate to backtesting page
            print("Navigating to backtesting page...")
            page.goto("http://localhost:8000/analytics/backtesting/")
            
            # Wait for page to load
            page.wait_for_load_state('networkidle')
            
            print(f"Backtesting page title: {page.title()}")
            print(f"Backtesting page URL: {page.url}")
            
            # Check for errors
            if "Server Error" in page.title():
                print("❌ Server Error detected!")
                # Get error details
                error_content = page.content()
                print(f"Error content: {error_content[:1000]}")
            else:
                print("✅ Backtesting page loaded successfully")
                
                # Check for key elements
                elements_to_check = [
                    ('h1', 'Page header'),
                    ('#symbol', 'Symbol dropdown'),
                    ('#start_date', 'Start date input'),
                    ('#end_date', 'End date input'),
                    ('#action', 'Action dropdown'),
                    ('#backtestForm', 'Form element')
                ]
                
                for selector, description in elements_to_check:
                    try:
                        element = page.locator(selector)
                        if element.is_visible():
                            print(f"✅ {description} found")
                        else:
                            print(f"❌ {description} not visible")
                    except Exception as e:
                        print(f"❌ {description} error: {e}")
            
            browser.close()
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        # Cleanup
        user.delete()

if __name__ == '__main__':
    test_backtesting_direct()
































































