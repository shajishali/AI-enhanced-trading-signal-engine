#!/usr/bin/env python
"""
Test script to get real cryptocurrency prices
"""

import requests
import json
from decimal import Decimal

def test_binance_api():
    """Test Binance API for real cryptocurrency prices"""
    print("=== 🪙 TESTING BINANCE API FOR REAL PRICES ===")
    
    try:
        # Get 24hr ticker for all symbols
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Filter for major cryptocurrencies
            major_coins = ['BTC', 'ETH', 'XRP', 'USDT', 'BNB', 'SOL', 'USDC', 'DOGE', 'TRX', 'ADA', 'LINK', 'XLM']
            
            print(f"Found {len(data)} trading pairs")
            print("\n=== 📊 REAL CRYPTOCURRENCY PRICES ===")
            
            for ticker in data:
                symbol = ticker['symbol']
                
                # Check if it's a major coin with USDT pair
                for coin in major_coins:
                    if symbol == f"{coin}USDT":
                        price = float(ticker['lastPrice'])
                        change_24h = float(ticker['priceChangePercent'])
                        volume_24h = float(ticker['volume'])
                        
                        print(f"{coin:6} | ${price:>12.2f} | {change_24h:>+8.2f}% | Volume: {volume_24h:>12,.0f}")
                        break
            
            return True
        else:
            print(f"Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error testing Binance API: {e}")
        return False

def test_coingecko_api():
    """Test CoinGecko API for real cryptocurrency prices"""
    print("\n=== 🪙 TESTING COINGECKO API FOR REAL PRICES ===")
    
    try:
        # Get current prices for major coins
        coin_ids = ['bitcoin', 'ethereum', 'ripple', 'tether', 'binancecoin', 'solana', 'usd-coin', 'dogecoin', 'tron', 'cardano', 'chainlink', 'stellar']
        
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("=== 📊 REAL CRYPTOCURRENCY PRICES (CoinGecko) ===")
            
            symbol_map = {
                'bitcoin': 'BTC',
                'ethereum': 'ETH',
                'ripple': 'XRP',
                'tether': 'USDT',
                'binancecoin': 'BNB',
                'solana': 'SOL',
                'usd-coin': 'USDC',
                'dogecoin': 'DOGE',
                'tron': 'TRX',
                'cardano': 'ADA',
                'chainlink': 'LINK',
                'stellar': 'XLM'
            }
            
            for coin_id, coin_data in data.items():
                symbol = symbol_map.get(coin_id, coin_id.upper())
                price = coin_data.get('usd', 0)
                change_24h = coin_data.get('usd_24h_change', 0)
                volume_24h = coin_data.get('usd_24h_vol', 0)
                
                print(f"{symbol:6} | ${price:>12.2f} | {change_24h:>+8.2f}% | Volume: ${volume_24h:>12,.0f}")
            
            return True
        else:
            print(f"Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error testing CoinGecko API: {e}")
        return False

def test_django_api():
    """Test Django API endpoint"""
    print("\n=== 🪙 TESTING DJANGO API ENDPOINT ===")
    
    try:
        # Test the Django API endpoint
        url = "http://127.0.0.1:8000/data/api/live-prices/"
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ API returned JSON data:")
                print(json.dumps(data, indent=2))
                return True
            except json.JSONDecodeError:
                print("❌ API didn't return valid JSON")
                print("Response preview:", response.text[:200])
                return False
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error testing Django API: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 TESTING LIVE CRYPTOCURRENCY PRICES")
    print("=" * 50)
    
    # Test external APIs
    binance_success = test_binance_api()
    coingecko_success = test_coingecko_api()
    
    # Test Django API
    django_success = test_django_api()
    
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY:")
    print(f"Binance API: {'✅ SUCCESS' if binance_success else '❌ FAILED'}")
    print(f"CoinGecko API: {'✅ SUCCESS' if coingecko_success else '❌ FAILED'}")
    print(f"Django API: {'✅ SUCCESS' if django_success else '❌ FAILED'}")
    
    if binance_success and coingecko_success:
        print("\n🎉 External APIs are working! Real prices available.")
        print("Next step: Fix Django API to return real prices.")
    else:
        print("\n⚠️ Some external APIs failed. Check internet connection.")

if __name__ == "__main__":
    main()
