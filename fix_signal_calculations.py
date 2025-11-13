#!/usr/bin/env python3
"""
Fix existing signals with proper capital-based calculations
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.models import TradingSignal

def fix_existing_signals():
    """Fix existing signals with proper capital-based calculations"""
    print("=== FIXING EXISTING SIGNALS WITH CAPITAL-BASED CALCULATIONS ===")
    
    try:
        # Get all signals
        signals = TradingSignal.objects.all().order_by('-created_at')[:20]
        print(f"Found {signals.count()} recent signals")
        
        updated_count = 0
        
        for signal in signals:
            entry_price = float(signal.entry_price)
            current_target = float(signal.target_price)
            current_stop = float(signal.stop_loss)
            
            # Calculate correct values with capital-based logic
            capital = 100  # $100 capital
            position_size = capital / entry_price
            
            if signal.signal_type.name in ['BUY', 'STRONG_BUY']:
                correct_target = entry_price + (60 / position_size)  # $60 profit
                correct_stop = entry_price - (50 / position_size)     # $50 loss
            else:
                correct_target = entry_price - (60 / position_size)  # $60 profit for sell
                correct_stop = entry_price + (50 / position_size)     # $50 loss for sell
            
            # Check if values need updating
            target_diff = abs(current_target - correct_target)
            stop_diff = abs(current_stop - correct_stop)
            
            # Update if difference is significant (>$1)
            if target_diff > 1.0 or stop_diff > 1.0:
                print(f"\nUpdating {signal.symbol.symbol} {signal.signal_type.name}:")
                print(f"  Entry: ${entry_price:.2f}")
                print(f"  Old Target: ${current_target:.2f} -> New: ${correct_target:.2f}")
                print(f"  Old Stop: ${current_stop:.2f} -> New: ${correct_stop:.2f}")
                
                # Update the signal
                signal.target_price = Decimal(str(correct_target))
                signal.stop_loss = Decimal(str(correct_stop))
                
                # Recalculate risk-reward ratio
                risk = abs(entry_price - correct_stop)
                reward = abs(correct_target - entry_price)
                signal.risk_reward_ratio = reward / risk if risk > 0 else 0
                
                signal.save()
                updated_count += 1
                
                # Verify calculations
                if signal.signal_type.name in ['BUY', 'STRONG_BUY']:
                    actual_profit = (correct_target - entry_price) * position_size
                    actual_loss = (entry_price - correct_stop) * position_size
                    print(f"  Verified Profit: ${actual_profit:.2f} (Expected: $60)")
                    print(f"  Verified Loss: ${actual_loss:.2f} (Expected: $50)")
                else:
                    actual_profit = (entry_price - correct_target) * position_size
                    actual_loss = (correct_stop - position_price) * position_size
                    print(f"  Verified Profit: ${actual_profit:.2f} (Expected: $60)")
                    print(f"  Verified Loss: ${actual_loss:.2f} (Expected: $50)")
        
        print(f"\n✅ Updated {updated_count} signals with correct capital-based calculations")
        
        # Check for duplicates
        print("\n=== CHECKING FOR DUPLICATE SIGNALS ===")
        recent_signals = TradingSignal.objects.filter(
            created_at__gte=datetime.now() - timedelta(hours=1)
        ).order_by('symbol', 'created_at')
        
        duplicates = {}
        for signal in recent_signals:
            key = f"{signal.symbol.symbol}_{signal.signal_type.name}_{float(signal.entry_price):.2f}"
            if key in duplicates:
                duplicates[key].append(signal)
            else:
                duplicates[key] = [signal]
        
        duplicate_groups = {k: v for k, v in duplicates.items() if len(v) > 1}
        
        if duplicate_groups:
            print(f"Found {len(duplicate_groups)} duplicate signal groups")
            for key, signals in duplicate_groups.items():
                print(f"\nDuplicate group: {key}")
                for signal in signals:
                    print(f"  ID: {signal.id}, Created: {signal.created_at}")
                
                # Keep the first signal, delete the rest
                signals_to_delete = signals[1:]
                for signal in signals_to_delete:
                    print(f"  Deleting duplicate signal {signal.id}")
                    signal.delete()
        else:
            print("No duplicate signals found")
        
        return True
        
    except Exception as e:
        print(f"Error fixing signals: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_existing_signals()
    if success:
        print("\n✅ Signal fixes completed successfully!")
    else:
        print("\n❌ Error occurred during signal fixes")




























































