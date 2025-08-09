from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db.models import Sum, Count
from apps.trading.models import Portfolio, Position, Trade
from apps.signals.models import TradingSignal, SignalType
from apps.data.models import MarketData, TechnicalIndicator


def home(request):
    """Home page view"""
    context = {
        'title': 'AI-Enhanced Trading Signal Engine',
        'description': 'Advanced trading platform powered by artificial intelligence',
    }
    return render(request, 'dashboard/home.html', context)


def login_view(request):
    """Login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        else:
            # Return an 'invalid login' error message.
            return render(request, 'dashboard/login.html', {
                'error': 'Invalid username or password.'
            })
    return render(request, 'dashboard/login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('/')


@login_required
def dashboard(request):
    """Main dashboard view"""
    try:
        portfolio = Portfolio.objects.get(user=request.user)
    except Portfolio.DoesNotExist:
        portfolio = None
    
    # Get recent signals
    recent_signals = TradingSignal.objects.filter(is_valid=True).order_by('-created_at')[:10]
    
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
    
    # Signal type statistics
    active_signal_types = SignalType.objects.filter(is_active=True).count()
    
    context = {
        'portfolio': portfolio,
        'recent_signals': recent_signals,
        'total_positions': total_positions,
        'total_pnl': total_pnl,
        'recent_trades': recent_trades,
        'active_signal_types': active_signal_types,
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
    signals = TradingSignal.objects.filter(is_valid=True).order_by('-created_at')
    
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
            'active_signals': TradingSignal.objects.filter(is_valid=True).count(),
        }
        
        return JsonResponse(stats)
    except Portfolio.DoesNotExist:
        return JsonResponse({'error': 'Portfolio not found'}, status=404)
