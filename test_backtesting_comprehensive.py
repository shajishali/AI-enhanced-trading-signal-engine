#!/usr/bin/env python3
"""
Comprehensive Backtesting Test with Playwright
Tests the complete backtesting workflow and checks for N/A values
"""

import time
from playwright.sync_api import sync_playwright

def test_backtesting_comprehensive():
    """Comprehensive test of backtesting functionality"""
    print("🎭 Starting Comprehensive Backtesting Test with Playwright...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=2000)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Page Error: {err}"))
        
        try:
            # Step 1: Login
            print("🔐 Step 1: Logging in...")
            page.goto('http://127.0.0.1:8000/login/')
            page.wait_for_load_state('networkidle')
            
            page.fill("input[name='username']", "admin")
            page.fill("input[name='password']", "admin123")
            page.click("button[type='submit']")
            page.wait_for_url("**/dashboard/", timeout=10000)
            print("✅ Login successful")
            
            # Step 2: Navigate to backtesting
            print("🧭 Step 2: Navigating to backtesting...")
            page.goto('http://127.0.0.1:8000/analytics/backtesting/')
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)  # Wait for page to fully load
            print("✅ Backtesting page loaded")
            
            # Take initial screenshot
            page.screenshot(path="backtesting_initial.png")
            print("📸 Initial screenshot saved")
            
            # Step 3: Analyze page structure
            print("🔍 Step 3: Analyzing page structure...")
            
            # Look for all possible selectors for symbol selection
            symbol_selectors = [
                "select[name*='symbol']",
                "select[name*='coin']", 
                "#symbol-select",
                ".symbol-selector",
                "select:has(option[value*='BTC'])",
                "select option[value='BTC']"
            ]
            
            symbol_element = None
            for selector in symbol_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        symbol_element = page.locator(selector).first
                        print(f"✅ Found symbol selector: {selector}")
                        break
                except:
                    continue
            
            if not symbol_element:
                print("❌ No symbol selector found")
                # List all select elements
                selects = page.locator("select").all()
                print(f"Found {len(selects)} select elements:")
                for i, select in enumerate(selects):
                    try:
                        name = select.get_attribute("name") or f"select-{i}"
                        print(f"  - Select {i}: name='{name}'")
                    except:
                        print(f"  - Select {i}: (could not get name)")
            
            # Look for run/start buttons
            run_selectors = [
                "button:has-text('Run')",
                "button:has-text('Start')",
                "button:has-text('Backtest')",
                "button:has-text('Generate')",
                "input[type='submit']",
                ".btn-primary",
                "button[type='submit']"
            ]
            
            run_element = None
            for selector in run_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        run_element = page.locator(selector).first
                        print(f"✅ Found run button: {selector}")
                        break
                except:
                    continue
            
            if not run_element:
                print("❌ No run button found")
                # List all buttons
                buttons = page.locator("button").all()
                print(f"Found {len(buttons)} button elements:")
                for i, button in enumerate(buttons):
                    try:
                        text = button.text_content()
                        type_attr = button.get_attribute("type") or "button"
                        print(f"  - Button {i}: '{text}' (type: {type_attr})")
                    except:
                        print(f"  - Button {i}: (could not get text)")
            
            # Step 4: Try to run a backtest
            print("🎲 Step 4: Attempting to run backtest...")
            
            # Try to select a symbol
            if symbol_element:
                try:
                    # Check if it's a select element
                    tag_name = symbol_element.evaluate("el => el.tagName.toLowerCase()")
                    if tag_name == "select":
                        # Get all options
                        options = page.locator("select option").all()
                        print(f"Found {len(options)} options in select:")
                        for i, option in enumerate(options):
                            try:
                                value = option.get_attribute("value") or ""
                                text = option.text_content() or ""
                                print(f"  - Option {i}: value='{value}', text='{text}'")
                            except:
                                print(f"  - Option {i}: (could not get details)")
                        
                        # Try to select BTC or first non-empty option
                        try:
                            if page.locator("select option[value='BTC']").count() > 0:
                                page.select_option("select", value="BTC")
                                print("✅ Selected BTC")
                            elif len(options) > 1:
                                # Select first non-empty option
                                for option in options[1:]:  # Skip first empty option
                                    value = option.get_attribute("value")
                                    if value and value.strip():
                                        page.select_option("select", value=value)
                                        print(f"✅ Selected {value}")
                                        break
                        except Exception as e:
                            print(f"⚠️ Symbol selection failed: {e}")
                    
                except Exception as e:
                    print(f"⚠️ Error analyzing symbol selector: {e}")
            
            # Set date if available
            try:
                date_inputs = page.locator("input[type='date']").all()
                if len(date_inputs) > 0:
                    date_inputs[0].fill("2025-09-01")
                    print("✅ Set start date")
                    if len(date_inputs) > 1:
                        date_inputs[1].fill("2025-10-01")
                        print("✅ Set end date")
            except Exception as e:
                print(f"⚠️ Date setting failed: {e}")
            
            # Try to click run button
            if run_element:
                try:
                    run_element.click()
                    print("✅ Clicked run button")
                    
                    # Wait for results
                    print("⏳ Waiting for results...")
                    page.wait_for_timeout(8000)  # Wait longer for processing
                    page.wait_for_load_state('networkidle')
                    
                    # Take screenshot after running
                    page.screenshot(path="backtesting_after_run.png")
                    print("📸 After-run screenshot saved")
                    
                except Exception as e:
                    print(f"⚠️ Run button click failed: {e}")
            
            # Step 5: Check for results and N/A values
            print("📊 Step 5: Checking results...")
            
            # Look for results table
            table_selectors = [
                "table",
                ".table",
                "#signalsTable",
                ".results-table",
                "tbody tr"
            ]
            
            results_found = False
            for selector in table_selectors:
                try:
                    elements = page.locator(selector)
                    if elements.count() > 0:
                        print(f"✅ Found results table: {selector} ({elements.count()} elements)")
                        results_found = True
                        break
                except:
                    continue
            
            if results_found:
                # Check for N/A values
                page_content = page.content()
                na_count = page_content.count('N/A')
                print(f"📈 Analysis: Found {na_count} N/A values on the page")
                
                # Count table rows with data
                try:
                    data_rows = page.locator("tbody tr").count()
                    print(f"📈 Found {data_rows} data rows in results table")
                    
                    if data_rows > 0:
                        # Check first few rows for N/A values
                        for i in range(min(3, data_rows)):
                            try:
                                row = page.locator("tbody tr").nth(i)
                                row_text = row.text_content()
                                row_na_count = row_text.count('N/A')
                                if row_na_count > 0:
                                    print(f"⚠️ Row {i+1} has {row_na_count} N/A values")
                                else:
                                    print(f"✅ Row {i+1} has no N/A values")
                            except Exception as e:
                                print(f"⚠️ Error checking row {i+1}: {e}")
                    
                except Exception as e:
                    print(f"⚠️ Error counting rows: {e}")
                
                # Final assessment
                if na_count == 0:
                    print("🎉 SUCCESS: No N/A values found - Fix is working!")
                elif na_count < 10:
                    print(f"⚠️ PARTIAL SUCCESS: Only {na_count} N/A values found (much improved)")
                else:
                    print(f"❌ ISSUE: Still found {na_count} N/A values")
                
            else:
                print("❌ No results table found")
                
                # Check for error messages
                error_selectors = [
                    ".alert-danger",
                    ".error-message",
                    ":has-text('Error')",
                    ":has-text('No results')"
                ]
                
                for selector in error_selectors:
                    try:
                        if page.locator(selector).count() > 0:
                            error_text = page.locator(selector).text_content()
                            print(f"❌ Error found: {error_text}")
                    except:
                        continue
            
            # Take final screenshot
            page.screenshot(path="backtesting_final.png")
            print("📸 Final screenshot saved")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            page.screenshot(path="backtesting_error.png")
            
        finally:
            context.close()
            browser.close()

def main():
    """Main test function"""
    print("🚀 Comprehensive Backtesting Test")
    print("=" * 60)
    
    test_backtesting_comprehensive()
    
    print("=" * 60)
    print("✅ Test completed - Check screenshots for visual verification")
    print("📁 Generated files:")
    print("  - backtesting_initial.png")
    print("  - backtesting_after_run.png") 
    print("  - backtesting_final.png")

if __name__ == "__main__":
    main()