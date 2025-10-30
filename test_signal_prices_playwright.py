#!/usr/bin/env python3
"""
Playwright Test for Signal Price Issue
Tests signal generation and verifies that Entry Price, Target Price, and Stop Loss are not N/A
"""

import os
import sys
import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, expect

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

class SignalPriceTest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {'passed': 0, 'failed': 0, 'total': 0}
        }
    
    def log_test_result(self, test_name, status, message="", screenshot_path=""):
        """Log test result"""
        result = {
            'test_name': test_name,
            'status': status,
            'message': message,
            'screenshot': screenshot_path,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results['tests'].append(result)
        self.test_results['summary']['total'] += 1
        if status == 'PASSED':
            self.test_results['summary']['passed'] += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.test_results['summary']['failed'] += 1
            print(f"❌ {test_name}: {message}")
    
    def login(self, page):
        """Login to the application"""
        print("🔐 Logging in...")
        
        try:
            page.goto(f"{self.base_url}/login/")
            page.wait_for_load_state('networkidle')
            
            # Fill login form
            page.fill("input[name='username']", "admin")
            page.fill("input[name='password']", "admin123")
            page.click("button[type='submit']")
            
            # Wait for redirect
            page.wait_for_url("**/dashboard/", timeout=10000)
            
            self.log_test_result("Login", "PASSED", "Successfully logged in")
            return True
            
        except Exception as e:
            self.log_test_result("Login", "FAILED", f"Login failed: {str(e)}")
            page.screenshot(path="test_login_failed.png")
            return False
    
    def test_signals_page_loads(self, page):
        """Test that signals page loads correctly"""
        print("📡 Testing signals page loads...")
        
        try:
            page.goto(f"{self.base_url}/signals/")
            page.wait_for_load_state('networkidle')
            
            # Check page title
            expect(page).to_have_title(lambda title: "Signal" in title or "Trading" in title)
            
            # Check for signals table
            signals_table = page.locator("table, .signals-table, #signals-tbody")
            expect(signals_table).to_be_visible(timeout=10000)
            
            self.log_test_result("Signals Page Load", "PASSED", "Signals page loaded successfully")
            return True
            
        except Exception as e:
            self.log_test_result("Signals Page Load", "FAILED", f"Failed to load signals page: {str(e)}")
            page.screenshot(path="test_signals_page_failed.png")
            return False
    
    def test_signal_generation(self, page):
        """Test signal generation functionality"""
        print("🔄 Testing signal generation...")
        
        try:
            page.goto(f"{self.base_url}/signals/")
            page.wait_for_load_state('networkidle')
            
            # Look for generate signals button
            generate_buttons = [
                "button:has-text('Generate')",
                "button:has-text('Refresh')",
                "button:has-text('Update')",
                ".btn:has-text('Generate')",
                ".btn:has-text('Refresh')"
            ]
            
            button_found = False
            for selector in generate_buttons:
                try:
                    if page.locator(selector).is_visible():
                        page.click(selector)
                        button_found = True
                        break
                except:
                    continue
            
            if button_found:
                # Wait for signals to load
                page.wait_for_timeout(3000)
                page.wait_for_load_state('networkidle')
                
                self.log_test_result("Signal Generation", "PASSED", "Signal generation triggered successfully")
                return True
            else:
                self.log_test_result("Signal Generation", "WARNING", "No generate button found, signals may auto-generate")
                return True
                
        except Exception as e:
            self.log_test_result("Signal Generation", "FAILED", f"Signal generation failed: {str(e)}")
            page.screenshot(path="test_signal_generation_failed.png")
            return False
    
    def test_signal_prices_not_na(self, page):
        """Test that signal prices are not N/A"""
        print("💰 Testing signal prices are not N/A...")
        
        try:
            page.goto(f"{self.base_url}/signals/")
            page.wait_for_load_state('networkidle')
            
            # Wait for signals to load
            page.wait_for_timeout(5000)
            
            # Look for signal rows
            signal_rows = page.locator("tr[data-signal-id], tbody tr, .signal-row")
            
            if signal_rows.count() == 0:
                self.log_test_result("Signal Prices Check", "WARNING", "No signals found to test")
                return True
            
            na_count = 0
            valid_price_count = 0
            total_signals = signal_rows.count()
            
            print(f"Found {total_signals} signals to check...")
            
            for i in range(min(total_signals, 10)):  # Check first 10 signals
                try:
                    row = signal_rows.nth(i)
                    
                    # Get all text content from the row
                    row_text = row.text_content()
                    
                    # Count N/A occurrences in price-related columns
                    na_in_row = row_text.count("N/A")
                    
                    # Look for price patterns ($X.XX)
                    import re
                    price_pattern = r'\$\d+\.?\d*'
                    prices_found = len(re.findall(price_pattern, row_text))
                    
                    if na_in_row > 0:
                        na_count += na_in_row
                        print(f"  Signal {i+1}: Found {na_in_row} N/A values")
                        
                        # Take screenshot of problematic row
                        row.screenshot(path=f"signal_na_issue_row_{i+1}.png")
                    
                    if prices_found > 0:
                        valid_price_count += prices_found
                        print(f"  Signal {i+1}: Found {prices_found} valid prices")
                    
                except Exception as e:
                    print(f"  Error checking signal {i+1}: {e}")
            
            # Evaluate results
            if na_count == 0:
                self.log_test_result("Signal Prices Check", "PASSED", 
                                   f"All signals have valid prices. Found {valid_price_count} valid prices across {total_signals} signals")
            elif na_count < total_signals:
                self.log_test_result("Signal Prices Check", "WARNING", 
                                   f"Some signals have N/A prices. Found {na_count} N/A values and {valid_price_count} valid prices")
            else:
                self.log_test_result("Signal Prices Check", "FAILED", 
                                   f"Most/all signals have N/A prices. Found {na_count} N/A values, only {valid_price_count} valid prices")
            
            # Take full page screenshot
            page.screenshot(path="signals_page_full.png", full_page=True)
            
            return na_count == 0
            
        except Exception as e:
            self.log_test_result("Signal Prices Check", "FAILED", f"Failed to check signal prices: {str(e)}")
            page.screenshot(path="test_signal_prices_failed.png")
            return False
    
    def test_signal_api_response(self, page):
        """Test signal API response for price data"""
        print("🔌 Testing signal API response...")
        
        try:
            # Intercept API calls
            api_responses = []
            
            def handle_response(response):
                if '/signals/api/' in response.url or '/api/signals' in response.url:
                    try:
                        data = response.json()
                        api_responses.append({
                            'url': response.url,
                            'status': response.status,
                            'data': data
                        })
                    except:
                        pass
            
            page.on('response', handle_response)
            
            # Navigate to signals page to trigger API calls
            page.goto(f"{self.base_url}/signals/")
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            
            # Check API responses
            if api_responses:
                for response in api_responses:
                    if response['status'] == 200 and 'signals' in response['data']:
                        signals = response['data']['signals']
                        
                        null_price_count = 0
                        valid_price_count = 0
                        
                        for signal in signals:
                            entry_price = signal.get('entry_price')
                            target_price = signal.get('target_price')
                            stop_loss = signal.get('stop_loss')
                            
                            if entry_price is None or target_price is None or stop_loss is None:
                                null_price_count += 1
                            else:
                                valid_price_count += 1
                        
                        if null_price_count == 0:
                            self.log_test_result("Signal API Check", "PASSED", 
                                               f"API returns valid prices for all {valid_price_count} signals")
                        else:
                            self.log_test_result("Signal API Check", "FAILED", 
                                               f"API returns null prices: {null_price_count} null, {valid_price_count} valid")
                        
                        # Save API response for debugging
                        with open('signal_api_response.json', 'w') as f:
                            json.dump(response['data'], f, indent=2)
                        
                        return null_price_count == 0
                
                self.log_test_result("Signal API Check", "WARNING", "API responses found but no signal data")
            else:
                self.log_test_result("Signal API Check", "WARNING", "No signal API responses intercepted")
            
            return True
            
        except Exception as e:
            self.log_test_result("Signal API Check", "FAILED", f"API test failed: {str(e)}")
            return False
    
    def test_signal_details_modal(self, page):
        """Test signal details modal for price information"""
        print("🔍 Testing signal details modal...")
        
        try:
            page.goto(f"{self.base_url}/signals/")
            page.wait_for_load_state('networkidle')
            
            # Look for clickable signal rows or view buttons
            view_buttons = page.locator("button:has-text('View'), .btn:has-text('View'), tr[data-signal-id]")
            
            if view_buttons.count() > 0:
                # Click first view button or signal row
                view_buttons.first.click()
                page.wait_for_timeout(2000)
                
                # Look for modal or details
                modal_selectors = [".modal", ".signal-details", ".popup", "[role='dialog']"]
                modal_found = False
                
                for selector in modal_selectors:
                    if page.locator(selector).is_visible():
                        modal_content = page.locator(selector).text_content()
                        
                        if "N/A" in modal_content:
                            self.log_test_result("Signal Details Modal", "FAILED", "Modal contains N/A values")
                            page.screenshot(path="signal_modal_na_issue.png")
                        else:
                            self.log_test_result("Signal Details Modal", "PASSED", "Modal shows valid price data")
                        
                        modal_found = True
                        break
                
                if not modal_found:
                    self.log_test_result("Signal Details Modal", "WARNING", "No modal opened or found")
            else:
                self.log_test_result("Signal Details Modal", "WARNING", "No view buttons or clickable signals found")
            
            return True
            
        except Exception as e:
            self.log_test_result("Signal Details Modal", "FAILED", f"Modal test failed: {str(e)}")
            page.screenshot(path="test_signal_modal_failed.png")
            return False
    
    def run_all_tests(self):
        """Run all signal price tests"""
        print("🚀 Starting Signal Price Tests with Playwright")
        print("=" * 60)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # Set to True for headless testing
                slow_mo=1000     # Slow down for visibility
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                record_video_dir="test_videos/",
                record_har_path="signal_test_results.har"
            )
            
            page = context.new_page()
            
            # Enable console logging
            page.on("console", lambda msg: print(f"Console: {msg.text}"))
            page.on("pageerror", lambda err: print(f"Page Error: {err}"))
            
            try:
                # Run tests in sequence
                if self.login(page):
                    self.test_signals_page_loads(page)
                    self.test_signal_generation(page)
                    self.test_signal_prices_not_na(page)
                    self.test_signal_api_response(page)
                    self.test_signal_details_modal(page)
                
            except Exception as e:
                print(f"❌ Test execution failed: {e}")
                page.screenshot(path="test_execution_failed.png")
            
            finally:
                context.close()
                browser.close()
        
        # Save test results
        with open('signal_price_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 Test Results Summary")
        print("=" * 60)
        summary = self.test_results['summary']
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {(summary['passed']/summary['total']*100):.1f}%" if summary['total'] > 0 else "N/A")
        
        # Print detailed results
        print("\n📋 Detailed Results:")
        for test in self.test_results['tests']:
            status_icon = "✅" if test['status'] == 'PASSED' else "⚠️" if test['status'] == 'WARNING' else "❌"
            print(f"{status_icon} {test['test_name']}: {test['message']}")
        
        print("\n📁 Generated Files:")
        print("- signal_price_test_results.json (detailed results)")
        print("- signal_api_response.json (API response data)")
        print("- Various screenshots for failed tests")
        print("- test_videos/ (recorded test videos)")
        
        if summary['failed'] > 0:
            print("\n🔧 Issues Found:")
            print("If tests show N/A prices, run the fix script:")
            print("python fix_signal_prices_now.py")
        else:
            print("\n🎉 All tests passed! Signal prices are working correctly.")
        
        return summary['failed'] == 0

if __name__ == "__main__":
    tester = SignalPriceTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)















































