"""
Phase 2 Comprehensive Test
Test all Phase 2 functionality including backtesting, logging, and performance metrics
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.test import TestCase
from django.utils import timezone
from apps.signals.models import TradeLog, BacktestResult, TradingSignal
from apps.signals.backtesting_service import Phase2BacktestingService
from apps.signals.performance_metrics_service import PerformanceMetricsService
from apps.trading.models import Symbol
from apps.data.models import MarketData


class Phase2ComprehensiveTest:
    """Comprehensive test suite for Phase 2 functionality"""
    
    def __init__(self):
        self.test_results = []
        self.symbol = None
        self.setup_test_data()
    
    def setup_test_data(self):
        """Setup test data for Phase 2 testing"""
        print("Setting up test data...")
        
        # Create or get test symbol
        self.symbol, created = Symbol.objects.get_or_create(
            symbol='TESTUSDT',
            defaults={
                'name': 'Test Coin',
                'symbol_type': 'CRYPTO',
                'exchange': 'Test Exchange',
                'is_active': True
            }
        )
        
        if created:
            print(f"Created test symbol: {self.symbol.symbol}")
        else:
            print(f"Using existing test symbol: {self.symbol.symbol}")
    
    def run_all_tests(self):
        """Run all Phase 2 tests"""
        print("\n" + "="*60)
        print("PHASE 2 COMPREHENSIVE TEST SUITE")
        print("="*60)
        
        tests = [
            ("Model Creation", self.test_model_creation),
            ("Backtesting Service", self.test_backtesting_service),
            ("Performance Metrics", self.test_performance_metrics),
            ("API Endpoints", self.test_api_endpoints),
            ("Dashboard Integration", self.test_dashboard_integration),
            ("Data Integrity", self.test_data_integrity)
        ]
        
        for test_name, test_func in tests:
            print(f"\nRunning {test_name} test...")
            try:
                result = test_func()
                self.test_results.append((test_name, True, result))
                print(f"✓ {test_name}: PASSED")
                if result:
                    print(f"  Result: {result}")
            except Exception as e:
                self.test_results.append((test_name, False, str(e)))
                print(f"✗ {test_name}: FAILED - {e}")
        
        self.print_summary()
    
    def test_model_creation(self):
        """Test TradeLog and BacktestResult model creation"""
        print("  Testing model creation...")
        
        # Test TradeLog creation
        trade = TradeLog.objects.create(
            symbol=self.symbol,
            trade_type='BUY',
            entry_price=Decimal('100.00'),
            quantity=Decimal('1.0'),
            entry_time=timezone.now(),
            backtest_id='test-backtest-001',
            strategy_name='Test Strategy',
            is_open=True
        )
        
        # Test BacktestResult creation
        backtest = BacktestResult.objects.create(
            name='Test Backtest',
            strategy_name='Test Strategy',
            symbol=self.symbol,
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now(),
            initial_capital=Decimal('10000.00'),
            total_trades=1,
            winning_trades=1,
            losing_trades=0,
            win_rate=1.0,
            total_return=Decimal('100.00'),
            total_return_percentage=1.0
        )
        
        return f"Created TradeLog ID: {trade.id}, BacktestResult ID: {backtest.id}"
    
    def test_backtesting_service(self):
        """Test the Phase2BacktestingService"""
        print("  Testing backtesting service...")
        
        service = Phase2BacktestingService(
            initial_capital=10000,
            commission_rate=0.001,
            slippage_rate=0.0005
        )
        
        # Run a test backtest
        start_date = timezone.now() - timedelta(days=30)
        end_date = timezone.now()
        
        result = service.run_backtest(
            symbol=self.symbol,
            strategy_name='Test Strategy',
            start_date=start_date,
            end_date=end_date
        )
        
        # Verify result
        assert result is not None, "Backtest result should not be None"
        assert result.strategy_name == 'Test Strategy', "Strategy name should match"
        assert result.symbol == self.symbol, "Symbol should match"
        
        return f"Backtest completed: {result.total_return_percentage:.2f}% return, {result.total_trades} trades"
    
    def test_performance_metrics(self):
        """Test the PerformanceMetricsService"""
        print("  Testing performance metrics service...")
        
        service = PerformanceMetricsService()
        
        # Test strategy performance calculation
        strategy_perf = service.calculate_strategy_performance('Test Strategy')
        
        # Test symbol performance calculation
        symbol_perf = service.calculate_symbol_performance(self.symbol)
        
        # Test portfolio performance calculation
        portfolio_perf = service.calculate_portfolio_performance()
        
        # Test performance trends
        trends = service.get_performance_trends(days=30)
        
        return f"Strategy performance: {strategy_perf.get('total_backtests', 0)} backtests, " \
               f"Portfolio performance: {portfolio_perf.get('total_backtests', 0)} total backtests"
    
    def test_api_endpoints(self):
        """Test API endpoint functionality"""
        print("  Testing API endpoints...")
        
        from django.test import Client
        from django.contrib.auth.models import User
        
        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        client = Client()
        client.force_login(user)
        
        # Test backtest API
        response = client.get('/signals/api/backtests/')
        assert response.status_code == 200, f"Backtest API should return 200, got {response.status_code}"
        
        # Test trade log API
        response = client.get('/signals/api/trades/')
        assert response.status_code == 200, f"Trade log API should return 200, got {response.status_code}"
        
        return f"API endpoints responding correctly"
    
    def test_dashboard_integration(self):
        """Test dashboard integration"""
        print("  Testing dashboard integration...")
        
        from django.test import Client
        from django.contrib.auth.models import User
        
        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser2',
            defaults={'email': 'test2@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        client = Client()
        client.force_login(user)
        
        # Test performance dashboard
        response = client.get('/signals/performance/')
        assert response.status_code == 200, f"Performance dashboard should return 200, got {response.status_code}"
        
        return f"Dashboard accessible and rendering correctly"
    
    def test_data_integrity(self):
        """Test data integrity and relationships"""
        print("  Testing data integrity...")
        
        # Test TradeLog relationships
        trades = TradeLog.objects.filter(symbol=self.symbol)
        assert trades.exists(), "Should have trades for test symbol"
        
        # Test BacktestResult relationships
        backtests = BacktestResult.objects.filter(symbol=self.symbol)
        assert backtests.exists(), "Should have backtests for test symbol"
        
        # Test trade calculations
        for trade in trades:
            if trade.exit_price:
                trade.calculate_pnl()
                assert trade.profit_loss is not None, "P&L should be calculated"
        
        # Test backtest metrics
        for backtest in backtests:
            assert backtest.total_trades >= 0, "Total trades should be non-negative"
            assert backtest.win_rate is None or 0 <= backtest.win_rate <= 1, "Win rate should be between 0 and 1"
        
        return f"Data integrity verified: {trades.count()} trades, {backtests.count()} backtests"
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, success, result in self.test_results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"  {status}: {test_name}")
            if result and success:
                print(f"    {result}")
            elif not success:
                print(f"    Error: {result}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Phase 2 implementation is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please review the implementation.")
        
        print("="*60)


def run_phase2_test():
    """Run the Phase 2 comprehensive test"""
    test_suite = Phase2ComprehensiveTest()
    test_suite.run_all_tests()


if __name__ == '__main__':
    run_phase2_test()

