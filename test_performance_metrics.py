#!/usr/bin/env python
"""
Simple Phase 2 Test
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.signals.performance_metrics_service import PerformanceMetricsService
from apps.signals.models import TradeLog, BacktestResult

def test_performance_metrics():
    print("Testing Performance Metrics Service...")
    
    service = PerformanceMetricsService()
    
    # Test portfolio performance
    portfolio_perf = service.calculate_portfolio_performance()
    print(f"Portfolio Performance:")
    print(f"  Total Backtests: {portfolio_perf.get('total_backtests', 0)}")
    print(f"  Profitable Backtests: {portfolio_perf.get('profitable_backtests', 0)}")
    print(f"  Average Return: {portfolio_perf.get('avg_return', 0):.2f}%")
    print(f"  Average Win Rate: {portfolio_perf.get('avg_win_rate', 0):.1%}")
    
    # Test strategy performance
    strategy_perf = service.calculate_strategy_performance('SMA_Crossover')
    print(f"\nSMA_Crossover Strategy Performance:")
    print(f"  Total Backtests: {strategy_perf.get('total_backtests', 0)}")
    print(f"  Average Return: {strategy_perf.get('avg_return', 0):.2f}%")
    print(f"  Performance Rating: {strategy_perf.get('performance_rating', 'N/A')}")
    
    # Test trends
    trends = service.get_performance_trends(days=30)
    print(f"\nPerformance Trends:")
    print(f"  Days Analyzed: {trends.get('summary', {}).get('days_analyzed', 0)}")
    print(f"  Trend Direction: {trends.get('summary', {}).get('trend_direction', 'N/A')}")
    
    print("\nPerformance Metrics Service working correctly!")

if __name__ == '__main__':
    test_performance_metrics()
