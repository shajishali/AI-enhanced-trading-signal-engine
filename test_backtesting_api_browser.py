#!/usr/bin/env python3
"""
Test the backtesting API endpoint through browser to bypass ALLOWED_HOSTS issue
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import json

def test_backtesting_api_browser():
    """Test the backtesting API endpoint through browser"""
    print("🔍 Testing Backtesting API Endpoint Through Browser")
    print("=" * 60)
    
    # Create test user
    user = User.objects.create_user(
        username='api_browser_user',
        email='api_browser@test.com',
        password='testpass123'
    )
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Enable logging
            page.on("console", lambda msg: print(f"📝 Console: {msg.text}"))
            page.on("pageerror", lambda error: print(f"❌ Page Error: {error}"))
            page.on("requestfailed", lambda request: print(f"🌐 Request Failed: {request.url} - {request.failure}"))
            
            # Login
            print("1️⃣ Logging in...")
            page.goto("http://localhost:8000/login/")
            page.fill('input[name="username"]', 'api_browser_user')
            page.fill('input[name="password"]', 'testpass123')
            page.click('button[type="submit"]')
            page.wait_for_load_state('networkidle')
            print("✅ Login successful")
            
            # Use actual past dates
            today = datetime.now()
            start_date = (today - timedelta(days=60)).strftime('%Y-%m-%d')
            end_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
            
            print(f"2️⃣ Testing with past dates: {start_date} to {end_date}")
            
            # Prepare API data
            api_data = {
                'action': 'generate_signals',
                'symbol': 'XRP',
                'start_date': f'{start_date}T00:00:00Z',
                'end_date': f'{end_date}T23:59:59Z',
                'search_name': 'API Browser Test',
                'notes': 'Testing API through browser'
            }
            
            print(f"API data: {api_data}")
            
            # Make API request through browser
            response = page.request.post(
                'http://localhost:8000/signals/api/backtests/',
                data=api_data
            )
            
            print(f"Response status: {response.status}")
            print(f"Response headers: {response.headers}")
            
            try:
                response_data = response.json()
                print(f"Response data: {response_data}")
                
                if response.status == 200:
                    print(f"✅ API call successful!")
                    print(f"Success: {response_data.get('success')}")
                    print(f"Total signals: {response_data.get('total_signals')}")
                    return True
                else:
                    print(f"❌ API call failed with status {response.status}")
                    print(f"Error: {response_data.get('error')}")
                    return False
            except Exception as e:
                print(f"❌ Error parsing response: {e}")
                print(f"Raw response: {response.text()}")
                return False
            
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        user.delete()

if __name__ == '__main__':
    test_backtesting_api_browser()











































