#!/usr/bin/env python3
"""
Detailed Stop Loss Investigation
Investigate the exact stop loss calculation and compare with TradingView data.
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
from apps.signals.models import TradingSignal

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

def get_tradingview_equivalent_data():
    """Get data that matches TradingView's AAVEUSDT Perpetual Contract"""
    print_status("Fetching TradingView equivalent data (Binance Futures PERP)", "INFO")
    
    # Test multiple timeframes around 2021-10-01
    dates_to_test = [
        datetime(2021, 9, 30, tzinfo=dt_timezone.utc),
        datetime(2021, 10, 1, tzinfo=dt_timezone.utc),
        datetime(2021, 10, 2, tzinfo=dt_timezone.utc),
    ]
    
    futures_url = "https://fapi.binance.com/fapi/v1/klines"
    
    for test_date in dates_to_test:
        start_ms = int(test_date.timestamp() * 1000)
        end_ms = int((test_date.timestamp() + 86400) * 1000)  # +1 day
        
        params = {
            'symbol': 'AAVEUSDT',
            'interval': '1d',
            'startTime': start_ms,
            'endTime': end_ms,
            'limit': 1
        }
        
        try:
            response = requests.get(futures_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data:
                kline = data[0]
                timestamp = datetime.fromtimestamp(kline[0] / 1000, tz=dt_timezone.utc)
                open_price = float(kline[1])
                high_price = float(kline[2])
                low_price = float(kline[3])
                close_price = float(kline[4])
                
                print_status(f"{timestamp.date()}: O=${open_price:.2f} H=${high_price:.2f} L=${low_price:.2f} C=${close_price:.2f}", "INFO")
                
                # Check against the stop loss from your screenshot
                stop_loss = 427.2204
                if low_price <= stop_loss:
                    print_status(f"  ❌ STOP HIT: Low ${low_price:.2f} <= Stop ${stop_loss:.2f}", "ERROR")
                else:
                    print_status(f"  ✅ NO STOP: Low ${low_price:.2f} > Stop ${stop_loss:.2f}", "SUCCESS")
                    
        except Exception as e:
            print_status(f"Error fetching data for {test_date.date()}: {e}", "ERROR")

def check_existing_signals():
    """Check existing signals in database for AAVE around 2021-10-01"""
    print_status("Checking existing signals in database", "INFO")
    
    try:
        # Look for AAVE signals around 2021-10-01
        start_date = datetime(2021, 9, 30, tzinfo=dt_timezone.utc)
        end_date = datetime(2021, 10, 2, tzinfo=dt_timezone.utc)
        
        aave_signals = TradingSignal.objects.filter(
            symbol__symbol='AAVE',
            created_at__gte=start_date,
            created_at__lte=end_date
        ).order_by('created_at')
        
        print_status(f"Found {aave_signals.count()} AAVE signals in date range", "INFO")
        
        for signal in aave_signals:
            print_status(f"Signal {signal.id}:", "INFO")
            print_status(f"  Date: {signal.created_at.date()}", "INFO")
            print_status(f"  Type: {signal.signal_type}", "INFO")
            print_status(f"  Entry: ${signal.entry_price}", "INFO")
            print_status(f"  Target: ${signal.target_price}", "INFO")
            print_status(f"  Stop Loss: ${signal.stop_loss}", "INFO")
            print_status(f"  Status: {signal.status}", "INFO")
            
            # Check if this matches your screenshot data
            if (signal.created_at.date() == datetime(2021, 10, 1).date() and 
                float(signal.entry_price) == 464.37 and
                float(signal.stop_loss) == 427.2204):
                print_status("  🎯 THIS MATCHES YOUR SCREENSHOT!", "SUCCESS")
                
                # Calculate what the stop loss should be based on 8% rule
                entry_price = float(signal.entry_price)
                calculated_stop = entry_price * (1 - 0.08)  # 8% stop loss
                print_status(f"  Calculated 8% stop: ${calculated_stop:.2f}", "INFO")
                print_status(f"  Actual stop: ${signal.stop_loss}", "INFO")
                print_status(f"  Difference: ${abs(calculated_stop - float(signal.stop_loss)):.2f}", "INFO")
                
    except Exception as e:
        print_status(f"Error checking signals: {e}", "ERROR")

def verify_stop_loss_calculation():
    """Verify the stop loss calculation logic"""
    print_status("Verifying stop loss calculation logic", "INFO")
    
    # From your screenshot: Entry 464.37, Stop 427.2204
    entry_price = 464.37
    actual_stop = 427.2204
    
    # Calculate percentage
    stop_percentage = (entry_price - actual_stop) / entry_price * 100
    print_status(f"Entry Price: ${entry_price:.2f}", "INFO")
    print_status(f"Stop Loss: ${actual_stop:.2f}", "INFO")
    print_status(f"Stop Loss Percentage: {stop_percentage:.2f}%", "INFO")
    
    # Check if this matches the 8% rule from your strategy
    expected_8_percent = entry_price * (1 - 0.08)
    print_status(f"Expected 8% stop: ${expected_8_percent:.2f}", "INFO")
    print_status(f"Difference from 8%: ${abs(actual_stop - expected_8_percent):.2f}", "INFO")
    
    # Check if this matches the 15% rule (which would be wrong)
    expected_15_percent = entry_price * (1 - 0.15)
    print_status(f"Expected 15% stop: ${expected_15_percent:.2f}", "INFO")
    print_status(f"Difference from 15%: ${abs(actual_stop - expected_15_percent):.2f}", "INFO")

def check_timezone_issues():
    """Check for timezone boundary issues"""
    print_status("Checking timezone boundary issues", "INFO")
    
    # Test different timezone interpretations
    utc_date = datetime(2021, 10, 1, tzinfo=dt_timezone.utc)
    
    print_status(f"UTC Date: {utc_date}", "INFO")
    print_status(f"UTC Timestamp: {utc_date.timestamp()}", "INFO")
    print_status(f"UTC Milliseconds: {int(utc_date.timestamp() * 1000)}", "INFO")
    
    # Test if the issue is with day boundaries
    # Binance Futures uses UTC for daily candles
    # But maybe the backtest is using local timezone
    
    # Check what happens if we shift by timezone
    import pytz
    
    # Test different timezones
    timezones_to_test = [
        ('UTC', dt_timezone.utc),
        ('EST', pytz.timezone('US/Eastern')),
        ('PST', pytz.timezone('US/Pacific')),
    ]
    
    for tz_name, tz in timezones_to_test:
        local_date = utc_date.astimezone(tz)
        print_status(f"{tz_name} Date: {local_date.date()}", "INFO")
        
        # If local date is different, this could cause the issue
        if local_date.date() != utc_date.date():
            print_status(f"⚠️ TIMEZONE MISMATCH: UTC {utc_date.date()} vs {tz_name} {local_date.date()}", "WARNING")

def main():
    """Main investigation function"""
    print_status("Starting Detailed Stop Loss Investigation", "INFO")
    print_status("=" * 60, "INFO")
    
    # Investigation 1: TradingView equivalent data
    print_status("INVESTIGATION 1: TradingView Equivalent Data", "INFO")
    print_status("-" * 50, "INFO")
    get_tradingview_equivalent_data()
    
    print_status("", "INFO")
    
    # Investigation 2: Existing signals
    print_status("INVESTIGATION 2: Existing Signals", "INFO")
    print_status("-" * 50, "INFO")
    check_existing_signals()
    
    print_status("", "INFO")
    
    # Investigation 3: Stop loss calculation
    print_status("INVESTIGATION 3: Stop Loss Calculation", "INFO")
    print_status("-" * 50, "INFO")
    verify_stop_loss_calculation()
    
    print_status("", "INFO")
    
    # Investigation 4: Timezone issues
    print_status("INVESTIGATION 4: Timezone Issues", "INFO")
    print_status("-" * 50, "INFO")
    check_timezone_issues()
    
    print_status("", "INFO")
    print_status("=" * 60, "INFO")
    print_status("Investigation Complete", "SUCCESS")

if __name__ == "__main__":
    main()













