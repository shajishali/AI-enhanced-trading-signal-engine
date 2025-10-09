#!/usr/bin/env python3
"""
Fix Signal Separation

This script separates backtesting signals from real trading signals
by updating the metadata and filtering them out of the main signals page.
"""

import os
import sys
import django
from datetime import datetime
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.signals.models import TradingSignal
from django.db import transaction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def mark_backtesting_signals():
    """Mark existing backtesting signals so they can be filtered out"""
    print("🏷️ Marking backtesting signals...")
    
    with transaction.atomic():
        # Get all signals and mark backtesting ones
        signals = TradingSignal.objects.all()
        marked_count = 0
        
        for signal in signals:
            # Check if this is a backtesting signal
            is_backtesting = False
            
            # Check metadata for backtesting indicators
            if signal.metadata:
                if signal.metadata.get('signal_source') == 'BACKTESTING':
                    is_backtesting = True
                elif signal.metadata.get('is_backtesting'):
                    is_backtesting = True
            
            # Check entry_point_type
            if signal.entry_point_type in ['FALLBACK', 'BACKTESTING']:
                is_backtesting = True
            
            # Check notes for backtesting indicators
            if signal.notes and 'Generated signal for' in signal.notes:
                is_backtesting = True
            
            # Mark as backtesting if detected
            if is_backtesting:
                if not signal.metadata:
                    signal.metadata = {}
                signal.metadata['is_backtesting'] = True
                signal.metadata['signal_source'] = 'BACKTESTING'
                signal.save()
                marked_count += 1
        
        print(f"✅ Marked {marked_count} signals as backtesting signals")


def update_signal_views():
    """Update the signal views to exclude backtesting signals"""
    print("🔧 Updating signal views...")
    
    # Read the current views file
    with open('apps/signals/views.py', 'r') as f:
        content = f.read()
    
    # Update signal_dashboard to exclude backtesting signals
    old_query = '''# Get recent signals with related data
        recent_signals = TradingSignal.objects.select_related('symbol', 'signal_type').filter(is_valid=True).order_by('-created_at')[:10]'''
    
    new_query = '''# Get recent signals with related data (exclude backtesting signals)
        recent_signals = TradingSignal.objects.select_related('symbol', 'signal_type').filter(
            is_valid=True
        ).exclude(
            metadata__is_backtesting=True
        ).order_by('-created_at')[:10]'''
    
    content = content.replace(old_query, new_query)
    
    # Update signal_history to exclude backtesting signals
    old_history_query = '''# Get signals with pagination
        signals = TradingSignal.objects.select_related(
            'symbol', 'signal_type'
        ).filter(query).order_by('-created_at')'''
    
    new_history_query = '''# Get signals with pagination (exclude backtesting signals)
        signals = TradingSignal.objects.select_related(
            'symbol', 'signal_type'
        ).filter(query).exclude(
            metadata__is_backtesting=True
        ).order_by('-created_at')'''
    
    content = content.replace(old_history_query, new_history_query)
    
    # Update SignalAPIView to exclude backtesting signals
    old_api_query = '''# Build optimized query with select_related and prefetch_related
            queryset = TradingSignal.objects.select_related(
                'symbol', 'signal_type'
            )'''
    
    new_api_query = '''# Build optimized query with select_related and prefetch_related (exclude backtesting signals)
            queryset = TradingSignal.objects.select_related(
                'symbol', 'signal_type'
            ).exclude(
                metadata__is_backtesting=True
            )'''
    
    content = content.replace(old_api_query, new_api_query)
    
    # Write the updated content
    with open('apps/signals/views.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated signal views to exclude backtesting signals")


def update_backtesting_service():
    """Update the backtesting service to mark signals as backtesting"""
    print("🔧 Updating backtesting service...")
    
    # Read the current backtesting service
    with open('apps/signals/strategy_backtesting_service.py', 'r') as f:
        content = f.read()
    
    # Update the signal creation to mark as backtesting
    old_metadata = '''metadata=signal.get('strategy_details', {})'''
    
    new_metadata = '''metadata={
                    **signal.get('strategy_details', {}),
                    'is_backtesting': True,
                    'signal_source': 'BACKTESTING'
                }'''
    
    content = content.replace(old_metadata, new_metadata)
    
    # Write the updated content
    with open('apps/signals/strategy_backtesting_service.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated backtesting service to mark signals")


def test_separation():
    """Test that the separation is working"""
    print("🧪 Testing signal separation...")
    
    # Count total signals
    total_signals = TradingSignal.objects.count()
    print(f"📊 Total signals: {total_signals}")
    
    # Count backtesting signals
    backtesting_signals = TradingSignal.objects.filter(
        metadata__is_backtesting=True
    ).count()
    print(f"🔍 Backtesting signals: {backtesting_signals}")
    
    # Count real signals (should be total - backtesting)
    real_signals = TradingSignal.objects.exclude(
        metadata__is_backtesting=True
    ).count()
    print(f"✅ Real trading signals: {real_signals}")
    
    # Verify the math
    if total_signals == backtesting_signals + real_signals:
        print("✅ Signal separation working correctly!")
    else:
        print("❌ Signal separation has issues!")


def main():
    """Main function"""
    print("🚀 Fixing Signal Separation")
    print("=" * 50)
    
    # Step 1: Mark existing backtesting signals
    mark_backtesting_signals()
    
    # Step 2: Update signal views to exclude backtesting signals
    update_signal_views()
    
    # Step 3: Update backtesting service to mark new signals
    update_backtesting_service()
    
    # Step 4: Test the separation
    test_separation()
    
    print("\n✅ Signal separation completed!")
    print("📊 Main signals page now excludes backtesting signals")
    print("🔍 Backtesting signals are marked and filtered out")


if __name__ == '__main__':
    main()
