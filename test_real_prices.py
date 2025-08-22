#!/usr/bin/env python
"""
Test script to verify the real price service with Django
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.real_price_service import get_live_prices, refresh_prices

def test_real_price_service():
    """Test the real price service"""
    print("🚀 TESTING REAL PRICE SERVICE WITH DJANGO")
    print("=" * 50)
    
    try:
        # Test getting live prices
        print("📊 Fetching live cryptocurrency prices...")
        live_prices = get_live_prices()
        
        if live_prices:
            print(f"✅ Successfully fetched prices for {len(live_prices)} symbols")
            print("\n=== 🪙 REAL CRYPTOCURRENCY PRICES ===")
            
            for symbol, data in live_prices.items():
                price = data.get('price', 0)
                change_24h = data.get('change_24h', 0)
                volume_24h = data.get('volume_24h', 0)
                source = data.get('source', 'Unknown')
                
                print(f"{symbol:6} | ${price:>12.2f} | {change_24h:>+8.2f}% | Volume: {volume_24h:>12,.0f} | Source: {source}")
            
            # Test refresh
            print("\n🔄 Testing price refresh...")
            refreshed_prices = refresh_prices()
            print(f"✅ Refreshed prices for {len(refreshed_prices)} symbols")
            
            return True
        else:
            print("❌ No prices returned")
            return False
            
    except Exception as e:
        print(f"❌ Error testing real price service: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_real_price_service()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 REAL PRICE SERVICE IS WORKING!")
        print("Your dashboard will now show real cryptocurrency prices!")
    else:
        print("⚠️ REAL PRICE SERVICE HAS ISSUES")
        print("Check the error messages above")

if __name__ == "__main__":
    main()






