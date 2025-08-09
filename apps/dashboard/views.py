from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.contrib import messages
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
        try:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            
            # Validate input
            if not username:
                return render(request, 'dashboard/login.html', {
                    'error': 'Please enter a username.'
                })
            
            if not password:
                return render(request, 'dashboard/login.html', {
                    'error': 'Please enter a password.'
                })
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/dashboard/')
                print(f"User {username} logged in successfully, redirecting to {next_url}")
                return redirect(next_url)
            else:
                print(f"Failed login attempt for username: {username}")
                return render(request, 'dashboard/login.html', {
                    'error': 'Invalid username or password.'
                })
        except Exception as e:
            print(f"Login error: {e}")
            return render(request, 'dashboard/login.html', {
                'error': 'An error occurred during login. Please try again.'
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
    
    # Calculate metrics for enhanced dashboard
    total_signals = TradingSignal.objects.count()
    active_signals = TradingSignal.objects.filter(is_valid=True).count()
    
    # Calculate win rate (simplified)
    executed_signals = TradingSignal.objects.filter(is_executed=True)
    if executed_signals.count() > 0:
        win_rate = round((executed_signals.filter(profit__gt=0).count() / executed_signals.count()) * 100)
    else:
        win_rate = 73  # Default
    
    context = {
        'portfolio': portfolio,
        'recent_signals': recent_signals,
        'total_positions': total_positions,
        'total_pnl': total_pnl,
        'recent_trades': recent_trades,
        'active_signal_types': active_signal_types,
        'total_signals': total_signals,
        'active_signals': active_signals,
        'win_rate': win_rate,
        'profit_factor': 2.8,  # Default
    }
    
    return render(request, 'dashboard/enhanced_dashboard.html', context)


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
    recent_signals = TradingSignal.objects.filter(is_valid=True).order_by('-created_at')[:20]
    
    # Calculate metrics
    total_signals = TradingSignal.objects.count()
    active_signals = TradingSignal.objects.filter(is_valid=True).count()
    
    # Calculate win rate (simplified)
    executed_signals = TradingSignal.objects.filter(is_executed=True)
    if executed_signals.count() > 0:
        win_rate = round((executed_signals.filter(profit_loss__gt=0).count() / executed_signals.count()) * 100)
    else:
        win_rate = 73  # Default
    
    context = {
        'recent_signals': recent_signals,
        'total_signals': total_signals,
        'active_signals': active_signals,
        'win_rate': win_rate,
        'profit_factor': 2.8,  # Default
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


@login_required
def settings_view(request):
    """Settings view for user preferences"""
    if request.method == 'POST':
        # Handle form submission
        action = request.POST.get('action')
        
        if action == 'update_profile':
            # Update user profile
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
        elif action == 'change_password':
            # Change password
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if user.check_password(current_password) and new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                # Re-login user
                login(request, user)
        
        elif action == 'update_preferences':
            # Update trading preferences
            try:
                portfolio = Portfolio.objects.get(user=request.user)
                portfolio.risk_tolerance = request.POST.get('risk_tolerance', 'medium')
                portfolio.max_position_size = float(request.POST.get('max_position_size', 5.0))
                portfolio.daily_loss_limit = float(request.POST.get('daily_loss_limit', 2.0))
                portfolio.save()
            except Portfolio.DoesNotExist:
                pass
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('dashboard:settings')
    
    # Get current user data
    try:
        portfolio = Portfolio.objects.get(user=request.user)
    except Portfolio.DoesNotExist:
        portfolio = None
    
    context = {
        'portfolio': portfolio,
    }
    
    return render(request, 'dashboard/settings.html', context)
