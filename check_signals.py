#!/usr/bin/env python3
"""
Check Signals Status
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.models import TradingSignal

def check_signals():
    print('🔍 Checking signals status...')
    
    # Check all signals
    all_signals = TradingSignal.objects.all()
    print(f'📊 Total signals: {all_signals.count()}')
    
    # Check backtesting signals
    backtesting_signals = TradingSignal.objects.filter(metadata__is_backtesting=True)
    print(f'🔍 Backtesting signals: {backtesting_signals.count()}')
    
    # Check non-backtesting signals
    non_backtesting = TradingSignal.objects.exclude(metadata__is_backtesting=True)
    print(f'✅ Non-backtesting signals: {non_backtesting.count()}')
    
    # Check valid signals
    valid_signals = non_backtesting.filter(is_valid=True)
    print(f'✅ Valid non-backtesting signals: {valid_signals.count()}')
    
    if valid_signals.exists():
        print('📊 Recent valid signals:')
        for signal in valid_signals.order_by('-created_at')[:5]:
            print(f'  {signal.created_at.strftime("%Y-%m-%d %H:%M")}: {signal.symbol.symbol} {signal.signal_type.name} - ${signal.entry_price}')
            print(f'    Is valid: {signal.is_valid}')
            print(f'    Metadata: {signal.metadata}')
            print()
    else:
        print('❌ No valid non-backtesting signals found')
        
        # Check what's wrong
        if non_backtesting.exists():
            print('📊 Non-backtesting signals (but not valid):')
            for signal in non_backtesting.order_by('-created_at')[:3]:
                print(f'  {signal.created_at.strftime("%Y-%m-%d %H:%M")}: {signal.symbol.symbol} {signal.signal_type.name} - ${signal.entry_price}')
                print(f'    Is valid: {signal.is_valid}')
                print(f'    Metadata: {signal.metadata}')
                print()

if __name__ == '__main__':
    check_signals()
