from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count
from apps.trading.models import Portfolio, Position, Trade
from apps.signals.models import Signal, AIModel
from apps.data.models import MarketData, TechnicalIndicator


def home(request):
    """Home page view"""
    context = {
        'title': 'AI-Enhanced Trading Signal Engine',
        'description': 'Advanced trading platform powered by artificial intelligence',
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def dashboard(request):
    """Main dashboard view"""
    try:
        portfolio = Portfolio.objects.get(user=request.user)
    except Portfolio.DoesNotExist:
        portfolio = None
    
    # Get recent signals
    recent_signals = Signal.objects.filter(is_active=True).order_by('-generated_at')[:10]
    
    # Get portfolio statistics
    if portfolio:
        open_positions = Position.objects.filter(portfolio=portfolio, is_open=True)
        total_positions = open_positions.count()
        total_pnl = sum([pos.unrealized_pnl for pos in open_positions])
        
        # Recent trades
        recent_trades = Trade.objects.filter(portfolio=portfolio).order_by('-executed_at')[:5]
    else:
        total_positions = 0
        total_pnl = 0
        recent_trades = []
    
    # AI model statistics
    active_models = AIModel.objects.filter(is_active=True).count()
    
    context = {
        'portfolio': portfolio,
        'recent_signals': recent_signals,
        'total_positions': total_positions,
        'total_pnl': total_pnl,
        'recent_trades': recent_trades,
        'active_models': active_models,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def portfolio_view(request):
    """Portfolio details view"""
    try:
        portfolio = Portfolio.objects.get(user=request.user)
        positions = Position.objects.filter(portfolio=portfolio, is_open=True)
        trades = Trade.objects.filter(portfolio=portfolio).order_by('-executed_at')[:20]
    except Portfolio.DoesNotExist:
        portfolio = None
        positions = []
        trades = []
    
    context = {
        'portfolio': portfolio,
        'positions': positions,
        'trades': trades,
    }
    
    return render(request, 'dashboard/portfolio.html', context)


@login_required
def signals_view(request):
    """Signals view"""
    signals = Signal.objects.filter(is_active=True).order_by('-generated_at')
    
    context = {
        'signals': signals,
    }
    
    return render(request, 'dashboard/signals.html', context)


def api_dashboard_stats(request):
    """API endpoint for dashboard statistics"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        portfolio = Portfolio.objects.get(user=request.user)
        open_positions = Position.objects.filter(portfolio=portfolio, is_open=True)
        total_pnl = sum([pos.unrealized_pnl for pos in open_positions])
        
        stats = {
            'total_positions': open_positions.count(),
            'total_pnl': float(total_pnl),
            'portfolio_balance': float(portfolio.balance),
            'active_signals': Signal.objects.filter(is_active=True).count(),
        }
        
        return JsonResponse(stats)
    except Portfolio.DoesNotExist:
        return JsonResponse({'error': 'Portfolio not found'}, status=404)
