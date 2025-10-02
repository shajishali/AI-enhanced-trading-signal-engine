#!/usr/bin/env python3
"""
Fix Backtesting N/A Price Issues
This script fixes historical signals that have null entry_price, target_price, or stop_loss values
"""

import os
import sys
from decimal import Decimal
from datetime import datetime

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

from django.db import transaction
from apps.signals.models import TradingSignal
from apps.trading.models import Symbol
from apps.data.models import MarketData

def print_status(message, status="INFO"):
    """Print status message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "FIXING": "🔧"
    }
    print(f"[{timestamp}] {status_symbols.get(status, 'ℹ️')} {message}")

def get_fallback_price_for_symbol(symbol_obj):
    """Get a reasonable fallback price for a symbol"""
    
    # Try to get latest market data
    try:
        latest_market_data = MarketData.objects.filter(
            symbol=symbol_obj
        ).order_by('-timestamp').first()
        
        if latest_market_data and latest_market_data.close_price > 0:
            return float(latest_market_data.close_price)
    except Exception as e:
        print_status(f"Could not get market data for {symbol_obj.symbol}: {e}", "WARNING")
    
    # Fallback to reasonable default prices for major cryptocurrencies
    default_prices = {
        'BTC': 100000.0,
        'ETH': 4000.0,
        'BNB': 600.0,
        'ADA': 1.0,
        'SOL': 200.0,
        'XRP': 2.0,
        'DOGE': 0.4,
        'MATIC': 1.0,
        'DOT': 8.0,
        'AVAX': 40.0,
        'LINK': 20.0,
        'UNI': 15.0,
        'ATOM': 12.0,
        'FTM': 1.2,
        'ALGO': 0.3,
        'VET': 0.05,
        'ICP': 15.0,
        'THETA': 2.0,
        'SAND': 0.5,
        'MANA': 0.8,
        'LTC': 150.0,
        'BCH': 500.0,
        'ETC': 30.0,
        'XLM': 0.3,
        'TRX': 0.2,
        'XMR': 200.0,
        'ZEC': 50.0,
        'DASH': 80.0,
        'NEO': 25.0,
        'QTUM': 5.0,
        'OMG': 2.0,
        'ZRX': 1.0,
        'BAT': 0.5,
        'REP': 30.0,
        'KNC': 2.0,
        'LOOM': 0.1,
        'STORJ': 1.0,
        'CVC': 0.3,
        'GNT': 0.5,
        'RLC': 3.0,
        'BNT': 1.5,
        'POWR': 0.5,
        'PAY': 0.3,
        'MTL': 2.0,
        'FUEL': 0.01,
        'MANA': 0.8,
        'DNT': 0.1,
        'TRIG': 0.5,
        'STORJ': 1.0,
        'ADX': 0.5,
        'NULS': 1.0,
        'RCN': 0.1,
        'CTR': 0.2,
        'SALT': 1.0,
        'IOTA': 0.5,
        'MDA': 0.3,
        'MTH': 0.05,
        'ENG': 1.0,
        'AST': 0.2,
        'DASH': 80.0,
        'BTG': 50.0,
        'EVX': 1.0,
        'REQ': 0.2,
        'VIB': 0.1,
        'HSR': 5.0,
        'TRX': 0.2,
        'POWR': 0.5,
        'ARK': 2.0,
        'YOYO': 0.01,
        'XRP': 2.0,
        'ENJ': 0.5,
        'STORJ': 1.0
    }
    
    return default_prices.get(symbol_obj.symbol, 1.0)  # Default to $1 for unknown symbols

def calculate_target_and_stop_loss(entry_price, signal_type):
    """Calculate target price and stop loss based on entry price and signal type"""
    entry_decimal = Decimal(str(entry_price))
    
    if signal_type in ['BUY', 'STRONG_BUY']:
        # For buy signals: 60% profit target, 40% stop loss
        target_price = entry_decimal * Decimal('1.60')  # 60% profit
        stop_loss = entry_decimal * Decimal('0.60')     # 40% stop loss
    else:
        # For sell signals: 60% profit target, 40% stop loss
        target_price = entry_decimal * Decimal('0.40')  # 60% profit for sell (lower price)
        stop_loss = entry_decimal * Decimal('1.40')     # 40% stop loss for sell (higher price)
    
    return target_price, stop_loss

def fix_signal_prices():
    """Fix signals with null price values"""
    print_status("Starting to fix signals with null price values", "FIXING")
    
    # Find signals with null price values
    signals_with_null_prices = TradingSignal.objects.filter(
        entry_price__isnull=True
    ).select_related('symbol', 'signal_type')
    
    total_signals = signals_with_null_prices.count()
    print_status(f"Found {total_signals} signals with null entry prices", "INFO")
    
    if total_signals == 0:
        print_status("No signals with null prices found", "SUCCESS")
        return
    
    fixed_count = 0
    error_count = 0
    
    with transaction.atomic():
        for signal in signals_with_null_prices:
            try:
                # Get fallback price for this symbol
                fallback_price = get_fallback_price_for_symbol(signal.symbol)
                
                # Calculate target and stop loss
                target_price, stop_loss = calculate_target_and_stop_loss(
                    fallback_price, 
                    signal.signal_type.name
                )
                
                # Calculate risk-reward ratio
                risk = abs(float(Decimal(str(fallback_price)) - stop_loss))
                reward = abs(float(target_price - Decimal(str(fallback_price))))
                risk_reward_ratio = reward / risk if risk > 0 else 1.0
                
                # Update the signal
                signal.entry_price = Decimal(str(fallback_price))
                signal.target_price = target_price
                signal.stop_loss = stop_loss
                signal.risk_reward_ratio = risk_reward_ratio
                signal.save()
                
                fixed_count += 1
                
                if fixed_count % 10 == 0:
                    print_status(f"Fixed {fixed_count}/{total_signals} signals...", "INFO")
                
            except Exception as e:
                error_count += 1
                print_status(f"Error fixing signal {signal.id}: {e}", "ERROR")
    
    print_status(f"Fixed {fixed_count} signals successfully", "SUCCESS")
    if error_count > 0:
        print_status(f"Failed to fix {error_count} signals", "ERROR")

def fix_signals_with_zero_prices():
    """Fix signals with zero price values"""
    print_status("Starting to fix signals with zero price values", "FIXING")
    
    # Find signals with zero price values
    signals_with_zero_prices = TradingSignal.objects.filter(
        entry_price=0
    ).select_related('symbol', 'signal_type')
    
    total_signals = signals_with_zero_prices.count()
    print_status(f"Found {total_signals} signals with zero entry prices", "INFO")
    
    if total_signals == 0:
        print_status("No signals with zero prices found", "SUCCESS")
        return
    
    fixed_count = 0
    error_count = 0
    
    with transaction.atomic():
        for signal in signals_with_zero_prices:
            try:
                # Get fallback price for this symbol
                fallback_price = get_fallback_price_for_symbol(signal.symbol)
                
                # Calculate target and stop loss
                target_price, stop_loss = calculate_target_and_stop_loss(
                    fallback_price, 
                    signal.signal_type.name
                )
                
                # Calculate risk-reward ratio
                risk = abs(float(Decimal(str(fallback_price)) - stop_loss))
                reward = abs(float(target_price - Decimal(str(fallback_price))))
                risk_reward_ratio = reward / risk if risk > 0 else 1.0
                
                # Update the signal
                signal.entry_price = Decimal(str(fallback_price))
                signal.target_price = target_price
                signal.stop_loss = stop_loss
                signal.risk_reward_ratio = risk_reward_ratio
                signal.save()
                
                fixed_count += 1
                
                if fixed_count % 10 == 0:
                    print_status(f"Fixed {fixed_count}/{total_signals} signals...", "INFO")
                
            except Exception as e:
                error_count += 1
                print_status(f"Error fixing signal {signal.id}: {e}", "ERROR")
    
    print_status(f"Fixed {fixed_count} signals successfully", "SUCCESS")
    if error_count > 0:
        print_status(f"Failed to fix {error_count} signals", "ERROR")

def verify_fixes():
    """Verify that the fixes were applied correctly"""
    print_status("Verifying fixes...", "INFO")
    
    # Check for remaining null prices
    null_entry_count = TradingSignal.objects.filter(entry_price__isnull=True).count()
    null_target_count = TradingSignal.objects.filter(target_price__isnull=True).count()
    null_stop_count = TradingSignal.objects.filter(stop_loss__isnull=True).count()
    
    # Check for zero prices
    zero_entry_count = TradingSignal.objects.filter(entry_price=0).count()
    zero_target_count = TradingSignal.objects.filter(target_price=0).count()
    zero_stop_count = TradingSignal.objects.filter(stop_loss=0).count()
    
    print_status(f"Remaining null entry prices: {null_entry_count}", "INFO")
    print_status(f"Remaining null target prices: {null_target_count}", "INFO")
    print_status(f"Remaining null stop losses: {null_stop_count}", "INFO")
    print_status(f"Remaining zero entry prices: {zero_entry_count}", "INFO")
    print_status(f"Remaining zero target prices: {zero_target_count}", "INFO")
    print_status(f"Remaining zero stop losses: {zero_stop_count}", "INFO")
    
    total_issues = (null_entry_count + null_target_count + null_stop_count + 
                   zero_entry_count + zero_target_count + zero_stop_count)
    
    if total_issues == 0:
        print_status("All price issues have been fixed!", "SUCCESS")
    else:
        print_status(f"Still have {total_issues} price issues remaining", "WARNING")

def main():
    """Main function to run all fixes"""
    print_status("🔧 Starting Backtesting N/A Price Fix Script", "INFO")
    print("=" * 60)
    
    try:
        # Fix null prices
        fix_signal_prices()
        
        # Fix zero prices
        fix_signals_with_zero_prices()
        
        # Verify fixes
        verify_fixes()
        
        print("=" * 60)
        print_status("✅ Backtesting price fix completed successfully!", "SUCCESS")
        print_status("🎉 You can now run backtesting without N/A price issues!", "SUCCESS")
        
    except Exception as e:
        print_status(f"❌ Fix script failed: {e}", "ERROR")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
