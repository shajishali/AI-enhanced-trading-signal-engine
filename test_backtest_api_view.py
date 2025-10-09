#!/usr/bin/env python3
"""
Test the entire BacktestAPIView to identify the 500 error
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.contrib.auth.models import User
from apps.trading.models import Symbol
from apps.signals.services import HistoricalSignalService
from apps.signals.models import BacktestSearch
from datetime import datetime
from django.utils import timezone
import json

def test_backtest_api_view():
    """Test the entire BacktestAPIView logic to identify the 500 error"""
    print("Testing BacktestAPIView logic...")
    
    # Create test user
    user = User.objects.create_user(
        username='api_view_user',
        email='api_view@test.com',
        password='testpass123'
    )
    
    try:
        # Get XRP symbol
        symbol = Symbol.objects.get(symbol='XRP')
        
        # Simulate the API data with past dates
        data = {
            'action': 'generate_signals',
            'symbol': 'XRP',
            'start_date': '2024-09-01T00:00:00Z',
            'end_date': '2024-10-01T23:59:59Z',
            'search_name': 'API Test Search',
            'notes': 'API test notes'
        }
        
        print(f"Testing with data: {data}")
        
        # Parse dates (same as in the API view)
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        
        print(f"Parsed dates:")
        print(f"  Start date: {start_date} (tzinfo: {start_date.tzinfo})")
        print(f"  End date: {end_date} (tzinfo: {end_date.tzinfo})")
        
        # Initialize historical signal service
        historical_service = HistoricalSignalService()
        
        # Validate date range
        is_valid, error_msg = historical_service.validate_date_range(start_date, end_date)
        print(f"Date validation: {is_valid}, error: {error_msg}")
        
        if not is_valid:
            print(f"❌ Date validation failed: {error_msg}")
            return False
        
        # Generate historical signals
        print("Generating signals...")
        signals = historical_service.generate_signals_for_period(symbol, start_date, end_date)
        print(f"Generated {len(signals)} signals")
        
        # Save search history
        print("Saving search history...")
        search, created = BacktestSearch.objects.get_or_create(
            user=user,
            symbol=symbol,
            start_date=start_date.date(),
            end_date=end_date.date(),
            defaults={
                'signals_generated': len(signals),
                'search_name': data.get('search_name', ''),
                'notes': data.get('notes', '')
            }
        )
        print(f"Search saved: created={created}, id={search.id}")
        
        # Serialize signals
        print("Serializing signals...")
        signals_data = []
        for signal in signals:
            signal_data = {
                'id': signal.id,
                'symbol': signal.symbol.symbol,
                'signal_type': signal.signal_type.name,
                'strength': signal.strength,
                'confidence_score': signal.confidence_score,
                'confidence_level': signal.confidence_level,
                'entry_price': float(signal.entry_price) if signal.entry_price else None,
                'target_price': float(signal.target_price) if signal.target_price else None,
                'stop_loss': float(signal.stop_loss) if signal.stop_loss else None,
                'risk_reward_ratio': signal.risk_reward_ratio,
                'timeframe': signal.timeframe,
                'entry_point_type': signal.entry_point_type,
                'quality_score': signal.quality_score,
                'created_at': signal.created_at.isoformat(),
                'expires_at': signal.expires_at.isoformat() if signal.expires_at else None
            }
            signals_data.append(signal_data)
        
        print(f"Serialized {len(signals_data)} signals")
        
        # Create response data
        response_data = {
            'success': True,
            'action': 'generate_signals',
            'signals': signals_data,
            'total_signals': len(signals),
            'search_saved': True,
            'search_id': search.id
        }
        
        print(f"✅ API view logic completed successfully!")
        print(f"Response data keys: {list(response_data.keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Error during API view test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        user.delete()

if __name__ == '__main__':
    test_backtest_api_view()
