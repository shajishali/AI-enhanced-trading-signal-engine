from playwright.sync_api import sync_playwright
import time

def test_signals_with_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # First, go to login page
            print("Navigating to login page...")
            page.goto("http://127.0.0.1:8000/login/")
            time.sleep(2)
            
            # Check if we're on login page
            title = page.title()
            print(f"Page title: {title}")
            
            # Fill in login credentials (you may need to adjust these)
            print("Attempting to login...")
            try:
                # Look for username and password fields
                username_field = page.locator('input[name="username"], input[type="text"]').first
                password_field = page.locator('input[name="password"], input[type="password"]').first
                
                if username_field.count() > 0 and password_field.count() > 0:
                    username_field.fill("admin")  # Adjust username as needed
                    password_field.fill("admin")  # Adjust password as needed
                    
                    # Find and click login button
                    login_button = page.locator('button[type="submit"], input[type="submit"]').first
                    if login_button.count() > 0:
                        login_button.click()
                        print("Login button clicked, waiting for redirect...")
                        time.sleep(3)
                    else:
                        print("Login button not found")
                        return
                else:
                    print("Username or password fields not found")
                    return
                    
            except Exception as e:
                print(f"Login error: {e}")
                return
            
            # Now try to access signals page
            print("Navigating to signals page...")
            page.goto("http://127.0.0.1:8000/signals/")
            time.sleep(3)
            
            # Check what's on the page
            print("\n=== PAGE TITLE ===")
            title = page.title()
            print(f"Page title: {title}")
            
            # Check for specific elements
            print("\n=== LOOKING FOR ELEMENTS ===")
            
            # Check for Signal Generation section
            signal_gen = page.locator("text=Signal Generation")
            if signal_gen.count() > 0:
                print("✅ Found 'Signal Generation' section")
            else:
                print("❌ 'Signal Generation' section NOT found")
            
            # Check for Test Timeframe Modal button
            test_button = page.locator("text=Test Timeframe Modal")
            if test_button.count() > 0:
                print("✅ Found 'Test Timeframe Modal' button")
            else:
                print("❌ 'Test Timeframe Modal' button NOT found")
            
            # Check for enhanced chart section
            chart_section = page.locator("text=Signals Overview Dashboard")
            if chart_section.count() > 0:
                print("✅ Found 'Signals Overview Dashboard' section")
            else:
                print("❌ 'Signals Overview Dashboard' section NOT found")
            
            # Check for signals table
            signals_table = page.locator("#signals-table")
            if signals_table.count() > 0:
                print("✅ Found signals table")
            else:
                print("❌ Signals table NOT found")
            
            # Check for modal
            modal = page.locator("#signalModal")
            if modal.count() > 0:
                print("✅ Found signal modal")
            else:
                print("❌ Signal modal NOT found")
            
            # Check for timeframe and entry point columns in table
            timeframe_col = page.locator("text=Timeframe")
            if timeframe_col.count() > 0:
                print("✅ Found Timeframe column in table")
            else:
                print("❌ Timeframe column NOT found")
            
            entry_point_col = page.locator("text=Entry Point")
            if entry_point_col.count() > 0:
                print("✅ Found Entry Point column in table")
            else:
                print("❌ Entry Point column NOT found")
            
            # Check for beautiful stat cards
            stat_cards = page.locator(".stat-card")
            if stat_cards.count() > 0:
                print(f"✅ Found {stat_cards.count()} beautiful stat cards")
            else:
                print("❌ Stat cards NOT found")
            
            # Take a screenshot
            print("\nTaking screenshot...")
            page.screenshot(path="signals_page_with_login.png")
            print("Screenshot saved as signals_page_with_login.png")
            
            # Test the modal if test button is found
            if test_button.count() > 0:
                print("\n=== TESTING MODAL ===")
                test_button.click()
                time.sleep(2)
                
                # Check if modal opened
                modal_content = page.locator("#signalModal")
                if modal_content.is_visible():
                    print("✅ Modal opened successfully")
                    
                    # Check for timeframe and entry point in modal
                    timeframe_in_modal = page.locator("text=Timeframe")
                    if timeframe_in_modal.count() > 0:
                        print("✅ Found Timeframe in modal")
                    else:
                        print("❌ Timeframe NOT found in modal")
                    
                    entry_point_in_modal = page.locator("text=Entry Point Type")
                    if entry_point_in_modal.count() > 0:
                        print("✅ Found Entry Point Type in modal")
                    else:
                        print("❌ Entry Point Type NOT found in modal")
                    
                    # Take screenshot of modal
                    page.screenshot(path="signals_modal_with_login.png")
                    print("Modal screenshot saved as signals_modal_with_login.png")
                else:
                    print("❌ Modal did not open")
            
            print("\n=== CHECK COMPLETE ===")
            
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_signals_with_login()
