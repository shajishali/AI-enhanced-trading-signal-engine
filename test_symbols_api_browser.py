#!/usr/bin/env python3
"""
Test the symbols API through browser to see if it's working
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from playwright.sync_api import sync_playwright
import json

def test_symbols_api_browser():
    """Test the symbols API through browser"""
    print("Testing symbols API through browser...")
    
    # Create test user
    user = User.objects.create_user(
        username='browser_api_user',
        email='browser@test.com',
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
            
            # Login
            page.goto("http://localhost:8000/login/")
            page.fill('input[name="username"]', 'browser_api_user')
            page.fill('input[name="password"]', 'testpass123')
            page.click('button[type="submit"]')
            page.wait_for_load_state('networkidle')
            
            # Navigate to backtesting page
            page.goto("http://localhost:8000/analytics/backtesting/")
            page.wait_for_load_state('networkidle')
            
            # Wait for JavaScript to load
            page.wait_for_timeout(3000)
            
            # Check the symbol dropdown
            symbol_select = page.locator('#symbol')
            options = symbol_select.locator('option')
            
            print(f"Number of options found: {options.count()}")
            
            # Get all option values
            option_values = []
            for i in range(options.count()):
                option = options.nth(i)
                value = option.get_attribute('value')
                text = option.text_content()
                option_values.append({'value': value, 'text': text})
                print(f"Option {i}: value='{value}', text='{text}'")
            
            # Check if XRP is in the options
            xrp_options = [opt for opt in option_values if 'XRP' in opt['value'] or 'XRP' in opt['text']]
            if xrp_options:
                print(f"✅ XRP found in options: {xrp_options}")
            else:
                print("❌ XRP not found in options")
            
            # Check if the dropdown is populated (not just "Loading symbols...")
            loading_text = [opt for opt in option_values if 'Loading' in opt['text']]
            if loading_text:
                print("⚠️ Dropdown still shows 'Loading symbols...'")
            else:
                print("✅ Dropdown appears to be populated")
            
            browser.close()
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        user.delete()

if __name__ == '__main__':
    test_symbols_api_browser()
































