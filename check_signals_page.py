from playwright.sync_api import sync_playwright
import time

def check_signals_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to signals page
            print("Navigating to signals page...")
            page.goto("http://127.0.0.1:8000/signals/")
            
            # Wait for page to load
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
            
            # Check for chart section
            chart_section = page.locator("text=Signals Overview Chart")
            if chart_section.count() > 0:
                print("✅ Found 'Signals Overview Chart' section")
            else:
                print("❌ 'Signals Overview Chart' section NOT found")
            
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
            
            # Take a screenshot
            print("\nTaking screenshot...")
            page.screenshot(path="signals_page_check.png")
            print("Screenshot saved as signals_page_check.png")
            
            # Look for any buttons or controls
            print("\n=== ALL BUTTONS ON PAGE ===")
            buttons = page.locator("button")
            button_count = buttons.count()
            print(f"Found {button_count} buttons:")
            
            for i in range(min(button_count, 20)):  # Show first 20 buttons
                try:
                    button_text = buttons.nth(i).inner_text()
                    print(f"  {i+1}. {button_text}")
                except:
                    print(f"  {i+1}. [Error reading button]")
            
            # Look for any cards or sections
            print("\n=== PAGE SECTIONS ===")
            cards = page.locator(".card")
            card_count = cards.count()
            print(f"Found {card_count} cards:")
            
            for i in range(min(card_count, 10)):  # Show first 10 cards
                try:
                    card_header = cards.nth(i).locator(".card-header, .card-title").first
                    if card_header.count() > 0:
                        header_text = card_header.inner_text()
                        print(f"  {i+1}. {header_text}")
                    else:
                        print(f"  {i+1}. [No header]")
                except:
                    print(f"  {i+1}. [Error reading card]")
            
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
                    page.screenshot(path="signals_modal_test.png")
                    print("Modal screenshot saved as signals_modal_test.png")
                else:
                    print("❌ Modal did not open")
            
            print("\n=== CHECK COMPLETE ===")
            
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    check_signals_page()
