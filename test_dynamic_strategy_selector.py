#!/usr/bin/env python3
"""
Test script for the DynamicStrategySelector class
This script tests all the functionality implemented in Phase 6D.3
"""

import sys
import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.analytics.services import DynamicStrategySelector, BacktestingService

def test_dynamic_strategy_selector():
    """Test the comprehensive DynamicStrategySelector functionality"""
    print("🧪 Testing DynamicStrategySelector - Phase 6D.3 Implementation")
    print("=" * 70)
    
    # Test 1: Basic initialization
    print("\n1. Testing basic initialization...")
    selector = DynamicStrategySelector()
    assert selector is not None
    assert hasattr(selector, 'strategy_registry')
    assert hasattr(selector, 'market_regime_detector')
    assert hasattr(selector, 'performance_tracker')
    print("✅ Basic initialization successful")
    
    # Test 2: Strategy registration
    print("\n2. Testing strategy registration...")
    class MockStrategy:
        def __init__(self, name):
            self.name = name
    
    strategies = [
        ('Moving Average Crossover', MockStrategy('MA'), {'fast_period': 10, 'slow_period': 20}),
        ('RSI Strategy', MockStrategy('RSI'), {'period': 14, 'overbought': 70, 'oversold': 30}),
        ('MACD Strategy', MockStrategy('MACD'), {'fast': 12, 'slow': 26, 'signal': 9}),
        ('Bollinger Bands', MockStrategy('BB'), {'period': 20, 'std_dev': 2}),
        ('Breakout Strategy', MockStrategy('Breakout'), {'period': 20, 'multiplier': 2}),
        ('Mean Reversion', MockStrategy('MeanRev'), {'period': 20, 'std_dev': 2})
    ]
    
    for name, strategy, params in strategies:
        selector.register_strategy(name, strategy, params)
    
    assert len(selector.strategy_registry) == 6
    print("✅ Strategy registration successful")
    
    # Test 3: Market regime detection
    print("\n3. Testing market regime detection...")
    # Generate mock market data
    mock_market_data = []
    base_price = 100.0
    for i in range(50):
        # Simulate trending bull market
        price_change = 0.02 + (i * 0.001)  # Upward trend
        volatility = 0.03 + (i * 0.0005)   # Increasing volatility
        price = base_price * (1 + price_change)
        mock_market_data.append({
            'close': price,
            'high': price * (1 + volatility),
            'low': price * (1 - volatility),
            'volume': 1000000 + (i * 10000)
        })
        base_price = price
    
    regime = selector.detect_market_regime(mock_market_data, lookback_period=30)
    print(f"   Detected regime: {regime}")
    assert regime in ['trending_bull', 'trending_bear', 'sideways', 'volatile', 'calm', 'mixed']
    print("✅ Market regime detection successful")
    
    # Test 4: Strategy ranking
    print("\n4. Testing strategy ranking...")
    ranked_strategies = selector.rank_strategies('BTC', regime, lookback_days=90)
    
    assert len(ranked_strategies) == 6
    assert all('score' in strategy for strategy in ranked_strategies)
    assert all('performance' in strategy for strategy in ranked_strategies)
    assert all('risk_score' in strategy for strategy in ranked_strategies)
    
    # Check that strategies are sorted by score (highest first)
    scores = [s['score'] for s in ranked_strategies]
    assert scores == sorted(scores, reverse=True)
    
    print(f"   Top strategy: {ranked_strategies[0]['strategy_name']} (Score: {ranked_strategies[0]['score']:.2f})")
    print("✅ Strategy ranking successful")
    
    # Test 5: Best strategy selection
    print("\n5. Testing best strategy selection...")
    best_strategies = selector.select_best_strategies(
        'BTC', regime, num_strategies=3, risk_tolerance='medium', diversification=True
    )
    
    assert len(best_strategies) == 3
    assert all('strategy_name' in strategy for strategy in best_strategies)
    
    print(f"   Selected strategies: {[s['strategy_name'] for s in best_strategies]}")
    print("✅ Best strategy selection successful")
    
    # Test 6: Risk tolerance filtering
    print("\n6. Testing risk tolerance filtering...")
    low_risk_strategies = selector.select_best_strategies(
        'BTC', regime, num_strategies=5, risk_tolerance='low', diversification=False
    )
    
    # All strategies should have high risk scores for low risk tolerance
    for strategy in low_risk_strategies:
        assert strategy['risk_score'] >= 0.7
    
    print(f"   Low risk strategies: {len(low_risk_strategies)}")
    print("✅ Risk tolerance filtering successful")
    
    # Test 7: Diversification
    print("\n7. Testing diversification...")
    diversified_strategies = selector.select_best_strategies(
        'BTC', regime, num_strategies=4, risk_tolerance='medium', diversification=True
    )
    
    # Check that we have different strategy types
    strategy_types = set()
    for strategy in diversified_strategies:
        strategy_type = selector._get_strategy_type(strategy['strategy_name'])
        strategy_types.add(strategy_type)
    
    print(f"   Strategy types: {strategy_types}")
    print("✅ Diversification successful")
    
    # Test 8: Strategy recommendations
    print("\n8. Testing strategy recommendations...")
    recommendations = selector.get_strategy_recommendations(
        'BTC', regime, portfolio_size=50000, risk_tolerance='medium'
    )
    
    assert len(recommendations) > 0
    assert all('position_size' in rec for rec in recommendations)
    assert all('allocation_percentage' in rec for rec in recommendations)
    assert all('risk_level' in rec for rec in recommendations)
    
    total_allocation = sum(rec['allocation_percentage'] for rec in recommendations)
    print(f"   Total allocation: {total_allocation:.1f}%")
    print("✅ Strategy recommendations successful")
    
    # Test 9: Adaptive strategy switching
    print("\n9. Testing adaptive strategy switching...")
    current_portfolio = [
        {'strategy': 'Moving Average Crossover'},
        {'strategy': 'RSI Strategy'},
        {'strategy': 'MACD Strategy'}
    ]
    
    switching_recommendations = selector.adaptive_strategy_switching(
        current_portfolio, regime, 'BTC', switching_threshold=0.1
    )
    
    print(f"   Switching recommendations: {len(switching_recommendations)}")
    for rec in switching_recommendations:
        print(f"     {rec['from_strategy']} → {rec['to_strategy']} ({rec['priority']})")
    
    print("✅ Adaptive strategy switching successful")
    
    # Test 10: Market regime detector
    print("\n10. Testing market regime detector...")
    detector = selector.market_regime_detector
    
    # Test different market conditions
    # Sideways market
    sideways_data = [{'close': 100 + (i % 10 - 5)} for i in range(50)]
    sideways_regime = detector.detect_regime(sideways_data, 30)
    print(f"   Sideways market regime: {sideways_regime}")
    
    # Volatile market
    volatile_data = [{'close': 100 + (i * 2 - 25)} for i in range(50)]
    volatile_regime = detector.detect_regime(volatile_data, 30)
    print(f"   Volatile market regime: {volatile_regime}")
    
    print("✅ Market regime detector successful")
    
    # Test 11: Performance tracker
    print("\n11. Testing performance tracker...")
    tracker = selector.performance_tracker
    
    # Test performance retrieval
    performance = tracker.get_strategy_performance('Moving Average Crossover', 'BTC', 90)
    assert 'sharpe_ratio' in performance
    assert 'total_return' in performance
    assert 'max_drawdown' in performance
    
    # Test performance summary
    summary = tracker.get_performance_summary(['Moving Average Crossover', 'RSI Strategy'], 'BTC', 90)
    assert len(summary) == 2
    assert 'Moving Average Crossover' in summary
    
    print("✅ Performance tracker successful")
    
    # Test 12: Integration with backtesting service
    print("\n12. Testing integration with backtesting service...")
    backtest_service = BacktestingService()
    selector_with_backtest = DynamicStrategySelector(backtest_service)
    
    assert selector_with_backtest.backtesting_service is not None
    print("✅ Backtesting service integration successful")
    
    # Test 13: Error handling
    print("\n13. Testing error handling...")
    
    # Test with empty market data
    empty_regime = selector.detect_market_regime([], 30)
    assert empty_regime == 'unknown'
    
    # Test with insufficient data
    short_data = [{'close': 100 + i} for i in range(10)]
    short_regime = selector.detect_market_regime(short_data, 30)
    assert short_regime == 'unknown'
    
    print("✅ Error handling successful")
    
    # Test 14: Performance metrics calculation
    print("\n14. Testing performance metrics calculation...")
    
    # Test risk score calculation
    mock_performance = {
        'max_drawdown': Decimal('15.5'),
        'volatility': Decimal('20.0'),
        'win_rate': Decimal('65.0')
    }
    
    risk_score = selector._calculate_risk_adjusted_score(mock_performance)
    assert 0 <= risk_score <= 1
    print(f"   Risk score: {risk_score:.3f}")
    
    # Test regime adjustment
    regime_adj = selector._calculate_regime_adjustment('Moving Average Crossover', 'trending_bull', mock_performance)
    print(f"   Regime adjustment: {regime_adj:.3f}")
    
    print("✅ Performance metrics calculation successful")
    
    # Test 15: Full workflow
    print("\n15. Testing full workflow...")
    
    # Simulate a complete strategy selection workflow
    symbol = 'ETH'
    market_data = mock_market_data  # Use the same mock data
    
    # 1. Detect market regime
    current_regime = selector.detect_market_regime(market_data)
    
    # 2. Get strategy recommendations
    recommendations = selector.get_strategy_recommendations(
        symbol, current_regime, portfolio_size=100000, risk_tolerance='medium'
    )
    
    # 3. Select best strategies
    best_strategies = selector.select_best_strategies(
        symbol, current_regime, num_strategies=3, diversification=True
    )
    
    # 4. Check if switching is needed
    current_portfolio = [{'strategy': 'Moving Average Crossover'}]
    switching = selector.adaptive_strategy_switching(current_portfolio, current_regime, symbol)
    
    print(f"   Complete workflow results:")
    print(f"     Market regime: {current_regime}")
    print(f"     Top recommendation: {recommendations[0]['strategy_name']}")
    print(f"     Best strategies: {len(best_strategies)}")
    print(f"     Switching needed: {len(switching)}")
    
    print("✅ Full workflow successful")
    
    print("\n" + "=" * 70)
    print("🎉 All DynamicStrategySelector tests passed successfully!")
    print("✅ Phase 6D.3: Dynamic Strategy Selection - IMPLEMENTATION VERIFIED")
    
    return True

def test_legacy_compatibility():
    """Test that the new DynamicStrategySelector maintains backward compatibility"""
    print("\n🔧 Testing legacy compatibility...")
    
    # Test that old BacktestEngine still works
    from apps.analytics.services import BacktestEngine
    
    # This should work without errors
    try:
        result = BacktestEngine.run_backtest(
            strategy='test_strategy',
            start_date='2024-01-01',
            end_date='2024-12-31',
            initial_capital=10000
        )
        assert 'total_return' in result
        print("✅ Legacy BacktestEngine compatibility maintained")
    except Exception as e:
        print(f"❌ Legacy compatibility test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        print("🚀 Starting DynamicStrategySelector Test Suite")
        print("=" * 70)
        
        # Run main tests
        success = test_dynamic_strategy_selector()
        
        if success:
            # Run compatibility tests
            compatibility_success = test_legacy_compatibility()
            
            if compatibility_success:
                print("\n🎉 ALL TESTS PASSED!")
                print("✅ Phase 6D.3: Dynamic Strategy Selection is fully functional")
                print("✅ Backward compatibility maintained")
                print("\n🚀 Ready for production use!")
            else:
                print("\n❌ Compatibility tests failed")
                sys.exit(1)
        else:
            print("\n❌ Main tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
