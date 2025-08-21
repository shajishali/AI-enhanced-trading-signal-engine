#!/usr/bin/env python3
"""
Simple Playwright Test Runner for AI Trading Engine
Run this script to execute all Playwright tests
"""

import os
import sys
from playwright.sync_api import sync_playwright

def test_home_page(page):
    """Test the home page loads correctly"""
    print("🏠 Testing home page...")
    
    page.goto("http://127.0.0.1:8000/")
    
    # Check title
    assert "AI Trading Engine" in page.title(), f"Expected 'AI Trading Engine' in title, got '{page.title()}'"
    
    # Check navigation elements
    assert page.locator("nav").is_visible(), "Navigation should be visible"
    assert page.locator("text=Dashboard").is_visible(), "Dashboard link should be visible"
    assert page.locator("text=Analytics").is_visible(), "Analytics link should be visible"
    assert page.locator("text=Signals").is_visible(), "Signals link should be visible"
    
    print("✅ Home page test passed")

def test_login(page):
    """Test login functionality"""
    print("🔐 Testing login...")
    
    page.goto("http://127.0.0.1:8000/login/")
    
    # Fill login form
    page.fill("input[name='username']", "admin")
    page.fill("input[name='password']", "admin123")
    page.click("button[type='submit']")
    
    # Wait for redirect to dashboard
    page.wait_for_url("**/dashboard/")
    
    # Check we're on dashboard
    assert "dashboard" in page.url, "Should be redirected to dashboard after login"
    
    print("✅ Login test passed")

def test_dashboard_navigation(page):
    """Test dashboard navigation"""
    print("🧭 Testing dashboard navigation...")
    
    # Start from dashboard (after login)
    page.goto("http://127.0.0.1:8000/dashboard/")
    
    # Test navigation to Portfolio
    page.click("text=Portfolio")
    page.wait_for_url("**/portfolio/")
    assert "portfolio" in page.url, "Should navigate to portfolio page"
    
    # Test navigation to Signals
    page.click("text=Signals")
    page.wait_for_url("**/signals/")
    assert "signals" in page.url, "Should navigate to signals page"
    
    # Test navigation to Analytics
    page.click("text=Analytics")
    page.wait_for_url("**/analytics/")
    assert "analytics" in page.url, "Should navigate to analytics page"
    
    print("✅ Dashboard navigation test passed")

def test_analytics_pages(page):
    """Test analytics sub-pages"""
    print("📊 Testing analytics pages...")
    
    # Start from analytics main page
    page.goto("http://127.0.0.1:8000/analytics/")
    
    # Test Performance page
    page.click("text=Performance")
    page.wait_for_url("**/performance/")
    assert "performance" in page.url, "Should navigate to performance page"
    
    # Test Risk Management page
    page.click("text=Risk Management")
    page.wait_for_url("**/risk/")
    assert "risk" in page.url, "Should navigate to risk management page"
    
    # Test Backtesting page
    page.click("text=Backtesting")
    page.wait_for_url("**/backtesting/")
    assert "backtesting" in page.url, "Should navigate to backtesting page"
    
    # Test ML Dashboard page
    page.click("text=ML Dashboard")
    page.wait_for_url("**/ml/")
    assert "ml" in page.url, "Should navigate to ML dashboard page"
    
    print("✅ Analytics pages test passed")

def test_signals_page(page):
    """Test signals page"""
    print("📡 Testing signals page...")
    
    page.goto("http://127.0.0.1:8000/signals/")
    
    # Check signals content loads
    assert page.locator("text=Market Signals").is_visible(), "Market Signals should be visible"
    
    print("✅ Signals page test passed")

def test_subscription_page(page):
    """Test subscription page"""
    print("💳 Testing subscription page...")
    
    page.goto("http://127.0.0.1:8000/subscription/choice/")
    
    # Check subscription content
    assert page.locator("text=Choose Your Plan").is_visible(), "Subscription plans should be visible"
    
    print("✅ Subscription page test passed")

def run_tests():
    """Run all tests"""
    print("🚀 Starting Playwright Tests for AI Trading Engine")
    print("=" * 60)
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(
            headless=False,  # Set to True for headless testing
            slow_mo=500      # Slow down actions for visibility
        )
        
        # Create context
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            record_video_dir="test_videos/"
        )
        
        page = context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Page Error: {err}"))
        
        tests = [
            test_home_page,
            test_login,
            test_dashboard_navigation,
            test_analytics_pages,
            test_signals_page,
            test_subscription_page
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                test(page)
                passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} failed: {e}")
                # Take screenshot on failure
                page.screenshot(path=f"test_failure_{test.__name__}.png")
                failed += 1
            print("-" * 40)
        
        # Close browser
        context.close()
        browser.close()
        
        # Print results
        print("=" * 60)
        print(f"🎯 Test Results: {passed} passed, {failed} failed")
        print("=" * 60)
        
        if failed > 0:
            sys.exit(1)
        else:
            print("🎉 All tests passed!")

if __name__ == "__main__":
    run_tests()
















