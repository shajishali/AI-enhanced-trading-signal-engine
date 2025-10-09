#!/usr/bin/env python3
"""
Test script to check if the backtesting page works properly
"""

import os
import sys
import django

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

# Now import Django components
from django.test import Client
from django.contrib.auth.models import User

def test_backtesting_page():
    """Test the backtesting page functionality"""
    print("Testing backtesting page...")
    
    # Create test client
    client = Client()
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com'
        }
    )
    # Always set password to ensure it's correct
    user.set_password('testpass123')
    user.save()
    
    # Login
    login_success = client.login(username='testuser', password='testpass123')
    print(f"Login successful: {login_success}")
    
    if not login_success:
        print("❌ Failed to login")
        return False
    
    # Test backtesting page
    try:
        response = client.get('/analytics/backtesting/')
        print(f"Backtesting page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backtesting page loads successfully")
            
            # Check if the page contains expected elements
            content = response.content.decode('utf-8')
            
            # Check for key elements
            checks = [
                ('Enhanced Backtesting', 'Page title'),
                ('symbol', 'Symbol dropdown'),
                ('start_date', 'Start date input'),
                ('end_date', 'End date input'),
                ('action', 'Action dropdown'),
                ('backtestForm', 'Form element'),
                ('loadSymbols', 'JavaScript function'),
                ('handleFormSubmit', 'Form submission handler')
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} missing")
            
            return True
        else:
            print(f"❌ Backtesting page failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing backtesting page: {e}")
        return False
    
    finally:
        # Clean up
        user.delete()

def test_api_endpoints():
    """Test the API endpoints used by the backtesting page"""
    print("\nTesting API endpoints...")
    
    client = Client()
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com'
        }
    )
    # Always set password to ensure it's correct
    user.set_password('testpass123')
    user.save()
    
    # Login
    client.login(username='testuser', password='testpass123')
    
    try:
        # Test symbols API
        response = client.get('/signals/api/backtests/search/?action=symbols')
        print(f"Symbols API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Symbols API working: {data.get('success', False)}")
            if data.get('success'):
                print(f"   Found {len(data.get('symbols', []))} symbols")
        else:
            print(f"❌ Symbols API failed: {response.status_code}")
        
        # Test search history API
        response = client.get('/signals/api/backtests/search/?action=history')
        print(f"Search history API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search history API working: {data.get('success', False)}")
        else:
            print(f"❌ Search history API failed: {response.status_code}")
        
        # Test backtest API
        test_data = {
            'action': 'generate_signals',
            'symbol': 'XRP',
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-01-31T23:59:59Z'
        }
        
        response = client.post(
            '/signals/api/backtests/',
            data=test_data,
            content_type='application/json'
        )
        print(f"Backtest API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backtest API working: {data.get('success', False)}")
            if data.get('success'):
                print(f"   Generated {len(data.get('signals', []))} signals")
        else:
            print(f"❌ Backtest API failed: {response.status_code}")
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Error response: {response.content.decode('utf-8')[:200]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False
    
    finally:
        # Clean up
        user.delete()

def main():
    """Main test function"""
    print("=" * 60)
    print("BACKTESTING PAGE DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Test backtesting page
    page_works = test_backtesting_page()
    
    # Test API endpoints
    api_works = test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if page_works and api_works:
        print("🎉 All tests passed! Backtesting page should be working.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        
        if not page_works:
            print("❌ Backtesting page has issues")
        if not api_works:
            print("❌ API endpoints have issues")
    
    print("\nIf you're still experiencing issues:")
    print("1. Check browser console for JavaScript errors")
    print("2. Verify all static files are loading")
    print("3. Check Django logs for server errors")
    print("4. Ensure all required models and services are properly imported")

if __name__ == '__main__':
    main()
