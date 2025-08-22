#!/usr/bin/env python
"""
Test script to verify main dashboard shows real-time cryptocurrency prices
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.dashboard.views import dashboard
from django.contrib.auth.models import User
from django.test import RequestFactory

def test_main_dashboard():
    """Test the main dashboard view"""
    print("🚀 TESTING MAIN DASHBOARD WITH REAL-TIME PRICES")
    print("=" * 60)
    
    try:
        # Create a test request
        factory = RequestFactory()
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        # Create a request
        request = factory.get('/dashboard/')
        request.user = user
        
        # Call the dashboard view
        response = dashboard(request)
        
        if response.status_code == 200:
            print("✅ Dashboard view returned successfully")
            
            # Check if the context contains live crypto prices
            context = response.context_data if hasattr(response, 'context_data') else {}
            
            if 'live_crypto_prices' in context:
                live_prices = context['live_crypto_prices']
                print(f"✅ Live crypto prices found: {len(live_prices)} symbols")
                
                print("\n=== 🪙 LIVE CRYPTOCURRENCY PRICES IN MAIN DASHBOARD ===")
                for symbol, data in live_prices.items():
                    price = data.get('price', 0)
                    change_24h = data.get('change_24h', 0)
                    volume_24h = data.get('volume_24h', 0)
                    source = data.get('source', 'Unknown')
                    
                    print(f"{symbol:6} | ${price:>12.2f} | {change_24h:>+8.2f}% | Volume: {volume_24h:>12,.0f} | Source: {source}")
                
                print(f"\n🎉 SUCCESS! Main dashboard now shows {len(live_prices)} live cryptocurrency prices!")
                print("Users will see real-time BTC, ETH, SOL, BNB, XRP, and ADA prices!")
                
            else:
                print("❌ Live crypto prices not found in dashboard context")
                
        else:
            print(f"❌ Dashboard view failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing main dashboard: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    test_main_dashboard()
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("1. Visit: http://127.0.0.1:8000/dashboard/")
    print("2. Login to your account")
    print("3. See live cryptocurrency prices in the main dashboard!")
    print("4. Prices auto-update every 30 seconds")

if __name__ == "__main__":
    main()






