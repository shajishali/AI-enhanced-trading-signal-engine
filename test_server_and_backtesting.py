#!/usr/bin/env python3
"""
Simple test to check server status and backtesting functionality
"""

import requests
import time
from playwright.sync_api import sync_playwright

def check_server_status():
    """Check if Django server is running"""
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print(f"✅ Server is running - Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False
    except Exception as e:
        print(f"❌ Server check failed: {e}")
        return False

def test_backtesting_page():
    """Test backtesting page with Playwright"""
    print("🎭 Testing backtesting page with Playwright...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        try:
            # Navigate to login page
            print("🔐 Navigating to login page...")
            page.goto('http://127.0.0.1:8000/login/')
            page.wait_for_load_state('networkidle')
            
            # Login
            print("🔑 Logging in...")
            page.fill("input[name='username']", "admin")
            page.fill("input[name='password']", "admin123")
            page.click("button[type='submit']")
            page.wait_for_url("**/dashboard/", timeout=10000)
            print("✅ Login successful")
            
            # Navigate to backtesting
            print("🧭 Navigating to backtesting page...")
            page.goto('http://127.0.0.1:8000/analytics/backtesting/')
            page.wait_for_load_state('networkidle')
            print("✅ Backtesting page loaded")
            
            # Take screenshot
            page.screenshot(path="backtesting_page_test.png")
            print("📸 Screenshot saved: backtesting_page_test.png")
            
            # Check for key elements
            print("🔍 Checking page elements...")
            
            # Check for symbol selector
            symbol_selector = page.locator("select[name*='symbol'], #symbol-select, .symbol-selector")
            if symbol_selector.count() > 0:
                print("✅ Symbol selector found")
            else:
                print("❌ Symbol selector not found")
            
            # Check for run button
            run_button = page.locator("button:has-text('Run'), button:has-text('Start'), button:has-text('Backtest')")
            if run_button.count() > 0:
                print("✅ Run button found")
            else:
                print("❌ Run button not found")
            
            # Try to run a simple backtest
            print("🎲 Attempting to run a simple backtest...")
            
            # Select BTC if available
            try:
                if page.locator("select option[value='BTC']").count() > 0:
                    page.select_option("select", value="BTC")
                    print("✅ Selected BTC")
                else:
                    print("⚠️ BTC option not found, using first available option")
                    options = page.locator("select option").all()
                    if len(options) > 1:  # Skip first empty option
                        page.select_option("select", index=1)
                        print("✅ Selected first available symbol")
            except Exception as e:
                print(f"⚠️ Symbol selection failed: {e}")
            
            # Set date range
            try:
                start_date = page.locator("input[type='date']").first
                if start_date.is_visible():
                    start_date.fill("2025-09-01")
                    print("✅ Set start date")
            except Exception as e:
                print(f"⚠️ Date setting failed: {e}")
            
            # Click run button
            try:
                if run_button.count() > 0:
                    run_button.first.click()
                    print("✅ Clicked run button")
                    
                    # Wait for results
                    page.wait_for_timeout(5000)
                    page.wait_for_load_state('networkidle')
                    
                    # Check for results table
                    results_table = page.locator("table, .results-table, #signalsTable")
                    if results_table.count() > 0:
                        print("✅ Results table found")
                        
                        # Check for N/A values
                        page_text = page.content()
                        na_count = page_text.count('N/A')
                        print(f"📊 Found {na_count} N/A values on the page")
                        
                        if na_count == 0:
                            print("🎉 No N/A values found - Fix successful!")
                        else:
                            print(f"⚠️ Still found {na_count} N/A values")
                        
                        # Take screenshot of results
                        page.screenshot(path="backtesting_results_test.png")
                        print("📸 Results screenshot saved: backtesting_results_test.png")
                        
                    else:
                        print("❌ No results table found")
                        
            except Exception as e:
                print(f"❌ Backtest execution failed: {e}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            page.screenshot(path="backtesting_error_test.png")
            
        finally:
            context.close()
            browser.close()

def main():
    """Main test function"""
    print("🚀 Starting Server and Backtesting Test")
    print("=" * 50)
    
    # Check server status
    if not check_server_status():
        print("❌ Server is not running. Please start the Django server first.")
        return False
    
    # Test backtesting page
    test_backtesting_page()
    
    print("=" * 50)
    print("✅ Test completed")
    return True

if __name__ == "__main__":
    main()
