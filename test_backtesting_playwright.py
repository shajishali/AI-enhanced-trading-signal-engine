#!/usr/bin/env python3
"""
Playwright Test for Backtesting Analytics Page
Tests backtesting functionality, selects random coins and durations, and checks for N/A values in signals
"""

import os
import sys
import time
import json
import random
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, expect

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

class BacktestingAnalyticsTest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'backtesting_results': [],
            'na_issues_found': [],
            'summary': {'passed': 0, 'failed': 0, 'total': 0}
        }
        
        # Common crypto symbols to test
        self.test_symbols = ['BTC', 'ETH', 'ADA', 'XRP', 'DOT', 'LINK', 'SOL', 'MATIC', 'AVAX', 'SAND']
        
        # Duration options to test
        self.test_durations = ['1 day', '3 days', '1 week', '2 weeks', '1 month', '3 months']
    
    def log_test_result(self, test_name, status, message="", screenshot_path="", data=None):
        """Log test result"""
        result = {
            'test_name': test_name,
            'status': status,
            'message': message,
            'screenshot': screenshot_path,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results['tests'].append(result)
        self.test_results['summary']['total'] += 1
        if status == 'PASSED':
            self.test_results['summary']['passed'] += 1
            print(f"✅ {test_name}: {message}")
        elif status == 'WARNING':
            print(f"⚠️ {test_name}: {message}")
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
    
    def navigate_to_analytics_backtesting(self, page):
        """Navigate to Analytics > Backtesting page"""
        print("🧭 Navigating to Analytics > Backtesting...")
        
        try:
            # Navigate to analytics page
            page.goto(f"{self.base_url}/analytics/")
            page.wait_for_load_state('networkidle')
            
            # Look for backtesting link/button
            backtesting_selectors = [
                "a[href*='backtesting']",
                "button:has-text('Backtesting')",
                "a:has-text('Backtesting')",
                ".nav-link:has-text('Backtesting')",
                "[data-bs-target*='backtesting']"
            ]
            
            navigation_successful = False
            for selector in backtesting_selectors:
                try:
                    if page.locator(selector).is_visible():
                        page.click(selector)
                        page.wait_for_timeout(2000)
                        navigation_successful = True
                        break
                except:
                    continue
            
            if not navigation_successful:
                # Try direct URL
                page.goto(f"{self.base_url}/analytics/backtesting/")
                page.wait_for_load_state('networkidle')
                navigation_successful = True
            
            # Verify we're on the backtesting page
            page.wait_for_timeout(3000)
            
            self.log_test_result("Navigate to Backtesting", "PASSED", "Successfully navigated to backtesting page")
            return True
            
        except Exception as e:
            self.log_test_result("Navigate to Backtesting", "FAILED", f"Navigation failed: {str(e)}")
            page.screenshot(path="test_backtesting_navigation_failed.png")
            return False
    
    def test_backtesting_page_elements(self, page):
        """Test that backtesting page has required elements"""
        print("🔍 Testing backtesting page elements...")
        
        try:
            # Look for key backtesting elements
            elements_to_check = [
                ("Symbol/Coin selector", ["select[name*='symbol']", "select[name*='coin']", "#symbol-select", ".symbol-selector"]),
                ("Duration selector", ["select[name*='duration']", "select[name*='period']", "#duration-select", ".duration-selector"]),
                ("Start Date input", ["input[type='date']", "input[name*='start']", "#start-date"]),
                ("Run/Start button", ["button:has-text('Run')", "button:has-text('Start')", "button:has-text('Backtest')", ".btn-primary"])
            ]
            
            found_elements = []
            missing_elements = []
            
            for element_name, selectors in elements_to_check:
                element_found = False
                for selector in selectors:
                    try:
                        if page.locator(selector).count() > 0:
                            found_elements.append(element_name)
                            element_found = True
                            break
                    except:
                        continue
                
                if not element_found:
                    missing_elements.append(element_name)
            
            if len(found_elements) >= 2:  # At least symbol selector and run button
                self.log_test_result("Backtesting Page Elements", "PASSED", 
                                   f"Found key elements: {', '.join(found_elements)}")
                return True
            else:
                self.log_test_result("Backtesting Page Elements", "FAILED", 
                                   f"Missing elements: {', '.join(missing_elements)}")
                page.screenshot(path="backtesting_elements_missing.png")
                return False
                
        except Exception as e:
            self.log_test_result("Backtesting Page Elements", "FAILED", f"Element check failed: {str(e)}")
            page.screenshot(path="test_backtesting_elements_failed.png")
            return False
    
    def run_random_backtests(self, page, num_tests=3):
        """Run multiple backtests with random symbols and durations"""
        print(f"🎲 Running {num_tests} random backtests...")
        
        successful_tests = 0
        
        for i in range(num_tests):
            # Select random symbol and duration
            random_symbol = random.choice(self.test_symbols)
            random_duration = random.choice(self.test_durations)
            
            print(f"  Test {i+1}: {random_symbol} for {random_duration}")
            
            try:
                success = self.run_single_backtest(page, random_symbol, random_duration, test_number=i+1)
                if success:
                    successful_tests += 1
                
                # Wait between tests
                page.wait_for_timeout(2000)
                
            except Exception as e:
                print(f"    ❌ Test {i+1} failed: {e}")
                page.screenshot(path=f"backtest_random_{i+1}_failed.png")
        
        if successful_tests > 0:
            self.log_test_result("Random Backtests", "PASSED", 
                               f"Successfully completed {successful_tests}/{num_tests} random backtests")
            return True
        else:
            self.log_test_result("Random Backtests", "FAILED", 
                               f"All {num_tests} random backtests failed")
            return False
    
    def run_single_backtest(self, page, symbol, duration, test_number=1):
        """Run a single backtest with specified parameters"""
        try:
            # Try to select symbol
            symbol_selectors = [
                f"select[name*='symbol'] option[value='{symbol}']",
                f"select[name*='coin'] option[value='{symbol}']",
                f"#symbol-select option[value='{symbol}']",
                f"option:has-text('{symbol}')"
            ]
            
            symbol_selected = False
            for selector in symbol_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.select_option("select", value=symbol)
                        symbol_selected = True
                        break
                except:
                    continue
            
            if not symbol_selected:
                # Try typing in input field
                input_selectors = ["input[name*='symbol']", "#symbol-input", ".symbol-input"]
                for selector in input_selectors:
                    try:
                        if page.locator(selector).is_visible():
                            page.fill(selector, symbol)
                            symbol_selected = True
                            break
                    except:
                        continue
            
            # Try to select duration
            duration_selected = False
            duration_selectors = [
                "select[name*='duration']",
                "select[name*='period']", 
                "#duration-select"
            ]
            
            for selector in duration_selectors:
                try:
                    if page.locator(selector).is_visible():
                        # Try to find option with matching text
                        options = page.locator(f"{selector} option").all()
                        for option in options:
                            if duration.lower() in option.text_content().lower():
                                page.select_option(selector, value=option.get_attribute('value'))
                                duration_selected = True
                                break
                        if duration_selected:
                            break
                except:
                    continue
            
            # Set date range if available
            try:
                start_date_input = page.locator("input[type='date']").first
                if start_date_input.is_visible():
                    # Set start date to 30 days ago
                    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                    start_date_input.fill(start_date)
            except:
                pass
            
            # Click run/start button
            run_button_selectors = [
                "button:has-text('Run')",
                "button:has-text('Start')", 
                "button:has-text('Backtest')",
                "button:has-text('Execute')",
                ".btn-primary",
                "input[type='submit']"
            ]
            
            backtest_started = False
            for selector in run_button_selectors:
                try:
                    if page.locator(selector).is_visible():
                        page.click(selector)
                        backtest_started = True
                        break
                except:
                    continue
            
            if not backtest_started:
                print(f"    ⚠️ Could not start backtest for {symbol}")
                return False
            
            # Wait for results
            page.wait_for_timeout(5000)
            page.wait_for_load_state('networkidle')
            
            # Check for results and N/A values
            na_issues = self.check_backtest_results_for_na(page, symbol, duration, test_number)
            
            # Take screenshot of results
            page.screenshot(path=f"backtest_results_{symbol}_{test_number}.png")
            
            # Store backtest result
            backtest_result = {
                'test_number': test_number,
                'symbol': symbol,
                'duration': duration,
                'symbol_selected': symbol_selected,
                'duration_selected': duration_selected,
                'backtest_started': backtest_started,
                'na_issues_found': len(na_issues),
                'na_details': na_issues
            }
            
            self.test_results['backtesting_results'].append(backtest_result)
            
            print(f"    ✅ Backtest completed for {symbol} ({duration})")
            if na_issues:
                print(f"    ⚠️ Found {len(na_issues)} N/A issues")
            
            return True
            
        except Exception as e:
            print(f"    ❌ Backtest failed for {symbol}: {e}")
            return False
    
    def check_backtest_results_for_na(self, page, symbol, duration, test_number):
        """Check backtest results for N/A values in entry/close prices"""
        na_issues = []
        
        try:
            # Look for results table or data
            result_selectors = [
                "table tbody tr",
                ".backtest-results tr",
                ".results-table tr",
                ".signal-row",
                "[data-signal-id]"
            ]
            
            results_found = False
            for selector in result_selectors:
                try:
                    rows = page.locator(selector)
                    if rows.count() > 0:
                        results_found = True
                        
                        # Check each row for N/A values
                        for i in range(min(rows.count(), 20)):  # Check first 20 rows
                            try:
                                row = rows.nth(i)
                                row_text = row.text_content()
                                
                                # Check for N/A in entry/close price columns
                                if 'N/A' in row_text:
                                    # Count N/A occurrences
                                    na_count = row_text.count('N/A')
                                    
                                    # Try to identify which columns have N/A
                                    cells = row.locator('td, th').all()
                                    na_columns = []
                                    
                                    for j, cell in enumerate(cells):
                                        cell_text = cell.text_content()
                                        if 'N/A' in cell_text:
                                            na_columns.append(f"Column {j+1}")
                                    
                                    na_issue = {
                                        'row_index': i + 1,
                                        'na_count': na_count,
                                        'na_columns': na_columns,
                                        'row_text_sample': row_text[:200] + "..." if len(row_text) > 200 else row_text
                                    }
                                    
                                    na_issues.append(na_issue)
                                    
                                    # Take screenshot of problematic row
                                    row.screenshot(path=f"na_issue_{symbol}_{test_number}_row_{i+1}.png")
                            
                            except Exception as e:
                                continue
                        
                        break
                        
                except:
                    continue
            
            if not results_found:
                # Check for error messages or empty results
                error_selectors = [
                    ".alert-danger",
                    ".error-message", 
                    ":has-text('No results')",
                    ":has-text('Error')"
                ]
                
                for selector in error_selectors:
                    try:
                        if page.locator(selector).is_visible():
                            error_text = page.locator(selector).text_content()
                            na_issues.append({
                                'type': 'error',
                                'message': error_text
                            })
                            break
                    except:
                        continue
            
            # Store N/A issues in main results
            if na_issues:
                self.test_results['na_issues_found'].extend([{
                    'symbol': symbol,
                    'duration': duration,
                    'test_number': test_number,
                    'issues': na_issues
                }])
            
            return na_issues
            
        except Exception as e:
            print(f"    Error checking N/A values: {e}")
            return []
    
    def test_api_backtesting_data(self, page):
        """Test backtesting API endpoints for N/A values"""
        print("🔌 Testing backtesting API data...")
        
        try:
            # Intercept API calls
            api_responses = []
            
            def handle_response(response):
                if any(keyword in response.url.lower() for keyword in ['backtest', 'analytics', 'performance']):
                    try:
                        if response.status == 200:
                            data = response.json()
                            api_responses.append({
                                'url': response.url,
                                'status': response.status,
                                'data': data
                            })
                    except:
                        pass
            
            page.on('response', handle_response)
            
            # Navigate to trigger API calls
            page.goto(f"{self.base_url}/analytics/backtesting/")
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            
            # Analyze API responses
            api_na_issues = []
            
            for response in api_responses:
                data = response['data']
                
                # Check for N/A values in API response
                def check_for_na_recursive(obj, path=""):
                    issues = []
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            current_path = f"{path}.{key}" if path else key
                            if value is None and any(price_key in key.lower() for price_key in ['entry', 'close', 'price', 'target', 'stop']):
                                issues.append({
                                    'path': current_path,
                                    'value': value,
                                    'type': 'null_price'
                                })
                            elif isinstance(value, (dict, list)):
                                issues.extend(check_for_na_recursive(value, current_path))
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            current_path = f"{path}[{i}]"
                            issues.extend(check_for_na_recursive(item, current_path))
                    
                    return issues
                
                na_issues_in_response = check_for_na_recursive(data)
                if na_issues_in_response:
                    api_na_issues.append({
                        'url': response['url'],
                        'issues': na_issues_in_response
                    })
            
            # Save API responses for debugging
            with open('backtesting_api_responses.json', 'w') as f:
                json.dump(api_responses, f, indent=2, default=str)
            
            if api_na_issues:
                self.log_test_result("API Backtesting Data", "FAILED", 
                                   f"Found N/A issues in {len(api_na_issues)} API responses")
                
                # Save API issues
                with open('backtesting_api_na_issues.json', 'w') as f:
                    json.dump(api_na_issues, f, indent=2)
                
                return False
            else:
                self.log_test_result("API Backtesting Data", "PASSED", 
                                   f"No N/A issues found in {len(api_responses)} API responses")
                return True
                
        except Exception as e:
            self.log_test_result("API Backtesting Data", "FAILED", f"API test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backtesting tests"""
        print("🚀 Starting Backtesting Analytics Tests with Playwright")
        print("=" * 70)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # Set to True for headless testing
                slow_mo=1000     # Slow down for visibility
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                record_video_dir="test_videos/",
                record_har_path="backtesting_test_results.har"
            )
            
            page = context.new_page()
            
            # Enable console logging
            page.on("console", lambda msg: print(f"Console: {msg.text}"))
            page.on("pageerror", lambda err: print(f"Page Error: {err}"))
            
            try:
                # Run tests in sequence
                if self.login(page):
                    if self.navigate_to_analytics_backtesting(page):
                        self.test_backtesting_page_elements(page)
                        self.run_random_backtests(page, num_tests=3)
                        self.test_api_backtesting_data(page)
                
            except Exception as e:
                print(f"❌ Test execution failed: {e}")
                page.screenshot(path="test_execution_failed.png")
            
            finally:
                context.close()
                browser.close()
        
        # Save test results
        with open('backtesting_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        # Print summary
        self.print_test_summary()
        
        return self.test_results['summary']['failed'] == 0
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 Backtesting Analytics Test Results Summary")
        print("=" * 70)
        
        summary = self.test_results['summary']
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {(summary['passed']/summary['total']*100):.1f}%" if summary['total'] > 0 else "N/A")
        
        # Print detailed results
        print("\n📋 Detailed Test Results:")
        for test in self.test_results['tests']:
            status_icon = "✅" if test['status'] == 'PASSED' else "⚠️" if test['status'] == 'WARNING' else "❌"
            print(f"{status_icon} {test['test_name']}: {test['message']}")
        
        # Print backtesting results
        if self.test_results['backtesting_results']:
            print("\n🎲 Random Backtest Results:")
            for result in self.test_results['backtesting_results']:
                symbol = result['symbol']
                duration = result['duration']
                na_count = result['na_issues_found']
                status = "✅" if na_count == 0 else f"⚠️ ({na_count} N/A issues)"
                print(f"  {status} {symbol} ({duration})")
        
        # Print N/A issues summary
        total_na_issues = len(self.test_results['na_issues_found'])
        if total_na_issues > 0:
            print(f"\n🔍 N/A Issues Found: {total_na_issues}")
            for issue_group in self.test_results['na_issues_found']:
                symbol = issue_group['symbol']
                duration = issue_group['duration']
                issues = issue_group['issues']
                print(f"  ❌ {symbol} ({duration}): {len(issues)} issues")
                for issue in issues[:3]:  # Show first 3 issues
                    if 'row_index' in issue:
                        print(f"    - Row {issue['row_index']}: {issue['na_count']} N/A values in {', '.join(issue['na_columns'])}")
        else:
            print("\n✅ No N/A Issues Found in Backtesting Results!")
        
        print("\n📁 Generated Files:")
        print("- backtesting_test_results.json (detailed results)")
        print("- backtesting_api_responses.json (API response data)")
        if total_na_issues > 0:
            print("- backtesting_api_na_issues.json (N/A issues details)")
        print("- Various screenshots for analysis")
        print("- test_videos/ (recorded test videos)")
        
        if total_na_issues > 0:
            print("\n🔧 N/A Issues Found:")
            print("The backtesting results contain N/A values in entry/close prices.")
            print("This indicates a data quality issue that needs to be addressed.")
            print("Check the generated files for detailed analysis.")
        else:
            print("\n🎉 All backtesting data looks good! No N/A issues found.")

if __name__ == "__main__":
    tester = BacktestingAnalyticsTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)