#!/usr/bin/env python3
"""
Test the symbols API endpoint to see if it's working
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
import json

def test_symbols_api():
    """Test the symbols API endpoint"""
    print("Testing symbols API endpoint...")
    
    # Create test user
    user = User.objects.create_user(
        username='api_test_user',
        email='api@test.com',
        password='testpass123'
    )
    
    try:
        client = Client()
        client.login(username='api_test_user', password='testpass123')
        
        # Test the symbols API endpoint
        response = client.get('/signals/api/backtests/search/?action=symbols')
        
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"API Response Data: {json.dumps(data, indent=2)}")
                
                if data.get('success'):
                    symbols = data.get('symbols', [])
                    print(f"✅ Found {len(symbols)} symbols")
                    
                    # Check if XRP is in the symbols
                    xrp_symbols = [s for s in symbols if 'XRP' in s.get('symbol', '')]
                    if xrp_symbols:
                        print(f"✅ XRP found: {xrp_symbols}")
                    else:
                        print("❌ XRP not found in symbols")
                    
                    return True
                else:
                    print(f"❌ API returned success=False: {data.get('error', 'Unknown error')}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"Response content: {response.content.decode('utf-8')[:500]}")
                return False
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response content: {response.content.decode('utf-8')[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False
    finally:
        user.delete()

if __name__ == '__main__':
    test_symbols_api()


























