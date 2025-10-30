#!/usr/bin/env python
"""
Script to get BTC price from the database
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

def get_btc_price():
    """Get the latest BTC price from database"""
    try:
        # Get BTC symbol
        btc_symbol = Symbol.objects.filter(symbol='BTC', symbol_type='CRYPTO').first()
        
        if not btc_symbol:
            print("❌ BTC symbol not found in database")
            return None
        
        # Get latest market data for BTC
        latest_data = MarketData.objects.filter(
            symbol=btc_symbol
        ).order_by('-timestamp').first()
        
        if not latest_data:
            print("❌ No BTC market data found in database")
            return None
        
        # Calculate data age
        now = django_timezone.now()
        data_age = now - latest_data.timestamp
        
        print("=" * 50)
        print("📊 BTC PRICE FROM DATABASE")
        print("=" * 50)
        print(f"💰 Current Price: ${latest_data.close_price:,.2f}")
        print(f"📈 Open Price:    ${latest_data.open_price:,.2f}")
        print(f"📉 Low Price:     ${latest_data.low_price:,.2f}")
        print(f"📊 High Price:     ${latest_data.high_price:,.2f}")
        print(f"📦 Volume:        {latest_data.volume:,.2f}")
        print(f"⏰ Timestamp:     {latest_data.timestamp}")
        print(f"🕐 Data Age:      {data_age}")
        print(f"📋 Timeframe:      {latest_data.timeframe}")
        print("=" * 50)
        
        # Show price change
        price_change = latest_data.close_price - latest_data.open_price
        change_percent = (price_change / latest_data.open_price) * 100
        
        if price_change > 0:
            print(f"📈 Price Change: +${price_change:,.2f} (+{change_percent:.2f}%)")
        else:
            print(f"📉 Price Change: ${price_change:,.2f} ({change_percent:.2f}%)")
        
        print("=" * 50)
        
        return {
            'price': float(latest_data.close_price),
            'open': float(latest_data.open_price),
            'high': float(latest_data.high_price),
            'low': float(latest_data.low_price),
            'volume': float(latest_data.volume),
            'timestamp': latest_data.timestamp,
            'timeframe': latest_data.timeframe,
            'data_age': data_age
        }
        
    except Exception as e:
        print(f"❌ Error getting BTC price: {e}")
        return None

def get_btc_price_history(hours=24):
    """Get BTC price history for the last N hours"""
    try:
        btc_symbol = Symbol.objects.filter(symbol='BTC', symbol_type='CRYPTO').first()
        
        if not btc_symbol:
            print("❌ BTC symbol not found in database")
            return []
        
        # Get data for the last N hours
        cutoff_time = django_timezone.now() - django_timezone.timedelta(hours=hours)
        
        historical_data = MarketData.objects.filter(
            symbol=btc_symbol,
            timestamp__gte=cutoff_time
        ).order_by('timestamp')
        
        print(f"\n📈 BTC PRICE HISTORY (Last {hours} hours)")
        print("=" * 60)
        print(f"{'Time':<20} {'Price':<12} {'Volume':<15} {'Change':<10}")
        print("-" * 60)
        
        data_points = []
        for data in historical_data:
            price_change = data.close_price - data.open_price
            change_percent = (price_change / data.open_price) * 100
            
            print(f"{data.timestamp.strftime('%Y-%m-%d %H:%M'):<20} "
                  f"${data.close_price:,.2f}{'':<4} "
                  f"{data.volume:,.0f}{'':<6} "
                  f"{change_percent:+.2f}%")
            
            data_points.append({
                'timestamp': data.timestamp,
                'price': float(data.close_price),
                'volume': float(data.volume),
                'change_percent': change_percent
            })
        
        print("=" * 60)
        print(f"📊 Total data points: {len(data_points)}")
        
        return data_points
        
    except Exception as e:
        print(f"❌ Error getting BTC price history: {e}")
        return []

if __name__ == "__main__":
    print("🔍 Fetching BTC price from database...")
    
    # Get current price
    current_price = get_btc_price()
    
    if current_price:
        # Get price history
        history = get_btc_price_history(hours=24)
        
        if history:
            # Calculate some statistics
            prices = [point['price'] for point in history]
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                
                print(f"\n📊 24-HOUR STATISTICS")
                print("=" * 30)
                print(f"📉 Lowest:  ${min_price:,.2f}")
                print(f"📈 Highest: ${max_price:,.2f}")
                print(f"📊 Average: ${avg_price:,.2f}")
                print(f"📋 Data Points: {len(prices)}")
                print("=" * 30)
    
    print("\n✅ Done!")


















