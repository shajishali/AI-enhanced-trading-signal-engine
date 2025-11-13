#!/usr/bin/env python
"""
Script to check prices for multiple major crypto coins
"""
import os
import sys
import django
from datetime import datetime, timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.models import MarketData, Symbol
from django.utils import timezone as django_timezone

def check_multiple_coins():
    """Check prices for multiple major crypto coins"""
    
    # Major coins to check
    coins_to_check = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'LINK', 'DOT', 'MATIC']
    
    print("🔍 CHECKING MULTIPLE CRYPTO COINS")
    print("=" * 80)
    print(f"{'Coin':<8} {'Price':<12} {'Change':<10} {'Volume':<12} {'Data Age':<15}")
    print("-" * 80)
    
    for coin in coins_to_check:
        try:
            # Get symbol
            symbol = Symbol.objects.filter(symbol=coin, symbol_type='CRYPTO').first()
            
            if not symbol:
                print(f"{coin:<8} {'N/A':<12} {'N/A':<10} {'N/A':<12} {'Not Found':<15}")
                continue
            
            # Get latest market data
            latest_data = MarketData.objects.filter(
                symbol=symbol
            ).order_by('-timestamp').first()
            
            if not latest_data:
                print(f"{coin:<8} {'N/A':<12} {'N/A':<10} {'N/A':<12} {'No Data':<15}")
                continue
            
            # Calculate data age
            now = django_timezone.now()
            data_age = now - latest_data.timestamp
            
            # Calculate price change
            price_change = latest_data.close_price - latest_data.open_price
            change_percent = (price_change / latest_data.open_price) * 100
            
            # Format data age
            if data_age.days > 0:
                age_str = f"{data_age.days}d {data_age.seconds//3600}h"
            elif data_age.seconds > 3600:
                age_str = f"{data_age.seconds//3600}h {(data_age.seconds%3600)//60}m"
            else:
                age_str = f"{data_age.seconds//60}m"
            
            # Format change
            change_str = f"{change_percent:+.2f}%"
            
            print(f"{coin:<8} ${latest_data.close_price:,.2f}{'':<4} {change_str:<10} {latest_data.volume:,.0f}{'':<6} {age_str:<15}")
            
        except Exception as e:
            print(f"{coin:<8} {'Error':<12} {'N/A':<10} {'N/A':<12} {str(e)[:15]:<15}")
    
    print("=" * 80)
    print("✅ All major crypto coins checked!")

if __name__ == "__main__":
    check_multiple_coins()




















