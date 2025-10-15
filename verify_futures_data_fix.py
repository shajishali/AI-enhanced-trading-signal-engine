#!/usr/bin/env python3
"""
Verify Futures Data Fix
Test the corrected Binance Futures API integration to ensure stop loss verification is accurate.
"""

import os
import sys
import django
from datetime import datetime, timezone as dt_timezone
import requests
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.trading.models import Symbol
from apps.data.historical_data_manager import HistoricalDataManager
from apps.data.historical_data_service import HistoricalDataService
from apps.data.models import MarketData

def print_status(message, status="INFO"):
    """Print status message with timestamp and emoji"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "ERROR": "❌",
        "WARNING": "⚠️",
        "DEBUG": "🔍"
    }
    print(f"[{timestamp}] {status_symbols.get(status, 'ℹ️')} {message}")

def test_binance_futures_api():
    """Test Binance Futures API directly for AAVE 2021-10-01"""
    print_status("Testing Binance Futures API for AAVE 2021-10-01", "INFO")
    
    # Test the exact date from your screenshot
    start_date = datetime(2021, 10, 1, tzinfo=dt_timezone.utc)
    end_date = datetime(2021, 10, 2, tzinfo=dt_timezone.utc)
    
    start_ms = int(start_date.timestamp() * 1000)
    end_ms = int(end_date.timestamp() * 1000)
    
    # Test Futures API
    futures_url = "https://fapi.binance.com/fapi/v1/klines"
    futures_params = {
        'symbol': 'AAVEUSDT',
        'interval': '1d',
        'startTime': start_ms,
        'endTime': end_ms,
        'limit': 1000
    }
    
    try:
        print_status("Fetching from Binance Futures API...", "DEBUG")
        response = requests.get(futures_url, params=futures_params, timeout=30)
        response.raise_for_status()
        futures_data = response.json()
        
        if futures_data:
            kline = futures_data[0]  # Should be the 2021-10-01 candle
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            timestamp = datetime.fromtimestamp(kline[0] / 1000, tz=dt_timezone.utc)
            
            print_status(f"Futures API Result for {timestamp.date()}:", "SUCCESS")
            print_status(f"  Open: ${open_price:.2f}", "INFO")
            print_status(f"  High: ${high_price:.2f}", "INFO")
            print_status(f"  Low: ${low_price:.2f}", "INFO")
            print_status(f"  Close: ${close_price:.2f}", "INFO")
            
            # Check if stop loss would have been hit
            stop_loss = 427.2204  # From your screenshot
            if low_price <= stop_loss:
                print_status(f"❌ STOP LOSS WOULD BE HIT: Low ${low_price:.2f} <= Stop ${stop_loss:.2f}", "ERROR")
            else:
                print_status(f"✅ STOP LOSS NOT HIT: Low ${low_price:.2f} > Stop ${stop_loss:.2f}", "SUCCESS")
                
            return {
                'timestamp': timestamp,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'stop_hit': low_price <= stop_loss
            }
        else:
            print_status("No data returned from Futures API", "ERROR")
            return None
            
    except Exception as e:
        print_status(f"Error fetching from Futures API: {e}", "ERROR")
        return None

def test_spot_api_for_comparison():
    """Test Binance Spot API for comparison"""
    print_status("Testing Binance Spot API for comparison", "INFO")
    
    start_date = datetime(2021, 10, 1, tzinfo=dt_timezone.utc)
    end_date = datetime(2021, 10, 2, tzinfo=dt_timezone.utc)
    
    start_ms = int(start_date.timestamp() * 1000)
    end_ms = int(end_date.timestamp() * 1000)
    
    # Test Spot API
    spot_url = "https://api.binance.com/api/v3/klines"
    spot_params = {
        'symbol': 'AAVEUSDT',
        'interval': '1d',
        'startTime': start_ms,
        'endTime': end_ms,
        'limit': 1000
    }
    
    try:
        print_status("Fetching from Binance Spot API...", "DEBUG")
        response = requests.get(spot_url, params=spot_params, timeout=30)
        response.raise_for_status()
        spot_data = response.json()
        
        if spot_data:
            kline = spot_data[0]  # Should be the 2021-10-01 candle
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            timestamp = datetime.fromtimestamp(kline[0] / 1000, tz=dt_timezone.utc)
            
            print_status(f"Spot API Result for {timestamp.date()}:", "SUCCESS")
            print_status(f"  Open: ${open_price:.2f}", "INFO")
            print_status(f"  High: ${high_price:.2f}", "INFO")
            print_status(f"  Low: ${low_price:.2f}", "INFO")
            print_status(f"  Close: ${close_price:.2f}", "INFO")
            
            # Check if stop loss would have been hit
            stop_loss = 427.2204  # From your screenshot
            if low_price <= stop_loss:
                print_status(f"❌ STOP LOSS WOULD BE HIT: Low ${low_price:.2f} <= Stop ${stop_loss:.2f}", "ERROR")
            else:
                print_status(f"✅ STOP LOSS NOT HIT: Low ${low_price:.2f} > Stop ${stop_loss:.2f}", "SUCCESS")
                
            return {
                'timestamp': timestamp,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'stop_hit': low_price <= stop_loss
            }
        else:
            print_status("No data returned from Spot API", "ERROR")
            return None
            
    except Exception as e:
        print_status(f"Error fetching from Spot API: {e}", "ERROR")
        return None

def test_updated_services():
    """Test the updated historical data services"""
    print_status("Testing updated Historical Data Services", "INFO")
    
    try:
        # Test HistoricalDataManager
        print_status("Testing HistoricalDataManager...", "DEBUG")
        manager = HistoricalDataManager()
        print_status(f"Manager API Base: {manager.binance_api_base}", "INFO")
        
        # Test HistoricalDataService
        print_status("Testing HistoricalDataService...", "DEBUG")
        service = HistoricalDataService()
        print_status(f"Service API Base: {service.binance_api}", "INFO")
        
        # Test with AAVE symbol
        print_status("Testing with AAVE symbol...", "DEBUG")
        aave_symbol, created = Symbol.objects.get_or_create(symbol='AAVE')
        
        start_date = datetime(2021, 10, 1, tzinfo=dt_timezone.utc)
        end_date = datetime(2021, 10, 2, tzinfo=dt_timezone.utc)
        
        # Test service data fetching
        historical_data = service.get_historical_data('AAVE', start_date, end_date, '1d')
        
        if historical_data:
            print_status(f"Service returned {len(historical_data)} data points", "SUCCESS")
            for data_point in historical_data:
                print_status(f"  {data_point['timestamp'].date()}: O=${data_point['open']:.2f} H=${data_point['high']:.2f} L=${data_point['low']:.2f} C=${data_point['close']:.2f}", "INFO")
        else:
            print_status("Service returned no data", "WARNING")
            
        return True
        
    except Exception as e:
        print_status(f"Error testing services: {e}", "ERROR")
        return False

def clear_existing_data():
    """Clear existing AAVE data to test fresh fetch"""
    print_status("Clearing existing AAVE data for fresh test", "INFO")
    
    try:
        aave_symbol = Symbol.objects.get(symbol='AAVE')
        
        # Clear MarketData for AAVE
        deleted_count = MarketData.objects.filter(symbol=aave_symbol).delete()[0]
        print_status(f"Deleted {deleted_count} existing MarketData records for AAVE", "SUCCESS")
        
        return True
        
    except Symbol.DoesNotExist:
        print_status("AAVE symbol not found, will be created", "INFO")
        return True
    except Exception as e:
        print_status(f"Error clearing data: {e}", "ERROR")
        return False

def main():
    """Main verification function"""
    print_status("Starting Futures Data Fix Verification", "INFO")
    print_status("=" * 60, "INFO")
    
    # Test 1: Direct API comparison
    print_status("TEST 1: Direct API Comparison", "INFO")
    print_status("-" * 40, "INFO")
    
    futures_result = test_binance_futures_api()
    spot_result = test_spot_api_for_comparison()
    
    if futures_result and spot_result:
        print_status("COMPARISON RESULTS:", "INFO")
        print_status(f"Futures Low: ${futures_result['low']:.2f}", "INFO")
        print_status(f"Spot Low: ${spot_result['low']:.2f}", "INFO")
        print_status(f"Difference: ${abs(futures_result['low'] - spot_result['low']):.2f}", "INFO")
        
        if futures_result['stop_hit'] != spot_result['stop_hit']:
            print_status("⚠️ DIFFERENT STOP LOSS RESULTS!", "WARNING")
            print_status(f"Futures: {'HIT' if futures_result['stop_hit'] else 'NOT HIT'}", "INFO")
            print_status(f"Spot: {'HIT' if spot_result['stop_hit'] else 'NOT HIT'}", "INFO")
        else:
            print_status("✅ Consistent stop loss results", "SUCCESS")
    
    print_status("", "INFO")
    
    # Test 2: Updated services
    print_status("TEST 2: Updated Services", "INFO")
    print_status("-" * 40, "INFO")
    
    services_ok = test_updated_services()
    
    print_status("", "INFO")
    
    # Test 3: Fresh data fetch
    print_status("TEST 3: Fresh Data Fetch", "INFO")
    print_status("-" * 40, "INFO")
    
    clear_ok = clear_existing_data()
    
    if clear_ok:
        print_status("Testing fresh data fetch with Futures API...", "INFO")
        try:
            manager = HistoricalDataManager()
            aave_symbol, created = Symbol.objects.get_or_create(symbol='AAVE')
            
            start_date = datetime(2021, 10, 1, tzinfo=dt_timezone.utc)
            end_date = datetime(2021, 10, 2, tzinfo=dt_timezone.utc)
            
            success = manager.fetch_complete_historical_data(aave_symbol, '1d', start_date, end_date)
            
            if success:
                print_status("✅ Fresh data fetch successful", "SUCCESS")
                
                # Verify the data
                market_data = MarketData.objects.filter(
                    symbol=aave_symbol,
                    timestamp__gte=start_date,
                    timestamp__lt=end_date
                ).first()
                
                if market_data:
                    print_status(f"Stored data: O=${market_data.open_price} H=${market_data.high_price} L=${market_data.low_price} C=${market_data.close_price}", "INFO")
                    
                    stop_loss = 427.2204
                    if float(market_data.low_price) <= stop_loss:
                        print_status(f"❌ STORED DATA SHOWS STOP HIT: Low ${market_data.low_price} <= Stop ${stop_loss}", "ERROR")
                    else:
                        print_status(f"✅ STORED DATA SHOWS NO STOP HIT: Low ${market_data.low_price} > Stop ${stop_loss}", "SUCCESS")
                else:
                    print_status("No market data found after fetch", "ERROR")
            else:
                print_status("❌ Fresh data fetch failed", "ERROR")
                
        except Exception as e:
            print_status(f"Error in fresh data fetch: {e}", "ERROR")
    
    print_status("", "INFO")
    print_status("=" * 60, "INFO")
    print_status("Verification Complete", "SUCCESS")

if __name__ == "__main__":
    main()
