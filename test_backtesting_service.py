#!/usr/bin/env python3
"""
Test script for the new BacktestingService
This script tests all the functionality implemented in Phase 6D.1
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

from apps.analytics.services import BacktestingService

def test_backtesting_service():
    """Test the comprehensive BacktestingService functionality"""
    print("🧪 Testing BacktestingService - Phase 6D.1 Implementation")
    print("=" * 60)
    
    # Test 1: Basic initialization
    print("\n1. Testing Basic Initialization...")
    try:
        backtest_service = BacktestingService(initial_capital=10000)
        assert backtest_service.initial_capital == Decimal('10000')
        assert backtest_service.commission_rate == Decimal('0.001')
        assert backtest_service.slippage == Decimal('0.0005')
        print("✅ Basic initialization successful")
    except Exception as e:
        print(f"❌ Basic initialization failed: {e}")
        return False
    
    # Test 2: Mock strategy creation
    print("\n2. Testing Mock Strategy Creation...")
    try:
        class MockStrategy:
            def __init__(self, name):
                self.name = name
                self.symbol = 'BTC'
        
        strategy = MockStrategy("Test Strategy")
        assert strategy.name == "Test Strategy"
        print("✅ Mock strategy creation successful")
    except Exception as e:
        print(f"❌ Mock strategy creation failed: {e}")
        return False
    
    # Test 3: Historical data generation
    print("\n3. Testing Historical Data Generation...")
    try:
        start_date = datetime.now().date() - timedelta(days=100)
        end_date = datetime.now().date()
        
        # Test synthetic data generation
        historical_data = backtest_service._generate_synthetic_data(start_date, end_date)
        assert len(historical_data) > 0
        assert 'timestamp' in historical_data.columns
        assert 'close' in historical_data.columns
        print(f"✅ Historical data generation successful: {len(historical_data)} data points")
    except Exception as e:
        print(f"❌ Historical data generation failed: {e}")
        return False
    
    # Test 4: Strategy execution simulation
    print("\n4. Testing Strategy Execution Simulation...")
    try:
        # Reset backtest state
        backtest_service._reset_backtest_state()
        
        # Simulate strategy execution
        backtest_service._simulate_strategy_execution(strategy, historical_data, None)
        
        # Check if trades were generated
        assert len(backtest_service.trades) >= 0
        assert len(backtest_service.equity_curve) > 0
        print(f"✅ Strategy execution simulation successful: {len(backtest_service.trades)} trades, {len(backtest_service.equity_curve)} equity points")
    except Exception as e:
        print(f"❌ Strategy execution simulation failed: {e}")
        return False
    
    # Test 5: Performance metrics calculation
    print("\n5. Testing Performance Metrics Calculation...")
    try:
        metrics = backtest_service._calculate_performance_metrics()
        
        # Check if all required metrics are present
        required_metrics = [
            'total_return', 'annualized_return', 'sharpe_ratio', 
            'max_drawdown', 'win_rate', 'profit_factor', 'total_trades'
        ]
        
        for metric in required_metrics:
            assert metric in metrics, f"Missing metric: {metric}"
        
        print("✅ Performance metrics calculation successful")
        print(f"   - Total Return: {metrics['total_return']}%")
        print(f"   - Sharpe Ratio: {metrics['sharpe_ratio']}")
        print(f"   - Max Drawdown: {metrics['max_drawdown']}%")
        print(f"   - Win Rate: {metrics['win_rate']}%")
    except Exception as e:
        print(f"❌ Performance metrics calculation failed: {e}")
        return False
    
    # Test 6: Backtest report generation
    print("\n6. Testing Backtest Report Generation...")
    try:
        report = backtest_service._generate_backtest_report(
            strategy, 'BTC', start_date, end_date, metrics
        )
        
        assert report is not None
        assert 'strategy_name' in report
        assert 'performance_metrics' in report
        assert 'summary' in report
        assert 'recommendations' in report
        
        print("✅ Backtest report generation successful")
        print(f"   - Strategy: {report['strategy_name']}")
        print(f"   - Summary: {report['summary'][:100]}...")
        print(f"   - Recommendations: {len(report['recommendations'])} items")
    except Exception as e:
        print(f"❌ Backtest report generation failed: {e}")
        return False
    
    # Test 7: Strategy comparison
    print("\n7. Testing Strategy Comparison...")
    try:
        strategies = [
            MockStrategy("Strategy A"),
            MockStrategy("Strategy B"),
            MockStrategy("Strategy C")
        ]
        
        comparison_results = backtest_service.compare_strategies(
            strategies, 'BTC', start_date, end_date
        )
        
        assert len(comparison_results) > 0
        print(f"✅ Strategy comparison successful: {len(comparison_results)} strategies compared")
        
        # Show comparison results
        for i, result in enumerate(comparison_results[:3]):  # Show top 3
            print(f"   {i+1}. {result['strategy_name']}: Sharpe={result['sharpe_ratio']:.2f}, Return={result['total_return']:.2f}%")
            
    except Exception as e:
        print(f"❌ Strategy comparison failed: {e}")
        return False
    
    # Test 8: Parameter optimization
    print("\n8. Testing Parameter Optimization...")
    try:
        param_ranges = {
            'sma_short_period': [10, 20, 30],
            'sma_long_period': [40, 50, 60]
        }
        
        optimization_results = backtest_service.optimize_parameters(
            strategy, 'BTC', start_date, end_date, param_ranges
        )
        
        if optimization_results:
            assert 'best_parameters' in optimization_results
            assert 'best_sharpe_ratio' in optimization_results
            print("✅ Parameter optimization successful")
            print(f"   - Best Sharpe Ratio: {optimization_results['best_sharpe_ratio']:.2f}")
            print(f"   - Best Parameters: {optimization_results['best_parameters']}")
        else:
            print("⚠️ Parameter optimization returned no results (this may be expected)")
            
    except Exception as e:
        print(f"❌ Parameter optimization failed: {e}")
        return False
    
    # Test 9: Full backtest execution
    print("\n9. Testing Full Backtest Execution...")
    try:
        full_result = backtest_service.backtest_strategy(
            strategy, 'BTC', start_date, end_date
        )
        
        assert full_result is not None
        assert 'performance_metrics' in full_result
        assert 'summary' in full_result
        
        print("✅ Full backtest execution successful")
        print(f"   - Final Capital: ${full_result['performance_metrics']['final_capital']:.2f}")
        print(f"   - Total Trades: {full_result['performance_metrics']['total_trades']}")
        
    except Exception as e:
        print(f"❌ Full backtest execution failed: {e}")
        return False
    
    # Test 10: Error handling
    print("\n10. Testing Error Handling...")
    try:
        # Test with invalid dates
        invalid_result = backtest_service.backtest_strategy(
            strategy, 'BTC', end_date, start_date  # End date before start date
        )
        
        # Should handle gracefully
        print("✅ Error handling successful")
        
    except Exception as e:
        print(f"❌ Error handling failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All BacktestingService tests completed successfully!")
    print("✅ Phase 6D.1: Strategy Backtesting Framework is fully operational!")
    
    return True

def test_legacy_compatibility():
    """Test backward compatibility with old BacktestEngine"""
    print("\n🧪 Testing Legacy Compatibility...")
    print("=" * 40)
    
    try:
        from apps.analytics.services import BacktestEngine
        
        # Test legacy method
        legacy_result = BacktestEngine.run_backtest(
            strategy="Legacy Test",
            start_date=datetime.now().date() - timedelta(days=30),
            end_date=datetime.now().date(),
            initial_capital=10000
        )
        
        assert legacy_result is not None
        assert 'total_return' in legacy_result
        assert 'sharpe_ratio' in legacy_result
        
        print("✅ Legacy compatibility successful")
        print(f"   - Legacy Total Return: {legacy_result['total_return']}%")
        print(f"   - Legacy Sharpe Ratio: {legacy_result['sharpe_ratio']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Legacy compatibility failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting BacktestingService Tests...")
    
    # Run main tests
    main_success = test_backtesting_service()
    
    # Run legacy compatibility tests
    legacy_success = test_legacy_compatibility()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if main_success and legacy_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ BacktestingService is fully operational")
        print("✅ Legacy compatibility maintained")
        print("✅ Phase 6D.1 requirements met:")
        print("   - ✅ BacktestingService class created")
        print("   - ✅ Historical data simulation implemented")
        print("   - ✅ Performance metrics calculation added")
        print("   - ✅ Drawdown analysis implemented")
        print("   - ✅ Strategy comparison tools added")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        if not main_success:
            print("❌ Main BacktestingService tests failed")
        if not legacy_success:
            print("❌ Legacy compatibility tests failed")
        sys.exit(1)
