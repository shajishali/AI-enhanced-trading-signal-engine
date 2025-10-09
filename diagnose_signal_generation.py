#!/usr/bin/env python3
"""
Diagnose Signal Generation Issues

This script checks why signals are not being generated for the specified period.
"""

import os
import sys
import django
from datetime import datetime
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.strategy_backtesting_service import StrategyBacktestingService
from apps.trading.models import Symbol
from apps.data.models import MarketData
from django.utils import timezone
import pandas as pd

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('apps.signals.strategy_backtesting_service')
logger.setLevel(logging.DEBUG)


def diagnose_signal_generation():
    """Diagnose why signals are not being generated"""
    print("🔍 Diagnosing Signal Generation Issues")
    print("=" * 50)
    
    # Test with BNBUSDT for the period you're trying
    try:
        symbol = Symbol.objects.get(symbol='BNBUSDT')
        print(f"✅ Found symbol: {symbol.symbol}")
    except Symbol.DoesNotExist:
        print("❌ BNBUSDT symbol not found!")
        return
    
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2025, 1, 31)
    
    print(f"📅 Testing period: {start_date.date()} to {end_date.date()}")
    
    # Check 1: Market data availability
    print("\n🔍 Step 1: Checking market data availability...")
    total_data = MarketData.objects.filter(symbol=symbol).count()
    print(f"📊 Total market data records for {symbol.symbol}: {total_data}")
    
    if total_data == 0:
        print("❌ No market data found for BNBUSDT!")
        print("💡 Solution: Generate market data for BNBUSDT")
        return
    
    # Check 2: Data in the specified period
    start_aware = timezone.make_aware(start_date)
    end_aware = timezone.make_aware(end_date)
    
    period_data = MarketData.objects.filter(
        symbol=symbol,
        timestamp__gte=start_aware,
        timestamp__lte=end_aware
    ).count()
    
    print(f"📊 Data in period: {period_data} records")
    
    if period_data == 0:
        print("❌ No data in the specified period!")
        print("💡 Solution: Check date range or generate data for this period")
        return
    
    # Check 3: Data quality
    print("\n🔍 Step 2: Checking data quality...")
    sample_data = MarketData.objects.filter(symbol=symbol).order_by('timestamp')[:5]
    
    print("📊 Sample data points:")
    for data in sample_data:
        print(f"  {data.timestamp.date()}: Close=${data.close_price}, High=${data.high_price}, Low=${data.low_price}")
    
    # Check 4: Test the backtesting service
    print("\n🔍 Step 3: Testing backtesting service...")
    
    service = StrategyBacktestingService()
    
    # Test data retrieval
    historical_data = service._get_historical_data(symbol, start_aware, end_aware)
    print(f"📊 Historical data retrieved: {len(historical_data)} records")
    
    if historical_data.empty:
        print("❌ Historical data is empty!")
        return
    
    # Check data validation
    is_valid = service._validate_historical_data(historical_data)
    print(f"📊 Data validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    if not is_valid:
        print("❌ Data failed validation!")
        return
    
    # Check 5: Test signal generation conditions
    print("\n🔍 Step 4: Testing signal generation conditions...")
    
    # Test a few specific dates
    test_dates = [
        datetime(2021, 6, 15),
        datetime(2022, 3, 15),
        datetime(2023, 9, 15),
        datetime(2024, 6, 15)
    ]
    
    for test_date in test_dates:
        test_date_aware = timezone.make_aware(test_date)
        data_up_to_date = historical_data[historical_data.index <= test_date_aware]
        
        print(f"\n📅 Testing {test_date.date()}:")
        print(f"  Data points available: {len(data_up_to_date)}")
        
        if len(data_up_to_date) >= 50:
            # Test trend analysis
            trend_bias = service._analyze_daily_trend(data_up_to_date)
            print(f"  Trend bias: {trend_bias}")
            
            # Test market structure
            structure_signal = service._analyze_market_structure(data_up_to_date)
            print(f"  Market structure: {structure_signal}")
            
            # Test entry confirmation
            entry_confirmation = service._analyze_entry_confirmation(data_up_to_date, trend_bias)
            print(f"  Entry confirmation: {entry_confirmation}")
            
            # Check if conditions are met for signal generation
            if entry_confirmation['direction'] == 'BUY' and trend_bias == 'BULLISH':
                print("  ✅ BUY signal conditions met!")
            elif entry_confirmation['direction'] == 'SELL' and trend_bias == 'BEARISH':
                print("  ✅ SELL signal conditions met!")
            else:
                print(f"  ❌ Signal conditions not met: Direction={entry_confirmation['direction']}, Trend={trend_bias}")
        else:
            print("  ❌ Insufficient data (need 50+ points)")
    
    # Check 6: Generate signals
    print("\n🔍 Step 5: Generating signals...")
    signals = service.generate_historical_signals(symbol, start_aware, end_aware)
    print(f"📊 Generated {len(signals)} signals")
    
    if signals:
        print("✅ Signal generation is working!")
        sample = signals[0]
        print(f"📊 Sample signal: {sample.get('signal_type')} at ${sample.get('entry_price')}")
    else:
        print("❌ No signals generated - conditions not met")


def check_specific_conditions():
    """Check the specific conditions that prevent signal generation"""
    print("\n🔍 Checking Specific Conditions")
    print("=" * 50)
    
    # The conditions for signal generation are:
    # 1. BUY signal: entry_confirmation['direction'] == 'BUY' AND trend_bias == 'BULLISH'
    # 2. SELL signal: entry_confirmation['direction'] == 'SELL' AND trend_bias == 'BEARISH'
    
    print("📋 Signal Generation Conditions:")
    print("1. BUY Signal requires:")
    print("   - Entry confirmation direction = 'BUY'")
    print("   - Trend bias = 'BULLISH'")
    print("   - Risk/reward ratio >= 1.5")
    print("")
    print("2. SELL Signal requires:")
    print("   - Entry confirmation direction = 'SELL'")
    print("   - Trend bias = 'BEARISH'")
    print("   - Risk/reward ratio >= 1.5")
    print("")
    print("3. Data Requirements:")
    print("   - Minimum 50 data points for analysis")
    print("   - Valid historical data (no empty prices)")
    print("   - Proper technical indicators calculated")
    
    # Check if the issue is with the conditions being too strict
    print("\n💡 Possible Issues:")
    print("- Trend bias and entry confirmation direction don't align")
    print("- Risk/reward ratio is too low")
    print("- Technical indicators don't meet criteria")
    print("- Data quality issues")


def main():
    """Main function"""
    diagnose_signal_generation()
    check_specific_conditions()
    
    print("\n🎯 Diagnosis completed!")
    print("Check the output above to identify why signals aren't being generated.")


if __name__ == '__main__':
    main()
