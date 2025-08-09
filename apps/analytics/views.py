from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import AnalyticsPortfolio, AnalyticsPosition, AnalyticsTrade, PerformanceMetrics, BacktestResult, MarketData, Alert
from .services import PortfolioAnalytics, TechnicalIndicators, BacktestEngine, RiskManager, MarketAnalyzer

@login_required
def analytics_dashboard(request):
    """Advanced analytics dashboard with interactive charts"""
    user = request.user
    
    # Get or create user portfolio
    portfolio, created = AnalyticsPortfolio.objects.get_or_create(
        user=user,
        defaults={'name': 'Main Portfolio', 'description': 'Primary trading portfolio'}
    )
    
    # Get portfolio positions
    positions = AnalyticsPosition.objects.filter(portfolio=portfolio, is_open=True)
    
    # Get recent trades
    recent_trades = AnalyticsTrade.objects.filter(portfolio=portfolio).order_by('-timestamp')[:10]
    
    # Get performance metrics
    performance_metrics = PerformanceMetrics.objects.filter(portfolio=portfolio).order_by('-date')[:30]
    
    # Calculate portfolio statistics
    total_positions = positions.count()
    total_value = sum([pos.market_value for pos in positions])
    total_pnl = sum([pos.unrealized_pnl for pos in positions])
    
    # Get market overview
    market_overview = MarketAnalyzer.get_market_overview()
    
    # Get recent alerts
    alerts = Alert.objects.filter(user=user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'portfolio': portfolio,
        'positions': positions,
        'recent_trades': recent_trades,
        'performance_metrics': performance_metrics,
        'total_positions': total_positions,
        'total_value': total_value,
        'total_pnl': total_pnl,
        'market_overview': market_overview,
        'alerts': alerts,
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def portfolio_view(request):
    """Detailed portfolio view with positions and performance"""
    user = request.user
    
    # Try to get portfolio, create one if it doesn't exist
    try:
        portfolio = AnalyticsPortfolio.objects.get(user=user)
    except AnalyticsPortfolio.DoesNotExist:
        # Create a default portfolio for the user
        portfolio = AnalyticsPortfolio.objects.create(
            user=user,
            name=f"{user.username}'s Portfolio",
            initial_balance=Decimal('10000.00'),
            current_balance=Decimal('10000.00')
        )
    
    # Get all positions
    positions = AnalyticsPosition.objects.filter(portfolio=portfolio).order_by('-updated_at')
    
    # Get portfolio performance data for charts
    performance_data = PerformanceMetrics.objects.filter(portfolio=portfolio).order_by('date')
    
    # Calculate portfolio metrics
    total_return = portfolio.total_return
    total_return_amount = portfolio.total_return_amount
    
    # Get sector allocation (simplified)
    sector_allocation = {
        'Technology': 35,
        'Healthcare': 25,
        'Finance': 20,
        'Energy': 15,
        'Other': 5
    }
    
    context = {
        'portfolio': portfolio,
        'positions': positions,
        'performance_data': performance_data,
        'total_return': total_return,
        'total_return_amount': total_return_amount,
        'sector_allocation': sector_allocation,
    }
    
    return render(request, 'analytics/portfolio.html', context)

@login_required
def performance_analytics(request):
    """Advanced performance analytics with charts"""
    user = request.user
    
    # Try to get portfolio, create one if it doesn't exist
    try:
        portfolio = AnalyticsPortfolio.objects.get(user=user)
    except AnalyticsPortfolio.DoesNotExist:
        # Create a default portfolio for the user
        portfolio = AnalyticsPortfolio.objects.create(
            user=user,
            name=f"{user.username}'s Portfolio",
            initial_balance=Decimal('10000.00'),
            current_balance=Decimal('10000.00')
        )
    
    # Get performance metrics for analysis
    metrics = PerformanceMetrics.objects.filter(portfolio=portfolio).order_by('date')
    
    # Calculate advanced metrics
    if metrics.exists():
        returns = [float(m.daily_return) for m in metrics]
        values = [float(m.total_value) for m in metrics]
        
        sharpe_ratio = PortfolioAnalytics.calculate_sharpe_ratio(returns)
        max_drawdown = PortfolioAnalytics.calculate_max_drawdown(values)
        volatility = PortfolioAnalytics.calculate_volatility(returns)
        var_95 = PortfolioAnalytics.calculate_var(returns)
    else:
        sharpe_ratio = max_drawdown = volatility = var_95 = 0
    
    # Get trade statistics
    trades = AnalyticsTrade.objects.filter(portfolio=portfolio)
    total_trades = trades.count()
    winning_trades = trades.filter(trade_type='SELL').count()  # Simplified
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    context = {
        'portfolio': portfolio,
        'metrics': metrics,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'volatility': volatility,
        'var_95': var_95,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'win_rate': win_rate,
    }
    
    return render(request, 'analytics/performance.html', context)

@login_required
def backtesting_view(request):
    """Backtesting interface for strategy validation"""
    user = request.user
    
    # Get user's backtest results
    backtest_results = BacktestResult.objects.filter(user=user).order_by('-created_at')
    
    if request.method == 'POST':
        # Handle backtest form submission
        strategy_name = request.POST.get('strategy_name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        initial_capital = float(request.POST.get('initial_capital', 10000))
        
        # Run backtest (simplified)
        results = BacktestEngine.run_backtest(
            strategy=strategy_name,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )
        
        # Save backtest results
        BacktestResult.objects.create(
            user=user,
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_capital=results['final_capital'],
            total_return=results['total_return'],
            annualized_return=results['annualized_return'],
            sharpe_ratio=results['sharpe_ratio'],
            max_drawdown=results['max_drawdown'],
            win_rate=results['win_rate'],
            profit_factor=results['profit_factor'],
            total_trades=results['total_trades'],
            winning_trades=results['winning_trades'],
            losing_trades=results['losing_trades'],
        )
        
        messages.success(request, f'Backtest completed for {strategy_name}')
        return redirect('analytics:backtesting')
    
    context = {
        'backtest_results': backtest_results,
    }
    
    return render(request, 'analytics/backtesting.html', context)

@login_required
def risk_management(request):
    """Risk management dashboard"""
    user = request.user
    
    # Try to get portfolio, create one if it doesn't exist
    try:
        portfolio = AnalyticsPortfolio.objects.get(user=user)
    except AnalyticsPortfolio.DoesNotExist:
        # Create a default portfolio for the user
        portfolio = AnalyticsPortfolio.objects.create(
            user=user,
            name=f"{user.username}'s Portfolio",
            initial_balance=Decimal('10000.00'),
            current_balance=Decimal('10000.00')
        )
    
    # Get open positions
    positions = AnalyticsPosition.objects.filter(portfolio=portfolio, is_open=True)
    
    # Calculate risk metrics
    total_value = sum([pos.market_value for pos in positions]) if positions else Decimal('0.00')
    portfolio_risk = RiskManager.calculate_portfolio_risk(positions, total_value) if total_value > 0 else Decimal('0.00')
    
    # Calculate position sizes for new trades
    risk_per_trade = 2.0  # 2% risk per trade
    stop_loss_pct = 5.0   # 5% stop loss
    
    # Calculate additional risk metrics for positions
    for position in positions:
        position.stop_loss_price = position.entry_price * Decimal('0.95')  # 5% below entry
        position.risk_amount = position.market_value * Decimal('0.05')  # 5% of market value
    
    context = {
        'portfolio': portfolio,
        'positions': positions,
        'total_value': total_value,
        'portfolio_risk': portfolio_risk,
        'risk_per_trade': risk_per_trade,
        'stop_loss_pct': stop_loss_pct,
    }
    
    return render(request, 'analytics/risk_management.html', context)

@login_required
def market_analysis(request):
    """Market analysis and technical indicators"""
    symbol = request.GET.get('symbol', 'BTC')
    
    # Get market data for the symbol
    market_data = MarketData.objects.filter(symbol=symbol).order_by('-date')[:100]
    
    # Calculate technical indicators
    if market_data.exists():
        prices = [float(data.close_price) for data in market_data]
        
        sma_20 = TechnicalIndicators.calculate_sma(prices, 20)
        sma_50 = TechnicalIndicators.calculate_sma(prices, 50)
        rsi = TechnicalIndicators.calculate_rsi(prices)
        macd_line, macd_signal = TechnicalIndicators.calculate_macd(prices)
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.calculate_bollinger_bands(prices)
    else:
        sma_20 = sma_50 = rsi = macd_line = macd_signal = None
        bb_upper = bb_middle = bb_lower = None
    
    # Get market sentiment
    sentiment = MarketAnalyzer.calculate_market_sentiment(symbol)
    
    context = {
        'symbol': symbol,
        'market_data': market_data,
        'sma_20': sma_20,
        'sma_50': sma_50,
        'rsi': rsi,
        'macd_line': macd_line,
        'macd_signal': macd_signal,
        'bb_upper': bb_upper,
        'bb_middle': bb_middle,
        'bb_lower': bb_lower,
        'sentiment': sentiment,
    }
    
    return render(request, 'analytics/market_analysis.html', context)

# API Views for AJAX requests
@login_required
def portfolio_data_api(request):
    """API endpoint for portfolio data"""
    user = request.user
    
    # Try to get portfolio, create one if it doesn't exist
    try:
        portfolio = AnalyticsPortfolio.objects.get(user=user)
    except AnalyticsPortfolio.DoesNotExist:
        # Create a default portfolio for the user
        portfolio = AnalyticsPortfolio.objects.create(
            user=user,
            name=f"{user.username}'s Portfolio",
            initial_balance=Decimal('10000.00'),
            current_balance=Decimal('10000.00')
        )
    
    # Get performance data for charts
    metrics = PerformanceMetrics.objects.filter(portfolio=portfolio).order_by('date')
    
    chart_data = {
        'labels': [m.date.strftime('%Y-%m-%d') for m in metrics],
        'values': [float(m.total_value) for m in metrics],
        'returns': [float(m.daily_return) for m in metrics],
    }
    
    return JsonResponse(chart_data)

@login_required
def position_data_api(request):
    """API endpoint for position data"""
    user = request.user
    
    # Try to get portfolio, create one if it doesn't exist
    try:
        portfolio = AnalyticsPortfolio.objects.get(user=user)
    except AnalyticsPortfolio.DoesNotExist:
        # Create a default portfolio for the user
        portfolio = AnalyticsPortfolio.objects.create(
            user=user,
            name=f"{user.username}'s Portfolio",
            initial_balance=Decimal('10000.00'),
            current_balance=Decimal('10000.00')
        )
    
    positions = AnalyticsPosition.objects.filter(portfolio=portfolio, is_open=True)
    
    position_data = []
    for pos in positions:
        position_data.append({
            'symbol': pos.symbol,
            'quantity': float(pos.quantity),
            'entry_price': float(pos.entry_price),
            'current_price': float(pos.current_price),
            'market_value': float(pos.market_value),
            'unrealized_pnl': float(pos.unrealized_pnl),
            'unrealized_pnl_percent': float(pos.unrealized_pnl_percent),
        })
    
    return JsonResponse({'positions': position_data})

@login_required
def market_data_api(request):
    """API endpoint for market data"""
    symbol = request.GET.get('symbol', 'BTC')
    
    market_data = MarketData.objects.filter(symbol=symbol).order_by('-date')[:50]
    
    chart_data = {
        'labels': [data.date.strftime('%Y-%m-%d') for data in market_data],
        'prices': [float(data.close_price) for data in market_data],
        'volumes': [float(data.volume) for data in market_data],
    }
    
    return JsonResponse(chart_data)
